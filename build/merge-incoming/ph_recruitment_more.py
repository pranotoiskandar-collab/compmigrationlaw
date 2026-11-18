"""Add more Philippine illegal recruitment cases from the PR 5 search results (status C, unverified).

Usage: python3 build/merge-incoming/ph_recruitment_more.py SITE OUT.json, then patch_site_decisions.py SITE OUT.json
oto (18 November 2026) asked for more recruitment cases. The PR 5 shortlist kept a Philippine decision only
if a core term occurred at least 30 times in it. This adds the Supreme Court decisions from the full list
(data/court-decisions/incoming/other-asia/migration-cases-all-2026-11-17.csv) that matched "illegal
recruitment" together with "POEA" or "overseas employment", have a title and a link, and are not on the
site yet. No new crawl: the cases come from the search already made on elibrary.judiciary.gov.ph.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "build/other-asia-cases"))
from build_candidates import entry  # noqa: E402

SITE = Path(sys.argv[1])
D = json.loads((SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8").split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
urls = {s["u"].rstrip("/") for d in D for s in d["src"]}
cites = {norm(p) for d in D for p in re.split(r"[;/,]", d.get("cite", "")) if len(norm(p)) > 5}
ids = {d["id"] for d in D}

new = []
for x in csv.DictReader(open(ROOT / "data/court-decisions/incoming/other-asia/migration-cases-all-2026-11-17.csv", encoding="utf-8")):
    m = x["matched_terms"].lower()
    if x["jurisdiction"] != "PH" or "illegal recruitment" not in m or not ("poea" in m or "overseas employment" in m):
        continue
    if not x["url"] or not x["title"] or x["url"].rstrip("/") in urls or norm(x["case_no"]) in cites:
        continue
    x["_level"] = "apex"; x["_subject"] = ""
    x["title"] = re.sub(r"\b(VS?)\.(?=\S)", r"\1. ", x["title"], flags=re.I)
    e = entry(x)
    e.pop("title_local", None)
    e["plain"] = "Recruitment for work abroad, including illegal recruitment and fraud."
    e["plain_id"] = "Perekrutan untuk bekerja di luar negeri, termasuk perekrutan ilegal dan penipuan."
    e["situations"], e["stages"] = ["fees"], [1]
    base, i = e["id"], 2
    while e["id"] in ids:
        e["id"] = f"{base}-{i}"; i += 1
    ids.add(e["id"]); urls.add(x["url"].rstrip("/")); cites.add(norm(x["case_no"]))
    new.append(e)
json.dump({"new": new, "links": {}}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("new Philippine recruitment cases:", len(new))
