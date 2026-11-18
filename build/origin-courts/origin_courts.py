"""Add section XII "Courts at home" to the Countries of Origin page (idempotent; rerun after cd-data.js changes).

Usage: python3 build/origin-courts/origin_courts.py SITE
Counts the Court Decisions entries decided by national courts of the origin states on the page and writes
one card per country, linking to that country's list in /court-decisions/all/. Indonesian strings go into
oc-i18n.js. Added 18 November 2026 (oto) so that Nepal's Supreme Court cases show as origin-state
jurisprudence without a South Asia page.
"""
import html, json, re, sys
from collections import Counter
from pathlib import Path

SITE = Path(sys.argv[1]); E = html.escape
ORIGINS = ["ID", "PH", "VN", "NP", "BD", "IN", "LK", "PK", "MM", "KH", "LA", "TL"]
B0, B1 = "<!-- origin-courts:start -->", "<!-- origin-courts:end -->"
I0, I1 = "/* origin-courts:start */", "/* origin-courts:end */"

D = json.loads((SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8").split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]
J = (SITE / "court-decisions/cd.js").read_text(encoding="utf-8")
CN = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\b([A-Z]{2}): \["([^"]+)", "([^"]+)"\]', J)}
home = [d for d in D if d["tier"] == "national" and d["forum"] == "origin" and d["cc"] in ORIGINS]
by = {cc: [d for d in home if d["cc"] == cc] for cc in ORIGINS}
by = {cc: v for cc, v in by.items() if v}
total = len(home); unchecked = sum(d["status"] == "C" for d in home)

NOTES = {
    "NP": ("Supreme Court decisions from Nepal Kanoon Patrika (nkp.gov.np), the Court's official law reports: foreign employment, trafficking, refugees, citizenship and immigration. Names are English labels made from the Nepali subject line, and years are converted from the Bikram Sambat calendar, so they can be off by one.",
           "Putusan Mahkamah Agung dari Nepal Kanoon Patrika (nkp.gov.np), laporan hukum resmi Mahkamah tersebut: kerja di luar negeri, perdagangan orang, pengungsi, kewarganegaraan dan imigrasi. Judul merupakan label bahasa Inggris yang kami susun dari pokok perkara dalam bahasa Nepal, dan tahun dikonversi dari kalender Bikram Sambat, sehingga bisa selisih satu tahun."),
    "PH": ("Supreme Court decisions, mostly from its E-Library (elibrary.judiciary.gov.ph): illegal recruitment, claims by overseas workers and seafarers against recruitment agencies, and trafficking.",
           "Putusan Mahkamah Agung, sebagian besar dari E-Library-nya (elibrary.judiciary.gov.ph): perekrutan ilegal, gugatan pekerja luar negeri dan pelaut terhadap agen perekrutan, serta perdagangan orang."),
}
# theme-by-country comparison (oto, 18 November 2026: "each country can be connected ... based on thematic question")
SIT = [[m.group(1), [m.group(2), m.group(3)]] for m in re.finditer(r'\["([a-z]+)", "([^"]+)", "([^"]+)"\]', J[J.index("var SIT = ["):J.index("var STAGE = [")])]
STAGE = [[int(m.group(1)), [m.group(2), m.group(3)]] for m in re.finditer(r'\[(\d), "([^"]+)", "([^"]+)"', J[J.index("var STAGE = ["):])][:5]
BRANCH = [["criminal", ["Criminal", "Pidana"]], ["private", ["Private dispute (labor, contract, tort)", "Sengketa perdata (kerja, kontrak, perbuatan melawan hukum)"]],
          ["administrative", ["Administrative (challenge to a government decision)", "Tata usaha negara (gugatan atas keputusan pemerintah)"]],
          ["constitutional", ["Constitutional and human rights", "Konstitusi dan hak asasi manusia"]]]
# Importance order of the situations (oto, 18 November 2026: themes "organized by the popularity or importance",
# based on a survey online). Ranked from official complaint figures of origin states and ILO studies,
# read through web search on 18 November 2026; the government sites themselves were not reachable from the
# cloud, so the figures are marked as being checked.
RANK = ["fees", "wages", "dismissed", "forced", "injury", "passport", "arrest", "coverage"]
WHY = {"lead": ["Ordered by how often each problem comes up in the complaints that origin-state agencies receive and in ILO studies of migrant workers in Asia, not by the number of court decisions. The figures were read online on 18 November 2026 and are being checked against the agencies' own tables.",
                "Diurutkan menurut seberapa sering tiap masalah muncul dalam pengaduan yang diterima lembaga di negara asal dan dalam kajian ILO tentang pekerja migran di Asia, bukan menurut jumlah putusan pengadilan. Angka-angka tersebut kami baca secara daring pada 18 November 2026 dan sedang dicocokkan dengan tabel resmi lembaga yang bersangkutan."],
       "items": [
    {"t": ["Indonesia, 2024: 1,500 complaints to BP2MI/KP2MI. The largest categories were requests to be brought home (316), failure to depart after recruitment (170), unpaid wages (129), social security (85) and deportation (61).",
           "Indonesia, 2024: 1.500 pengaduan kepada BP2MI/KP2MI. Kategori terbesar ialah PMI ingin dipulangkan (316), gagal berangkat setelah direkrut (170), gaji tidak dibayar (129), jaminan sosial (85) dan deportasi (61)."],
     "s": "KP2MI, Laporan Tahunan Publikasi Data PMI 2024", "u": "https://kp2mi.go.id/uploads/statistik/images/data_06-02-2025_Laporan_Tahunan__Publikasi_Data_PMI_2024.pdf"},
    {"t": ["Nepal: among grievances registered at Migrant Resource Centres, cheating by recruiters comes first, followed by deaths of workers and money withheld in Nepal.",
           "Nepal: di antara keluhan yang tercatat di Migrant Resource Centre, penipuan oleh perekrut berada di urutan pertama, disusul kematian pekerja dan uang yang ditahan di Nepal."],
     "s": "Ministry of Labour, Employment and Social Security, Nepal Labour Migration Report 2024", "u": "https://moless.gov.np/content/13312/nepal-labor-migration-report--2024/"},
    {"t": ["Philippines, 2023: the Department of Migrant Workers filed 4,521 administrative charges and revoked the licences of 14 recruitment agencies for prohibited practices.",
           "Filipina, 2023: Department of Migrant Workers mengajukan 4.521 dakwaan administratif dan mencabut izin 14 agen perekrutan karena praktik terlarang."],
     "s": "ILO Committee on the Application of Standards, Philippines (C29), 2025", "u": "https://ilo.org/sites/default/files/2025-05/ILC113-CAN-D-Philippines-C29-[NORMES-250520-017]-EN.pdf"},
    {"t": ["ILO: excessive recruitment fees, deception about the contract, fake documents and confiscation of passports are the most common recruitment abuses for migrants in low-wage jobs; wage claims are the abuse workers most often take further.",
           "ILO: biaya rekrutmen berlebihan, penipuan isi kontrak, dokumen palsu dan penahanan paspor merupakan pelanggaran rekrutmen yang paling umum bagi pekerja migran berupah rendah; tuntutan upah merupakan pelanggaran yang paling sering dibawa pekerja ke jalur hukum."],
     "s": "ILO, Access to justice for migrant workers in South-East Asia", "u": "https://www.ilo.org/media/423796/download"},
]}
ccs = sorted(by, key=lambda cc: -len(by[cc]))
# Do complaints reach the courts? Importance rank (complaints) against the rank by number of origin-court
# decisions; BP2MI/KP2MI 2024 complaint counts where a category matches a situation (being checked).
BP2MI = {"fees": [170, "failed to depart after recruitment", "gagal berangkat setelah direkrut"],
         "wages": [129, "unpaid wages", "gaji tidak dibayar"],
         "dismissed": [316, "asked to be brought home", "ingin dipulangkan"],
         "arrest": [61, "deportation", "deportasi"]}
cnt = {k: sum(k in d.get("situations", []) for d in home) for k in RANK}
drank = {k: i + 1 for i, k in enumerate(sorted(RANK, key=lambda k: (-cnt[k], RANK.index(k))))}
n = len(RANK); rho = 1 - 6 * sum((RANK.index(k) + 1 - drank[k]) ** 2 for k in RANK) / (n * (n * n - 1))
GAP = {"total": len(home), "bp_total": 1500, "rho": round(rho, 2),
       "rows": [[k, i + 1, drank[k], cnt[k], BP2MI.get(k)] for i, k in enumerate(RANK)]}
# Law on the books and in court (oto, 18 November 2026): which statute each origin-court decision names,
# from the full-text search terms that found it (PR 5 search results), set beside the Countries of Origin codings.
import csv as _csv
ALL = list(_csv.DictReader(open(Path(__file__).resolve().parents[2] / "data/court-decisions/incoming/other-asia/migration-cases-all-2026-11-17.csv", encoding="utf-8")))
STAT = [
    {"k": "ra8042", "cc": "PH", "en": "Migrant Workers and Overseas Filipinos Act (RA 8042, amended by RA 10022)", "id": "Undang-Undang Pekerja Migran dan Warga Filipina di Luar Negeri (RA 8042, diubah dengan RA 10022)",
     "year": 1995, "re": r"Migrant Workers and Overseas Filipinos Act|Republic Act No\. 8042|Republic Act No\. 10022", "feat": ["rec", "fees", "redress"], "src": "codings"},
    {"k": "ra9208", "cc": "PH", "en": "Anti-Trafficking in Persons Act (RA 9208, amended)", "id": "Undang-Undang Anti-Perdagangan Orang (RA 9208, sebagaimana diubah)",
     "year": 2003, "re": r"Anti-Trafficking|Republic Act No\. 9208", "feat": ["traffic"], "src": "protection"},
    {"k": "fea", "cc": "NP", "en": "Foreign Employment Act 2064 (2007)", "id": "Undang-Undang Kerja Luar Negeri 2064 (2007)",
     "year": 2007, "re": r"वैदेशिक रोजगार", "feat": ["rec", "fees", "redress"], "src": "codings"},
    {"k": "htta", "cc": "NP", "en": "Human Trafficking and Transportation (Control) Act 2064 (2007)", "id": "Undang-Undang Pengendalian Perdagangan dan Pengangkutan Orang 2064 (2007)",
     "year": 2007, "re": r"मानव बेचबिखन", "feat": ["traffic"], "src": "protection"},
]
DROOT = Path(__file__).resolve().parents[2] / "data/countries-of-origin"
CODES = {}
for f in ["codings.csv", "protection.csv"]:
    for r in _csv.DictReader(open(DROOT / f, encoding="utf-8")):
        CODES[(r["country"], r["feature"])] = [r["value"], r["feature_name"]]
FEAT_ID = {"rec": "Perizinan dan tanggung jawab perekrut", "fees": "Biaya rekrutmen yang dibebankan kepada pekerja",
           "redress": "Pemulihan di negara asal", "traffic": "Hukum anti-perdagangan orang yang mencakup kerja"}
url2stat = {}
for st in STAT:
    hits = [x for x in ALL if x["jurisdiction"] == st["cc"] and re.search(st["re"], x["matched_terms"])]
    st["hits"] = len(hits)
    per = Counter(int(x["date"][:4]) // 5 * 5 for x in hits if x["date"][:4].isdigit())
    st["per"] = sorted(per.items())
    st["before"] = sum(v for k, v in per.items() if k + 4 < st["year"])
    for x in hits:
        if x["url"]:
            url2stat.setdefault(x["url"].rstrip("/"), []).append(st["k"])
    st["codes"] = [[f, CODES.get((st["cc"], f), ["", f])[0], CODES.get((st["cc"], f), ["", f])[1], FEAT_ID.get(f, f)] for f in st["feat"]]
    del st["re"]
dstat = {d["id"]: sorted(set(sum((url2stat.get(s["u"].rstrip("/"), []) for s in d["src"]), []))) for d in home}
for st in STAT:
    st["site"] = sum(st["k"] in v for v in dstat.values())
LAW = {"stat": STAT, "dec": {k: v for k, v in dstat.items() if v}}
DATA = {"law": LAW, "gap": GAP, "rank": RANK, "why": WHY, "dims": {"sit": SIT, "stage": STAGE, "branch": BRANCH}, "countries": [[cc, list(CN.get(cc, (cc, cc)))] for cc in ccs],
        "d": [[d["id"], d["name"], d["cc"], d["date"][:4], d.get("situations", []), d.get("stages", []), d.get("branch", ""), d["status"]] for d in home]}
JS = (Path(__file__).parent / "oc_courts_js.txt").read_text(encoding="utf-8").replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
(SITE / "countries-of-origin/oc-courts.js").write_text(JS, encoding="utf-8")

lead_en = (f"Courts in countries of origin also make migration law. They try illegal recruitment and trafficking, hear workers' claims against recruitment agencies, and review exit bans and passport rules. "
           f"The Court Decisions database holds {total} decisions by national courts of the countries on this page. {unchecked} of them were found by searching the courts' own sites and have not yet been read, so they are marked Unverified and their summaries give the subject only.")
lead_id = (f"Pengadilan di negara asal juga membentuk hukum migrasi. Pengadilan tersebut mengadili perekrutan ilegal dan perdagangan orang, memeriksa gugatan pekerja terhadap agen perekrutan, dan menguji larangan keluar serta aturan paspor. "
           f"Basis data Putusan Pengadilan memuat {total} putusan pengadilan nasional dari negara-negara di halaman ini. Sebanyak {unchecked} di antaranya kami temukan melalui penelusuran di situs pengadilan itu sendiri dan belum dibaca, sehingga ditandai Belum diverifikasi dan ringkasannya hanya memuat pokok perkara.")
CMP_EN = "Pick a theme to set the countries side by side: the table counts the decisions on each theme from each country's courts, and choosing a row lists them next to each other. Group the themes by the worker's situation, by the stage of the migration journey, or by the type of case. Situations are listed by importance, from the complaints that origin-state agencies receive and from ILO studies, and can be re-sorted by number of decisions; the stages follow the order of the journey."
CMP_ID = "Pilih satu tema untuk menyandingkan negara-negara: tabel menghitung putusan tentang tiap tema dari pengadilan tiap negara, dan memilih satu baris menampilkan daftarnya secara berdampingan. Tema dapat dikelompokkan menurut situasi pekerja, tahap perjalanan migrasi, atau jenis perkara. Situasi diurutkan menurut tingkat kepentingannya, berdasarkan pengaduan yang diterima lembaga di negara asal dan kajian ILO, dan dapat diurutkan ulang menurut jumlah putusan; tahap perjalanan mengikuti urutan perjalanan."
I18N = {lead_en: lead_id, "XII · COURTS AT HOME": "XII · PENGADILAN DI NEGARA ASAL", "Courts at home": "Pengadilan di negara asal",
        "Court decisions from countries of origin": "Putusan pengadilan dari negara asal", "List of decisions →": "Daftar putusan →",
        "Compare countries by theme": "Bandingkan negara menurut tema",
        CMP_EN: CMP_ID, "By country": "Menurut negara",
        "See courts at home and courts abroad side by side, along the migration journey →": "Lihat pengadilan di negara asal dan di negara tujuan secara berdampingan, di sepanjang perjalanan migrasi →"}
cards = []
for cc, ds in sorted(by.items(), key=lambda kv: -len(kv[1])):
    en, idn = CN.get(cc, (cc, cc)); n = len(ds); c = sum(d["status"] == "C" for d in ds)
    cnt_en = f"{n} decision{'s' if n != 1 else ''}" + (f", {c} unchecked" if c else "") + "."
    cnt_id = f"{n} putusan" + (f", {c} belum diperiksa" if c else "") + "."
    I18N[cnt_en] = cnt_id; I18N[en] = idn
    note = NOTES.get(cc)
    if note:
        I18N[note[0]] = note[1]
    anchor = "c-" + en.lower().replace(" ", "-")
    cards.append(f'<div class="g-card"><h3>{E(en)}</h3><p>{E(cnt_en)}</p>' + (f'<p class="g-note">{E(note[0])}</p>' if note else "") +
                 f'<p><a href="/court-decisions/all/#{anchor}">List of decisions →</a></p></div>')
sec = (f'{B0}\n<section class="g-sec" id="courts">\n<p class="g-eye">XII · COURTS AT HOME</p>\n<h2>Court decisions from countries of origin</h2>\n'
       f'<p class="g-lead">{E(lead_en)}</p>\n<h3>Compare countries by theme</h3>\n<p>{E(CMP_EN)}</p>\n<div id="oc-courts" data-noi18n></div>\n<h3 style="margin-top:32px">By country</h3>\n<div class="g-grid2">\n' + "\n".join(cards) + '\n</div>\n'
       '<p><a href="/court-decisions/#journey">See courts at home and courts abroad side by side, along the migration journey →</a></p>\n</section>\n' + B1 + "\n\n")

p = SITE / "countries-of-origin/index.html"; H = p.read_text(encoding="utf-8")
if B0 in H:
    H = H[:H.index(B0)] + sec.rstrip("\n") + H[H.index(B1) + len(B1):]
else:
    for a, b in [("XIV · SOURCES AND DOWNLOADS", "XV · SOURCES AND DOWNLOADS"), ("XIII · FROM RESEARCH TO PRACTICE", "XIV · FROM RESEARCH TO PRACTICE"),
                 ("XII · METHOD AND CITATION", "XIII · METHOD AND CITATION")]:
        H = H.replace(f'<p class="g-eye">{a}</p>', f'<p class="g-eye">{b}</p>', 1)
    k = H.index('<section class="g-sec" id="methods">'); H = H[:k] + sec + H[k:]
    H = H.replace('<li><a href="#methods">Method and citation</a></li>', '<li><a href="#courts">Courts at home</a></li>\n<li><a href="#methods">Method and citation</a></li>', 1)
if 'src="oc-courts.js"' not in H:
    H = H.replace('<script src="oc-i18n.js" defer></script>', '<script src="oc-courts.js" defer></script>\n<script src="oc-i18n.js" defer></script>', 1)
p.write_text(H, encoding="utf-8")

q = SITE / "countries-of-origin/oc-i18n.js"; T = q.read_text(encoding="utf-8")
block = I0 + "\n" + "".join(f"{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in I18N.items()) + I1 + "\n"
# the section shifts the later eyebrows by one; do it once
if '"XIII · METHOD AND CITATION"' not in T:
    for a, b in [("XIV · SOURCES AND DOWNLOADS", "XV · SUMBER DAN UNDUHAN"), ("XIII · FROM RESEARCH TO PRACTICE", "XIV · DARI RISET KE PRAKTIK"),
                 ("XII · METHOD AND CITATION", "XIII · METODE DAN SITASI")]:
        T = re.sub(rf'"{a}": "[^"]*",', lambda m: f'"{a.replace(a.split(" ")[0], b.split(" ")[0], 1)}": "{b}",', T, count=1)
if I0 in T:
    T = T[:T.index(I0)] + block + T[T.index(I1) + len(I1) + 1:]
else:
    T = T.replace("  var A = {\n", "  var A = {\n" + block, 1)
q.write_text(T, encoding="utf-8")
print("origin courts:", total, "decisions,", unchecked, "unchecked;", {cc: len(v) for cc, v in by.items()})
