# Builds hv-data.js and the CSV/BibTeX downloads for /hate-speech-voting/.
# Inputs: codings.py, vparty_out.json and vdem_out.json (from V-Dem v16 and V-Party via the vdemdata package),
# country covariates from the Farmworker Norms Atlas (World Bank). Usage: python3 build_data.py OUTDIR
import json, sys, os, re, csv, io, math
sys.path.insert(0, os.path.dirname(__file__))
from codings import COUNTRIES, C, INTL, HCA
B = os.path.dirname(__file__)
OUT = sys.argv[1]; os.makedirs(OUT + "/data", exist_ok=True)
VERSION, UPDATED = "1.1", "2026-10-31"

vp = json.load(open(B + "/vparty_out.json")); VP, PARTIES = vp["vp"], vp["parties"]
VD = json.load(open(B + "/vdem_out.json"))
atlas = open("/mnt/project-files/theimr-site/atlas/index.html").read()
COV = json.loads(re.search(r"const COV = (\{.*?\});", atlas, re.S).group(1))
_hs = open("/mnt/project-files/theimr-site/government-hate-speech/hs-data.js").read()
HS = {r.get("iso3"): r for r in json.loads(_hs[_hs.index("{"):_hs.rstrip().rstrip(";").rindex("}") + 1])["rows"]}
# OSCE ODIHR hate crime figures (optional, from the iMac collection): {iso3: {"xeno_pm":..., "recorded":..., "prosecuted":..., "sentenced":..., "year":...}}
# Built from odihr/odihr.csv (ODIHR hatecrime.osce.org, 2019-2024, collected 2026-10-31) and odihr/pop2023.csv (World Bank SP.POP.TOTL).
# xeno_pm and total_pm: median over available years of police-recorded crimes per million; pros_rate: prosecuted per 100 police-recorded,
# median of yearly shares (at least two years, shares above 100 dropped); sent_rate likewise for sentenced. Medians blunt one-year breaks in national series.
def _num(v): return float(v) if v not in ("", None) else None
ODIHR = list(csv.DictReader(open(B + "/odihr/odihr.csv")))
POP = {r["iso3"]: float(r["population_2023"]) for r in csv.DictReader(open(B + "/odihr/pop2023.csv"))}
def _med(a): a = sorted(a); n = len(a); return None if not n else (a[n // 2] if n % 2 else (a[n // 2 - 1] + a[n // 2]) / 2)
OSCE = {}
for iso in POP:
    rx = [r for r in ODIHR if r["iso3"] == iso and r["category"] == "racism_xenophobia" and _num(r["police_recorded"]) is not None]
    rt = [r for r in ODIHR if r["iso3"] == iso and r["category"] == "total" and _num(r["police_recorded"]) is not None]
    def share(col):  # yearly share of police-recorded totals; years above 1 dropped (units and periods differ between police, prosecutors and courts)
        a = [_num(r[col]) / _num(r["police_recorded"]) for r in rt if _num(r[col]) is not None and _num(r["police_recorded"]) > 0]
        a = [x for x in a if x <= 1]
        return (round(100 * _med(a), 1) if len(a) >= 2 else None), len(a)
    pr, prn = share("prosecuted"); se, sen = share("sentenced")
    OSCE[iso] = {"xeno_pm": round(_med([_num(r["police_recorded"]) / POP[iso] * 1e6 for r in rx]), 1) if rx else None, "xeno_years": len(rx),
                 "total_pm": round(_med([_num(r["police_recorded"]) / POP[iso] * 1e6 for r in rt]), 1) if rt else None, "total_years": len(rt),
                 "pros_rate": pr, "pros_years": prn, "sent_rate": se, "sent_years": sen}
WB = {"United States":"United States of America","South Korea":"Republic of Korea"}

CODEBOOK = [
 {"k":"const","en":"Constitutional equality guarantee","id":"Jaminan kesetaraan dalam konstitusi",
  "l2":"Text expressly extends rights or equal treatment to foreigners or non-citizens, or to all persons irrespective of nationality",
  "l1":"Universal wording (everyone, every person, all persons) without naming non-citizens, or a citizens-only clause paired with a universal one",
  "l0":"No general equality guarantee, or a guarantee framed for citizens or nationals only",
  "l2_id":"Teks secara tegas memberikan hak atau perlakuan setara kepada orang asing atau bukan warga negara, atau kepada semua orang tanpa memandang kewarganegaraan",
  "l1_id":"Rumusan universal (setiap orang, semua orang) tanpa menyebut orang yang bukan warga negara, atau klausul khusus warga negara yang disertai klausul universal",
  "l0_id":"Tidak ada jaminan kesetaraan umum, atau jaminan hanya untuk warga negara"},
 {"k":"adl","en":"Anti-discrimination statute","id":"Undang-undang antidiskriminasi",
  "l2":"A general civil, labor or penal statute lists nationality, citizenship or immigration status as a protected ground",
  "l1":"A statute covers race, ethnicity, colour or national origin, but not nationality or citizenship",
  "l0":"No general anti-discrimination statute",
  "l2_id":"Undang-undang perdata, ketenagakerjaan atau pidana umum mencantumkan kewarganegaraan atau status imigrasi sebagai dasar yang dilindungi",
  "l1_id":"Undang-undang mencakup ras, etnis, warna kulit atau asal kebangsaan, tetapi tidak kewarganegaraan",
  "l0_id":"Tidak ada undang-undang antidiskriminasi umum"},
 {"k":"hsl","en":"Hate speech law","id":"Hukum ucapan kebencian",
  "l2":"The protected grounds name nationality or citizenship, a nation or national group, or foreigners or migrants",
  "l1":"The protected grounds cover race, ethnicity, colour, religion or national origin only",
  "l0":"No prohibition of group-directed hate speech beyond incitement to imminent violence",
  "l2_id":"Dasar yang dilindungi menyebut kewarganegaraan, bangsa atau kelompok kebangsaan, atau orang asing atau migran",
  "l1_id":"Dasar yang dilindungi hanya ras, etnis, warna kulit, agama atau asal kebangsaan",
  "l0_id":"Tidak ada larangan ucapan kebencian terhadap kelompok selain hasutan kekerasan langsung"},
 {"k":"mig","en":"Migrant-specific equality guarantee","id":"Jaminan kesetaraan khusus migran",
  "l2":"A migration or foreigners statute guarantees migrants equal treatment or prohibits discrimination against them, with a remedy",
  "l1":"A statute or national plan commits the state to counter xenophobia or discrimination against migrants, without an individual remedy",
  "l0":"None",
  "l2_id":"Undang-undang migrasi atau orang asing menjamin perlakuan setara bagi migran atau melarang diskriminasi terhadap mereka, dengan upaya hukum",
  "l1_id":"Undang-undang atau rencana nasional mewajibkan negara melawan xenofobia atau diskriminasi terhadap migran, tanpa upaya hukum individual",
  "l0_id":"Tidak ada"},
]
FEATS = [d["k"] for d in CODEBOOK]

def at(cell, year):
    v, since, prior = cell[0], cell[1], cell[2]
    if year is None or since is None or since <= year: return v
    return prior if prior is not None else 0

rows, codes, profiles = [], {}, []
for iso, name, name_id, grp, esys in COUNTRIES:
    cc = C[iso]; vd = VD[iso]; p = VP.get(iso); wb = COV.get(WB.get(name, name)) or {}
    if iso == "KEN": p = None  # latest V-Party election with vote shares is 2007: too far from the period
    year = p["vp_year"] if p else None
    idx = sum(cc[f][0] for f in FEATS)
    idx_el = sum(at(cc[f], year) for f in FEATS) if year else None
    expl = int(cc["const"][0] == 2 or cc["mig"][0] == 2)
    codes[iso] = {f: [cc[f][0], cc[f][3], cc[f][4], cc[f][1], cc[f][2]] for f in FEATS}
    ic = INTL[iso]
    r = {"id": name, "iso3": iso, "western": 1 if grp == "W" else 0, "group": "Western" if grp == "W" else "Non-Western",
         "explicit": expl, "expl_index": idx, "expl_index_el": idx_el,
         "const": cc["const"][0], "adl": cc["adl"][0], "hsl": cc["hsl"][0], "mig": cc["mig"][0],
         "hsl_nat": int(cc["hsl"][0] == 2), "adl_nat": int(cc["adl"][0] == 2),
         "icerd14": ic[1], "icrmw": ic[2],
         "polhate": vd["polhate"], "polhate_mean5": vd["polhate_mean5"], "polhate_chg": round(vd["polhate"] - vd["polhate_2015"], 2),
         "tgt_relig": vd["tgt_relig"], "tgt_ethnic": vd["tgt_ethnic"], "tgt_race": vd["tgt_race"],
         "socgrp_ineq": vd["socgrp_ineq"], "polar": vd["polar"], "libdem": vd["libdem"], "regime": vd["regime"],
         "democracy": 1 if vd["regime"] >= 2 else 0,
         "elec_year": year, "polhate_elec": vd.get("polhate_by_year", {}).get(str(year)) if year else None,
         "nativist_vote": p["nativist_vote"] if p else None, "restrict_vote": p["restrict_vote"] if p else None,
         "stance": p["stance"] if p else None, "vote_cover": p["vp_cover"] if p else None,
         "system": esys, "majoritarian": 1 if esys == "Majoritarian" else 0,
         "hca": HCA[iso][0], "hca_nat": int(HCA[iso][0] == 2), "acjst": vd["acjst"], "eqprotec": vd["eqprotec"], "rule": vd["rule"],
         "shi": HS.get(iso, {}).get("shi"), "pew_mob_yrs": HS.get(iso, {}).get("pew_mob_yrs"), "pew_comm_yrs": HS.get(iso, {}).get("pew_comm_yrs"),
         "acled_mob": HS.get(iso, {}).get("acled_mob"),
         "osce_xeno_pm": OSCE.get(iso, {}).get("xeno_pm"), "osce_total_pm": OSCE.get(iso, {}).get("total_pm"), "osce_pros_rate": OSCE.get(iso, {}).get("pros_rate"), "osce_pros_years": OSCE.get(iso, {}).get("pros_years"), "osce_sent_rate": OSCE.get(iso, {}).get("sent_rate"), "osce_sent_years": OSCE.get(iso, {}).get("sent_years"),
         "migstock": wb.get("migstock"), "gdppc": round(wb["gdppc"]) if wb.get("gdppc") else None}
    rows.append(r)

LIT = [
 ["Coppedge, M., Gerring, J., Knutsen, C. H., Lindberg, S. I., Teorell, J., et al. (2026). V-Dem Dataset v16. Varieties of Democracy (V-Dem) Project.", "https://doi.org/10.23696/vdemds26"],
 ["Graells-Garrido, E., Opitz, D., Rowe, F., & Cabrera, C. (2026). Hate speech toward migrants on a citizen reporting platform concentrates in neighborhoods undergoing demographic change. arXiv:2608.12581 (preprint).", "https://arxiv.org/abs/2608.12581"],
 ["Lührmann, A., Düpont, N., Higashijima, M., et al. (2020). Varieties of Party Identities and Organizations (V-Party) Dataset. V-Dem Institute. Distributed in the vdemdata R package.", "https://github.com/vdeminstitute/vdemdata"],
 ["Mechkova, V., Pemstein, D., Seim, B., & Wilson, S. Digital Society Project dataset (items v2smpolhate and v2smhargr in V-Dem).", "https://digitalsocietyproject.org/"],
 ["World Bank. World Development Indicators: SM.POP.TOTL.ZS (international migrant stock, % of population) and NY.GDP.PCAP.CD.", "https://data.worldbank.org/"],
 ["Bleich, E. (2011). The Freedom to Be Racist? How the United States and Europe Struggle to Preserve Freedom and Combat Racism. Oxford University Press.", ""],
 ["Bosniak, L. (2006). The Citizen and the Alien: Dilemmas of Contemporary Membership. Princeton University Press.", ""],
 ["Martikainen, T. (2020). The role of religion in migrant incorporation. In C. Inglis, W. Li & B. Khadria (Eds.), The SAGE Handbook of International Migration. SAGE.", "https://doi.org/10.4135/9781526470416"],
 ["Mudde, C. (2007). Populist Radical Right Parties in Europe. Cambridge University Press.", ""],
 ["Müller, K., & Schwarz, C. (2021). Fanning the flames of hate: Social media and hate crime. Journal of the European Economic Association, 19(4), 2131–2167.", ""],
 ["McCann, W. S., & Boateng, F. D. (2022). An analysis of hate crime victimization amongst immigrants. American Journal of Criminal Justice, 47, 795–817.", "https://doi.org/10.1007/s12103-021-09616-x"],
 ["Suárez-Vergne, Á. (2026). Mapping hate crime research in Europe: Trends, challenges, and future directions. Deviant Behavior.", "https://doi.org/10.1080/01639625.2025.2612264"],
 ["van Spanje, J., & de Vreese, C. (2015). The good, the bad and the voter: The impact of hate speech prosecution of a politician on the electoral support for his party. Party Politics, 21(1), 115–130.", ""],
 ["Pew Research Center (2025). Global Restrictions on Religion, 2007–2022 public dataset and 2023 Social Hostilities Index (items SHI_Q_2 mob violence and SHI_Q_3 communal violence).", "https://www.pewresearch.org/religion/"],
 ["Raleigh, C., Kishi, R., & Linke, A. Armed Conflict Location & Event Data (ACLED), regional aggregated data, sub-event type Mob violence, 2021–2025.", "https://acleddata.com/"],
 ["OSCE Office for Democratic Institutions and Human Rights (ODIHR). Hate Crime Reporting: national data on police-recorded, prosecuted and sentenced hate crimes.", "https://hatecrime.osce.org/"],
 ["UN Committee on the Elimination of Racial Discrimination (2004). General Recommendation No. 30: Discrimination against non-citizens.", "https://www.ohchr.org/en/treaty-bodies/cerd"],
 ["UN Committee on the Elimination of Racial Discrimination (2013). General Recommendation No. 35: Combating racist hate speech.", "https://www.ohchr.org/en/treaty-bodies/cerd"],
]
CHANGELOG = [[UPDATED, "1.1", "Added a test of whether the electoral popularity of anti-immigrant parties goes with hate crime, using Pew social hostilities and mob violence items and ACLED mob violence rates, with a slot for OSCE ODIHR police-recorded hate crimes.", "Menambahkan uji apakah popularitas elektoral partai anti-imigran berjalan bersama kejahatan kebencian, memakai butir permusuhan sosial dan kekerasan massa Pew serta tingkat kekerasan massa ACLED, dengan tempat untuk kejahatan kebencian tercatat polisi OSCE ODIHR."], [UPDATED, "1.0", "First release: 34 constitutional democracies, four legal features coded with notes and sources, an impunity layer (hate crime aggravation and V-Dem access to justice), V-Dem v16 and V-Party outcomes.", "Rilis pertama: 34 demokrasi konstitusional, empat fitur hukum dikodekan dengan catatan dan sumber, lapisan kekebalan (pemberatan kejahatan kebencian dan akses keadilan V-Dem), hasil dari V-Dem v16 dan V-Party."]]

data = {"version": VERSION, "updated": UPDATED, "codebook": CODEBOOK, "countries": [{"k": c[0], "n": c[1], "n_id": c[2], "g": c[3]} for c in COUNTRIES],
        "codes": codes, "hca": {k: [v[0], v[3], v[4], v[1], v[2]] for k, v in HCA.items()}, "intl": {k: list(v) for k, v in INTL.items()}, "rows": rows, "osce_ready": bool(OSCE), "parties": PARTIES, "lit": LIT, "changelog": CHANGELOG}
open(OUT + "/hv-data.js", "w").write("/* Data for the hate speech, voting and non-citizen protection comparison. Built by build_data.py. */\nwindow.HV = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")

def wcsv(path, fields, recs):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in recs]
LV = {2: "explicit", 1: "general", 0: "none"}
cod = []
for iso, name, *_ in COUNTRIES:
    for d in CODEBOOK:
        c = C[iso][d["k"]]
        cod.append({"iso3": iso, "country": name, "feature": d["k"], "feature_name": d["en"], "value": c[0], "value_label": LV[c[0]], "in_force_since": c[1] or "", "prior_value": "" if c[2] is None else c[2], "note": c[3], "source": c[4], "evidence": "S", "coded": UPDATED, "checked_official_text": "no"})
wcsv(OUT + "/data/codings.csv", list(cod[0].keys()), cod)
for iso, name, *_ in COUNTRIES:
    c = HCA[iso]
    cod.append({"iso3": iso, "country": name, "feature": "hca", "feature_name": "Hate crime aggravation (impunity layer, not in index)", "value": c[0], "value_label": LV[c[0]], "in_force_since": c[1] or "", "prior_value": "" if c[2] is None else c[2], "note": c[3], "source": c[4], "evidence": "S", "coded": UPDATED, "checked_official_text": "no"})
wcsv(OUT + "/data/codings.csv", list(cod[0].keys()), cod)
wcsv(OUT + "/data/codebook.csv", ["feature", "name", "value_2", "value_1", "value_0"], [{"feature": d["k"], "name": d["en"], "value_2": d["l2"], "value_1": d["l1"], "value_0": d["l0"]} for d in CODEBOOK])
fields = ["iso3", "id", "group", "western", "explicit", "expl_index", "expl_index_el", "const", "adl", "hsl", "mig", "icerd14", "icrmw", "polhate", "polhate_mean5", "polhate_chg", "tgt_relig", "tgt_ethnic", "tgt_race", "socgrp_ineq", "polar", "libdem", "regime", "elec_year", "polhate_elec", "nativist_vote", "restrict_vote", "stance", "vote_cover", "system", "majoritarian", "hca", "acjst", "eqprotec", "rule", "shi", "pew_mob_yrs", "pew_comm_yrs", "acled_mob", "osce_xeno_pm", "osce_total_pm", "osce_pros_rate", "osce_pros_years", "osce_sent_rate", "osce_sent_years", "migstock", "gdppc"]
wcsv(OUT + "/data/country-data.csv", fields, rows)
wcsv(OUT + "/data/odihr-hate-crime-2019-2024.csv", list(ODIHR[0].keys()), ODIHR)
wcsv(OUT + "/data/parties.csv", ["iso3", "year", "party", "abbr", "vote", "immig_osp", "people_osp", "restrictive", "nativist", "mapped_from"], PARTIES)
wcsv(OUT + "/data/treaty-status.csv", ["iso3", "icerd", "icerd_art14", "icrmw"], [{"iso3": k, "icerd": "" if v[0] is None else v[0], "icerd_art14": "" if v[1] is None else v[1], "icrmw": "" if v[2] is None else v[2]} for k, v in INTL.items()])
open(OUT + "/data/imr-hate-speech-voting.bib", "w").write("""@misc{imr_hate_speech_voting_2026,
  author       = {{Institute for Migrant Rights}},
  title        = {Hate Speech, Voting and the Legal Protection of Non-Citizens: A Comparative Dataset of 34 Constitutional Democracies},
  year         = {2026},
  version      = {%s},
  howpublished = {\\url{https://theimr.org/hate-speech-voting/}},
  note         = {Accessed: [date]. Licensed CC BY 4.0}
}
""" % VERSION)
print(len(rows), "rows", len(cod), "cells", len(PARTIES), "parties")
