"""Writes /domestic-workers/index.html and dw-i18n.js from the Countries of Origin page shell. Run: python3 build_page.py SITE_DIR"""
import json, os, re, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/theimr-site"
OUT = os.path.join(SITE, "domestic-workers")
T = {}
def t(en, id_):
    T[en] = id_; return en

tpl = open(os.path.join(SITE, "countries-of-origin", "index.html"), encoding="utf-8").read()
head, rest = tpl.split("<main", 1)
tail = rest.split("</main>", 1)[1]

TITLE = "Migrant domestic workers"
DESC = ("International, regional, bilateral and national law on migrant domestic workers compared: 115 instruments and 44 jurisdictions coded "
        "on 17 provisions of the ILO Domestic Workers Convention (C189) and 8 duties of countries of origin, with comparison, corridor, timeline, statistics and downloads.")
head = re.sub(r"<title>.*?</title>", "<title>%s · Institute for Migrant Rights</title>" % TITLE, head)
head = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + DESC, head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + DESC, head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>%s · Institute for Migrant Rights" % TITLE, head)
head = head.replace("https://theimr.org/countries-of-origin/", "https://theimr.org/domestic-workers/")
head = re.sub(r'(<meta name="keywords" content=")[^"]*', r"\g<1>migrant domestic workers, domestic work, ILO C189, Domestic Workers Convention, kafala, live-in care work, recruitment fees, bilateral labor agreements, comparative labor law, empirical legal studies, empirical legal scholarship, quantitative legal research, statistical analysis in law, law and economics, socio-legal studies, Global South, open data, replication data", head)
ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Migrant domestic workers: international, regional and national law compared",
      "alternateName": "IMR migrant domestic workers database", "description": DESC, "url": "https://theimr.org/domestic-workers/",
      "license": "https://creativecommons.org/licenses/by/4.0/", "version": "1.3", "dateModified": "2026-11-11", "inLanguage": ["en", "id"],
      "creator": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
      "keywords": ["migrant domestic workers", "ILO C189", "comparative labor law", "empirical legal studies", "recruitment fees", "bilateral labor agreements"],
      "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "https://theimr.org/domestic-workers/data/" + f} for f in ["codings.csv", "codebook.csv", "instruments.csv", "treaty-status.csv"]]}
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", head, flags=re.S)
head = head.replace('<a href="/countries-of-origin/" aria-current="page">Countries of Origin</a>', '<a href="/countries-of-origin/">Countries of Origin</a>')
head = head.replace("</style>", """.g-bench{font-family:'JetBrains Mono',monospace;font-size:11px;color:#3D5A4D;font-weight:400}
.g-reg td{background:#DCE8E1;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#2E493D;padding:6px 12px}
.g-dot{color:#1E6B4A;font-weight:700;margin-left:3px}
.g-ev{display:inline-block;margin-left:4px;padding:0 5px;border:1px solid #8A9C92;border-radius:2px;font:500 11px/1.5 'JetBrains Mono',monospace;color:#3D5A4D;vertical-align:1px}.g-ev.p{border-color:#1E6B4A;color:#1E6B4A}
.g-small{font-size:14.5px;line-height:1.45;color:#2E493D}.g-src{font-family:'JetBrains Mono',monospace;font-size:12px;color:#3D5A4D}
.g-list{margin:4px 0 0;padding-left:20px;font-size:16px}.g-list li{margin:0 0 8px}
.g-btn.sm{min-height:40px;font-size:15px;padding:0 12px}.g-btn:disabled{opacity:.4;cursor:not-allowed}
.g-grid3{display:grid;grid-template-columns:1fr 1.1fr 1fr;gap:24px}
.g-c189r{display:grid;grid-template-columns:minmax(220px,300px) 1fr;gap:14px;align-items:center;margin:0 0 8px;font-size:15px}
.g-stack .p-no{background:#FFFFFF}.g-stack span{display:flex;align-items:center;justify-content:center;font:500 12px 'JetBrains Mono',monospace}
.g-hist{display:flex;align-items:flex-end;gap:3px;height:140px;border-bottom:1px solid #172D24;margin:0 0 26px}
.g-hcol{flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;position:relative}
.g-hbar{display:block;background:#1E6B4A;min-height:0}.g-hlab{position:absolute;top:100%;left:0;font:400 11px 'JetBrains Mono',monospace;color:#3D5A4D;padding-top:4px}
.g-tl li.intl::before{background:#172D24}.g-tl li.reg::before{background:#1E6B4A;border-color:#1E6B4A}.g-tl li.bil::before{background:#C79A16;border-color:#C79A16}
.g-tools .wide{grid-column:span 2}
#g-glance{min-width:1500px}#g-gorig #g-glance{min-width:900px}#g-ctable{min-width:760px}#g-itable{min-width:900px}#g-ttable{min-width:900px}
@media (max-width:900px){.g-grid3{grid-template-columns:1fr}.g-c189r{grid-template-columns:1fr;gap:2px}.g-tools .wide{grid-column:span 2}}
</style>""")
FIG = open(os.path.join(SITE, "legal-clinic", "how-we-work", "index.html"), encoding="utf-8").read()
FIG = '<figure class="imr-band"' + FIG.split('<figure class="imr-band"', 1)[1].split("</figure>", 1)[0] + "</figure>"
head = re.sub(r'<figure class="imr-band".*?</figure>', lambda m: FIG, head, flags=re.S)

AI = '<p class="imr-ai-note" style="margin:0 0 20px;max-width:820px;font-size:16px;line-height:1.55;color:#2E493D"><b>Use of AI:</b> AI is used to re-confirm that none of the data we use infringes intellectual property law, to test our labels and to edit summaries into plain language, which people then re-edit. <a href="/ai-use/">How we use AI</a></p>'

def sec(i, n, eye, h2, lead, body):
    return '\n<section class="g-sec" id="%s">\n<p class="g-eye">%s</p>\n<h2>%s</h2>\n%s%s\n</section>\n' % (i, t(n + " · " + eye, n + " · " + eye_id[eye]), t(h2[0], h2[1]), ('<p class="g-lead">%s</p>\n' % t(lead[0], lead[1])) if lead else "", body)
eye_id = {"AT A GLANCE": "SEKILAS", "SIDE BY SIDE": "BERDAMPINGAN", "BUILD YOUR OWN COMPARISON": "SUSUN PERBANDINGAN SENDIRI", "C189 PROVISION MAP": "PETA KETENTUAN C189",
          "COUNTRY PROFILES": "PROFIL NEGARA", "CORRIDORS": "KORIDOR", "INSTRUMENTS": "INSTRUMEN", "TIMELINE": "LINIMASA", "TREATY STATUS": "STATUS TRAKTAT",
          "EXPLORE THE DATA": "JELAJAHI DATA", "METHOD AND CITATION": "METODE DAN SITASI", "FROM RESEARCH TO PRACTICE": "DARI RISET KE PRAKTIK", "SOURCES AND DOWNLOADS": "SUMBER DAN UNDUHAN"}
TOC = [("glance", "At a glance", "Sekilas"), ("compare", "Side by side", "Berdampingan"), ("score", "Your own comparison", "Perbandingan Anda"), ("c189", "C189 map", "Peta C189"),
       ("profiles", "Country profiles", "Profil negara"), ("corridors", "Corridors", "Koridor"), ("instruments", "Instruments", "Instrumen"), ("timeline", "Timeline", "Linimasa"),
       ("treaties", "Treaty status", "Status traktat"), ("analyze", "Explore the data", "Jelajahi data"), ("methods", "Method and citation", "Metode dan sitasi"),
       ("help", "From research to practice", "Dari riset ke praktik"), ("sources", "Sources and downloads", "Sumber dan unduhan")]

main = '<main style="padding: 64px 0 88px">\n<div class="g-wrap">\n<p class="g-eye">%s</p>\n<h1 class="g-h1">%s</h1>\n<p class="g-lede">%s</p>\n<p class="g-lede">%s</p>\n<ul class="g-toc">%s</ul>\n' % (
    "MIGRATION AND LABOR LAWS IN COMPARISON", t(TITLE, "Pekerja rumah tangga migran"),
    t("Domestic work is one of the largest occupations for women who migrate, and for decades it was left outside labor law in most countries. The ILO Domestic Workers Convention of 2011 (C189) set the first international standard. This database brings together the international, regional, bilateral and national instruments that govern migrant domestic work, and codes the law of 34 countries of destination and 10 countries of origin on the questions those standards ask.",
      "Kerja rumah tangga adalah salah satu pekerjaan terbesar bagi perempuan yang bermigrasi, dan selama puluhan tahun berada di luar hukum ketenagakerjaan di sebagian besar negara. Konvensi ILO tentang Pekerja Rumah Tangga tahun 2011 (C189) menetapkan standar internasional pertama. Basis data ini menghimpun instrumen internasional, kawasan, bilateral dan nasional yang mengatur kerja rumah tangga migran, serta mengodekan hukum 34 negara tujuan dan 10 negara asal pada pertanyaan-pertanyaan yang diajukan standar tersebut."),
    t("Version 1.3 is a working draft. The UAE, Saudi Arabia and Oman entries and Bahrain's recruitment rules are coded from the legal texts (marked P); the other cells come from secondary sources and are marked S until they are checked against the official texts.",
      "Versi 1.3 adalah draf kerja. Entri UEA, Arab Saudi dan Oman serta aturan rekrutmen Bahrain dikodekan dari teks hukum (ditandai P); sel lain berasal dari sumber sekunder dan ditandai S sampai dicocokkan dengan teks resmi."),
    "".join('<li><a href="#%s">%s</a></li>' % (a, t(b, c)) for a, b, c in TOC))

R = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]
main += sec("glance", R[0], "AT A GLANCE", ("What the law provides, provision by provision", "Apa yang diatur hukum, ketentuan demi ketentuan"),
  ("For countries of destination, each column is a provision of C189, the standard the convention sets for every domestic worker; for countries of origin, each column is a duty that international law places on the state workers leave from. Select a cell to see the note and the source.",
   "Untuk negara tujuan, setiap kolom adalah satu ketentuan C189, standar yang ditetapkan konvensi bagi setiap pekerja rumah tangga; untuk negara asal, setiap kolom adalah kewajiban yang dibebankan hukum internasional kepada negara yang ditinggalkan pekerja. Pilih sel untuk melihat catatan dan sumbernya."),
  '<div class="g-btns" id="g-gview" role="group" data-noi18n></div>\n<div class="g-scroll"><table class="g-t" id="g-glance" data-noi18n></table></div>\n<div class="g-legend" id="g-legend" data-noi18n></div>\n<div id="g-cellnote" data-noi18n></div>')
main += sec("compare", R[1], "SIDE BY SIDE", ("Compare up to four countries", "Bandingkan hingga empat negara"),
  ("Pick countries to read their rules next to each other, with the note and source for every cell.", "Pilih negara untuk membaca aturannya berdampingan, dengan catatan dan sumber untuk setiap sel."),
  '<div class="g-btns" id="g-cview" role="group" data-noi18n></div>\n<div class="g-btns" id="g-cpick" role="group" data-noi18n></div>\n<p class="g-note" id="g-cmsg" data-noi18n></p>\n<div class="g-scroll"><table class="g-t" id="g-ctable" data-noi18n></table></div>')
main += sec("score", R[2], "BUILD YOUR OWN COMPARISON", ("Weigh the provisions that matter for your question", "Timbang ketentuan yang penting bagi pertanyaan Anda"),
  ("There is no default ranking. Move the sliders to give weight to the provisions your question is about, and a comparison of the destinations appears. Each provision counts 2 when the law meets the benchmark, 1 when it does so in part and 0 when it does not.",
   "Tidak ada peringkat bawaan. Geser penggeser untuk memberi bobot pada ketentuan yang menjadi pokok pertanyaan Anda, lalu perbandingan negara tujuan akan muncul. Setiap ketentuan bernilai 2 bila hukum memenuhi tolok ukur, 1 bila sebagian dan 0 bila tidak."),
  '<div class="g-btns"><button type="button" class="g-btn" id="g-wequal">%s</button><button type="button" class="g-btn" id="g-wreset">%s</button></div>\n<div class="g-w" id="g-weights" data-noi18n></div>\n<div class="g-bars" id="g-rank" data-noi18n></div>\n<p class="g-note" id="g-rank-note" data-noi18n></p>\n<details id="g-robust-d" style="margin-top:22px"><summary style="cursor:pointer;font-weight:500">%s</summary>\n<div class="g-scroll" style="margin-top:10px"><table class="g-t" id="g-robust" data-noi18n></table></div>\n<p class="g-note">%s</p></details>' % (
    t("Weigh all equally", "Beri bobot sama"), t("Clear all weights", "Hapus semua bobot"), t("Check how stable any ranking is: 10,000 random weightings", "Periksa seberapa stabil peringkat: 10.000 pembobotan acak"),
    t("Each weighting draws every weight uniformly between 0 and 3 (fixed seed, so the result is reproducible). A country that scores highest under most weightings does so whatever one values; a split result means the comparison depends on the weights.",
      "Setiap pembobotan menarik setiap bobot secara seragam antara 0 dan 3 (benih tetap, sehingga hasilnya bisa diulang). Negara yang skornya tertinggi pada sebagian besar pembobotan unggul apa pun yang dianggap penting; hasil yang terbagi berarti perbandingan bergantung pada bobot.")))
main += sec("c189", R[3], "C189 PROVISION MAP", ("Which provisions of C189 are most and least reflected in national law", "Ketentuan C189 mana yang paling banyak dan paling sedikit tercermin dalam hukum nasional"),
  ("The map counts, for each provision, how many of the destinations meet the benchmark, meet it in part or do not provide for it.", "Peta ini menghitung, untuk setiap ketentuan, berapa banyak negara tujuan yang memenuhi tolok ukur, memenuhinya sebagian, atau tidak mengaturnya."),
  '<div id="g-c189" data-noi18n></div>\n<div class="g-legend" id="g-c189leg" data-noi18n></div>\n<p class="g-note" id="g-c189note" data-noi18n></p>')
main += sec("profiles", R[4], "COUNTRY PROFILES", ("Each country in detail", "Setiap negara secara rinci"), None,
  '<div class="g-btns" id="g-states" role="group" data-noi18n></div>\n<div id="g-profile" data-noi18n></div>')
main += sec("corridors", R[5], "CORRIDORS", ("Follow the law along a migration corridor", "Ikuti hukum di sepanjang koridor migrasi"),
  ("A domestic worker who moves is governed by two legal orders and often by an agreement between them. Choose a country of origin and a country of destination to see the rules before departure, the instruments that link the two, and the rules at work.",
   "Pekerja rumah tangga yang berpindah diatur oleh dua tatanan hukum dan sering oleh perjanjian di antara keduanya. Pilih negara asal dan negara tujuan untuk melihat aturan sebelum berangkat, instrumen yang menghubungkan keduanya, dan aturan di tempat kerja."),
  '<div class="g-tools" style="grid-template-columns:1fr 1fr"><label>%s<select id="g-co" data-noi18n></select></label><label>%s<select id="g-cd" data-noi18n></select></label></div>\n<div id="g-corr" data-noi18n></div>' % (t("Country of origin", "Negara asal"), t("Country of destination", "Negara tujuan")))
main += sec("instruments", R[6], "INSTRUMENTS", ("All instruments, with filters and search", "Semua instrumen, dengan penyaring dan pencarian"),
  ("Treaties, recommendations, interpretations by treaty bodies, regional instruments, bilateral agreements and national laws. Filter by level, region, kind, topic or binding force, or search the titles, summaries and coded notes.",
   "Traktat, rekomendasi, tafsir badan traktat, instrumen kawasan, perjanjian bilateral dan hukum nasional. Saring menurut tingkat, kawasan, jenis, topik atau daya ikat, atau cari di judul, ringkasan dan catatan kode."),
  '<div class="g-tools" id="g-ftools" data-noi18n></div>\n<p class="g-mono" id="g-icount" data-noi18n></p>\n<div class="g-scroll"><table class="g-t" id="g-itable" data-noi18n></table></div>\n<div id="g-nhits" data-noi18n></div>')
main += sec("timeline", R[7], "TIMELINE", ("When the instruments were adopted", "Kapan instrumen-instrumen itu diadopsi"),
  ("Most instruments specific to domestic work date from after 2008, when the ILO placed the subject on its agenda; national reforms cluster after C189 was adopted in 2011.", "Sebagian besar instrumen khusus kerja rumah tangga berasal dari setelah 2008, ketika ILO memasukkan topik ini ke agendanya; reformasi nasional berkumpul setelah C189 diadopsi pada 2011."),
  '<div class="g-btns" id="g-tfilter" role="group" data-noi18n></div>\n<div id="g-hist" data-noi18n></div>\n<details><summary style="cursor:pointer;font-weight:500">%s</summary>\n<ul class="g-tl" id="g-tl" style="margin-top:14px" data-noi18n></ul></details>' % t("Show every instrument in order of adoption", "Tampilkan semua instrumen menurut urutan adopsi"))
main += sec("treaties", R[8], "TREATY STATUS", ("Which treaties each country has joined", "Traktat yang telah diikuti tiap negara"),
  ("Ratifications of C181, C190, the Forced Labour Protocol, the UN Migrant Workers Convention and ICESCR come from the ILO and UN records collected on 30 October 2026. C189, C97 and C143 were checked on the ILO NORMLEX database on 11 November 2026.",
   "Ratifikasi C181, C190, Protokol Kerja Paksa, Konvensi Pekerja Migran PBB dan ICESCR berasal dari catatan ILO dan PBB yang dihimpun pada 30 Oktober 2026. C189, C97 dan C143 diperiksa pada basis data NORMLEX ILO pada 11 November 2026."),
  '<div class="g-scroll"><table class="g-t" id="g-ttable" data-noi18n></table></div>\n<p class="g-note" id="g-tkey" data-noi18n></p>')
main += sec("analyze", R[9], "EXPLORE THE DATA", ("Ask your own questions of the data", "Ajukan pertanyaan Anda sendiri pada data"),
  ("Compare groups, look for associations or fit a simple model across the destinations, with plain explanations of each result. Every row is a jurisdiction, so the sample is small: the tools describe these countries and do not test causes.",
   "Bandingkan kelompok, cari keterkaitan atau susun model sederhana antarnegara tujuan, dengan penjelasan sederhana untuk setiap hasil. Setiap baris adalah satu yurisdiksi, jadi sampelnya kecil: alat ini menggambarkan negara-negara tersebut dan tidak menguji sebab-akibat."),
  '<div id="g-stats"></div>')
main += '\n<section class="g-sec" id="methods">\n<p class="g-eye">%s</p>\n<h2>%s</h2>\n%s\n<p class="g-lead">%s</p>\n<div class="g-scroll" style="margin-bottom:18px"><table class="g-t" id="g-prov" data-noi18n></table></div>\n<h3 style="font-weight:500;font-size:24px;margin:24px 0 8px">%s</h3>\n<div class="g-scroll"><table class="g-t" id="g-cbd" data-noi18n></table></div>\n<h3 style="font-weight:500;font-size:24px;margin:24px 0 8px">%s</h3>\n<div class="g-scroll"><table class="g-t" id="g-cbo" data-noi18n></table></div>\n<ul style="max-width:820px">%s</ul>\n<h3 style="font-weight:500;font-size:24px;margin:32px 0 8px">%s</h3>\n<p class="g-mono" id="g-cite" data-noi18n></p>\n</section>\n' % (
  t(R[10] + " · METHOD AND CITATION", R[10] + " · METODE DAN SITASI"), t("How the data was built", "Bagaimana data disusun"), AI,
  t("The unit of analysis is the law in force for migrant domestic workers in each jurisdiction, on paper (de jure), as of the date shown. Statutes, regulations, binding standard contracts and collective agreements are coded; practice is not. Each cell records a value, a note, the provision relied on and whether it rests on the official text (P) or on a secondary source (S). Benchmarks are the provisions of C189 for destinations and of ICRMW, CMW General Comment No. 1 and CEDAW General Recommendation No. 26 for origins. A higher value means the rule is closer to the benchmark, not that a country is a better place to work.",
    "Unit analisisnya adalah hukum yang berlaku bagi pekerja rumah tangga migran di setiap yurisdiksi, di atas kertas (de jure), per tanggal yang tertera. Undang-undang, peraturan, kontrak standar yang mengikat dan perjanjian kerja bersama dikodekan; praktiknya tidak. Setiap sel mencatat nilai, catatan, ketentuan yang dirujuk dan apakah sel itu bertumpu pada teks resmi (P) atau sumber sekunder (S). Tolok ukurnya adalah ketentuan C189 untuk negara tujuan, serta ICRMW, Komentar Umum CMW No. 1 dan Rekomendasi Umum CEDAW No. 26 untuk negara asal. Nilai lebih tinggi berarti aturan lebih dekat ke tolok ukur, bukan bahwa suatu negara tempat kerja yang lebih baik."),
  t("Codebook: countries of destination", "Buku kode: negara tujuan"), t("Codebook: countries of origin", "Buku kode: negara asal"),
  "".join("<li>%s</li>" % t(a, b) for a, b in [
    ("Sources: the UAE entry is coded from the official English translation of Federal Decree-Law No. 9 of 2022, Saudi Arabia from the Domestic Workers Regulation (Ministerial Decision 40676/1445), Oman from Ministerial Decision No. 574 of 2025 (Official Gazette No. 1617) and Bahrain's recruitment-fee rule from the official English text of Law No. 19 of 2006. The official legislation databases of the other countries could not be reached from our collection server, so their article numbers and positions come from secondary sources and must be checked against the official texts; the check is under way.",
     "Sumber: entri UEA dikodekan dari terjemahan resmi bahasa Inggris Dekret-Undang-Undang Federal No. 9 Tahun 2022, Arab Saudi dari Peraturan Pekerja Rumah Tangga (Keputusan Menteri 40676/1445), Oman dari Keputusan Menteri No. 574 Tahun 2025 (Lembaran Negara No. 1617) dan aturan biaya rekrutmen Bahrain dari teks resmi bahasa Inggris Undang-Undang No. 19 Tahun 2006. Basis data perundang-undangan resmi negara lain tidak bisa dijangkau dari server pengumpul kami, sehingga nomor pasal dan posisinya berasal dari sumber sekunder dan harus dicocokkan dengan teks resmi; pemeriksaan sedang berjalan."),
    ("Federal and sub-national systems: the United States is coded at federal level and Canada with Ontario as the reference province; state and provincial law can be more protective.",
     "Sistem federal dan subnasional: Amerika Serikat dikodekan pada tingkat federal dan Kanada dengan Ontario sebagai provinsi acuan; hukum negara bagian dan provinsi bisa lebih melindungi."),
    ("Background literature (not used to code current law, which has changed since): Antoinette Vlieger, Domestic Workers in Saudi Arabia and the Emirates: A Socio-Legal Study on Conflicts (Quid Pro Books, 2013); Maysa Zahra, The Legal Framework of the Sponsorship Systems of the Gulf Cooperation Council Countries: A Comparative Examination (GLMM Explanatory Note 10/2015).",
     "Literatur latar (tidak dipakai untuk mengodekan hukum yang berlaku sekarang, yang sudah berubah): Antoinette Vlieger, Domestic Workers in Saudi Arabia and the Emirates: A Socio-Legal Study on Conflicts (Quid Pro Books, 2013); Maysa Zahra, The Legal Framework of the Sponsorship Systems of the Gulf Cooperation Council Countries: A Comparative Examination (GLMM Explanatory Note 10/2015)."),
    ("A blank cell means the position could not yet be determined; it is left out of the comparison rather than counted as zero.",
     "Sel kosong berarti posisinya belum bisa ditentukan; sel itu tidak dihitung dalam perbandingan, bukan dianggap nol."),
    ("Reliability: one coder applied the rules to all 658 cells. A second, independent coding against the official texts is planned, with agreement reported as Cohen's kappa.",
     "Keandalan: satu pengode menerapkan aturan pada 658 sel. Pengodean kedua yang independen terhadap teks resmi direncanakan, dengan kesepakatan dilaporkan sebagai kappa Cohen."),
    ("Any weighted comparison depends on the weights chosen; the stability check shows how often each country scores highest across 10,000 random weightings.",
     "Setiap perbandingan berbobot bergantung pada bobot yang dipilih; uji stabilitas menunjukkan seberapa sering tiap negara mendapat skor tertinggi pada 10.000 pembobotan acak.")]),
  t("How to cite", "Cara mengutip"))
main += sec("help", R[11], "FROM RESEARCH TO PRACTICE", ("From research to practice", "Dari riset ke praktik"),
  ("Free legal help and a way to bring a complaint, for domestic workers and the people who support them.", "Bantuan hukum gratis dan cara mengajukan pengaduan, bagi pekerja rumah tangga dan orang-orang yang mendampingi mereka."),
  '<div class="g-grid2">\n<div class="g-card"><h3>%s</h3><p>%s</p><div class="g-acts"><a href="/legal-help/?country=ID">Indonesia</a><a href="/legal-help/?country=PH">%s</a><a href="/legal-help/">%s</a></div></div>\n<div class="g-card"><h3>%s</h3><p>%s</p><div class="g-acts"><a href="/legal-clinic/">%s</a><a href="/court-decisions/">%s</a></div></div>\n</div>' % (
    t("Free legal help", "Bantuan hukum gratis"), t("Organizations in countries of origin and destination, with phone numbers we have checked.", "Organisasi di negara asal dan tujuan, dengan nomor telepon yang sudah kami periksa."),
    t("Philippines", "Filipina"), t("All countries", "Semua negara"), t("Courts and complaints", "Pengadilan dan pengaduan"),
    t("Bring a complaint to a human rights body through our Legal Clinic, or read how courts have decided cases about migrant workers.", "Ajukan pengaduan ke badan hak asasi manusia melalui Klinik Hukum kami, atau baca bagaimana pengadilan memutus perkara tentang pekerja migran."),
    t("Open the Legal Clinic", "Buka Klinik Hukum"), t("Court decisions", "Putusan pengadilan")))
main += sec("sources", R[12], "SOURCES AND DOWNLOADS", ("Sources and downloads", "Sumber dan unduhan"), None,
  '<div class="g-btns" id="g-dls" data-noi18n></div>\n<p class="g-note">%s <a href="data/codings.csv">%s</a> · <a href="data/codebook.csv">%s</a> · <a href="data/instruments.csv">%s</a> · <a href="data/treaty-status.csv">%s</a>%s</p>\n<p class="g-mono" id="g-ver" data-noi18n></p>\n<p class="g-note">%s <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.</p>' % (
    t("Static CSV files:", "Berkas CSV statis:"), t("Coded cells with notes and sources", "Sel terkode dengan catatan dan sumber"), t("Codebook", "Buku kode"), t("Instruments", "Instrumen"), t("Treaty status", "Status traktat"),
    t(". Licensed CC BY 4.0.", ". Berlisensi CC BY 4.0."),
    t("This page summarizes laws for research and advocacy. It is not legal advice. Found a mistake? Write to", "Halaman ini merangkum hukum untuk riset dan advokasi. Ini bukan nasihat hukum. Menemukan kesalahan? Tulis ke")))
main += "</div>\n"

tail = tail.replace('<script src="oc-data.js" defer></script>\n<script src="oc.js" defer></script>\n<script src="oc-i18n.js" defer></script>',
                    '<script src="dw-data.js" defer></script>\n<script src="dw.js" defer></script>\n<script src="dw-i18n.js" defer></script>')
assert "dw-i18n.js" in tail
tail = tail.replace("emigration policy; countries of origin; recruitment regulation; remittances; diaspora policy; bilateral labor agreements;", "migrant domestic workers; domestic work; ILO C189; kafala; live-in care work; recruitment fees; bilateral labor agreements;")
tail = tail.replace("the rights of migrant workers, as well as for advocacy.", "the rights of migrant domestic workers, as well as for advocacy.")
tail = tail.replace("how recruitment fees, wage protection and limits on changing employer affect migrant workers.", "how coverage by labor law, recruitment fees and limits on changing employer relate to the conditions of migrant domestic workers.")
html = head + main + "</main>" + tail
html = html.replace('<a href="/countries-of-origin/">Countries of Origin</a>\n', '<a href="/countries-of-origin/">Countries of Origin</a>\n<a href="/domestic-workers/" aria-current="page">Migrant Domestic Workers</a>\n', 1)
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)

T.update({"MIGRATION AND LABOR LAWS IN COMPARISON": "PERBANDINGAN HUKUM MIGRASI DAN KETENAGAKERJAAN", "Migrant Domestic Workers": "Pekerja Rumah Tangga Migran",
          "Use of AI:": "Penggunaan AI:"})
js = """/* Indonesian strings for the Migrant domestic workers page. Loaded just before /assets/lang.js (same pattern as oc-i18n.js). */
(function () {
  var A = %s;
  function merge(D) { D.id = D.id || {}; for (var k in A) if (!Object.prototype.hasOwnProperty.call(D.id, k)) D.id[k] = A[k]; return D; }
  if (window.SITE_I18N) { merge(window.SITE_I18N); return; }
  var cur;
  try { Object.defineProperty(window, "SITE_I18N", {configurable: true, enumerable: true, get: function () { return cur; }, set: function (v) { cur = merge(v || {}); }}); }
  catch (e) { window.SITE_I18N = merge({}); }
})();
""" % json.dumps({k.replace(" ", " "): v for k, v in T.items()}, ensure_ascii=False, indent=0)
open(os.path.join(OUT, "dw-i18n.js"), "w", encoding="utf-8").write(js)
shutil.copy(os.path.join(HERE, "dw.js"), os.path.join(OUT, "dw.js"))
print("page written,", len(T), "strings")
