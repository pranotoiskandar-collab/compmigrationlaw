"""Turn the South and Southeast Asia crawl of 21 November 2026 (PR #56) into Court Decisions entries.

Usage: python3 build/merge-incoming/decisions_round4_2026_11_21.py SITE OUT.json [IN.csv]
IN.csv defaults to the first batch; the second batch (174 more E-Library decisions screened the same day,
court-decisions-2026-11-21b.csv) is run by passing its path.
Reads   data/court-decisions/incoming/other-asia/court-decisions-2026-11-21.csv
        (376 Philippine Supreme Court decisions from the E-Library + 2 Bangladesh High Court Division notes)
Writes  OUT.json with {"new": [...], "links": {}, "cites": {}} for patch_site_decisions.py.

Pranoto asked on 21 November 2026 to publish right after merge. Every entry has status C ("Unverified: unchecked
candidate"). The Philippine decisions were picked by counting keywords in the E-Library text and nobody has read
them, so the topic line is the keyword guess and the codes are first-read only. Indonesian lines are AI-drafted.
Rows already on the site (same G.R. number or same link) are skipped, so the script is safe to rerun.
"""
import csv, json, re, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
IN = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "data/court-decisions/incoming/other-asia/court-decisions-2026-11-21.csv"

src = (SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8")
existing = json.loads(src.split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def cite_keys(cite):
    return {norm(p) for p in re.split(r";", cite) if len(norm(p)) > 5}


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


seen, ids = set(), {d["id"] for d in existing}
for d in existing:
    seen |= cite_keys(d.get("cite", ""))
    seen |= {s["u"].rstrip("/") for s in d.get("src", [])}

# topic guessed from keyword counts -> (plain EN, plain ID, situations, issues, stages, sector)
TOPIC = {
    "seafarer disability benefits": ("Seafarer's claim for disability benefits (topic guessed from keywords; not yet read).",
                                     "Tuntutan tunjangan cacat seorang pelaut (topik ditebak dari kata kunci; belum dibaca).",
                                     ["injury"], ["injury"], [3, 5], "seafarers"),
    "seafarer death benefits": ("Claim for death benefits after a seafarer died (topic guessed from keywords; not yet read).",
                                "Tuntutan tunjangan kematian setelah seorang pelaut meninggal (topik ditebak dari kata kunci; belum dibaca).",
                                ["injury"], ["injury"], [5], "seafarers"),
    "trafficking in persons": ("Trafficking in persons (topic guessed from keywords; not yet read).",
                               "Perdagangan orang (topik ditebak dari kata kunci; belum dibaca).",
                               ["forced"], ["trafficking"], [1, 3], ""),
    "illegal recruitment": ("Illegal recruitment for work abroad (topic guessed from keywords; not yet read).",
                            "Perekrutan ilegal untuk kerja di luar negeri (topik ditebak dari kata kunci; belum dibaca).",
                            ["fees"], ["recruitment"], [1], ""),
    "overseas worker dismissal and unpaid wages": ("Overseas worker's claim for illegal dismissal and unpaid wages (topic guessed from keywords; not yet read).",
                                                   "Tuntutan pekerja luar negeri atas pemecatan tidak sah dan upah yang tidak dibayar (topik ditebak dari kata kunci; belum dibaca).",
                                                   ["dismissed", "wages"], ["dismissal", "wages"], [4], ""),
    "deployment and POEA regulation": ("Deployment of overseas workers and the rules of the overseas employment agency (topic guessed from keywords; not yet read).",
                                       "Penempatan pekerja ke luar negeri dan aturan badan penempatan luar negeri (topik ditebak dari kata kunci; belum dibaca).",
                                       ["fees"], ["recruitment"], [1, 2], ""),
    "deportation of a foreign national": ("A foreign national's challenge to arrest, detention or deportation by the Bureau of Immigration (topic guessed from keywords; not yet read).",
                                          "Gugatan warga negara asing atas penangkapan, penahanan, atau deportasi oleh Biro Imigrasi (topik ditebak dari kata kunci; belum dibaca).",
                                          ["arrest"], ["expulsion", "detention"], [4], ""),
}

BD = {
    "oa-bd-maruf-travels-2016": ("Court's own note: 508 people sent by the agency to Saudi Arabia for Umrah did not come back; the travel agency was sanctioned for the overstays. Not yet read.",
                                 "Catatan pengadilan: 508 orang yang diberangkatkan agen ke Arab Saudi untuk umrah tidak kembali; agen perjalanan dikenai sanksi karena mereka tinggal melewati izin. Belum dibaca."),
    "oa-bd-madina-air-travels-2017": ("Court's own note: 63 people sent by the agency to Saudi Arabia for Umrah did not come back; same issue as Maruf Travels. Not yet read.",
                                      "Catatan pengadilan: 63 orang yang diberangkatkan agen ke Arab Saudi untuk umrah tidak kembali; persoalannya sama dengan perkara Maruf Travels. Belum dibaca."),
}


# Keyword false positives seen from the case names before publishing (plunder, graft, tax, martial law, court
# administration): not migration cases, so they stay out of Court Decisions.
EXCLUDE = {"/46854", "/60980", "/61874", "/62631", "/62984", "/63920", "/64581", "/64755"}


def iso(d):
    for f in ("%B %d, %Y", "%b. %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(d.replace("Sept.", "Sep.").replace("Sept ", "Sep "), f).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return d


def entry(**kw):
    base = dict(region="asia", forum="origin", tier="national", sector="", issues=[], situations=[], stages=[],
                outcome="unknown", follow="unknown", status="C", q="", q_id="", held="", harvest=True,
                tools=[], args=[], after=[])
    base.update(kw)
    return base


new, skipped = [], []
for r in csv.DictReader(open(IN, encoding="utf-8")):
    u = r["official_link"].strip()
    if any(u.endswith(x) for x in EXCLUDE):
        skipped.append(("excluded", r["citation"])); continue
    if r["country"] == "PH":
        topic = re.search(r"Topic guessed from keyword counts: ([^.(]+)", r["note"]).group(1).strip()
        en, idn, sits, iss, st, sector = TOPIC[topic]
        date = iso(r["date"])
        gr = r["citation"].replace("G.R. No. ", "").replace("G.R. Nos. ", "").replace("A.C. No. ", "")
        name = re.sub(r"\*", "", r["name"])
        name = re.sub(r",? Petitioners?,? (Vs?\.|versus)", " v.", name)
        name = re.sub(r",? (Accused-)?(Appellants?|Appellees?|Respondents?|Petitioners?)\.?$", "", name.strip())
        name = re.sub(r"\s+", " ", name).strip(" ,")[:160]
        branch = "criminal" if r["name"].startswith("People") or topic == "trafficking in persons" and "People" in r["name"] else (
            "criminal" if topic in ("illegal recruitment", "trafficking in persons") and re.search(r"People|Prosecutor", r["name"]) else "private")
        if topic == "deportation of a foreign national":
            branch = "administrative"
        if r["citation"].startswith("A.C."):
            branch = "administrative"
        e = entry(id=f"c-l-ph-{'ac' if r['citation'].startswith('A.C.') else 'gr'}-{slug(gr)[:40]}-{date[:4]}", forum=r["forum"] or "origin", name=name, court="Supreme Court of the Philippines", cc="PH",
                  level="apex", date=date, cite=r["citation"], branch=branch, sector=sector, issues=iss, situations=sits,
                  stages=st, plain=en, plain_id=idn, src=[{"t": "Supreme Court E-Library (elibrary.judiciary.gov.ph)", "u": u}])
    else:
        en, idn = BD[r["id"]]
        e = entry(id="c-l-" + r["id"].replace("oa-", ""), name=r["name"], court=r["court"], cc="BD", level="first",
                  date=r["date"], cite=r["citation"], branch="administrative", sector="", issues=["exit", "recruitment"],
                  situations=["fees"], stages=[2], plain=en, plain_id=idn,
                  src=[{"t": "Supreme Court of Bangladesh (court's own short note)", "u": u}])
    keys = cite_keys(e["cite"])
    if keys & seen or u.rstrip("/") in seen or e["id"] in ids:
        skipped.append((e["id"], e["cite"])); continue
    seen.update(keys); seen.add(u.rstrip("/")); ids.add(e["id"])
    new.append(e)

json.dump({"new": new, "links": {}, "cites": {}}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("new entries:", len(new), Counter(e["cc"] for e in new), Counter(e["branch"] for e in new))
print("skipped as already on the site:", len(skipped))
dup = [k for k, v in Counter(e["id"] for e in new).items() if v > 1]
assert not dup, dup
