"""Turn the third round of incoming court decisions (Africa, 21 November 2026) into Court Decisions entries.

Usage: python3 build/merge-incoming/decisions_round3_2026_11_21.py SITE OUT.json
Reads   data/africa/incoming/court-decisions-2026-11-21.csv (116 decisions: Zambia 39, Tanzania 36, Namibia 29,
        Malawi 10, Lesotho 2, from the Laws.Africa legal information institutes)
Writes  OUT.json with {"new": [...], "links": {}, "cites": {}} for patch_site_decisions.py.

Pranoto asked on 21 November 2026 to publish these rows right away. Every entry has status C ("Unverified:
unchecked candidate"): the issue line comes from the LII search summary and nobody has read the judgment yet.
Situations, issues and stages are coded from keywords in that issue line, so they are first-read codes only.
Indonesian lines are AI-drafted from the English issue lines and are as unverified as the English.
Rows already on the site (same citation or same link) are skipped, so the script is safe to rerun.
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
IN = ROOT / "data/africa/incoming/court-decisions-2026-11-21.csv"

src = (SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8")
existing = json.loads(src.split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def cite_keys(cite):
    return {norm(p) for p in re.split(r";", cite) if len(norm(p)) > 5}


seen, ids = set(), {d["id"] for d in existing}
for d in existing:
    seen |= cite_keys(d.get("cite", ""))
    seen |= {s["u"].rstrip("/") for s in d.get("src", [])}

LII = {"TZ": "TanzLII (Tanzania)", "ZM": "ZambiaLII (Zambia)", "NA": "NamibLII (Namibia)",
       "MW": "MalawiLII (Malawi)", "LS": "LesLII (Lesotho)"}

# keyword -> (situation, issue, stage); first-read coding from the one-line issue
RULES = [
    (r"deport|removal|repatriation order|leave namibia|expul", ("residence", "expulsion", 4)),
    (r"detention|detainee|detain|habeas|false imprisonment|arrest", ("arrest", "detention", 4)),
    (r"bail", ("arrest", "criminal", 4)),
    (r"prohibited immigrant", ("residence", "status", 4)),
    (r"citizen|nationality|naturalisation", ("residence", "nationality", 3)),
    (r"refugee|unhcr", ("residence", "asylum", 3)),
    (r"work permit|employment permit|working without a permit|zambianisation", ("residence", "work permission", 3)),
    (r"residence permit|residence|temporary permit|permit|extension of stay|entry|visa|investor", ("residence", "residence", 3)),
    (r"unlawful presence|lawful presence|overstay|immigration act conviction|immigration offence|immigration act offences|absolute liability|plea", ("arrest", "criminal", 4)),
    (r"traffick", ("forced", "trafficking", 3)),
    (r"smuggl|harbouring", ("arrest", "criminal", 2)),
    (r"dismiss|terminat|rescission", ("dismissed", "dismissal", 4)),
    (r"contract|employ|worker|labour commission", ("dismissed", "contract", 3)),
    (r"spouse|same-sex|husband", ("residence", "family", 3)),
    (r"child", ("forced", "children", 3)),
    (r"camps|encampment", ("residence", "mobility", 3)),
]


def code(text, branch):
    t = text.lower()
    sits, iss, st = [], [], set()
    for pat, (s, i, g) in RULES:
        if re.search(pat, t):
            if s == "dismissed" and not re.search(r"dismiss|terminat|rescission|contract|employ|worker", t):
                continue
            if s == "dismissed" and i == "contract" and branch != "private":
                s = "residence"
            sits.append(s); iss.append(i); st.add(g)
    if not sits:  # immigration case with no keyword: first-read default by branch
        sits, iss, st = (["arrest"], ["criminal"], {4}) if branch == "criminal" else (["residence"], ["residence"], {3})
    return list(dict.fromkeys(sits)), list(dict.fromkeys(iss)), sorted(st)


def sector(text):
    t = text.lower()
    if "farm" in t or "plantation" in t or "agricult" in t:
        return "agriculture"
    if "refugee" in t:
        return "asylum seekers and refugees"
    return ""


ID = [l.strip() for l in (Path(__file__).with_name("decisions_round3_2026_11_21_id.txt")).read_text(encoding="utf-8").split("\n") if l.strip()]

rows = list(csv.DictReader(open(IN, encoding="utf-8")))
assert len(ID) == len(rows), (len(ID), len(rows))
new, skipped = [], []
for i, r in enumerate(rows):
    issue = r["note"].split("Issue: ", 1)[-1].strip().rstrip(".")
    plain = issue[0].upper() + issue[1:] + "."
    sits, iss, st = code(issue, r["branch"])
    eid = "c-l-" + re.sub(r"^af-", "", r["id"])
    u = r["sources"].split(" | ")[0].strip()
    e = dict(region="africa", forum="destination", tier="national", sector=sector(issue), issues=iss, situations=sits,
             stages=st, outcome="unknown", follow="unknown", status="C", q="", q_id="", held="", plain_id=ID[i],
             harvest=True, tools=[], args=[], after=[], id=eid, name=r["name"], court=r["court"], cc=r["country"],
             level=r["level"], date=r["date"], cite=r["citation"], branch=r["branch"], plain=plain,
             src=[{"t": LII[r["country"]], "u": u}])
    keys = cite_keys(e["cite"])
    if keys & seen or u.rstrip("/") in seen or eid in ids:
        skipped.append((eid, e["cite"])); continue
    seen.update(keys); seen.add(u.rstrip("/")); ids.add(eid)
    new.append(e)

json.dump({"new": new, "links": {}, "cites": {}}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("new entries:", len(new), Counter(e["cc"] for e in new))
print("skipped as already on the site:", len(skipped), skipped)
print("uncoded:", [e["id"] for e in new if not e["situations"]])
dup = [k for k, v in Counter(e["id"] for e in new).items() if v > 1]
assert not dup, dup
