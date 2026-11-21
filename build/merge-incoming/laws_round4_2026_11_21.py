"""Publish the laws of the South and Southeast Asia crawl and the sources Pranoto sent on 21 November 2026 (PR #56).

Usage: python3 build/merge-incoming/laws_round4_2026_11_21.py SITE
Idempotent: rows already in a table (same link, or same country and title) are not added twice.

1. Countries of origin (BD, VN, PK, NP, LK, ID, IN, KH, PH) from data/countries-of-origin/incoming/laws-2026-11-21.csv
   -> data/countries-of-origin/laws-policies.csv and site/countries-of-origin/oc-data.js. Rows marked "adds deep link"
   replace a portal front page with the text itself. LawPhil is flagged as a secondary source, NATLEX as a UN copy.
2. Thailand (Department of Employment copies) and one Malaysian link from data/southeast-asia/incoming/laws-2026-11-21.csv
   -> data/southeast-asia/domestic-laws.csv and site/southeast-asia/sea-data.js. The 2018 amending ordinance and the
   consolidated text belong to the 2017 Royal Ordinance row already on the page, so its link moves to the consolidated
   text instead of adding two rows.
3. Africa, Middle East and Pacific update files (*-update.csv) -> data/migration-law/national-laws.csv: new rows are added,
   rows already in the table get the checked dates, links and notes. LEAD rows (no official text yet) wait.
4. Gulf: UAE Federal Decree-Law 24/2023 added; Federal Law 51/2006 marked as repealed by it (Art. 26(1)), not amended.
Every new row is "Unverified". Descriptive only: no scores or rankings.
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
DATE = "2026-11-21"
D = ROOT / "data"


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def write(p, fields, rs):
    eol = "\r\n" if p.exists() and b"\r\n" in p.read_bytes()[:4000] else "\n"  # keep the file's own line endings
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore", restval="", lineterminator=eol); w.writeheader(); w.writerows(rs)


slug = lambda s: re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
J = lambda v: json.dumps(v, ensure_ascii=False)


def link_kind(url, tier):
    t = tier.lower()
    if "lawphil" in url or t.startswith("secondary") or "law firm" in t:
        return "secondary"
    if "natlex" in url or "sherloc" in url or "refworld" in url or t.startswith("un"):
        return "un"
    return "guidance" if "guidance" in t else "text"


def insert_js(js, s, line, prefix):
    """Insert a law line after the last line of the same state inside the laws: [ ... ] array."""
    L = js.split("\n")
    a = next(i for i, ln in enumerate(L) if ln.strip() == "laws: [")
    b = next(i for i in range(a, len(L)) if L[i].strip() in ("],", "]"))
    last = max((i for i in range(a, b) if L[i].lstrip().startswith(prefix + J(s))), default=b - 1)
    if not L[last].rstrip().endswith(","):
        L[last] = L[last].rstrip() + ","
    L.insert(last + 1, line)
    return "\n".join(L)


def set_js_url(js, s, title_part, url, link):
    L = js.split("\n")
    n = 0
    for i, ln in enumerate(L):
        if ln.lstrip().startswith("{s:" + J(s)) and title_part in ln and "url:" in ln:
            L[i] = re.sub(r'url:"[^"]*", link:"[^"]*"', f"url:{J(url)}, link:{J(link)}", ln); n += 1
    return "\n".join(L), n


TYPE = {"law": "statute", "act": "statute", "ordinance": "statute", "regulation": "regulation", "policy": "policy",
        "bill": "draft", "official guidance": "guidance", "decree-law": "statute", "law (amending law)": "statute"}

# ---------------------------------------------------------------- 1. countries of origin
OCP = D / "countries-of-origin/laws-policies.csv"
OC = rows(OCP); oc_fields = list(OC[0].keys())
ocp = SITE / "countries-of-origin/oc-data.js"; ocjs = ocp.read_text(encoding="utf-8")
have = {r["url"] for r in OC} | {(r["s"], norm(r["title"])) for r in OC}
# title fragments of the rows on the site that get a deep link (site_status "adds deep link" / "full-text link")
DEEP = {"PK": "Domestic Workers", "IN": "Emigration Act", "LK": "Bureau of Foreign Employment", "ID": None, "VN": None, "PH": None}
oc_add, oc_up = Counter(), []
# Titles the crawl cut short (it kept only the link text); full titles from the official listing, keyed by number.
FIX = {"145/2026/VBHN-LQ-VPQH": "Law on Vietnamese Workers Working Abroad under Contracts, consolidated text (2026)",
       "8/VBHN-BNV": "Decree 112/2021/ND-CP detailing the Guest Workers Law, consolidated text (2026)",
       "45/2019/QH14": "Labour Code (No. 45/2019/QH14)",
       "51/2019/QH14": "Law amending the Law on Entry, Exit, Transit and Residence of Foreigners (No. 51/2019/QH14)",
       "23/2023/QH15": "Law amending the Law on Exit and Entry of Vietnamese Citizens and the Law on Entry, Exit, Transit and Residence of Foreigners (No. 23/2023/QH15)",
       "62/VBHN-VPQH": "Law on Entry, Exit, Transit and Residence of Foreigners, consolidated text (2026)",
       "PP No. 10 Tahun 2020": "Government Regulation No. 10 of 2020 on placement of migrant workers by BP2MI",
       "Kepmenaker No. 349 Tahun 2019": "Ministerial Decision No. 349 of 2019 on positions closed to foreign workers"}
for r in rows(D / "countries-of-origin/incoming/laws-2026-11-21.csv"):
    s, title, url, st = r["country"], FIX.get(r["number"], r["title"]), r["official_link"], r["site_status"]
    kind = link_kind(url, r["source_tier"])
    if st.startswith("ON SITE"):
        if "same link" in st:
            continue
        m = re.search(r"laws-policies\.csv ([a-z]{2}-\d{4}-[a-z0-9-]+)", st)
        hit = [x for x in OC if m and x["id"].startswith(m.group(1))]
        if not hit:  # match by a distinctive part of the title or the number in the status
            key = re.search(r"\((?:laws-policies\.csv(?: \+ instruments\.csv [A-Z0-9-]+)? )?\(?([^;)]+)", st)
            frag = {"IN": "Emigration Act", "LK": "Bureau of Foreign Employment", "VN-69": "69/2020",
                    "Decree 112": "112", "N-VN-69": "69/2020", "Decree 12/2022": "12/2022", "N-ID-18": "18 of 2017", "PP 59": "59"}
            for k, v in frag.items():
                if k in st or k == s:
                    hit = [x for x in OC if x["s"] == s and v in (x["title"] + " " + x.get("orig", ""))]
                    if hit:
                        break
        if not hit:
            oc_up.append(("no match", s, title)); continue
        x = hit[0]
        if x["url"] == url:
            continue
        old_title = x["title"]; x["url"] = url; x["link"] = kind; x["last_checked"] = DATE
        ocjs, n = set_js_url(ocjs, s, "title:" + J(old_title), url, kind)
        oc_up.append((s, old_title[:50], kind, n)); have.add(url)
        continue
    if url in have or (s, norm(title)) in have:
        continue
    year = (r["adopted"] or "")[:4]
    typ = TYPE.get(r["type"].lower(), "statute")
    topic = (r["topic"] or "").replace(";", ",")
    topic = (topic[0].upper() + topic[1:] if topic else "Migration-related law") + " (added 2026-11-21, unverified)"
    x = {"id": f"{s.lower()}-{year or 'nd'}-{slug(title)}"[:48].rstrip("-"), "s": s, "title": title, "orig": r["title_original"],
         "year": year, "amended": r["amended"], "type": typ, "topic": topic, "url": url, "link": kind, "last_checked": DATE}
    OC.append(x); have.add(url); have.add((s, norm(title))); oc_add[s] += 1
    line = ("    {s:%s, title:%s, orig:%s, year:%s, amended:%s, type:%s, topic:%s, url:%s, link:%s},"
            % (J(s), J(title), J(x["orig"]), J(year), J(x["amended"]), J(typ), J(topic), J(url), J(kind)))
    ocjs = insert_js(ocjs, s, line, "{s:")
order = []
for r in OC:
    if r["s"] not in order:
        order.append(r["s"])
OC.sort(key=lambda r: order.index(r["s"]))
write(OCP, oc_fields, OC)
ocp.write_text(ocjs, encoding="utf-8")
print("Countries of origin: added", sum(oc_add.values()), dict(oc_add))
print("  links upgraded:", oc_up)

# ---------------------------------------------------------------- 2. Southeast Asia (Thailand, Malaysia link)
SLP = D / "southeast-asia/domestic-laws.csv"
SL = rows(SLP); sl_fields = list(SL[0].keys())
sp = SITE / "southeast-asia/sea-data.js"; sjs = sp.read_text(encoding="utf-8")
shave = {r["url"] for r in SL} | {(r["s"], norm(r["title"])) for r in SL}
ALL_TH = "TH-MOU TH-AGR TH-FSH"
sea_add = 0
for r in rows(D / "southeast-asia/incoming/laws-2026-11-21.csv"):
    s, title, url = r["country"], r["title"], r["official_link"]
    if s == "TH" and ("No. 2" in title or title.startswith("consolidated")):
        continue  # covered by the 2017 Royal Ordinance row (amended 2018)
    if s == "TH" and r["site_status"].startswith("ON SITE"):
        url = "https://www.doe.go.th/prd/download/download_by_pool_file/61900"  # DOE consolidated text to 16 Oct 2018
        for x in SL:
            if x["s"] == "TH" and x["title"].startswith("Royal Ordinance on the Management"):
                if x["url"] != url:
                    sjs, n = set_js_url(sjs, "TH", "title:" + J(x["title"]), url, "text")
                    x["url"], x["link"], x["last_checked"] = url, "text", DATE
                    print("  TH Royal Ordinance link ->", url, n)
        continue
    if s == "MY":
        if not url:
            continue
        for x in SL:
            if x["s"] == "MY" and x["title"].startswith("Immigration Act 1959") and x["url"] != url:
                sjs, n = set_js_url(sjs, "MY", "title:" + J(x["title"]), url, "text")
                x["url"], x["link"], x["last_checked"] = url, "text", DATE
                print("  MY Immigration Act link ->", url, n)
        continue
    if url in shave or (s, norm(title)) in shave:
        continue
    year = (r["adopted"] or "")[:4]
    typ = TYPE.get(r["type"].lower(), "regulation")
    groups = "TH-MOU" if re.search(r"MOU", title) else ALL_TH
    topic = re.sub(r"^Listed on the portal on 2026-11-21; (date [0-9-]+ from the listing|year from the title)\.\s*", "", r["note"]).strip()
    topic = (topic or (r["topic"] or "Foreign workers").replace(";", ",")) + " Department of Employment copy (added 2026-11-21, unverified)."
    topic = topic.replace(". Department", "; Department")
    x = {"id": f"th-{year}-{slug(title)}"[:48].rstrip("-"), "s": s, "title": title, "orig": r["title_original"], "year": year,
         "amended": r["amended"], "type": typ, "topic": topic, "groups": groups, "url": url, "link": "text", "last_checked": DATE}
    SL.append(x); shave.add(url); sea_add += 1
    line = ("    {s:%s, title:%s, orig:%s, year:%s, amended:%s, type:%s, topic:%s, groups:%s, url:%s, link:%s},"
            % (J(s), J(title), J(x["orig"]), J(year), J(x["amended"]), J(typ), J(topic), J(groups), J(url), J("text")))
    sjs = insert_js(sjs, s, line, "{s:")
write(SLP, sl_fields, SL)
sp.write_text(sjs, encoding="utf-8")
print("Southeast Asia: Thai laws added", sea_add)

# ---------------------------------------------------------------- 3. national laws (Africa, Middle East, Pacific)
NL_FIELDS = ["id", "s", "region", "title", "orig", "no", "year", "amended", "type", "topic", "farm_domestic",
             "url", "link", "source_tier", "status", "note", "last_checked"]
NLP = D / "migration-law/national-laws.csv"
NL = rows(NLP)
REGION = {"africa": "africa", "middle-east": "mideast", "pacific": "pacific"}
nl_add, nl_up, nl_wait = Counter(), [], []
for f, region in REGION.items():
    for r in rows(D / f"{f}/incoming/laws-2026-11-21-update.csv"):
        s, title, url, st = r["country"], r["title"], r["official_link"], r["site_status"]
        if st.startswith("LEAD"):
            nl_wait.append((s, title[:50])); continue
        m = re.search(r"national-laws\.csv ([a-z0-9-]+)", st)
        hit = [x for x in NL if (m and x["id"] == m.group(1)) or (x["s"] == s and (norm(x["title"]) == norm(title) or (url and x["url"] == url)))]
        if not hit and st.startswith("IN INCOMING"):  # published in round 3 under the incoming title
            base = norm(re.sub(r",? \d{4}.*$|\s*\(.*$", "", title))[:18]
            hit = [x for x in NL if x["s"] == s and norm(x["title"]).startswith(base)]
        if "as enacted" in st:  # the bill text: the Act is already on the site
            continue
        if hit:
            x = hit[0]
            keep_link = "keep SHERLOC" in st
            if url and not keep_link and x["url"] != url:
                x["url"] = url; x["link"] = link_kind(url, r["source_tier"]); x["source_tier"] = r["source_tier"]
            if not x["year"] and r["adopted"]:
                x["year"] = r["adopted"][:4]
            if r["amended"]:
                x["amended"] = r["amended"]
            x["note"] = r["note"]; x["last_checked"] = DATE
            nl_up.append((s, x["id"])); continue
        year = (r["adopted"] or "")[:4]
        rid = f"{s.lower()}-{year or 'nd'}-{slug(title)}"[:60].rstrip("-"); n = 2
        while any(y["id"] == rid for y in NL):
            rid = f"{rid[:57]}-{n}"; n += 1
        farm = r["covers_farm_or_domestic_work"]
        NL.append({"id": rid, "s": s, "region": region, "title": title, "orig": r["title_original"], "no": r["number"],
                   "year": year, "amended": r["amended"], "type": TYPE.get(r["type"].lower(), "statute"),
                   "topic": r["topic"], "farm_domestic": "" if farm.startswith("no specific") else farm, "url": url,
                   "link": link_kind(url, r["source_tier"]), "source_tier": r["source_tier"], "status": "Unverified",
                   "note": r["note"], "last_checked": DATE})
        nl_add[s] += 1
        if s == "ZM" and title.startswith("Refugees Act"):
            for y in NL:
                if y["s"] == "ZM" and y["title"].startswith("Refugees (Control) Act") and "Repealed" not in y["note"]:
                    y["note"] = ("Repealed and replaced by the Refugees Act No. 1 of 2017. " + y["note"]).strip()
order = {"africa": 0, "mideast": 1, "asia": 2, "pacific": 3}
NL.sort(key=lambda r: (order.get(r["region"], 9), r["s"], r["year"] or "0", r["title"]))
write(NLP, NL_FIELDS, NL)
print("national laws:", len(NL), "added", sum(nl_add.values()), dict(nl_add))
print("  updated:", nl_up)
print("  waiting for an official text:", nl_wait)

# ---------------------------------------------------------------- 4. Gulf (UAE)
GLP = D / "gcc/domestic-laws.csv"
GL = rows(GLP); gl_fields = list(GL[0].keys())
gp = SITE / "gcc/gcc-data.js"; G = gp.read_text(encoding="utf-8").split("\n")
gi = next(i for i, ln in enumerate(G) if ln.startswith("GCC.laws = "))
GJ = json.loads(G[gi][len("GCC.laws = "):].rstrip().rstrip(";"))
REP = "Federal Decree-Law 24/2023 (repealed this Law, Art. 26(1); in force 16 Sep 2023)"
GROUPS_51 = "All persons. Historic: repealed by Federal Decree-Law 24/2023 (Art. 26(1)), in force 16 Sep 2023; amended earlier by Federal Law 1/2015"
for coll in (GL, GJ):
    for x in coll:
        if x["s"] == "AE" and x.get("no") == "Federal Law 51":
            x["amended"] = REP; x["groups"] = GROUPS_51
            if "last_checked" in x:
                x["last_checked"] = DATE
NEW = {"s": "AE", "title": "Federal Decree-Law on Combating Human Trafficking", "orig": "مرسوم بقانون اتحادي في شأن مكافحة الاتجار بالبشر",
       "no": "Federal Decree-Law 24", "year": "2023", "amended": "", "type": "statute", "topic": "trafficking",
       "groups": "All persons; forced labour and forced service count as trafficking (Art. 2); victim consent irrelevant (Art. 3); hiding or destroying a victim's documents is an offence (Art. 11); in force 16 Sep 2023",
       "url": "https://uaelegislation.gov.ae/en/legislations/2127", "link": "text", "checked": "yes"}
if not any(x.get("no") == NEW["no"] and x["s"] == "AE" for x in GJ):
    i51 = next(i for i, x in enumerate(GJ) if x["s"] == "AE" and x.get("no") == "Federal Law 51")
    GJ.insert(i51 + 1, NEW)
    j51 = next(i for i, x in enumerate(GL) if x["s"] == "AE" and x.get("no") == "Federal Law 51")
    GL.insert(j51 + 1, dict(NEW, id="ae-2023-federal-decree-law-on-combating-human-traf", last_checked=DATE))
    print("Gulf: UAE Federal Decree-Law 24/2023 added")
G[gi] = "GCC.laws = " + json.dumps(GJ, ensure_ascii=False) + ";"
gp.write_text("\n".join(G), encoding="utf-8")
write(GLP, gl_fields, GL)
