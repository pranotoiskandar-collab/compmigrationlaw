"""Replace fields of existing decisions with fuller codes (the "stub" part of mk_decisions.py output).

Usage: python3 build/sea-thin/update_stub.py SITE OUT.json
Updates cd-data.js, data/decisions.json and data/decisions.csv under SITE/court-decisions,
and the summary text on the decision's static page. Idempotent.
"""
import csv, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "build/east-asia-cases"))
from imr_candidates import to_row, COLS  # noqa: E402

SITE = Path(sys.argv[1]); STUB = json.load(open(sys.argv[2], encoding="utf-8"))["stub"]
CD = SITE / "court-decisions"

src = (CD / "cd-data.js").read_text(encoding="utf-8")
pre, body = src.split("window.CD=", 1)
data = json.loads(body.rstrip().rstrip(";"))
old_plain = {}
for d in data["decisions"]:
    if d["id"] in STUB:
        old_plain[d["id"]] = d["plain"]
        d.update(STUB[d["id"]])
(CD / "cd-data.js").write_text(pre + "window.CD=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
by = {d["id"]: d for d in data["decisions"]}

j = json.load(open(CD / "data/decisions.json", encoding="utf-8"))
j["decisions"] = [by[d["id"]] if d["id"] in STUB else d for d in j["decisions"]]
json.dump(j, open(CD / "data/decisions.json", "w", encoding="utf-8"), ensure_ascii=False)

rows = list(csv.DictReader(open(CD / "data/decisions.csv", encoding="utf-8")))
rows = [to_row(by[r["id"]]) if r["id"] in STUB else r for r in rows]
with open(CD / "data/decisions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, COLS); w.writeheader(); w.writerows(rows)

for did, old in old_plain.items():
    p = CD / "d" / did / "index.html"
    if p.exists():
        t = p.read_text(encoding="utf-8")
        new = by[did]
        for a, b in [(old, new["plain"]), ("Judicial review of Law 39/2004 on overseas workers", new["name"])]:
            t = t.replace(html.escape(a), html.escape(b)).replace(a, b)
        p.write_text(t, encoding="utf-8")
print("updated", list(old_plain))
