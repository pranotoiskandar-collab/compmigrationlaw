# One-page country sheets for workers going abroad, in English and Indonesian.
# Reads the repository's own data and writes, for each origin country and language:
#   site/country-sheets/<cc>-<lang>.pdf   A4, for printing
#   site/country-sheets/<cc>-<lang>.jpg   phone-width image, for WhatsApp
# plus site/country-sheets/index.html, the download page.
#
# Sources (nothing is typed in by hand except the plain-language wording in text.py):
#   data/countries-of-origin/codings.csv, protection.csv, laws-policies.csv
#   site/legal-help/places.js            (verified phone numbers only)
#   data/court-decisions/decisions.csv   (plain_en / plain_id summaries)
#
# Usage, from the repository root:
#   python3 build/country-sheets/build.py            # all countries
#   python3 build/country-sheets/build.py ID NP      # some countries
# Needs: python3 with qrcode (pip install qrcode), node with playwright.
import csv, datetime, html, io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from text import COUNTRY_NAMES, FEATURES, LEVEL, MONTHS, T  # noqa: E402

OUT = os.path.join(ROOT, 'site', 'country-sheets')
WORK = os.path.join(HERE, 'html')
ORDER = ['ID', 'PH', 'NP', 'BD', 'VN', 'IN', 'LK', 'PK']
LANGS = ['en', 'id']
SITE = 'https://theimr.org'

# Court decisions to show, chosen for relevance to people working abroad.
# Only decisions with status S or P, outcome "won" and both plain summaries are used;
# a country without a pick falls back to the newest qualifying origin-court decision.
CASE_PICKS = {
    'ID': ['mk-127-2023', 'mk-050-2013'],
    'PH': ['serrano-2009', 'sameer-2014'],
    'NP': ['np-welfare-fund-2020', 'np-free-visa-2019'],
}

# Help entries to show for Indonesia (the directory has 22; one page fits about seven).
ID_HELP = ['YLBHI', 'LBH Jakarta', 'LBH Bandung', 'SBMI', 'Migrant CARE', 'KP2MI']
# Indonesian names for the Indonesian sheet (the directory gives English names).
NAME_ID = {
    'YLBHI': 'YLBHI (Yayasan Lembaga Bantuan Hukum Indonesia), kantor pusat',
    'SBMI': 'SBMI (Serikat Buruh Migran Indonesia)',
    'KP2MI': 'KP2MI (Kementerian Pelindungan Pekerja Migran Indonesia)',
    'Indonesian embassies': 'KBRI dan KJRI di negara tujuan (Perlindungan WNI)',
}
COURT_ID = {
    'Constitutional Court of Indonesia': 'Mahkamah Konstitusi',
    'Supreme Court of the Philippines': 'Mahkamah Agung Filipina',
    'Supreme Court of Nepal': 'Mahkamah Agung Nepal',
}
CROSS_BORDER = {'Justice Without Borders': None, 'Indonesian embassies': 'ID'}


def esc(s):
    return html.escape(s or '', quote=True)


def read_csv(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_places():
    js = open(os.path.join(ROOT, 'site', 'legal-help', 'places.js'), encoding='utf-8').read()
    out = subprocess.run(['node', '-e', 'global.window={};eval(require("fs").readFileSync(0,"utf8"));'
                          'process.stdout.write(JSON.stringify(window.LEGAL_HELP))'],
                         input=js, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def nice_date(d, lang):
    return f'{d.day} {MONTHS[lang][d.month - 1]} {d.year}'


def first_sentence(s):
    m = re.match(r'(.+?[.!?])(\s|$)', s or '')
    return m.group(1) if m else (s or '')


def web_label(u):
    u = re.sub(r'^https?://(www\.)?', '', u or '').rstrip('/')
    return u.split('/')[0] if len(u) > 34 else u


def qr_svg(url):
    import qrcode
    import qrcode.image.svg
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    buf = io.BytesIO(); img.save(buf)
    s = buf.getvalue().decode()
    s = re.sub(r'<\?xml[^>]*>', '', s)
    s = re.sub(r'width="[^"]*mm" height="[^"]*mm"', 'width="100%" height="100%"', s, count=1)
    return s


ICONS = {
    'coin': '<circle cx="12" cy="12" r="8"/><path d="M14.5 9.5c-.6-.9-1.5-1.3-2.5-1.3-1.4 0-2.5.8-2.5 1.9 0 2.7 5 1.4 5 4 0 1.1-1.1 1.9-2.5 1.9-1.1 0-2-.4-2.6-1.3M12 6.5v1.7M12 15.9v1.6"/>',
    'doc': '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M9.5 12h6M9.5 15h6M9.5 18h4"/>',
    'class': '<path d="M3 9l9-4 9 4-9 4z"/><path d="M7 11v4.5c1.5 1.3 3.2 2 5 2s3.5-.7 5-2V11M21 9v5"/>',
    'shield': '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    'phone': '<path d="M6.5 3.5h3l1.5 4-2 1.3a10 10 0 005.2 5.2l1.3-2 4 1.5v3a2 2 0 01-2 2A15 15 0 014.5 5.5a2 2 0 012-2z"/>',
    'scale': '<path d="M12 4v16M8 20h8M5 7h14M5 7l-2.5 6a2.5 2.5 0 005 0zM19 7l-2.5 6a2.5 2.5 0 005 0z"/>',
    'house': '<path d="M3.5 11L12 4l8.5 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>',
    'flag': '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
}


def icon(name, cls='ic'):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def pick_cases(cc, decisions):
    ok = {d['id']: d for d in decisions
          if d['country'] == cc and d['outcome'] == 'won' and d['status'] in ('S', 'P')
          and d['plain_en'] and d['plain_id']}
    picks = [ok[i] for i in CASE_PICKS.get(cc, []) if i in ok]
    if not picks and cc not in CASE_PICKS:
        picks = sorted((d for d in ok.values() if d['forum'] == 'origin'), key=lambda d: d['date'], reverse=True)[:2]
    return picks


def pick_help(cc, places):
    rows = [p for p in places if p['c'] == cc and not p.get('lbh')]
    if cc == 'ID':
        rows = [p for key in ID_HELP for p in places if p['c'] == 'ID' and p['n'].startswith(key)]
    for p in places:
        if p['c'] == 'XB':
            for key, only in CROSS_BORDER.items():
                if p['n'].startswith(key) and (only is None or only == cc):
                    rows.append(p)
    return rows


def pick_laws(cc, laws):
    rows = [r for r in laws if r['s'] == cc and r['type'] == 'statute']
    return rows[:3]


def law_title(r, lang):
    # The Indonesian sheet shows the official Indonesian title for Indonesian laws.
    if lang == 'id' and r['s'] == 'ID' and r['orig']:
        return r['orig']
    return r['title']


def sheet(cc, lang, data, today):
    L = 0 if lang == 'en' else 1
    cname = COUNTRY_NAMES[cc][L]
    cap = cname[0].upper() + cname[1:]
    t = lambda k, **kw: T[k][L].format(**kw)
    cod = {r['feature']: r for r in data['codings'] if r['country'] == cc}
    cod.update({r['feature']: r for r in data['protection'] if r['country'] == cc})

    rows = []
    for key, ic, labels, ans in FEATURES:
        r = cod.get(key)
        if not r:
            continue
        v = int(r['value'])
        rows.append(
            f'<li class="f v{v}">{icon(ic)}<div><div class="fl"><b>{esc(labels[L])}</b>'
            f'<span class="lv"><i></i>{esc(LEVEL[v][L])}</span></div>'
            f'<p>{esc(ans[v][L])}</p></div></li>')

    laws = ''.join(f'<li>{esc(law_title(r, lang))}</li>' for r in pick_laws(cc, data['laws']))

    helps = []
    for p in pick_help(cc, data['places']):
        tel = ' · '.join(esc(x) for x in (p.get('tel') or [])[:2])
        d = first_sentence(p.get('d_id') if lang == 'id' and p.get('d_id') else p.get('d'))
        city = p.get('city_id') if lang == 'id' and p.get('city_id') else p.get('city')
        name = p['n']
        if lang == 'id':
            name = next((v for k, v in NAME_ID.items() if name.startswith(k)), name)
        if p['c'] == 'XB':
            city = None
        if city:
            city = city.split(',')[0]
        helps.append(
            f'<li><b>{esc(name)}</b>' + (f' <span class="city">{esc(city)}</span>' if city and cc == 'ID' else '') +
            (f'<div class="tel">{icon("phone", "ic s")}{tel}</div>' if tel else '') +
            (f'<div class="web">{esc(web_label(p.get("web")))}</div>' if p.get('web') else '') +
            f'<p>{esc(d)}</p></li>')
    has_phone = any(p.get('tel') for p in pick_help(cc, data['places']) if p['c'] == cc)
    help_none = '' if has_phone else f'<p class="none">{esc(t("help_none", c=cname))}</p>'

    cases = pick_cases(cc, data['decisions'])
    if cases:
        case_html = ''.join(
            f'<li><p>{esc(d["plain_" + lang])}</p><div class="cite">{esc(COURT_ID.get(d["court"], d["court"]) if lang == "id" else d["court"])}, {esc(d["date"][:4])} · {esc(d["citation"] if lang == "id" and d["citation"] else d["name"])}</div></li>'
            for d in cases)
        case_html = f'<ul class="cases">{case_html}</ul><p class="small">{esc(t("cases_note"))}</p>'
    else:
        case_html = f'<p class="none">{esc(t("cases_none", c=cname))}</p>'

    tips = ''.join(f'<li>{esc(x[L])}</li>' for x in T['tips'])
    lh = f'{SITE}/legal-help/' + ('?lang=id' if lang == 'id' else '')
    more = f'{SITE}/countries-of-origin/'

    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(t("title", c=cname))}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="../sheet.css">
</head><body>
<main class="page">
<header class="hero">
  <div class="hills">{data["hills"]}</div>
  <div class="ht">
    <div class="org">Institute for Migrant Rights · theimr.org</div>
    <h1>{esc(t("title", c=cname))}</h1>
    <p class="sub">{esc(t("sub", c=cname))}</p>
  </div>
</header>
<div class="cols">
  <section class="law">
    <h2>{esc(t("law_h", c=cname))}</h2>
    <ul class="feat">{"".join(rows)}</ul>
    <p class="small">{esc(t("law_note"))}</p>
    <h3>{esc(t("laws_h"))}</h3>
    <ul class="laws">{laws}</ul>
    <div class="tips">
      <h2>{esc(t("tips_h"))}</h2>
      <ol>{tips}</ol>
    </div>
  </section>
  <section class="side">
    <div class="help">
      <h2>{icon("phone", "ic h")}{esc(t("help_h"))}</h2>
      {help_none}
      <ul class="hl">{"".join(helps)}</ul>
      <p class="small">{esc(t("help_note"))}</p>
    </div>
    <div class="court">
      <h2>{icon("scale", "ic h")}{esc(t("cases_h"))}</h2>
      {case_html}
    </div>
  </section>
</div>
<footer class="foot">
  <div class="qr"><div class="code">{qr_svg(lh)}</div><div><b>{esc(t("qr_help"))}</b><span>theimr.org/legal-help</span></div></div>
  <div class="qr"><div class="code">{qr_svg(more)}</div><div><b>{esc(t("qr_more"))}</b><span>theimr.org/countries-of-origin</span></div></div>
  <div class="qr"><div class="code">{qr_svg(SITE + '/updates/')}</div><div><b>{esc(t("qr_updates"))}</b><span>theimr.org/updates</span></div></div>
  <p class="made"><b>{esc(t("disclaimer"))}</b> {esc(t("made", d=nice_date(today, lang)))}</p>
</footer>
</main>
</body></html>'''


def index_page(done, today):
    # Uses the head, header and footer of an existing site page so the look follows the site.
    tpl = open(os.path.join(ROOT, 'site', 'ai-use', 'index.html'), encoding='utf-8').read()
    head_end = tpl.index('</header>') + len('</header>')
    foot_start = tpl.index('<div class="imr-ridge"') if '<div class="imr-ridge"' in tpl else tpl.index('<footer')
    top, bottom = tpl[:head_end], tpl[foot_start:]
    title = 'Country sheets to print and share'
    desc = ('One-page sheets for people going abroad to work: what the law of their country says, '
            'where to get free help, and court decisions that helped workers. In English and Indonesian.')
    top = re.sub(r'<title>.*?</title>', f'<title>{title} · Institute for Migrant Rights</title>', top, flags=re.S)
    top = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + desc, top)
    top = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + title, top)
    top = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + desc, top)
    top = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>https://theimr.org/country-sheets/', top)
    top = top.replace('https://theimr.org/ai-use/', 'https://theimr.org/country-sheets/')
    top = re.sub(r'<script type="application/ld\+json">.*?</script>',
                 '<script type="application/ld+json">' + json.dumps({
                     "@context": "https://schema.org", "@type": "WebPage", "name": title,
                     "url": "https://theimr.org/country-sheets/", "description": desc,
                     "inLanguage": ["en", "id"], "license": "https://creativecommons.org/licenses/by/4.0/"}) + '</script>',
                 top, count=1, flags=re.S)
    cards = []
    for cc in [c for c in ORDER if c in done]:
        en = COUNTRY_NAMES[cc][0].replace('the ', '')
        links = ' '.join(
            f'<a class="cs-btn" href="{cc.lower()}-{lg}.pdf" download data-goatcounter-click="country-sheet-{cc.lower()}-{lg}-pdf">'
            f'{"English" if lg == "en" else "Bahasa Indonesia"} · PDF</a>'
            f'<a class="cs-btn alt" href="{cc.lower()}-{lg}.jpg" data-goatcounter-click="country-sheet-{cc.lower()}-{lg}-png">'
            f'{"Image for WhatsApp" if lg == "en" else "Gambar untuk WhatsApp"}</a>'
            for lg in LANGS)
        cards.append(f'<li class="cs-card"><a href="{cc.lower()}-en.jpg"><img src="{cc.lower()}-en-thumb.jpg" alt="" loading="lazy" width="300" height="424"></a>'
                     f'<h3>{esc(en)}</h3><div class="cs-links">{links}</div></li>')
    body = f'''
<main class="wrap" style="max-width:1120px;margin:0 auto;padding:40px 20px 24px">
<style>
.cs-intro{{max-width:760px;font-size:18px;line-height:1.55}}
.cs-grid{{list-style:none;padding:0;margin:28px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:22px}}
.cs-card{{background:#fff;border:1px solid var(--rule,#B2C7BC);border-radius:10px;padding:14px}}
.cs-card img{{width:100%;height:auto;display:block;border:1px solid #DCE8E1;border-radius:4px}}
.cs-card h3{{margin:12px 0 8px;font-size:19px}}
.cs-links{{display:flex;flex-wrap:wrap;gap:6px}}
.cs-btn{{display:inline-block;font-size:13.5px;font-weight:600;padding:7px 10px;border-radius:6px;background:#1E6B4A;color:#fff!important;text-decoration:none}}
.cs-btn.alt{{background:transparent;color:#1E6B4A!important;border:1px solid #1E6B4A}}
.cs-how{{max-width:760px;font-size:16px;line-height:1.55}}
</style>
<h1>{title}</h1>
<p class="cs-intro">One page for each country. Each sheet says, in plain words, what the law of the worker's own country promises before departure and while abroad, lists free help with checked phone numbers, and summarises court decisions that helped workers. Clinics, unions, embassies and families can print them or send them on WhatsApp.</p>
<ul class="cs-grid">{"".join(cards)}</ul>
<div class="cs-how">
<h2>Where the content comes from</h2>
<p>The sheets are made automatically from our open data: the <a href="/countries-of-origin/">Countries of Origin</a> database (law), the <a href="/legal-help/">Find legal help</a> directory (help, with phone numbers only where checked), and <a href="/court-decisions/">Court Decisions</a> (summaries). The short answers restate the database codes in everyday words; the database pages give the legal sources. This is general information, not legal advice. Last made on {nice_date(today, "en")}.</p>
<p>Free to copy, print and share under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. To suggest a correction, <a href="/contact.html">write to us</a>.</p>
</div>
</main>
'''
    return top + body + bottom


def i18n_block():
    # Indonesian strings for the download page, added to the site switch (assets/lang.js).
    d = {
        'Country sheets to print and share': 'Lembar negara untuk dicetak dan dibagikan',
        "One page for each country. Each sheet says, in plain words, what the law of the worker's own country promises before departure and while abroad, lists free help with checked phone numbers, and summarises court decisions that helped workers. Clinics, unions, embassies and families can print them or send them on WhatsApp.":
            'Satu halaman untuk setiap negara. Setiap lembar menjelaskan dengan bahasa sederhana apa yang dijanjikan hukum negara asal pekerja sebelum keberangkatan dan selama di luar negeri, mencantumkan bantuan gratis dengan nomor telepon yang telah diperiksa, serta meringkas putusan pengadilan yang membantu pekerja. Klinik hukum, serikat pekerja, perwakilan, dan keluarga dapat mencetaknya atau mengirimkannya melalui WhatsApp.',
        'Where the content comes from': 'Asal isi lembar',
        'Image for WhatsApp': 'Gambar untuk WhatsApp',
        'One-page country sheets to print or send on WhatsApp →': 'Lembar negara satu halaman untuk dicetak atau dikirim melalui WhatsApp →',
    }
    return d


def patch_lang():
    # Adds the download page's Indonesian strings to the site language switch. Idempotent.
    p = os.path.join(ROOT, 'site', 'assets', 'lang.js')
    js = open(p, encoding='utf-8').read()
    head = 'window.SITE_I18N={"id":{'
    if head not in js:
        print('lang.js: dictionary start not found, Indonesian strings not added'); return
    add = ''.join(json.dumps(k, ensure_ascii=False) + ':' + json.dumps(v, ensure_ascii=False) + ','
                  for k, v in i18n_block().items() if json.dumps(k, ensure_ascii=False) + ':' not in js)
    if add:
        open(p, 'w', encoding='utf-8').write(js.replace(head, head + add, 1))


def patch_links(today):
    # Lists the page in the sitemap and llms.txt and links it from Find legal help. Idempotent.
    url = 'https://theimr.org/country-sheets/'
    p = os.path.join(ROOT, 'site', 'sitemap.xml'); x = open(p, encoding='utf-8').read()
    line = f'  <url><loc>{url}</loc><lastmod>{today.isoformat()}</lastmod></url>'
    x = re.sub(r'  <url><loc>' + re.escape(url) + r'</loc>.*?</url>\n', '', x)
    open(p, 'w', encoding='utf-8').write(x.replace('</urlset>', line + '\n</urlset>'))
    p = os.path.join(ROOT, 'site', 'llms.txt'); x = open(p, encoding='utf-8').read()
    if url not in x:
        anchor = '- [Find legal help](https://theimr.org/legal-help/)'
        i = x.index(anchor); j = x.index('\n', i) + 1
        x = x[:j] + f'- [Country sheets]({url}): one-page sheets (PDF and image, English and Indonesian) for workers from origin countries: what their law says, free help with checked phone numbers, court decisions\n' + x[j:]
        open(p, 'w', encoding='utf-8').write(x)
    p = os.path.join(ROOT, 'site', 'legal-help', 'index.html'); x = open(p, encoding='utf-8').read()
    if '/country-sheets/' not in x:
        h = '<h1 class="lh-h1">Find free legal help near you</h1>'
        x = x.replace(h, h + '\n<p class="lh-sheets" style="margin:6px 0 0;font-size:15px"><a href="/country-sheets/">One-page country sheets to print or send on WhatsApp →</a></p>', 1)
        open(p, 'w', encoding='utf-8').write(x)


def main():
    want = [a.upper() for a in sys.argv[1:]] or ORDER
    today = datetime.date.today()
    hills = open(os.path.join(HERE, 'hills.svg'), encoding='utf-8').read()
    hills = hills.replace('preserveAspectRatio="xMinYMax slice"', 'preserveAspectRatio="xMidYMax slice"')
    data = {
        'codings': read_csv('data', 'countries-of-origin', 'codings.csv'),
        'protection': read_csv('data', 'countries-of-origin', 'protection.csv'),
        'laws': read_csv('data', 'countries-of-origin', 'laws-policies.csv'),
        'decisions': read_csv('data', 'court-decisions', 'decisions.csv'),
        'places': load_places()['places'],
        'hills': hills,
    }
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    jobs = []
    for cc in want:
        for lg in LANGS:
            name = f'{cc.lower()}-{lg}'
            with open(os.path.join(WORK, name + '.html'), 'w', encoding='utf-8') as f:
                f.write(sheet(cc, lg, data, today))
            jobs.append(name)
    subprocess.run(['node', os.path.join(HERE, 'render.js'), WORK, OUT, *jobs], check=True)
    done = sorted({f.split('-')[0].upper() for f in os.listdir(OUT) if f.endswith('-en.pdf')})
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_page(done, today))
    patch_lang()
    patch_links(today)
    print('sheets:', ', '.join(jobs))


if __name__ == '__main__':
    main()
