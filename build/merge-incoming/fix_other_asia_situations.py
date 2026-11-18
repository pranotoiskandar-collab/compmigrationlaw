"""Correct the situation codes of the Other Asia candidates (PR 5) where the keyword mapping misled.

Usage: python3 build/merge-incoming/fix_other_asia_situations.py SITE   (idempotent)
- "Citizenship and identity documents" cases were coded "passport", which the site labels
  "Passport kept by employer". They are about citizenship, so the situation is left empty.
- "Immigration control, detention or deportation" cases were coded "residence"; they belong
  under "arrest" ("Arrested, detained or expelled").
- Recruitment cases were coded "recruitment", a key the site does not know, so they appeared under no
  situation; they belong under "fees" ("Recruitment and the agency").
- The keyword topics "seafarer", "labour" and "domestic" were coded "employer", which the site labels
  "Could not change employer". Seafarers' standard-contract claims are mostly disability and death
  claims, so they go under "injury"; the other two get no situation until the judgment is read.
Applies to every decision whose summary is one of these generated topic sentences (PR 5 candidates
and the later additions from the same search), so it can be rerun after each merge.
Updates cd-data.js and data/decisions.json/.csv under SITE/court-decisions and DATA (data/court-decisions).
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; SITE = Path(sys.argv[1])
FIX = {"Recruitment for work abroad, including illegal recruitment and fraud.": ("recruitment", "fees"),
       "Overseas worker's claim under the standard employment contract (disability, death or wages).": ("employer", "injury"),
       "Migrant workers: rules on foreign workers' employment and stay.": ("employer", None),
       "Migrant domestic worker.": ("employer", None),
       "Citizenship and identity documents.": ("passport", None),
       "Immigration control, detention or deportation of a foreign national.": ("residence", "arrest")}
OA = None  # every decision whose summary is a generated topic sentence (see FIX)


def fix(sits, plain):
    if plain not in FIX:
        return sits
    old, new = FIX[plain]
    out = [s for s in sits if s != old]
    if new and new not in out:
        out.append(new)
    return out


n = 0
p = SITE / "court-decisions/cd-data.js"; pre, body = p.read_text(encoding="utf-8").split("window.CD=", 1)
data = json.loads(body.rstrip().rstrip(";"))
for d in data["decisions"]:
    if d.get("plain", d.get("plain_en")) in FIX:
        s2 = fix(d["situations"], d["plain"]); n += s2 != d["situations"]; d["situations"] = s2
p.write_text(pre + "window.CD=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
for base in [SITE / "court-decisions/data", ROOT / "data/court-decisions"]:
    j = json.load(open(base / "decisions.json", encoding="utf-8"))
    for d in j["decisions"]:
        if d.get("plain", d.get("plain_en")) in FIX:
            d["situations"] = fix(d["situations"], d["plain"])
    json.dump(j, open(base / "decisions.json", "w", encoding="utf-8"), ensure_ascii=False)
    rows = list(csv.DictReader(open(base / "decisions.csv", encoding="utf-8"))); cols = list(rows[0].keys())
    for r in rows:
        if r["plain_en"] in FIX:
            r["situations"] = ";".join(fix([x for x in r["situations"].split(";") if x], r["plain_en"]))
    with open(base / "decisions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)
print("decisions recoded:", n)
