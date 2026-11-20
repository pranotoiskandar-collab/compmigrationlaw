"""Check that every CSV under data/ can be read and has a consistent number of columns."""
import csv
import pathlib
import re
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
    published = not ({"incoming", "sources"} & set(path.relative_to(ROOT).parts))
    if published and rows:
        header = rows[0]
        if header and header[0].startswith("\ufeff"):
            problems.append(f"{path.relative_to(ROOT)}: starts with a byte-order mark; save as UTF-8 without BOM")
        for column in ("id", "last_checked"):
            if column not in header:
                continue
            i = header.index(column)
            values = [row[i] for row in rows[1:] if row and len(row) == width]
            if column == "id":
                seen = set()
                for number, value in enumerate(values, start=2):
                    if not value:
                        problems.append(f"{path.relative_to(ROOT)} line {number}: empty id")
                    elif value in seen:
                        problems.append(f"{path.relative_to(ROOT)} line {number}: id {value} is used twice")
                    seen.add(value)
            else:
                for number, value in enumerate(values, start=2):
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        problems.append(f"{path.relative_to(ROOT)} line {number}: last_checked must be YYYY-MM-DD, found '{value}'")
print("\n".join(problems) or "All CSV files OK")
sys.exit(1 if problems else 0)
