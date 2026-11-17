"""Turn the incoming court-decision files into Court Decisions entries (status C, unverified).

Usage: python3 build/merge-incoming/decisions_from_incoming.py SITE OUT.json
Reads   data/east-asia/incoming/judgments-jp-kr-2026-11-17.csv   (36 Japan/Korea leads)
        data/gcc/incoming/court-decisions-2026-11-17.csv         (9 Qatar Court of Cassation rulings)
        data/africa/incoming/court-decisions-2026-11-17.csv      (87 African decisions)
        build/east-asia-cases/imr_candidates.json                (287 East Asia candidates)
Writes  OUT.json with {"new": [...entries...], "links": {existing_id: [src, ...]}}
Every new entry has status C, which the page shows as "Unverified". Sources that the
contributing project marked as secondary carry "(secondary source)" in their label.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
FALLBACK_ID = "Ringkasan bahasa Indonesia sedang disiapkan. Perkara ini baru ditemukan dan belum dibaca."

src = (SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8")
existing = json.loads(src.split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]
ids = {d["id"] for d in existing}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def cite_keys(cite):
    return {norm(p) for p in re.split(r"[;/]", cite) if len(norm(p)) > 5}


seen = set()
for d in existing:
    seen |= cite_keys(d.get("cite", ""))
    for s in d.get("src", []):
        seen.add(s["u"].rstrip("/"))


def is_dup(e):
    keys = cite_keys(e["cite"])
    return bool(keys & seen) or e["src"][0]["u"].rstrip("/") in seen or e["id"] in ids


def remember(e):
    seen.update(cite_keys(e["cite"]))
    seen.add(e["src"][0]["u"].rstrip("/"))
    ids.add(e["id"])


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def entry(**kw):
    base = dict(region="asia", forum="destination", tier="national", sector="", issues=[], situations=[], stages=[],
                outcome="unknown", follow="unknown", status="C", q="", q_id="", held="", plain_id=FALLBACK_ID,
                harvest=True, tools=[], args=[], after=[])
    base.update(kw)
    return base


new, links, skipped = [], {}, []


def add(e, origin):
    if is_dup(e):
        skipped.append((origin, e["id"], e["cite"]))
        return
    remember(e)
    new.append(e)


# 1. East Asia candidates (already in the page's format)
for e in json.load(open(ROOT / "build/east-asia-cases/imr_candidates.json", encoding="utf-8")):
    e = dict(e)
    e["src"] = [dict(s, t=s["t"] + " (secondary source)") if s["t"] == "HKLII" else s for s in e["src"]]
    add(e, "east-asia candidates")

# 2. Japan and Korea leads
def level(court):
    c = court.lower()
    if "supreme" in c or "constitutional" in c or "cassation" in c:
        return "apex"
    if "high" in c or "appeal" in c:
        return "appeal"
    return "first"


def branch_jp_kr(case_no):
    c = case_no.lower()
    if re.search(r"\((a|u)\)|\d+do\d", c):
        return "criminal"
    if re.search(r"gyo|\d+(du|nu|guhap)\d", c):
        return "administrative"
    return "private"


for r in csv.DictReader(open(ROOT / "data/east-asia/incoming/judgments-jp-kr-2026-11-17.csv", encoding="utf-8")):
    if r["site_status"] != "new":
        skipped.append(("jp-kr leads", r["case_no"], r["site_status"]))
        continue
    courts = [c.strip() for c in r["court"].split("/")]
    dates = [d.strip() for d in r["date"].split("/")]
    top = max(courts, key=lambda c: ["first", "appeal", "apex"].index(level(c)))
    date = max(dates)
    cname = "Japan" if r["country"] == "JP" else "South Korea"
    court = top if top.lower().startswith(("supreme", "constitutional")) is False else top
    court = f"{court}, {cname}" if cname not in court else court
    e = entry(id=f"c-l-{r['country'].lower()}-{slug(r['case_no'].split('/')[-1])}-{date[:4]}",
              name=r["topic_from_official_summary"], court=court, cc=r["country"], level=level(top), date=date,
              cite=r["case_no"].replace(" / ", "; "), branch=branch_jp_kr(r["case_no"]),
              plain=r["topic_from_official_summary"] + ".",
              src=[{"t": "Courts in Japan (courts.go.jp)" if r["country"] == "JP" else "law.go.kr (National Law Information Center)",
                    "u": r["official_link"]}])
    add(e, "jp-kr leads")

# 3. Qatar Court of Cassation
for r in csv.DictReader(open(ROOT / "data/gcc/incoming/court-decisions-2026-11-17.csv", encoding="utf-8")):
    num = r["case_no"].replace("Appeal ", "")
    e = entry(id=f"c-l-qa-cassation-{slug(num)}", name=r["topic_from_official_summary"],
              court="Court of Cassation, Qatar", cc="QA", region="gulf", level="apex", date=r["date"],
              cite=f"Court of Cassation, {r['case_no']}", branch="criminal" if r["chamber"] == "Criminal" else "private",
              held=r["holding_from_official_principles"], plain=r["topic_from_official_summary"] + ".",
              src=[{"t": "Al Meezan, Qatar legal portal (official)", "u": r["official_link"]}])
    add(e, "gcc")

# 4. Africa
def src_label(link, tier):
    host = re.sub(r"^https?://(www\.)?", "", link).split("/")[0]
    names = {"hdl.handle.net": "Constitutional Court of South Africa, judgment archive", "new.kenyalaw.org": "Kenya Law",
             "kenyalaw.org": "Kenya Law", "ulii.org": "ULII (Uganda)", "ghalii.org": "GhaLII (Ghana)",
             "zimlii.org": "ZimLII (Zimbabwe)", "nigerialii.org": "NigeriaLII", "lawlibrary.org.za": "lawlibrary.org.za",
             "africanlii.org": "AfricanLII"}
    label = names.get(host, host)
    if "secondary" in tier.lower():
        label += " (secondary source)"
    return label


for r in csv.DictReader(open(ROOT / "data/africa/incoming/court-decisions-2026-11-17.csv", encoding="utf-8")):
    link = r["official_link"] or r["sources"].split(" | ")[0]
    s = {"t": src_label(link, r["source_tier"]), "u": link}
    m = re.match(r"ON SITE \(([^)]+)\)", r["site_status"])
    if m:
        target = m.group(1)
        if target in {d["id"] for d in existing}:
            links.setdefault(target, []).append(s)
        else:
            skipped.append(("africa on-site", target, "id not found"))
        continue
    issue = re.search(r"Issue: (.*)", r["note"])
    plain = r["plain_en"] or (issue.group(1).strip().rstrip(".") + "." if issue and "to be read" not in issue.group(1) else
                               "Subject to be confirmed from the judgment.")
    e = entry(id=r["id"], name=r["name"], court=r["court"], cc=r["country"], region=r["region"] or "africa",
              forum="regional" if r["tier"] == "regional" else (r["forum"] or "destination"), tier=r["tier"] or "national", level=r["level"] or "first",
              date=r["date"], cite=r["citation"], branch=r["branch"] or "private", sector=r["sector"],
              issues=[x for x in r["issues"].split(";") if x], situations=[x for x in r["situations"].split(";") if x],
              stages=[int(x) for x in r["stages"].split(";") if x], held=r["holding"], plain=plain,
              plain_id=r["plain_id"] or FALLBACK_ID, src=[s])
    add(e, "africa")

json.dump({"new": new, "links": links}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
from collections import Counter
print("new entries:", len(new), Counter(e["cc"] for e in new))
print("official links added to existing entries:", sum(len(v) for v in links.values()))
print("skipped as duplicates or already on the site:", len(skipped))
for s in skipped:
    print("  ", *s)
