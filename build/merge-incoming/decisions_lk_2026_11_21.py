"""Sri Lanka Court of Appeal decisions found on courtofappeal.lk (21 November 2026).

Usage: python3 build/merge-incoming/decisions_lk_2026_11_21.py OUT.json
Writes data/court-decisions/incoming/other-asia/court-decisions-2026-11-21-lk.csv (the incoming rows) and OUT.json
({"new": [...], "links": {}, "cites": {}}) for patch_site_decisions.py.

How they were found: the court's own judgment lists for 2010-2026 (courtofappeal.lk/judgments?year=...) were
searched in the court's keyword and legislation columns for foreign employment, the Bureau of Foreign Employment,
the Immigrants and Emigrants Act, deportation and human trafficking. Drug-trafficking cases and staff disputes of
the Bureau or the Labour Ministry were left out. Every entry is status C: the summaries rest on the court's own
keywords, and nobody has read the judgments yet. supremecourt.lk was not reachable (bot check).
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURT = "Court of Appeal of Sri Lanka"
NOTE = "Unverified (AI-gathered on 2026-11-21 from the Court of Appeal's own judgment list and keywords; judgment not yet read)."

# id, name, date, case no., branch, issues, situations, stages, forum, plain EN, plain ID, pdf
ROWS = [
    ("lk-ca-tukhtabonu-2015", "T. Tukhtabonu alias Jhonu Jausmin and Others v. Attorney General", "2015-10-21", "CA/HC/0081/2011",
     "criminal", ["trafficking"], ["forced"], [3], "destination",
     "Appeal in a human trafficking case: procuring women for prostitution; the sentences were questioned as too lenient (court's keywords; not yet read).",
     "Banding dalam perkara perdagangan orang: perekrutan perempuan untuk pelacuran; hukumannya dipersoalkan karena dianggap terlalu ringan (kata kunci pengadilan; belum dibaca).",
     "https://courtofappeal.lk/uploads/judgments/ca_hc_81_2011.pdf"),
    ("lk-ca-justin-perera-2016", "Liyanage Justin Perera v. Officer-in-Charge, Minor Offence Branch, Cinnamon Gardens Police Station", "2016-12-05", "CA/PHC/0120/2013",
     "criminal", ["recruitment"], ["fees"], [1], "origin",
     "Criminal revision: a man pleaded guilty in eleven cases of taking money on a promise of jobs abroad; the court looked at the consecutive sentences (court's keywords; not yet read).",
     "Revisi pidana: seorang laki-laki mengaku bersalah dalam sebelas perkara menerima uang dengan janji pekerjaan di luar negeri; pengadilan menilai hukuman yang dijalankan berturut-turut (kata kunci pengadilan; belum dibaca).",
     "https://courtofappeal.lk/uploads/judgments/ca_phc_120_2013.pdf"),
    ("lk-ca-maliyedda-2021", "Hettinayake Mudiyanselage Lilanthi Dinesha Maliyedda v. Attorney General", "2021-05-03", "CA/HCC/300/2016",
     "criminal", ["recruitment"], ["fees"], [1], "origin",
     "Appeal against conviction for cheating and criminal breach of trust in a foreign-employment fraud (court's keywords; not yet read).",
     "Banding atas putusan bersalah karena penipuan dan penggelapan dalam perkara penipuan kerja ke luar negeri (kata kunci pengadilan; belum dibaca).",
     "https://courtofappeal.lk/uploads/judgments/court-of-appeal-judgment-hcc-0300.16-copy.pdf"),
    ("lk-ca-frazer-2022", "Kayleigh Frazer v. Commissioner General of Immigration and Emigration", "2022-08-16", "CA/WRIT/0299/2022",
     "administrative", ["expulsion", "residence"], ["residence"], [4], "destination",
     "A foreign national challenged a deportation order and the refusal to extend her visa, issued after an alleged offence, under the Immigrants and Emigrants Act (court's keywords; not yet read).",
     "Seorang warga negara asing menggugat perintah deportasi dan penolakan perpanjangan visanya, yang dikeluarkan setelah dugaan suatu tindak pidana, berdasarkan Undang-Undang Imigran dan Emigran (kata kunci pengadilan; belum dibaca).",
     "https://courtofappeal.lk/uploads/judgments/12.-ca-writ-299-2022.pdf"),
    ("lk-ca-weerasinghe-2024", "Edward Weerasinghe and another v. Manusha Nanayakkara (Minister of Labour and Foreign Employment)", "2024-09-30", "CA/WRT/0821/2023",
     "administrative", ["recruitment"], ["fees"], [1], "origin",
     "Writ of mandamus over a foreign employment agency licence under the Sri Lanka Bureau of Foreign Employment Act (court's keywords; not yet read).",
     "Permohonan writ mandamus terkait izin agen penempatan kerja luar negeri berdasarkan Undang-Undang Biro Ketenagakerjaan Luar Negeri Sri Lanka (kata kunci pengadilan; belum dibaca).",
     "https://courtofappeal.lk/uploads/judgments/WRT-821-23-JUDGMENT-1.pdf"),
    ("lk-ca-ayisha-beebi-2024", "Karungu Aboobucker Ayisha Beebi v. Officer in Charge, Crimes Investigation Division", "2024-03-21", "CPA/0097/2023",
     "criminal", ["recruitment"], ["fees"], [1], "origin",
     "Revision in foreign-job transaction offences: cheating, criminal breach of trust and misappropriation, with the Bureau of Foreign Employment Act (court's keywords; not yet read).",
     "Revisi dalam perkara tindak pidana transaksi kerja luar negeri: penipuan, penggelapan, dan penyalahgunaan, terkait Undang-Undang Biro Ketenagakerjaan Luar Negeri (kata kunci pengadilan; belum dibaca).",
     "https://courtofappeal.lk/uploads/judgments/CA-CPA-0097-23-1.pdf"),
]

inc = ROOT / "data/court-decisions/incoming/other-asia/court-decisions-2026-11-21.csv"
hdr = next(csv.reader(open(inc, encoding="utf-8")))
out_rows, new = [], []
for (i, name, date, cite, branch, iss, sits, st, forum, en, idn, u) in ROWS:
    r = dict.fromkeys(hdr, "")
    r.update(id="oa-" + i, name=name, court=COURT, tier="national", forum=forum, level="appeal", country="LK", region="asia",
             date=date, citation=cite, branch=branch, issues=";".join(iss), situations=";".join(sits), stages=";".join(map(str, st)),
             status="C", plain_en=en, plain_id=idn, sources=u, official_link=u, source_tier="official (Court of Appeal of Sri Lanka website)",
             site_status="new", note=NOTE)
    out_rows.append(r)
    new.append(dict(id="c-l-" + i, name=name, court=COURT, cc="LK", region="asia", forum=forum, level="appeal", date=date, cite=cite,
                    tier="national", branch=branch, sector="", issues=iss, situations=sits, stages=st, outcome="unknown", follow="unknown",
                    status="C", q="", q_id="", held="", harvest=True, tools=[], args=[], after=[], plain=en, plain_id=idn,
                    src=[{"t": "Court of Appeal of Sri Lanka (courtofappeal.lk)", "u": u}]))

p = ROOT / "data/court-decisions/incoming/other-asia/court-decisions-2026-11-21-lk.csv"
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, hdr, lineterminator="\n"); w.writeheader(); w.writerows(out_rows)
json.dump({"new": new, "links": {}, "cites": {}}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(new), "Sri Lanka entries")
