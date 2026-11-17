# Turns /publications.html into one "Publications" page with the journal (IJICL) and the IMR Press books,
# renames the "IMR Press" menu item to "Publications", points the "Journal" menu item to the journal section,
# and adds the Indonesian strings to /assets/lang.js. Safe to rerun.
import glob, json, re

SITE = '/mnt/project-files/theimr-site'
P = SITE + '/publications.html'

LBL = "margin: 0; font-family: 'Familjen Grotesk', sans-serif; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: #1E6B4A"
FACT_K = "margin: 0; font-family: 'Familjen Grotesk', sans-serif; font-size: 12px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #1E6B4A"
CITE = "display: flex; gap: 16px; align-items: center; background: #172D24; color: #FFFFFF; padding: 16px 18px; text-decoration: none"
CITE_K = "display: block; font-family: 'Familjen Grotesk', sans-serif; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #BCCFC5"
JUMP = "color: #172D24; font-family: 'Familjen Grotesk', sans-serif; font-size: 15px; font-weight: 600; text-decoration: underline; text-underline-offset: 5px"

HERO = f'''<section style="padding: 88px 0 40px">
<div style="max-width: 760px; margin: 0 auto; padding: 0 24px; text-align: center">
<p style="{LBL}">IMR Press</p>
<h1 style="margin: 16px 0 0; font-weight: 400; font-size: 54px; line-height: 1.1">Publications</h1>
<p style="margin: 18px 0 0; color: #2E493D">IMR Press publishes a peer-reviewed journal and books in contemporary legal studies, mainly international and comparative law.</p>
<p style="margin: 22px 0 0; display: flex; justify-content: center; gap: 28px"><a href="#journal" style="{JUMP}">Journal</a><a href="#books" style="{JUMP}">Books</a></p>
</div>
</section>

<section id="journal" style="padding: 0 0 72px; scroll-margin-top: 16px">
<div style="max-width: 1120px; margin: 0 auto; padding: 40px 24px 0; border-top: 1px solid #B2C7BC">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 32px 56px; align-items: start">
<div>
<p style="{LBL}">Journal</p>
<h2 style="margin: 12px 0 0; font-weight: 400; font-size: 36px; line-height: 1.2">Indonesian Journal of International &amp; Comparative Law</h2>
<p style="margin: 16px 0 0; color: #2E493D">A peer-reviewed journal of international and comparative law, published by the Institute since January 2014. It gives particular attention to Indonesia, Asia and the Global South, and welcomes work from scholars and practitioners in and beyond the region.</p>
<p style="margin: 24px 0 0; display: flex; flex-wrap: wrap; gap: 10px 28px; font-family: 'Familjen Grotesk', sans-serif; font-size: 15px; font-weight: 600"><a href="https://ijicl.org">Visit the journal at ijicl.org →</a><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2600789">Read the inaugural foreword →</a></p>
</div>
<dl style="margin: 0; display: grid; grid-template-columns: 1fr; gap: 16px; font-size: 17px; background: #DCE8E1; border: 1px solid #B2C7BC; padding: 22px 24px">
<div><dt style="{FACT_K}">First issue</dt><dd style="margin: 4px 0 0">Volume 1, Issue 1, January 2014</dd></div>
<div><dt style="{FACT_K}">Publisher</dt><dd style="margin: 4px 0 0">IMR Press, Cianjur, Indonesia</dd></div>
<div><dt style="{FACT_K}">ISSN</dt><dd style="margin: 4px 0 0; font-family: 'JetBrains Mono', monospace; font-size: 15px">2338-7602 (print) · 2338-770X (online)</dd></div>
<div><dt style="{FACT_K}">Review</dt><dd style="margin: 4px 0 0">Every article is peer reviewed</dd></div>
</dl>
</div>
<p style="margin: 36px 0 0; font-family: 'Familjen Grotesk', sans-serif; font-size: 14px; color: #2E493D">Cited by courts</p>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; margin-top: 10px">
<a href="https://law.justia.com/cases/federal/appellate-courts/ca9/17-15589/17-15589-2017-06-12.html" style="{CITE}"><span style="flex: 1"><span style="{CITE_K}">U.S. Court of Appeals for the Ninth Circuit</span><span style="display: block; margin-top: 3px; font-size: 18px; line-height: 1.3"><i>Hawaii v. Trump</i>, 859 F.3d 741 (9th Cir. 2017)</span></span><span style="font-family: 'Familjen Grotesk', sans-serif; font-size: 13px; font-weight: 600; white-space: nowrap">Read the decision →</span></a>
<a href="https://www.govinfo.gov/content/pkg/USCOURTS-nyed-1_13-cr-00570/pdf/USCOURTS-nyed-1_13-cr-00570-3.pdf" style="{CITE}"><span style="flex: 1"><span style="{CITE_K}">U.S. District Court, Eastern District of New York</span><span style="display: block; margin-top: 3px; font-size: 18px; line-height: 1.3"><i>United States v. Chin Chong</i>, No. 13-CR-570 (E.D.N.Y. 2014)</span></span><span style="font-family: 'Familjen Grotesk', sans-serif; font-size: 13px; font-weight: 600; white-space: nowrap">Read the decision →</span></a>
</div>
</div>
</section>

<section id="books" style="padding: 0 0 32px; scroll-margin-top: 16px">
<div style="max-width: 1120px; margin: 0 auto; padding: 40px 24px 0; border-top: 1px solid #B2C7BC">
<div style="max-width: 760px">
<p style="{LBL}">IMR Press</p>
<h2 style="margin: 12px 0 0; font-weight: 400; font-size: 36px; line-height: 1.2">Books</h2>
<p style="margin: 16px 0 0; color: #2E493D">IMR Press publishes scholarly work in contemporary legal studies, mainly international and comparative law, in two series: International Law &amp; Comparative Law, and IMR Perspectives, for interdisciplinary work on pressing global questions. Every manuscript goes through peer review.</p>
</div>
</div>
</section>
'''

ID = {
    'Publications': 'Publikasi',
    'IMR Press publishes a peer-reviewed journal and books in contemporary legal studies, mainly international and comparative law.':
        'IMR Press menerbitkan jurnal dan buku yang ditelaah sejawat dalam kajian hukum kontemporer, terutama hukum internasional dan hukum perbandingan.',
    'A peer-reviewed journal of international and comparative law, published by the Institute since January 2014. It gives particular attention to Indonesia, Asia and the Global South, and welcomes work from scholars and practitioners in and beyond the region.':
        'Jurnal hukum internasional dan hukum perbandingan yang ditelaah sejawat, diterbitkan Institut sejak Januari 2014. Jurnal ini memberi perhatian khusus pada Indonesia, Asia, dan negara-negara Selatan, serta terbuka bagi karya akademisi dan praktisi dari dalam maupun luar kawasan.',
    'Visit the journal at ijicl.org →': 'Kunjungi jurnal di ijicl.org →',
    'Read the inaugural foreword →': 'Baca kata pengantar edisi perdana →',
    'First issue': 'Edisi pertama',
    'Volume 1, Issue 1, January 2014': 'Volume 1, Nomor 1, Januari 2014',
    'Publisher': 'Penerbit',
    'IMR Press, Cianjur, Indonesia': 'IMR Press, Cianjur, Indonesia',
    'Review': 'Telaah',
    'Every article is peer reviewed': 'Setiap artikel ditelaah sejawat',
    'Cited by courts': 'Dikutip oleh pengadilan',
    'U.S. Court of Appeals for the Ninth Circuit': 'U.S. Court of Appeals for the Ninth Circuit',
    'U.S. District Court, Eastern District of New York': 'U.S. District Court, Eastern District of New York',
    'Read the decision →': 'Baca putusannya →',
    'Publications · Institute for Migrant Rights': 'Publikasi · Institute for Migrant Rights',
}

# 1. The page itself
s = open(P, encoding='utf-8').read()
if 'id="journal"' not in s:
    a = s.index('<section style="padding: 88px 0 56px">')
    b = s.index('</section>', a) + len('</section>')
    s = s[:a] + HERO.rstrip('\n') + s[b:]
    s = s.replace('<section style="padding: 0 0 80px">\n<div style="max-width: 1120px; margin: 0 auto; padding: 0 24px; display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 0 48px; border-top: 1px solid #B2C7BC">',
                  '<section style="padding: 0 0 80px">\n<div style="max-width: 1120px; margin: 0 auto; padding: 0 24px; display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 0 48px">', 1)
    s = s.replace('<title>IMR Press · Institute for Migrant Rights</title>', '<title>Publications · Institute for Migrant Rights</title>')
    s = s.replace('content="IMR Press · Institute for Migrant Rights"', 'content="Publications · Institute for Migrant Rights"')
    d_old = 'Books from IMR Press: peer-reviewed work in international and comparative law, mostly in Bahasa Indonesia, with links to Google Books.'
    d_new = 'Publications of the Institute for Migrant Rights: the Indonesian Journal of International &amp; Comparative Law (ISSN 2338-7602, 2338-770X) and IMR Press books in international and comparative law.'
    s = s.replace(d_old, d_new)
    # Machine-readable record of the journal for search engines
    ld = {"@context": "https://schema.org", "@type": "Periodical", "name": "Indonesian Journal of International & Comparative Law",
          "issn": ["2338-7602", "2338-770X"], "url": "https://ijicl.org", "startDate": "2014-01", "inLanguage": "en",
          "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights Press", "url": "https://theimr.org/"}}
    s = s.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n</head>', 1)
    open(P, 'w', encoding='utf-8').write(s)
    print('publications.html rebuilt')

# 2. Menu on every page: "IMR Press" -> "Publications", "Journal" -> the journal section
n = 0
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    t = open(p, encoding='utf-8').read(); o = t
    t = re.sub(r'(<a href="/?publications\.html"(?: aria-current="page")?(?: style="[^"]*")?>)IMR Press</a>', r'\1Publications</a>', t)
    t = re.sub(r'<a href="https://ijicl\.org"((?: style="[^"]*")?)>Journal</a>', r'<a href="/publications.html#journal"\1>Journal</a>', t)
    if t != o: open(p, 'w', encoding='utf-8').write(t); n += 1
print('menu updated on', n, 'pages')

# 3. Indonesian strings
L = SITE + '/assets/lang.js'
j = open(L, encoding='utf-8').read()
head = 'window.SITE_I18N={"id":{'
assert j.startswith(head)
d = json.JSONDecoder().raw_decode(j, len('window.SITE_I18N='))[0]['id']
add = {k: v for k, v in ID.items() if k not in d}
if add:
    j = head + json.dumps(add, ensure_ascii=False)[1:-1] + ',' + j[len(head):]
    open(L, 'w', encoding='utf-8').write(j)
print('lang strings added:', len(add))

# 4. llms.txt
T = SITE + '/llms.txt'
t = open(T, encoding='utf-8').read()
t2 = t.replace('- [IMR Press](https://theimr.org/publications.html)',
               '- [Publications: Indonesian Journal of International & Comparative Law and IMR Press books](https://theimr.org/publications.html)')
if t2 != t: open(T, 'w', encoding='utf-8').write(t2); print('llms.txt updated')
print('done')
