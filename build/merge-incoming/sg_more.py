"""Add Singapore migrant-worker cases below the Court of Appeal from the PR 5 search results (status C).

Usage: python3 build/merge-incoming/sg_more.py SITE OUT.json, then patch_site_decisions.py SITE OUT.json
PR 5 put only 13 Court of Appeal decisions on the site. Pranoto (18 November 2026) agreed to sort the
other eLitigation hits without a new crawl. Kept: decisions that matched a statute-specific term
(Employment of Foreign Manpower Act, Employment Claims Act, Employment Agencies Act, Prevention of
Human Trafficking Act, "foreign domestic worker", "migrant worker"), all Employment Claims Tribunal
decisions, and decisions that matched two or more of "work permit", "foreign worker", "foreign
employee" and "special pass". Family and commercial court decisions are left out.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "build/other-asia-cases"))
from build_candidates import entry  # noqa: E402

SITE = Path(sys.argv[1])
D = json.loads((SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8").split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]
urls = {s["u"].rstrip("/") for d in D for s in d["src"]}
ids = {d["id"] for d in D}
STRONG = {"Employment of Foreign Manpower Act", "foreign domestic worker", "Employment Claims Act", "Prevention of Human Trafficking Act", "Employment Agencies Act", "migrant worker"}
WEAK = {"work permit", "foreign worker", "foreign employee", "special pass"}
FIX = {"recruitment": "fees", "residence": "arrest"}


def level(court):
    if "Court of Appeal" in court:
        return "apex"
    if court.startswith("High Court") or "Appellate Division" in court:
        return "appeal"
    return "first"


new = []
for x in csv.DictReader(open(ROOT / "data/court-decisions/incoming/other-asia/migration-cases-all-2026-11-17.csv", encoding="utf-8")):
    if x["jurisdiction"] != "SG" or "Family" in x["court"] or "Commercial" in x["court"]:
        continue
    t = set(x["matched_terms"].split(";"))
    if not (t & STRONG or "Employment Claims Tribunal" in x["court"] or len(t & WEAK) >= 2):
        continue
    if not x["url"] or x["url"].rstrip("/") in urls:
        continue
    x["_level"] = level(x["court"]); x["_subject"] = ""
    e = entry(x); e.pop("title_local", None)
    if e["plain"].startswith("Immigration control"):
        e["situations"] = ["arrest"]
    e["situations"] = [FIX.get(s, s) for s in e["situations"]]
    if "Employment Claims Tribunal" in x["court"]:
        e["situations"], e["branch"] = ["wages"], "private"
        e["plain"] = "Salary or employment claim by a foreign worker before the Employment Claims Tribunal."
        e["plain_id"] = "Tuntutan gaji atau ketenagakerjaan oleh pekerja asing di Employment Claims Tribunal."
    if e["id"] in ids:
        continue
    ids.add(e["id"]); urls.add(x["url"].rstrip("/"))
    new.append(e)
json.dump({"new": new, "links": {}}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
from collections import Counter
print("new Singapore cases:", len(new), Counter(e["level"] for e in new), Counter(s for e in new for s in e["situations"]))
