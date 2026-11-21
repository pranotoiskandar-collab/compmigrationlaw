"""Cohen's kappa for the data papers' second coding (see make_paper_sheets.py).

Usage:
  python3 build/second-coding/kappa_papers.py KEYS_DIR RETURNED_DIR [PAGES_ANSWER_KEY.csv]
  python3 build/second-coding/kappa_papers.py --selftest     (synthetic data; checks the arithmetic only)

KEYS_DIR holds answer-key-court.csv, answer-key-dw.csv and assignment.csv. RETURNED_DIR holds the
coders' returned workbooks (any file name ending .xlsx; the coder is read from the Read me title).

Two comparisons are reported, and they mean different things:
  IMR vs second coder   the published code against an independent person who coded blind (primary
                        coder only, so each item counts once).
  coder vs coder        two second coders on the overlap items: agreement between two people.
For each: n (items both coded, 'unclear', blanks and items marked 'seen' left out), raw agreement,
Cohen's kappa, quadratic-weighted kappa for the ordered 0/1/2 codes, and a bootstrap 95% interval
(2,000 resamples). Kappa per feature is printed with its n; below n = 10 it is too unstable to publish.
Writes report.md and disagreements.csv into RETURNED_DIR.
"""
import csv, random, sys
from collections import Counter, defaultdict
from pathlib import Path


def kappa(pairs, weighted=False, cats=None):
    n = len(pairs)
    if n == 0:
        return None
    cats = cats or sorted({x for p in pairs for x in p}, key=str)
    if weighted:
        idx = {c: i for i, c in enumerate(cats)}; m = max(len(cats) - 1, 1)
        w = lambda a, b: 1 - ((idx[a] - idx[b]) / m) ** 2
    else:
        w = lambda a, b: 1.0 if a == b else 0.0
    po = sum(w(a, b) for a, b in pairs) / n
    pa, pb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(w(i, j) * pa[i] / n * pb[j] / n for i in cats for j in cats)
    return None if abs(1 - pe) < 1e-12 else (po - pe) / (1 - pe)


def boot(pairs, weighted=False, cats=None, reps=2000, seed=1):
    if len(pairs) < 5:
        return None
    r = random.Random(seed); ks = []
    for _ in range(reps):
        k = kappa([pairs[r.randrange(len(pairs))] for _ in pairs], weighted, cats)
        if k is not None:
            ks.append(k)
    ks.sort()
    return (ks[int(0.025 * len(ks))], ks[int(0.975 * len(ks)) - 1]) if ks else None


def line(label, pairs, ordinal=False, cats=None):
    f = lambda v: "n/a" if v is None else f"{v:.2f}"
    n = len(pairs)
    if n == 0:
        return f"| {label} | 0 | | | | |"
    agr = sum(a == b for a, b in pairs) / n
    k = kappa(pairs, cats=cats); ci = boot(pairs, cats=cats)
    kw = kappa(pairs, True, cats) if ordinal else None
    cis = "n/a" if ci is None else f"{ci[0]:.2f} to {ci[1]:.2f}"
    flag = " (n < 10: do not publish)" if n < 10 else ""
    return f"| {label}{flag} | {n} | {agr:.0%} | {f(k)} | {cis} | {f(kw) if ordinal else ''} |"


def norm(v):
    v = "" if v is None else str(v).strip().lower()
    return v[:-2] if v.endswith(".0") else v


def args_map(s):
    out = {}
    for part in str(s or "").replace(",", ";").split(";"):
        if "=" in part:
            k, v = part.split("=", 1); out[k.strip().lower()] = v.strip()[:1]
    return out


def read_returned(folder):
    from openpyxl import load_workbook
    got = defaultdict(dict)  # coder -> item -> dict
    for p in sorted(Path(folder).glob("*.xlsx")):
        wb = load_workbook(p, data_only=True)
        title = str(wb["Read me"]["A1"].value or "")
        coder = title.split("worksheet for", 1)[-1].strip() or p.stem
        for name in ("Court decisions", "Domestic workers", "Comparison pages"):
            if name not in wb.sheetnames:
                continue
            ws = wb[name]; head = [c.value for c in ws[1]]
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:
                    got[coder][row[0]] = dict(zip(head, row))
    return got


def analyse(court_key, dw_key, pages_key, assign, got):
    rep, dis = [], []
    H = "| Variable | n | Agreement | Cohen's κ | 95% interval | Weighted κ |\n|---|---|---|---|---|---|"
    seen = lambda r: "seen" in norm(r.get("Notes or doubts"))

    def pairs_for(items, key, getter_ours, getter_coder, mode):
        out = []
        for it in items:
            coders = assign.get(it, [])
            if mode == "imr":
                if not coders or it not in got.get(coders[0], {}):
                    continue
                r = got[coders[0]][it]
                if seen(r):
                    continue
                a, b = getter_ours(key[it]), getter_coder(r)
            else:
                if len(coders) < 2 or any(it not in got.get(c, {}) for c in coders[:2]):
                    continue
                r1, r2 = got[coders[0]][it], got[coders[1]][it]
                a, b = getter_coder(r1), getter_coder(r2)
            if a in ("", "unclear", "none_given") or b in ("", "unclear", "none_given"):
                continue
            out.append((it, a, b))
        return out

    for mode, title in (("imr", "IMR vs second coder"), ("hh", "Coder vs coder (overlap items)")):
        rep.append(f"\n## {title}\n")
        # court
        rep.append("### Court decisions\n\n" + H)
        items = list(court_key)
        for var, col in (("branch", "Type of case"), ("outcome", "Outcome for migrant side"), ("follow_up", "What happened afterwards")):
            ps = pairs_for(items, court_key, lambda k, v=var: norm(k[v]), lambda r, c=col: norm(r.get(c)), mode)
            rep.append(line(var, [(a, b) for _, a, b in ps]))
            if mode == "imr":
                dis += [["court", it, var, a, b] for it, a, b in ps if a != b]
        for s in range(1, 6):
            col = [c for c in ("Stage 1 recruitment", "Stage 2 leaving", "Stage 3 working abroad", "Stage 4 changing or losing job", "Stage 5 return and after")][s - 1]
            ours = lambda k, s=s: "yes" if str(s) in k["stages"].split(";") else "no"
            theirs = lambda r, c=col: "yes" if norm(r.get(c)) == "yes" else ("no" if any(norm(r.get(x)) for x in ("Stage 1 recruitment", "Stage 2 leaving", "Stage 3 working abroad", "Stage 4 changing or losing job", "Stage 5 return and after")) else "")
            ps = pairs_for(items, court_key, ours, theirs, mode)
            rep.append(line(f"stage {s}", [(a, b) for _, a, b in ps]))
        # arguments: each code either side named, state absent / 1 / 0
        ap = []
        col = "Arguments (code=1 accepted, code=0 rejected)"
        for it in items:
            coders = assign.get(it, [])
            if mode == "imr":
                if not coders or it not in got.get(coders[0], {}) or seen(got[coders[0]][it]):
                    continue
                A, B = args_map(court_key[it]["arguments"]), args_map(got[coders[0]][it].get(col))
                if not court_key[it]["arguments"] or not B:
                    continue
            else:
                if len(coders) < 2 or any(it not in got.get(c, {}) for c in coders[:2]):
                    continue
                A, B = args_map(got[coders[0]][it].get(col)), args_map(got[coders[1]][it].get(col))
                if not A or not B:
                    continue
            for code in set(A) | set(B):
                ap.append((A.get(code, "absent"), B.get(code, "absent")))
        rep.append(line("arguments (per code named by either)", ap))
        # domestic workers
        rep.append("\n### Domestic workers (C189 features)\n\n" + H)
        items = list(dw_key)
        ps = pairs_for(items, dw_key, lambda k: norm(k["our_value"]), lambda r: norm(r.get("Your code")), mode)
        rep.append(line("all features", [(a, b) for _, a, b in ps], True, ["0", "1", "2"]))
        if mode == "imr":
            dis += [["domestic-workers", it, dw_key[it]["feature"], a, b] for it, a, b in ps if a != b]
        byf = defaultdict(list)
        for it, a, b in ps:
            byf[dw_key[it]["feature"]].append((a, b))
        for f in sorted(byf):
            rep.append(line(f"  {f}", byf[f], True, ["0", "1", "2"]))
        # comparison pages
        if pages_key:
            rep.append("\n### Comparison pages (East Asia, Southeast Asia, Countries of Origin)\n\n" + H)
            items = list(pages_key)
            ps = pairs_for(items, pages_key, lambda k: norm(k["our_value"]), lambda r: norm(r.get("Your code")), mode)
            rep.append(line("all pages", [(a, b) for _, a, b in ps], True, ["0", "1", "2"]))
            if mode == "imr":
                dis += [["pages", it, pages_key[it]["feature"], a, b] for it, a, b in ps if a != b]
            for pg in ("East Asia", "Southeast Asia", "Countries of Origin"):
                rep.append(line(f"  {pg}", [(a, b) for it, a, b in ps if pages_key[it]["page"] == pg], True, ["0", "1", "2"]))
    return "\n".join(rep), dis


def load_keys(kd, pk):
    rd = lambda p: {r["item"]: r for r in csv.DictReader(open(p, encoding="utf-8"))}
    court, dw = rd(Path(kd) / "answer-key-court.csv"), rd(Path(kd) / "answer-key-dw.csv")
    assign = {}
    for r in csv.DictReader(open(Path(kd) / "assignment.csv", encoding="utf-8")):
        assign[r["item"]] = [c for c in (r["primary_coder"], r["overlap_coder"]) if c]
    pages = rd(pk) if pk else {}
    return court, dw, pages, assign


def selftest():
    # Arithmetic check against a textbook case: 50 items, 2 categories.
    # Agree yes 20, agree no 15, A yes/B no 5, A no/B yes 10 -> po .70, pe .50, kappa .40.
    pairs = [("y", "y")] * 20 + [("n", "n")] * 15 + [("y", "n")] * 5 + [("n", "y")] * 10
    k = kappa(pairs); assert abs(k - 0.40) < 1e-9, k
    assert kappa([("1", "1"), ("2", "2"), ("0", "0")]) == 1.0
    kw = kappa([("0", "1"), ("1", "2"), ("2", "2"), ("0", "0")], True, ["0", "1", "2"])
    assert kw > kappa([("0", "1"), ("1", "2"), ("2", "2"), ("0", "0")], cats=["0", "1", "2"])
    print("selftest passed: kappa", round(k, 2), "weighted", round(kw, 2), "(synthetic numbers, not results)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest(); sys.exit()
    court, dw, pages, assign = load_keys(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else None)
    got = read_returned(sys.argv[2])
    report, dis = analyse(court, dw, pages, assign, got)
    head = ("# Second coding: agreement report\n\nComputed by build/second-coding/kappa_papers.py from the returned sheets of: "
            + ", ".join(sorted(got)) + ". Kappa: 1 = perfect agreement, 0 = no better than chance; above about 0.6 is usually read as substantial.\n")
    out = Path(sys.argv[2]); (out / "report.md").write_text(head + report + "\n", encoding="utf-8")
    with open(out / "disagreements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["dataset", "item", "variable", "imr_code", "second_coder"]); w.writerows(dis)
    print(head + report)
