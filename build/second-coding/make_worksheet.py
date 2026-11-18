"""Second-coding worksheet for the law codings (inter-coder reliability, Cohen's kappa).

Usage: python3 build/second-coding/make_worksheet.py CODES.json OUTDIR
CODES.json is dumped from the live pages by dump_codes.js (window.EA, window.SEA, window.OC as the
visitor sees them, after the official-text checks and recodes). OUTDIR gets:
  second-coding-worksheet.xlsx  for the second coder: a random sample of cells, our codes hidden
  answer-key.csv                our codes for the same cells (keep away from the coder)
The sample is stratified: 2 cells per worker group (East Asia, Southeast Asia) or per country
(Countries of Origin), drawn with a fixed seed so it can be rebuilt. Promised on the pages as
"Second coding: planned (Cohen's kappa)"; started 18 November 2026 at oto's request.
"""
import csv, json, random, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

D = json.load(open(sys.argv[1], encoding="utf-8")); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(20261118)
PAGES = {"ea": "East Asia", "sea": "Southeast Asia", "oc": "Countries of Origin"}
VAL = {2: "2", 1: "1", 0: "0", None: "unclear"}


def laws_for(page, state):
    ls = [l for l in D[page]["laws"] if l.get("s") == state]
    titles = "; ".join(l["title"] for l in ls[:8])
    sites = sorted({"/".join(l["url"].split("/")[:3]) for l in ls if l.get("url")})
    return titles, " ".join(sites)


units = []
for page in ("ea", "sea"):
    for g in D[page]["groups"]:
        units.append((page, g["k"], g["n"], g["s"], g["codes"]))
names = {s["k"]: s["n"] for s in D["oc"]["states"]}
for cc, codes in D["oc"]["codes"].items():
    units.append(("oc", cc, names.get(cc, cc), cc, codes))

items, key = [], []
for page, uk, uname, state, codes in units:
    cb = {c["k"]: c for c in D[page]["codebook"]}
    feats = sorted(f for f in codes if f in cb)
    for f in rng.sample(feats, 2):
        c = cb[f]; titles, sites = laws_for(page, state)
        iid = f"{page}-{uk}-{f}"
        items.append([iid, PAGES[page], uname, c["en"], c["l2"], c["l1"], c["l0"], titles, sites])
        v = codes[f][0]
        key.append({"item": iid, "page": PAGES[page], "unit": uname, "feature": f, "our_value": VAL.get(v, str(v))})
rng.shuffle(items)

wb = Workbook(); ws = wb.active; ws.title = "Read me"
readme = [
    "Second coding of IMR's law codings",
    "",
    "Thank you for helping. You will code a random sample of the cells that IMR's comparison pages score 2, 1 or 0. Please work alone and do not look at the IMR pages, the Court Decisions database or the downloads while coding, so that your codes are independent of ours.",
    "For each row: read the feature and what 2, 1 and 0 mean; find the law in force today (start with the statutes and the official databases listed); then enter your code in column J (2, 1, 0 or unclear), the law and section you relied on in column K, the link in column L, and any doubt in column M.",
    "Use official sources only: government legislation databases, official gazettes, ministry or agency pages. If you can only find a secondary source (a law firm, an NGO report, a news story), say so in column M. If you cannot decide, enter 'unclear' rather than guessing.",
    "Worker groups (East Asia, Southeast Asia) are coded for that group only, not for all workers in the country. Countries of Origin rows are about what the home country does for its emigrant workers.",
    "When you finish, return the file to IMR. We compare your codes with ours using Cohen's kappa (agreement beyond chance) and publish the result on the pages. Disagreements are discussed and the outcome is noted; they do not count against you.",
    f"Sample: {len(items)} cells, two per worker group or country, drawn at random (seed 20261118).",
]
for i, line in enumerate(readme, 1):
    ws.cell(row=i, column=1, value=line).alignment = Alignment(wrap_text=True, vertical="top")
ws["A1"].font = Font(bold=True, size=14); ws.column_dimensions["A"].width = 120

w2 = wb.create_sheet("Worksheet")
head = ["Item", "Page", "Worker group or country", "Feature", "Code 2 means", "Code 1 means", "Code 0 means",
        "Statutes to start with", "Official databases", "Your code", "Law and section relied on", "Link", "Notes or doubts", "Minutes spent"]
w2.append(head)
for r in items:
    w2.append(r + ["", "", "", "", ""])
for c in w2[1]:
    c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="8F5E12"); c.alignment = Alignment(wrap_text=True, vertical="top")
for col, wdt in zip("ABCDEFGHIJKLMN", [22, 16, 26, 28, 40, 40, 32, 45, 30, 10, 30, 30, 30, 9]):
    w2.column_dimensions[col].width = wdt
for row in w2.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    row[9].fill = PatternFill("solid", fgColor="FFF4D6")
dv = DataValidation(type="list", formula1='"2,1,0,unclear"', allow_blank=True); w2.add_data_validation(dv); dv.add(f"J2:J{len(items) + 1}")
w2.freeze_panes = "D2"
wb.save(OUT / "second-coding-worksheet.xlsx")
with open(OUT / "answer-key.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, list(key[0].keys())); w.writeheader(); w.writerows(key)
print("items", len(items), {p: sum(k["page"] == p for k in key) for p in PAGES.values()})
