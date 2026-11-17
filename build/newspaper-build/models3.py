# Model F "Mix and match" (2026-11-16): header from A, unit chart from E, journey from D, three questions from E, charts row from A.
# Usage: python3 models3.py SITE OUTDIR
import os, sys, runpy
SITE, OUT = sys.argv[1], sys.argv[2]
G = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models2.py'), run_name='models2')
g = lambda k: G[k]
Q3 = [q for q in g('Q') if q[0] in ('/court-decisions/', '/court-decisions/#argument', '/legal-clinic/')]
q3 = ''.join(f'<a href="{h}"><span class="q">{q}</span><span class="n">{n}</span><span class="ans">{a}</span><span class="lk">{l} →</span></a>' for h, q, n, a, l in Q3)
oc = g('oc'); NDEC = g('NDEC')
body = f'''<main class="w"><section class="hero split">
<div><span class="kick">Institute for Migrant Rights · Cianjur, West Java</span><h1 style="font-size:clamp(32px,4vw,52px)">Migration law, collected, coded and explained.</h1>
<p>An initiative trying to be of some use to people who cross borders to work: free legal help for workers and families, open data for researchers.</p>
<p style="margin-top:18px;display:flex;flex-wrap:wrap;gap:10px"><a class="btn" href="/legal-clinic/" style="background:#1E6B4A">Get legal help →</a><a class="btn" href="/databases/">Explore the data →</a></p></div>
<figure style="margin:0"><figcaption style="margin:0 0 10px;font:700 17px/1.3 var(--sans)">{NDEC} court decisions on migrant workers. Each square is one.</figcaption>
<div class="units" role="img" aria-label="{NDEC} squares, one per decision">{g('units')}</div>
<div class="legend"><span style="--c:#1E6B4A">Worker side won ({oc["won"]})</span><span style="--c:#9CC9B2">Advisory ({oc["advisory"]})</span><span style="--c:#172D24">Worker side lost ({oc["lost"]})</span><span style="--c:transparent;--b:1">To be checked ({oc["unknown"]})</span></div>
<p class="src" style="font-size:11.5px;margin-top:10px">Source: IMR Court Decisions database. <a href="/court-decisions/">Explore the decisions →</a></p></figure>
</section>
<section class="band"><div class="shead"><h2>Where are you on the journey?</h2><span>Pick a step: the law, the decisions, the help</span></div>
<div class="road">{g('ridge')}<div class="stops">{g('stops')}</div></div></section>
<section class="band"><div class="shead"><h2>Questions people ask us</h2><span>Short answers from the databases</span></div><div class="qgrid">{q3}</div></section>
</main>
{g('CLINIC')}
<main class="w">
<section class="band"><div class="shead"><h2>Charts from the databases</h2><a href="/databases/">All data and downloads</a></div><div class="three">{G['G']['FIG_YEAR']}{G['G']['FIG_RAT']}<div><span class="tag"></span><h3 style="margin:0;font-size:20px">In the news</h3>{g('NEWS')}</div></div></section>
<section class="band"><div class="shead"><h2>Migration Jurisprudence from the South</h2><a href="/databases/">All databases</a></div>{g('DBG')}</section>
<section class="band"><div class="shead"><h2>Ideas from the fields</h2><a href="/publications.html">Publications</a></div><div class="three">{g('IDEAS')}<div><span class="kick">IMR Press · Journal</span><h3 style="margin:0;font-size:21px;line-height:1.2"><a href="https://ijicl.org" style="color:inherit;text-decoration:none">Indonesian Journal of International &amp; Comparative Law</a></h3><p style="margin:6px 0 0;font-size:14.5px;color:#2E493D">Peer-reviewed, since 2014 · <a href="/publications.html">All IMR Press books</a></p></div></div></section>
</main>
<style>{g('EXTRA')}</style>'''
open(os.path.join(OUT, 'model-f.html'), 'w', encoding='utf-8').write(g('page')('Model F: Mix and match', g('mastA'), body))
print('ok')
