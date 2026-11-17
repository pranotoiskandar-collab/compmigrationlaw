"""Check that every CSV under data/ can be read and has a consistent number of columns."""
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
problems = []
for path in sorted((ROOT / "data").rglob("*.csv")):
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
    except UnicodeDecodeError:
        problems.append(f"{path.relative_to(ROOT)}: not UTF-8")
        continue
    if not rows:
        problems.append(f"{path.relative_to(ROOT)}: empty")
        continue
    width = len(rows[0])
    for number, row in enumerate(rows[1:], start=2):
        if row and len(row) != width:
            problems.append(f"{path.relative_to(ROOT)} line {number}: {len(row)} columns, header has {width}")
print("\n".join(problems) or "All CSV files OK")
sys.exit(1 if problems else 0)
