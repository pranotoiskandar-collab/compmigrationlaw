import json, os, html, sys
SP=os.path.dirname(os.path.abspath(__file__))
R=lambda f: open(os.path.join(SP,f),encoding='utf-8').read()
T=R('template.html')
NEWS=json.load(open(os.path.join(SP,'news.json')))
base={'__DATA__':R('data_block.js'),'__MIGRATION__':R('migration_block.js'),'__IMPL__':R('impl_block.js')+R('cases_block.js')+R('recs_block.js')+R('corridors_block.js')+R('cov_block.js')+R('stats_block.js'),'__STATSLIB__':R('stats.js'),'__NEWS__':json.dumps(NEWS,ensure_ascii=False),
      '__RATS__':R('rats.json'),'__COUNTRIES__':R('countries.json'),'__TOPO__':R('topo.json')}
SIGNUP_ART='''<div class="signup"><h3>Get these updates by email</h3><p class="muted">Sign up on <a href="https://theimr.org/migration-law/#news" target="_blank" rel="noopener">theimr.org</a>, or follow the <a href="https://theimr.org/feed.xml" target="_blank" rel="noopener">RSS feed</a>.</p></div>'''
SIGNUP_SITE='''<div class="signup" id="signup">
      <h3>Get significant developments by email</h3>
      <p class="muted">We send a short note when a new law, court ruling or ratification changes migration or farmworker law. You can unsubscribe at any time. You can also follow the <a href="/feed.xml">RSS feed</a>.</p>
      <form name="news-signup" method="POST" action="/news-thanks.html" data-netlify="true" netlify-honeypot="bot-field">
        <input type="hidden" name="form-name" value="news-signup">
        <p hidden><label>Leave this empty <input name="bot-field"></label></p>
        <input type="email" name="email" required placeholder="Your email address" aria-label="Your email address" autocomplete="email">
        <label class="note"><input type="checkbox" name="topics" value="migration" checked> Migration law</label>
        <label class="note"><input type="checkbox" name="topics" value="farmworkers" checked> Farmworker law</label>
        <button class="btn primary" type="submit">Sign up</button>
      </form>
    </div>'''
TITLES={'mig':'Migration Law Atlas','farm':'Farmworker Norms Atlas'}
def dataset_ld(lens, desc, canon):
    base = 'https://theimr.org/'
    files = ([('Migration law norms', 'migration-law/data/migration-norms.csv')] if lens == 'mig' else [('Farmworker law norms', 'atlas/data/farmworker-norms.csv')]) + [
        ('Ratifications by country', 'atlas/data/ratifications.csv'), ('Country indicators and ratification scores', 'atlas/data/country-indicators.csv'),
        ('Domestic implementation assessments', 'atlas/data/implementation.csv'), ('Key court and committee decisions', 'atlas/data/cases.csv')]
    d = {'@context': 'https://schema.org', '@type': 'Dataset', 'name': TITLES[lens].split(' · ')[0], 'description': desc, 'url': canon,
         'dateModified': '2026-11-11', 'inLanguage': ['en', 'id'], 'isAccessibleForFree': True,
         'keywords': ['migrant workers', 'farmworkers', 'agricultural workers', 'labor law', 'migration law', 'ILO conventions', 'treaty ratification', 'domestic implementation', 'comparative law', 'human rights'],
         'creator': {'@type': 'Organization', 'name': 'Institute for Migrant Rights', 'url': base},
         'publisher': {'@type': 'Organization', 'name': 'Institute for Migrant Rights', 'url': base},
         'spatialCoverage': {'@type': 'Place', 'name': 'Worldwide'}, 'temporalCoverage': '1919/2026',
         'distribution': [{'@type': 'DataDownload', 'name': n, 'encodingFormat': 'text/csv', 'contentUrl': base + f} for n, f in files]}
    return json.dumps(d, ensure_ascii=False).replace('</', '<\\/')

def page(lens, backlink, signup, locked=False):
    s=T.replace('__LOCKED__','true' if locked else 'false')
    for k,v in base.items(): s=s.replace(k,v)
    s=s.replace('__LENS__',lens).replace('__TITLE__',TITLES[lens]).replace('__BACKLINK__',backlink).replace('__SIGNUP__',signup)
    assert '__' not in ''.join(x for x in ['__LENS__','__TITLE__','__SIGNUP__','__BACKLINK__','__DATA__','__NEWS__'] if x in s), 'placeholder left'
    return s
SITE_NAV_CSS="""<style>
body{margin:0}
.imr-hd{background:#E5EEE8;border-bottom:1px solid #B2C7BC;margin:-28px calc(-1 * max(16px,env(safe-area-inset-left,0px))) 8px;font-family:'Familjen Grotesk',system-ui,sans-serif;font-size:14px;color:#172D24}
.imr-hd .in{max-width:1180px;margin:0 auto;padding:14px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 28px}
.imr-hd .brand{color:#172D24;text-decoration:none;font-weight:600;letter-spacing:.12em;text-transform:uppercase}
.imr-hd nav{display:flex;flex-wrap:wrap;align-items:center;gap:2px 22px}
.imr-hd nav a{color:#172D24;text-decoration:none;padding:10px 0}
.imr-hd details{position:relative}
.imr-hd summary{cursor:pointer;padding:10px 0;list-style:none;font-weight:600}
.imr-hd summary::-webkit-details-marker{display:none}
.imr-hd summary::after{content:" \\25BE";font-size:11px}
.imr-hd .menu{position:absolute;right:0;top:100%;z-index:40;min-width:230px;background:#DCE8E1;border:1px solid #B2C7BC;padding:6px 0}
.imr-hd .menu a{display:block;padding:8px 16px}
.imr-hd .menu a[aria-current]{font-weight:600}
@media (max-width:640px){.imr-hd .menu{right:auto;left:0}}
</style>"""
NAV_JS="<script>document.addEventListener('click',function(e){document.querySelectorAll('.imr-hd details[open]').forEach(function(d){if(!d.contains(e.target))d.removeAttribute('open');});});</script>"
def site_nav(current):
    items=[('/migration-law/','Migration Law Atlas'),('/atlas/','Farmworker Norms Atlas'),('/government-hate-speech/','Government Hate Speech')]
    menu='\n'.join(f'<a href="{h}"'+(' aria-current="page"' if h==current else '')+f'>{t}</a>' for h,t in items)
    return f"""<header class="imr-hd"><div class="in">
<a class="brand" href="/">Institute for Migrant Rights</a>
<nav aria-label="Main">
<a href="/legal-clinic/">Legal Clinic</a>
<a href="/legal-help/">Find legal help</a>
<details>
<summary>Projects</summary>
<div class="menu">
{menu}
</div>
</details>
<details>
<summary>Migration and Labor Laws in Comparison</summary>
<div class="menu">
<a href="/gcc/">Gulf States</a>
<a href="/east-asia/">East Asia</a>
<a href="/countries-of-origin/">Countries of Origin</a>
<a href="/hate-speech-voting/">Hate Speech and Voting</a>
<a href="/court-decisions/">Court Decisions</a>
</div>
</details>
<a href="/publications.html">IMR Press</a>
<a href="https://ijicl.org">Journal</a>
<a href="/people.html">People</a>
<a href="/contact.html">Contact</a>
<a class="cta-clinic" href="/legal-clinic/" style="background:#1E6B4A;color:#FFFFFF;text-decoration:none;padding:9px 16px;border-radius:2px;font-weight:600;white-space:nowrap">Submit a rights communication</a>
</nav>
</div></header>
"""+NAV_JS
def standalone(lens, canon, current):
    full=page(lens,'',SIGNUP_SITE,locked=(lens=='farm')).replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
    i=full.index('<div class="wrap">'); headpart, bodypart = full[:i], full[i:]
    desc='Compare migration law across global, regional and national tiers, with farmworker law as a subset. Ranked norms, ratifications, country profiles, news and downloadable data.' if lens=='mig' else 'Ranked register of the international, regional and national law on farm work, with ratifications, country profiles, news and downloadable data.'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Institute for Migrant Rights">
<meta property="og:title" content="{html.escape(TITLES[lens])}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://theimr.org/images/rice-fields-cianjur-1975.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{dataset_ld(lens, desc, canon)}</script>
<link rel="alternate" type="application/rss+xml" title="Institute for Migrant Rights: migration and farmworker law news" href="/feed.xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400;500;600;700&display=swap">
{headpart}{SITE_NAV_CSS}
</head>
<body>
{site_nav(current)}
{bodypart}
<script src="/assets/lang.js" defer></script>
<script src="/assets/plain.js" defer></script>
</body>
</html>
"""
def rss():
    import datetime, email.utils
    items=[]
    for n in NEWS:
        d=n[0] if len(n[0])==10 else n[0]+'-28'
        dt=datetime.datetime.strptime(d,'%Y-%m-%d').replace(hour=12,tzinfo=datetime.timezone.utc)
        items.append(f"""<item><title>{html.escape(n[4])}</title><link>{html.escape(n[7])}</link><guid isPermaLink="false">imr-news-{n[0]}-{__import__("hashlib").md5(n[4].encode()).hexdigest()[:10]}</guid><pubDate>{email.utils.format_datetime(dt)}</pubDate><category>{html.escape(", ".join(n[2]))}</category><description>{html.escape(n[5]+" Source: "+n[6]+".")}</description></item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Institute for Migrant Rights: migration and farmworker law news</title>
<link>https://theimr.org/migration-law/#news</link>
<description>Significant developments in migration law and farmworker law: new laws, court rulings and ratifications.</description>
<language>en</language>
{chr(10).join(items)}
</channel></rss>
"""
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else os.path.join(SP,'farmworker-norms.html')
    open(out,'w',encoding='utf-8').write(page('mig','',SIGNUP_ART))
    print('wrote',out,len(open(out).read()))
    if len(sys.argv)>2:
        site=sys.argv[2]
        for d,lens,canon in [('atlas','farm','https://theimr.org/atlas/'),('migration-law','mig','https://theimr.org/migration-law/')]:
            os.makedirs(os.path.join(site,d),exist_ok=True)
            open(os.path.join(site,d,'index.html'),'w',encoding='utf-8').write(standalone(lens,canon,'/'+d+'/'))
        open(os.path.join(site,'feed.xml'),'w',encoding='utf-8').write(rss())
        open(os.path.join(site,'assets','stats.js'),'w',encoding='utf-8').write(R('stats.js'))
        import subprocess; subprocess.run(['node',os.path.join(os.path.dirname(os.path.abspath(__file__)),'gen_data.js'),site],check=True)
        print('site files in',site)
