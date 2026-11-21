"""Publish the Africa and Middle East laws of the third crawl round (Pranoto, 21 November 2026: publish right away).

Usage: python3 build/merge-incoming/laws_round3_2026_11_21.py
Adds the rows marked "new" in data/africa/incoming/laws-2026-11-21.csv (Tanzania, Zambia, Namibia, Eswatini,
Lesotho, Malawi) and data/middle-east/incoming/laws-2026-11-21.csv (Turkiye from mevzuat.gov.tr; Morocco, Tunisia,
Algeria and Libya from UNODC SHERLOC) to data/migration-law/national-laws.csv. Then run national_laws_page.py.
Idempotent: rows already in the table (same link, or same country and title) are skipped.
The three rows marked "ON SITE" are text links for instruments already in data/domestic-workers/instruments.csv;
that table has no link column, so they are left for the editors (as in the round of 2026-11-20).
Every row is "Unverified". LII rows are consolidated texts on judiciary-partnered portals; SHERLOC rows are
flagged as a UN-hosted copy. Descriptive only: no scores or rankings.
"""
import csv, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data"
DATE = "2026-11-21"
NL_FIELDS = ["id", "s", "region", "title", "orig", "no", "year", "amended", "type", "topic", "farm_domestic",
             "url", "link", "source_tier", "status", "note", "last_checked"]
NLP = D / "migration-law/national-laws.csv"
NL = list(csv.DictReader(open(NLP, encoding="utf-8")))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
slug = lambda s: re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")
have = {r["url"] for r in NL} | {(r["s"], norm(r["title"])) for r in NL}
TYPE = {"law": "statute", "regulation": "regulation", "order": "regulation", "notice": "regulation",
        "bilateral labour agreement": "agreement", "policy": "policy", "bill": "draft"}
MIDEAST = {"TR", "MA", "TN", "DZ", "LY"}


def link_kind(tier):
    t = tier.lower()
    return "un" if t.startswith("un-hosted") else ("guidance" if "guidance" in t else "text")


added = Counter()
for f in ["africa/incoming/laws-2026-11-21.csv", "middle-east/incoming/laws-2026-11-21.csv"]:
    for r in csv.DictReader(open(D / f, encoding="utf-8")):
        s, title, url = r["country"], r["title"], r["official_link"]
        if r["site_status"] != "new" or not s or url in have or (s, norm(title)) in have:
            continue
        year = (r["adopted"] or "")[:4]
        rid = f"{s.lower()}-{year or 'nd'}-{slug(title)}"[:60].rstrip("-"); n = 2
        while any(x["id"] == rid for x in NL):
            rid = f"{rid[:57]}-{n}"; n += 1
        NL.append({"id": rid, "s": s, "region": "mideast" if s in MIDEAST else "africa", "title": title,
                   "orig": r["title_original"], "no": r["number"], "year": year, "amended": r["amended"],
                   "type": TYPE.get(r["type"].lower(), "statute"), "topic": r["topic"],
                   "farm_domestic": r["covers_farm_or_domestic_work"], "url": url, "link": link_kind(r["source_tier"]),
                   "source_tier": r["source_tier"], "status": "Unverified", "note": r["note"], "last_checked": DATE})
        have.add(url); have.add((s, norm(title))); added[s] += 1

order = {"africa": 0, "mideast": 1, "asia": 2, "pacific": 3}
NL.sort(key=lambda r: (order.get(r["region"], 9), r["s"], r["year"] or "0", r["title"]))
with open(NLP, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, NL_FIELDS, extrasaction="ignore", restval=""); w.writeheader(); w.writerows(NL)
print("national laws:", len(NL), "added", sum(added.values()), dict(added))
