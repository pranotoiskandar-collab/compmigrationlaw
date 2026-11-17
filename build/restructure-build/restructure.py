# Site restructure (oto, 2026-11-13): "Migration Jurisprudence from the South" is the umbrella name of the whole
# databases project. One menu replaces "Projects" + "Migration and Labor Laws in Comparison", in five groups:
#   Law across tiers (Migration Law Atlas, incl. farmworker view) / Destination states (Gulf, East Asia, Southeast Asia)
#   / Origin states (Countries of Origin) / Themes (Domestic Workers, Government Hate Speech) / Courts (Court Decisions)
# - /hate-speech-voting/ moves to /government-hate-speech/elections/ (part of Government Hate Speech)
# - /atlas/ page is retired: /migration-law/?lens=farm opens the Atlas in the farmworker view (/atlas/data/ CSVs stay)
# - /court-decisions/ is renamed "Court Decisions" (URL unchanged)
# - "Journal" top link dropped (it is a section of Publications)
# Usage: python3 restructure.py SITE_DIR      Safe to rerun; rerun after any page rebuild (like analytics.py).
import os, re, sys, json, glob, shutil, subprocess
SITE = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/theimr-site'
HERE = os.path.dirname(os.path.abspath(__file__))
MJS = 'Migration Jurisprudence from the South'
ELEC = '/government-hate-speech/elections/'
FARM = '/migration-law/?lens=farm'
def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s): open(p, 'w', encoding='utf-8').write(s)
def files(*ext):
    for p in glob.glob(SITE + '/**/*', recursive=True):
        if os.path.isfile(p) and p.endswith(ext): yield p
ID = {}

# ---------- 1. move pages ----------
old, new = SITE + '/hate-speech-voting', SITE + ELEC.rstrip('/')
if os.path.exists(old + '/index.html'):
    if os.path.exists(new): shutil.rmtree(new)
    shutil.move(old, new); print('moved hate-speech-voting ->', ELEC)
if os.path.isdir(old) and not os.listdir(old): os.rmdir(old)
if os.path.exists(SITE + '/atlas/index.html'):
    os.remove(SITE + '/atlas/index.html'); print('removed atlas/index.html (data/ kept)')

# ---------- 2. sitemap: drop retired URLs before links are rewritten ----------
sm = rd(SITE + '/sitemap.xml')
sm = re.sub(r'\s*<url><loc>https://theimr.org/atlas/</loc>.*?</url>', '', sm)
wr(SITE + '/sitemap.xml', sm)

# ---------- 3. links and names everywhere ----------
ATLAS = re.compile(r'(?<![\w-])/atlas/(?=["\'#)\s<])')
for p in files('.html', '.js', '.xml', '.txt', '.json'):
    if '/data/' in p: continue
    s = o = rd(p)
    s = s.replace('/hate-speech-voting/', ELEC)
    s = ATLAS.sub(FARM, s)
    # eyebrows
    s = s.replace('MIGRATION AND LABOR LAWS IN COMPARISON', MJS.upper())
    for x in ('PERBANDINGAN HUKUM MIGRASI DAN KETENAGAKERJAAN', 'HUKUM MIGRASI DAN KETENAGAKERJAAN DALAM PERBANDINGAN'):
        s = s.replace(x, 'YURISPRUDENSI MIGRASI DARI SELATAN')
    # Court Decisions = the court decisions database, inside the umbrella
    if '/court-decisions/' in p.replace(SITE, ''):
        s = re.sub(r'(?<!Court Decisions · )' + MJS + ' ·', 'Court Decisions · ' + MJS + ' ·', s)
    s = s.replace(MJS + ', version', MJS + ': Court Decisions, version')
    s = s.replace('Yurisprudensi Migrasi dari Selatan, versi', 'Yurisprudensi Migrasi dari Selatan: Putusan Pengadilan, versi')
    s = s.replace('<a href="/court-decisions/">' + MJS + '</a>', '<a href="/court-decisions/">Court Decisions</a>')
    s = s.replace('[' + MJS + '](https://theimr.org/court-decisions/)', '[Court Decisions](https://theimr.org/court-decisions/)')
    if '/court-decisions/' in p.replace(SITE, ''):
        s = s.replace('<h1 class="g-h1">' + MJS + '</h1>', '<h1 class="g-h1">Court Decisions</h1>')
        s = s.replace('"@type": "Dataset", "name": "' + MJS + '"', '"@type": "Dataset", "name": "Court Decisions"')
    s = s.replace(': Migration and Labor Laws in Comparison}', ', ' + MJS + '}')  # BibTeX titles
    # names of the moved/merged pages
    s = s.replace('<a href="' + ELEC + '">Hate Speech and Voting</a>', '<a href="' + ELEC + '">Government Hate Speech: elections and non-citizens</a>')
    s = s.replace('<a href="' + FARM + '">Farmworker Norms Atlas</a>', '<a href="' + FARM + '">Migration Law Atlas: farmworker law view</a>')
    s = s.replace('[Farmworker Norms Atlas](https://theimr.org' + FARM + ')', '[Migration Law Atlas, farmworker law view](https://theimr.org' + FARM + ')')
    s = s.replace('[Hate Speech and Voting](https://theimr.org' + ELEC + ')', '[Government Hate Speech: elections and non-citizens](https://theimr.org' + ELEC + ')')
    if s != o: wr(p, s)
ID.update({MJS.upper(): 'YURISPRUDENSI MIGRASI DARI SELATAN', 'Court Decisions': 'Putusan Pengadilan',
           'Government Hate Speech: elections and non-citizens': 'Ucapan Kebencian oleh Pemerintah: pemilu dan orang yang bukan warga negara',
           'Migration Law Atlas: farmworker law view': 'Atlas Hukum Migrasi: tampilan hukum buruh tani'})

# ---------- 4. Migration Law Atlas opens in the farmworker view with ?lens=farm ----------
p = SITE + '/migration-law/index.html'; s = rd(p)
s = s.replace('let LENS = "mig";', 'let LENS = /[?&]lens=farm\\b/.test(location.search) ? "farm" : "mig"; // /atlas/ redirects here with ?lens=farm')
wr(p, s)

# ---------- 5. plain-language boxes: the elections page keeps its own boxes ----------
p = SITE + '/assets/plain.js'; s = rd(p)
a = 'var page = (location.pathname.split("/").filter(Boolean)[0] || "").toLowerCase();'
if a in s:
    s = s.replace(a, 'var pp = location.pathname.split("/").filter(Boolean); var page = (pp[0] === "government-hate-speech" && pp[1] === "elections" ? "hate-speech-voting" : (pp[0] || "")).toLowerCase();')
    wr(p, s)

# ---------- 6. one umbrella menu ----------
SEA = os.path.exists(SITE + '/southeast-asia/index.html')
GROUPS = [('Law across tiers', [('/migration-law/', 'Migration Law Atlas'), (FARM, 'Farmworker law view')]),
          ('Destination states', [('/gcc/', 'Gulf States'), ('/east-asia/', 'East Asia')] + ([('/southeast-asia/', 'Southeast Asia')] if SEA else [])),
          ('Origin states', [('/countries-of-origin/', 'Countries of Origin')]),
          ('Themes', [('/domestic-workers/', 'Migrant Domestic Workers'), ('/government-hate-speech/', 'Government Hate Speech')]),
          ('Courts', [('/court-decisions/', 'Court Decisions')])]
ID.update({'Overview': 'Ikhtisar', 'Law across tiers': 'Hukum lintas tingkat', 'Farmworker law view': 'Tampilan hukum buruh tani',
           'Destination states': 'Negara tujuan', 'Origin states': 'Negara pengirim', 'Themes': 'Tema', 'Courts': 'Pengadilan',
           'Southeast Asia': 'Asia Tenggara', MJS: 'Yurisprudensi Migrasi dari Selatan'})
GH = "display:block;padding:12px 16px 2px;font:500 11px 'JetBrains Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#3D5A4C"
def menu(cur):
    def a(u, n, extra=''):
        c = ' aria-current="page"' if u == cur else ''
        return '<a href="%s"%s%s>%s</a>\n' % (u, c, extra, n)
    m = '<details data-imr-nav="mjs">\n<summary>%s</summary>\n<div class="menu" style="max-height:80vh;overflow-y:auto">\n' % MJS
    m += a('/databases/', 'Overview', ' style="font-weight:600"')
    for h, items in GROUPS:
        m += '<span style="%s">%s</span>\n' % (GH, h) + ''.join(a(u, n, ' style="padding-left:28px"' if u == FARM else '') for u, n in items)
    return m + '</div>\n</details>'
def current(p):
    r = '/' + os.path.relpath(p, SITE).replace('index.html', '')
    for u in ['/migration-law/', '/gcc/', '/east-asia/', '/southeast-asia/', '/countries-of-origin/', '/domestic-workers/',
              '/government-hate-speech/', '/court-decisions/', '/databases/']:
        if r.startswith(u): return u
    return None
OLD = re.compile(r'<details>\s*<summary[^>]*>Projects</summary>.*?</details>\s*<details>\s*<summary[^>]*>Migration and Labor Laws in Comparison</summary>.*?</details>', re.S)
NEW = re.compile(r'<details data-imr-nav="mjs">.*?</details>', re.S)
JOUR = re.compile(r'\n?<a href="/?publications\.html#journal"[^>]*>Journal</a>')
n = 0
for p in files('.html'):
    s = o = rd(p)
    if '<nav' not in s: continue
    s = OLD.sub(lambda m: menu(current(p)), s, count=1)
    s = NEW.sub(lambda m: menu(current(p)), s, count=1)
    i = s.find('<nav'); j = s.find('</nav>', i)
    if i >= 0 and j > 0: s = s[:i] + JOUR.sub('', s[i:j]) + s[j:]
    if s != o: wr(p, s); n += 1
print('menu updated on', n, 'pages')

# ---------- 6b. Legal Clinic menu: the practical parts of the site (oto, 2026-11-13) ----------
def ex(u): return os.path.exists(SITE + u.split('#')[0] + ('index.html' if u.split('#')[0].endswith('/') else ''))
CLIN = [(None, [('/legal-clinic/', 'Prepare a rights communication'), ('/legal-clinic/trafficking-check/', 'Could this be trafficking? Self-check'), ('/legal-clinic/how-we-work/', 'How the Clinic works'), ('/legal-help/', 'Find free legal help')]),
        ('Arguments that work', [('/legal-clinic/what-works/', 'What works where'), ('/court-decisions/#argument', 'Arguments courts accepted or rejected'), ('/court-decisions/#compare', 'Compare courts and countries')]),
        ('Where to take a case', [('/gcc/mechanisms/', 'Gulf States'), ('/east-asia/mechanisms/', 'East Asia'), ('/southeast-asia/mechanisms/', 'Southeast Asia')]),
        ('From research to practice', [('/gcc/#help', 'Gulf States'), ('/east-asia/#help', 'East Asia'), ('/southeast-asia/#help', 'Southeast Asia'),
                                       ('/countries-of-origin/#help', 'Countries of Origin'), ('/domestic-workers/#help', 'Migrant Domestic Workers'),
                                       (ELEC + '#help', 'Elections and non-citizens'), ('/government-hate-speech/#report', 'Report official hate speech')])]
ID.update({'Legal Clinic': 'Klinik Hukum', 'Prepare a rights communication': 'Siapkan pengaduan hak', 'How the Clinic works': 'Cara kerja Klinik',
           'Find free legal help': 'Cari bantuan hukum gratis', 'Could this be trafficking? Self-check': 'Apakah ini perdagangan orang? Periksa sendiri', 'What works where': 'Apa yang berhasil, dan di mana', 'Arguments that work': 'Argumen yang berhasil',
           'Arguments courts accepted or rejected': 'Argumen yang diterima atau ditolak pengadilan', 'Compare courts and countries': 'Bandingkan pengadilan dan negara',
           'Where to take a case': 'Ke mana membawa perkara', 'From research to practice': 'Dari riset ke praktik',
           'Elections and non-citizens': 'Pemilu dan orang yang bukan warga negara', 'Report official hate speech': 'Laporkan ucapan kebencian pejabat'})
def cmenu(cur):
    m = '<details data-imr-nav="clinic">\n<summary>Legal Clinic</summary>\n<div class="menu" style="left:0;right:auto;max-height:80vh;overflow-y:auto;min-width:290px">\n'
    for h, items in CLIN:
        items = [(u, n) for u, n in items if ex(u)]
        if not items: continue
        if h: m += '<span style="%s">%s</span>\n' % (GH, h)
        for u, n in items:
            st = ' style="font-weight:600"' if u == '/legal-clinic/' else ''
            m += '<a href="%s"%s%s>%s</a>\n' % (u, ' aria-current="page"' if u == cur else '', st, n)
    return m + '</div>\n</details>'
def ccur(p):
    r = '/' + os.path.relpath(p, SITE).replace('index.html', '')
    for u in ['/legal-clinic/how-we-work/', '/legal-clinic/what-works/', '/legal-clinic/trafficking-check/', '/legal-help/', '/gcc/mechanisms/', '/east-asia/mechanisms/', '/southeast-asia/mechanisms/', '/legal-clinic/']:
        if r.startswith(u): return u
    return None
COLD = re.compile(r'<a href="/?legal-clinic/"[^>]*>Legal Clinic</a>\s*<a href="/?legal-help/"[^>]*>Find legal help</a>')
CNEW = re.compile(r'<details data-imr-nav="clinic">.*?</details>', re.S)
n = 0
for p in files('.html'):
    s = o = rd(p)
    if '<nav' not in s: continue
    s = COLD.sub(lambda m: cmenu(ccur(p)), s, count=1)
    s = CNEW.sub(lambda m: cmenu(ccur(p)), s, count=1)
    if s != o: wr(p, s); n += 1
print('clinic menu updated on', n, 'pages')

# ---------- 7. Government Hate Speech: elections section + elections page header ----------
p = SITE + '/government-hate-speech/index.html'; s = rd(p)
s = s.replace('<p class="kicker">Projects · Research</p>', '<p class="kicker">%s</p>' % MJS)
if 'id="elections"' not in s:
    sec = ('<section id="elections" class="fold alt">\n<details>\n<summary class="wrap fsum"><p class="kicker blue">VIII · Elections and non-citizens</p>'
           '<h2>Hate speech, voting and the protection of non-citizens</h2><p class="teaser">Party hate speech, anti-immigration votes and impunity in 34 democracies.</p>'
           '<span class="chev" aria-hidden="true"></span></summary>\n<div class="fbody">\n<div class="narrow">\n'
           '<p style="margin: 28px 0 0">This part of the project asks whether countries whose law names non-citizens explicitly see less party hate speech and fewer votes for anti-immigration parties, and whether crimes against migrants are punished. It codes four features of domestic law in 34 democracies and sets them beside V-Dem, V-Party and OSCE ODIHR hate crime data. You can test your own questions and download the data.</p>\n'
           '<p style="margin: 24px 0 0"><a href="%s" style="font-weight: 600">Open the comparison of elections and non-citizens →</a></p>\n'
           '</div>\n</div>\n</details>\n</section>\n\n' % ELEC)
    s = s.replace('<section id="report" class="fold">', sec + '<section id="report" class="fold">', 1)
    s = s.replace('<a href="#evidence" class="pill">Statistics</a>', '<a href="#evidence" class="pill">Statistics</a><a href="#elections" class="pill">Elections</a>', 1)
wr(p, s)
ID.update({'VIII · Elections and non-citizens': 'VIII · Pemilu dan orang yang bukan warga negara',
           'Hate speech, voting and the protection of non-citizens': 'Ucapan kebencian, pemilu, dan pelindungan orang yang bukan warga negara',
           'Party hate speech, anti-immigration votes and impunity in 34 democracies.': 'Ucapan kebencian partai, suara anti-imigrasi, dan kekebalan di 34 negara demokrasi.',
           'This part of the project asks whether countries whose law names non-citizens explicitly see less party hate speech and fewer votes for anti-immigration parties, and whether crimes against migrants are punished. It codes four features of domestic law in 34 democracies and sets them beside V-Dem, V-Party and OSCE ODIHR hate crime data. You can test your own questions and download the data.':
             'Bagian proyek ini menanyakan apakah negara yang hukumnya menyebut orang yang bukan warga negara secara tegas mengalami lebih sedikit ucapan kebencian partai dan lebih sedikit suara bagi partai anti-imigrasi, serta apakah kejahatan terhadap migran dihukum. Bagian ini mengodekan empat fitur hukum nasional di 34 negara demokrasi dan menyandingkannya dengan data V-Dem, V-Party, dan data kejahatan kebencian OSCE ODIHR. Anda bisa menguji pertanyaan sendiri dan mengunduh datanya.',
           'Open the comparison of elections and non-citizens →': 'Buka perbandingan pemilu dan orang yang bukan warga negara →',
           'Elections': 'Pemilu', 'Government Hate Speech': 'Ucapan Kebencian oleh Pemerintah'})
p = SITE + ELEC + 'index.html'; s = rd(p)
s = s.replace('<p class="g-eye">%s</p>' % MJS.upper(),
              '<p class="g-eye">%s · <a href="/government-hate-speech/" style="color:inherit">GOVERNMENT HATE SPEECH</a></p>' % MJS.upper(), 1)
s = s.replace('<title>Hate speech, voting and non-citizens · Institute', '<title>Hate speech, voting and non-citizens · Government Hate Speech · Institute')
wr(p, s)
ID.update({MJS.upper() + ' ·': 'YURISPRUDENSI MIGRASI DARI SELATAN ·', 'GOVERNMENT HATE SPEECH': 'UCAPAN KEBENCIAN OLEH PEMERINTAH'})

# ---------- 8. every database is part of the umbrella (JSON-LD) ----------
PART = {"@type": "DataCatalog", "name": MJS, "url": "https://theimr.org/databases/"}
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
def addpart(m):
    try: d = json.loads(m.group(2))
    except Exception: return m.group(0)
    ch = False
    for x in (d if isinstance(d, list) else [d]):
        if isinstance(x, dict) and x.get('@type') == 'Dataset' and 'isPartOf' not in x:
            x['isPartOf'] = PART; ch = True
    return m.group(1) + json.dumps(d, ensure_ascii=False) + m.group(3) if ch else m.group(0)
for u in ['migration-law', 'gcc', 'east-asia', 'southeast-asia', 'countries-of-origin', 'domestic-workers', 'government-hate-speech',
          'government-hate-speech/elections', 'court-decisions']:
    p = SITE + '/' + u + '/index.html'
    if os.path.exists(p):
        s = rd(p); t = LD.sub(addpart, s)
        if t != s: wr(p, t)

# ---------- 9. homepage ----------
p = SITE + '/index.html'; s = rd(p)
s = s.replace('<p class="eyebrow" style="color: #9CC9B2 !important">Projects</p>', '<p class="eyebrow" style="color: #9CC9B2 !important">%s</p>' % MJS)
s = re.sub(r'<li><a href="' + re.escape(FARM) + r'"><span class="mz-tag">Live · Project 2</span><span class="mz-pn">Farmworker Norms Atlas</span><span class="mz-pd">[^<]*</span>',
           '<li><a href="/court-decisions/"><span class="mz-tag">Live · Project 2</span><span class="mz-pn">Court Decisions</span><span class="mz-pd">Nearly 500 court decisions on migrant workers from Asia, Africa, the Middle East and Latin America, searchable by argument.</span>', s)
s = s.replace('<a href="/databases/">All databases and a welcoming remark</a>', '<a href="/databases/">All databases in Migration Jurisprudence from the South</a>')
wr(p, s)
ID.update({'Nearly 500 court decisions on migrant workers from Asia, Africa, the Middle East and Latin America, searchable by argument.':
             'Hampir 500 putusan pengadilan tentang pekerja migran dari Asia, Afrika, Timur Tengah, dan Amerika Latin, yang bisa dicari menurut argumen.',
           'All databases in Migration Jurisprudence from the South': 'Semua basis data dalam Yurisprudensi Migrasi dari Selatan'})

# ---------- 10. umbrella landing page (/databases/) ----------
subprocess.run([sys.executable, HERE + '/landing.py', SITE], check=True)
p = SITE + '/databases/index.html'; s = rd(p)
s = NEW.sub(lambda m: menu('/databases/'), s, count=1); s = COLD.sub(lambda m: cmenu(None), s, count=1); s = CNEW.sub(lambda m: cmenu(None), s, count=1); wr(p, s)

# ---------- 10b. Bentham banner on every page + citations on /databases/#bentham (oto, 2026-11-13) ----------
Q1 = 'Every man his own lawyer!'
Q2 = 'Whatever is not in the code of laws, ought not to be law.'
BAN = ('<nav class="imr-bentham" aria-label="Jeremy Bentham" style="background:#172D24;color:#D8E5DE;font-family:\'Familjen Grotesk\',system-ui,sans-serif;font-size:14px;line-height:1.4">'
       '<div style="max-width:1120px;margin:0 auto;padding:7px 24px;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 12px">'
       '<q class="imr-bq" style="font-style:italic">%s</q><q class="imr-bq" style="font-style:italic" hidden>%s</q>'
       '<a href="/databases/#bentham" style="color:#9CC9B2;text-underline-offset:3px">Jeremy Bentham, Legislator of the World</a>'
       '<button type="button" class="imr-bnext" style="margin-left:auto;background:none;border:0;padding:0;color:#9CC9B2;font:inherit;font-size:13px;cursor:pointer;text-decoration:underline;text-underline-offset:3px">Another maxim</button>'
       '</div></nav>\n<script>(function(){var b=document.currentScript.previousElementSibling,q=b.querySelectorAll(".imr-bq"),i=0;'
       'function sw(){q[i].hidden=true;i=(i+1)%%q.length;q[i].hidden=false;}'
       'b.querySelector(".imr-bnext").addEventListener("click",sw);'
       'if(!(window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches))setInterval(function(){if(!b.matches(":hover"))sw();},12000);})();</script>\n') % (Q1, Q2)
BRAND = re.compile(r'<header\b(?=[^>]*>\s*<div[^>]*>\s*<a [^>]*href="(?:/?(?:index\.html)?|#top)"[^>]*>\s*Institute for Migrant Rights)', re.I)
n = 0
for p in files('.html'):
    s = o = rd(p)
    if 'class="imr-bentham' in s:
        s = re.sub(r'<(?:div|nav) class="imr-bentham[^"]*".*?</script>\n', lambda m: BAN, s, count=1, flags=re.S)
        if s != o: wr(p, s); n += 1
        continue
    m = BRAND.search(s)
    if not m: continue
    s = s[:m.start()] + BAN + s[m.start():]
    wr(p, s); n += 1
print('Bentham banner added/updated on', n, 'pages')
C1 = ('Jeremy Bentham, <i>Papers relative to Codification and Public Instruction</i> (London, 1817), No. VIII, Letter IV, “Of Completeness, as applied to the Body of the Laws”, '
      'in J. Bowring (ed.), <i>The Works of Jeremy Bentham</i>, vol. IV (Edinburgh: William Tait, 1843), p. 490. Bentham had already called it a maxim in his '
      '<i>Draught of a New Plan for the Organisation of the Judicial Establishment in France</i> (1790), ibid., p. 332.')
C2 = ('Jeremy Bentham, “A General View of a Complete Code of Laws”, ch. XXXI, “Of the Integrality of the Code of Laws”, in J. Bowring (ed.), '
      '<i>The Works of Jeremy Bentham</i>, vol. III (Edinburgh: William Tait, 1843), p. 205.')
WHY = ('Bentham wanted the law written down in a complete code that anyone could read and consult without paying a lawyer. '
       'Migration Jurisprudence from the South shares that aim for migrant workers and the people who help them: the law, collected, coded and explained, within everyone’s reach. '
       'Bentham wrote “every man”, as people did in his time; we read it as every person.')
p = SITE + '/databases/index.html'; s = rd(p)
if 'id="bentham"' not in s:
    blk = ('<section id="bentham" style="padding: 8px 0 56px"><div style="max-width: 720px; margin: 0 auto; padding: 0 24px">'
           '<p class="db-eye" style="margin:0">Jeremy Bentham, Legislator of the World</p>'
           '<h2 style="margin: 10px 0 0; font-weight: 400; font-size: 32px; line-height: 1.2">Two maxims from Jeremy Bentham</h2>'
           '<blockquote style="margin: 22px 0 0; padding: 14px 20px; border-left: 4px solid #1E6B4A; background: #FFFFFF"><p style="margin:0;font-size:22px;font-style:italic">“%s”</p>'
           '<p style="margin:8px 0 0;font-size:14px;color:#3D5A4C">%s</p></blockquote>'
           '<blockquote style="margin: 14px 0 0; padding: 14px 20px; border-left: 4px solid #1E6B4A; background: #FFFFFF"><p style="margin:0;font-size:22px;font-style:italic">“%s”</p>'
           '<p style="margin:8px 0 0;font-size:14px;color:#3D5A4C">%s</p></blockquote>'
           '<p style="margin: 20px 0 0">%s</p></div></section>\n') % (Q1, C1, Q2, C2, WHY)
    s = s.replace('<section id="groups"', blk + '<section id="groups"', 1); wr(p, s)
ID.update({'Jeremy Bentham, Legislator of the World': 'Jeremy Bentham, Legislator Dunia',
           Q1: 'Setiap orang menjadi pengacara bagi dirinya sendiri!',
           Q2: 'Apa pun yang tidak tercantum dalam kitab undang-undang, tidak semestinya menjadi hukum.',
           'Another maxim': 'Maksim lain',
           'Two maxims from Jeremy Bentham': 'Dua maksim dari Jeremy Bentham',
           WHY: 'Bentham menginginkan hukum dituliskan dalam kitab yang lengkap, yang bisa dibaca dan dirujuk siapa pun tanpa membayar pengacara. '
                'Yurisprudensi Migrasi dari Selatan berbagi cita-cita itu bagi pekerja migran dan orang-orang yang membantu mereka: hukum yang dihimpun, dikodekan, dan dijelaskan, dalam jangkauan semua orang. '
                'Bentham menulis “every man” (setiap laki-laki), sesuai kebiasaan zamannya; kami membacanya sebagai setiap orang.'})

# ---------- 11. lang.js ----------
L = SITE + '/assets/lang.js'; s = rd(L); pre = 'window.SITE_I18N={"id":{'
assert s.startswith(pre)
add = {k: v for k, v in ID.items() if json.dumps(k, ensure_ascii=False) + ':' not in s}
if add:
    s = pre + ''.join('%s:%s,' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in add.items()) + s[len(pre):]
    wr(L, s)
print('lang.js entries added:', len(add))

# ---------- 12. redirects, llms.txt ----------
R = SITE + '/_redirects'; s = rd(R) if os.path.exists(R) else ''
rules = ['/hate-speech-voting       %s  301' % ELEC, '/hate-speech-voting/*     %s:splat  301' % ELEC,
         '/atlas                    %s  301' % FARM, '/atlas/                   %s  301' % FARM, '/atlas/index.html         %s  301' % FARM]
for r in rules:
    if r.split()[0] + ' ' not in s: s = s.rstrip('\n') + '\n' + r + '\n'
wr(R, s)
lt = rd(SITE + '/llms.txt')
if MJS + ' (umbrella)' not in lt:
    lt = lt.replace('/databases/): welcoming remark', '/databases/): ' + MJS + ' (umbrella), the overview of all IMR databases; welcoming remark')
    lt = lt.replace('in two groups (Projects; Migration and Labor Laws in Comparison)', 'in five groups (Law across tiers; Destination states; Origin states; Themes; Courts)')
    wr(SITE + '/llms.txt', lt)
print('restructure done')
