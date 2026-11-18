"""Turn the Other Asia candidates (PR 5) into Court Decisions entries (status C, unverified).

Usage: python3 build/merge-incoming/other_asia_from_incoming.py SITE OUT.json
Reads   build/other-asia-cases/imr_candidates.json (398 candidates: Philippines 275, Nepal 110, Singapore 13)
Writes  OUT.json with {"new": [...], "links": {}} for patch_site_decisions.py.
Singapore and the Philippines were merged first (PR 6). On 18 November 2026 oto asked for the Nepal cases
too, as origin-state jurisprudence (no South Asia page), so all three are kept now; cases already merged
are skipped as duplicates, which makes the script safe to rerun.
Candidates already on the site (same citation or same source link) are skipped.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
KEEP = {"SG", "PH", "NP"}

src = (SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8")
existing = json.loads(src.split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def cite_keys(cite):
    return {norm(p) for p in re.split(r"[;/,]", cite) if len(norm(p)) > 5}


seen, ids = set(), {d["id"] for d in existing}
for d in existing:
    seen |= cite_keys(d.get("cite", ""))
    seen |= {s["u"].rstrip("/") for s in d.get("src", [])}

new, skipped = [], []
for e in json.load(open(ROOT / "build/other-asia-cases/imr_candidates.json", encoding="utf-8")):
    if e["cc"] not in KEEP:
        continue
    keys, u = cite_keys(e["cite"]), e["src"][0]["u"].rstrip("/")
    if keys & seen or u in seen or e["id"] in ids:
        skipped.append((e["id"], e["cite"]))
        continue
    seen |= keys; seen.add(u); ids.add(e["id"])
    new.append(e)

json.dump({"new": new, "links": {}}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("new entries:", len(new), Counter(e["cc"] for e in new))
print("skipped as already on the site:", len(skipped))
for s in skipped:
    print("  ", *s)
