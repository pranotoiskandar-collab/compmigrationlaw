# Indonesian for the model F homepage, the shared masthead and the Clinic journey (2026-11-16). Idempotent.
# Usage: python3 i18n.py SITE
# Site pages: /assets/lang.js (window.SITE_I18N.id + __pat). Clinic page: /legal-clinic/i18n.js (window.CLINIC_I18N.id).
# Follows oto's translation guide: everyday register (bisa, memakai), pengaduan hak, Negara asal, kawasan.
import sys, os, json
SITE = sys.argv[1]
J = lambda x: json.dumps(x, ensure_ascii=False)

HOME = {
 "Institute for Migrant Rights · Cianjur, West Java": "Institute for Migrant Rights · Cianjur, Jawa Barat",
 "Migration law, collected, coded and explained.": "Hukum migrasi, dihimpun, dikodekan, dan dijelaskan.",
 "An initiative trying to be of some use to people who cross borders to work: free legal help for workers and families, open data for researchers.": "Sebuah prakarsa yang berusaha sedikit berguna bagi mereka yang melintasi batas negara untuk bekerja: bantuan hukum gratis bagi pekerja dan keluarganya, data terbuka bagi peneliti.",
 "Get legal help →": "Cari bantuan hukum →",
 "Explore the data →": "Jelajahi data →",
 "Source: IMR Court Decisions database.": "Sumber: basis data Putusan Pengadilan IMR.",
 "Explore the decisions →": "Jelajahi putusan →",
 "Where are you on the journey?": "Di mana Anda dalam perjalanan?",
 "Pick a step: the law, the decisions, the help": "Pilih satu tahap: hukumnya, putusannya, bantuannya",
 "Recruitment at home": "Perekrutan di dalam negeri",
 "Fees, agencies, false promises": "Biaya, agen, janji palsu",
 "Leaving the country": "Berangkat ke luar negeri",
 "Exit rules, visas, documents": "Aturan keberangkatan, visa, dokumen",
 "Working abroad": "Bekerja di luar negeri",
 "Wages, hours, passport, abuse, unions": "Upah, jam kerja, paspor, kekerasan, serikat",
 "Changing or losing the job": "Pindah atau kehilangan pekerjaan",
 "Changing employer, dismissal": "Pindah majikan, pemecatan",
 "Return and after": "Pulang dan sesudahnya",
 "Claims from home, residence": "Tuntutan dari rumah, izin tinggal",
 "Find free legal help →": "Cari bantuan hukum gratis →",
 "What works where →": "Apa yang berhasil, dan di mana →",
 "Prepare a rights communication →": "Siapkan pengaduan hak →",
 "Questions people ask us": "Pertanyaan yang sering diajukan kepada kami",
 "Short answers from the databases": "Jawaban singkat dari basis data",
 "Can my employer keep my passport?": "Bolehkah majikan menahan paspor saya?",
 "court decisions deal with a passport kept by the employer. See what the courts said.": "putusan pengadilan membahas paspor yang ditahan majikan. Lihat apa kata pengadilan.",
 "Read the decisions →": "Baca putusannya →",
 "Do I have rights if my papers are not in order?": "Apakah saya punya hak jika dokumen saya tidak lengkap?",
 "decisions accepted that labor rights apply whatever a worker’s immigration status.": "putusan menerima bahwa hak pekerja berlaku apa pun status imigrasinya.",
 "Arguments that work →": "Argumen yang berhasil →",
 "Can I take my case to the UN?": "Bisakah saya membawa kasus saya ke PBB?",
 "Free": "Gratis",
 "The Clinic drafts a rights communication with you, and an IMR lawyer reviews it.": "Klinik menyusun pengaduan hak bersama Anda, lalu pengacara IMR memeriksanya.",
 "Prepare a communication →": "Siapkan pengaduan →",
 "Answer a few short questions. An IMR lawyer reviews the draft with you.": "Jawab beberapa pertanyaan singkat. Pengacara IMR memeriksa drafnya bersama Anda.",
 "Charts from the databases": "Grafik dari basis data",
 "All data and downloads": "Semua data dan unduhan",
 "Migrant-worker cases in the database, by year": "Kasus pekerja migran dalam basis data, per tahun",
 "Coded court decisions per year, 1996–2025; recent years are still being added": "Putusan pengadilan yang dikodekan per tahun, 1996–2025; tahun-tahun terakhir masih terus ditambah",
 "Ratifications of migrant-worker treaties": "Ratifikasi perjanjian tentang pekerja migran",
 "Cumulative ratifications, 1950–2025": "Ratifikasi kumulatif, 1950–2025",
 "Source: NORMLEX, UN Treaty Collection, via the Migration Law Atlas": "Sumber: NORMLEX, UN Treaty Collection, melalui Atlas Hukum Migrasi",
 "Cited by the U.S. Court of Appeals, 9th Cir.": "Dikutip oleh U.S. Court of Appeals, 9th Cir.",
 "Global, regional and national migration law in one comparative explorer.": "Hukum migrasi tingkat dunia, kawasan, dan nasional dalam satu alat jelajah perbandingan.",
 "Statistics and legal frameworks for hateful speech by officials.": "Statistik dan kerangka hukum untuk ucapan kebencian oleh pejabat.",
 "Comparative notes on labor and migration law.": "Catatan perbandingan tentang hukum ketenagakerjaan dan migrasi.",
 "Japan, Korea, Taiwan, Hong Kong and more.": "Jepang, Korea, Taiwan, Hong Kong, dan lainnya.",
 "What sending states promise their workers abroad.": "Apa yang dijanjikan negara asal kepada pekerjanya di luar negeri.",
 "Instruments that cover work in private homes.": "Instrumen yang mengatur kerja di rumah tangga.",
 "Destination and origin states in ASEAN.": "Negara tujuan dan negara asal di ASEAN.",
 "Arguments that courts accepted, by jurisdiction.": "Argumen yang diterima pengadilan, menurut yurisdiksi.",
 "IMR Press · Journal": "IMR Press · Jurnal",
 "Peer-reviewed, since 2014 ·": "Ditelaah sejawat, sejak 2014 ·",
 "2024 · Ideas from the fields": "2024 · Gagasan dari sawah dan ladang",
 "2018 · Ideas from the fields": "2018 · Gagasan dari sawah dan ladang",
}
SIT = {"recruitment and the agency": "perekrutan dan agen", "wages not paid": "upah tidak dibayar", "arrested, detained or expelled": "ditangkap, ditahan atau diusir",
       "residence and staying on": "izin tinggal dan menetap", "treated worse as a foreigner": "diperlakukan lebih buruk sebagai orang asing",
       "forced labour or trafficking": "kerja paksa atau perdagangan orang", "hurt or injured at work": "terluka saat bekerja", "dismissed or sent home": "dipecat atau dipulangkan"}
for a in SIT:
    for b in SIT:
        if a != b: HOME["Most often: %s, %s" % (a, b)] = "Paling sering: %s, %s" % (SIT[a], SIT[b])
PAT = [
 ["^(\\d+) court decisions on migrant workers\\. Each square is one\\.$", "$1 putusan pengadilan tentang pekerja migran. Satu kotak untuk satu putusan."],
 ["^(\\d+) court decisions$", "$1 putusan pengadilan"],
 ["^Worker side won \\((\\d+)\\)$", "Pihak pekerja menang ($1)"],
 ["^Worker side lost \\((\\d+)\\)$", "Pihak pekerja kalah ($1)"],
 ["^Advisory \\((\\d+)\\)$", "Nasihat ($1)"],
 ["^To be checked \\((\\d+)\\)$", "Perlu diperiksa ($1)"],
 ["^Source: Migration Jurisprudence from the South, Court Decisions database \\(IMR\\)\\. Peak year: (\\d+) \\((\\d+) decisions\\)\\.$", "Sumber: Yurisprudensi Migrasi dari Selatan, basis data Putusan Pengadilan (IMR). Tahun tertinggi: $1 ($2 putusan)."],
 ["^(\\d+) decisions, searchable by situation, argument and journey\\.$", "$1 putusan, bisa dicari menurut keadaan, argumen, dan tahap perjalanan."],
]

CLINIC = {
 "Migration Jurisprudence from the South": "Yurisprudensi Migrasi dari Selatan",
 "Where are you now?": "Anda sekarang di tahap mana?",
 "Tap the step that fits you. You will see what to do and where to get help.": "Ketuk tahap yang sesuai dengan Anda. Anda akan melihat apa yang bisa dilakukan dan ke mana mencari bantuan.",
 "Before you leave": "Sebelum berangkat",
 "An agent, fees or a promise of a job": "Agen, biaya, atau janji pekerjaan",
 "Leaving the country": "Berangkat ke luar negeri",
 "Papers, visa, exit rules": "Dokumen, visa, aturan keberangkatan",
 "Working abroad": "Bekerja di luar negeri",
 "Pay, hours, passport, abuse": "Gaji, jam kerja, paspor, kekerasan",
 "Losing or changing the job": "Kehilangan atau pindah pekerjaan",
 "Sent away, arrested, cannot change employer": "Dipulangkan, ditangkap, tidak bisa pindah majikan",
 "Back home": "Sudah pulang",
 "Claims after you return": "Tuntutan setelah pulang",
 "Keep every receipt and message from the agent. Ask for your contract in your own language before you pay anything.": "Simpan semua kuitansi dan pesan dari agen. Minta kontrak dalam bahasa Anda sendiri sebelum membayar apa pun.",
 "Keep a copy of your passport, visa and contract with your family. Note the phone number of your embassy.": "Titipkan salinan paspor, visa, dan kontrak kepada keluarga. Catat nomor telepon kedutaan negara Anda.",
 "In most countries an employer may not keep your passport. Write down unpaid wages, dates and hours. Courts have ruled for workers in cases like these.": "Di sebagian besar negara, majikan tidak boleh menahan paspor Anda. Catat upah yang belum dibayar, tanggal, dan jam kerja. Pengadilan pernah memenangkan pekerja dalam kasus seperti ini.",
 "Ask for a letter that says why the job ended. If you are detained, ask to contact your embassy.": "Minta surat yang menjelaskan mengapa pekerjaan berakhir. Jika Anda ditahan, minta untuk menghubungi kedutaan negara Anda.",
 "In many cases you can still make a claim after you come home. Keep your documents. The Clinic can help you take the case to an international body.": "Dalam banyak kasus, Anda masih bisa menuntut setelah pulang. Simpan dokumen Anda. Klinik bisa membantu membawa kasus ke badan internasional.",
 "Could this be trafficking? Self-check →": "Apakah ini perdagangan orang? Periksa sendiri →",
 "What your government promises →": "Apa yang dijanjikan pemerintah Anda →",
 "Find free legal help →": "Cari bantuan hukum gratis →",
 "What works where →": "Apa yang berhasil, dan di mana →",
 "Prepare a rights communication →": "Siapkan pengaduan hak →",
}

def patch(path, prefix, entries, pats=None):
    s = open(path, encoding='utf-8').read(); add = ''
    for k, v in entries.items():
        if J(k) + ':' not in s: add += J(k) + ':' + J(v) + ','
    if add:
        assert prefix in s, prefix
        s = s.replace(prefix, prefix + add, 1)
    n = add.count('":"')
    if pats:
        new = [p for p in pats if J(p[0]) not in s]
        if new:
            s = s.replace('"__pat":[', '"__pat":[' + ','.join(J(p) for p in new) + ',', 1); n += len(new)
    open(path, 'w', encoding='utf-8').write(s)
    return n

print('lang.js:', patch(os.path.join(SITE, 'assets/lang.js'), 'window.SITE_I18N={"id":{', HOME, PAT))
print('clinic i18n.js:', patch(os.path.join(SITE, 'legal-clinic/i18n.js'), 'window.CLINIC_I18N = {"id":{', CLINIC))
