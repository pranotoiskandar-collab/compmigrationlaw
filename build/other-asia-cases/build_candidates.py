"""Build the other-Asia migration case lists from the raw browser exports.

Reads data/court-decisions/incoming/other-asia/raw/ and writes, in the same folder's parent:
  migration-cases-all-2026-11-17.csv        every case kept after filtering, one row per case
  migration-cases-top-courts-2026-11-17.csv the subset proposed for Court Decisions (status C)
and imr_candidates.json here (the site's own field names, for patch_imr_site.py in build/east-asia-cases/).

Sources: Singapore eLitigation, Nepal Kanoon Patrika (Supreme Court), Philippines Supreme Court E-Library.
"""
import csv, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "data" / "court-decisions" / "incoming" / "other-asia"
RAW = OUT / "raw"
DATE = "2026-11-17"

ALL_COLS = ["jurisdiction", "source", "court", "case_no", "date", "date_local", "title", "url", "lang",
            "matched_terms", "farm_terms", "retrieved"]
COLS = ["id", "name", "court", "tier", "forum", "level", "country", "region", "date", "citation", "branch", "sector", "issues",
        "situations", "stages", "outcome", "follow_up", "arguments", "status", "reasoning_tools", "question", "holding",
        "plain_en", "plain_id", "sources"]

FARM_EN = re.compile(r"\b(farm|farms|farmer|plantation|agricultur\w*|fishing|fisherm[ae]n|fishery|fisheries|fishing vessel|livestock)\b", re.I)
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def iso(d, mon, y):
    return f"{int(y):04d}-{MONTHS[mon[:3].lower()]:02d}-{int(d):02d}"


# ---------------------------------------------------------------- Singapore
SG_COURTS = {"SGCA": ("Court of Appeal of Singapore", "apex"), "SGCAI": ("Court of Appeal of Singapore", "apex"),
             "SGHCA": ("Appellate Division of the High Court of Singapore", "appeal"),
             "SGHC": ("High Court of Singapore", "first"), "SGHCR": ("High Court of Singapore (Registrar)", "first"),
             "SGHCF": ("High Court of Singapore (Family Division)", "first"),
             "SGHCI": ("Singapore International Commercial Court", "first"),
             "SGDC": ("District Court of Singapore", "first"), "SGMC": ("Magistrate's Court of Singapore", "first"),
             "SGFC": ("Family Court of Singapore", "first"), "SGECT": ("Employment Claims Tribunal of Singapore", "first"),
             "SGSCT": ("Small Claims Tribunal of Singapore", "first")}
# eLitigation searches the full text, so a single passing mention is common. A Court of Appeal case goes to
# the site only if it hit one of these statute-specific terms, or three or more terms.
SG_STRONG = {"Employment of Foreign Manpower Act", "Prevention of Human Trafficking Act", "foreign domestic worker",
             "Employment Agencies Act", "migrant worker", "Employment Claims Act"}


def singapore():
    rows = {}
    for r in csv.DictReader(open(RAW / "sg_elitigation.csv", encoding="utf-8")):
        x = rows.setdefault(r["href"], {**r, "terms": []})
        t = r["term"].strip('"')
        if t not in x["terms"]:
            x["terms"].append(t)
    out = []
    for href, r in rows.items():
        m = re.search(r"/(\d{4})_(SG[A-Z]+)_(\d+)", href)
        yr, code, no = m.groups()
        court, lvl = SG_COURTS.get(code, (code, "first"))
        d = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", r["meta"])
        out.append({"jurisdiction": "SG", "source": "eLitigation (elitigation.sg)", "court": court,
                    "case_no": f"[{yr}] {code} {no}", "date": iso(*d.groups()) if d else yr, "date_local": "",
                    "title": r["title"].strip(), "url": "https://www.elitigation.sg" + href, "lang": "en",
                    "matched_terms": ";".join(r["terms"]), "farm_terms": ";".join(sorted({f.lower() for f in FARM_EN.findall(r["title"])})),
                    "retrieved": DATE, "_level": lvl,
                    "_site": lvl == "apex" and (bool(SG_STRONG & set(r["terms"])) or len(r["terms"]) >= 3)})
    return out


# ---------------------------------------------------------------- Nepal
DEV = str.maketrans("०१२३४५६७८९", "0123456789")
NP_MIG = re.compile("वैदेशिक|बेचबिखन|बेचविखन|ओसार|जिउ मास्ने|नागरिकता|शरणार्थी|अध्यागमन|राहदानी|भिसा|विदेशी")
NP_WRIT = re.compile("उत्प्रेषण|परमादेश|बन्दीप्रत्यक्षीकरण|प्रतिषेध")
NP_PARTY = re.compile("अध्यागमन|वैदेशिक रोजगार|नागरिकता|शरणार्थी|विदेशी|राहदानी")
NP_FARM = re.compile("कृषि|खेती|पशुपालन|माछा")
NP_SUBJECT = [  # (pattern, English)
    ("वैदेशिक रोजगार ठगी", "Foreign employment fraud"), ("वैदेशिक रोजगार", "Foreign employment offence"),
    ("बेचबिखन|बेचविखन|ओसार|जिउ मास्ने", "Human trafficking"), ("नागरिकता किर्ते", "Forged citizenship certificate"),
    ("नागरिकता", "Citizenship"), ("शरणार्थी", "Refugees"), ("अध्यागमन", "Immigration"), ("राहदानी", "Passport"),
    ("बन्दीप्रत्यक्षीकरण", "Habeas corpus"), ("उत्प्रेषण|परमादेश|प्रतिषेध", "Writ petition (certiorari or mandamus)"),
]
BENCH = {"संयुक्त इजलास": "Division Bench", "पूर्ण इजलास": "Full Bench", "विशेष इजलास": "Special Bench",
         "एकल इजलास": "Single Bench", "संवैधानिक इजलास": "Constitutional Bench"}


def bs_to_year(bs):
    """Approximate Gregorian year of a Bikram Sambat date (YYYY/MM/DD); the BS year starts in mid-April."""
    y, m = int(bs[:4]), int(bs[5:7])
    return y - 56 if m >= 10 else y - 57


def nepal():
    rows = {}
    for r in csv.DictReader(open(RAW / "np_nkp.csv", encoding="utf-8")):
        x = rows.setdefault(r["id"], {**r, "terms": []})
        if r["term"] not in x["terms"]:
            x["terms"].append(r["term"])
    out = []
    for i, r in rows.items():
        r["head"] = r["head"].replace("\u200c", "").replace("\u200d", "")
        subject = r["head"].split(" - ", 1)[-1].strip(" ।")
        if not (NP_MIG.search(subject) or (NP_WRIT.search(subject) and NP_PARTY.search(r["parties"]))):
            continue
        no = re.search(r"निर्णय नं\. ([०-९0-9]+)", r["head"]).group(1).translate(DEV)
        bs = r["date"].translate(DEV)
        out.append({"jurisdiction": "NP", "source": "Nepal Kanoon Patrika (nkp.gov.np)",
                    "court": "Supreme Court of Nepal (" + BENCH.get(r["bench"], r["bench"]) + ")",
                    "case_no": f"NKP Decision No. {no}", "date": str(bs_to_year(bs)) if re.match(r"\d{4}/\d\d", bs) else "",
                    "date_local": bs + " BS", "title": r["head"].strip(), "url": f"https://nkp.gov.np/full_detail/{i}",
                    "lang": "ne", "matched_terms": ";".join(r["terms"]),
                    "farm_terms": ";".join(sorted(set(NP_FARM.findall(r["parties"] + subject)))), "retrieved": DATE,
                    "_level": "apex", "_site": True, "_subject": subject})
    return out


# ---------------------------------------------------------------- Philippines
PH_CORE = {"Migrant Workers and Overseas Filipinos Act", "Republic Act No. 8042", "Republic Act No. 10022",
           "illegal recruitment", "trafficking in persons", "Anti-Trafficking", "Republic Act No. 9208",
           "overseas Filipino worker", "OFW", "Department of Migrant Workers", "Overseas Workers Welfare Administration",
           "deportation", "Bureau of Immigration"}


def philippines():
    f, ft = RAW / "ph_elibrary.csv", RAW / "ph_titles.csv"
    if not f.exists():
        return []
    titles = {}
    if ft.exists():
        for r in csv.DictReader(open(ft, encoding="utf-8")):
            m = re.match(r"\s*((?:G\.R\.|A\.M\.|A\.C\.|UDK)[^A-Z]*?\d[\w\-]*)", r["t"])
            if m:
                titles[re.sub(r"\s+", " ", m.group(1)).rstrip(" .,")] = r
    rows = {}
    for r in csv.DictReader(open(f, encoding="utf-8")):
        x = rows.setdefault(r["doc"], {**r, "terms": [], "hits": 0})
        t = r["term"].strip('"')
        if t not in x["terms"]:
            x["terms"].append(t)
        h = re.search(r"No\. of hits: (\d+)", r["snip"])
        x["hits"] = max(x["hits"], int(h.group(1)) if h else 0)
    out = []
    for doc, r in rows.items():
        head = re.sub(r"\s+", " ", r["head"]).strip()
        m = re.match(r"(.+?)[.,]? ((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})", head)
        case_no = (m.group(1) if m else head).rstrip(" .,")
        d = re.search(r"(\w+) (\d{1,2}), (\d{4})", m.group(2)) if m else None
        t = titles.get(case_no)
        title = re.sub(r"^\s*(?:G\.R\.|A\.M\.|A\.C\.|UDK)[^A-Z]*?\d[\w\-]*\s*", "", t["t"]).strip() if t else ""
        title = re.sub(r"\s*(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\s*$", "", title)
        url = f"https://elibrary.judiciary.gov.ph/thebookshelf/showdocs/1/{t['u']}" if t else ""
        out.append({"jurisdiction": "PH", "source": "Supreme Court E-Library (elibrary.judiciary.gov.ph)",
                    "court": "Supreme Court of the Philippines", "case_no": case_no,
                    "date": iso(d.group(2), d.group(1), d.group(3)) if d else "", "date_local": "",
                    "title": title, "url": url, "lang": "en", "matched_terms": ";".join(r["terms"]),
                    "farm_terms": ";".join(sorted({x.lower() for x in FARM_EN.findall(title + " " + r["snip"])})),
                    "retrieved": DATE, "_level": "apex",
                    "_site": bool(title) and (bool(PH_CORE & set(r["terms"])) and r["hits"] >= 3 or bool(FARM_EN.search(title)))})
    return out


# ---------------------------------------------------------------- site entries
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48].strip("-")


ABBR = {"PTE": "Pte", "LTD": "Ltd", "S/O": "s/o", "D/O": "d/o", "A/L": "a/l", "A/P": "a/p", "BIN": "bin", "BINTE": "binte",
        "ANOR": "Anor", "ORS": "Ors", "INC": "Inc", "CO": "Co", "PHILS": "Phils", "CORP": "Corp"}
SMALL = {"of", "and", "for", "the", "in", "on", "by", "to", "a", "an", "or", "and/or", "y"}


def tcase(t):
    """Readable party names from an all-capitals title. A party written as a short code (anonymised, e.g. BDB) is kept."""
    t = re.sub(r",?\s*\b(PETITIONERS?|RESPONDENTS?|PLAINTIFF-APPELLEES?|ACCUSED-APPELLANTS?|ACCUSED|APPELLANTS?|APPELLEES?)\b[.,]?", "", t, flags=re.I)
    t = re.sub(r"\[\*\]", "", t)
    parties = re.split(r"\s+(?:v\.?|vs\.?|VS\.?|V\.?)\s+", t.strip())
    out = []
    for p in parties:
        p = p.strip(" ,.")
        if re.fullmatch(r"[A-Z]{2,4}", p):
            out.append(p)
            continue
        ws = []
        for w in re.split(r"(\s+)", p):
            u = w.strip(",.").upper()
            if w.isspace() or not w:
                ws.append(w)
            elif u in ABBR:
                ws.append(w.upper().replace(u, ABBR[u]))
            elif w.lower() in SMALL and ws:
                ws.append(w.lower())
            elif w.isupper() and len(re.sub(r"\W", "", w)) > 1:
                ws.append("-".join(x[:1] + x[1:].lower() for x in w.split("-")))
            else:
                ws.append(w)
        out.append("".join(ws))
    return " v. ".join(out).strip(" ,.")


TOPICS = [
    ("traffic", r"traffick|बेचबिखन|बेचविखन|ओसार|जिउ मास्ने", "Human trafficking.", "Perdagangan orang.", ["forced"], [3], ""),
    ("recruit", r"illegal recruitment|recruitment|Employment Agencies|वैदेशिक रोजगार", "Recruitment for work abroad, including illegal recruitment and fraud.",
     "Perekrutan untuk bekerja di luar negeri, termasuk perekrutan ilegal dan penipuan.", ["recruitment"], [1], ""),
    ("seafarer", r"seafarer|POEA|seaman", "Overseas worker's claim under the standard employment contract (disability, death or wages).",
     "Klaim pekerja migran berdasarkan kontrak kerja standar (cacat, kematian atau upah).", ["employer"], [3], "seafarers"),
    ("domestic", r"domestic worker|domestic helper", "Migrant domestic worker.", "Pekerja rumah tangga migran.", ["employer"], [3], "domestic work"),
    ("deport", r"deportation|banishment|Bureau of Immigration|अध्यागमन|Immigration", "Immigration control, detention or deportation of a foreign national.",
     "Pengawasan imigrasi, penahanan atau deportasi warga negara asing.", ["residence"], [4], ""),
    ("refugee", r"refugee|शरणार्थी", "Refugees.", "Pengungsi.", ["residence"], [4], "asylum seekers and refugees"),
    ("nationality", r"citizenship|नागरिकता|राहदानी", "Citizenship and identity documents.", "Kewarganegaraan dan dokumen identitas.", ["passport"], [5], ""),
    ("labour", r"Foreign Manpower|work permit|foreign worker|foreign employee|special pass|Employment Claims|migrant worker|overseas|OFW",
     "Migrant workers: rules on foreign workers' employment and stay.", "Pekerja migran: aturan tentang kerja dan tinggal pekerja asing.", ["employer"], [3], ""),
]
FORUM = {"SG": "destination", "PH": "origin", "NP": "origin"}


def topic(text):
    for t in TOPICS:
        if re.search(t[1], text, re.I):
            return t
    return ("other", "", "Migration-related case (topic to be confirmed).", "Perkara terkait migrasi (pokok perkara akan dikonfirmasi).", [], [], "")


def branch(x):
    if x["jurisdiction"] == "NP" and re.search("वैदेशिक रोजगार", x["title"]) and not re.search("उत्प्रेषण|परमादेश", x["title"]):
        return "criminal"
    if re.search(r"PUBLIC PROSECUTOR|PEOPLE OF THE PHILIPPINES|^People v", x["title"], re.I) or re.search("कसुर|ठगी|बेचबिखन|बेचविखन|किर्ते|जिउ", x["title"]):
        return "criminal"
    if re.search(r"ATTORNEY.GENERAL|MINISTER|COMMISSIONER|BUREAU|SECRETARY|REPUBLIC OF THE PHILIPPINES|COMMISSION", x["title"], re.I) or re.search("उत्प्रेषण|परमादेश|बन्दीप्रत्यक्षीकरण|नागरिकता|अध्यागमन", x["title"]):
        return "administrative"
    return "private"


def entry(x):
    j = x["jurisdiction"]
    if j == "NP":
        subj = next((en for p, en in NP_SUBJECT if re.search(p, x["_subject"])), "Migration-related case")
        name = f"{subj}, {x['case_no']}"
        text = x["_subject"] + " " + x["matched_terms"]
    else:
        name = tcase(x["title"]) or x["case_no"]
        name = f"{name}, {x['case_no']}" if j == "PH" else name
        text = x["title"] + " " + x["matched_terms"]
    tp = topic(text)
    br = branch(x)
    sector = tp[6] or ("agriculture or fishing" if x["farm_terms"] else "")
    yr = x["date"][:4]
    return {"id": f"c-h-{j.lower()}-{slug(x['case_no'])}" + ("" if x["case_no"].startswith("[") else f"-{yr}"),
            "name": name, "court": x["court"], "cc": j, "region": "asia", "forum": FORUM[j], "tier": "national",
            "level": x["_level"], "date": x["date"], "cite": x["case_no"], "sector": sector, "issues": [],
            "situations": tp[4], "stages": tp[5], "outcome": "unknown", "follow": "unknown", "status": "C",
            "q": "", "q_id": "", "held": "", "plain": tp[2], "plain_id": tp[3], "harvest": True, "branch": br,
            "tools": [], "args": [], "after": [], "src": [{"t": x["source"], "u": x["url"]}],
            "title_local": x["title"] if j == "NP" else ""}


def to_row(e):
    return {"id": e["id"], "name": e["name"], "court": e["court"], "tier": e["tier"], "forum": e["forum"], "level": e["level"],
            "country": e["cc"], "region": e["region"], "date": e["date"], "citation": e["cite"], "branch": e["branch"],
            "sector": e["sector"], "issues": "", "situations": ";".join(e["situations"]),
            "stages": ";".join(map(str, e["stages"])), "outcome": e["outcome"], "follow_up": e["follow"], "arguments": "",
            "status": e["status"], "reasoning_tools": "", "question": "", "holding": "", "plain_en": e["plain"],
            "plain_id": e["plain_id"], "sources": " | ".join(s["u"] for s in e["src"])}


def main():
    rows = singapore() + nepal() + philippines()
    rows.sort(key=lambda x: (x["jurisdiction"], x["date"], x["case_no"]))
    with open(OUT / f"migration-cases-all-{DATE}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ALL_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    ents = {}
    for x in rows:
        if x["_site"] or x["farm_terms"]:
            e = entry(x)
            base, i = e["id"], 2
            while e["id"] in ents:
                e["id"] = f"{base}-{i}"; i += 1
            ents[e["id"]] = e
    ents = list(ents.values())
    json.dump(ents, open(HERE / "imr_candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    with open(OUT / f"migration-cases-top-courts-{DATE}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(to_row(e) for e in ents)
    from collections import Counter
    print("all", len(rows), Counter(x["jurisdiction"] for x in rows))
    print("site", len(ents), Counter(e["cc"] for e in ents))


if __name__ == "__main__":
    main()
