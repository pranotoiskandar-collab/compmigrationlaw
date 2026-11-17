"""Add status-C candidates to an unzipped copy of theimr.org.

Usage: python3 tools/patch_imr_site.py SITE_DIR REGION/tables/imr_candidates.json REGION/scripts
Updates cd-data.js, decisions.json/.csv, sources.csv, static pages, the all-decisions lists,
sitemap.xml and the decision counts. The home page squares are not updated by this script.
"""
import json, re, csv, html, sys, io
from pathlib import Path
SITE = Path(sys.argv[1]); NEW = json.load(open(sys.argv[2], encoding="utf-8")); DATE = "2026-11-17"
CD = SITE / "court-decisions"
src = (CD / "cd-data.js").read_text(encoding="utf-8")
pre, body = src.split("window.CD=", 1)
data = json.loads(body.rstrip().rstrip(";"))
old = data["decisions"]
N0 = len(old)
CN = {"HK": "Hong Kong", "KR": "South Korea", "JP": "Japan", "MO": "Macau", "TW": "Taiwan"}

def norm(c):
    c = c.split(";")[0].lower()
    return re.sub(r"[^a-z0-9]", "", c)
have = set()
for d in old:
    for part in d.get("cite", "").split(";"):
        n = re.sub(r"[^a-z0-9]", "", part.lower())
        if len(n) > 5: have.add(n)
ids = {d["id"] for d in old}
add = []
for e in NEW:
    if norm(e["cite"]) in have or e["id"] in ids:
        continue
    e = {k: v for k, v in e.items() if k != "title_local"} | {"_local": e.get("title_local", "")}
    add.append(e)
print("existing", N0, "new", len(NEW), "added", len(add), "skipped as duplicates", len(NEW) - len(add))
clean_add = [{k: v for k, v in e.items() if k != "_local"} for e in add]
data["decisions"] = old + clean_add
data["date"] = DATE
N1 = len(data["decisions"])
pre = pre.replace("2026-11-01", DATE)
(CD / "cd-data.js").write_text(pre + "window.CD=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
j = json.load(open(CD / "data/decisions.json", encoding="utf-8"))
j["decisions"] = j["decisions"] + clean_add; j["date"] = DATE
json.dump(j, open(CD / "data/decisions.json", "w", encoding="utf-8"), ensure_ascii=False)
# decisions.csv
sys.path.insert(0, sys.argv[3]); from imr_candidates import to_row, COLS
with open(CD / "data/decisions.csv", "a", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, COLS)
    for e in clean_add: w.writerow(to_row(e))
# sources.csv
rows = list(csv.DictReader(open(CD / "data/sources.csv", encoding="utf-8")))
cnt = {}
for e in clean_add: cnt[e["src"][0]["t"]] = cnt.get(e["src"][0]["t"], 0) + 1
SROW = {"HKLII": "HKLII", "Courts in Japan (courts.go.jp)": "Courts in Japan",
        "law.go.kr (National Law Information Center)": None, "Courts of Macau (court.gov.mo)": None}
newsrc = {"law.go.kr (National Law Information Center)": dict(database="National Law Information Center (law.go.kr)", run_by="Ministry of Government Legislation, Korea", site="law.go.kr", kind="official", home="https://www.law.go.kr/"),
          "Courts of Macau (court.gov.mo)": dict(database="Courts of Macau", run_by="Courts of the Macau SAR", site="court.gov.mo", kind="official", home="https://www.court.gov.mo/")}
for t, n in cnt.items():
    name = SROW.get(t)
    hit = [r for r in rows if r["database"] == name] if name else []
    if hit: hit[0]["decisions_linked"] = str(int(hit[0]["decisions_linked"]) + n)
    else: rows.append(newsrc[t] | {"decisions_linked": str(n)})
rows.sort(key=lambda r: -int(r["decisions_linked"] or 0))
with open(CD / "data/sources.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# static pages
tpl = (CD / "d/c-h-kr-ccourt-2020hun-ma1079-2024/index.html").read_text(encoding="utf-8")
head, rest = tpl.split("<main", 1); main, foot = rest.split("</main>", 1)
ld_re = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)
LV = {"apex": "Highest court", "appeal": "Appeal court", "first": "First-instance court"}
BR = {"administrative": "Administrative (challenge to a government decision)", "constitutional": "Constitutional and human rights",
      "criminal": "Criminal", "private": "Private dispute (labor, contract, tort)"}
E = html.escape
def page(e):
    cname = CN[e["cc"]]; yr = e["date"][:4]
    t = f"{e['name']} ({cname}{', ' + yr if yr else ''})"
    h = head
    h = re.sub(r"<title>.*?</title>", f"<title>{E(t)} · Institute for Migrant Rights</title>", h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(e["plain"])}">', h)
    h = h.replace("c-h-kr-ccourt-2020hun-ma1079-2024", e["id"])
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": e["name"], "headline": t, "description": e["plain"],
          "url": f"https://theimr.org/court-decisions/d/{e['id']}/", "inLanguage": ["en", "id"],
          "about": f"Court decision on migrants' rights: {e['court']}, {cname}, {e['date']}", "dateModified": DATE, "isAccessibleForFree": True,
          "isPartOf": {"@type": "Dataset", "name": "Court Decisions", "url": "https://theimr.org/court-decisions/"},
          "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
          "citation": e["cite"], "sameAs": [s["u"] for s in e["src"]]}
    h = ld_re.sub(lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", h)
    local = f'<p>Title in the original language: <span lang="{ {"KR":"ko","JP":"ja","MO":"zh-Hant"}.get(e["cc"],"en") }">{E(e["_local"])}</span></p>' if e.get("_local") else ""
    m = (f'<main style="padding: 48px 0 72px" id="court-decision"><div class="g-wrap" style="max-width:820px;margin:0 auto;padding:0 24px">\n'
         f'<p class="g-note"><a href="/court-decisions/">Court Decisions</a> › {E(cname)}</p>\n<h1>{E(e["name"])}</h1>\n'
         f'<p><b>{E(e["court"])}</b> · {E(cname)} · {E(e["date"] or "date to be confirmed")} · {LV[e["level"]]}</p>\n'
         f'<p>Citation: {E(e["cite"])}<br>Type of case: {BR[e["branch"]]}<br>Outcome: Outcome to be confirmed</p>\n{local}\n'
         '<p class="g-note"><b>Unchecked candidate.</b> This decision has been located in an official or free law database but has not yet been read and written up. The summary below describes the subject only.</p>\n'
         f'<h2>Subject</h2><p>{E(e["plain"])}</p>\n<h2 lang="id">Pokok perkara</h2><p lang="id">{E(e["plain_id"])}</p>\n'
         '<h2>Sources</h2><ul>' + "".join(f'<li><a href="{E(s["u"])}" rel="noopener">{E(s["t"])}</a></li>' for s in e["src"]) + '</ul>\n'
         f'<p><a href="/court-decisions/#d/{e["id"]}">Open this decision in the interactive collection</a> (compare, filter, Indonesian view, downloads).</p>\n'
         f'<p class="g-note">Cite as: Institute for Migrant Rights (2026), Migration Jurisprudence from the South: Court Decisions, version 0.1, https://theimr.org/court-decisions/d/{e["id"]}/. This page summarizes a court decision for research and advocacy; it is not legal advice.</p>\n'
         f'<p><a href="/court-decisions/all/#c-{cname.lower().replace(" ", "-")}">More decisions from {E(cname)} →</a></p></div>')
    return h + m + "</main>" + foot
for e in add:
    p = CD / "d" / e["id"]; p.mkdir(parents=True, exist_ok=True)
    (p / "index.html").write_text(page(e), encoding="utf-8")
# all/index.html: append items per country, update counts
A = (CD / "all/index.html").read_text(encoding="utf-8")
def li(e):
    return f'<li><a href="/court-decisions/d/{e["id"]}/">{E(e["name"])}</a> <span class="g-note">{E(e["court"])} · {e["date"][:4] or "n.d."}</span></li>'
for cc in sorted({e["cc"] for e in add}):
    es = sorted([e for e in add if e["cc"] == cc], key=lambda e: e["date"], reverse=True)
    cname = CN[cc]; anchor = "c-" + cname.lower().replace(" ", "-")
    m = re.search(rf'<h2 id="{anchor}">{re.escape(cname)} <span class="g-note">\((\d+)\)</span></h2><ul style="padding-left:18px;line-height:1.5">(.*?)</ul>', A, re.S)
    if m:
        n = int(m.group(1)) + len(es)
        A = A[:m.start()] + f'<h2 id="{anchor}">{cname} <span class="g-note">({n})</span></h2><ul style="padding-left:18px;line-height:1.5">{m.group(2)}{"".join(map(li, es))}</ul>' + A[m.end():]
    else:
        # new country section: insert before the next alphabetical h2
        sec = f'<h2 id="{anchor}">{cname} <span class="g-note">({len(es)})</span></h2><ul style="padding-left:18px;line-height:1.5">{"".join(map(li, es))}</ul>\n'
        hs = [(mm.start(), mm.group(1)) for mm in re.finditer(r'<h2 id="c-[^"]*">([^<]*?) <span', A)]
        pos = next((s for s, nm in hs if nm > cname and not nm.startswith("Americas")), None)
        A = A[:pos] + sec + A[pos:]
        A = A.replace(f'<a href="#c-malawi">Malawi</a>', f'<a href="#{anchor}">{cname}</a> · <a href="#c-malawi">Malawi</a>') if cname == "Macau" else A
A = A.replace(f"<p>{N0} decisions on migrant workers", f"<p>{N1} decisions on migrant workers")
(CD / "all/index.html").write_text(A, encoding="utf-8")
# d/index.html plain list
D = (CD / "d/index.html").read_text(encoding="utf-8")
items = "".join(f'<li><a href="/court-decisions/d/{e["id"]}/">{E(e["name"])}</a> ({CN[e["cc"]]}, {e["date"][:4] or "n.d."})</li>\n' for e in add)
k = D.index("All decisions: list"); k2 = D.index("</ul>", k)
D = D[:k2] + items + D[k2:]
D = D.replace(f"all {N0} court decisions", f"all {N1} court decisions").replace(f"as plain links. {N0} decisions.", f"as plain links. {N1} decisions.")
(CD / "d/index.html").write_text(D, encoding="utf-8")
# sitemap
S = (SITE / "sitemap.xml").read_text(encoding="utf-8")
S = S.replace("</urlset>", "".join(f'  <url><loc>https://theimr.org/court-decisions/d/{e["id"]}/</loc><lastmod>{DATE}</lastmod></url>\n' for e in add) + "</urlset>")
(SITE / "sitemap.xml").write_text(S, encoding="utf-8")
# headline counts on other pages
for f in [CD / "index.html", SITE / "index.html"]:
    t = f.read_text(encoding="utf-8")
    t2 = re.sub(rf"\b{N0}( court decisions| decisions| squares)", lambda m: f"{N1}{m.group(1)}", t)
    f.write_text(t2, encoding="utf-8"); print(f, t.count(str(N0)), "->", t2.count(str(N1)))
print("total now", N1)
# country label for Macau in the interactive collection
J = (CD / "cd.js").read_text(encoding="utf-8")
if 'MO: ["Macau"' not in J:
    J = J.replace('HK: ["Hong Kong", "Hong Kong"],', 'HK: ["Hong Kong", "Hong Kong"], MO: ["Macau", "Makau"],', 1)
    (CD / "cd.js").write_text(J, encoding="utf-8")
