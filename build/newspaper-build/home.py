# Rebuilds theimr.org's homepage in the editorial ("newspaper") layout, 2026-11-16.
# Usage: python3 home.py SITE   (reads SITE/index.html, keeps all English strings so lang.js still translates them)
# Then run masthead.py SITE for the shared header, then restructure.py, ai_use.py, analytics.py, apply_guide.py.
import re, sys, os, html
SITE = sys.argv[1]
P = os.path.join(SITE, 'index.html')
s = open(P, encoding='utf-8').read()
if 'class="ed-page"' in s:
    print('home already editorial'); sys.exit()

def between(a, b, src=s):
    i = src.index(a); j = src.index(b, i)
    return src[i:j]

head = s[:s.index('</head>')]
# drop the old magazine-only style block (.wrap/.mz-*), keep the nav dropdown + banana styles
head = re.sub(r'<style>\nhtml\{scroll-behavior:smooth\}.*?</style>\n', '<style>html{scroll-behavior:smooth}.wrap{max-width:1180px;margin:0 auto;padding:0 24px;box-sizing:border-box}</style>\n', head, flags=re.S)
head = head.replace('<link rel="stylesheet" href="/assets/notebook.css">', '<link rel="stylesheet" href="/assets/notebook.css">\n<link rel="stylesheet" href="/assets/editorial.css">')

bentham = between('<nav class="imr-bentham"', '<header')
nav = between('<nav aria-label="Main"', '</nav>') + '</nav>'
nav = nav.replace(' style="display: flex; flex-wrap: wrap; align-items: center; gap: 2px 22px"', '')
tail = s[s.index('<div class="imr-ridge"'):]

def articles(sec):
    return re.findall(r'<article.*?</article>', sec, flags=re.S)
ideas = between('<section id="ideas"', '</section>')
arts = []
for a in articles(ideas):
    year = re.search(r'text-transform: uppercase; color: #1E6B4A">(\d{4})</p>', a).group(1)
    title = re.search(r'<h2[^>]*>(.*?)</h2>', a, re.S).group(1)
    meta = re.findall(r'<p style="margin: 12px 0 0[^>]*>(.*?)</p>', a, re.S)[0]
    abs_ = re.findall(r'<p style="margin: 16px 0 0[^>]*>(.*?)</p>', a, re.S)[0]
    links = re.findall(r'<a class="btn" href="([^"]+)"[^>]*>(.*?)</a>', a)
    cite = re.search(r'<button.*?</button>', a, re.S)
    acts = ' '.join('<a href="%s">%s</a>' % l for l in links)
    if cite:
        c = cite.group(0)
        c = re.sub(r' class="btn"', '', c); c = re.sub(r' style="[^"]*"', '', c)
        acts += ' ' + c
    arts.append('<article class="ed-art"><span class="ed-kick">%s</span><h3>%s</h3><p class="ed-meta">%s</p><p class="ed-abs">%s</p><div class="ed-acts">%s</div></article>' % (year, title, meta, abs_, acts))

press = between('<section id="press"', '</section>')
books = re.findall(r'<li[^>]*>(.*?)</li>', press, re.S)
blis = []
for b in books:
    bid = re.search(r'id=([A-Za-z0-9_-]+)"', b).group(1)
    alt = re.sub('<[^>]+>', '', re.search(r'<i>(.*?)</i>', b).group(1))
    img = '/images/cover-%s.jpg' % bid
    im = '<img src="%s" alt="" width="52" loading="lazy">' % img if os.path.exists(os.path.join(SITE, img[1:])) else '<span></span>'
    blis.append('<li>%s<span>%s</span></li>' % (im, b))
press_series = re.search(r'font-style: italic; color: #2E493D">(.*?)</p>', press).group(1)
press_eds = re.search(r'font-size: 13px; color: #2E493D">(General Editor.*?)</p>', press).group(1)

news = between('<section id="news"', '</section>')
cited = re.findall(r'<a href="([^"]+)" style="display: flex.*?color: #BCCFC5">(.*?)</span><span[^>]*>(.*?)</span></span><span[^>]*>(.*?)</span></a>', news, re.S)
cited_html = ''.join('<a href="%s"><span class="ed-kick">%s</span><b>%s</b><span class="ed-more">%s</span></a>' % c for c in cited)
items = re.findall(r'<a href="([^"]+)" style="display: block.*?color: #1E6B4A">(.*?) · <span[^>]*>(.*?)</span></span><span[^>]*>(.*?)</span><span style="([^"]*)">(.*?)</span></a>', news, re.S)
news_html = ''
for href, src, date, title, st, summ in items:
    q = ' style="font-style:italic"' if 'italic' in st else ''
    news_html += '<a href="%s"><span class="ed-src">%s · <i>%s</i></span><b>%s</b><span class="ed-sum"%s>%s</span></a>' % (href, src, date, title, q, summ)
news_note = re.search(r'color: #2E493D">(Coverage of the Institute.*?)</p>', news).group(1)

work = between('<section id="work"', '</section>')
cards = re.findall(r'<div class="card"><div class="b"><p[^>]*>(.*?)</p><h3>(.*?)</h3><p>(.*?)</p><a class="go" href="([^"]+)">(.*?)</a></div></div>', work)
work_html = ''.join('<div class="ed-brief"><span class="ed-kick">%s</span><h3>%s</h3><p>%s</p><a class="go" href="%s">%s</a></div>' % c for c in cards)

people = between('<section id="people"', '</section>')
groups = re.findall(r'<div><p[^>]*>(.*?)</p><p style="margin: 0">(.*?)</p></div>', people)
people_html = ''.join('<div><h3>%s</h3><p>%s</p></div>' % g for g in groups)

projects = between('<section id="projects"', '</section>')
prows = re.findall(r'<li><a href="([^"]+)"><span class="mz-tag">(.*?)</span><span class="mz-pn">(.*?)</span><span class="mz-pd">(.*?)</span><span class="mz-go">(.*?)</span></a></li>', projects)
proj_html = ''.join('<div class="ed-proj"><a href="%s"><span class="ed-kick">%s</span><h3>%s</h3><p>%s</p><span class="ed-go">%s</span></a></div>' % p for p in prows)

top = between('<section id="top"', '</section>')
h1 = re.search(r'<h1[^>]*>(.*?)</h1>', top).group(1)
clinic = between('<div id="clinic-cta">', '<div id="about">', top)
c_kick = re.search(r'</span>(Free · International Legal Clinic)</p>', clinic).group(1)
c_h = re.search(r'<h2 class="mz-h2">(.*?)</h2>', clinic).group(1)
c_p = re.search(r'</h2>\n<p>(.*?)</p>', clinic).group(1)
c_btn = re.search(r'href="/legal-clinic/">(.*?)</a>', clinic).group(1)
about = between('<div id="about">', '<div>\n<p class="eyebrow"><span class="mz-n">03', top)
a_h = re.search(r'<h2 class="mz-h2">(.*?)</h2>', about).group(1)
a_ps = re.findall(r'<p>(.*?)</p>', about)
a_small = re.search(r'<p class="mz-small">(.*?)</p>', about).group(1)
a_link = re.search(r'(<a href="/legal-clinic/how-we-work/">.*?</a>)', about).group(1)
stats = re.search(r'<dl class="mz-stats">(.*?)</dl>', top, re.S).group(1)
fig = re.search(r'<figure class="mz-fig">\s*(<img[^>]*>)\s*<figcaption class="wrap">(.*?)</figcaption>', s, re.S)
img = fig.group(1).replace('src="images/', 'src="/images/').replace(' width="1600" height="560"', ' width="1280" height="873"')

def L(href, text, group=None):
    g = '<span class="ed-g">%s</span>' % group if group else ''
    return '<li>%s<a href="%s">%s</a></li>' % (g, href, text)
groups = [('Law across tiers', [('/migration-law/?lens=farm', 'Farmworker law view')]),
  ('Destination states', [('/gcc/', 'Gulf States'), ('/east-asia/', 'East Asia')] + ([('/southeast-asia/', 'Southeast Asia')] if os.path.exists(os.path.join(SITE, 'southeast-asia/index.html')) else [])),
  ('Origin states', [('/countries-of-origin/', 'Countries of Origin')]),
  ('Themes', [('/domestic-workers/', 'Migrant Domestic Workers')])]
more_db = ''.join('<div><span class="ed-g">%s</span>%s</div>' % (g, ' · '.join('<a href="%s">%s</a>' % l for l in ls)) for g, ls in groups)
# front-page rail: latest coverage (the two court citations + the two most recent press items); the rest stays in #news below
rail = ''.join('<div class="ed-brief"><span class="ed-kick">%s</span><h3><a href="%s">%s</a></h3><p><a href="%s">%s</a></p></div>' % (c[1], c[0], c[2], c[0], c[3]) for c in cited)
for href, src, date, title, st, summ in items[:2]:
    rail += '<div class="ed-brief"><span class="ed-kick">%s · %s</span><h3><a href="%s">%s</a></h3></div>' % (src, date, href, title)
news_html = ''
for href, src, date, title, st, summ in items[2:]:
    q = ' style="font-style:italic"' if 'italic' in st else ''
    news_html += '<a href="%s"><span class="ed-src">%s · <i>%s</i></span><b>%s</b><span class="ed-sum"%s>%s</span></a>' % (href, src, date, title, q, summ)

body = f'''<body>
<div class="ed-page">
{bentham}<header class="ed-mast">
<div class="ed-in">
<div class="ed-strap"><span class="ed-loc">Cianjur, West Java · Indonesia</span><span>Free legal help · Open research · Since 2007</span><a class="ed-cta cta-clinic" href="/legal-clinic/">Submit a rights communication</a></div>
<a class="ed-plate" href="/">Institute for Migrant Rights<small>Migration Jurisprudence from the South</small></a>
<div class="ed-rules"></div>
<div class="ed-navrow">
{nav}
</div>
</div>
</header>

<main id="top" class="ed-w">
<h1 class="ed-h1">{h1}</h1>

<div class="ed-front">
<section class="ed-rail" aria-label="In the news">
<span class="ed-kick" style="color:#172D24">In the news</span>
{rail}
<p style="margin:4px 0 0;font-size:14.5px;font-weight:600"><a href="#news">In the news ↓</a></p>
</section>

<article id="clinic-cta" class="ed-lead">
<figure>{img}<figcaption>{fig.group(2)}</figcaption></figure>
<span class="ed-kick">{c_kick}</span>
<h2>{c_h}</h2>
<p class="ed-dek">{c_p}</p>
<div class="ed-acts"><a class="ed-btn" href="/legal-clinic/">{c_btn}</a>{a_link.replace('<a ', '<a class="ed-more" ')}</div>
</article>

<aside id="about" class="ed-leader">
<span class="ed-kick">About</span>
<h2>{a_h}</h2>
<p>{a_ps[0]}</p>
<p class="ed-small">{a_small}</p>
<dl class="ed-stats">{stats}</dl>
</aside>
</div>

<section id="ideas" class="ed-band">
<div class="ed-shead"><h2>Ideas from the fields</h2><a href="publications.html">Publications</a></div>
<div class="ed-cols ed-821">
<div class="ed-cols ed-c2" style="padding-left:0">{''.join(arts)}</div>
<div id="work" class="ed-work"><span class="ed-kick" style="color:#172D24">Our work</span>{work_html}</div>
</div>
</section>
</main>

<section id="projects" class="ed-dark has-banana"><div class="banana" aria-hidden="true" style="right:2%;bottom:-60px;width:240px;height:312px;opacity:.10"></div>
<div class="ed-w">
<div class="ed-shead"><h2>Migration Jurisprudence from the South</h2><span>Open research projects</span></div>
<div class="ed-cols ed-c3">{proj_html}</div>
<div class="ed-moredb">{more_db}<div><a href="/databases/">All databases in Migration Jurisprudence from the South</a></div></div>
</div>
</section>

<div class="ed-w">
<section id="news" class="ed-band">
<div class="ed-shead"><h2>In the news</h2><span>{news_note}</span></div>
<div class="ed-news ed-n3">{news_html}</div>
</section>

<section id="press" class="ed-band">
<div class="ed-shead"><h2>IMR Press</h2><span style="font-family:inherit;font-style:italic">{press_series}</span></div>
<ol class="ed-books">{''.join(blis)}</ol>
<p style="margin:16px 0 0;font-size:14px;color:#2E493D"><a href="publications.html" style="font-weight:600">All IMR Press books</a> · {press_eds}</p>
</section>

<section id="people" class="ed-band ed-people">
<div class="ed-shead"><h2>People</h2><a href="people.html">People</a></div>
<div class="ed-cols ed-c4">{people_html}</div>
</section>
</div>

{tail}'''
open(P, 'w', encoding='utf-8').write(head + '</head>\n' + body)
print('home rebuilt', len(head + body))
