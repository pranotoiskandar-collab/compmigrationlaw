"""One-off clean-up of the published data files (2026-11-19).

Run from the repository root:  python3 build/records-cleanup/clean.py
It is safe to run again: every step checks before it changes anything.

What it does
1. Removes the byte-order mark some Southeast Asia files had, so the first
   column name reads "feature", not "﻿feature".
2. Writes dates like "03 Jun 1957" as 1957-06-03 (ISO 8601).
3. Merges court decisions listed in data/court-decisions/duplicates.csv into the
   record that is kept, then removes the duplicate row everywhere
   (decisions.csv, decisions.json, site/court-decisions/cd-data.js).
4. Gives every law, instrument and norm a stable `id` where the file had none.
5. Adds a `last_checked` column (YYYY-MM-DD) to every record file: the check
   date already recorded in the row if there is one, otherwise the date the row
   last changed in this repository (git history).
6. Rewrites list fields in decisions.json as real JSON lists, not Python text.
"""
import ast
import csv
import datetime
import io
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
# Commit that first imported the site and data (2026-11-17). Rows unchanged since
# then take the release date of their database instead (RELEASED below).
FIRST_IMPORT = "7b725ac"
# Release date of each database version, from the page metadata at import.
RELEASED = {
    "atlas": "2026-11-11", "migration-law": "2026-11-11", "gcc": "2026-11-12", "east-asia": "2026-11-13",
    "southeast-asia": "2026-11-13", "countries-of-origin": "2026-11-11", "domestic-workers": "2026-11-11",
    "court-decisions": "2026-11-17", "government-hate-speech": "2026-10-31",
}
MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def read(path):
    text = path.read_text(encoding="utf-8")
    text = text.lstrip("﻿")
    rows = list(csv.reader(io.StringIO(text)))
    return rows[0], [r for r in rows[1:] if r]


def write(path, header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")


def iso_from_text(value):
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]{3})[a-z]* (\d{4})", value.strip())
    if m and m.group(2).lower() in MONTHS:
        return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(2).lower()], int(m.group(1)))
    return value


def blame_dates(path):
    """Commit date (YYYY-MM-DD) for every line of a file, from git blame."""
    rel = path.relative_to(ROOT)
    try:
        out = subprocess.run(["git", "blame", "--line-porcelain", "HEAD", "--", str(rel)], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    dates, current, commit = [], None, None
    for line in out.splitlines():
        if re.match(r"[0-9a-f]{40} ", line):
            commit = line[:40]
        elif line.startswith("committer-time "):
            current = datetime.datetime.fromtimestamp(int(line.split()[1]), datetime.timezone.utc).strftime("%Y-%m-%d")
        elif line.startswith("\t"):
            # rows that come unchanged from the first import have no date of their own
            dates.append(None if commit.startswith(FIRST_IMPORT) else current)
    return dates


def row_dates(path):
    """For each data row, the newest blame date over the physical lines it spans."""
    lines = blame_dates(path)
    if not lines:
        return None
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    reader = csv.reader(io.StringIO(text))
    out, start = [], 0
    for i, row in enumerate(reader):
        end = reader.line_num
        if i > 0 and row:
            known = [d for d in lines[start:end] if d]
            out.append(max(known) if known else None)
        start = end
    return out


# ---------------------------------------------------------------- 1 + 2
DATE_COLS = {("atlas", "ratifications.csv"): ["date"], ("domestic-workers", "treaty-status.csv"): ["date"]}

# ---------------------------------------------------------------- 4 + 5
# file -> (title column, state column or None, year column or None)
ID_FILES = {
    "atlas/farmworker-norms.csv": ("name", None, "adopted"),
    "atlas/cases.csv": ("case", "country", "year"),
    "migration-law/migration-norms.csv": ("name", None, "adopted"),
    "countries-of-origin/laws-policies.csv": ("title", "s", "year"),
    "countries-of-origin/instruments.csv": ("title", "s", "signed"),
    "east-asia/domestic-laws.csv": ("title", "s", "year"),
    "east-asia/instruments.csv": ("title", "s", "signed"),
    "gcc/domestic-laws.csv": ("title", "s", "year"),
    "gcc/frameworks.csv": ("title", "s", "signed"),
    "southeast-asia/domestic-laws.csv": ("title", "s", "year"),
    "southeast-asia/instruments.csv": ("title", "s", "signed"),
}
# Files whose rows are records that someone checks against a source.
CHECK_FILES = list(ID_FILES) + [
    "court-decisions/decisions.csv",
    "countries-of-origin/codings.csv", "countries-of-origin/protection.csv", "countries-of-origin/developments.csv",
    "east-asia/codings.csv", "east-asia/developments.csv",
    "southeast-asia/codings.csv", "southeast-asia/developments.csv", "southeast-asia/origins.csv",
    "domestic-workers/codings.csv", "domestic-workers/instruments.csv", "domestic-workers/treaty-status.csv",
    "government-hate-speech/elections/codings.csv",
    "atlas/implementation.csv",
]
EXPLICIT = ["checked_official_text", "checked_on"]


def slug(text, n=40):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:n].rstrip("-") or "item"


def add_ids(rel, header, rows):
    if "id" in header:
        return header, rows
    tcol, scol, ycol = ID_FILES[rel]
    ti, si = header.index(tcol), header.index(scol) if scol else None
    yi = header.index(ycol) if ycol in header else None
    seen, new = set(), []
    for r in rows:
        year = re.search(r"\d{4}", r[yi]).group(0) if yi is not None and re.search(r"\d{4}", r[yi]) else "nd"
        parts = ([slug(r[si].split(",")[0], 12)] if si is not None and r[si] else []) + [year, slug(r[ti])]
        base = "-".join(parts)
        uid, k = base, 2
        while uid in seen:
            uid, k = f"{base}-{k}", k + 1
        seen.add(uid)
        new.append([uid] + r)
    return ["id"] + header, new


def add_last_checked(rel, header, rows, dates):
    """Explicit check date in the row; else the date the row last changed here;
    else the date it was coded; else the release date of its database."""
    if "last_checked" in header:
        return header, rows
    idx = [header.index(c) for c in EXPLICIT if c in header]
    coded = header.index("coded") if "coded" in header else None
    out = []
    for i, r in enumerate(rows):
        explicit = [m.group(0) for j in idx for m in [re.match(r"\d{4}-\d{2}-\d{2}", r[j])] if m]
        history = dates[i] if dates and i < len(dates) else None
        if explicit:
            value = max(explicit)
        elif history:
            value = history
        elif coded is not None and re.match(r"\d{4}-\d{2}-\d{2}$", r[coded]):
            value = r[coded]
        else:
            value = RELEASED[rel.split("/")[0]]
        out.append(r + [value])
    return header + ["last_checked"], out


# ---------------------------------------------------------------- 3 + 6
def merge_duplicates():
    dup_path = DATA / "court-decisions" / "duplicates.csv"
    _, dups = read(dup_path)
    pairs = {d[0]: d[1] for d in dups}  # removed -> kept
    path = DATA / "court-decisions" / "decisions.csv"
    header, rows = read(path)
    by_id = {r[0]: r for r in rows}
    H = {c: i for i, c in enumerate(header)}
    for gone, kept in pairs.items():
        if gone not in by_id or kept not in by_id:
            continue
        g, k = by_id[gone], by_id[kept]
        # keep the curated text; take the official citation and links the harvested row had
        if not k[H["citation"]] or "to be added" in k[H["citation"]]:
            k[H["citation"]] = g[H["citation"]]
        elif g[H["citation"]] and g[H["citation"]] not in k[H["citation"]]:
            k[H["citation"]] = k[H["citation"]] + "; " + g[H["citation"]]
        srcs = [s.strip() for s in k[H["sources"]].split("|") if s.strip()]
        for s in g[H["sources"]].split("|"):
            if s.strip() and s.strip() not in srcs:
                srcs.insert(0, s.strip())  # official judgment link first
        k[H["sources"]] = " | ".join(srcs)
    rows = [r for r in rows if r[0] not in pairs]
    write(path, header, rows)
    kept_rows = {r[0]: dict(zip(header, r)) for r in rows}

    jpath = DATA / "court-decisions" / "decisions.json"
    j = json.loads(jpath.read_text(encoding="utf-8"))
    j["decisions"] = [d for d in j["decisions"] if d["id"] not in pairs]
    for d in j["decisions"]:
        for key, val in list(d.items()):
            if isinstance(val, str) and val[:1] in "[{" and val[-1:] in "]}":
                try:
                    d[key] = ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    pass
        if d["id"] in pairs.values():
            row = kept_rows[d["id"]]
            d["cite"] = row["citation"]
            urls = [s.strip() for s in row["sources"].split("|") if s.strip()]
            have = {s.get("u") for s in d.get("src", []) if isinstance(s, dict)}
            d["src"] = [{"t": "Judgment (official)", "u": u} for u in urls if u not in have][:1] + list(d.get("src", []))
    jpath.write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")

    cd = ROOT / "site" / "court-decisions" / "cd-data.js"
    text = cd.read_text(encoding="utf-8")
    head, _, body = text.partition("window.CD=")
    body = body.rstrip().rstrip(";")
    obj = json.loads(body)
    obj["decisions"] = [d for d in obj["decisions"] if d["id"] not in pairs]
    for d in obj["decisions"]:
        if d["id"] in pairs.values():
            row = kept_rows[d["id"]]
            d["cite"] = row["citation"]
            urls = [s.strip() for s in row["sources"].split("|") if s.strip()]
            have = {s.get("u") for s in d.get("src", [])}
            d["src"] = [{"t": "Judgment (official)", "u": u} for u in urls if u not in have][:1] + list(d.get("src", []))
    cd.write_text(head + "window.CD=" + json.dumps(obj, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("merged", len(pairs), "duplicate decisions")


def main():
    # blame before any change, so the dates describe the rows as they were
    dates = {rel: row_dates(DATA / rel) for rel in CHECK_FILES}
    merge_duplicates()
    for path in sorted(DATA.rglob("*.csv")):
        rel = str(path.relative_to(DATA))
        if "/incoming/" in "/" + rel or "/sources/" in "/" + rel:
            continue
        raw = path.read_text(encoding="utf-8")
        header, rows = read(path)
        changed = raw.startswith("﻿")
        for key, cols in DATE_COLS.items():
            if rel == "/".join(key):
                for c in cols:
                    i = header.index(c)
                    for r in rows:
                        v = iso_from_text(r[i])
                        if v != r[i]:
                            r[i], changed = v, True
        if rel in ID_FILES and "id" not in header:
            header, rows = add_ids(rel, header, rows)
            changed = True
        if rel in CHECK_FILES and "last_checked" not in header:
            d = dates.get(rel)
            if rel == "court-decisions/decisions.csv" and d:
                # rows were removed by the merge: re-map dates by id from the old file
                old = subprocess.run(["git", "show", "HEAD:data/" + rel], cwd=ROOT, capture_output=True, text=True).stdout
                old_ids = [r[0] for r in list(csv.reader(io.StringIO(old)))[1:] if r]
                m = dict(zip(old_ids, d))
                d = [m.get(r[0]) for r in rows]
            header, rows = add_last_checked(rel, header, rows, d)
            changed = True
        if changed:
            write(path, header, rows)
            print("cleaned", rel)


if __name__ == "__main__":
    main()
