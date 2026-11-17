# Homepage layout models for oto (2026-11-16): A "Data desk" (data-journal style) and C "Mix" (newspaper masthead + data lead).
# Usage: python3 models.py SITE OUTDIR   (SITE = an unpacked site; writes OUTDIR/model-a.html, model-c.html using SITE's real data)
import os, sys, re, json, csv, collections, html
SITE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
def between(a, b, s=src):
    i = s.index(a); return s[i:s.index(b, i)]
bentham = between('<nav class="imr-bentham"', '<header')
nav = between('<nav aria-label="Main"', '</nav>') + '</nav>'
nav = re.sub(r'(<nav aria-label="Main")[^>]*>', r'\1 class="nav">', nav, count=1)
tail = src[src.index('<div class="imr-ridge"'):]
headfonts = re.search(r'<link rel="preconnect".*?display=swap">', src, re.S).group(0)
navcss = re.search(r'<style>\n\.nav details.*?</style>', src, re.S).group(0)

# ---------- data ----------
s = open(os.path.join(SITE, 'court-decisions/cd-data.js'), encoding='utf-8').read()
D = json.loads(s[s.index('{'):s.rindex('}') + 1])['decisions']
NDEC = len(D)
years = collections.Counter(x['date'][:4] for x in D if x.get('date'))
yr = [(y, years.get(str(y), 0)) for y in range(1996, 2026)]
REG = {'asia': 'Asia', 'africa': 'Africa', 'latam': 'Latin America', 'europe': 'Europe', 'intl': 'International bodies', 'americas': 'North America & Caribbean', 'pacific': 'Pacific', 'gulf': 'Gulf States', 'mideast': 'Middle East'}
reg = collections.Counter(x['region'] for x in D).most_common()
R = list(csv.DictReader(open(os.path.join(SITE, 'atlas/data/ratifications.csv'), encoding='utf-8')))
def cum(ins):
    ys = collections.Counter(int(x['date'][-4:]) for x in R if x['instrument'] == ins and x['date'][-4:].isdigit())
    out, t = [], 0
    for y in range(1950, 2026): t += ys.get(y, 0); out.append((y, t))
    return out
lines = {'ICRMW': cum('ICRMW'), 'C97': cum('C97'), 'C143': cum('C143'), 'C189': cum('C189')}
NCTRY = len(set(x['country'] for x in R))

# ---------- charts (inline SVG, palette tokens) ----------
INK, ACC, LIGHT, RULE, MUTE = '#172D24', '#1E6B4A', '#9CC9B2', '#B2C7BC', '#3D5A4D'
def bars(data, w=720, h=260, hi=None):
    mx = max(v for _, v in data); pad_l, pad_b, pad_t = 30, 24, 10
    bw = (w - pad_l) / len(data)
    g = []
    for t in range(0, mx + 1, 10):
        y = pad_t + (h - pad_t - pad_b) * (1 - t / mx)
        g.append(f'<line x1="{pad_l}" x2="{w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{RULE}" stroke-width="{1.4 if t==0 else .6}"/><text x="{pad_l-6}" y="{y+4:.1f}" text-anchor="end">{t}</text>')
    for i, (y, v) in enumerate(data):
        bh = (h - pad_t - pad_b) * v / mx; x = pad_l + i * bw + 1.5
        g.append(f'<rect x="{x:.1f}" y="{h-pad_b-bh:.1f}" width="{bw-3:.1f}" height="{bh:.1f}" fill="{ACC if y in (hi or []) else INK}"><title>{y}: {v}</title></rect>')
        if y % 5 == 0: g.append(f'<text x="{x+(bw-3)/2:.1f}" y="{h-6}" text-anchor="middle">{y}</text>')
    return f'<svg viewBox="0 0 {w} {h}" class="ch" role="img" aria-label="Court decisions per year">{"".join(g)}</svg>'
def hbars(data, w=380, rowh=26):
    mx = max(v for _, v in data); lab = 172; h = rowh * len(data)
    g = []
    for i, (k, v) in enumerate(data):
        y = i * rowh; bw = (w - lab - 34) * v / mx
        g.append(f'<text x="0" y="{y+17}">{html.escape(REG.get(k, k))}</text><rect x="{lab}" y="{y+5}" width="{bw:.1f}" height="{rowh-10}" fill="{INK if i else ACC}"/><text x="{lab+bw+5:.1f}" y="{y+17}" class="v">{v}</text>')
    return f'<svg viewBox="0 0 {w} {h}" class="ch" role="img" aria-label="Court decisions by region">{"".join(g)}</svg>'
def multiline(series, w=360, h=200):
    mx = max(v for s in series.values() for _, v in s); pl, pb, pt, pr = 26, 22, 8, 46
    X = lambda y: pl + (w - pl - pr) * (y - 1950) / 75; Y = lambda v: pt + (h - pt - pb) * (1 - v / mx)
    cols = {'ICRMW': ACC, 'C97': INK, 'C143': MUTE, 'C189': LIGHT}
    g = []
    for t in range(0, mx + 1, 20): g.append(f'<line x1="{pl}" x2="{w-pr}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{RULE}" stroke-width="{1.4 if t==0 else .6}"/><text x="{pl-5}" y="{Y(t)+4:.1f}" text-anchor="end">{t}</text>')
    for y in (1950, 1975, 2000, 2025): g.append(f'<text x="{X(y):.1f}" y="{h-5}" text-anchor="middle">{y}</text>')
    for k, s in series.items():
        pts = ' '.join(f'{X(y):.1f},{Y(v):.1f}' for y, v in s)
        g.append(f'<polyline points="{pts}" fill="none" stroke="{cols[k]}" stroke-width="2.4"/><text x="{X(2025)+4:.1f}" y="{Y(s[-1][1])+4:.1f}" class="v" fill="{cols[k]}">{k}</text>')
    return f'<svg viewBox="0 0 {w} {h}" class="ch" role="img" aria-label="Ratifications over time">{"".join(g)}</svg>'

CH_YEAR = bars(yr)
CH_REG = hbars(reg)
CH_RAT = multiline(lines)
peak = max(yr, key=lambda t: t[1])

CSS = '''
:root{--ink:#172D24;--soft:#2E493D;--mute:#3D5A4D;--rule:#B2C7BC;--panel:#E5EEE8;--paper:#F6F9F7;--acc:#1E6B4A;--acc2:#134A33;--mono:'JetBrains Mono',ui-monospace,monospace;--sans:'Familjen Grotesk',system-ui,sans-serif}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans)}
a{color:var(--acc)}a:hover{color:var(--acc2)}
.w{max-width:1180px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.tag{display:block;width:44px;height:8px;background:var(--acc);margin:0 0 10px}
.kick{display:block;margin:0 0 6px;font:500 12px/1.3 var(--mono);letter-spacing:.05em;text-transform:uppercase;color:var(--acc)}
.ch{display:block;width:100%;height:auto;font:11px var(--mono);fill:var(--mute)}
.ch .v{font-weight:600;fill:var(--ink)}
.src{margin:8px 0 0;font:11.5px/1.4 var(--mono);color:var(--mute)}
.fig h3{margin:0;font-size:20px;line-height:1.2;font-weight:700;letter-spacing:-.01em}
.fig .sub{margin:4px 0 12px;font-size:15px;color:var(--soft)}
.nums{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--ink);border-bottom:1px solid var(--ink)}
.nums div{padding:14px 18px}.nums div+div{border-left:1px solid var(--rule)}
.nums b{display:block;font:500 34px/1 var(--mono);color:var(--ink)}
.nums span{display:block;margin-top:6px;font-size:14px;line-height:1.35;color:var(--soft)}
.btn{display:inline-block;padding:12px 20px;background:var(--ink);color:#fff!important;text-decoration:none;font-weight:600}
.btn:hover{background:var(--acc)}
.shead{display:flex;justify-content:space-between;align-items:baseline;gap:6px 16px;flex-wrap:wrap;margin:0 0 16px;padding-top:10px;border-top:1px solid var(--ink)}
.shead h2{margin:0;font-size:22px;font-weight:700;letter-spacing:-.01em}
.shead a,.shead span{font:500 12.5px var(--mono);color:var(--mute)}
.list{list-style:none;margin:0;padding:0}
.list li{padding:10px 0;border-top:1px solid var(--rule)}
.list a{color:var(--ink);text-decoration:none;font-weight:600}.list a:hover{color:var(--acc)}
.list small{display:block;font:500 11.5px var(--mono);color:var(--acc);text-transform:uppercase;letter-spacing:.04em}
.clinic{background:var(--ink);color:#E5EEE8;padding:26px 0}
.clinic .w{display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:center}
.clinic h2{margin:0;color:#fff;font-size:28px;line-height:1.15;letter-spacing:-.02em}
.clinic p{margin:8px 0 0;color:#BCCFC5}
.clinic .btn{background:#fff;color:var(--ink)!important}.clinic .btn:hover{background:#9CC9B2}
.clinic .kick{color:#9CC9B2}
.dbgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:0}
.dbgrid>a{display:block;padding:14px 20px 18px;color:var(--ink);text-decoration:none;border-top:1px solid var(--rule)}
.dbgrid>a:not(:nth-child(3n+1)){border-left:1px solid var(--rule)}
.dbgrid>a:nth-child(3n+1){padding-left:0}
.dbgrid b{display:block;font-size:19px;line-height:1.2}.dbgrid>a:hover b{color:var(--acc)}
.dbgrid span{display:block;margin-top:4px;font-size:14.5px;line-height:1.45;color:var(--soft)}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:0}
.three>*{padding:0 22px;min-width:0}.three>*:first-child{padding-left:0}.three>*:last-child{padding-right:0}.three>*+*{border-left:1px solid var(--rule)}
.band{margin-top:40px}
/* masthead A: compact, left-aligned, data-journal */
.mA{background:#fff;border-bottom:1px solid var(--rule)}
.mA .w{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 24px;padding-top:12px;padding-bottom:12px}
.mA .brand{display:flex;align-items:center;gap:12px;color:var(--ink);text-decoration:none}
.mA .brand i{display:block;width:36px;height:36px;background:var(--acc);color:#fff;font:700 15px/36px var(--sans);text-align:center;font-style:normal}
.mA .brand b{font-size:19px;letter-spacing:-.01em}.mA .brand small{display:block;font:500 11px var(--mono);color:var(--mute);letter-spacing:.06em;text-transform:uppercase}
.mA .nav{display:flex;flex-wrap:wrap;align-items:center;gap:0 20px;font-size:14.5px;font-weight:600}
.mA .nav>a{color:var(--ink);text-decoration:none;padding:10px 0}
.mA .nav .cta-clinic{background:var(--acc);color:#fff;padding:8px 14px}
/* masthead C: newspaper nameplate */
.mC .strap{display:flex;justify-content:space-between;align-items:center;padding-top:10px;font:500 12px var(--mono);color:var(--mute)}
.mC .strap a{font:600 13px var(--sans);background:var(--acc);color:#fff;text-decoration:none;padding:8px 14px}
.mC .plate{display:block;text-align:center;padding:12px 0 10px;color:var(--ink);text-decoration:none;font:700 clamp(30px,5vw,56px)/1 var(--sans);letter-spacing:-.03em}
.mC .plate small{display:block;margin-top:8px;font:500 11.5px var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--mute)}
.mC .rules{border-top:3px solid var(--ink);border-bottom:1px solid var(--ink);height:2px}
.mC .navrow{border-bottom:1px solid var(--ink)}
.mC .nav{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;font-size:14.5px;font-weight:600}
.mC .nav>a,.mC .nav>details>summary{display:block;padding:10px 12px!important;color:var(--ink);text-decoration:none}
.mC .nav>a+a,.mC .nav>details+a,.mC .nav>details+details{border-left:1px solid var(--rule)}
.mC .nav .cta-clinic{display:none}
.nav .menu{background:#fff!important;border:1px solid var(--ink)!important}
.front{display:grid;grid-template-columns:3fr 6fr 3fr;border-top:1px solid var(--ink);margin-top:22px}
.front>*{padding:18px 22px 24px;min-width:0}.front>*:first-child{padding-left:0}.front>*:last-child{padding-right:0}.front>*+*{border-left:1px solid var(--rule)}
.lead h2{margin:0;font-size:clamp(26px,3vw,36px);line-height:1.1;letter-spacing:-.02em}
.lead .sub{margin:8px 0 14px;font-size:17px;line-height:1.45;color:var(--soft)}
.box{background:#fff;border-top:4px solid var(--acc);padding:16px 18px}
.box h3{margin:0;font-size:21px;line-height:1.2}
.box p{margin:8px 0 12px;font-size:15px;line-height:1.5;color:var(--soft)}
@media (max-width:900px){.front,.three,.dbgrid,.clinic .w{grid-template-columns:1fr}.front>*,.three>*,.dbgrid>a{padding-left:0!important;padding-right:0!important;border-left:0!important}
 .three>*+*,.front>*+*{border-top:1px solid var(--rule);margin-top:14px;padding-top:14px}.nums{grid-template-columns:1fr 1fr}.nums div:nth-child(3){border-left:0}.nums div:nth-child(n+3){border-top:1px solid var(--rule)}
 .front .lead{order:-1}}
'''

def page(title, mast, body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
{headfonts}{navcss}<style>{CSS}</style></head><body>
{bentham}{mast}{body}
{tail.replace('</div>' + chr(10) + '<script>', '<script>', 1)}'''

NUMS = f'''<div class="nums"><div><b>{NDEC}</b><span>court decisions coded, from Asia, Africa, the Middle East and Latin America first</span></div>
<div><b>{NCTRY}</b><span>countries with treaty ratification records</span></div>
<div><b>{lines['ICRMW'][-1][1]}</b><span>states parties to the UN Migrant Workers Convention</span></div>
<div><b>{lines['C189'][-1][1]}</b><span>ratifications of ILO C189 on domestic workers</span></div></div>'''
FIG_YEAR = f'''<div class="fig"><span class="tag"></span><h3>Migrant-worker cases in the database, by year</h3><p class="sub">Coded court decisions per year, 1996–2025; recent years are still being added</p>{CH_YEAR}<p class="src">Source: Migration Jurisprudence from the South, Court Decisions database (IMR). Peak year: {peak[0]} ({peak[1]} decisions).</p></div>'''
FIG_REG = f'''<div class="fig"><span class="tag"></span><h3>Where the decisions come from</h3><p class="sub">Coded decisions by region</p>{CH_REG}<p class="src">Source: IMR Court Decisions database</p></div>'''
FIG_RAT = f'''<div class="fig"><span class="tag"></span><h3>Ratifications of migrant-worker treaties</h3><p class="sub">Cumulative ratifications, 1950–2025</p>{CH_RAT}<p class="src">Source: NORMLEX, UN Treaty Collection, via the Migration Law Atlas</p></div>'''
DBS = [('/migration-law/', 'Migration Law Atlas', 'Global, regional and national migration law in one comparative explorer.'),
       ('/court-decisions/', 'Court Decisions', f'{NDEC} decisions, searchable by situation, argument and journey.'),
       ('/government-hate-speech/', 'Government Hate Speech', 'Statistics and legal frameworks for hateful speech by officials.'),
       ('/gcc/', 'Gulf States', 'Comparative notes on labor and migration law.'),
       ('/east-asia/', 'East Asia', 'Japan, Korea, Taiwan, Hong Kong and more.'),
       ('/countries-of-origin/', 'Countries of Origin', 'What sending states promise their workers abroad.'),
       ('/domestic-workers/', 'Migrant Domestic Workers', 'Instruments that cover work in private homes.'),
       ('/southeast-asia/', 'Southeast Asia', 'Destination and origin states in ASEAN.'),
       ('/legal-clinic/what-works/', 'What works where', 'Arguments that courts accepted, by jurisdiction.')]
DBG = '<div class="dbgrid">' + ''.join(f'<a href="{h}"><b>{t}</b><span>{d}</span></a>' for h, t, d in DBS) + '</div>'
CLINIC = '''<section class="clinic band"><div class="w"><div><span class="kick">Free · International Legal Clinic</span><h2>Were your rights violated? Prepare a rights communication to a UN or regional human rights body.</h2><p>Answer a few short questions. An IMR lawyer reviews the draft with you.</p></div><div><a class="btn" href="/legal-clinic/">Start your communication →</a></div></div></section>'''
IDEAS = '''<div><span class="kick">2024 · Ideas from the fields</span><h3 style="margin:0;font-size:21px;line-height:1.2"><a href="https://doi.org/10.1080/27706869.2024.2374631" style="color:inherit;text-decoration:none">Relational self and farmworker law reform: the case of Indonesia</a></h3><p style="margin:6px 0 0;font-size:14.5px;color:#2E493D">Lyon &amp; Iskandar, <i>Legal Pluralism and Critical Social Analysis</i> 56(3)</p></div>
<div><span class="kick">2018 · Ideas from the fields</span><h3 style="margin:0;font-size:21px;line-height:1.2"><a href="https://doi.org/10.1177/0964663917746485" style="color:inherit;text-decoration:none">Non-Citizen Rights in ASEAN: The Need to Chart a New Course</a></h3><p style="margin:6px 0 0;font-size:14.5px;color:#2E493D">Iskandar, <i>Social &amp; Legal Studies</i> 27(2)</p></div>'''
NEWS = '''<ul class="list"><li><small>Cited by the U.S. Court of Appeals, 9th Cir.</small><a href="https://law.justia.com/cases/federal/appellate-courts/ca9/17-15589/17-15589-2017-06-12.html"><i>Hawaii v. Trump</i> (2017)</a></li>
<li><small>Borgen Magazine · 9 October 2026</small><a href="https://www.borgenmagazine.com/indonesian-migrant-remittances/">How Indonesian migrant remittances help the economy</a></li>
<li><small>Bangkok Post · 17 March 2018</small><a href="https://www.pressreader.com/thailand/bangkok-post/20180317/281801399489386">Farmworkers and migrant labor in Asia</a></li>
<li><small>The Jakarta Post · August 2016</small><a href="https://www.thejakartapost.com/academia/2016/08/24/why-low-skilled-migration-matters.html">Why low-skilled migration matters</a></li></ul>'''

# ----- Model A: Data desk -----
mastA = f'''<header class="mA"><div class="w"><a class="brand" href="/"><i>IMR</i><span><b>Institute for Migrant Rights</b><small>Migration Jurisprudence from the South</small></span></a>{nav}</div></header>'''
bodyA = f'''<main class="w" style="padding-top:28px">
<div style="display:grid;grid-template-columns:7fr 5fr;gap:36px" class="heroA">
<div>{FIG_YEAR}</div>
<div><span class="kick">Data from the South</span><h1 style="margin:0;font-size:clamp(28px,3.4vw,42px);line-height:1.08;letter-spacing:-.025em">Migration law, collected, coded and explained.</h1>
<p style="margin:12px 0 0;font-size:18px;line-height:1.5;color:#2E493D">An initiative trying to be of some use to people who cross borders to work. Open data on treaties, statutes and court decisions, with plain-language notes and downloads.</p>
<p style="margin:18px 0 0;display:flex;gap:16px;flex-wrap:wrap;align-items:center"><a class="btn" href="/databases/">Explore the databases →</a><a href="/court-decisions/" style="font-weight:600">Court Decisions</a></p></div>
</div>
<div class="band">{NUMS}</div>
<section class="band"><div class="shead"><h2>Charts from the databases</h2><a href="/databases/">All data and downloads</a></div><div class="three">{FIG_REG}{FIG_RAT}<div><span class="tag"></span><h3 style="margin:0;font-size:20px">In the news</h3><p class="sub" style="margin:4px 0 4px;color:#2E493D">Coverage and citations</p>{NEWS}</div></div></section>
<section class="band"><div class="shead"><h2>Databases</h2><span>Migration Jurisprudence from the South</span></div>{DBG}</section>
</main>
{CLINIC}
<main class="w"><section class="band"><div class="shead"><h2>Ideas from the fields</h2><a href="/publications.html">Publications</a></div><div class="three">{IDEAS}<div><span class="kick">IMR Press · Journal</span><h3 style="margin:0;font-size:21px;line-height:1.2"><a href="https://ijicl.org" style="color:inherit;text-decoration:none">Indonesian Journal of International &amp; Comparative Law</a></h3><p style="margin:6px 0 0;font-size:14.5px;color:#2E493D">Peer-reviewed, since 2014 · <a href="/publications.html">8 IMR Press books</a></p></div></div></section></main>
<style>@media (max-width:900px){{.heroA{{grid-template-columns:1fr!important}}.heroA>div:last-child{{order:-1}}}}</style>'''
open(os.path.join(OUT, 'model-a.html'), 'w', encoding='utf-8').write(page('Model A: Data desk', mastA, bodyA))

# ----- Model C: Mix -----
mastC = f'''<header class="mC"><div class="w"><div class="strap"><span>Cianjur, West Java · Indonesia</span><a href="/legal-clinic/">Submit a rights communication</a></div>
<a class="plate" href="/">Institute for Migrant Rights<small>Migration Jurisprudence from the South</small></a><div class="rules"></div><div class="navrow">{nav}</div></div></header>'''
bodyC = f'''<main class="w"><h1 style="margin:18px auto 0;max-width:820px;text-align:center;font-size:clamp(19px,2.2vw,25px);font-weight:400;line-height:1.3;color:#2E493D">An initiative trying to be of some use to people who cross borders to work.</h1>
<div class="front">
<section><span class="kick" style="color:#172D24">In the news</span>{NEWS}</section>
<article class="lead">{FIG_YEAR}<p style="margin:14px 0 0"><a class="btn" href="/court-decisions/">Open the Court Decisions database →</a></p></article>
<aside><div class="box"><span class="kick">Free · International Legal Clinic</span><h3>Were your rights violated?</h3><p>Prepare a rights communication to a UN or regional human rights body. An IMR lawyer reviews it with you.</p><a class="btn" href="/legal-clinic/">Start →</a></div>
<div style="margin-top:18px">{FIG_REG}</div></aside>
</div>
<div class="band">{NUMS}</div>
<section class="band"><div class="shead"><h2>Migration Jurisprudence from the South</h2><a href="/databases/">All databases</a></div>{DBG}</section>
<section class="band"><div class="shead"><h2>Ideas from the fields</h2><a href="/publications.html">Publications</a></div><div class="three">{IDEAS}<div>{FIG_RAT}</div></div></section>
</main>'''
open(os.path.join(OUT, 'model-c.html'), 'w', encoding='utf-8').write(page('Model C: Mix', mastC, bodyC))
print('ok', NDEC, NCTRY, peak)
