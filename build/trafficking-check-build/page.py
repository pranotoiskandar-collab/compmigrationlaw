# Builds /legal-clinic/trafficking-check/index.html from the site chrome of /legal-clinic/what-works/.
# Usage: node build.js SITE && python3 page.py SITE, then restructure.py, ai_use.py, analytics.py.
import re, sys, json, os
SITE = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/theimr-site'
SRC = open(SITE + '/legal-clinic/what-works/index.html', encoding='utf-8').read()
URL = 'https://theimr.org/legal-clinic/trafficking-check/'
TITLE = 'Could this be human trafficking? A self-check · Legal Clinic · Institute for Migrant Rights'
DESC = ('A free, private self-check for migrant workers and their families: answer short questions and get a result sheet on whether a situation may be human trafficking or forced labor under the Palermo Protocol, ILO standards, Indonesian law and the law of the destination country.')

def LL(en, id_): return '<span class="en">%s</span><span class="id">%s</span>' % (en, id_)

CSS = r'''
html[lang="id"] .en{display:none} html:not([lang="id"]) .id{display:none}
.tc{max-width:1120px;margin:0 auto;padding:0 24px}
.tc-eye{margin:0;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1E6B4A}
.tc-exit{position:fixed;right:14px;bottom:14px;z-index:20;background:#172D24;color:#fff;border:0;padding:12px 16px;font:600 15px 'Familjen Grotesk',system-ui,sans-serif;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.25)}
.tc-card{margin:32px 0 0;background:#fff;border:1px solid #B2C7BC;padding:28px clamp(18px,4vw,40px);max-width:860px}
.tc-big{font-size:21px;margin:0}
.tc-ticks{list-style:none;margin:20px 0 0;padding:0}.tc-ticks li{display:flex;gap:12px;align-items:flex-start;padding:8px 0;font-size:17px}
.tc-ticks svg,.tc-opt svg{flex:0 0 auto;width:32px;height:32px;color:#1E6B4A}
.tc-danger{margin:18px 0 0;padding:14px 18px;background:#F2DCD6;font-size:17px}
.tc-prog{height:6px;background:#DCE8E1}.tc-prog i{display:block;height:6px;background:#1E6B4A}
.tc-count{margin:14px 0 0;font:500 13px 'JetBrains Mono',monospace;color:#3D5A4C}
.tc-card fieldset{border:0;margin:0;padding:0;min-width:0}
.tc-q{font-size:26px;line-height:1.25;font-weight:500;margin:8px 0 0;padding:0;outline:none}
.tc-hint{margin:8px 0 0;color:#2E493D;font-size:17px}
.tc-opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin:22px 0 0}
.tc-small.tc-opts,.tc-opts.tc-small{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.tc-opt{position:relative;display:flex;gap:12px;align-items:center;text-align:left;min-height:64px;padding:12px 40px 12px 14px;background:#EEF4F0;border:2px solid #B2C7BC;color:#172D24;font:17px/1.35 'Familjen Grotesk',system-ui,sans-serif;cursor:pointer}
.tc-opt:hover{border-color:#1E6B4A}.tc-opt[aria-pressed="true"]{background:#C9E3D3;border-color:#1E6B4A;font-weight:600}
.tc-box{position:absolute;right:12px;top:50%;width:20px;height:20px;margin-top:-10px;border:2px solid #3D5A4C;background:#fff}
.tc-opt[aria-pressed="true"] .tc-box{background:#1E6B4A;border-color:#1E6B4A;box-shadow:inset 0 0 0 3px #fff}
.tc-nav{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:24px 0 0}
.tc-go,.tc-back,.tc-listen{display:inline-flex;gap:8px;align-items:center;min-height:48px;padding:10px 20px;font:600 17px 'Familjen Grotesk',system-ui,sans-serif;cursor:pointer;border:2px solid #1E6B4A}
.tc-go{background:#1E6B4A;color:#fff}.tc-go:hover{background:#134A33}.tc-go[disabled]{opacity:.45;cursor:default}
.tc-back{background:#fff;color:#1E6B4A}.tc-listen{background:none;border-color:transparent;color:#1E6B4A;margin-left:auto}
.tc-go svg,.tc-back svg,.tc-listen svg{width:22px;height:22px}
.tc-sheet{margin:32px 0 0;background:#fff;border:1px solid #B2C7BC;padding:32px clamp(18px,4vw,48px);max-width:900px;font-size:17px;line-height:1.6;color:#172D24}
.tc-sheet section{margin:28px 0 0;padding:22px 0 0;border-top:1px solid #DCE8E1}
.tc-sh h2{margin:8px 0 0;font-weight:500;font-size:30px;line-height:1.2}.tc-meta{margin:8px 0 0;font-size:14px;color:#3D5A4C}
.tc-sheet h3{margin:6px 0 0;font-size:26px;font-weight:600;line-height:1.25}.tc-sheet h4{margin:18px 0 0;font-size:18px}
.tc-verdict{padding:20px 22px!important;border:0!important;border-left:8px solid}
.tc-v-red{background:#F7E4DF;border-left-color:#A33B2A}.tc-v-amber{background:#F6EFD9;border-left-color:#9A6B1F}.tc-v-green{background:#E2F0E7;border-left-color:#1E6B4A}
.tc-local{padding:10px 14px;background:#fff}
.tc-lead{margin:8px 0 0}.tc-note{margin:14px 0 0;padding:12px 16px;background:#EEF4F0}.tc-small{font-size:14px;color:#3D5A4C}
.tc-els{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0 0}
.tc-el{padding:14px 16px;border:2px solid #B2C7BC}.tc-el h4{margin:2px 0 0;font-size:17px}
.tc-eln{margin:0;font:600 26px 'JetBrains Mono',monospace}.tc-st{margin:4px 0 0;font-weight:700}
.tc-el ul{margin:6px 0 0;padding-left:18px;font-size:15px}
.tc-ok{border-color:#A33B2A;background:#FBF1EE}.tc-ok .tc-st{color:#A33B2A}.tc-unk{border-color:#9A6B1F}.tc-unk .tc-st{color:#7A5418}
.tc-no .tc-st,.tc-na .tc-st{color:#3D5A4C}
.tc-ilo{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:4px 16px}
.tc-ilo li{display:flex;gap:8px;align-items:center;font-size:15px;color:#7F9A8C}.tc-ilo li.on{color:#172D24;font-weight:600}.tc-ilo svg{width:20px;height:20px;flex:0 0 auto}.tc-ilo li.on svg{color:#A33B2A}
.tc-list{margin:10px 0 0;padding-left:20px}.tc-list li{margin:8px 0}
.tc-refs{margin:8px 0 0;padding-left:18px;font-size:15px}.tc-refs li{margin:10px 0}
.tc-chk{display:inline-block;padding:0 7px;border:1px solid #9A6B1F;color:#7A5418;font:500 11px 'JetBrains Mono',monospace;letter-spacing:.04em;vertical-align:1px}
.tc-tr{border-collapse:collapse;margin:8px 0 0;font-size:15px;width:100%;max-width:620px}.tc-tr th,.tc-tr td{text-align:left;padding:6px 8px;border-bottom:1px solid #DCE8E1;font-weight:400}
.tc-yes{color:#1E6B4A}.tc-nop{color:#7A5418}
.tc-cases{margin:12px 0 0;padding-left:22px}.tc-cases li{margin:12px 0}
.tc-ans{margin:10px 0 0;font-size:15px}.tc-ans dt{font-weight:600;margin:8px 0 0}.tc-ans dd{margin:2px 0 0 0;color:#2E493D}
.tc-sf{margin:28px 0 0;padding:16px 0 0;border-top:2px solid #172D24;font-size:13px;color:#3D5A4C}
.tc-meth{max-width:860px}.tc-meth h3{margin:28px 0 0;font-size:20px}.tc-meth p,.tc-meth li{font-size:17px}
.tc-flow{margin:16px 0 0;padding:16px 18px;background:#fff;border:1px solid #B2C7BC;font:14px/1.7 'JetBrains Mono',monospace;white-space:pre-wrap;overflow-x:auto}
@media (max-width:640px){.tc-exit{padding:8px 12px;font-size:14px;right:8px;bottom:8px}.tc-h1{font-size:36px!important}.tc-q{font-size:22px}.tc-opts{grid-template-columns:1fr}.tc-listen{margin-left:0}}
@media print{
 body *{visibility:hidden}.tc-sheet,.tc-sheet *{visibility:visible}
 .tc-sheet{position:absolute;left:0;top:0;margin:0;border:0;padding:0;max-width:none;font-size:12pt}
 .tc-sheet section{break-inside:avoid-page}.tc-sheet a{color:#172D24}.tc-exit,.tc-sheetnav{display:none}
}
'''

FLOW = LL(
'''Age under 18?  ── yes ──▶  ACT + PURPOSE            ⇒ trafficking (child)
      │ no
      ▼
ACT + MEANS + PURPOSE                              ⇒ trafficking
      │ not all three
      ▼
NOT FREE (involuntary) + COERCION                  ⇒ forced labor
      │ no
      ▼
paid to cross a border, free on arrival            ⇒ smuggling
two parts present, or one present + one unclear    ⇒ more facts needed
wage, document, debt or condition problems         ⇒ other labor rights problems
otherwise                                          ⇒ few signs''',
'''Di bawah 18?  ── ya ──▶  PERBUATAN + TUJUAN       ⇒ perdagangan anak
      │ tidak
      ▼
PERBUATAN + CARA + TUJUAN                          ⇒ perdagangan orang
      │ tidak ketiganya
      ▼
TIDAK SUKARELA + PAKSAAN                           ⇒ kerja paksa
      │ tidak
      ▼
membayar untuk menyeberang, bebas setelah tiba     ⇒ penyelundupan
dua unsur ada, atau satu ada + satu belum jelas    ⇒ perlu fakta lebih banyak
masalah upah, dokumen, utang, atau kondisi         ⇒ masalah hak pekerja lain
selain itu                                         ⇒ sedikit tanda''')

METHOD = '''<section id="method" class="tc-meth" style="margin-top:72px">
<p class="tc-eye">%s</p>
<h2 style="margin:10px 0 0;font-weight:500;font-size:32px">%s</h2>
<p>%s</p>
<div class="tc-flow">%s</div>
<h3>%s</h3><p>%s</p>
<h3>%s</h3><p>%s</p>
<h3>%s</h3><p>%s</p>
<h3>%s</h3><p>%s</p>
<h3>%s</h3><p>%s</p>
<h3>%s</h3><p>%s</p>
</section>''' % (
LL('Method', 'Metode'),
LL('How the self-check reaches its result', 'Bagaimana pemeriksaan ini sampai pada hasilnya'),
LL('The check is a transparent decision tree, not a statistical or machine-learning model. Every answer maps onto a named legal element, and the same answers always give the same result. The full logic, the legal sources and their limits are set out in the explanatory note.',
   'Pemeriksaan ini adalah pohon keputusan yang terbuka, bukan model statistik atau pembelajaran mesin. Setiap jawaban dipetakan ke unsur hukum yang disebut namanya, dan jawaban yang sama selalu memberi hasil yang sama. Seluruh logika, sumber hukum, dan batasannya dijelaskan dalam catatan penjelasan.'),
FLOW,
LL('1. Trafficking: three elements', '1. Perdagangan orang: tiga unsur'),
LL('The test follows Article 3 of the UN Trafficking in Persons Protocol (2000), which Indonesia ratified by Law 14/2009, and Article 1(1) of Law 21/2007. An adult case needs an <i>act</i> (recruitment, transportation, transfer, harboring or receipt; Indonesian law adds sending), a <i>means</i> (threat, force, coercion, abduction, fraud, deception, abuse of power or of a position of vulnerability, payments to a person in control; Indonesian law adds confinement, falsification and debt bondage) and a <i>purpose</i> of exploitation. For a child (under 18) the means element is not required (Art. 3(c)–(d)). Consent is irrelevant once a means is used (Art. 3(b); Law 21/2007, Art. 26). A planned purpose is enough; Indonesian law also covers conduct that results in exploitation.',
   'Uji ini mengikuti Pasal 3 Protokol PBB tentang Perdagangan Orang (2000), yang diratifikasi Indonesia dengan UU 14/2009, dan Pasal 1 angka 1 UU 21/2007. Perkara orang dewasa memerlukan <i>perbuatan</i> (perekrutan, pengangkutan, pemindahan, penampungan, atau penerimaan; hukum Indonesia menambahkan pengiriman), <i>cara</i> (ancaman, kekerasan, paksaan, penculikan, penipuan, penyalahgunaan kekuasaan atau posisi rentan, pemberian bayaran kepada orang yang memegang kendali; hukum Indonesia menambahkan penyekapan, pemalsuan, dan penjeratan utang), dan <i>tujuan</i> eksploitasi. Untuk anak (di bawah 18) unsur cara tidak diperlukan (Pasal 3(c)–(d)). Persetujuan tidak relevan begitu suatu cara dipakai (Pasal 3(b); UU 21/2007, Pasal 26). Tujuan yang direncanakan sudah cukup; hukum Indonesia juga mencakup perbuatan yang mengakibatkan eksploitasi.'),
LL('2. Forced labor: two dimensions', '2. Kerja paksa: dua dimensi'),
LL('Forced labor is defined by ILO Convention No. 29, Art. 2(1). To operationalize it, the check uses the two-dimension rule of the Guidelines concerning the measurement of forced labor adopted by the 20th International Conference of Labour Statisticians (2018): work counts as forced only when it is both <i>involuntary</i> (deceptive recruitment, conditions not agreed, no freedom to leave, excessive hours, degrading conditions) and imposed by <i>coercion</i> (violence, threats, confinement, isolation, withheld wages or documents, debt manipulation). The eleven ILO indicators (2012) are shown as a checklist. When forced labor is found, the purpose element of trafficking is treated as present.',
   'Kerja paksa didefinisikan oleh Konvensi ILO No. 29, Pasal 2(1). Untuk menerapkannya, pemeriksaan memakai aturan dua dimensi dari Pedoman pengukuran kerja paksa yang diadopsi Konferensi Internasional Ahli Statistik Ketenagakerjaan ke-20 (2018): pekerjaan dihitung sebagai kerja paksa hanya bila <i>tidak sukarela</i> (rekrutmen yang menipu, kondisi yang tidak disepakati, tidak bebas pergi, jam kerja berlebihan, kondisi yang merendahkan) sekaligus dipaksakan melalui <i>paksaan</i> (kekerasan, ancaman, pengurungan, isolasi, upah atau dokumen ditahan, manipulasi utang). Sebelas indikator ILO (2012) ditampilkan sebagai daftar periksa. Bila kerja paksa ditemukan, unsur tujuan perdagangan orang dianggap ada.'),
LL('3. National peculiarities', '3. Kekhususan hukum nasional'),
LL('The result is first stated against international law and Indonesian law, which applies to recruiters and agents in Indonesia and protects Indonesians abroad (Law 21/2007, Arts. 4 and 54; Law 18/2017). For 14 destination countries the sheet adds the country’s trafficking statute, its treaty obligations, its rules on changing employer, recruitment fees and domestic work, and a note on how its law departs from the Palermo model. Where the difference changes the likely outcome (for example Hong Kong, whose only trafficking offense concerns prostitution, or Thailand and South Korea, which punish forced labor separately), the result says so. Treaty status and work rules come from the IMR comparison datasets; Gulf entries are descriptive.',
   'Hasil pertama-tama dinyatakan menurut hukum internasional dan hukum Indonesia, yang berlaku bagi perekrut dan agen di Indonesia dan melindungi WNI di luar negeri (UU 21/2007, Pasal 4 dan 54; UU 18/2017). Untuk 14 negara tujuan, lembar hasil menambahkan undang-undang perdagangan orang negara itu, kewajiban traktatnya, aturan pindah majikan, biaya rekrutmen, dan kerja rumah tangga, serta catatan tentang bagaimana hukumnya berbeda dari model Palermo. Bila perbedaan itu mengubah kemungkinan hasil (misalnya Hong Kong, yang satu-satunya tindak pidana perdagangan orangnya menyangkut pelacuran, atau Thailand dan Korea Selatan, yang menghukum kerja paksa secara tersendiri), hasil menyebutkannya. Status traktat dan aturan kerja diambil dari dataset perbandingan IMR; entri Teluk bersifat deskriptif.'),
LL('4. Similar decisions', '4. Putusan serupa'),
LL('Decisions are drawn from the Court Decisions collection of Migration Jurisprudence from the South by matching the situation (sector, form of exploitation, child, debt, forced labor, migration abroad) to tagged decisions. National, regional and international decisions from Asia, Africa, the Middle East and Latin America rank first; European decisions follow. Uncoded candidates rank last and are labelled.',
   'Putusan diambil dari koleksi Putusan Pengadilan dalam Yurisprudensi Migrasi dari Selatan dengan mencocokkan keadaan (sektor, bentuk eksploitasi, anak, utang, kerja paksa, migrasi ke luar negeri) dengan putusan bertanda. Putusan nasional, kawasan, dan internasional dari Asia, Afrika, Timur Tengah, dan Amerika Latin diurutkan lebih dulu; putusan Eropa menyusul. Kandidat yang belum dikodekan diurutkan terakhir dan diberi label.'),
LL('5. Limits', '5. Batasan'),
LL('The check relies on what the person reports and simplifies legal concepts into plain questions. It cannot weigh evidence, credibility or intent, and it does not cover every national offense. Indonesian statutory references are marked “being checked” until compared with the official texts (JDIH BPK, peraturan.go.id); destination-country notes rest partly on secondary sources. The plain-language wording was drafted with AI assistance and edited by IMR (<a href="/ai-use/">how we use AI</a>). The rules themselves are fixed and written by people.',
   'Pemeriksaan ini bergantung pada apa yang dilaporkan dan menyederhanakan konsep hukum menjadi pertanyaan sederhana. Pemeriksaan ini tidak bisa menimbang bukti, kredibilitas, atau niat, dan tidak mencakup setiap tindak pidana nasional. Rujukan undang-undang Indonesia ditandai “sedang diperiksa” sampai dibandingkan dengan naskah resmi (JDIH BPK, peraturan.go.id); catatan negara tujuan sebagian bersandar pada sumber sekunder. Kata-kata sederhana disusun dengan bantuan AI dan disunting IMR (<a href="/ai-use/">cara kami memakai AI</a>). Aturannya sendiri tetap dan ditulis oleh manusia.'),
LL('6. Privacy and usage counts', '6. Privasi dan hitungan penggunaan'),
LL('Answers are kept only in the page’s memory and are never stored or sent; the result sheet is made in the browser. To report how much the tool is used, the page sends anonymous counts to GoatCounter (no cookies): that a check was started, that it was finished with its result level (for example “forced labor”) and whether it concerned Indonesia or abroad, and whether a sheet was printed or downloaded. No answers, countries or identifiers are sent.',
   'Jawaban hanya disimpan di memori halaman dan tidak pernah disimpan atau dikirim; lembar hasil dibuat di peramban. Untuk melaporkan seberapa sering alat ini dipakai, halaman mengirim hitungan anonim ke GoatCounter (tanpa cookie): bahwa pemeriksaan dimulai, bahwa pemeriksaan selesai beserta tingkat hasilnya (misalnya “kerja paksa”) dan apakah menyangkut Indonesia atau luar negeri, serta apakah lembar hasil dicetak atau diunduh. Tidak ada jawaban, negara, atau penanda identitas yang dikirim.'))

MAIN = '''<main id="trafficking-check" data-noi18n style="padding: 64px 0 40px">
<div class="tc">
<p class="tc-eye">%s</p>
<h1 class="tc-h1" style="margin: 14px 0 0; font-weight: 400; font-size: 52px; line-height: 1.1">%s</h1>
<p style="margin: 18px 0 0; max-width: 820px">%s</p>
<button type="button" class="tc-exit" id="tc-exit">%s</button>
<div id="tc-app" aria-live="polite"><noscript><p>%s</p></noscript></div>
%s
<p style="margin: 40px 0 0; font-size: 16px"><a href="/legal-help/">%s</a> · <a href="/legal-clinic/">%s</a> · <a href="/court-decisions/">%s</a></p>
</div>
</main>
<script src="/legal-clinic/trafficking-check/tc-data.js" defer></script>
<script src="/legal-clinic/trafficking-check/tc.js" defer></script>''' % (
LL('Legal Clinic · Self-check', 'Klinik Hukum · Periksa sendiri'),
LL('Could this be human trafficking?', 'Apakah ini perdagangan orang?'),
LL('A private check for migrant workers and their families. Answer short questions, one at a time, and get a result sheet you can print or save: what the law looks for, which laws apply in Indonesia and abroad, what could follow in law, and similar court decisions.',
   'Pemeriksaan rahasia untuk pekerja migran dan keluarganya. Jawab pertanyaan singkat satu per satu, lalu dapatkan lembar hasil yang bisa dicetak atau disimpan: apa yang dicari hukum, hukum mana yang berlaku di Indonesia dan di luar negeri, apa akibat hukumnya, dan putusan pengadilan yang serupa.'),
LL('Leave this page quickly', 'Tinggalkan halaman ini'),
LL('This check needs JavaScript. You can still <a href="/legal-help/">find free legal help</a>.', 'Pemeriksaan ini memerlukan JavaScript. Anda tetap bisa <a href="/legal-help/">mencari bantuan hukum gratis</a>.'),
METHOD,
LL('Find free legal help', 'Cari bantuan hukum gratis'), LL('Prepare a rights communication', 'Siapkan pengaduan hak'), LL('Court Decisions', 'Putusan Pengadilan'))

s = SRC
s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, s, count=1)
s = s.replace('What works where · Legal Clinic · Institute for Migrant Rights', TITLE)
old_desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
s = s.replace(old_desc, DESC)
s = s.replace('https://theimr.org/legal-clinic/what-works/', URL)
# page CSS: replace what-works block
a = s.index('<style>\nhtml[lang="id"] .en'); b = s.index('</style>', a) + 8
s = s[:a] + '<style id="tc-css">' + CSS + '</style>' + s[b:]
ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Could this be human trafficking? A self-check", "url": URL, "description": DESC,
      "applicationCategory": "LegalService", "operatingSystem": "Any", "inLanguage": ["en", "id"], "isAccessibleForFree": True, "dateModified": "2026-11-14",
      "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
      "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"}}
s = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False), s, count=1, flags=re.S)
a = s.index('<main'); b = s.index('</main>') + 7
s = s[:a] + MAIN + s[b:]
s = s.replace(' aria-current="page"', '')
os.makedirs(SITE + '/legal-clinic/trafficking-check', exist_ok=True)
open(SITE + '/legal-clinic/trafficking-check/index.html', 'w', encoding='utf-8').write(s)
print('page written', len(s))

# sitemap + llms.txt (idempotent)
sm = open(SITE + '/sitemap.xml', encoding='utf-8').read()
if URL not in sm:
    sm = sm.replace('</urlset>', '  <url><loc>%s</loc><lastmod>2026-11-14</lastmod></url>\n</urlset>' % URL)
    open(SITE + '/sitemap.xml', 'w', encoding='utf-8').write(sm)
lt = open(SITE + '/llms.txt', encoding='utf-8').read()
if URL not in lt:
    line = '- [Could this be human trafficking? A self-check](%s): rule-based check of a situation against the Palermo Protocol (act, means, purpose), the ILO forced labor test, Indonesian law and 14 destination countries\' laws, with a printable result sheet. Nothing is stored.\n' % URL
    i = lt.index('- [What works where]')
    lt = lt[:i] + line + lt[i:]
    open(SITE + '/llms.txt', 'w', encoding='utf-8').write(lt)
