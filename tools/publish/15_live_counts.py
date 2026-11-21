"""Keep the decision and law counts written into page text in step with the published data.

Some pages state counts in their text: the lead of /court-decisions/, the status list on /data-quality/,
and the figures on /impact/. Each data update used to leave those sentences behind (the site said
"2,028 decisions" after 2,398 were published). This step recounts from data/ and rewrites the English
sentence and its Indonesian string together, so the i18n keys still match. Safe to run more than once.
"""
import csv
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import DATA, SITE  # noqa: E402


def rows(rel):
    with open(DATA / rel, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


dec = rows("court-decisions/decisions.csv")
n = len(dec)
cand = sum(1 for r in dec if r.get("status") == "C")
coded = sum(1 for r in dec if r.get("status") in ("S", "P"))
laws = sum(len(rows(p)) for p in ("southeast-asia/domestic-laws.csv", "east-asia/domestic-laws.csv",
                                  "gcc/domestic-laws.csv", "countries-of-origin/laws-policies.csv",
                                  "migration-law/national-laws.csv"))


def en(x):
    return f"{x:,}"


def ind(x):
    return f"{x:,}".replace(",", ".")


EDITS = {
    "court-decisions/index.html": [(r"(version [\d.]+ \([^)]*\), with )[\d,]+( decisions\.)", en(n))],
    "court-decisions/cd-i18n.js": [(r"(version [\d.]+ \([^)]*\), with )[\d,]+( decisions\.)", en(n)),
                                   (r"(\(\d+ \w+ \d{4}\) dengan )[\d.]+( putusan\.)", ind(n))],
    "data-quality/index.html": [(r"(These figures describe the )[\d,]+( decisions)", en(n)),
                                (r"(not yet coded it\. )[\d,]+( decisions are at this stage)", en(cand)),
                                (r"(full judgment\. )[\d,]+( decisions are at this stage)", en(coded))],
    "data-quality/i18n.js": [(r"(These figures describe the )[\d,]+( decisions)", en(n)),
                             (r"(menggambarkan )[\d.]+( putusan)", ind(n)),
                             (r"(not yet coded it\. )[\d,]+( decisions are at this stage)", en(cand)),
                             (r"(C, kandidat:[^\"]*?Sebanyak )[\d.]+( putusan)", ind(cand)),
                             (r"(S, telah dikodekan:[^\"]*?Sebanyak )[\d.]+( putusan)", ind(coded)),
                             (r"(full judgment\. )[\d,]+( decisions are at this stage)", en(coded))],
    "impact/index.html": [(r"(<b>)[\d,]+(</b><span>court decisions</span>)", en(n)),
                          (r"(<b>)[\d,]+(</b><span>decisions fully coded</span>)", en(coded)),
                          (r"(<b>)[\d,]+(</b><span>national laws and regulations with source links</span>)", en(laws))],
}

changed = 0
for rel, subs in EDITS.items():
    p = SITE / rel
    if not p.exists():
        continue
    s0 = s = p.read_text(encoding="utf-8")
    for pat, val in subs:
        s = re.sub(pat, lambda m: m.group(1) + val + m.group(2), s)
    if s != s0:
        p.write_text(s, encoding="utf-8")
        changed += 1
print(f"  page counts: {n:,} decisions ({cand:,} candidates, {coded:,} coded), {laws:,} laws; {changed} files updated")
