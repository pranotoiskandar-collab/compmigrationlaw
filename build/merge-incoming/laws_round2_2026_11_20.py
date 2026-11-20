"""Publish the incoming laws and instruments that were still waiting (Pranoto, 20 November 2026: "put all out").

Usage: python3 build/merge-incoming/laws_round2_2026_11_20.py SITE
Idempotent: rows already in a table (same official link, or same country and title) are skipped.

1. data/migration-law/national-laws.csv (new table): national laws of states that have no regional page of their own
   (Africa, the Pacific, the Middle East outside the GCC, and Macau, Mongolia and China), from
     data/africa/incoming/laws-2026-11-17.csv, data/pacific/incoming/laws-2026-11-20.csv,
     data/middle-east/incoming/laws-2026-11-20.csv, data/migration-law/incoming/jordan-laws-2026-11-18.csv,
     data/east-asia/incoming/migration-statutes-2026-11-17.csv (MO, MN, CN only; TW, KR, JP, HK are on /east-asia/).
   Every row is "Unverified". PacLII rows are flagged as a secondary source, SHERLOC rows as a UN-hosted copy.
2. Regional instruments (AU, EAC, SADC, Andean Community, EAEU) go into the Migration Law Atlas regional tier:
   data/migration-law/migration-norms.csv, the DM block in build/farmworker-norms/atlas-source/migration_block.js
   and the same block embedded in site/migration-law/index.html. South Africa's Immigration Act gets its DHA link.
3. Countries of origin: new laws and official-text links in data/countries-of-origin/laws-policies.csv and
   site/countries-of-origin/oc-data.js.
4. Gulf States: Qatar ratification decrees for labour agreements in data/gcc/frameworks.csv and site/gcc/gcc-data.js
   (new agreements added; for agreements already listed, the official decree link replaces a secondary link).
Descriptive only: no scores or rankings are added for national laws.
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
DATE = "2026-11-20"
D = ROOT / "data"


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def write(p, fields, rs):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore", restval=""); w.writeheader(); w.writerows(rs)


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ---------------------------------------------------------------- 1. national laws
NL_FIELDS = ["id", "s", "region", "title", "orig", "no", "year", "amended", "type", "topic", "farm_domestic",
             "url", "link", "source_tier", "status", "note", "last_checked"]
NLP = D / "migration-law/national-laws.csv"
NL = rows(NLP) if NLP.exists() else []
have = {r["url"] for r in NL} | {(r["s"], norm(r["title"])) for r in NL}
TYPE = {"law": "statute", "regulation": "regulation", "ministerial decision": "decision", "policy": "policy",
        "bill": "draft", "official guidance": "guidance", "bilateral agreement": "agreement", "act": "statute"}
REGION = {"ZA": "africa", "KE": "africa", "UG": "africa", "GH": "africa", "NG": "africa", "ZW": "africa",
          "EG": "mideast", "LB": "mideast", "IQ": "mideast", "IL": "mideast", "JO": "mideast",
          "MO": "asia", "MN": "asia", "CN": "asia"}


def link_kind(tier):
    t = tier.lower()
    if t.startswith("paclii"):
        return "secondary"
    if t.startswith("un-hosted"):
        return "un"
    if "guidance" in t:
        return "guidance"
    return "text"


def add_nl(s, title, orig, no, year, amended, typ, topic, farm, url, tier, note):
    front_page = re.fullmatch(r"https?://[^/]+/?", url or "") is not None  # several laws share a database front page
    if (url in have and not front_page) or (s, norm(title)) in have:
        return False
    rid = f"{s.lower()}-{year or 'nd'}-{slug(title)}"[:60].rstrip("-")
    n = 2
    while any(r["id"] == rid for r in NL):
        rid = f"{rid[:57]}-{n}"; n += 1
    NL.append({"id": rid, "s": s, "region": REGION.get(s, "pacific"), "title": title, "orig": orig, "no": no,
               "year": year, "amended": amended, "type": TYPE.get(typ.lower(), typ.lower() or "statute"), "topic": topic,
               "farm_domestic": farm, "url": url, "link": link_kind(tier), "source_tier": tier, "status": "Unverified",
               "note": note, "last_checked": DATE})
    have.add(url); have.add((s, norm(title)))
    return True


added = Counter()
for f in ["africa/incoming/laws-2026-11-17.csv", "pacific/incoming/laws-2026-11-20.csv", "middle-east/incoming/laws-2026-11-20.csv"]:
    for r in rows(D / f):
        if r["site_status"] != "new" or not r["country"]:
            continue  # link upgrades handled below; regional instruments go to the Atlas
        if add_nl(r["country"], r["title"], r["title_original"], r["number"], (r["adopted"] or "")[:4], r["amended"], r["type"],
                  r["topic"], r["covers_farm_or_domestic_work"], r["official_link"], r["source_tier"], r["note"]):
            added[r["country"]] += 1
for r in rows(D / "migration-law/incoming/jordan-laws-2026-11-18.csv"):
    if r["site_status"] != "new":
        continue
    typ = "regulation" if r["title"].startswith(("Regulation", "Instructions")) else "statute"
    if add_nl("JO", r["title"], r["title_original"], r["number"], r["adopted"][:4], "", typ, "", r["covers_farm_or_domestic_work"],
              r["official_link"], r["source_tier"], (r["note"] + f" Status on the portal: {r['status_on_portal']}.").strip()):
        added["JO"] += 1
EA_URL = {"Boletim Oficial (bo.io.gov.mo)": "https://bo.io.gov.mo/", "legalinfo.mn": "https://legalinfo.mn/",
          "National Database of Laws and Regulations (flk.npc.gov.cn)": "https://flk.npc.gov.cn/",
          "Ministry of Human Resources and Social Security": "https://www.mohrss.gov.cn/"}
for r in rows(D / "east-asia/incoming/migration-statutes-2026-11-17.csv"):
    if r["jurisdiction"] not in ("MO", "MN", "CN"):
        continue
    m = re.match(r"Law (\d+/\d{4}): (.*)", r["title_en"])
    title = r["title_en"]
    if add_nl(r["jurisdiction"], title, r["title_local"], m.group(1) if m else "", r["year"], "", r["type"],
              r["topic"], "farm work relevant" if r["farm_relevant"] == "yes" else "", EA_URL.get(r["official_source"], ""),
              f"official ({r['official_source']}); link to the database front page",
              ("Found in the East Asia crawl of 2026-11-17; the text was not opened. " + r["notes"]).strip()):
        added[r["jurisdiction"]] += 1
order = {"africa": 0, "mideast": 1, "asia": 2, "pacific": 3}
NL.sort(key=lambda r: (order.get(r["region"], 9), r["s"], r["year"] or "0", r["title"]))
write(NLP, NL_FIELDS, NL)
print("national laws:", len(NL), "added", sum(added.values()), dict(added))

# codebook for the new table
CBP = D / "migration-law/national-laws-codebook.csv"
write(CBP, ["variable", "definition", "values"], [
    {"variable": "id", "definition": "Stable identifier of the row", "values": "text"},
    {"variable": "s", "definition": "ISO 3166 code of the state that made the law", "values": "code"},
    {"variable": "region", "definition": "Region used for ordering", "values": "africa | mideast | asia | pacific"},
    {"variable": "title", "definition": "Title in English (official English title where one exists)", "values": "text"},
    {"variable": "orig", "definition": "Title in the original language, where recorded", "values": "text"},
    {"variable": "no", "definition": "Official number", "values": "text"},
    {"variable": "year", "definition": "Year adopted", "values": "YYYY"},
    {"variable": "amended", "definition": "Amending instruments or years, where recorded", "values": "text"},
    {"variable": "type", "definition": "Kind of instrument", "values": "statute | regulation | decision | policy | guidance | agreement | draft"},
    {"variable": "topic", "definition": "Subject, as listed by the source", "values": "text"},
    {"variable": "farm_domestic", "definition": "What the source says about farm or domestic workers, where recorded", "values": "text"},
    {"variable": "url", "definition": "Link to the text or the database entry", "values": "URL"},
    {"variable": "link", "definition": "What the link is: text = official text; guidance = official guidance from a ministry or agency site; "
                                         "db = front page of an official database; secondary = not a government site (PacLII); "
                                         "un = copy held in a UN database (UNODC SHERLOC), not the national gazette", "values": "text | guidance | db | secondary | un"},
    {"variable": "source_tier", "definition": "The source as described when the row was found", "values": "text"},
    {"variable": "status", "definition": "Unverified = found with AI help on the source named and not yet read by a person", "values": "Unverified"},
    {"variable": "note", "definition": "Notes for editors: what was checked and what still needs checking", "values": "text"},
    {"variable": "last_checked", "definition": "Date the row was last compared with its source", "values": "YYYY-MM-DD"},
])

# ---------------------------------------------------------------- 2. regional instruments -> Atlas
MN_FIELDS = ["id", "name", "citation", "family", "authority_B", "relevance_R", "adopted", "in_force", "provisions", "drivers",
             "link", "tier", "relevance_RM", "topics", "last_checked"]
MNP = D / "migration-law/migration-norms.csv"
MN = rows(MNP)
mn_have = {norm(r["name"]) for r in MN} | {r["link"] for r in MN if r["link"]}
# (B, R, RM, family, topics) per instrument; B: 5 in force, 4 adopted but not in force, 2 policy (see codebook)
CODE = {
    "African Charter on Human and Peoples' Rights": (5, 1, 3, "Regional treaty", ["Borders, entry & return", "Refugees & asylum"]),
    "African Charter on the Rights and Welfare of the Child": (5, 1, 3, "Regional treaty", ["Children", "Nationality & statelessness", "Refugees & asylum"]),
    "Protocol to the African Charter on Human and Peoples' Rights on the Rights of Women in Africa (Maputo Protocol)": (5, 2, 3, "Regional treaty", ["Trafficking & smuggling", "Refugees & asylum"]),
    "Protocol to the African Charter on Human and Peoples' Rights Relating to the Specific Aspects of the Right to a Nationality and the Eradication of Statelessness in Africa": (4, 1, 5, "Regional treaty", ["Nationality & statelessness"]),
    "Protocol to the African Charter on Human and Peoples' Rights on the Rights of Citizens to Social Protection and Social Security": (4, 2, 3, "Regional treaty", ["Social security"]),
    "Protocol on the Establishment of the East African Community Common Market": (5, 2, 4, "Regional treaty", ["Labor migration", "Borders, entry & return"]),
    "Protocol on Facilitation of Movement of Persons": (4, 1, 5, "Regional treaty", ["Borders, entry & return", "Labor migration"]),
    "Protocol on Employment and Labour": (4, 2, 4, "Regional treaty", ["Labor migration", "Social security"]),
    "Decision 545: Andean Labour Migration Instrument": (5, 2, 5, "Regional treaty", ["Labor migration", "Non-discrimination & equality"]),
    "Decision 548: Andean Mechanism for Cooperation on Consular Assistance and Protection and Migration Matters": (5, 1, 5, "Regional treaty", ["Labor migration"]),
    "Decision 583: Andean Social Security Instrument": (5, 2, 5, "Regional treaty", ["Social security", "Labor migration"]),
    "Decision 878: Andean Migration Statute": (5, 2, 5, "Regional treaty", ["Labor migration", "Borders, entry & return"]),
    "Treaty on the Eurasian Economic Union, Section XXVI (Labour Migration, Arts 96-98) and Annex 30": (5, 2, 4, "Regional treaty", ["Labor migration", "Social security"]),
    "Migration Policy Framework for Africa and Plan of Action (2018-2030)": (2, 1, 5, "Regional declaration", ["Labor migration", "Borders, entry & return"]),
}
BODY_CIT = {"African Union": "African Union", "East African Community": "East African Community", "SADC": "SADC",
            "Andean Community": "Andean Community", "Eurasian Economic Union": "Eurasian Economic Union", "AU": "African Union"}
new_norms = []
new_mpfa = ("AU guidance to member states on labour migration, border governance, irregular migration, forced displacement, "
            "internal migration and the rights of migrants. ")
reg = rows(D / "migration-law/incoming/regional-instruments-2026-11-18.csv")
reg += [{"body": r["regional_body"], "title": r["title"], "adopted": r["adopted"], "in_force": r["in_force"],
         "migration_provisions": r["note"].split(". Listed on the source")[0] + ".", "official_link": r["official_link"],
         "status_on_portal": "policy" if "Policy" in r["type"] else "", "site_status": r["site_status"]}
        for r in rows(D / "africa/incoming/laws-2026-11-17.csv") if not r["country"] and "Migration Policy Framework" in r["title"]]
for r in reg:
    name = r["title"]
    if r["site_status"] != "new" or norm(name) in mn_have or r["official_link"] in mn_have:
        continue
    B, R, RM, fam, tops = CODE[name]
    status = r.get("status_on_portal", "")
    prov = r["migration_provisions"]
    if prov.startswith("Policy, not a treaty"):
        prov = new_mpfa + prov
    if "not in force" in status:
        prov += " Not yet in force."
    prov += " (Unverified: added 2026-11-20 from the regional body's site; articles still to be checked against the text.)"
    row = {"id": f"{r['adopted'][:4]}-{slug(BODY_CIT.get(r['body'], r['body']) + ' ' + name)}"[:45].rstrip("-"),
           "name": name, "citation": BODY_CIT.get(r["body"], r["body"]) + (f", {r['adopted'][:4]}" if r["adopted"] else ""),
           "family": fam, "authority_B": str(B), "relevance_R": str(R), "adopted": r["adopted"], "in_force": r["in_force"],
           "provisions": prov, "drivers": "", "link": r["official_link"], "tier": "R", "relevance_RM": str(RM),
           "topics": "; ".join(tops), "last_checked": DATE}
    MN.append(row); new_norms.append(row); mn_have.add(norm(name))
# South Africa Immigration Act: official DHA link
ZA_LINK = "http://www.dha.gov.za/images/PDFs/IMMIGRATION-ACT-2002---UPDATED-2015.pdf"
for r in MN:
    if r["name"] == "Immigration Act 13 of 2002" and not r["link"]:
        r["link"] = ZA_LINK; r["last_checked"] = DATE
write(MNP, MN_FIELDS, MN)


def dm_row(r):
    return json.dumps([r["name"], r["citation"], r["family"], int(r["authority_B"]), int(r["relevance_R"]), r["adopted"], r["in_force"],
                       r["provisions"], r["drivers"], r["link"], r["tier"], int(r["relevance_RM"]), r["topics"].split("; ")], ensure_ascii=False)


def patch_dm(text):
    for r in new_norms:
        if json.dumps(r["name"], ensure_ascii=False) + "," in text:
            continue
        k = text.index("// ---------- NATIONAL ----------")
        text = text[:k] + dm_row(r) + ",\n" + text[k:]
    text = text.replace('["Immigration Act 13 of 2002","Republic of South Africa","National: South Africa",5,2,"2002-05-31","2003-04-07",',
                        '["Immigration Act 13 of 2002","Republic of South Africa","National: South Africa",5,2,"2002-05-31","2003-04-07",', 1)
    m = re.search(r'(\["Immigration Act 13 of 2002",(?:"[^"]*",){2}\d,\d,(?:"[^"]*",){4})""', text)
    if m:
        text = text[:m.end() - 2] + json.dumps(ZA_LINK) + text[m.end():]
    return text


for p in [ROOT / "build/farmworker-norms/atlas-source/migration_block.js", SITE / "migration-law/index.html"]:
    t = p.read_text(encoding="utf-8"); t2 = patch_dm(t)
    if p.suffix == ".html":
        t2 = re.sub(r'("dateModified": *")[^"]*(")', rf"\g<1>{DATE}\2", t2, count=1)
    p.write_text(t2, encoding="utf-8")
print("Atlas regional tier: added", len(new_norms), [r["name"][:40] for r in new_norms])

# ---------------------------------------------------------------- 3. countries of origin
OCP = D / "countries-of-origin/laws-policies.csv"
OC = rows(OCP); oc_fields = list(OC[0].keys())
ocjs_p = SITE / "countries-of-origin/oc-data.js"; ocjs = ocjs_p.read_text(encoding="utf-8")
inc = rows(D / "countries-of-origin/incoming/laws-2026-11-18.csv") + rows(D / "countries-of-origin/incoming/laws-lk-2026-11-18.csv")
TOPIC_OC = {"Foreign Employment Tribunal Rules": "Foreign Employment Tribunal procedure",
            "Human Trafficking and Transportation (Control) Rules": "Trafficking",
            "National Policy against Trafficking": "Trafficking (policy)",
            "Prevention of Smuggling of Migrants": "Migrant smuggling",
            "Overseas Employment and Migrants (Amendment)": "Amends the Overseas Employment and Migrants Act 2013",
            "Human Trafficking and Migrant Smuggling": "Trafficking and migrant smuggling; replaces the 2012 Act",
            "Emigration Ordinance 1982": "Historical: repealed by the Overseas Employment and Migrants Act 2013"}
ORIG_URL = {r["url"] for r in OC}
oc_added = oc_up = 0
for r in inc:
    title = r["title"].replace(" [repealed]", "")
    base = re.sub(r"\s*\(\d{4}\)$", "", title)
    hit = [x for x in OC if x["s"] == r["country"] and (norm(x["title"]) == norm(title) or norm(x["title"]).startswith(norm(base)))]
    if hit:
        x = hit[0]
        if x["url"] != r["official_link"]:
            old = x["url"]; x["url"] = r["official_link"]; x["link"] = "text"; x["last_checked"] = DATE
            if "[repealed]" in r["title"] and "repealed" not in x["topic"].lower():
                x["topic"] += "; repealed by the Human Trafficking and Migrant Smuggling Prevention and Suppression Act 2026 (official portal; unverified)"
            # same change in the page data (match the JS line by country and title)
            lines = ocjs.split("\n")
            for i, ln in enumerate(lines):
                if ln.lstrip().startswith("{s:" + json.dumps(x["s"])) and ("title:" + json.dumps(x["title"], ensure_ascii=False)) in ln:
                    ln = re.sub(r'url:"[^"]*", link:"[^"]*"', f'url:{json.dumps(x["url"])}, link:"text"', ln)
                    ln = re.sub(r'topic:"[^"]*"', "topic:" + json.dumps(x["topic"], ensure_ascii=False), ln)
                    lines[i] = ln
            ocjs = "\n".join(lines); oc_up += 1
        continue
    if r["official_link"] in ORIG_URL:
        continue
    typ = "policy" if "Policy" in title else ("regulation" if "Rules" in title else "statute")
    topic = next((v for k, v in TOPIC_OC.items() if title.startswith(k) or k in title), "") + " (added 2026-11-20, unverified)"
    x = {"id": f"{r['country'].lower()}-{r['adopted']}-{slug(title)}"[:48].rstrip("-"), "s": r["country"], "title": title, "orig": "",
         "year": r["adopted"], "amended": r["amended"], "type": typ, "topic": topic.strip(), "url": r["official_link"], "link": "text",
         "last_checked": DATE}
    OC.append(x); ORIG_URL.add(x["url"]); oc_added += 1
    js = ('    {s:%s, title:%s, orig:"", year:%s, amended:%s, type:"%s", topic:%s, url:%s, link:"text"},' % (
        json.dumps(x["s"]), json.dumps(title, ensure_ascii=False), json.dumps(x["year"]), json.dumps(x["amended"]), typ,
        json.dumps(x["topic"], ensure_ascii=False), json.dumps(x["url"])))
    # after the last law line of the same country
    lines = ocjs.split("\n")
    a = next(i for i, ln in enumerate(lines) if ln.strip() == "laws: [")
    b = next(i for i in range(a, len(lines)) if lines[i].strip() == "],")
    last = max((i for i in range(a, b) if lines[i].lstrip().startswith("{s:" + json.dumps(x["s"]))), default=b - 1)
    lines.insert(last + 1, js); ocjs = "\n".join(lines)
order_s = []
for r in OC:
    if r["s"] not in order_s:
        order_s.append(r["s"])
OC.sort(key=lambda r: order_s.index(r["s"]))
write(OCP, oc_fields, OC)
ocjs_p.write_text(ocjs, encoding="utf-8")
p = SITE / "countries-of-origin/index.html"; t = p.read_text(encoding="utf-8")
p.write_text(re.sub(r'("dateModified": *")[^"]*(")', rf"\g<1>{DATE}\2", t, count=1), encoding="utf-8")
print(f"Countries of origin: {oc_added} laws added, {oc_up} links upgraded to the official text")

# ---------------------------------------------------------------- 4. Gulf: Qatar labour agreements
FWP = D / "gcc/frameworks.csv"
FW = rows(FWP); fw_fields = list(FW[0].keys())
gp = SITE / "gcc/gcc-data.js"; g = gp.read_text(encoding="utf-8")
line = next(l for l in g.split("\n") if l.startswith("GCC.frameworks = "))
GF = json.loads(line[len("GCC.frameworks = "):].rstrip().rstrip(";"))
PARTNER = {"KE": "Kenya", "GH": "Ghana", "KZ": "Kazakhstan", "PS": "Palestine", "SY": "Syrian Arab Republic", "UZ": "Uzbekistan",
           "AF": "Afghanistan", "KH": "Cambodia", "AL": "Albania", "MK": "North Macedonia", "GM": "Gambia", "CN": "China",
           "SD": "Sudan", "BD": "Bangladesh", "PK": "Pakistan", "IN": "India", "MA": "Morocco", "SO": "Somalia", "TN": "Tunisia"}
SRC = "Al Meezan, Qatar legal portal (official): ratification decree"
fw_added = fw_up = 0; unmatched = []
fw_urls = {r["url"] for r in FW}
for r in rows(D / "gcc/incoming/labour-agreements-2026-11-17.csv"):
    if r["official_link"] in fw_urls:
        continue
    partner = PARTNER.get(r["partner"], r["partner"])
    dec = re.match(r"Decree (\d+/\d{4})", r["title"]).group(1)
    yr = int(r["year_ratified"])
    if r["site_status"] == "new":
        x = {"id": f"qa-{yr}-ratification-decree-{slug(dec)}-{r['partner'].lower()}", "s": "QA", "partner": partner, "title": r["title"],
             "level": r["level"], "nature": r["nature"], "signed": "", "in_force": "",
             "scope": f"Ratified by Decree {dec}; the agreement text itself was not opened (unverified, added 2026-11-20)",
             "src": SRC, "url": r["official_link"], "last_checked": DATE}
        FW.append(x); GF.append({k: v for k, v in x.items() if k not in ("id", "last_checked")}); fw_added += 1; fw_urls.add(x["url"])
        continue
    # already listed: the agreement or protocol with this partner signed in or before the ratification year, closest first,
    # whose current link is secondary (BLA dataset or GLMM)
    cands = [x for x in FW if x["s"] == "QA" and x["partner"] == partner and x["nature"] == r["nature"]
             and (x["signed"] or "")[:4].isdigit() and int(x["signed"][:4]) <= yr and not x["url"].startswith("https://almeezan")]
    if not cands:
        cands = [x for x in FW if x["s"] == "QA" and x["partner"] == partner and x["nature"] in ("agreement", "protocol", "uncoded")
                 and (x["signed"] or "")[:4].isdigit() and int(x["signed"][:4]) <= yr and not x["url"].startswith("https://almeezan")]
    if not cands:
        unmatched.append((partner, dec)); continue
    x = max(cands, key=lambda x: x["signed"])
    for gx in GF:
        if gx["s"] == "QA" and gx["title"] == x["title"] and gx["url"] == x["url"]:
            gx["src"] = f"{SRC} {dec} (earlier source: {gx['src']})"; gx["url"] = r["official_link"]
    x["src"] = f"{SRC} {dec} (earlier source: {x['src']})"; x["url"] = r["official_link"]; x["last_checked"] = DATE
    fw_up += 1; fw_urls.add(x["url"])
write(FWP, fw_fields, FW)
g = g.replace(line, "GCC.frameworks = " + json.dumps(GF, ensure_ascii=False) + ";")
g = re.sub(r'GCC.updated = "[^"]*"', f'GCC.updated = "{DATE}"', g)
gp.write_text(g, encoding="utf-8")
p = SITE / "gcc/index.html"; t = p.read_text(encoding="utf-8")
p.write_text(re.sub(r'("dateModified": *")[^"]*(")', rf"\g<1>{DATE}\2", t, count=1), encoding="utf-8")
print(f"Gulf: {fw_added} agreements added, {fw_up} given the official ratification decree link; left for an editor: {unmatched}")
