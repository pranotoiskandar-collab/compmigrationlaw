# Phone-width fixes for theimr.org (2026-11-17). Idempotent. Run after apply_guide.py / apply_v2.py.
# Usage: python3 responsive.py SITE
# 1) grid columns minmax(Npx, 1fr) -> minmax(min(Npx,100%), 1fr): grids no longer push past a 320-414px screen.
# 2) appends a small safety block to /assets/editorial.css (form controls, long links, media never wider than the screen).
import os, re, sys
SITE = sys.argv[1]
RX = re.compile(r'minmax\(\s*(\d+(?:\.\d+)?px)\s*,\s*1fr\s*\)')
n = 0
for root, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith(('.html', '.css', '.js')): continue
        p = os.path.join(root, f); s = open(p, encoding='utf-8').read()
        t = RX.sub(lambda m: 'minmax(min(%s,100%%),1fr)' % m.group(1), s)
        if t != s: open(p, 'w', encoding='utf-8').write(t); n += 1
CSS = '''
/* responsive safety (responsive.py) */
@media (max-width:760px){
 main select,main input:not([type=checkbox]):not([type=radio]),main textarea{max-width:100%}
 main li a,main p a,main dd,main td a{overflow-wrap:anywhere}
 main img,main video,main iframe{max-width:100%;height:auto}
 }
@media (max-width:480px){
 h1,h2,h3{overflow-wrap:break-word;hyphens:auto}
 h1[style*="font-size"]{font-size:clamp(32px,10.5vw,48px)!important}
 .st-out,.g-grid3,.ww-two,.checkwrap,.charts,.elements{grid-template-columns:minmax(0,1fr)!important}
 .st-out>*,.g-grid3>*,.ww-two>*,.checkwrap>*,.charts>*,.elements>*{min-width:0}
}
'''
CSS2 = '''
/* journey columns line up (responsive.py) */
@media (min-width:901px){
 .stops{grid-template-rows:repeat(6,auto)}
 .stop{display:grid;grid-row:span 6;grid-template-rows:subgrid;align-content:start}
 .stop>.dot{align-self:start}.stop .what{min-height:0}.stop .go{align-self:start}
}
'''
CSS3 = '''
/* calmer phone layout (responsive.py, oto 2026-11-17: phone site too crowded) */
@media (max-width:600px){
 .imr-bentham .imr-bnext,.imr-bentham a{display:none!important}
 .imr-bentham>div{padding:6px 16px!important;font-size:13px}
 .ed-brand small{display:none}
 body[data-home=f] .hero .kick{display:none}
 body[data-home=f] .hero h1{font-size:34px!important}
 body[data-home=f] .hero p{font-size:17px}
 body[data-home=f] .units{grid-template-columns:repeat(46,1fr)!important;gap:1.5px!important}
 body[data-home=f] .stop .meter,body[data-home=f] .stop ul{display:none}
 body[data-home=f] .stop .go{margin-top:10px}
 body[data-home=f] .stop,body[data-home=f] .stop:first-child,body[data-home=f] .stop:last-child{padding-bottom:22px}
 body[data-home=f] .dbgrid a span{display:none}
 body[data-home=f] #news+ul li:nth-child(n+3){display:none}
 body[data-home=f] .band{padding-top:28px!important;padding-bottom:28px!important}
}
'''
p = os.path.join(SITE, 'assets', 'editorial.css'); s = open(p, encoding='utf-8').read()
if 'calmer phone layout' not in s: s += CSS3
if 'responsive safety' not in s: s += CSS
if 'journey columns line up' not in s: s += CSS2
open(p, 'w', encoding='utf-8').write(s)
print('grid fixes in', n, 'files')
