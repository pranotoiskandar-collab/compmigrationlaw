"""Cohen's kappa between IMR's codes and the second coder's (see make_worksheet.py).

Usage: python3 build/second-coding/kappa.py answer-key.csv returned-worksheet.xlsx [SITE]
Prints, per page and overall: number of cells both coded, raw agreement, Cohen's kappa (unweighted)
and quadratic-weighted kappa (the codes 0 < 1 < 2 are ordered). 'unclear' and blanks are left out
of kappa and counted separately. With SITE, writes the result into the "Second coding" cell of the
method table on the three pages (east-asia/ea.js, southeast-asia/sea.js, countries-of-origin/oc.js).
Also writes disagreements.csv next to the returned worksheet, for the discussion of differences.
"""
import csv, re, sys
from collections import Counter
from datetime import date
from pathlib import Path
from openpyxl import load_workbook


def kappa(pairs, weighted=False):
    cats = [0, 1, 2]; n = len(pairs)
    if n == 0:
        return None
    w = (lambda i, j: 1 - ((i - j) / 2) ** 2) if weighted else (lambda i, j: 1.0 if i == j else 0.0)
    po = sum(w(a, b) for a, b in pairs) / n
    pa, pb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(w(i, j) * pa[i] / n * pb[j] / n for i in cats for j in cats)
    return None if pe == 1 else (po - pe) / (1 - pe)


key = {r["item"]: r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
ws = load_workbook(sys.argv[2])["Worksheet"]
rows = list(ws.iter_rows(min_row=2, values_only=True))
res, dis = {}, []
for r in rows:
    iid, mine = r[0], str(r[9]).strip().lower() if r[9] is not None else ""
    if iid not in key:
        continue
    k = key[iid]; ours = k["our_value"]
    res.setdefault(k["page"], {"pairs": [], "unclear": 0, "blank": 0})
    if mine in ("", "none"):
        res[k["page"]]["blank"] += 1; continue
    if mine == "unclear" or ours == "unclear":
        res[k["page"]]["unclear"] += 1
        if mine != ours:
            dis.append([iid, k["unit"], k["feature"], ours, mine, r[10], r[11], r[12]])
        continue
    a, b = int(ours), int(float(mine))
    res[k["page"]]["pairs"].append((a, b))
    if a != b:
        dis.append([iid, k["unit"], k["feature"], ours, mine, r[10], r[11], r[12]])

summary = {}
allp = []
for page, x in res.items():
    p = x["pairs"]; allp += p
    summary[page] = (len(p), sum(a == b for a, b in p) / len(p) if p else None, kappa(p), kappa(p, True), x["unclear"], x["blank"])
summary["All pages"] = (len(allp), sum(a == b for a, b in allp) / len(allp) if allp else None, kappa(allp), kappa(allp, True), 0, 0)
for page, (n, agr, k1, k2, u, bl) in summary.items():
    f = lambda v: "n/a" if v is None else f"{v:.2f}"
    print(f"{page}: n={n} agreement={f(agr)} kappa={f(k1)} weighted kappa={f(k2)} unclear={u} blank={bl}")
with open(Path(sys.argv[2]).with_name("disagreements.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["item", "unit", "feature", "our_value", "second_coder", "law_relied_on", "link", "notes"]); w.writerows(dis)

if len(sys.argv) > 3:
    SITE = Path(sys.argv[3]); today = date.today().isoformat()
    for page, rel in [("East Asia", "east-asia/ea.js"), ("Southeast Asia", "southeast-asia/sea.js"), ("Countries of Origin", "countries-of-origin/oc.js")]:
        if page not in summary or summary[page][2] is None:
            continue
        n, agr, k1, k2, u, bl = summary[page]
        en = f"κ = {k1:.2f} (weighted {k2:.2f}), {n} cells, {today}"
        idn = f"κ = {k1:.2f} (berbobot {k2:.2f}), {n} sel, {today}".replace(".", ",", 2)
        p = SITE / rel; t = p.read_text(encoding="utf-8")
        t2 = re.sub(r't\("(?:planned \(Cohen\'s κ\)|κ = [^"]*)", "(?:direncanakan \(κ Cohen\)|κ = [^"]*)"\)', f't("{en}", "{idn}")', t)
        p.write_text(t2, encoding="utf-8"); print(rel, "updated" if t2 != t else "unchanged")
