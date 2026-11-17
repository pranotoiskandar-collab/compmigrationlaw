"""Builds dw-data.js and the CSV downloads for /domestic-workers/. Run: python3 build_data.py SITE_DIR"""
import csv, json, sys, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codebook import DCB, OCB
from countries import COUNTRIES, REGIONS, NORMLEX_NAME
import codings_dest, codings_dest2, codings_origin, instruments

VERSION, UPDATED = "1.3", "2026-11-11"
SITE = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/theimr-site"
OUT = os.path.join(SITE, "domestic-workers"); os.makedirs(os.path.join(OUT, "data"), exist_ok=True)

def parse(raw, keys):
    out = {}
    for c, block in raw.items():
        cells = {}
        for line in block.strip().splitlines():
            k, v, note, src, ev = (line.split("|") + ["", "", "", ""])[:5]
            assert k in keys, (c, k)
            cells[k] = [int(v) if v != "" else None, note.strip(), src.strip(), ev.strip() or ("P" if c == "AE" else "S")]
        missing = [k for k in keys if k not in cells]; assert not missing, (c, missing)
        out[c] = cells
    return out

DK = [d[0] for d in DCB]; OK = [d[0] for d in OCB]
DC = parse(dict(codings_dest.RAW, **codings_dest2.RAW), DK); OC = parse(codings_origin.RAW, OK)

# ---------- treaty status ----------
TRE = [("C189","ILO C189 Domestic Workers"),("C181","ILO C181 Private Employment Agencies"),("C97","ILO C97 Migration for Employment"),
       ("C143","ILO C143 Migrant Workers (Supplementary)"),("C190","ILO C190 Violence and Harassment"),("P29","ILO Forced Labour Protocol"),
       ("ICRMW","UN Migrant Workers Convention"),("ICESCR","UN Covenant on Economic, Social and Cultural Rights")]
OFFICIAL = {"C181","C190","P29","ICRMW","ICESCR"}   # in the NORMLEX / UN extract of 2026-10-30 (iMac)
rat = {}
for r in csv.DictReader(open("/mnt/project-files/farmworker-norms/ratifications_2026-10-30.csv")):
    rat[(r["instrument"], r["country"])] = r
# C189, C97, C143: checked on NORMLEX via the iMac, 2026-11-11 (P)
NX = {
 "C189": {"AR":("24 Mar 2014",""),"BO":("15 Apr 2013",""),"BR":("31 Jan 2018",""),"CL":("10 Jun 2015",""),"CR":("20 Jan 2014",""),
          "IT":("22 Jan 2013",""),"MX":("03 Jul 2020",""),"NA":("09 Dec 2020",""),"PY":("07 May 2013",""),"PE":("26 Nov 2018",""),
          "PH":("05 Sep 2012",""),"ZA":("20 Jun 2013",""),"ES":("28 Feb 2023",""),"UY":("14 Jun 2012","")},
 "C97": {"BR":("18 Jun 1965",""),"IL":("30 Mar 1953",""),"IT":("22 Oct 1952",""),"KE":("30 Nov 1965","Annexes I-III excluded"),
         "MY":("03 Mar 1964","Sabah only; Annexes I-III excluded"),"MA":("14 Jun 2019","Annexes I-III excluded"),
         "PH":("21 Apr 2009","Annexes II-III excluded"),"ES":("21 Mar 1967",""),"GB":("22 Jan 1951","Annexes I and III excluded"),
         "TZ":("22 Jun 1964","Zanzibar only; Annexes I-III excluded"),"UY":("18 Mar 1954",""),"ZM":("02 Dec 1964","Annexes I-III excluded"),
         "HK":("01 Jul 1997","Declared applicable to Hong Kong SAR by China")},
 "C143": {"IT":("23 Jun 1981",""),"KE":("09 Apr 1979",""),"PH":("14 Sep 2006",""),"UG":("31 Mar 1978","")},
}
TS = {}
for c in COUNTRIES:
    k = c[0]; TS[k] = {}
    for t, _ in TRE:
        if k == "TW": TS[k][t] = ["ne", "", "Not eligible to join UN or ILO treaties", "S"]; continue
        if k == "HK" and t in NX:
            v = NX[t].get(k); TS[k][t] = ["yes", v[0], v[1], "P"] if v else ["no", "", "Not declared applicable to Hong Kong SAR", "P"]; continue
        if k == "HK" and t != "ICESCR":
            TS[k][t] = ["na", "", "Application to Hong Kong depends on China's declarations; not coded", "S"]; continue
        if t in OFFICIAL:
            r = rat.get((t, NORMLEX_NAME[k]))
            if r and r["status"] in ("in force", "party"): TS[k][t] = ["yes", r["date"], "", "P"]
            elif r and "not yet in force" in r["status"]: TS[k][t] = ["pending", r["date"], "Ratified, not yet in force", "P"]
            elif r and r["status"] == "signatory only": TS[k][t] = ["sig", "", "Signed only", "P"]
            else: TS[k][t] = ["no", "", "", "P"]
        else:
            v = NX.get(t, {}).get(k)
            TS[k][t] = ["yes", v[0], v[1], "P"] if v else ["no", "", "", "P"]
    if k == "HK": TS[k]["ICESCR"][2] = "Applies to Hong Kong (China's party status)"

# ---------- instruments ----------
INS = []
for line in instruments.ROWS.strip().splitlines():
    f = line.split("|"); assert len(f) == 12, (len(f), line[:40])
    i, tier, reg, cs, typ, y, inf, iss, title, en, idt, topics = f
    INS.append({"id": i, "tier": tier, "region": reg, "countries": cs, "type": typ, "year": int(y), "in_force": inf, "issuer": iss,
                "title": title, "sum": en, "sum_id": idt, "topics": [x for x in topics.split(",") if x],
                "binding": 1 if typ in ("treaty", "protocol", "statute", "reg", "judgment") else 0,
                "evidence": "P" if i == "N-AE-9-2022" else "S"})

S = [{"k": c[0], "n": c[1], "n_id": c[2], "role": c[3], "region": c[4], "iso3": c[5]} for c in COUNTRIES]
G = {"version": VERSION, "updated": UPDATED, "countries": S, "regions": REGIONS,
     "dcb": [{"k": d[0], "en": d[1], "id": d[2], "bench": d[3], "l2": d[4][0], "l2_id": d[4][1], "l1": d[5][0], "l1_id": d[5][1], "l0": d[6][0], "l0_id": d[6][1]} for d in DCB],
     "ocb": [{"k": d[0], "en": d[1], "id": d[2], "bench": d[3], "l2": d[4][0], "l2_id": d[4][1], "l1": d[5][0], "l1_id": d[5][1], "l0": d[6][0], "l0_id": d[6][1]} for d in OCB],
     "dc": DC, "oc": OC, "treaties": TRE, "ts": TS, "ins": INS,
     "changelog": [[UPDATED, "1.3", "Saudi recruitment-company rules (MD 119698/2025) added; UAE gratuity note updated; Saudi Arabia: all 17 cells now coded from the Domestic Workers Regulation (MD 40676/1445) and the 2022 transfer decision; Oman wage and housing cells from the Official Gazette text; Bahrain agency licensing from LMRA Resolution 1/2014; earlier: ten Saudi cells recoded from the Domestic Workers Regulation (MD 40676/1445); Oman recoded from Ministerial Decision 574/2025 (which repeals the 2004 regulation); Bahrain recruitment fees recoded from Law 19/2006 art. 23(C); C189, C97 and C143 ratifications checked on NORMLEX (adds C97 for Morocco, Zambia, Tanzania-Zanzibar and Hong Kong SAR).", "Oman dikodekan ulang dari Keputusan Menteri 574/2025 (yang mencabut peraturan 2004); biaya rekrutmen Bahrain dikodekan ulang dari UU 19/2006 pasal 23(C); ratifikasi C189, C97 dan C143 diperiksa di NORMLEX (menambah C97 untuk Maroko, Zambia, Tanzania-Zanzibar dan Hong Kong SAR)."], [UPDATED, "1.2", "Saudi Arabia recoded from the ILO FAIRWAY factsheet (December 2023); UAE notes extended from the ILO FAIRWAY factsheet (May 2024); Kuwait recoded from the ILO FAIRWAY factsheet (December 2023); Qatar recoded from the ILO FAIRWAY factsheet (December 2023); Oman and Bahrain recoded from the ILO FAIRWAY factsheets (December 2023); six Gulf instruments added; treaty-status names fixed for Bolivia and Tanzania.", "Arab Saudi dikodekan ulang dari lembar fakta ILO FAIRWAY (Desember 2023); catatan UEA dilengkapi dari lembar fakta ILO FAIRWAY (Mei 2024); Kuwait dikodekan ulang dari lembar fakta ILO FAIRWAY (Desember 2023); Qatar dikodekan ulang dari lembar fakta ILO FAIRWAY (Desember 2023); Oman dan Bahrain dikodekan ulang dari lembar fakta ILO FAIRWAY (Desember 2023); enam instrumen Teluk ditambahkan; nama status perjanjian untuk Bolivia dan Tanzania diperbaiki."], [UPDATED, "1.1", "Added Morocco, Thailand, Pakistan, Namibia, Zambia, Tanzania, Brazil, Mexico, Costa Rica, Bolivia, Peru, Chile, Paraguay and Uruguay (34 destinations); all new cells from secondary sources.", "Menambahkan Maroko, Thailand, Pakistan, Namibia, Zambia, Tanzania, Brasil, Meksiko, Kosta Rika, Bolivia, Peru, Chili, Paraguay dan Uruguay (34 negara tujuan); semua sel baru dari sumber sekunder."], [UPDATED, "1.0", "First release: 20 destination and 10 origin jurisdictions, 89 instruments. UAE coded from the official translation; other cells from secondary sources, being checked.",
                    "Rilis pertama: 20 yurisdiksi tujuan dan 10 negara asal, 89 instrumen. UEA dikodekan dari terjemahan resmi; sel lain dari sumber sekunder, sedang diperiksa."]]}
G["changelog"][1][2] = G["changelog"][1][2].replace("89", "92"); G["changelog"][1][3] = G["changelog"][1][3].replace("89", "92")
open(os.path.join(OUT, "dw-data.js"), "w").write("/* IMR migrant domestic workers database, data v%s (%s). CC BY 4.0. */\nwindow.DW=%s;\n" % (VERSION, UPDATED, json.dumps(G, ensure_ascii=False, separators=(",", ":"))))

# ---------- CSVs ----------
def wcsv(name, fields, rows):
    with open(os.path.join(OUT, "data", name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); [w.writerow(r) for r in rows]
nm = {c[0]: c for c in COUNTRIES}
rows = []
for c, cells in DC.items():
    for d in DCB:
        v = cells[d[0]]; rows.append({"country": c, "country_name": nm[c][1], "iso3": nm[c][5], "role": "destination", "feature": d[0], "feature_name": d[1], "benchmark": d[3],
            "value": "" if v[0] is None else v[0], "value_label": "" if v[0] is None else d[6 - v[0]][0] if False else {2: d[4][0], 1: d[5][0], 0: d[6][0]}[v[0]] if v[0] is not None else "",
            "note": v[1], "source": v[2], "evidence": v[3], "coded": UPDATED})
for c, cells in OC.items():
    for d in OCB:
        v = cells[d[0]]; rows.append({"country": c, "country_name": nm[c][1], "iso3": nm[c][5], "role": "origin", "feature": d[0], "feature_name": d[1], "benchmark": d[3],
            "value": "" if v[0] is None else v[0], "value_label": {2: d[4][0], 1: d[5][0], 0: d[6][0]}.get(v[0], ""), "note": v[1], "source": v[2], "evidence": v[3], "coded": UPDATED})
wcsv("codings.csv", ["country","country_name","iso3","role","feature","feature_name","benchmark","value","value_label","note","source","evidence","coded"], rows)
cb = [{"role": "destination", "feature": d[0], "label": d[1], "label_id": d[2], "benchmark": d[3], "2": d[4][0], "1": d[5][0], "0": d[6][0], "2_id": d[4][1], "1_id": d[5][1], "0_id": d[6][1]} for d in DCB] + \
     [{"role": "origin", "feature": d[0], "label": d[1], "label_id": d[2], "benchmark": d[3], "2": d[4][0], "1": d[5][0], "0": d[6][0], "2_id": d[4][1], "1_id": d[5][1], "0_id": d[6][1]} for d in OCB]
cb += [{"role": "all", "feature": "evidence", "label": "Evidence", "label_id": "Bukti", "benchmark": "", "2": "", "1": "", "0": "", "2_id": "", "1_id": "",
        "0_id": "P = coded from the official text; S = coded from secondary sources, not yet checked against the official text"},
       {"role": "all", "feature": "value", "label": "Missing value", "label_id": "Nilai kosong", "benchmark": "", "2": "", "1": "", "0": "", "2_id": "", "1_id": "", "0_id": "Blank = not yet determined"}]
wcsv("codebook.csv", ["role","feature","label","label_id","benchmark","2","1","0","2_id","1_id","0_id"], cb)
wcsv("instruments.csv", ["id","tier","region","countries","type","binding","year","in_force","issuer","title","sum","topics","evidence"],
     [dict({k: x[k] for k in ["id","tier","region","countries","type","binding","year","in_force","issuer","title","sum","evidence"]}, topics=";".join(x["topics"])) for x in INS])
wcsv("treaty-status.csv", ["country","country_name","instrument","status","date","note","evidence"],
     [{"country": c[0], "country_name": c[1], "instrument": t, "status": TS[c[0]][t][0], "date": TS[c[0]][t][1], "note": TS[c[0]][t][2], "evidence": TS[c[0]][t][3]} for c in COUNTRIES for t, _ in TRE])
print("instruments", len(INS), "cells", len(rows))
