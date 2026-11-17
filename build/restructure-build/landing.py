# Umbrella landing page "Migration Jurisprudence from the South" at /databases/ (restructure, oto 2026-11-13; based on databases-build/databases.py of 2026-11-05)
# Called by restructure.py with the site dir as argv[1].
# /databases/ landing page (oto, 2026-11-05): a welcoming remark adapted from oto's Kompas op-ed
# ("Melindungi Pekerja Migran Tanpa Kompas"), then the databases in two groups (the two menus).
# EN on the page; ID (oto's original Indonesian) in /assets/lang.js. Safe to rerun.
import os, re, json, glob
import sys
SITE = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/theimr-site'
def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s): open(p, 'w', encoding='utf-8').write(s)

# (English, Indonesian) pairs. The ID side is oto's Kompas text, lightly adapted for the site.
T = {}
def t(en, id_): T[en] = id_; return en

TITLE = t('Protecting Migrant Workers Without a Compass', 'Melindungi Pekerja Migran Tanpa Kompas')
P = [
 ('p', t('When her son’s wages from abroad stopped arriving, a mother in Cianjur went to the village head, who wanted to help but did not know which law applied.',
         'Ketika gaji anaknya di luar negeri berhenti datang, seorang ibu di Cianjur mengadu kepada kepala desa, yang ingin menolong tetapi tidak tahu hukum mana yang berlaku.')),
 ('p', t('Going to a trusted person rather than a government office is not a sign of ignorance. In fieldwork with Beth Lyon of Cornell Law School in two farmworker communities in rural West Java, I found that people understand their rights through their relationships with family, neighbors and respected figures. Beth Lyon and I call this the “relational self”. Justice is not imagined as an abstract right claimed alone before the state; it is pursued together, through people one trusts.',
         'Mendatangi orang yang dipercaya, bukan kantor dinas, bukan tanda ketidaktahuan. Dalam penelitian lapangan bersama Beth Lyon dari Cornell Law School di dua komunitas buruh tani di pedesaan Jawa Barat, saya menemukan bahwa orang memahami haknya melalui hubungan dengan keluarga, tetangga, dan orang yang dihormati. Saya dan Beth Lyon menyebutnya “diri relasional”. Keadilan tidak dibayangkan sebagai hak abstrak yang diklaim seorang diri di depan negara, tetapi diupayakan bersama, lewat orang-orang yang dipercaya.')),
 ('p', t('Indonesia’s law on the protection of migrant workers was written with a different picture in mind. Law No. 18 of 2017 and the UN Migrant Workers Convention, which Indonesia ratified through Law No. 6 of 2012, assume a worker who reads the contract, knows their rights and complains in their own name. In practice, the law reaches workers only when an intermediary has mastered it: paralegals and advocates at legal aid institutes, officers of migrant worker organizations, staff of local manpower offices and one-stop service centers, village officials, and officials in ministries and at Indonesian missions abroad.',
         'Hukum pelindungan pekerja migran kita disusun dengan bayangan lain. UU No. 18 Tahun 2017 dan Konvensi Pekerja Migran PBB, yang kita ratifikasi melalui UU No. 6 Tahun 2012, mengandaikan pekerja yang membaca kontraknya, mengetahui haknya, dan mengadu atas namanya sendiri. Dalam praktik, hukum baru sampai kepada pekerja bila ada perantara yang menguasainya: paralegal dan advokat LBH, pengurus organisasi pekerja migran, petugas dinas dan Layanan Terpadu Satu Atap, perangkat desa, serta pejabat di kementerian dan perwakilan RI di luar negeri.')),
 ('h', t('Working without a compass', 'Bekerja tanpa kompas')),
 ('p', t('This is where the problem lies. Most of these intermediaries, activists and officials alike, work without a compass. Not for lack of good will, but because they seldom have a whole picture of the global and comparative legal map: what international law requires, how other countries of origin regulate the same matter, what the law says in countries of destination, and how courts elsewhere have decided similar cases.',
         'Di sinilah persoalannya. Para perantara itu, baik aktivis maupun pejabat, sebagian besar bekerja tanpa kompas. Bukan karena kurang niat baik, melainkan karena mereka jarang memiliki gambaran utuh tentang peta hukum global dan perbandingan: apa yang diwajibkan hukum internasional, bagaimana negara asal lain mengatur hal yang sama, apa isi hukum di negara tujuan, dan bagaimana pengadilan di tempat lain memutus perkara serupa.')),
 ('p', t('The consequences show in many decisions. Policy is often a reaction to whichever case is in the news, such as a temporary halt to placements, without being weighed against the experience of other countries of origin. Restrictions on women’s departure are still seen as protection, although the CEDAW Committee’s General Recommendation No. 26 regards them as discrimination. Memoranda of understanding are negotiated without a comparison table. Civil society campaigns often borrow frameworks from Europe or North America, while complaints to international mechanisms are seldom tried because few people know which doors are open.',
         'Akibatnya terlihat dalam banyak keputusan. Kebijakan sering lahir sebagai reaksi atas kasus yang sedang ramai, misalnya penghentian sementara penempatan, tanpa ditimbang terhadap pengalaman negara asal lain. Pembatasan keberangkatan bagi perempuan masih dianggap pelindungan, padahal Rekomendasi Umum No. 26 Komite CEDAW memandangnya sebagai diskriminasi. Nota kesepahaman dirundingkan tanpa tabel pembanding. Kampanye masyarakat sipil kerap meminjam kerangka dari Eropa atau Amerika Utara, sementara pengaduan ke mekanisme internasional jarang dicoba karena tidak banyak yang tahu pintu mana yang terbuka.')),
 ('p', t('I do not mean to blame anyone. Such knowledge is scattered across dozens of government websites, official gazettes and court archives, in many languages, and it is often not free.',
         'Saya tidak bermaksud menyalahkan siapa pun. Pengetahuan semacam itu tercecer di puluhan situs pemerintah, lembaran negara, dan arsip pengadilan, dalam banyak bahasa, dan sering tidak gratis.')),
 ('p', t('International initiatives have not helped much either. Most migration indexes and databases are designed, funded and run from the most developed countries, so their questions are those countries’ questions: asylum, integration, naturalization and control of arrivals. The issues closest to Indonesian workers, such as placement-fee debt, work permits tied to a single employer, the exclusion of domestic workers and farmworkers from labor law, and the role of countries of origin, receive little attention. Almost none were designed with a village in Cianjur or a district office in Indramayu in mind.',
         'Inisiatif internasional juga belum banyak menolong. Sebagian besar indeks dan basis data migrasi dirancang, didanai, dan dikelola dari negara-negara paling maju, sehingga pertanyaannya adalah pertanyaan negara-negara itu: suaka, integrasi, naturalisasi, dan pengendalian kedatangan. Persoalan yang paling dekat dengan pekerja kita, seperti utang biaya penempatan, izin kerja yang terikat pada satu majikan, pengecualian pekerja rumah tangga dan buruh tani dari hukum ketenagakerjaan, serta peran negara asal, kurang mendapat tempat. Hampir tidak ada yang dirancang dengan desa di Cianjur atau kantor dinas di Indramayu dalam pikiran.')),
 ('p', t('To fill that gap, the Institute for Migrant Rights in Cianjur has spent several years building the open legal databases on this site, helped by many volunteers, most of them law students from many countries. All of them can be downloaded and are explained in everyday language, in Indonesian and English.',
         'Untuk mengisi kekosongan itu, Institute for Migrant Rights (IMR) di Cianjur menyusun basis data hukum terbuka di situs ini selama beberapa tahun, dibantu banyak relawan, sebagian besar mahasiswa hukum dari berbagai negara. Semuanya bisa diunduh dan dijelaskan dalam bahasa sehari-hari, dalam bahasa Indonesia dan Inggris.')),
 ('em', t('They are free, cheap and, above all, meant to be hassle-free to use: no account, no subscription and no special software. A browser is enough, and the data come as files that open in an ordinary spreadsheet.',
          'Basis data ini gratis, murah, dan yang terpenting dimaksudkan agar mudah dipakai tanpa repot: tanpa akun, tanpa langganan, dan tanpa perangkat lunak khusus. Cukup peramban, dan datanya tersedia sebagai berkas yang bisa dibuka di program lembar kerja biasa.')),
 ('h', t('For NGOs and legal aid institutes', 'Bagi LSM dan lembaga bantuan hukum')),
 ('p', t('IMR’s online International Legal Clinic guides workers, or those assisting them, to the UN body or regional mechanism that may be able to receive their case, and then drafts a complaint that is reviewed with IMR advocates. It is an additional route, not a substitute, for litigation and mediation already under way.',
         'Klinik Hukum Internasional daring IMR menuntun pekerja atau pendampingnya menemukan badan PBB atau mekanisme kawasan yang mungkin bisa menerima perkaranya, lalu menyusun draf pengaduan yang ditinjau bersama advokat IMR. Ini jalur tambahan, bukan pengganti, bagi litigasi dan mediasi yang sudah berjalan.')),
 ('p', t('The Court Decisions database holds nearly 500 decisions from Asia, Africa, the Middle East and Latin America, searchable by the arguments judges accepted or rejected. An advocate suing a placement agency, for example, can see how Philippine courts have held agencies jointly liable with employers abroad. The directory of free legal help helps refer victims to organizations in the country where they work, and the ratification and comparison data can be cited in shadow reports to the UN Committee on Migrant Workers.',
         'Basis data “Putusan Pengadilan” memuat hampir 500 putusan dari Asia, Afrika, Timur Tengah, dan Amerika Latin, yang bisa dicari menurut argumen yang diterima atau ditolak hakim. Advokat yang menggugat perusahaan penempatan, misalnya, bisa melihat bagaimana pengadilan Filipina membebankan tanggung jawab bersama kepada agen dan majikan di luar negeri. Direktori bantuan hukum gratis membantu merujuk korban ke organisasi di negara tempatnya bekerja, dan data ratifikasi serta perbandingan bisa dikutip dalam laporan bayangan kepada Komite Pekerja Migran PBB.')),
 ('h', t('For central and local government', 'Bagi pemerintah pusat dan daerah')),
 ('p', t('The Countries of Origin page sets Indonesia beside the Philippines, Vietnam, Nepal, Bangladesh, India, Sri Lanka and Pakistan on nine questions, from the licensing of placement agencies and fees to restrictions on departure and reintegration. Ministries can use it when drafting implementing regulations or considering a revision of Law No. 18 of 2017. The pages on countries of destination, from domestic workers in Hong Kong and fishing crews in Taiwan to the legal frameworks of the Gulf states, can serve as starting material for bilateral negotiations.',
         'Halaman perbandingan negara asal menyandingkan Indonesia dengan Filipina, Vietnam, Nepal, Bangladesh, India, Sri Lanka, dan Pakistan pada sembilan soal, dari perizinan perusahaan penempatan dan biaya sampai pembatasan keberangkatan dan reintegrasi. Kementerian bisa memakainya ketika menyusun peraturan pelaksana atau menimbang revisi UU 18/2017. Halaman tentang negara tujuan, dari pekerja rumah tangga di Hong Kong dan awak kapal ikan Taiwan sampai kerangka hukum negara-negara Teluk, bisa menjadi bahan awal perundingan bilateral.')),
 ('p', t('The Migration Law Atlas, with its farmworker law view, records more than 80 international and regional instruments and their ratification status in 187 countries, which helps in weighing the ILO conventions Indonesia has not yet ratified, for example on domestic workers and on fishing crews. District offices and village officials can use the plain-language explanations in outreach, and the decisions database can be used in training judges and prosecutors.',
         'Atlas Hukum Migrasi, dengan tampilan khusus hukum buruh tani, mencatat lebih dari 80 instrumen internasional dan kawasan serta status ratifikasinya di 187 negara, sehingga membantu menimbang konvensi ILO yang belum kita ratifikasi, misalnya tentang pekerja rumah tangga dan awak kapal perikanan. Dinas kabupaten dan perangkat desa bisa memakai penjelasan berbahasa sederhana sebagai bahan sosialisasi, dan basis data putusan bisa menjadi bahan pelatihan hakim dan jaksa.')),
 ('h', t('For universities', 'Bagi perguruan tinggi')),
 ('p', t('Legal education in Indonesia still rests on the interpretation of provisions and doctrine, while questions about how law works in practice are seldom tested with data. Every rule and decision in IMR’s databases is coded on the same variables, with a codebook and its sources, so that students can write undergraduate, master’s and doctoral theses that test legal questions in measurable ways. Comparative law courses can also look to the Philippines, South Africa, Kenya or Colombia, countries whose problems are closer to Indonesia’s. University law clinics can use all these tools in practice, and help check the data at the same time.',
         'Pendidikan hukum kita masih bertumpu pada tafsir pasal dan doktrin, sementara pertanyaan tentang bagaimana hukum bekerja dalam kenyataan jarang diuji dengan data. Setiap aturan dan putusan dalam basis data IMR diberi kode menurut variabel yang sama, disertai buku kode dan sumbernya, sehingga mahasiswa bisa menulis skripsi, tesis, dan disertasi yang menguji pertanyaan hukum secara terukur. Mata kuliah perbandingan hukum pun bisa menengok Filipina, Afrika Selatan, Kenya, atau Kolombia, negara yang persoalannya lebih mirip dengan kita. Klinik hukum kampus bisa memakai semua alat ini sebagai bahan praktik, sekaligus membantu memeriksa data.')),
 ('h', t('An invitation to work together', 'Undangan untuk bekerja sama')),
 ('p', t('I want to stress that these databases are not final. This is a first version, published early on purpose so that it can be tested and corrected. Many entries still await checking against the official text, several countries important to Indonesian workers are not yet covered, and some of my coding choices are certainly open to debate.',
         'Saya ingin menegaskan bahwa basis data ini belum final. Ini versi pertama yang sengaja diterbitkan lebih awal agar bisa diuji dan dikoreksi. Banyak isian masih menunggu pemeriksaan terhadap teks resmi, sejumlah negara penting bagi pekerja kita belum tercakup, dan sebagian pilihan pengodean saya tentu bisa diperdebatkan.')),
 ('pmail', t('I therefore invite officials, legal aid institutes, SBMI, Migrant CARE, local organizations, lecturers, students, and former migrant workers and their families to help improve them, by sending laws and decisions, checking entries, or simply telling us whether these pages help. Every contribution is credited by name and every correction is logged openly. Suggestions can be sent to',
         'Karena itu saya mengundang pejabat, LBH, SBMI, Migrant CARE, organisasi di daerah, dosen, mahasiswa, serta mantan pekerja migran dan keluarganya untuk ikut menyempurnakannya, dengan mengirim peraturan dan putusan, memeriksa isian, atau sekadar memberi tahu apakah halaman-halaman ini menolong. Setiap sumbangan dicantumkan namanya dan setiap koreksi dicatat terbuka. Masukan bisa dikirim ke')),
 ('p', t('If justice for migrant workers is indeed sought through relationships, then humane law is law that reaches the hands of those intermediaries, clear enough to be retold on the front porch of a home.',
         'Jika keadilan bagi pekerja migran memang dicari lewat hubungan, hukum yang manusiawi adalah hukum yang sampai ke tangan para perantara itu, cukup jelas untuk diceritakan ulang di beranda rumah.')),
]
SIGN = t('Founding Director, Institute for Migrant Rights', 'Direktur Pendiri, Institute for Migrant Rights')

SEA = os.path.exists(SITE + '/southeast-asia/index.html')
GROUPS = [
 (('Law across tiers', 'Hukum lintas tingkat', 'Global, regional and national law in one explorer.', 'Hukum tingkat dunia, kawasan, dan nasional dalam satu alat jelajah.'),
  [('/migration-law/', 'Migration Law Atlas', t('Global, regional and national migration law with ratifications for 187 countries. Switch to the farmworker law view for the norms on farm work, their timeline and how they are implemented.', 'Hukum migrasi tingkat dunia, kawasan, dan nasional dengan data ratifikasi 187 negara. Beralih ke tampilan hukum buruh tani untuk norma kerja pertanian, linimasanya, dan penerapannya.'))]),
 (('Destination states', 'Negara tujuan', 'The law that applies where migrant workers are employed.', 'Hukum yang berlaku di tempat pekerja migran dipekerjakan.'),
  [('/gcc/', 'Gulf States', t('Labor and migration law in the six Gulf states, coded rule by rule with sources.', 'Hukum ketenagakerjaan dan migrasi di enam negara Teluk, dikodekan per aturan beserta sumbernya.')),
   ('/east-asia/', 'East Asia', t('Migrant worker law in the main East Asian destinations.', 'Hukum pekerja migran di negara tujuan utama di Asia Timur.'))]
  + ([('/southeast-asia/', 'Southeast Asia', t('Migrant worker law in the main Southeast Asian destinations.', 'Hukum pekerja migran di negara tujuan utama di Asia Tenggara.'))] if SEA else [])),
 (('Origin states', 'Negara pengirim', 'The law of the countries migrant workers leave from.', 'Hukum negara tempat pekerja migran berangkat.'),
  [('/countries-of-origin/', 'Countries of Origin', t('Indonesia and other major countries of origin compared on nine questions.', 'Indonesia dan negara asal utama lainnya dibandingkan pada sembilan soal.'))]),
 (('Themes', 'Tema', 'Questions that cut across origin and destination.', 'Persoalan yang melintasi negara asal dan negara tujuan.'),
  [('/domestic-workers/', 'Migrant Domestic Workers', t('International, regional, bilateral and national law on domestic workers who migrate, coded against ILO C189 for 44 countries.', 'Hukum internasional, kawasan, bilateral, dan nasional tentang pekerja rumah tangga yang bermigrasi, dikodekan menurut ILO C189 untuk 44 negara.')),
   ('/government-hate-speech/', 'Government Hate Speech', t('Hateful speech by officials and politicians: statistics, legal frameworks and episodes, with a comparison of hate speech, elections and the protection of non-citizens in 34 democracies.', 'Ucapan kebencian oleh pejabat dan politisi: statistik, kerangka hukum, dan peristiwa, dengan perbandingan ucapan kebencian, pemilu, dan pelindungan orang yang bukan warga negara di 34 negara demokrasi.'))]),
 (('Courts', 'Pengadilan', 'Judgments and decisions of national, regional and international bodies.', 'Putusan badan nasional, kawasan, dan internasional.'),
  [('/court-decisions/', 'Court Decisions', t('Nearly 500 court decisions from Asia, Africa, the Middle East and Latin America.', 'Hampir 500 putusan pengadilan dari Asia, Afrika, Timur Tengah, dan Amerika Latin.'))]),
]
for (h, hid, d, did), _ in GROUPS: T.setdefault(h, hid); T.setdefault(d, did)
for k, v in [('Databases', 'Basis data'), ('All databases', 'Semua basis data'), ('Welcoming remark', 'Kata sambutan'),
             ('Open legal databases on migration', 'Basis data hukum terbuka tentang migrasi'),
             ('A welcoming remark, then the databases in five groups.', 'Kata sambutan, lalu basis data dalam lima kelompok.'), ('Open legal databases', 'Basis data hukum terbuka'), ('Court Decisions', 'Putusan Pengadilan'), ('Southeast Asia', 'Asia Tenggara'),
             ('Go to the databases', 'Langsung ke basis data'),
             ('Projects', 'Proyek'),
             ('Atlases of international, regional and national norms, and IMR’s research projects.', 'Atlas norma internasional, kawasan, dan nasional, serta proyek penelitian IMR.'),
             ('Migration and Labor Laws in Comparison', 'Hukum Migrasi dan Ketenagakerjaan dalam Perbandingan'),
             ('Country-by-country comparisons of laws and court decisions.', 'Perbandingan hukum dan putusan pengadilan antarnegara.'),
             ('Open →', 'Buka →'),
             ('Need help with a case?', 'Perlu bantuan untuk suatu perkara?'),
             ('Legal Clinic', 'Klinik Hukum'), ('Find legal help', 'Cari bantuan hukum'),
             ('How we use AI', 'Cara kami memakai AI')]:
    T.setdefault(k, v)

# ---------- page ----------
S = rd(SITE + '/people.html')
head = S[:S.index('</header>') + len('</header>')]
tail = S[S.index('<div class="imr-ridge"'):]
title = 'Migration Jurisprudence from the South · Institute for Migrant Rights'
desc = ('Free, open legal databases on migration and migrant workers from the Institute for Migrant Rights: '
        'atlases of migration and farmworker law, and comparisons of national laws and court decisions.')
for a, b in [(r'<title>.*?</title>', '<title>%s</title>' % title),
             (r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc),
             (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % title),
             (r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % desc),
             (r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://theimr.org/databases/">'),
             (r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="https://theimr.org/databases/">')]:
    head = re.sub(a, b, head)
head = head.replace('<a href="people.html" aria-current="page" style="color: #1E6B4A; text-decoration: underline; text-underline-offset: 6px; padding: 10px 0">People</a>',
                    '<a href="/people.html" style="color: #172D24; text-decoration: none; padding: 10px 0">People</a>')
head = re.sub(r'href="(?!/|https?:|mailto:|#)([^"]+)"', r'href="/\1"', head)
ld = {"@context": "https://schema.org", "@type": "DataCatalog", "name": "Migration Jurisprudence from the South", "url": "https://theimr.org/databases/",
      "description": desc, "inLanguage": ["en", "id"], "dateModified": "2026-11-13",
      "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
      "hasPart": [{"@type": "Dataset", "name": n, "url": "https://theimr.org" + u} for _, g in GROUPS for u, n, _ in g]}
head = head.replace('</head>', '<style>\n.db-remark p{margin:18px 0 0}\n.db-remark h2{margin:40px 0 0;font-weight:500;font-size:26px;line-height:1.25}\n'
  '.db-remark .em{margin:24px 0 0;padding:18px 22px;background:#DCE8E1;border-left:4px solid #1E6B4A;font-weight:500}\n'
  '.db-cards{list-style:none;margin:24px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}\n'
  '.db-cards a{display:flex;flex-direction:column;height:100%;box-sizing:border-box;padding:22px 22px 18px;background:#FFFFFF;border:1px solid #B2C7BC;color:#172D24;text-decoration:none}\n'
  '.db-cards a:hover{border-color:#1E6B4A}.db-cards b{font-weight:600;font-size:21px;line-height:1.25}\n'
  '.db-cards span{margin-top:8px;font-size:16px;color:#2E493D;flex:1}.db-cards i{margin-top:14px;font-style:normal;font-weight:600;font-size:15px;color:#1E6B4A}\n'
  ".db-eye{margin:0;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#1E6B4A}\n"
  '@media (max-width:640px){.db-h1{font-size:40px!important}}\n</style>\n'
  '<script type="application/ld+json">LDJSON</script>\n</head>').replace('LDJSON', json.dumps(ld, ensure_ascii=False))

def cards(g):
    return '<ul class="db-cards">' + ''.join('<li><a href="%s"><b>%s</b><span>%s</span><i>Open →</i></a></li>' % (u, n, d) for u, n, d in g) + '</ul>'
body = []
for kind, txt in P:
    if kind == 'h': body.append('<h2>%s</h2>' % txt)
    elif kind == 'em': body.append('<p class="em">%s</p>' % txt)
    elif kind == 'pmail': body.append('<p>%s <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.</p>' % txt)
    else: body.append('<p>%s</p>' % txt)
main = '\n'.join([
 '<main id="databases">',
 '<section style="padding: 80px 0 24px"><div style="max-width: 760px; margin: 0 auto; padding: 0 24px; text-align: center">',
 "<p style=\"margin: 0; font-family: 'Familjen Grotesk', sans-serif; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: #1E6B4A\">Open legal databases</p>",
 '<h1 class="db-h1" style="margin: 16px 0 0; font-weight: 400; font-size: 54px; line-height: 1.1">Migration Jurisprudence from the South</h1>',
 '<p style="margin: 18px 0 0; color: #2E493D">A welcoming remark, then the databases in five groups.</p>',
 '<p style="margin: 14px 0 0; font-size: 16px; font-weight: 600"><a href="#groups">Go to the databases</a></p>',
 '</div></section>',
 '<section id="remark" style="padding: 24px 0 56px"><div class="db-remark" style="max-width: 720px; margin: 0 auto; padding: 0 24px">',
 '<p class="db-eye" style="margin:0">Welcoming remark</p>',
 '<h2 style="margin: 10px 0 0; font-weight: 400; font-size: 36px; line-height: 1.15">%s</h2>' % TITLE,
 '\n'.join(body),
 '<p style="margin: 28px 0 0"><b>Pranoto Iskandar</b><br><span style="font-size: 16px; color: #3D5A4D">%s</span></p>' % SIGN,
 '</div></section>',
 '<section id="groups" style="padding: 56px 0 72px; background: #DCE8E1; border-top: 1px solid #B2C7BC; scroll-margin-top: 12px"><div style="max-width: 1120px; margin: 0 auto; padding: 0 24px">',
 ''.join('<div id="g%d" style="%sscroll-margin-top: 12px"><p class="db-eye">%s</p><h2 style="margin: 6px 0 0; font-weight: 500; font-size: 30px">%s</h2><p style="margin: 8px 0 0; color: #2E493D">%s</p>%s</div>' % (k+1, '' if k == 0 else 'margin-top: 56px; ', ['I','II','III','IV','V'][k], h[0], h[2], cards(g)) for k, (h, g) in enumerate(GROUPS)),
 '<p style="margin: 48px 0 0; font-size: 16px"><b>Need help with a case?</b> <a href="/legal-clinic/">Legal Clinic</a> · <a href="/legal-help/">Find legal help</a> · <a href="/ai-use/">How we use AI</a></p>',
 '</div></section>',
 '</main>', ''])
os.makedirs(SITE + '/databases', exist_ok=True)
wr(SITE + '/databases/index.html', head + '\n' + main + tail)
print('page written')

# ---------- lang.js ----------
L = SITE + '/assets/lang.js'; s = rd(L); pre = 'window.SITE_I18N={"id":{'
assert s.startswith(pre)
add = {k: v for k, v in T.items() if json.dumps(k, ensure_ascii=False) + ':' not in s}
if add:
    s = pre + ''.join('%s:%s,' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in add.items()) + s[len(pre):]
    wr(L, s)
print('lang.js entries added:', len(add))

print('landing done')
