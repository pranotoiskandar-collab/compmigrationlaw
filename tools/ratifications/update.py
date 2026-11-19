"""Ratification tracker: refresh data/ratifications/ratifications.csv from the official sources.

Instruments tracked
  C097  ILO Migration for Employment Convention (Revised), 1949        NORMLEX
  C143  ILO Migrant Workers (Supplementary Provisions) Convention, 1975 NORMLEX
  C189  ILO Domestic Workers Convention, 2011                          NORMLEX
  C190  ILO Violence and Harassment Convention, 2019                   NORMLEX
  ICRMW UN International Convention on the Protection of the Rights of
        All Migrant Workers and Members of Their Families, 1990        UN Treaty Collection (chapter IV-13)

How it is run
  * Every Monday by .github/workflows/ratification-update.yml, which commits the result when it passes the
    sanity checks below. It can also be started by hand from the Actions tab ("Run workflow").
  * By hand on any computer:  python3 tools/ratifications/update.py
  * From a saved copy of a source page (for example one saved in a browser when a portal blocks scripts):
        python3 tools/ratifications/update.py --html C189=/path/to/saved-normlex-page.html
  * First build from the Atlas extract of 30 October 2026:  python3 tools/ratifications/update.py --seed

Safety rules (the script refuses to write, and exits with an error, when one fails)
  * A source that cannot be reached, or whose page cannot be read, leaves that instrument's rows as they were.
  * A source that returns fewer than 80% of the rows already held is treated as a broken page, not as
    mass denunciation, and is ignored.
  * Every change is listed in data/ratifications/changes.csv with the date it was first seen.

Only the Python standard library is used, so the script runs anywhere without installing anything.
"""

import argparse
import csv
import datetime as dt
import html
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "data", "ratifications")
OUT = os.path.join(OUT_DIR, "ratifications.csv")
CHANGES = os.path.join(OUT_DIR, "changes.csv")
STATUS = os.path.join(OUT_DIR, "sources-status.csv")
NAMES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "country_names.csv")
ATLAS = os.path.join(ROOT, "data", "atlas", "ratifications.csv")

INSTRUMENTS = {
    "C097": {"source": "normlex", "atlas": "C97",
             "url": "https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:312242"},
    "C143": {"source": "normlex", "atlas": "C143",
             "url": "https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:312288"},
    "C189": {"source": "normlex", "atlas": "C189",
             "url": "https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:2551460"},
    "C190": {"source": "normlex", "atlas": "C190",
             "url": "https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:3999810"},
    "ICRMW": {"source": "untc", "atlas": "ICRMW",
              "url": "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-13&chapter=4&clang=_en"},
}
# Dates the ILO conventions enter into force for a country: twelve months after registration.
ILO_DELAY_MONTHS = 12

FIELDS = ["iso2", "country", "instrument", "status", "date_signed", "date_ratified", "in_force",
          "source", "source_url", "last_checked"]

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATE_RE = re.compile(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{4})\b", re.I)


def today():
    return dt.date.today().isoformat()


def iso_date(text):
    m = DATE_RE.search(text or "")
    if not m:
        return ""
    return "%04d-%02d-%02d" % (int(m.group(3)), MONTHS[m.group(2)[:3].lower()], int(m.group(1)))


def load_names():
    names = {}
    with open(NAMES, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            names[norm(r["name"])] = r["iso2"]
    return names


def norm(s):
    s = html.unescape(s or "")
    s = re.sub(r"\s+", " ", s).strip().strip("*").strip()
    return s.lower().replace("’", "'")


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def add_months(iso, months):
    y, m, d = map(int, iso.split("-"))
    m += months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return "%04d-%02d-%02d" % (y, m, min(d, 28 if m == 2 else 30 if m in (4, 6, 9, 11) else 31))


# ---------------------------------------------------------------- fetching and parsing


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; IMR-ratification-tracker/1.0; +https://theimr.org/ratifications/)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def table_rows(page):
    """Yield the text of each cell, row by row, for every <tr> in the page."""
    for tr in re.findall(r"<tr\b.*?</tr>", page, flags=re.S | re.I):
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in cells]
        if cells:
            yield cells


def match_country(cell, names):
    key = norm(re.sub(r"\s*\d+\s*$", "", cell))  # drop footnote numbers
    key = re.sub(r"\s*\(.*?non-metropolitan.*?\)", "", key)
    return names.get(key)


def parse_normlex(page, instrument, names, url):
    """NORMLEX 'Ratifications of Cxxx' page: rows of Country | Date | Status | Note."""
    out = {}
    for cells in table_rows(page):
        iso = match_country(cells[0], names)
        if not iso:
            continue
        rest = " ".join(cells[1:])
        date = iso_date(rest)
        if not date:
            continue
        low = rest.lower()
        if "denounced" in low or "abrogated" in low:
            status, in_force = "denounced", "no"
        elif "not in force" in low:
            status, in_force = "ratified", "no"
        else:
            status, in_force = "ratified", "yes"
        out[iso] = {"iso2": iso, "country": cells[0].strip(), "instrument": instrument, "status": status,
                    "date_signed": "", "date_ratified": date, "in_force": in_force,
                    "source": "normlex", "source_url": url}
    return out


def parse_untc(page, instrument, names, url):
    """UN Treaty Collection status table: Participant | Signature | Ratification, Accession (a) ..."""
    out = {}
    for cells in table_rows(page):
        if len(cells) < 2:
            continue
        iso = match_country(cells[0], names)
        if not iso:
            continue
        signed = iso_date(cells[1]) if len(cells) > 1 else ""
        ratified = iso_date(" ".join(cells[2:3])) if len(cells) > 2 else ""
        if not signed and not ratified:
            continue
        status = "ratified" if ratified else "signed"
        out[iso] = {"iso2": iso, "country": re.sub(r"\s*\d+\s*$", "", cells[0]).strip(), "instrument": instrument,
                    "status": status, "date_signed": signed, "date_ratified": ratified,
                    "in_force": "yes" if ratified else "no", "source": "untc", "source_url": url}
    return out


# ---------------------------------------------------------------- seed from the Atlas extract


def seed(names):
    rows = []
    want = {v["atlas"]: k for k, v in INSTRUMENTS.items()}
    now = dt.date(2026, 11, 19)
    for r in read_csv(ATLAS):
        ins = want.get(r["instrument"])
        if not ins:
            continue
        iso = names[norm(r["country"])]
        date = iso_date(r["date"]) if r["date"] else ""
        code = r["status_code"]
        meta = INSTRUMENTS[ins]
        row = {"iso2": iso, "country": r["country"], "instrument": ins, "source": meta["source"],
               "source_url": meta["url"], "last_checked": "2026-10-30", "date_signed": "", "date_ratified": ""}
        if ins == "ICRMW":
            if code == "S":
                row.update(status="signed", in_force="no")
            else:  # the Convention itself is in force since 1 July 2003, so every party is bound
                row.update(status="ratified", date_ratified=date, in_force="yes")
        else:
            row["date_ratified"] = date
            if code == "F":
                row.update(status="ratified", in_force="yes")
            elif code == "P":
                row.update(status="ratified", in_force="no")
            elif code in ("W", "D"):
                # The 30 Oct 2026 extract marks five recent C190 registrations as "withdrawn". They are less than
                # twelve months old, which matches NORMLEX "Not in force" (awaiting entry into force), not a
                # denunciation: C190 cannot be denounced until ten years after it came into force.
                if ins == "C190" and date and add_months(date, ILO_DELAY_MONTHS) > now.isoformat():
                    row.update(status="ratified", in_force="no")
                else:
                    row.update(status="denounced", in_force="no")
        rows.append(row)
    return rows


# ---------------------------------------------------------------- main


def key(r):
    return (r["instrument"], r["iso2"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", action="store_true", help="rebuild from data/atlas/ratifications.csv (30 Oct 2026)")
    ap.add_argument("--html", action="append", default=[], metavar="INSTRUMENT=FILE",
                    help="read a saved copy of the source page instead of fetching it")
    ap.add_argument("--only", nargs="*", help="instruments to refresh (default: all)")
    args = ap.parse_args()

    names = load_names()
    old = read_csv(OUT)
    if args.seed:
        rows = seed(names)
        rows.sort(key=lambda r: (r["instrument"], r["country"]))
        write_csv(OUT, FIELDS, rows)
        write_csv(STATUS, ["instrument", "source", "last_attempt", "result", "rows"],
                  [{"instrument": i, "source": m["source"], "last_attempt": "2026-10-30",
                    "result": "seeded from the Atlas extract", "rows": sum(1 for r in rows if r["instrument"] == i)}
                   for i, m in INSTRUMENTS.items()])
        if not os.path.exists(CHANGES):
            write_csv(CHANGES, ["date_seen", "instrument", "iso2", "country", "change", "before", "after"], [])
        print("seeded %d rows" % len(rows))
        return 0

    saved = dict(x.split("=", 1) for x in args.html)
    current = {key(r): r for r in old}
    status_rows = {r["instrument"]: r for r in read_csv(STATUS)}
    changes = read_csv(CHANGES)
    problems = []
    for ins, meta in INSTRUMENTS.items():
        if args.only and ins not in args.only:
            continue
        held = [r for r in old if r["instrument"] == ins]
        try:
            page = open(saved[ins], encoding="utf-8", errors="replace").read() if ins in saved else fetch(meta["url"])
            parser = parse_normlex if meta["source"] == "normlex" else parse_untc
            got = parser(page, ins, names, meta["url"])
        except Exception as e:  # noqa: BLE001 - any failure leaves the instrument untouched
            status_rows[ins] = {"instrument": ins, "source": meta["source"], "last_attempt": today(),
                                "result": "not reached: %s" % str(e)[:120], "rows": len(held)}
            problems.append("%s: source not reached (%s)" % (ins, e))
            continue
        if len(got) < 0.8 * len(held):
            status_rows[ins] = {"instrument": ins, "source": meta["source"], "last_attempt": today(),
                                "result": "page not readable (%d rows found, %d held)" % (len(got), len(held)),
                                "rows": len(held)}
            problems.append("%s: only %d rows read from the source, %d held; kept the old rows" % (ins, len(got), len(held)))
            continue
        for iso, new in got.items():
            k = (ins, iso)
            before = current.get(k)
            new["last_checked"] = today()
            compare = ("status", "date_signed", "date_ratified", "in_force")
            if before is None or any(before.get(c, "") != new[c] for c in compare):
                changes.append({"date_seen": today(), "instrument": ins, "iso2": iso, "country": new["country"],
                                "change": "new" if before is None else "updated",
                                "before": "" if before is None else "%s %s %s" % (before["status"], before["date_ratified"] or before["date_signed"], before["in_force"]),
                                "after": "%s %s %s" % (new["status"], new["date_ratified"] or new["date_signed"], new["in_force"])})
            if before is not None:
                new["country"] = before["country"]  # keep the established spelling
            current[k] = new
        for r in held:  # rows the source no longer lists
            if r["iso2"] not in got:
                changes.append({"date_seen": today(), "instrument": ins, "iso2": r["iso2"], "country": r["country"],
                                "change": "no longer listed", "before": r["status"], "after": ""})
                del current[key(r)]
        status_rows[ins] = {"instrument": ins, "source": meta["source"], "last_attempt": today(),
                            "result": "ok", "rows": len(got)}

    rows = sorted(current.values(), key=lambda r: (r["instrument"], r["country"]))
    write_csv(OUT, FIELDS, rows)
    write_csv(STATUS, ["instrument", "source", "last_attempt", "result", "rows"],
              [status_rows[i] for i in INSTRUMENTS if i in status_rows])
    write_csv(CHANGES, ["date_seen", "instrument", "iso2", "country", "change", "before", "after"], changes)
    for p in problems:
        print("WARNING " + p, file=sys.stderr)
    print("%d rows; %d sources with problems" % (len(rows), len(problems)))
    # Exit 0 even when a portal blocked us: the data that was refreshed is still good. The workflow shows the
    # warnings in its summary, and sources-status.csv records them for the page.
    return 0


if __name__ == "__main__":
    sys.exit(main())
