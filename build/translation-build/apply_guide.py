"""Apply oto's Indonesian translation guide (doc "Terjemahan situs IMR: beranda (draf)",
https://claude.ai/artifact/GFGq8WG3Rcm4zVppXAWMkF) to theimr.org.

Usage: python3 apply_guide.py SITE_DIR [more files or dirs ...]
Idempotent. Run it LAST, after restructure.py / other builds (they still emit older wording),
then ai_use.py and analytics.py as usual.

Fixed terms that override the guide draft (oto, 2026-10-31): hate speech = "ucapan kebencian"
(never "ujaran"), impunity = "kekebalan", nativist = "pro-pribumi", "suara" only = vote.
"""
import json, os, re, sys

# 1. Exact homepage / menu strings from the guide, keyed by the English text in assets/lang.js.
OVERRIDES = {
 "Prepare a rights communication": "Siapkan pengaduan hak",
 "Submit a rights communication": "Kirim pengaduan hak",
 "Gulf States": "Negara-Negara Teluk",
 "Elections and non-citizens": "Pemilu dan orang yang bukan warga negara",
 "Report official hate speech": "Laporkan ucapan kebencian oleh pejabat",
 "Farmworker law view": "Tampilan hukum buruh tani",
 "Origin states": "Negara asal",
 "People": "Tim",
 "Contact": "Hubungi Kami",
 "Contact · Institute for Migrant Rights": "Hubungi Kami · Institute for Migrant Rights",
 "Write to us": "Hubungi Kami",  # contact page heading (oto 2026-11-15: the contact page is "Hubungi Kami")
 "An initiative trying to be of some use to people who cross borders to work.":
   "Sebuah prakarsa yang berusaha sedikit berguna bagi mereka yang melintasi batas negara untuk bekerja.",
 "Were your rights violated? Prepare a rights communication to a UN or regional human rights body.":
   "Hak Anda dilanggar? Siapkan pengaduan hak (rights communication) ke badan hak asasi manusia PBB atau badan HAM kawasan.",
 "Answer a few short questions. We tell you which bodies can hear your case, write a draft communication in the UN Human Rights Committee format, and an IMR lawyer reviews it with you.":
   "Jawab beberapa pertanyaan singkat. Kami beri tahu badan mana saja yang bisa memeriksa kasus Anda dan kami buatkan draf pengaduan dalam format Komite HAM PBB. Setelah itu, seorang pengacara IMR memeriksanya bersama Anda.",
 "Start your communication →": "Mulai pengaduan Anda →",
 "Another path to protection for people who cross borders to work":
   "Jalan lain menuju perlindungan bagi mereka yang melintasi batas negara untuk bekerja",
 "The Institute for Migrant Rights is an academy-based initiative in Cianjur, West Java. It starts from a plain observation: advocacy for migrant workers in Indonesia has brought very limited protection in practice, and international human rights law may offer another path.":
   "Institute for Migrant Rights adalah prakarsa berbasis akademi di Cianjur, Jawa Barat. Titik tolaknya sebuah pengamatan sederhana. Dalam praktiknya, advokasi bagi pekerja migran di Indonesia baru membawa perlindungan yang sangat terbatas, dan hukum hak asasi manusia internasional mungkin bisa membuka jalan lain.",
 "We do not claim to have found it. What we try to do is modest: to take the situation of migrant workers, especially women in domestic work and those who have been trafficked, to international forums; to learn from good practice under the UN Migrant Workers Convention, above all in the administration of justice; and to help human rights norms take root a little more widely in Indonesia.":
   "Kami tidak mengaku sudah menemukan jalan itu. Yang kami coba lakukan sederhana saja. Kami membawa keadaan pekerja migran ke forum-forum internasional, terutama perempuan yang bekerja di rumah tangga dan korban perdagangan orang. Kami belajar dari praktik baik di bawah Konvensi Pekerja Migran PBB, terutama dalam penyelenggaraan peradilan. Selain itu, kami ingin membantu norma hak asasi manusia berakar sedikit lebih luas di Indonesia.",
 "Comparative research, openly shared": "Riset perbandingan yang dibagikan secara terbuka",
 "Explore our projects": "Jelajahi proyek kami",
 "Global, regional and national migration law in one comparative explorer, with farmworker law as a subset.":
   "Hukum migrasi tingkat dunia, kawasan, dan nasional dalam satu alat jelajah perbandingan, dengan hukum buruh tani sebagai salah satu bagiannya.",
 "Nearly 500 court decisions on migrant workers from Asia, Africa, the Middle East and Latin America, searchable by argument.":
   "Hampir 500 putusan pengadilan tentang pekerja migran dari Asia, Afrika, Timur Tengah, dan Amerika Latin, yang bisa dicari menurut argumennya.",
 "Statistics, legal frameworks and a proposed crime for hateful speech by officials and politicians.":
   "Statistik, kerangka hukum, dan usulan tindak pidana baru untuk ucapan kebencian oleh pejabat dan politisi.",
 "Ideas from the fields": "Gagasan dari sawah dan ladang",
 "On the rights of non-citizens in Southeast Asia, and why ASEAN needs a new course to protect them.":
   "Tentang hak orang yang bukan warga negara di Asia Tenggara, dan mengapa ASEAN perlu menempuh jalan baru untuk melindungi mereka.",
 "Legal assistance and scholarship": "Bantuan hukum dan karya ilmiah",
 "Scholarly publication": "Terbitan ilmiah",
 "Non-citizens in Indonesia often have few places to turn. We offer free legal assistance so they can approach international human rights bodies, and we try, where we can, to bring international standards into the work of advocates here.":
   "Di Indonesia, orang yang bukan warga negara sering tidak tahu harus mengadu ke mana. Kami memberi bantuan hukum gratis agar mereka bisa mengadu ke badan hak asasi manusia internasional. Sebisa mungkin, kami juga membawa standar internasional ke dalam kerja para advokat di sini.",
 "Prepare a rights communication online →": "Siapkan pengaduan hak secara daring →",
 "International Law & Comparative Law series · IMR Perspectives series":
   "Seri Hukum Internasional & Hukum Perbandingan · Seri Perspektif IMR",
 "General Editor: Pranoto Iskandar · Assistant Editor: Saru Arifin":
   "Penyunting Umum: Pranoto Iskandar · Asisten Penyunting: Saru Arifin",
 "General Editor": "Penyunting Umum",
 "Assistant Editor": "Asisten Penyunting",
 "Editors": "Penyunting",
 "In the news": "IMR di media",
 "Coverage of the Institute, its people and its publications":
   "Liputan tentang Institute, orang-orangnya, dan terbitannya",
 "How we use AI": "Cara kami memakai kecerdasan buatan (AI)",
}
# Article titles stay in English (guide: they were published in English).
REMOVE = ["Relational self and farmworker law reform: the case of Indonesia"]

# 2. Site-wide wording, applied to Indonesian text in every page, data and i18n file.
#    Every pattern is Indonesian-only, so English text is never touched.
NOUN_BEFORE = r"(melindungi|bagi|menyebut|melarang|membedakan|dan|pelindungan|perlindungan|Bolehkah|bahwa|tempat)"
RULES = [
 # oto's fixed terms (guard)
 (r"\bujaran\b", "ucapan"), (r"\bUjaran\b", "Ucapan"),
 (r"\bimpunitas\b", "kekebalan"),
 # rights communication -> pengaduan hak (lay wording; technical UN terms such as
 # "komunikasi perorangan", "prosedur komunikasi", "dapat diterimanya komunikasi" stay)
 (r"\b[Ss]usun komunikasi hak asasi\b", lambda m: ("S" if m.group(0)[0]=="S" else "s")+"iapkan pengaduan hak"),
 (r"\b([Ss])iapkan komunikasi hak asasi\b", r"\1iapkan pengaduan hak"),
 (r"\bAjukan komunikasi hak asasi\b", "Kirim pengaduan hak"),
 (r"\bMenyusun komunikasi hak asasi manusia\b", "Menyiapkan pengaduan hak asasi manusia"),
 (r"\bMenyusun komunikasi hak asasi\b", "Menyiapkan pengaduan hak"),
 (r"\bkomunikasi hak asasi\b", "pengaduan hak"),
 (r"\bkomunikasi hak\b", "pengaduan hak"),
 (r"\b([Dd])raf komunikasi\b", r"\1raf pengaduan"),
 (r"\b([Ss])usun komunikasi\b", r"\1usun pengaduan"),
 (r"\bkomunikasinya\b", "pengaduannya"),
 (r"\bMulai komunikasi Anda\b", "Mulai pengaduan Anda"),
 (r"\bPengirim komunikasi\b", "Pengirim pengaduan"),
 (r"\bselama komunikasi diperiksa\b", "selama pengaduan diperiksa"),
 # farmworker -> buruh tani
 (r"\bpekerja pertanian\b", "buruh tani"), (r"\bPekerja pertanian\b", "Buruh tani"),
 (r"\bPekerja Pertanian\b", "Buruh Tani"),
 # non-citizens as a noun -> orang yang bukan warga negara
 (NOUN_BEFORE + r" bukan warga negara\b", r"\1 orang yang bukan warga negara"),
 # tiers: global/regional -> tingkat dunia/kawasan (oto 2026-11-15: kawasan)
 (r"\b([Hh]ukum(?: migrasi)?) global, regional,? dan nasional\b", r"\1 tingkat dunia, kawasan, dan nasional"),
 (r"\b([Hh]ukum(?: migrasi)?) tingkat dunia, wilayah, dan nasional\b", r"\1 tingkat dunia, kawasan, dan nasional"),
 (r"\bbadan hak asasi manusia PBB atau regional\b", "badan hak asasi manusia PBB atau badan HAM kawasan"),
 (r"\bbadan HAM tingkat wilayah\b", "badan HAM kawasan"),
 # oto 2026-11-15: regional = "kawasan" everywhere (Indonesian text only; see fix_regional)
 (r'"Regional", "Regional"\]', '"Regional", "Kawasan"]'),
 (r"\bsatu penjelajah\b", "satu alat jelajah"),
 (r"\bdi penjelajah\b", "di alat jelajah"),
 # everyday register (guide): dapat -> bisa, except the legal term of admissibility
 (r"\b(?<!tidak )dapat\b(?! diterima)", "bisa"),
 (r"\btidak dapat\b(?! diterima)", "tidak bisa"),
 (r"\bDapat\b(?! diterima)", "Bisa"),
 (r"\bmenggunakannya\b", "memakainya"), (r"\bmenggunakan\b", "memakai"),
 (r"\bMenggunakan\b", "Memakai"), (r"\bdigunakan\b", "dipakai"), (r"\bDigunakan\b", "Dipakai"),
 (r"\btidak mengklaim telah\b", "tidak mengaku sudah"),
 (r"\bEditor Umum\b", "Penyunting Umum"), (r"\bAsisten Editor\b", "Asisten Penyunting"),
]
RX = [(re.compile(p), r) for p, r in RULES]
EXT = (".js", ".html", ".py")
SKIP_DIRS = {"leaflet"}

ID_WORDS = set("""dan yang di ke dari untuk badan tingkat hukum pengadilan norma perjanjian mekanisme sistem
organisasi instrumen internasional nasional atau serta dengan lembaga komisi mahkamah proses perikanan traktat
antarkawasan PBB HAM mengikat lunak empat Tingkat Sistem Norma Hukum Putusan Di bagi ini itu antara Kebijakan kebijakan tentang kerja sama Badan Pengadilan Mekanisme Organisasi Instrumen Perjanjian""".split())
RX_REG = re.compile(r"\b([Rr])egional\b")
WORD_BEFORE = re.compile(r"([A-Za-z]+)[^A-Za-z\n\"']{1,3}$")
WORD_AFTER = re.compile(r"^[^A-Za-z\n\"']{1,3}([A-Za-z]+)")
def fix_regional(s, force=False):
    def rep(m):
        if not force:
            b = WORD_BEFORE.search(s[max(0, m.start()-30):m.start()])
            a = WORD_AFTER.search(s[m.end():m.end()+30])
            if not ((b and b.group(1) in ID_WORDS) or (a and a.group(1) in ID_WORDS)): return m.group(0)
        return "Kawasan" if m.group(1) == "R" else "kawasan"
    return RX_REG.sub(rep, s)

def fix(s, force_regional=False):
    for rx, r in RX: s = rx.sub(r, s)
    return fix_regional(s, force_regional)

def patch_lang(path):
    src = open(path, encoding="utf-8").read()
    first, rest = src.split("\n", 1)
    pre = "window.SITE_I18N="
    assert first.startswith(pre)
    data = json.loads(first[len(pre):].rstrip(";"))
    d = data["id"]
    for k in REMOVE: d.pop(k, None)
    for k, v in d.items():
        if k != "__pat": d[k] = fix(v, True)
    d["__pat"] = [[a, fix(b, True)] for a, b in d["__pat"]]
    d.update(OVERRIDES)
    out = pre + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + (";" if first.endswith(";") else "") + "\n" + rest
    if out != src: open(path, "w", encoding="utf-8").write(out); return True
    return False

def patch_file(path):
    if os.path.basename(path) == "apply_guide.py": return False
    if path.endswith(os.path.join("assets", "lang.js")): return patch_lang(path)
    src = open(path, encoding="utf-8").read()
    out = fix(src)
    if out != src: open(path, "w", encoding="utf-8").write(out); return True
    return False

def walk(p):
    if os.path.isfile(p): yield p; return
    for root, dirs, files in os.walk(p):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and x != "__pycache__"]
        for f in files:
            if f.endswith(EXT): yield os.path.join(root, f)

if __name__ == "__main__":
    n = 0
    for arg in sys.argv[1:]:
        for f in walk(arg):
            if patch_file(f): n += 1; print("patched", f)
    print(n, "files changed")
