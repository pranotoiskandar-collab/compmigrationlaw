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
ccs = sorted(by, key=lambda cc: -len(by[cc]))
DATA = {"dims": {"sit": SIT, "stage": STAGE, "branch": BRANCH}, "countries": [[cc, list(CN.get(cc, (cc, cc)))] for cc in ccs],
        "d": [[d["id"], d["name"], d["cc"], d["date"][:4], d.get("situations", []), d.get("stages", []), d.get("branch", ""), d["status"]] for d in home]}
JS = (Path(__file__).parent / "oc_courts_js.txt").read_text(encoding="utf-8").replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
(SITE / "countries-of-origin/oc-courts.js").write_text(JS, encoding="utf-8")

lead_en = (f"Courts in countries of origin also make migration law. They try illegal recruitment and trafficking, hear workers' claims against recruitment agencies, and review exit bans and passport rules. "
           f"The Court Decisions database holds {total} decisions by national courts of the countries on this page. {unchecked} of them were found by searching the courts' own sites and have not yet been read, so they are marked Unverified and their summaries give the subject only.")
lead_id = (f"Pengadilan di negara asal juga membentuk hukum migrasi. Pengadilan tersebut mengadili perekrutan ilegal dan perdagangan orang, memeriksa gugatan pekerja terhadap agen perekrutan, dan menguji larangan keluar serta aturan paspor. "
           f"Basis data Putusan Pengadilan memuat {total} putusan pengadilan nasional dari negara-negara di halaman ini. Sebanyak {unchecked} di antaranya kami temukan melalui penelusuran di situs pengadilan itu sendiri dan belum dibaca, sehingga ditandai Belum diverifikasi dan ringkasannya hanya memuat pokok perkara.")
CMP_EN = "Pick a theme to set the countries side by side: the table counts the decisions on each theme from each country's courts, and choosing a row lists them next to each other. Group the themes by the worker's situation, by the stage of the migration journey, or by the type of case."
CMP_ID = "Pilih satu tema untuk menyandingkan negara-negara: tabel menghitung putusan tentang tiap tema dari pengadilan tiap negara, dan memilih satu baris menampilkan daftarnya secara berdampingan. Tema dapat dikelompokkan menurut situasi pekerja, tahap perjalanan migrasi, atau jenis perkara."
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
