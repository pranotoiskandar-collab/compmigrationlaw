"""Add incoming Gulf and East Asia laws to the law tables on /gcc/ and /east-asia/.

Usage: python3 build/merge-incoming/patch_site_laws.py SITE
Gulf: new rows from data/gcc/incoming/laws-2026-11-17.csv are added unchecked; rows already on
the site get the official link in place of a secondary one (matched by state and number).
East Asia: statutes for the four jurisdictions on the page (TW, KR, JP, HK) that the table
does not list yet. Macau, Mongolia and China statutes stay in incoming/ (no page for them).
Then rewrites data/gcc/domestic-laws.csv and data/east-asia/domestic-laws.csv from the page data.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])

# ---------- Gulf ----------
gp = SITE / "gcc/gcc-data.js"
g = gp.read_text(encoding="utf-8")
line = next(l for l in g.split("\n") if l.startswith("GCC.laws = "))
L = json.loads(line[len("GCC.laws = "):].rstrip().rstrip(";"))


ABBR = [("federal decree-law", "fdl"), ("federal law", "fl"), ("royal decree", "rd"), ("ministerial decision", "md"),
        ("ministerial decree", "md"), ("ministerial resolution", "mr"), ("cabinet resolution", "cr"), ("decree-law", "dl")]


def num_key(no, year=""):
    """'Federal Decree-Law 33' + '2021' and 'FDL 33/2021' both give 'fdl33/2021'; MR and MD count as the same."""
    s = no.lower().replace("no.", "").replace(" of ", "/")
    for a, b in ABBR:
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9/]", "", s).replace("mr", "md")
    if "/" not in s and year:
        s += "/" + year[:4]
    return s


# Site rows without a number, matched by the start of their title
UNNUMBERED = {("SA", "Ministerial Decision 146652"): "Labour Reform Initiative",
              ("AE", "MR 676/2022"): "Ministerial Resolution licensing and regulating domestic",
              ("AE", "MD 51/2022"): "Ministerial Resolution licensing and regulating private"}


TYPE = {"Law": "statute", "Ministerial decision": "decision", "Cabinet decision": "decision", "Regulation": "regulation",
        "Decree (ratification)": "decision", "Official guidance": "policy"}
TOPIC = [("trafficking", "trafficking"), ("domestic", "domestic work"), ("recruit", "recruitment"), ("fee", "recruitment"),
         ("wage", "wages"), ("end of service", "wages"), ("social security", "social security"), ("osh", "OSH/heat"),
         ("safety", "OSH/heat"), ("housing", "OSH/heat"), ("health", "OSH/heat"), ("complaint", "disputes"), ("justice", "disputes"),
         ("enforcement", "disputes"), ("mobility", "residence/sponsorship"), ("residence", "residence/sponsorship"),
         ("permit", "residence/sponsorship"), ("equality", "equality")]


def topic(t):
    t = t.lower()
    return next((v for k, v in TOPIC if k in t), "labor")


added = updated = 0
unmatched = []
for r in csv.DictReader(open(ROOT / "data/gcc/incoming/laws-2026-11-17.csv", encoding="utf-8")):
    guidance = "guidance" in r["source_tier"]
    if r["site_status"] != "new":
        k = num_key(r["number"], r["adopted"])
        hit = [x for x in L if x["s"] == r["country"] and x.get("no") and num_key(x["no"], x.get("year", "")) == k]
        pref = UNNUMBERED.get((r["country"], r["number"]))
        if pref:
            hit = [x for x in L if x["s"] == r["country"] and x["title"].startswith(pref)]
            for x in hit:
                x["no"] = r["number"]
        if not hit:  # rows the site lists without a number: match on the topic named in site_status
            unmatched.append((r["country"], r["number"], r["site_status"]))
            continue
        for x in hit:
            x["url"] = r["official_link"]; x["link"] = "guidance" if guidance else "text"
        updated += 1
        continue
    note = r["note"]
    if note.startswith("Listed on the source") or not note:
        note = "Coverage to be described once the text is read."
    if r["covers_farm_or_domestic_work"] == "excluded":
        note = "Excludes domestic and/or farm workers. " + note
    if guidance:
        note = "Official guidance from a ministry site, not the legislation itself. " + note
    L.append({"s": r["country"], "title": r["title"], "orig": r["title_original"], "no": r["number"],
              "year": (r["adopted"] or "")[:4], "amended": r["amended"], "type": TYPE.get(r["type"], "decision"),
              "topic": topic(r["topic"]), "groups": "Unverified (AI-gathered from an official portal). " + note,
              "url": r["official_link"], "link": "guidance" if guidance else "text",
              "checked": "yes" if r["checked_on"] else "no"})
    added += 1
g = g.replace(line, "GCC.laws = " + json.dumps(L, ensure_ascii=False) + ";")
g = re.sub(r'GCC.updated = "[^"]*"', 'GCC.updated = "2026-11-17"', g)
gp.write_text(g, encoding="utf-8")
js = (SITE / "gcc/gcc.js").read_text(encoding="utf-8")
js = js.replace('var LK = {text: t("text", "teks"), db: t("database", "basis data"), glmm: "GLMM"};',
                'var LK = {text: t("text", "teks"), db: t("database", "basis data"), glmm: "GLMM (secondary)", guidance: t("official guidance", "panduan resmi")};')
(SITE / "gcc/gcc.js").write_text(js, encoding="utf-8")
with open(ROOT / "data/gcc/domestic-laws.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, ["s", "title", "orig", "no", "year", "amended", "type", "topic", "groups", "url", "link", "checked"])
    w.writeheader(); w.writerows(L)
print(f"Gulf: {added} laws added, {updated} existing rows given official links, {len(unmatched)} left for an editor:")
for u in unmatched:
    print("   ", *u)

# ---------- East Asia ----------
ep = SITE / "east-asia/ea-data.js"
e = ep.read_text(encoding="utf-8")
have = [(m.group(1), m.group(2).lower()) for m in re.finditer(r'\{s:"([A-Z]{2})", title:"([^"]*)"', e)]
DB = {"KR": "https://www.law.go.kr/", "JP": "https://laws.e-gov.go.jp/", "TW": "https://law.moj.gov.tw/",
      "HK": "https://www.elegislation.gov.hk/"}
rows = []
for r in csv.DictReader(open(ROOT / "data/east-asia/incoming/migration-statutes-2026-11-17.csv", encoding="utf-8")):
    s = r["jurisdiction"]
    if s not in DB:
        continue
    core = re.sub(r"\s*(art\.|\(cap).*$", "", r["title_en"].lower()).strip()
    if any(hs == s and core in ht for hs, ht in have):
        continue
    typ = "regulation" if r["type"] == "regulation" else "statute"
    topic_txt = r["topic"].replace(";", ",")
    rows.append('    {s:%s, title:%s, orig:%s, year:%s, amended:"", type:"%s", topic:%s, groups:"", url:%s, link:"db"},' % (
        json.dumps(s), json.dumps(r["title_en"], ensure_ascii=False), json.dumps(r["title_local"], ensure_ascii=False),
        json.dumps(r["year"]), typ, json.dumps(topic_txt[:1].upper() + topic_txt[1:] + " (added 2026-11-17, unverified)", ensure_ascii=False),
        json.dumps(DB[s])))
k = e.index("  laws: [") + len("  laws: [")
k = e.index("\n", k) + 1
e = e[:k] + "\n".join(rows) + "\n" + e[k:]
ep.write_text(e, encoding="utf-8")
print(f"East Asia: {len(rows)} statutes added")
