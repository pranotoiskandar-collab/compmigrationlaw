# Builds the IMR Press pages: /press/ (all books) and one page per book at /press/<slug>/,
# using /publications.html as the page template (masthead, menu, footer).
# Also links each book on /publications.html to its own page and adds the new pages to the sitemap.
# Book facts come from the publisher's Google Books records (ISBN, series, year, pages, translator).
# Run from the repository root: python3 build/press-build/press.py. Safe to rerun.
import html, json, re

SITE = 'site'
PUB = SITE + '/publications.html'
TODAY = '2026-11-18'

BOOKS = [
    dict(slug='satu-bumi', gb='Hzs9cGMXGQUC', title='Satu Bumi', sub='Etika bagi Era Globalisasi',
         authors=['Peter Singer'], translator='Pranoto Iskandar',
         series='Perspektif IMR', vol=1, isbn='9786029648072',
         orig=('One World: The Ethics of Globalization', 'Yale University Press', '2002'),
         blurb='The case for an ethics built on shared responsibility for one planet, with a foreword by the author for this Indonesian edition.'),
    dict(slug='membela-globalisasi', gb='IWbjSy-TkBUC', title='Membela Globalisasi', sub='Melawan Okol dengan Akal',
         authors=['Jagdish Bhagwati'], translator='Pranoto Iskandar', contributors=['Hal Hill (foreword)'],
         series='Perspektif IMR', vol=4, isbn='9786027598096',
         orig=('In Defense of Globalization', 'Oxford University Press', '2004'),
         blurb=None),
    dict(slug='muslim-dan-keadilan-global', gb='-WJH9Vpk_-kC', title='Muslim dan Keadilan Global', sub=None,
         authors=['Abdullahi Ahmed An-Na’im'], translator='Jawahir Thontowi',
         series='Perspektif IMR', vol=3, isbn='9786029648096',
         orig=('Muslims and Global Justice', 'University of Pennsylvania Press', '2011'),
         blurb=None),
    dict(slug='hukum-ham-internasional', gb='THKI-DXUj44C', title='Hukum HAM Internasional', sub='Sebuah Pengantar Kontekstual',
         authors=['Pranoto Iskandar'], series='Rangkaian Studi IMR', vol=2, isbn='9786021981894', blurb=None),
    dict(slug='standar-internasional-migrasi-ketenagakerjaan', gb='SsagokPHWI4C',
         title='Standar Internasional Migrasi Ketenagakerjaan Berbasis HAM', sub=None,
         authors=['Pranoto Iskandar'], translator='Yudi Junadi', contributors=['Robyn Iredale (foreword)'],
         series='Referensi IMR', vol=1, isbn='9786029648034', year='2011', pages=208, blurb=None),
    dict(slug='tradisi-hukum-indonesia', gb='4tH3i_6dKQcC', title='Tradisi Hukum Indonesia', sub=None,
         authors=['Ratno Lukito'], contributors=['Pranoto Iskandar (postscript)'],
         series='Rangkaian Studi IMR', vol=5, isbn='9786027598089', year='2012', pages=196, blurb=None),
    dict(slug='using-world-trade-law', gb='zIREyy3DlHMC',
         title='Using World Trade Law to Promote the Interests of Global South',
         sub='A Study on the Effectiveness of Special & Differential Treatments', lang='en',
         authors=['Nandang Sutrisno'], series='Rangkaian Studi IMR', vol=1, isbn='9786029648003', blurb=None),
    dict(slug='pemajuan-kepentingan-negara-berkembang-wto', gb='Pa9jXzFr3nAC',
         title='Pemajuan Kepentingan Negara-Negara Berkembang dalam Sistem WTO', sub=None,
         authors=['Nandang Sutrisno'], translator='Susi Fauziah',
         series='Rangkaian Studi IMR', vol=4, isbn='9786027598034', year='2012', pages=276,
         orig_local='using-world-trade-law', blurb=None),
    dict(slug='relasi-negara-dan-agama', gb='C5PY486dmr8C', title='Relasi Negara & Agama',
         sub='Redefinisi Diskursus Konstitusionalisme di Indonesia',
         authors=['Yudi Junadi'], series='Rangkaian Studi IMR', vol=3, isbn='9786027598027', year='2012', blurb=None),
]
BY = {b['slug']: b for b in BOOKS}

e = lambda s: html.escape(s, quote=True)
F = "font-family: 'Figtree', sans-serif"
LBL = f"margin: 0; {F}; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: #8F5E12"
FACT_K = f"margin: 0; {F}; font-size: 12px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #8F5E12"


def isbn13(s):
    return f'{s[:3]}-{s[3:]}'  # prefix shown, rest unhyphenated (registrant ranges vary)


def full_title(b):
    return b['title'] + (': ' + b['sub'] if b.get('sub') else '')


# --- template from /publications.html ---
pub = open(PUB, encoding='utf-8').read()

# blurbs: reuse the text already on /publications.html
for a in re.findall(r'<article.*?</article>', pub, re.S):
    gb = re.search(r'books\?id=([\w-]+)', a).group(1)
    ps = re.findall(r'<p[^>]*>(.*?)</p>', a, re.S)
    for b in BOOKS:
        if b['gb'] == gb and not b['blurb']:
            b['blurb'] = html.unescape(re.sub('<.*?>', '', ps[1]))

head_end = pub.index('</head>')
body_start = pub.index('<section', head_end)
foot_start = pub.rindex('</section>') + len('</section>')
HEAD, TOP, FOOT = pub[:head_end], pub[head_end:body_start], pub[foot_start:]
# absolute paths, since the new pages sit two folders down
for rel in ['favicon.ico', 'favicon-32.png', 'apple-touch-icon.png', 'contact.html', 'people.html', 'publications.html']:
    HEAD = HEAD.replace(f'href="{rel}"', f'href="/{rel}"')
    TOP = TOP.replace(f'href="{rel}"', f'href="/{rel}"')
    FOOT = FOOT.replace(f'href="{rel}"', f'href="/{rel}"')
HEAD = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', HEAD, flags=re.S)


def page(title, desc, url, ld, main, lang='en'):
    h = HEAD
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', h)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(title)}">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(desc)}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h)
    h = h.replace('<!-- imr-analytics -->', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n<!-- imr-analytics -->')
    return h + TOP + main + FOOT


PUBLISHER = {'@type': 'Organization', 'name': 'Institute for Migrant Rights Press', 'alternateName': 'IMR Press',
             'url': 'https://theimr.org/press/',
             'address': {'@type': 'PostalAddress', 'addressLocality': 'Cianjur', 'addressRegion': 'Jawa Barat', 'addressCountry': 'ID'}}


def book_ld(b):
    url = f'https://theimr.org/press/{b["slug"]}/'
    d = {'@context': 'https://schema.org', '@type': 'Book', '@id': url, 'url': url, 'name': full_title(b),
         'author': [{'@type': 'Person', 'name': a} for a in b['authors']],
         'publisher': PUBLISHER, 'isbn': b['isbn'], 'inLanguage': b.get('lang', 'id'),
         'image': f'https://theimr.org/images/cover-{b["gb"]}.jpg',
         'isPartOf': {'@type': 'BookSeries', 'name': b['series']}, 'position': b['vol'],
         'description': b['blurb'], 'sameAs': f'https://books.google.com/books?id={b["gb"]}'}
    if b.get('translator'):
        d['translator'] = {'@type': 'Person', 'name': b['translator']}
    if b.get('year'):
        d['datePublished'] = b['year']
    if b.get('pages'):
        d['numberOfPages'] = b['pages']
    if b.get('orig'):
        t, p, y = b['orig']
        d['translationOfWork'] = {'@type': 'Book', 'name': t, 'author': [{'@type': 'Person', 'name': a} for a in b['authors']],
                                  'publisher': {'@type': 'Organization', 'name': p}, 'datePublished': y, 'inLanguage': 'en'}
    if b.get('orig_local'):
        o = BY[b['orig_local']]
        d['translationOfWork'] = {'@id': f'https://theimr.org/press/{o["slug"]}/'}
    return d


def byline(b):
    s = ', '.join(b['authors'])
    if b.get('translator'):
        s += f' · translated by {b["translator"]}'
    return s


def book_main(b):
    facts = []
    if b.get('orig'):
        t, p, y = b['orig']
        facts.append(('Original edition', f'<i>{e(t)}</i> ({e(p)}, {y})'))
    if b.get('orig_local'):
        o = BY[b['orig_local']]
        facts.append(('Original edition', f'<a href="/press/{o["slug"]}/"><i>{e(o["title"])}</i></a> (IMR Press)'))
    facts.append(('Author', e(', '.join(b['authors']))))
    if b.get('translator'):
        facts.append(('Translator', e(b['translator'])))
    if b.get('contributors'):
        facts.append(('With', e(', '.join(b['contributors']))))
    facts.append(('Series', f'{e(b["series"])}, volume {b["vol"]}'))
    if b.get('year'):
        facts.append(('Published', b['year']))
    if b.get('pages'):
        facts.append(('Pages', str(b['pages'])))
    facts.append(('Language', 'English' if b.get('lang') == 'en' else 'Indonesian'))
    facts.append(('ISBN', f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 15px">{isbn13(b["isbn"])}</span>'))
    facts.append(('Publisher', 'IMR Press (Institute for Migrant Rights Press), Cianjur, Indonesia'))
    dl = ''.join(f'<div><dt style="{FACT_K}">{k}</dt><dd style="margin: 4px 0 0">{v}</dd></div>' for k, v in facts)
    sub = f'<p style="margin: 8px 0 0; font-size: 24px; line-height: 1.3; color: #4A3B2D"><i>{e(b["sub"])}</i></p>' if b.get('sub') else ''
    lang = ' lang="en"' if b.get('lang') == 'en' else ' lang="id"'
    return f'''<section style="padding: 72px 0 80px">
<div style="max-width: 1120px; margin: 0 auto; padding: 0 24px">
<p style="{LBL}"><a href="/press/" style="color: inherit">IMR Press</a> · Books</p>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(300px,100%),1fr)); gap: 32px 56px; align-items: start; margin-top: 20px">
<div style="display: grid; grid-template-columns: 120px minmax(0, 1fr); gap: 24px; align-items: start">
<img src="/images/cover-{b["gb"]}.jpg" alt="Cover of {e(b["title"])}" style="display: block; width: 120px; height: auto; border: 1px solid #C8BCB1">
<div>
<h1{lang} style="margin: 0; font-weight: 400; font-size: 40px; line-height: 1.15"><i>{e(b["title"])}</i></h1>
{sub}
<p style="margin: 12px 0 0; {F}; font-size: 16px; color: #4A3B2D">{e(byline(b))}</p>
<p style="margin: 18px 0 0">{e(b["blurb"])}</p>
<p style="margin: 22px 0 0; display: flex; flex-wrap: wrap; gap: 10px 28px; {F}; font-size: 15px; font-weight: 600"><a href="https://books.google.com/books?id={b["gb"]}">View on Google Books →</a></p>
</div>
</div>
<dl style="margin: 0; display: grid; grid-template-columns: 1fr; gap: 14px; font-size: 17px; background: #E8E2DC; border: 1px solid #C8BCB1; padding: 22px 24px">{dl}</dl>
</div>
<p style="margin: 48px 0 0; {F}; font-size: 15px; font-weight: 600"><a href="/press/">← All IMR Press books</a></p>
</div>
</section>
'''


def card(b):
    return (f'<article style="padding: 28px 0; border-bottom: 1px solid #C8BCB1; display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 20px; align-items: start">'
            f'<a href="/press/{b["slug"]}/"><img src="/images/cover-{b["gb"]}.jpg" alt="Cover of {e(b["title"])}" style="display: block; width: 64px; height: auto; border: 1px solid #C8BCB1"></a><div>'
            f'<h2 style="margin: 0; font-weight: 500; font-size: 23px; line-height: 1.3"><a href="/press/{b["slug"]}/" style="color: inherit; text-decoration: none"><i>{e(full_title(b))}</i></a></h2>'
            f'<p style="margin: 6px 0 0; {F}; font-size: 15px; color: #4A3B2D">{e(byline(b))}</p>'
            + (f'<p style="margin: 6px 0 0; {F}; font-size: 15px; color: #4A3B2D">Indonesian edition of <i>{e(b["orig"][0])}</i></p>' if b.get('orig') else '')
            + f'<p style="margin: 10px 0 0; font-size: 17px">{e(b["blurb"])}</p>'
            f'<a href="/press/{b["slug"]}/" style="display: inline-block; margin-top: 10px; {F}; font-size: 15px; font-weight: 600">About this book →</a></div></article>')


def press_main():
    cards = '\n'.join(card(b) for b in BOOKS)
    return f'''<section style="padding: 88px 0 40px">
<div style="max-width: 760px; margin: 0 auto; padding: 0 24px; text-align: center">
<p style="{LBL}">Institute for Migrant Rights</p>
<h1 style="margin: 16px 0 0; font-weight: 400; font-size: 54px; line-height: 1.1">IMR Press</h1>
<p style="margin: 18px 0 0; color: #4A3B2D">IMR Press (Institute for Migrant Rights Press) is the publishing house of the Institute for Migrant Rights in Cianjur, West Java. It publishes books in contemporary legal studies, mainly international and comparative law, including Indonesian editions of Peter Singer, Jagdish Bhagwati and Abdullahi Ahmed An-Na’im, and the <a href="https://ijicl.org">Indonesian Journal of International &amp; Comparative Law</a>.</p>
<p style="margin: 14px 0 0; color: #4A3B2D">Three series: Rangkaian Studi IMR (international and comparative law), Perspektif IMR (interdisciplinary work on pressing global questions) and Referensi IMR. Every manuscript goes through peer review.</p>
</div>
</section>

<section style="padding: 0 0 80px">
<div style="max-width: 1120px; margin: 0 auto; padding: 0 24px; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(320px,100%),1fr)); gap: 0 48px">
{cards}
</div>
<p style="max-width: 1120px; margin: 32px auto 0; padding: 0 24px; {F}; font-size: 15px; font-weight: 600"><a href="/publications.html">The journal and all publications →</a></p>
</section>
'''


import os
os.makedirs(f'{SITE}/press', exist_ok=True)
press_ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'url': 'https://theimr.org/press/', 'name': 'IMR Press books',
            'publisher': PUBLISHER, 'hasPart': [{'@id': f'https://theimr.org/press/{b["slug"]}/'} for b in BOOKS]}
open(f'{SITE}/press/index.html', 'w', encoding='utf-8').write(page(
    'IMR Press · Institute for Migrant Rights Press, Indonesia',
    'IMR Press, the publishing house of the Institute for Migrant Rights in Cianjur, Indonesia: books in international and comparative law, and Indonesian editions of Peter Singer, Jagdish Bhagwati and Abdullahi Ahmed An-Na’im.',
    'https://theimr.org/press/', press_ld, press_main()))

for b in BOOKS:
    os.makedirs(f'{SITE}/press/{b["slug"]}', exist_ok=True)
    if b.get('orig'):
        title = f'{b["title"]} ({b["orig"][0]}) · {b["authors"][0]} · IMR Press'
        desc = f'Indonesian edition of {b["authors"][0]}’s {b["orig"][0]}' + (f', translated by {b["translator"]}' if b.get('translator') else '') + f'. {b["blurb"]} IMR Press, ISBN {isbn13(b["isbn"])}.'
    else:
        title = f'{full_title(b)} · {b["authors"][0]} · IMR Press'
        desc = f'{full_title(b)} by {", ".join(b["authors"])}' + (f', translated by {b["translator"]}' if b.get('translator') else '') + f'. {b["blurb"]} IMR Press, ISBN {isbn13(b["isbn"])}.'
    open(f'{SITE}/press/{b["slug"]}/index.html', 'w', encoding='utf-8').write(
        page(title, desc, f'https://theimr.org/press/{b["slug"]}/', book_ld(b), book_main(b)))

# --- /publications.html: link each book to its page, and the IMR Press label to /press/ ---
for b in BOOKS:
    pat = re.compile(r'(<article[^>]*>)(<img src="images/cover-' + re.escape(b['gb']) + r'\.jpg"[^>]*>)(<div><h2[^>]*>)(<i>.*?</i>)(</h2>)')
    pub = pat.sub(lambda m: m.group(1) + f'<a href="/press/{b["slug"]}/">' + m.group(2) + '</a>' + m.group(3)
                  + f'<a href="/press/{b["slug"]}/" style="color: inherit; text-decoration: none">' + m.group(4) + '</a>' + m.group(5), pub, count=1)
    pub = pub.replace(f'<a href="https://books.google.com/books?id={b["gb"]}" style="display: inline-block; margin-top: 10px;',
                      f'<a href="/press/{b["slug"]}/" style="display: inline-block; margin-top: 10px; margin-right: 24px; {F}; font-size: 15px; font-weight: 600">About this book</a><a href="https://books.google.com/books?id={b["gb"]}" style="display: inline-block; margin-top: 10px;', 1)
pub = pub.replace('<h2 style="margin: 12px 0 0; font-weight: 400; font-size: 36px; line-height: 1.2">Books</h2>',
                  '<h2 style="margin: 12px 0 0; font-weight: 400; font-size: 36px; line-height: 1.2"><a href="/press/" style="color: inherit; text-decoration: none">Books</a></h2>', 1)
open(PUB, 'w', encoding='utf-8').write(pub)

# --- sitemap ---
sm = open(f'{SITE}/sitemap.xml', encoding='utf-8').read()
sm = re.sub(r'  <url><loc>https://theimr.org/press/[^<]*</loc><lastmod>[^<]*</lastmod></url>\n', '', sm)
new = ''.join(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n'
              for u in ['https://theimr.org/press/'] + [f'https://theimr.org/press/{b["slug"]}/' for b in BOOKS])
sm = sm.replace('  <url><loc>https://theimr.org/publications.html</loc><lastmod>2026-11-11</lastmod></url>\n',
                f'  <url><loc>https://theimr.org/publications.html</loc><lastmod>{TODAY}</lastmod></url>\n' + new, 1)
assert new in sm
open(f'{SITE}/sitemap.xml', 'w', encoding='utf-8').write(sm)
print('built', len(BOOKS), 'book pages')
