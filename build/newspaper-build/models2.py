# Two more homepage models for oto (2026-11-16): D "Along the journey" and E "Ask the law" (unit chart + plain questions).
# Usage: python3 models2.py SITE OUTDIR   (reuses helpers/data from models.py)
import os, sys, runpy, json, collections, html
SITE, OUT = sys.argv[1], sys.argv[2]
G = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models.py'), run_name='models')
page, mastA, D, NDEC, lines = G['page'], G['mastA'], G['D'], G['NDEC'], G['lines']
CLINIC, NEWS, IDEAS, NUMS, DBG = G['CLINIC'], G['NEWS'], G['IDEAS'], G['NUMS'], G['DBG']
SITN = {'wages': 'Wages not paid', 'passport': 'Passport kept by employer', 'employer': 'Could not change employer', 'dismissed': 'Dismissed or sent home',
        'forced': 'Forced labour or trafficking', 'injury': 'Hurt or injured at work', 'fees': 'Recruitment and the agency', 'union': 'Joining a union',
        'discrimination': 'Treated worse as a foreigner', 'housing': 'Living in the employer’s home', 'residence': 'Residence and staying on',
        'arrest': 'Arrested, detained or expelled', 'health': 'Health care', 'coverage': 'Who the law protects', 'welfare': 'Food and support in a crisis'}

EXTRA = '''
.hero{padding:34px 0 10px}
.hero h1{margin:0;font-size:clamp(34px,4.6vw,58px);line-height:1.02;letter-spacing:-.03em;max-width:900px}
.hero p{margin:14px 0 0;max-width:720px;font-size:19px;line-height:1.5;color:var(--soft)}
/* journey */
.road{position:relative;margin:30px 0 0}
.road svg.line{position:absolute;left:0;right:0;top:0;width:100%;height:56px}
.stops{display:grid;grid-template-columns:repeat(5,1fr);gap:0;position:relative}
.stop{padding:0 16px 0;min-width:0}.stop:first-child{padding-left:0}.stop:last-child{padding-right:0}
.stop .dot{display:flex;align-items:center;justify-content:center;width:56px;height:56px;border-radius:50%;background:var(--ink);color:#fff;font:600 22px var(--mono);position:relative;z-index:1;box-shadow:0 0 0 6px var(--paper)}
.stop.now .dot{background:var(--acc)}
.stop h2{margin:14px 0 0;font-size:22px;line-height:1.15;letter-spacing:-.01em}
.stop .what{margin:6px 0 0;font-size:15px;color:var(--soft);line-height:1.45;min-height:44px}
.stop .meter{margin:12px 0 0;padding-top:10px;border-top:1px solid var(--rule);font:12px var(--mono);color:var(--mute)}
.stop .meter i{display:block;height:6px;background:var(--acc);margin:6px 0 4px}
.stop ul{list-style:none;margin:8px 0 0;padding:0;font-size:14.5px;line-height:1.35}
.stop ul li{padding:5px 0;border-top:1px dotted #6F8A7D}
.stop ul a{color:var(--ink);text-decoration:none}.stop ul a:hover{color:var(--acc)}
.stop .go{display:flex;flex-direction:column;gap:6px;margin-top:12px;font-weight:600;font-size:14.5px}
.stop .go a.help{display:inline-block;background:var(--ink);color:#fff;text-decoration:none;padding:8px 12px;align-self:flex-start}
.stop .go a.help:hover{background:var(--acc)}
@media (max-width:900px){
 .road svg.line{display:none}
 .stops{grid-template-columns:1fr;border-left:3px solid var(--ink);margin-left:26px}
 .stop,.stop:first-child,.stop:last-child{padding:0 0 26px 0}
 .stop .dot{margin-left:-30px;width:52px;height:52px;font-size:20px}
 .stop>*:not(.dot){margin-left:34px}.stop h2{margin-top:-40px}
 .stop .what{min-height:0}}
/* unit chart + questions */
.units{display:grid;grid-template-columns:repeat(46,1fr);gap:3px;max-width:620px}
.units i{display:block;aspect-ratio:1;background:transparent;box-shadow:inset 0 0 0 1px #9AB3A6}
.units i.won{background:var(--acc)}.units i.lost{background:var(--ink)}.units i.adv{background:#9CC9B2}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin:12px 0 0;font:12.5px var(--mono);color:var(--mute)}
.legend span[style*='--b']::before{box-shadow:inset 0 0 0 1px #9AB3A6}.legend span::before{content:"";display:inline-block;width:11px;height:11px;margin-right:6px;vertical-align:-1px;background:var(--c)}
.qgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid var(--ink)}
.qgrid a{display:flex;flex-direction:column;padding:20px 22px 22px;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}
.qgrid a:not(:nth-child(3n+1)){border-left:1px solid var(--rule)}.qgrid a:nth-child(3n+1){padding-left:0}
.qgrid .q{font-size:23px;line-height:1.18;font-weight:700;letter-spacing:-.015em}
.qgrid .n{margin:14px 0 0;font:500 40px/1 var(--mono);color:var(--acc)}
.qgrid .ans{margin:6px 0 0;font-size:15px;line-height:1.45;color:var(--soft);flex:1}
.qgrid .lk{margin-top:12px;font-weight:600;font-size:14.5px;color:var(--acc)}
.qgrid a:hover .q{color:var(--acc)}
.split{display:grid;grid-template-columns:5fr 7fr;gap:40px;align-items:center}
@media (max-width:900px){.split{grid-template-columns:1fr;gap:20px}.qgrid{grid-template-columns:1fr}.qgrid a{padding-left:0!important;border-left:0!important}}
@media (max-width:600px){.units{grid-template-columns:repeat(23,1fr)}}
'''

# ---------- D: Along the journey ----------
STAGES = [
 (1, 'Recruitment at home', 'Fees, agencies, false promises',
  [('/countries-of-origin/', 'Countries of Origin'), ('/legal-clinic/trafficking-check/', 'Could this be trafficking? Self-check')], ('/legal-help/', 'Find free legal help')),
 (2, 'Leaving the country', 'Exit rules, visas, documents',
  [('/countries-of-origin/', 'Countries of Origin'), ('/migration-law/', 'Migration Law Atlas')], ('/legal-help/', 'Find free legal help')),
 (3, 'Working abroad', 'Wages, hours, passport, abuse, unions',
  [('/gcc/', 'Gulf States'), ('/east-asia/', 'East Asia'), ('/southeast-asia/', 'Southeast Asia'), ('/domestic-workers/', 'Migrant Domestic Workers')], ('/legal-clinic/what-works/', 'What works where')),
 (4, 'Changing or losing the job', 'Changing employer, dismissal',
  [('/legal-clinic/what-works/', 'What works where'), ('/court-decisions/', 'Court Decisions')], ('/legal-clinic/', 'Prepare a rights communication')),
 (5, 'Return and after', 'Claims from home, residence',
  [('/court-decisions/', 'Court Decisions'), ('/legal-clinic/how-we-work/', 'How the Clinic works')], ('/legal-clinic/', 'Prepare a rights communication')),
]
counts = {st: [x for x in D if st in x['stages']] for st, *_ in STAGES}
mx = max(len(v) for v in counts.values())
stops = ''
for st, name, what, links, help_ in STAGES:
    sub = counts[st]; top = collections.Counter(s for x in sub for s in x['situations']).most_common(2)
    stops += (f'<div class="stop{" now" if st == 3 else ""}"><span class="dot">{st}</span><h2>{name}</h2><p class="what">{what}</p>'
              f'<div class="meter">{len(sub)} court decisions<i style="width:{100*len(sub)/mx:.0f}%"></i>Most often: {", ".join(SITN[k].lower() for k, _ in top)}</div>'
              f'<ul>{"".join(f"<li><a href=\"{h}\">{t}</a></li>" for h, t in links)}</ul>'
              f'<div class="go"><a class="help" href="{help_[0]}">{help_[1]} →</a></div></div>')
ridge = ('<svg class="line" viewBox="0 0 1000 56" preserveAspectRatio="none" aria-hidden="true">'
         '<path d="M0 28 L1000 28" stroke="#172D24" stroke-width="3"/><path d="M0 28 L1000 28" stroke="#9CC9B2" stroke-width="3" stroke-dasharray="2 14" transform="translate(0 0)"/></svg>')
bodyD = f'''<main class="w"><section class="hero"><span class="kick">Migration law, step by step</span>
<h1>Where are you on the journey?</h1>
<p>Pick the step that fits your situation. Each one leads to the law that applies, the court decisions on it, and where to get help.</p></section>
<div class="road">{ridge}<div class="stops">{stops}</div></div>
<p class="src" style="margin-top:18px">Decision counts: IMR Court Decisions database ({NDEC} decisions; one decision can concern several steps).</p>
</main>
{CLINIC}
<main class="w"><div class="band">{NUMS}</div>
<section class="band"><div class="shead"><h2>For researchers</h2><a href="/databases/">All data and downloads</a></div>{DBG}</section>
<section class="band"><div class="shead"><h2>Ideas from the fields</h2><a href="/publications.html">Publications</a></div><div class="three">{IDEAS}<div><span class="kick">In the news</span>{NEWS}</div></div></section></main>
<style>{EXTRA}</style>'''
open(os.path.join(OUT, 'model-d.html'), 'w', encoding='utf-8').write(page('Model D: Along the journey', mastA, bodyD))

# ---------- E: Ask the law ----------
oc = collections.Counter(x['outcome'] for x in D)
order = sorted(D, key=lambda x: {'won': 0, 'advisory': 1, 'lost': 2}.get(x['outcome'], 3))
cls = {'won': 'won', 'lost': 'lost', 'advisory': 'adv'}
units = ''.join(f'<i class="{cls.get(x["outcome"], "")}" title="{html.escape(x["name"])}"></i>' for x in order)
npass = sum('passport' in x['situations'] for x in D)
nstat = sum(any(a.get('a') == 'status' and a.get('ok') for a in x.get('args', [])) for x in D)
Q = [('/court-decisions/', 'Can my employer keep my passport?', npass, 'court decisions deal with a passport kept by the employer. See what the courts said.', 'Read the decisions'),
     ('/court-decisions/#argument', 'Do I have rights if my papers are not in order?', nstat, 'decisions accepted that labor rights apply whatever a worker’s immigration status.', 'Arguments that work'),
     ('/migration-law/', 'Has my country joined the Migrant Workers Convention?', lines['ICRMW'][-1][1], 'states are parties so far. Check any country in the Atlas.', 'Open the Atlas'),
     ('/legal-clinic/trafficking-check/', 'Could this be trafficking?', 'Private', 'A free self-check: answer short questions and get a result sheet you can keep.', 'Start the self-check'),
     ('/legal-help/', 'Where can I find free legal help?', 10, 'countries covered, with checked phone numbers and addresses.', 'Find help near you'),
     ('/legal-clinic/', 'Can I take my case to the UN?', 'Free', 'The Clinic drafts a rights communication with you, and an IMR lawyer reviews it.', 'Prepare a communication')]
qhtml = ''.join(f'<a href="{h}"><span class="q">{q}</span><span class="n">{n}</span><span class="ans">{a}</span><span class="lk">{l} →</span></a>' for h, q, n, a, l in Q)
bodyE = f'''<main class="w"><section class="hero split">
<div><span class="kick">Migration Jurisprudence from the South</span><h1 style="font-size:clamp(32px,4vw,50px)">{NDEC} court decisions on migrant workers. Each square is one.</h1>
<p>Workers won {oc["won"]} of them and lost {oc["lost"]}. Another {oc["unknown"]} are still being checked. Most come from courts in Asia, Africa, the Middle East and Latin America.</p>
<p style="margin-top:18px"><a class="btn" href="/court-decisions/">Explore the decisions →</a></p></div>
<div><div class="units" role="img" aria-label="{NDEC} squares, one per decision">{units}</div>
<div class="legend"><span style="--c:#1E6B4A">Worker side won ({oc["won"]})</span><span style="--c:#9CC9B2">Advisory: rights affirmed ({oc["advisory"]})</span><span style="--c:#172D24">Worker side lost ({oc["lost"]})</span><span style="--c:transparent;--b:1">Outcome to be checked ({oc["unknown"]})</span></div></div>
</section>
<section class="band"><div class="shead"><h2>Questions people ask us</h2><span>Short answers from the databases</span></div><div class="qgrid">{qhtml}</div></section>
<section class="band"><div class="shead"><h2>Migration Jurisprudence from the South</h2><a href="/databases/">All databases</a></div>{DBG}</section>
<section class="band"><div class="shead"><h2>Ideas from the fields</h2><a href="/publications.html">Publications</a></div><div class="three">{IDEAS}<div><span class="kick">In the news</span>{NEWS}</div></div></section>
</main>
<style>{EXTRA}</style>'''
open(os.path.join(OUT, 'model-e.html'), 'w', encoding='utf-8').write(page('Model E: Ask the law', mastA, bodyE))
print('ok', {k: len(v) for k, v in counts.items()}, oc, npass, nstat)
