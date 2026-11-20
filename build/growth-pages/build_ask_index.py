"""Build the search index behind "Ask IMR" (Tanya IMR) on the Legal Clinic page.

Reads only the published databases in data/ and the legal-help directory, and writes
site/legal-clinic/ask/ask-index.json. Nothing is generated or paraphrased here: every
record keeps the database's own wording, its source and its checking status.

Run from the repository root:  python3 build/growth-pages/build_ask_index.py
Rerun after any change to data/ or site/legal-help/places.js.
"""
import csv
import datetime
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "site" / "legal-clinic" / "ask" / "ask-index.json"


def rows(path):
    with open(DATA / path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def short(text, n=320):
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


# Country names in English and Indonesian, and the words people type for them.
# Only countries that appear somewhere in the databases are kept in the output.
COUNTRIES = {
    "MY": ("Malaysia", "Malaysia", "malaysia malaysian kuala lumpur sabah sarawak johor penang"),
    "SG": ("Singapore", "Singapura", "singapore singapura"),
    "TH": ("Thailand", "Thailand", "thailand thai bangkok"),
    "BN": ("Brunei", "Brunei", "brunei"),
    "HK": ("Hong Kong", "Hong Kong", "hong kong hongkong hk"),
    "MO": ("Macao", "Makau", "macao macau makau"),
    "TW": ("Taiwan", "Taiwan", "taiwan taipei"),
    "KR": ("South Korea", "Korea Selatan", "korea korsel korea selatan south korea seoul"),
    "JP": ("Japan", "Jepang", "japan jepang tokyo osaka"),
    "SA": ("Saudi Arabia", "Arab Saudi", "saudi arab saudi saudi arabia riyadh jeddah jeddah mekkah makkah madinah"),
    "AE": ("United Arab Emirates", "Uni Emirat Arab", "uae uea emirat emirates dubai abu dhabi sharjah"),
    "QA": ("Qatar", "Qatar", "qatar doha"),
    "KW": ("Kuwait", "Kuwait", "kuwait"),
    "BH": ("Bahrain", "Bahrain", "bahrain"),
    "OM": ("Oman", "Oman", "oman muscat"),
    "JO": ("Jordan", "Yordania", "jordan yordania amman"),
    "LB": ("Lebanon", "Lebanon", "lebanon libanon beirut"),
    "IL": ("Israel", "Israel", "israel"),
    "ID": ("Indonesia", "Indonesia", "indonesia indonesian"),
    "PH": ("Philippines", "Filipina", "philippines filipina filipino pinoy"),
    "VN": ("Vietnam", "Vietnam", "vietnam viet nam"),
    "NP": ("Nepal", "Nepal", "nepal"),
    "BD": ("Bangladesh", "Bangladesh", "bangladesh"),
    "IN": ("India", "India", "india"),
    "LK": ("Sri Lanka", "Sri Lanka", "sri lanka srilanka"),
    "PK": ("Pakistan", "Pakistan", "pakistan"),
    "AU": ("Australia", "Australia", "australia"),
    "NZ": ("New Zealand", "Selandia Baru", "new zealand selandia baru"),
    "US": ("United States", "Amerika Serikat", "united states amerika usa"),
    "CA": ("Canada", "Kanada", "canada kanada"),
    "GB": ("United Kingdom", "Inggris", "united kingdom uk inggris britain"),
    "ZA": ("South Africa", "Afrika Selatan", "south africa afrika selatan"),
    "KE": ("Kenya", "Kenya", "kenya"),
    "ZW": ("Zimbabwe", "Zimbabwe", "zimbabwe"),
    "GH": ("Ghana", "Ghana", "ghana"),
    "UG": ("Uganda", "Uganda", "uganda"),
    "NG": ("Nigeria", "Nigeria", "nigeria"),
    "CO": ("Colombia", "Kolombia", "colombia kolombia"),
    "CL": ("Chile", "Chili", "chile chili"),
    "AR": ("Argentina", "Argentina", "argentina"),
    "MX": ("Mexico", "Meksiko", "mexico meksiko"),
    "DE": ("Germany", "Jerman", "germany jerman"),
    "FR": ("France", "Prancis", "france prancis perancis"),
    "IT": ("Italy", "Italia", "italy italia"),
    "ES": ("Spain", "Spanyol", "spain spanyol"),
    "NL": ("Netherlands", "Belanda", "netherlands belanda"),
    "CY": ("Cyprus", "Siprus", "cyprus siprus"),
}

# Topic tags. Each record gets the tags whose codes or words it matches; the page
# matches the visitor's question to the same tags with its own word lists.
FEATURE_TAGS = {
    "wage": "wage", "pay": "wage", "hours": "hours", "hrs": "hours", "rest": "hours", "leave": "hours",
    "doc": "passport", "mob": "employer", "fees": "fees", "fee": "fees", "ofee": "fees", "rec": "fees",
    "agen": "fees", "contract": "fees", "ocon": "fees", "con": "fees", "predep": "fees",
    "union": "union", "org": "union", "ins": "health", "soc": "health", "death": "health",
    "comp": "complain", "disp": "complain", "insp": "complain", "legalaid": "complain", "redress": "complain",
    "hotline": "complain", "res": "status", "fam": "family", "viol": "violence", "gender": "violence",
    "traffic": "trafficking", "live": "housing", "shelter": "violence", "welfare": "return",
    "return": "return", "home": "return", "exit": "status", "attache": "complain", "pdo": "fees",
    "wel": "return", "att": "complain", "bil": "fees", "lab": "coverage", "cov": "coverage",
}
SITUATION_TAGS = {
    "wages": "wage", "fees": "fees", "forced": "trafficking", "arrest": "status", "residence": "status",
    "injury": "health", "health": "health", "discrimination": "equality", "dismissed": "employer",
    "welfare": "return", "housing": "housing", "union": "union", "passport": "passport",
    "coverage": "coverage", "employer": "employer",
    # issues column
    "equality": "equality", "expulsion": "status", "detention": "status", "asylum": "status",
    "recruitment": "fees", "nationality": "status", "status": "status", "family": "family",
    "children": "family", "mobility": "employer", "abuse": "violence", "violence": "violence",
    "trafficking": "trafficking", "dismissal": "employer", "contract": "fees", "hours": "hours",
    "exit": "status", "punish": "status", "criminal": "status", "nonrefoulement": "status",
}
WORD_TAGS = [
    ("wage", r"\b(wage|salar|pay|paid|unpaid)"), ("hours", r"\b(hours|rest day|day off|leave)\b"),
    ("passport", r"passport"), ("fees", r"(recruit|agenc|placement fee|debt bondage)"),
    ("violence", r"(violence|abuse|harass|rape|assault)"), ("trafficking", r"(traffick|forced labo)"),
    ("status", r"(deport|detention|detain|visa|overstay|immigration|residence permit)"),
    ("union", r"\bunion"), ("health", r"(injur|accident|insurance|sick|death|died)"),
    ("family", r"(family|child|spouse)"), ("housing", r"(housing|dormitor|accommodation)"),
    ("domestic", r"(domestic work|domestic employee|household|maid)"),
    ("farm", r"(agricultur|plantation|farm|estate worker|palm)"), ("fishing", r"(fish|seafar|crew|vessel|ship)"),
]


def tags_for(codes=(), text=""):
    tags = {FEATURE_TAGS.get(c) or SITUATION_TAGS.get(c) for c in codes}
    low = (text or "").lower()
    for tag, pat in WORD_TAGS:
        if re.search(pat, low):
            tags.add(tag)
    tags.discard(None)
    return sorted(tags)


def codebook(path, key, en, idn, levels):
    """Return {feature: (name_en, name_id, {value: (label_en, label_id)})} for the codebook layouts in data/."""
    out = {}
    for r in rows(path):
        labels = {}
        for v in "210":
            le = r.get(levels[0].format(v), "")
            li = r.get(levels[1].format(v), "")
            labels[v] = (le, li)
        out[r[key]] = (r.get(en, ""), r.get(idn, ""), labels)
    return out


def main():
    rules, laws, decisions, help_places = [], [], [], []

    # 1. Coded rules (what the law says, feature by feature)
    sea = codebook("southeast-asia/codebook.csv", "feature", "name", "name_id", ("value_{}", "value_{}_id"))
    for r in rows("southeast-asia/codings.csv"):
        cb = sea.get(r["feature"], ("", "", {}))
        rules.append(dict(c=r["state"], g=r["group_name"], f=r["feature_name"], fi=cb[1],
                          v=r["value_label"], vi=cb[2].get(r["value"], ("", ""))[1], n=short(r["note"], 420),
                          s=short(r["source"], 220), e=r["evidence"], p="/southeast-asia/",
                          t=tags_for([r["feature"]], r["group_name"])))
    ea = codebook("east-asia/codebook.csv", "k", "en", "id", ("l{}", "l{}_id"))
    for r in rows("east-asia/codings.csv"):
        rules.append(dict(c=r["state"], g=r["group_name"], f=r["feature_name"], fi=sea.get(r["feature"], ("", "", {}))[1],
                          v=r["value_label"], vi=sea.get(r["feature"], ("", "", {}))[2].get(r["value"], ("", ""))[1],
                          n=short(r["note"], 420), s=short(r["source"], 220), e=r["evidence"], p="/east-asia/",
                          t=tags_for([r["feature"]], r["group_name"])))
    for path, cbpath, page in (("countries-of-origin/codings.csv", "countries-of-origin/codebook.csv", "/countries-of-origin/"),
                               ("countries-of-origin/protection.csv", "countries-of-origin/protection-codebook.csv", "/countries-of-origin/")):
        cb = codebook(cbpath, "k", "en", "id", ("l{}", "l{}_id"))
        for r in rows(path):
            f = cb.get(r["feature"], ("", "", {}))
            rules.append(dict(c=r["country"], g=r["country_name"] + " · " + "country of origin", gi=r["country_name"] + " · negara asal",
                              f=r["feature_name"], fi=f[1], v=r["value_label"], vi=f[2].get(r["value"], ("", ""))[1],
                              n=short(r["note"], 420), s=short(r["source"], 220), e=r["evidence"], p=page,
                              t=tags_for([r["feature"]]), o=1))
    dw = {}
    for r in rows("domestic-workers/codebook.csv"):
        dw[(r["role"], r["feature"])] = (r["label_id"], {v: r.get(v + "_id", "") for v in "210"})
    for r in rows("domestic-workers/codings.csv"):
        f = dw.get((r["role"], r["feature"]), ("", {}))
        role = "domestic workers" if r["role"] == "destination" else "domestic workers going abroad"
        role_id = "pekerja rumah tangga" if r["role"] == "destination" else "pekerja rumah tangga yang berangkat"
        rules.append(dict(c=r["country"], g=r["country_name"] + " · " + role, gi=r["country_name"] + " · " + role_id,
                          f=r["feature_name"], fi=f[0], v=r["value_label"], vi=f[1].get(r["value"], ""),
                          n=short(r["note"], 420), s=short(r["source"], 220), e=r["evidence"], p="/domestic-workers/",
                          t=sorted(set(tags_for([r["feature"]])) | {"domestic"}), o=1 if r["role"] != "destination" else 0))

    # 2. Laws and policies, with the official link the database gives
    for path, page in (("southeast-asia/domestic-laws.csv", "/southeast-asia/"), ("east-asia/domestic-laws.csv", "/east-asia/"),
                       ("gcc/domestic-laws.csv", "/gcc/"), ("countries-of-origin/laws-policies.csv", "/countries-of-origin/"),
                       ("migration-law/national-laws.csv", "/migration-law/national-laws/")):
        for r in rows(path):
            laws.append(dict(c=r["s"], ti=r["title"], or_=r.get("orig", ""), y=r.get("year", ""),
                             tp=short(r.get("topic", ""), 240), u=r.get("url", ""), p=page,
                             t=tags_for([], r.get("topic", "") + " " + r["title"] + " " + r.get("groups", ""))))

    # 3. Court decisions (plain-language summaries in English and Indonesian)
    for r in rows("court-decisions/decisions.csv"):
        codes = [x for x in (r["issues"] + ";" + r["situations"]).split(";") if x]
        decisions.append(dict(id=r["id"], c=r["country"], nm=short(r["name"], 160), ct=r["court"], d=r["date"][:4],
                              oc=r["outcome"], st=r["status"], pe=short(r["plain_en"]), pi=short(r["plain_id"]),
                              t=tags_for(codes, r["name"] + " " + r["sector"] + " " + r["plain_en"])))

    # 4. Free legal help (verified phone numbers only, as on /legal-help/)
    places_js = str(ROOT / "site" / "legal-help" / "places.js")
    script = ("global.window={};global.document={addEventListener(){},querySelector(){return null}};"
              "try{require(process.argv[1])}catch(e){};process.stdout.write(JSON.stringify(window.LEGAL_HELP))")
    dump = subprocess.run(["node", "-e", script, places_js],
                          capture_output=True, text=True, check=True).stdout
    lh = json.loads(dump)
    for p in lh["places"]:
        help_places.append(dict(c=p["c"], ty=p["t"], nm=p["n"], city=p.get("city_id") or p.get("city", ""),
                                tel=p.get("tel", []), web=p.get("web", ""), de=short(p.get("d", ""), 220),
                                di=short(p.get("d_id", ""), 220)))

    used = {r["c"] for r in rules} | {r["c"] for r in laws} | {r["c"] for r in decisions} | {r["c"] for r in help_places}
    countries = {k: dict(en=v[0], id=v[1], a=v[2]) for k, v in COUNTRIES.items() if k in used}
    for k, v in lh["countries"].items():
        if k in used and k not in countries:
            countries[k] = dict(en=v["en"], id=v["id"], a=v["en"].lower() + " " + v["id"].lower())

    # One small file per country, loaded only when a visitor asks about that country,
    # so the page stays light on weak phone connections.
    def dumps(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    (OUT.parent / "c").mkdir(exist_ok=True)
    for old in (OUT.parent / "c").glob("*.json"):
        old.unlink()
    for code in countries:
        part = dict(rules=[r for r in rules if r["c"] == code], laws=[r for r in laws if r["c"] == code],
                    decisions=[r for r in decisions if r["c"] == code], help=[r for r in help_places if r["c"] == code])
        countries[code]["n"] = [len(part["rules"]), len(part["laws"]), len(part["decisions"]), len(part["help"])]
        (OUT.parent / "c" / f"{code}.json").write_text(dumps(part), encoding="utf-8")
    # Help that works across borders is shown with every country.
    cross = [r for r in help_places if r["c"] == "XB"]
    index = dict(built=datetime.date.today().isoformat(), countries=countries, cross=cross,
                 totals=[len(rules), len(laws), len(decisions), len(help_places)])
    OUT.write_text(dumps(index), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(rules)} rules, {len(laws)} laws, {len(decisions)} decisions, "
          f"{len(help_places)} help places, {len(countries)} countries, index {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
