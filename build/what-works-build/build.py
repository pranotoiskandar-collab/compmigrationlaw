# Builds /legal-clinic/what-works/ ("What works where", Pranoto 2026-11-13) from the Court Decisions data and notes.py.
# Usage: python3 build.py SITE_DIR   (rerun whenever court-decisions/cd-data.js changes; then restructure.py, ai_use.py, analytics.py)
import os, sys, json, subprocess, html, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from notes import J
SITE = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/theimr-site'
def rd(p): return open(p, encoding='utf-8').read()
e = lambda s: html.escape(str(s), quote=True)
def B(en, id_): return '<span class="en">%s</span><span class="id">%s</span>' % (en, id_)

C = json.loads(subprocess.run(['node', '-e', 'global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.CD))',
                               SITE + '/court-decisions/cd-data.js'], capture_output=True, text=True, check=True).stdout)
D = [d for d in C['decisions'] if d.get('status') != 'C' and d.get('args')]
ARG = {a['k']: a for a in C['args'].values()} if isinstance(C['args'], dict) else {a['k']: a for a in C['args']}
TOOL = {t['k']: t for t in C['tools']}
VER, DATE = C.get('version', ''), C.get('date', '')

def stats(ds):
    s = {}
    for d in ds:
        for a in d['args']:
            x = s.setdefault(a['a'], [0, 0, [], []]); x[1] += 1
            if a['ok']: x[0] += 1; x[2].append(d)
            else: x[3].append(d)
    return s
ALL = stats(D)
GROUPS = [(k, en, id_, set(cc), nen, nid, src, [d for d in D if d['cc'] in cc]) for k, en, id_, cc, nen, nid, src in J]

# ---------- matrix: arguments x jurisdictions ----------
gstats = {g[0]: stats(g[7]) for g in GROUPS}
rows = sorted([k for k in ALL if sum(1 for g in GROUPS if k in gstats[g[0]]) >= 2],
              key=lambda k: -sum(gstats[g[0]].get(k, [0, 0])[1] for g in GROUPS))
def cell(x):
    if not x: return '<td class="ww-c ww-0">–</td>'
    a, t = x[0], x[1]; r = a / t
    cls = 'ww-hi' if r >= .67 else 'ww-mid' if r > .33 else 'ww-lo'
    return '<td class="ww-c %s" title="%d / %d">%d / %d</td>' % (cls, a, t, a, t)
mat = ['<div class="ww-scroll"><table class="ww-t" data-noi18n><thead><tr><th>%s</th>' % B('Argument', 'Argumen')]
mat += ['<th class="ww-v"><a href="#%s">%s</a></th>' % (g[0], B(e(g[1].split(' (')[0]), e(g[2].split(' (')[0]))) for g in GROUPS]
mat.append('</tr></thead><tbody>')
for k in rows:
    a = ARG[k]
    mat.append('<tr><th scope="row">%s</th>%s</tr>' % (B(e(a['en']), e(a['id'])), ''.join(cell(gstats[g[0]].get(k)) for g in GROUPS)))
mat.append('</tbody></table></div>')

# ---------- cards ----------
def dlink(d): return '<a href="/court-decisions/d/%s/">%s</a> (%s)' % (e(d['id']), e(d['name']), e(d['date'][:4]))
def arglist(items, ok):
    out = []
    for k, x in items:
        ds = x[2] if ok else x[3]
        n = x[0] if ok else x[1] - x[0]
        out.append('<li><b>%s</b> <span class="ww-n">%d / %d</span><br><span class="ww-ds">%s</span></li>'
                   % (B(e(ARG[k]['en']), e(ARG[k]['id'])), n, x[1], '; '.join(dlink(d) for d in ds[:4]) + (' …' if len(ds) > 4 else '')))
    return '<ul class="ww-al">' + ''.join(out) + '</ul>'
cards = []
ntot = len(D)
tool_all = {}
for d in D:
    for t in d.get('tools') or []: tool_all[t] = tool_all.get(t, 0) + 1
for k, en, id_, cc, nen, nid, src, ds in GROUPS:
    s = gstats[k]
    good = sorted([(a, x) for a, x in s.items() if x[0] > 0], key=lambda z: (-z[1][0], -z[1][1]))
    bad = sorted([(a, x) for a, x in s.items() if x[1] - x[0] > 0], key=lambda z: (-(z[1][1] - z[1][0]), -z[1][1]))
    # compared with the rest of the collection
    rest = stats([d for d in D if d['cc'] not in cc]); cmp_ = []
    for a, x in s.items():
        y = rest.get(a)
        if x[1] >= 2 and y and y[1] >= 3:
            r1, r2 = x[0] / x[1], y[0] / y[1]
            if abs(r1 - r2) >= .35:
                up = r1 > r2
                cmp_.append((abs(r1 - r2), '<li>%s <b>%s</b>: %s</li>' % (
                    B('Accepted more often here:' if up else 'Accepted less often here:', 'Lebih sering diterima di sini:' if up else 'Lebih jarang diterima di sini:'),
                    B(e(ARG[a]['en']), e(ARG[a]['id'])),
                    B('%d of %d here, against %d of %d elsewhere in the collection.' % (x[0], x[1], y[0], y[1]),
                      '%d dari %d di sini, dibandingkan %d dari %d di bagian lain koleksi.' % (x[0], x[1], y[0], y[1])))))
    tl = {}
    for d in ds:
        for t in d.get('tools') or []: tl[t] = tl.get(t, 0) + 1
    for t, n in tl.items():
        sh, sa = n / len(ds), tool_all[t] / ntot
        if n >= 2 and sh - sa >= .2:
            cmp_.append((sh - sa, '<li>%s <b>%s</b>: %s</li>' % (
                B('Reasoning used more often here:', 'Penalaran yang lebih sering dipakai di sini:'), B(e(TOOL[t]['en']), e(TOOL[t]['id'])),
                B('%d of %d decisions here, against %d%% across the collection.' % (n, len(ds), round(sa * 100)),
                  '%d dari %d putusan di sini, dibandingkan %d%% di seluruh koleksi.' % (n, len(ds), round(sa * 100))))))
    cmp_ = [h for _, h in sorted(cmp_, key=lambda z: -z[0])][:5]
    tools = sorted(tl.items(), key=lambda z: -z[1])[:4]
    srcs = ''.join('<li>%s</li>' % B(e(a), e(b)) for a, b in src)
    cards.append('\n'.join([
        '<section class="ww-card" id="%s">' % k,
        '<h2>%s</h2>' % B(e(en), e(id_)),
        '<p class="ww-meta">%s</p>' % B('%d coded decisions in the collection' % len(ds), '%d putusan berkode dalam koleksi' % len(ds)),
        '<div class="ww-note"><p class="ww-eye">%s <span class="ww-tag">%s</span></p><p>%s</p>%s</div>' % (
            B('What makes it distinctive', 'Apa yang membuatnya khas'), B('Being checked', 'Sedang diperiksa'), B(e(nen), e(nid)),
            ('<p class="ww-src">%s</p><ul class="ww-srcs">%s</ul>' % (B('Also drawing on:', 'Juga bersandar pada:'), srcs)) if srcs else ''),
        ('<div class="ww-cmp"><p class="ww-eye">%s</p><ul>%s</ul></div>' % (B('Compared with the rest of the collection', 'Dibandingkan dengan bagian lain koleksi'), ''.join(cmp_))) if cmp_ else '',
        '<div class="ww-two"><div><h3>%s</h3>%s</div><div><h3>%s</h3>%s</div></div>' % (
            B('Arguments that worked here', 'Argumen yang berhasil di sini'), arglist(good, True) if good else '<p>%s</p>' % B('None in the collection yet.', 'Belum ada dalam koleksi.'),
            B('Arguments that did not work here', 'Argumen yang tidak berhasil di sini'), arglist(bad, False) if bad else '<p>%s</p>' % B('None in the collection yet.', 'Belum ada dalam koleksi.')),
        ('<p class="ww-tools"><b>%s</b> %s</p>' % (B('How courts here reason most often:', 'Cara bernalar yang paling sering di sini:'),
          '; '.join('%s (%d)' % (B(e(TOOL[t]['en']), e(TOOL[t]['id'])), n) for t, n in tools))) if tools else '',
        '</section>']))

# ---------- page ----------
S = rd(SITE + '/legal-clinic/how-we-work/index.html')
head = S[:S.index('</header>') + len('</header>')]
tail = S[S.index('<div class="imr-ridge"'):]
title = 'What works where · Legal Clinic · Institute for Migrant Rights'
desc = ('Which legal arguments for migrant workers courts have accepted or rejected in each jurisdiction, and what sets each jurisdiction apart. '
        'Drawn from the Court Decisions collection of Migration Jurisprudence from the South.')
for a, b in [(r'<title>.*?</title>', '<title>%s</title>' % title),
             (r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc),
             (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % title),
             (r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % desc),
             (r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://theimr.org/legal-clinic/what-works/">'),
             (r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="https://theimr.org/legal-clinic/what-works/">')]:
    head = re.sub(a, b.replace('\\', '\\\\'), head)
head = head.replace(' aria-current="page"', '')
CSS = '''<style>
html[lang="id"] .en{display:none} html:not([lang="id"]) .id{display:none}
.ww{max-width:1120px;margin:0 auto;padding:0 24px}
.ww-eye{margin:0;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1E6B4A}
.ww-warn{margin:28px 0 0;padding:18px 22px;border:2px dashed #172D24;font-size:16px}
.ww-pills{display:flex;flex-wrap:wrap;gap:8px;margin:28px 0 0}.ww-pills a{border:1px solid #B2C7BC;background:#fff;padding:7px 12px;font-size:15px;color:#172D24;text-decoration:none}.ww-pills a:hover{border-color:#1E6B4A;color:#1E6B4A}
.ww-scroll{overflow-x:auto;margin:20px 0 0;border:1px solid #B2C7BC;background:#fff}
.ww-t{border-collapse:collapse;min-width:980px;font-size:14px}.ww-t th,.ww-t td{border-bottom:1px solid #DCE8E1;padding:7px 8px;text-align:left;vertical-align:top}
.ww-t thead th{font-weight:600;font-size:13px;background:#EEF4F0;position:sticky;top:0}.ww-t thead th a{color:#172D24}
.ww-t tbody th{font-weight:500;min-width:260px;max-width:320px}
.ww-c{text-align:center!important;font-family:'JetBrains Mono',monospace;font-size:13px;white-space:nowrap}
.ww-hi{background:#C9E3D3}.ww-mid{background:#EEF0D8}.ww-lo{background:#F2DCD6}.ww-0{color:#A9B9B0}
.ww-key{display:flex;flex-wrap:wrap;gap:14px;margin:10px 0 0;font-size:14px;color:#2E493D}.ww-key i{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin-right:6px;border:1px solid #B2C7BC}
.ww-card{margin:56px 0 0;padding:32px 0 0;border-top:1px solid #B2C7BC;scroll-margin-top:12px}
.ww-card h2{margin:0;font-weight:500;font-size:32px;line-height:1.2}.ww-meta{margin:6px 0 0;font-size:15px;color:#3D5A4C}
.ww-note{margin:20px 0 0;padding:20px 24px;background:#fff;border-left:4px solid #1E6B4A;max-width:860px}.ww-note p{margin:8px 0 0}.ww-note .ww-eye{margin:0}
.ww-tag{display:inline-block;margin-left:8px;padding:1px 8px;border:1px solid #9A6B1F;color:#7A5418;font-size:11px;letter-spacing:.06em}
.ww-src{font-size:14px;color:#3D5A4C}.ww-srcs{margin:4px 0 0;padding-left:18px;font-size:14px;color:#3D5A4C}
.ww-cmp{margin:18px 0 0;max-width:860px}.ww-cmp ul{margin:8px 0 0;padding-left:18px;font-size:16px}.ww-cmp li{margin:4px 0}
.ww-two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px 40px;margin:22px 0 0}.ww-two h3{margin:0;font-size:19px;font-weight:600}
.ww-al{list-style:none;margin:10px 0 0;padding:0}.ww-al li{padding:10px 0;border-bottom:1px solid #DCE8E1;font-size:16px}
.ww-n{font-family:'JetBrains Mono',monospace;font-size:13px;color:#3D5A4C;margin-left:6px}.ww-ds{font-size:14px;color:#2E493D}
.ww-tools{margin:16px 0 0;font-size:15px;color:#2E493D}
@media (max-width:640px){.ww-h1{font-size:38px!important}.ww-card h2{font-size:26px}}
</style>
<script type="application/ld+json">%s</script>
</head>''' % json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "What works where", "url": "https://theimr.org/legal-clinic/what-works/",
                         "description": desc, "inLanguage": ["en", "id"], "dateModified": "2026-11-13",
                         "isPartOf": {"@type": "DataCatalog", "name": "Migration Jurisprudence from the South", "url": "https://theimr.org/databases/"},
                         "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"}}, ensure_ascii=False)
head = head.replace('</head>', CSS, 1)
pills = ''.join('<a href="#%s">%s</a>' % (g[0], B(e(g[1].split(' (')[0]), e(g[2].split(' (')[0]))) for g in GROUPS)
main = '\n'.join([
 '<main id="what-works" data-noi18n style="padding: 72px 0 40px">', '<div class="ww">',
 '<p class="ww-eye">%s</p>' % B('Legal Clinic · Arguments that work', 'Klinik Hukum · Argumen yang berhasil'),
 '<h1 class="ww-h1" style="margin: 14px 0 0; font-weight: 400; font-size: 52px; line-height: 1.1">%s</h1>' % B('What works where', 'Apa yang berhasil, dan di mana'),
 '<p style="margin: 18px 0 0; max-width: 820px">%s</p>' % B(
   'Which lines of legal argument for migrant workers have courts accepted, and which have they rejected, in each jurisdiction? This guide reads the coded decisions in the Court Decisions collection by jurisdiction and by argument. Each jurisdiction has a short note on what sets it apart from the others.',
   'Argumen hukum mana bagi pekerja migran yang diterima pengadilan, dan mana yang ditolak, di setiap yurisdiksi? Panduan ini membaca putusan berkode dalam koleksi Putusan Pengadilan menurut yurisdiksi dan menurut argumen. Setiap yurisdiksi dilengkapi catatan singkat tentang apa yang membedakannya dari yang lain.'),
 '<div class="ww-warn">%s</div>' % B(
   '<b>Read with care.</b> The counts describe %d coded decisions in this collection, not all litigation, so they are not success rates. The summaries and the notes below were prepared with AI assistance and are still being checked against the judgments (<a href="/ai-use/">how we use AI</a>). This is not legal advice: for a case, read the judgment or <a href="/legal-clinic/">ask the Legal Clinic</a>.' % len(D),
   '<b>Baca dengan hati-hati.</b> Angka-angka ini menggambarkan %d putusan berkode dalam koleksi ini, bukan seluruh perkara, sehingga bukan tingkat keberhasilan. Ringkasan dan catatan di bawah disusun dengan bantuan AI dan masih diperiksa terhadap putusannya (<a href="/ai-use/">cara kami memakai AI</a>). Ini bukan nasihat hukum: untuk suatu perkara, bacalah putusannya atau <a href="/legal-clinic/">tanyakan kepada Klinik Hukum</a>.' % len(D)),
 '<div class="ww-pills">%s</div>' % pills,
 '<section id="matrix" style="margin-top: 56px"><p class="ww-eye">%s</p><h2 style="margin: 8px 0 0; font-weight: 500; font-size: 32px">%s</h2>' % (B('At a glance', 'Sekilas'), B('Arguments by jurisdiction', 'Argumen menurut yurisdiksi')),
 '<p style="margin: 10px 0 0; max-width: 820px; font-size: 16px">%s</p>' % B('Each cell shows how many times courts in that jurisdiction accepted the argument, out of the decisions in which it was tried. Only arguments tried in at least two jurisdictions are shown.',
   'Setiap sel menunjukkan berapa kali pengadilan di yurisdiksi itu menerima argumen tersebut, dari seluruh putusan yang mengujinya. Hanya argumen yang diuji di sedikitnya dua yurisdiksi yang ditampilkan.'),
 '<div class="ww-key"><span><i style="background:#C9E3D3"></i>%s</span><span><i style="background:#EEF0D8"></i>%s</span><span><i style="background:#F2DCD6"></i>%s</span></div>' % (
   B('Mostly accepted', 'Umumnya diterima'), B('Mixed', 'Campuran'), B('Mostly rejected', 'Umumnya ditolak')),
 ''.join(mat), '</section>',
 '\n'.join(cards),
 '<section id="method" class="ww-card"><h2>%s</h2><p style="max-width:820px">%s</p></section>' % (B('How this guide is made', 'Cara panduan ini disusun'), B(
   'The guide is generated from the Court Decisions data (version %s, %s). It uses only decisions with a written summary, not unchecked candidates. Each argument a court ruled on is coded as accepted or rejected, and each decision is tagged with the reasoning tools the court relied on, following Farnsworth\'s <i>The Tools of Argument</i> and the other sources listed in the Court Decisions method section. The comparisons with the rest of the collection flag differences of 35 percentage points or more, and only where the argument was tried at least twice in the jurisdiction and three times elsewhere. They describe this collection only. The distinctive-feature notes were written with AI assistance from the decisions and from the sources named in each note, and they are being checked. Corrections are welcome at <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.' % (e(VER), e(DATE)),
   'Panduan ini dibuat dari data Putusan Pengadilan (versi %s, %s). Panduan ini hanya memakai putusan yang sudah memiliki ringkasan tertulis, bukan kandidat yang belum diperiksa. Setiap argumen yang diputus pengadilan dikodekan sebagai diterima atau ditolak, dan setiap putusan ditandai dengan alat penalaran yang dipakai pengadilan, mengikuti <i>The Tools of Argument</i> karya Farnsworth dan sumber lain yang tercantum di bagian metode Putusan Pengadilan. Perbandingan dengan bagian lain koleksi menandai perbedaan sebesar 35 poin persentase atau lebih, dan hanya bila argumen itu diuji sedikitnya dua kali di yurisdiksi tersebut dan tiga kali di tempat lain. Perbandingan ini hanya menggambarkan koleksi ini. Catatan tentang ciri khas ditulis dengan bantuan AI dari putusan dan dari sumber yang disebut dalam setiap catatan, dan sedang diperiksa. Koreksi bisa dikirim ke <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.' % (e(VER), e(DATE)))),
 '<p style="margin: 40px 0 0; font-size: 16px"><a href="/court-decisions/#argument">%s</a> · <a href="/legal-clinic/">%s</a> · <a href="/legal-help/">%s</a></p>' % (
   B('Open Court Decisions by argument', 'Buka Putusan Pengadilan menurut argumen'), B('Prepare a rights communication', 'Siapkan pengaduan hak'), B('Find free legal help', 'Cari bantuan hukum gratis')),
 '</div>', '</main>', ''])
os.makedirs(SITE + '/legal-clinic/what-works', exist_ok=True)
open(SITE + '/legal-clinic/what-works/index.html', 'w', encoding='utf-8').write(head + '\n' + main + tail)
# sitemap
sm = rd(SITE + '/sitemap.xml')
if '/legal-clinic/what-works/' not in sm:
    sm = sm.replace('</urlset>', '  <url><loc>https://theimr.org/legal-clinic/what-works/</loc><lastmod>2026-11-13</lastmod></url>\n</urlset>')
    open(SITE + '/sitemap.xml', 'w', encoding='utf-8').write(sm)
lt = rd(SITE + '/llms.txt')
if '/legal-clinic/what-works/' not in lt:
    lt = lt.rstrip('\n') + '\n- [What works where](https://theimr.org/legal-clinic/what-works/): which legal arguments for migrant workers courts accepted or rejected in each jurisdiction, with a note on what sets each jurisdiction apart.\n'
    open(SITE + '/llms.txt', 'w', encoding='utf-8').write(lt)
print('what-works page:', len(D), 'decisions,', len(GROUPS), 'jurisdictions,', len(rows), 'argument rows')
