"""Blind second-coding sheets for the two Data in Brief data papers (court decisions; normative datasets).

Usage:
  python3 build/second-coding/make_paper_sheets.py PAGES_WORKSHEET.xlsx PAGES_ANSWER_KEY.csv OUTDIR

Inputs: the repository's data/ folder, plus the comparison-pages worksheet and answer key drawn on
18 November 2026 by make_worksheet.py (East Asia, Southeast Asia, Countries of Origin; 54 cells).

What it draws (seed 20261120, so the sample can be rebuilt):
  Court decisions  about 20% of the fully coded entries (status S), stratified by region, at least one
                   per region. Variables: branch, outcome, follow_up, stages 1-5, arguments.
  Domestic workers about 20% of the coded cells in codings.csv for each of the 25 features (blank
                   cells, "not determined", are left out), spread across jurisdictions.
  Comparison pages the 54 cells already drawn on 18 November 2026, reused unchanged.
Each item gets one second coder (round robin within each stratum, so every coder gets a mix).
About 20% of items also get a second human coder ("overlap"), so agreement between two people can be
reported alongside agreement between a person and IMR's own coding.

OUTDIR gets one workbook per coder (no IMR codes in it) and, in OUTDIR/keys/, the answer keys and the
assignment list. Keep keys/ away from the coders and outside this public repository.
"""
import csv, random, sys
from collections import defaultdict
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2] / "data"
PAGES_WS, PAGES_KEY, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
(OUT / "keys").mkdir(parents=True, exist_ok=True)
SEED, SHARE, OVERLAP = 20261120, 0.20, 0.20
CODERS = ["Felicia Nathania", "Michelle Tjugito", "Intan Nevia Cahyana"]
rng = random.Random(SEED)
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))


def take(n_total):
    return max(1, round(n_total * SHARE))


# ---------- court decisions ----------
dec = [d for d in rd(ROOT / "court-decisions/decisions.csv") if d["status"] == "S"]
by_region = defaultdict(list)
for d in dec:
    by_region[d["region"]].append(d)
court = []
for reg in sorted(by_region):
    court += rng.sample(by_region[reg], take(len(by_region[reg])))
argcodes = rd(ROOT / "court-decisions/argument-codes.csv")
cb = {r["variable"]: r for r in rd(ROOT / "court-decisions/codebook.csv")}

# ---------- domestic workers ----------
dw = [c for c in rd(ROOT / "domestic-workers/codings.csv") if c["value"].strip() != ""]
dwcb = {(r["role"], r["feature"]): r for r in rd(ROOT / "domestic-workers/codebook.csv")}
inst = rd(ROOT / "domestic-workers/instruments.csv")
by_feat = defaultdict(list)
for c in dw:
    by_feat[(c["role"], c["feature"])].append(c)
dws, used = [], defaultdict(int)
for key in sorted(by_feat):
    pool = by_feat[key][:]
    rng.shuffle(pool)
    pool.sort(key=lambda c: used[c["country"]])  # spread across jurisdictions
    for c in pool[: take(len(pool))]:
        dws.append(c); used[c["country"]] += 1

# ---------- comparison pages (18 Nov sample) ----------
pws = load_workbook(PAGES_WS)["Worksheet"]
pages_rows = [list(r[:9]) for r in pws.iter_rows(min_row=2, values_only=True) if r[0]]
pages_key = {r["item"]: r for r in rd(PAGES_KEY)}

# ---------- assignment ----------
assign = defaultdict(list)  # item id -> coders
def deal(items, strat):
    groups = defaultdict(list)
    for it in items:
        groups[strat(it)].append(it)
    k = 0
    for g in sorted(groups):
        for it in groups[g]:
            assign[it].append(CODERS[k % 3]); k += 1
court_ids = [f"cd-{d['id']}" for d in court]
dw_ids = [f"dw-{c['country']}-{c['role']}-{c['feature']}" for c in dws]
page_ids = [r[0] for r in pages_rows]
deal(court_ids, lambda i: next(d["region"] for d in court if f"cd-{d['id']}" == i))
deal(dw_ids, lambda i: i.rsplit("-", 1)[1])
deal(page_ids, lambda i: pages_key[i]["page"])
for ids in (court_ids, dw_ids, page_ids):
    for i in rng.sample(ids, round(len(ids) * OVERLAP)):
        first = assign[i][0]
        assign[i].append(CODERS[(CODERS.index(first) + 1 + rng.randrange(2)) % 3])

# ---------- answer keys ----------
with open(OUT / "keys/answer-key-court.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["item", "region", "tier", "branch", "outcome", "follow_up", "stages", "arguments"])
    for d in court:
        w.writerow([f"cd-{d['id']}", d["region"], d["tier"], d["branch"], d["outcome"], d["follow_up"], d["stages"], d["arguments"]])
with open(OUT / "keys/answer-key-dw.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["item", "country", "role", "feature", "our_value", "evidence"])
    for c in dws:
        w.writerow([f"dw-{c['country']}-{c['role']}-{c['feature']}", c["country"], c["role"], c["feature"], c["value"], c["evidence"]])
with open(OUT / "keys/assignment.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["item", "dataset", "primary_coder", "overlap_coder"])
    for ids, ds in ((court_ids, "court"), (dw_ids, "domestic-workers"), (page_ids, "pages")):
        for i in ids:
            cs = assign[i]; w.writerow([i, ds, cs[0], cs[1] if len(cs) > 1 else ""])

# ---------- workbooks ----------
HEAD = PatternFill("solid", fgColor="2F5D3A"); YOU = PatternFill("solid", fgColor="FFF4D6")
wrap = Alignment(wrap_text=True, vertical="top")


def sheet(wb, title, head, rows, widths, inputs, lists):
    ws = wb.create_sheet(title); ws.append(head)
    for r in rows:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = HEAD; c.alignment = wrap
    for i, wdt in enumerate(widths):
        ws.column_dimensions[ws.cell(row=1, column=i + 1).column_letter].width = wdt
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = wrap
        for j in inputs:
            row[j].fill = YOU
    for j, opts in lists.items():
        if rows:
            dv = DataValidation(type="list", formula1='"' + ",".join(opts) + '"', allow_blank=True); ws.add_data_validation(dv)
            col = ws.cell(row=1, column=j + 1).column_letter; dv.add(f"{col}2:{col}{len(rows) + 1}")
    ws.freeze_panes = "C2"


def court_link(d):
    return " ".join(s.strip() for s in d["sources"].split("|") if s.strip())


counts = {}
for coder in CODERS:
    mine = lambda ids: [i for i in ids if coder in assign[i]]
    wb = Workbook(); rm = wb.active; rm.title = "Read me"
    cc, cdw, cpg = mine(court_ids), mine(dw_ids), mine(page_ids)
    counts[coder] = (len(cc), len(cdw), len(cpg))
    text = [
        f"Second coding for IMR's data papers: worksheet for {coder}",
        "",
        "Thank you. This is a test of how reliable IMR's codes are. You code a random sample of entries again, on your own, and we compare your codes with ours using Cohen's kappa (agreement beyond chance). The result is published in the two data papers and on the website.",
        "The one rule that matters: work blind. Do not look at the IMR website, the downloads, the GitHub repository or the Court Decisions pages while you code, and do not discuss items with the other coders until all three sheets are back. If you have already seen IMR's code for an item, write 'seen' in the notes column and code it anyway; we will leave it out.",
        "Use official sources: the judgment itself, government legislation databases, official gazettes, ministry or agency pages. If you can only find a secondary source (a law firm, an NGO report, a news story), say so in the notes. If you cannot decide, choose 'unclear' rather than guessing. 'Unclear' is a useful answer.",
        f"Your sample: {len(cc)} court decisions, {len(cdw)} domestic-worker cells and {len(cpg)} comparison-page cells. Some items are also given to a second colleague; that is deliberate.",
        "Tabs: 'Court decisions' and its 'Court codebook' and 'Argument codes'; 'Domestic workers' (each row shows what 2, 1 and 0 mean); 'Comparison pages'. Fill in only the yellow columns. Record the minutes each item took: it helps us plan the next round.",
        "Court decisions: read the judgment (links given), then code the type of case, the outcome for the migrant side, what happened afterwards, the stages of the journey involved, and the arguments made for the migrant side. For arguments, write the codes from the 'Argument codes' tab with =1 if the court accepted the argument and =0 if it rejected it, separated by semicolons, for example: status=1; equality=0.",
        "Domestic workers: code the law in force today for that jurisdiction and feature on the 2 / 1 / 0 scale against the benchmark shown. The instruments listed are a starting point, not a hint at the answer.",
        "When you finish, save the file with your name and the date, and put it back in your folder in Drive. Disagreements are discussed afterwards and do not count against you.",
        f"Drawn on 20 November 2026 (seed {SEED}); comparison-page cells drawn on 18 November 2026 (seed 20261118).",
    ]
    for i, line in enumerate(text, 1):
        rm.cell(row=i, column=1, value=line).alignment = wrap
    rm["A1"].font = Font(bold=True, size=14); rm.column_dimensions["A"].width = 120

    rows = []
    for d in court:
        i = f"cd-{d['id']}"
        if i in cc:
            rows.append([i, d["name"], d["court"], d["country"], d["date"], d["citation"], court_link(d)] + [""] * 12)
    sheet(wb, "Court decisions",
          ["Item", "Case", "Court", "Country", "Date", "Citation", "Judgment and sources",
           "Type of case", "Outcome for migrant side", "What happened afterwards",
           "Stage 1 recruitment", "Stage 2 leaving", "Stage 3 working abroad", "Stage 4 changing or losing job", "Stage 5 return and after",
           "Arguments (code=1 accepted, code=0 rejected)", "Pages or paragraphs relied on", "Notes or doubts", "Minutes spent"],
          rows, [20, 34, 26, 8, 11, 22, 40, 14, 14, 14, 10, 10, 10, 10, 10, 36, 22, 30, 9], range(7, 19),
          {7: ["criminal", "private", "administrative", "constitutional", "unclear"],
           8: ["won", "lost", "advisory", "unclear"],
           9: ["carried", "partly", "not", "unknown", "none", "unclear"],
           10: ["yes", "no"], 11: ["yes", "no"], 12: ["yes", "no"], 13: ["yes", "no"], 14: ["yes", "no"]})
    cbs = wb.create_sheet("Court codebook"); cbs.append(["Variable", "Definition", "Values"])
    for v in ("branch", "outcome", "follow_up", "stages", "arguments"):
        r = cb[v]; cbs.append([r["variable"], r["definition"], r["values"]])
    for c in cbs[1]:
        c.font = Font(bold=True)
    for col, wdt in zip("ABC", [14, 100, 40]):
        cbs.column_dimensions[col].width = wdt
    for row in cbs.iter_rows():
        for c in row:
            c.alignment = wrap
    ac = wb.create_sheet("Argument codes"); ac.append(["Code", "Argument (English)", "Argumen (Indonesia)", "Type of law"])
    for r in argcodes:
        ac.append([r["code"], r["label_en"], r["label_id"], r["type_of_law"]])
    for col, wdt in zip("ABCD", [14, 60, 60, 24]):
        ac.column_dimensions[col].width = wdt

    rows = []
    for c in dws:
        i = f"dw-{c['country']}-{c['role']}-{c['feature']}"
        if i not in cdw:
            continue
        b = dwcb[(c["role"], c["feature"])]
        titles = "; ".join(x["title"] for x in inst if c["country"] in x["countries"].split(";") and x["tier"] in ("nat", "bil"))[:600]
        rows.append([i, c["country_name"], c["role"], b["label"], b["benchmark"], b["2"], b["1"], b["0"], titles] + [""] * 5)
    sheet(wb, "Domestic workers",
          ["Item", "Jurisdiction", "Role", "Feature", "Benchmark", "Code 2 means", "Code 1 means", "Code 0 means",
           "Instruments to start with", "Your code", "Law and section relied on", "Link", "Notes or doubts", "Minutes spent"],
          rows, [26, 16, 11, 26, 16, 36, 36, 30, 40, 10, 28, 28, 28, 9], range(9, 14), {9: ["2", "1", "0", "unclear"]})

    rows = [r + [""] * 5 for r in pages_rows if r[0] in cpg]
    sheet(wb, "Comparison pages",
          ["Item", "Page", "Worker group or country", "Feature", "Code 2 means", "Code 1 means", "Code 0 means",
           "Statutes to start with", "Official databases", "Your code", "Law and section relied on", "Link", "Notes or doubts", "Minutes spent"],
          rows, [22, 16, 26, 28, 36, 36, 30, 40, 28, 10, 28, 28, 28, 9], range(9, 14), {9: ["2", "1", "0", "unclear"]})
    wb.save(OUT / f"second-coding-{coder.split()[0].lower()}.xlsx")

print("court", len(court), "of", len(dec), "| domestic workers", len(dws), "of", len(dw), "| pages", len(page_ids))
print("overlap items", sum(len(v) > 1 for v in assign.values()))
for k, v in counts.items():
    print(k, "court/dw/pages =", v, "total", sum(v))
