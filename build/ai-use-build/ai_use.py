# 2026-11-13: paths updated for the site restructure (hate-speech-voting -> government-hate-speech/elections; /atlas/ page retired).
# Adds the "How we use AI" statement to theimr.org (Pranoto, 2026-11-03).
# 1. writes /ai-use/index.html (EN, with ID strings in /assets/lang.js)
# 2. adds a "How we use AI" link to the footer of every page (a small footer where a page has none)
# 3. adds a one-line "Use of AI" note to the method/data section of each database page
# 4. adds the page to sitemap.xml and llms.txt
# Safe to rerun (every step checks for its marker). Rerun after rebuilding a page
# (atlas build.py, court-decisions page.py / static_pages.py, etc.).
import os, re, json, glob
SITE = __import__('sys').argv[1] if len(__import__('sys').argv) > 1 else '/mnt/project-files/theimr-site'
LINK = '/ai-use/'

# ---------- strings ----------
ONE = ('AI is used to re-confirm that none of the data we use infringes intellectual property law, to test our labels '
       'and to edit summaries into plain language, which people then re-edit.')
CD_EXTRA = 'Summaries pre-written by AI are marked “unverified”.'
ID = {
 'How we use AI': 'Cara kami memakai AI',
 'Statement': 'Pernyataan',
 'This statement explains where artificial intelligence (AI) tools are used in building the databases on this site.':
   'Pernyataan ini menjelaskan di mana perangkat kecerdasan buatan (AI) dipakai dalam penyusunan basis data di situs ini.',
 'Research use': 'Penggunaan dalam riset',
 'AI is used to re-confirm that none of the data we use infringes intellectual property law, and to test our labels.':
   'AI dipakai untuk memastikan kembali bila semua data yang dipakai tidak bertentangan dengan hukum atas kekayaan intelektual, serta untuk menguji label kami.',
 'Composition use': 'Penggunaan dalam penulisan',
 'AI is used to edit our written summaries into plain language. Each summary is then re-edited by a person.':
   'AI dipakai untuk menyunting ringkasan yang kami tulis ke dalam bahasa sederhana. Setiap ringkasan kemudian disunting ulang oleh manusia.',
 'In some instances we have used summaries pre-written by AI. These are marked “unverified”.':
   'Dalam beberapa kasus kami memakai ringkasan yang ditulis lebih dahulu oleh AI. Ringkasan ini ditandai “belum diverifikasi”.',
 'Where this applies': 'Di mana pernyataan ini berlaku',
 'The statement covers the databases and comparison pages below. Each of them repeats it in one line in its method or data section.':
   'Pernyataan ini mencakup basis data dan halaman perbandingan di bawah ini. Setiap halaman mengulanginya dalam satu baris di bagian metode atau datanya.',
 'Corrections': 'Koreksi',
 'If you find an error in a source, a label or a summary, please write to':
   'Jika Anda menemukan kesalahan pada sumber, label, atau ringkasan, silakan tulis kepada',
 'Last updated 3 November 2026.': 'Terakhir diperbarui 3 November 2026.',
 'Use of AI:': 'Penggunaan AI:',
 ONE: 'AI dipakai untuk memastikan kembali bila semua data yang dipakai tidak bertentangan dengan hukum atas kekayaan intelektual, menguji label kami, dan menyunting ringkasan ke dalam bahasa sederhana, yang kemudian disunting ulang oleh manusia.',
 CD_EXTRA: 'Ringkasan yang ditulis lebih dahulu oleh AI ditandai “belum diverifikasi”.',
 'Unverified': 'Belum diverifikasi',
 'Summary pre-written by AI from secondary sources, being checked against the judgment.':
   'Ringkasan ini ditulis lebih dahulu oleh AI dari sumber sekunder dan sedang diperiksa dengan teks putusan.',
 'Institute for Migrant Rights': 'Institute for Migrant Rights',
}

PAGES = [  # (path, name) for the "Where this applies" list
 ('/migration-law/', 'Migration Law Atlas'), ('/migration-law/?lens=farm', 'Migration Law Atlas: farmworker law view'),
 ('/government-hate-speech/', 'Government Hate Speech'), ('/gcc/', 'Gulf States'), ('/east-asia/', 'East Asia'),
 ('/countries-of-origin/', 'Countries of Origin'), ('/domestic-workers/', 'Migrant Domestic Workers'), ('/government-hate-speech/elections/', 'Government Hate Speech: elections and non-citizens'),
 ('/court-decisions/', 'Court Decisions'), ('/legal-clinic/trafficking-check/', 'Trafficking self-check (plain-language wording)')]

def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s): open(p, 'w', encoding='utf-8').write(s)

# ---------- 1. the page ----------
P = rd(SITE + '/people.html')
head = P[:P.index('</header>') + len('</header>')]
tail = P[P.index('<div class="imr-ridge"'):]
title = 'How we use AI · Institute for Migrant Rights'
desc = ('How the Institute for Migrant Rights uses AI in its databases: to re-confirm that none of the data '
        'used infringes intellectual property law, to test labels, and to edit summaries into plain language.')
head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, head)
head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, head)
head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % title, head)
head = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % desc, head)
head = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://theimr.org/ai-use/">', head)
head = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="https://theimr.org/ai-use/">', head)
head = head.replace('<a href="people.html" aria-current="page" style="color: #1E6B4A; text-decoration: underline; text-underline-offset: 6px; padding: 10px 0">People</a>',
                    '<a href="/people.html" style="color: #172D24; text-decoration: none; padding: 10px 0">People</a>')
head = re.sub(r'href="(?!/|https?:|mailto:|#)([^"]+)"', r'href="/\1"', head)   # page sits one level down
ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "How we use AI", "url": "https://theimr.org/ai-use/",
      "description": desc, "inLanguage": ["en", "id"], "dateModified": "2026-11-03",
      "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"}}
head = head.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(ld, ensure_ascii=False))

H2 = 'margin: 0; font-weight: 500; font-size: 28px; line-height: 1.2'
EY = "margin: 0 0 8px; font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: #1E6B4A"
def block(id_, n, h, body):
    return ('<div id="%s" style="padding: 32px 0; border-top: 1px solid #B2C7BC; scroll-margin-top: 24px">'
            '<p style="%s">%s</p><h2 style="%s">%s</h2>%s</div>') % (id_, EY, n, H2, h, body)
plist = ''.join('<li><a href="%s">%s</a></li>' % (u, t) for u, t in PAGES)
main = '\n'.join([
 '<main id="ai-use">',
 '<section style="padding: 88px 0 40px">',
 '<div style="max-width: 760px; margin: 0 auto; padding: 0 24px; text-align: center">',
 "<p style=\"margin: 0; font-family: 'Familjen Grotesk', sans-serif; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: #1E6B4A\">Statement</p>",
 '<h1 style="margin: 16px 0 0; font-weight: 400; font-size: 54px; line-height: 1.1">How we use AI</h1>',
 '<p style="margin: 20px 0 0; color: #2E493D">This statement explains where artificial intelligence (AI) tools are used in building the databases on this site.</p>',
 '</div></section>',
 '<section style="padding: 0 0 72px"><div style="max-width: 760px; margin: 0 auto; padding: 0 24px">',
 block('research', 'I', 'Research use', '<p style="margin: 12px 0 0">AI is used to re-confirm that none of the data we use infringes intellectual property law, and to test our labels.</p>'),
 block('composition', 'II', 'Composition use',
       '<p style="margin: 12px 0 0">AI is used to edit our written summaries into plain language. Each summary is then re-edited by a person.</p>'
       '<p style="margin: 12px 0 0">In some instances we have used summaries pre-written by AI. These are marked “unverified”.</p>'),
 block('scope', 'III', 'Where this applies',
       '<p style="margin: 12px 0 0">The statement covers the databases and comparison pages below. Each of them repeats it in one line in its method or data section.</p>'
       '<ul style="margin: 12px 0 0; padding-left: 22px">' + plist + '</ul>'),
 block('corrections', 'IV', 'Corrections',
       '<p style="margin: 12px 0 0">If you find an error in a source, a label or a summary, please write to <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.</p>'
       "<p style=\"margin: 24px 0 0; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #3D5A4D\">Last updated 3 November 2026.</p>"),
 '</div></section>',
 '</main>', ''])
os.makedirs(SITE + '/ai-use', exist_ok=True)
wr(SITE + '/ai-use/index.html', head + '\n' + main + tail)

# ---------- 2. footer link on every page ----------
FOOT_ROW = ('<div class="imr-foot-ai" style="max-width: 1120px; margin: 32px auto 0; padding: 0 24px; '
            "font-family: 'Familjen Grotesk', sans-serif; font-size: 14px\">"
            '<p style="margin: 0; padding-top: 16px; border-top: 1px solid #2E493D; color: #BCCFC5">'
            '<a href="/ai-use/" style="color: #FFFFFF">How we use AI</a></p></div>\n')
MINI = ('<footer class="imr-foot-ai" style="background: #172D24; color: #BCCFC5; padding: 20px 24px; '
        "font-family: 'Familjen Grotesk', system-ui, sans-serif; font-size: 14px\">"
        '<div style="max-width: 1120px; margin: 0 auto"><span>Institute for Migrant Rights</span> · '
        '<a href="/ai-use/" style="color: #FFFFFF">How we use AI</a></div></footer>\n')
nf = nm = 0
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    if '/embed/' in p or p.endswith('/offline.html'): continue  # embeddable widgets on partner sites stay bare
    s = rd(p)
    if 'imr-foot-ai' in s: continue
    if '</footer>' in s:
        i = s.rindex('</footer>')
        s = s[:i] + FOOT_ROW + s[i:]; nf += 1
    else:
        i = s.rindex('</body>'); s = s[:i] + MINI + s[i:]; nm += 1  # last </body>: atlas has one inside a JS string
    wr(p, s)
print('footer link added:', nf, 'pages; small footer added:', nm, 'pages')

# ---------- 3. one-line note on database pages ----------
def note(extra='', cls='', style='margin:0 0 20px;max-width:820px;font-size:16px;line-height:1.55;color:#2E493D', a_txt='How we use AI'):
    return ('<p class="%simr-ai-note"%s><b>Use of AI:</b> %s%s <a href="/ai-use/">%s</a></p>'
            % ((cls + ' ') if cls else '', (' style="%s"' % style) if style else '', ONE, (' ' + extra) if extra else '', a_txt))
SPOTS = [
 ('gcc/index.html', '<h2>How the data was built</h2>', note()),
 ('east-asia/index.html', '<h2>How the data was built</h2>', note()),
 ('countries-of-origin/index.html', '<h2>How the data was built</h2>', note()),
 ('domestic-workers/index.html', '<h2>How the data was built</h2>', note()),
 ('government-hate-speech/elections/index.html', '<span class="chev" aria-hidden="true"></span></summary>\n<div class="fbody">', note(), '<p class="g-eye">VIII · METHOD AND CODEBOOK</p>'),
 ('court-decisions/index.html', '<h2>How decisions are chosen and coded</h2>', note(CD_EXTRA)),
 ('migration-law/index.html', '<p class="note" id="dlnote"></p>', note(cls='note', style='')),
 ('government-hate-speech/index.html', 'test a statement against the proposed offense, and download the data.</p>',
  note(cls='note', style='margin: 10px auto 0; max-width: 740px; text-align: center')),
]
for spot in SPOTS:
    f, anchor, html_ = spot[:3]
    p = SITE + '/' + f; s = rd(p)
    if 'imr-ai-note' in s: print('note already on', f); continue
    if len(spot) > 3:  # anchor that repeats: use the one after a section marker
        j = s.index(spot[3]); i = s.index(anchor, j)
    else:
        assert s.count(anchor) == 1, (f, s.count(anchor)); i = s.index(anchor)
    i += len(anchor)
    s = s[:i] + '\n' + html_ + s[i:]
    wr(p, s); print('note added to', f)

# ---------- 4. Indonesian strings ----------
L = SITE + '/assets/lang.js'; s = rd(L)
pre = 'window.SITE_I18N={"id":{'
assert s.startswith(pre)
add = {k: v for k, v in ID.items() if json.dumps(k, ensure_ascii=False) + ':' not in s}
if add:
    s = pre + ''.join('%s:%s,' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in add.items()) + s[len(pre):]
    wr(L, s)
print('lang.js entries added:', len(add))

# ---------- 5. sitemap and llms.txt ----------
sm = rd(SITE + '/sitemap.xml')
if 'https://theimr.org/ai-use/' not in sm:
    sm = sm.replace('</urlset>', '  <url><loc>https://theimr.org/ai-use/</loc><lastmod>2026-11-03</lastmod></url>\n</urlset>')
    wr(SITE + '/sitemap.xml', sm)
lt = rd(SITE + '/llms.txt')
if '/ai-use/' not in lt:
    lt = lt.rstrip('\n') + '\n\n## How we use AI\n- [How we use AI](https://theimr.org/ai-use/): AI re-confirms that none of the data used infringes intellectual property law and tests labels; it edits summaries into plain language, which people re-edit; summaries pre-written by AI are marked "unverified".\n'
    wr(SITE + '/llms.txt', lt)
print('done')
