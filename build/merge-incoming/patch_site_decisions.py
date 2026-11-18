"""Add the entries made by decisions_from_incoming.py to the Court Decisions pages.

Usage: python3 build/merge-incoming/patch_site_decisions.py SITE NEW.json
Run tools/copy_data.py first (this script also updates site/court-decisions/data/,
which must then be copied back to data/court-decisions/). Adapted from
build/east-asia-cases/patch_imr_site.py so that it works for every country.
Updates cd-data.js, decisions.json/.csv, sources.csv, a static page per new decision,
the all-decisions lists, sitemap.xml, the decision counts and the country labels.
"""
import csv, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "build/east-asia-cases"))
from imr_candidates import to_row, COLS  # noqa: E402

SITE = Path(sys.argv[1]); IN = json.load(open(sys.argv[2], encoding="utf-8")); DATE = "2026-11-17"
CD = SITE / "court-decisions"
E = html.escape

# Country labels used by the interactive page. Add the ones it does not know yet.
J = (CD / "cd.js").read_text(encoding="utf-8")
EXTRA = {"MO": ["Macau", "Makau"], "GH": ["Ghana", "Ghana"], "UG": ["Uganda", "Uganda"], "EG": ["Egypt", "Mesir"], "MM": ["Myanmar", "Myanmar"]}
for k, v in EXTRA.items():
    if not re.search(rf"\b{k}: \[", J):
        J = J.replace('HK: ["Hong Kong", "Hong Kong"],', f'HK: ["Hong Kong", "Hong Kong"], {k}: {json.dumps(v, ensure_ascii=False)},', 1)
(CD / "cd.js").write_text(J, encoding="utf-8")
CN = {m.group(1): m.group(2) for m in re.finditer(r'\b([A-Z]{2}): \["([^"]+)"', J)}

src = (CD / "cd-data.js").read_text(encoding="utf-8")
pre, body = src.split("window.CD=", 1)
data = json.loads(body.rstrip().rstrip(";"))
old = data["decisions"]; N0 = len(old)
byid = {d["id"]: d for d in old}

# 1. official links for decisions already on the site
for did, srcs in IN["links"].items():
    d = byid[did]
    have = {s["u"].rstrip("/") for s in d["src"]}
    d["src"] = [s for s in srcs if s["u"].rstrip("/") not in have] + d["src"]
    page = CD / "d" / did / "index.html"
    if page.exists():
        t = page.read_text(encoding="utf-8")
        items = "".join(f'<li><a href="{E(s["u"])}" rel="noopener">{E(s["t"])}</a></li>' for s in srcs if s["u"].rstrip("/") not in have)
        t = t.replace("<h2>Sources</h2><ul>", "<h2>Sources</h2><ul>" + items, 1)
        page.write_text(t, encoding="utf-8")

# 2. new decisions
add = [e for e in IN["new"] if e["id"] not in byid]
clean = [{k: v for k, v in e.items() if k != "title_local"} for e in add]
data["decisions"] = old + clean
data["date"] = DATE
N1 = len(data["decisions"])
pre = pre.replace("2026-11-01", DATE)
(CD / "cd-data.js").write_text(pre + "window.CD=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")

j = json.load(open(CD / "data/decisions.json", encoding="utf-8"))
jb = {d["id"]: d for d in j["decisions"]}
for did in IN["links"]:
    if did in jb:
        jb[did]["src"] = byid[did]["src"]
j["decisions"] = j["decisions"] + clean; j["date"] = DATE
json.dump(j, open(CD / "data/decisions.json", "w", encoding="utf-8"), ensure_ascii=False)

rows = list(csv.DictReader(open(CD / "data/decisions.csv", encoding="utf-8")))
for r in rows:
    if r["id"] in IN["links"]:
        r["sources"] = " | ".join(s["u"] for s in byid[r["id"]]["src"])
rows += [to_row(e) for e in clean]
with open(CD / "data/decisions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, COLS); w.writeheader(); w.writerows(rows)

# sources.csv: count new decisions per database
srows = list(csv.DictReader(open(CD / "data/sources.csv", encoding="utf-8")))
cnt = {}
for e in clean:
    cnt[e["src"][0]["t"]] = cnt.get(e["src"][0]["t"], 0) + 1
for label, n in cnt.items():
    base = label.replace(" (secondary source)", "")
    hit = [r for r in srows if r["database"] == base or r["database"].startswith(base.split(" (")[0])]
    if hit:
        hit[0]["decisions_linked"] = str(int(hit[0]["decisions_linked"] or 0) + n)
    else:
        url = next(s["u"] for e in clean for s in e["src"] if s["t"] == label)
        host = re.sub(r"^https?://", "", url).split("/")[0]
        srows.append({"database": base, "run_by": "", "site": host,
                      "kind": "secondary" if "secondary" in label else "official",
                      "decisions_linked": str(n), "home": "https://" + host + "/"})
srows.sort(key=lambda r: -int(r["decisions_linked"] or 0))
with open(CD / "data/sources.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, list(srows[0].keys())); w.writeheader(); w.writerows(srows)

# 3. static page per new decision
tpl = (CD / "d/c-h-kr-ccourt-2020hun-ma1079-2024/index.html").read_text(encoding="utf-8")
head, rest = tpl.split("<main", 1); main, foot = rest.split("</main>", 1)
ld_re = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)
LV = {"apex": "Highest court", "appeal": "Appeal court", "first": "First-instance court", "regional": "Regional court or body"}
BR = {"administrative": "Administrative (challenge to a government decision)", "constitutional": "Constitutional and human rights",
      "criminal": "Criminal", "private": "Private dispute (labor, contract, tort)"}
LANG = {"KR": "ko", "JP": "ja", "MO": "zh-Hant", "QA": "ar"}


def page(e):
    cname = CN.get(e["cc"], e["cc"]); yr = e["date"][:4]
    t = f"{e['name']} ({cname}{', ' + yr if yr else ''})"
    h = re.sub(r"<title>.*?</title>", f"<title>{E(t)} · Institute for Migrant Rights</title>", head, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(e["plain"])}">', h)
    h = h.replace("c-h-kr-ccourt-2020hun-ma1079-2024", e["id"])
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": e["name"], "headline": t, "description": e["plain"],
          "url": f"https://theimr.org/court-decisions/d/{e['id']}/", "inLanguage": ["en", "id"],
          "about": f"Court decision on migrants' rights: {e['court']}, {cname}, {e['date']}", "dateModified": DATE,
          "isAccessibleForFree": True,
          "isPartOf": {"@type": "Dataset", "name": "Court Decisions", "url": "https://theimr.org/court-decisions/"},
          "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
          "citation": e["cite"], "sameAs": [s["u"] for s in e["src"]]}
    h = ld_re.sub(lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", h)
    local = (f'<p>Title in the original language: <span lang="{LANG.get(e["cc"], "en")}">{E(e["title_local"])}</span></p>'
             if e.get("title_local") else "")
    held = f'<h2>What the court held (from its published summary)</h2><p>{E(e["held"])}</p>\n' if e.get("held") else ""
    m = (f'<main style="padding: 48px 0 72px" id="court-decision"><div class="g-wrap" style="max-width:820px;margin:0 auto;padding:0 24px">\n'
         f'<p class="g-note"><a href="/court-decisions/">Court Decisions</a> › {E(cname)}</p>\n<h1>{E(e["name"])}</h1>\n'
         f'<p><b>{E(e["court"])}</b> · {E(cname)} · {E(e["date"] or "date to be confirmed")} · {LV.get(e["level"], "")}</p>\n'
         f'<p>Citation: {E(e["cite"])}<br>Type of case: {BR.get(e["branch"], "")}<br>Outcome: Outcome to be confirmed</p>\n{local}\n'
         '<p class="g-note"><b>Unverified: unchecked candidate.</b> This decision was found and described with AI help from an official or free law database. '
         'Nobody has yet read the judgment and written it up, so the summary below describes the subject only.</p>\n'
         f'<h2>Subject</h2><p>{E(e["plain"])}</p>\n{held}<h2 lang="id">Pokok perkara</h2><p lang="id">{E(e["plain_id"])}</p>\n'
         '<h2>Sources</h2><ul>' + "".join(f'<li><a href="{E(s["u"])}" rel="noopener">{E(s["t"])}</a></li>' for s in e["src"]) + '</ul>\n'
         f'<p><a href="/court-decisions/#d/{e["id"]}">Open this decision in the interactive collection</a> (compare, filter, Indonesian view, downloads).</p>\n'
         f'<p class="g-note">Cite as: Institute for Migrant Rights (2026), Migration Jurisprudence from the South: Court Decisions, version 0.1, https://theimr.org/court-decisions/d/{e["id"]}/. This page summarizes a court decision for research and advocacy; it is not legal advice.</p>\n'
         f'<p><a href="/court-decisions/all/#c-{cname.lower().replace(" ", "-")}">More decisions from {E(cname)} →</a></p></div>')
    return h + m + "</main>" + foot


for e in add:
    p = CD / "d" / e["id"]; p.mkdir(parents=True, exist_ok=True)
    (p / "index.html").write_text(page(e), encoding="utf-8")

# 4. all-decisions list
A = (CD / "all/index.html").read_text(encoding="utf-8")


def li(e):
    return (f'<li><a href="/court-decisions/d/{e["id"]}/">{E(e["name"])}</a> '
            f'<span class="g-note">{E(e["court"])} · {e["date"][:4] or "n.d."}</span></li>')


UL = '<ul style="padding-left:18px;line-height:1.5">'
for cc in sorted({e["cc"] for e in add}):
    es = sorted([e for e in add if e["cc"] == cc], key=lambda e: e["date"], reverse=True)
    cname = CN.get(cc, cc); anchor = "c-" + cname.lower().replace(" ", "-")
    m = re.search(rf'<h2 id="{re.escape(anchor)}">{re.escape(cname)} <span class="g-note">\((\d+)\)</span></h2>{re.escape(UL)}(.*?)</ul>', A, re.S)
    if m:
        n = int(m.group(1)) + len(es)
        A = A[:m.start()] + f'<h2 id="{anchor}">{cname} <span class="g-note">({n})</span></h2>{UL}{m.group(2)}{"".join(map(li, es))}</ul>' + A[m.end():]
        continue
    sec = f'<h2 id="{anchor}">{cname} <span class="g-note">({len(es)})</span></h2>{UL}{"".join(map(li, es))}</ul>\n'
    hs = [(mm.start(), mm.group(1)) for mm in re.finditer(r'<h2 id="c-[^"]*">([^<]*?) <span', A)]
    pos = next((s for s, nm in hs if nm > cname and not nm.startswith("Americas")), None)
    if pos is None:  # after the last country section
        last = hs[-1][0]; pos = A.index("</ul>", last) + len("</ul>\n")
    A = A[:pos] + sec + A[pos:]
    # country jump links
    links = [(mm.start(), mm.group(2)) for mm in re.finditer(r'<a href="#(c-[^"]*)">([^<]*)</a>', A)]
    after = next((s for s, nm in links if nm > cname and not nm.startswith("Americas")), None)
    if after is not None:
        A = A[:after] + f'<a href="#{anchor}">{cname}</a> · ' + A[after:]
A = A.replace(f"<p>{N0} decisions on migrant workers", f"<p>{N1} decisions on migrant workers")
(CD / "all/index.html").write_text(A, encoding="utf-8")

# plain list
D = (CD / "d/index.html").read_text(encoding="utf-8")
items = "".join(f'<li><a href="/court-decisions/d/{e["id"]}/">{E(e["name"])}</a> ({CN.get(e["cc"], e["cc"])}, {e["date"][:4] or "n.d."})</li>\n' for e in add)
k = D.index("All decisions: list"); k2 = D.index("</ul>", k)
D = D[:k2] + items + D[k2:]
D = D.replace(f"all {N0} court decisions", f"all {N1} court decisions").replace(f"as plain links. {N0} decisions.", f"as plain links. {N1} decisions.")
(CD / "d/index.html").write_text(D, encoding="utf-8")

S = (SITE / "sitemap.xml").read_text(encoding="utf-8")
S = S.replace("</urlset>", "".join(f'  <url><loc>https://theimr.org/court-decisions/d/{e["id"]}/</loc><lastmod>{DATE}</lastmod></url>\n' for e in add) + "</urlset>")
(SITE / "sitemap.xml").write_text(S, encoding="utf-8")

# homepage unit chart: one square per decision, new ones are "to be checked"
H = (SITE / "index.html").read_text(encoding="utf-8")
i = H.find('class="units"'); k = H.find("</div>", i)
if i > 0:
    H = H[:k] + "".join(f'<i class="" title="{E(e["name"])}"></i>' for e in add) + H[k:]
    m = re.search(r"To be checked \((\d+)\)", H)
    if m:
        H = H[:m.start()] + f"To be checked ({int(m.group(1)) + len(add)})" + H[m.end():]
    (SITE / "index.html").write_text(H, encoding="utf-8")

for f in [CD / "index.html", SITE / "index.html", SITE / "databases/index.html"]:
    if f.exists():
        t = f.read_text(encoding="utf-8")
        t2 = re.sub(rf"\b{N0}( court decisions| decisions| squares| putusan)", lambda m: f"{N1}{m.group(1)}", t)
        f.write_text(t2, encoding="utf-8"); print(f.relative_to(SITE), t.count(str(N0)), "->", t2.count(str(N1)))
print("decisions before", N0, "added", len(add), "now", N1, "| existing entries given official links", len(IN["links"]))
