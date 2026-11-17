# Adds model D's journey (five big picture buttons) to the Legal Clinic page, above the form's stage rail. Idempotent.
# Usage: python3 clinic_journey.py SITE
# Plain words for readers with limited literacy; each step opens a short panel with what to do and where to go next.
import os, sys
SITE = sys.argv[1]
P = os.path.join(SITE, 'legal-clinic', 'index.html')
s = open(P, encoding='utf-8').read()
if 'id="lc-journey"' in s:
    print('already there'); sys.exit()
I = lambda d: f'<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
ICONS = [
    I('<path d="M8 22 24 9l16 13"/><path d="M12 19v20h24V19"/><path d="M20 39V28h8v11"/>'),                      # home
    I('<path d="M6 30l36-14-6 18-10-4-6 8v-10"/><path d="M26 30 42 16"/>'),                                       # leaving (paper plane)
    I('<rect x="7" y="16" width="34" height="22" rx="2"/><path d="M18 16v-5h12v5"/><path d="M7 26h34"/>'),           # work
    I('<path d="M20 8H9v32h11"/><path d="M27 16l8 8-8 8"/><path d="M35 24H17"/>'),                                 # job lost / leave
    I('<path d="M40 24a16 16 0 1 1-5-11.6"/><path d="M40 8v8h-8"/>'),                                             # return
]
STEPS = [
    ('Before you leave', 'An agent, fees or a promise of a job',
     'Keep every receipt and message from the agent. Ask for your contract in your own language before you pay anything.',
     [('/legal-clinic/trafficking-check/', 'Could this be trafficking? Self-check'), ('/countries-of-origin/', 'What your government promises'), ('/legal-help/', 'Find free legal help')]),
    ('Leaving the country', 'Papers, visa, exit rules',
     'Keep a copy of your passport, visa and contract with your family. Note the phone number of your embassy.',
     [('/countries-of-origin/', 'What your government promises'), ('/legal-help/', 'Find free legal help')]),
    ('Working abroad', 'Pay, hours, passport, abuse',
     'In most countries an employer may not keep your passport. Write down unpaid wages, dates and hours. Courts have ruled for workers in cases like these.',
     [('/legal-clinic/what-works/', 'What works where'), ('/legal-help/', 'Find free legal help'), ('#wiz', 'Prepare a rights communication')]),
    ('Losing or changing the job', 'Sent away, arrested, cannot change employer',
     'Ask for a letter that says why the job ended. If you are detained, ask to contact your embassy.',
     [('/legal-clinic/what-works/', 'What works where'), ('#wiz', 'Prepare a rights communication')]),
    ('Back home', 'Claims after you return',
     'In many cases you can still make a claim after you come home. Keep your documents. The Clinic can help you take the case to an international body.',
     [('#wiz', 'Prepare a rights communication'), ('/legal-help/', 'Find free legal help')]),
]
btns = ''.join(f'<button type="button" class="jy-b" data-j="{i}" aria-expanded="false"><span class="jy-n">{i+1}</span>{ICONS[i]}<b>{t}</b><span class="jy-d">{d}</span></button>' for i, (t, d, _, _) in enumerate(STEPS))
panels = ''.join(f'<div class="jy-p" data-j="{i}" hidden><p>{tip}</p><p class="jy-l">{"".join(f"<a href=\"{h}\">{l} →</a>" for h, l in links)}</p></div>' for i, (_, _, tip, links) in enumerate(STEPS))
CSS = '''<style>
#lc-journey{max-width:1120px;margin:8px auto 28px;padding:0 24px;box-sizing:border-box}
#lc-journey h2{margin:0 0 4px;font-size:26px;letter-spacing:-.01em}
#lc-journey .jy-sub{margin:0 0 16px;color:#2E493D;font-size:17px}
.jy-row{display:grid;grid-template-columns:repeat(5,1fr);gap:0;position:relative}
.jy-row::before{content:"";position:absolute;left:4%;right:4%;top:44px;border-top:3px dashed #9AB3A6;z-index:0}
.jy-b{all:unset;box-sizing:border-box;cursor:pointer;position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;padding:10px 8px 14px;color:#172D24;border-radius:4px}
.jy-b svg{width:62px;height:62px;padding:13px;box-sizing:border-box;border-radius:50%;background:#172D24;color:#fff;box-shadow:0 0 0 6px #E5EEE8}
.jy-b .jy-n{position:absolute;top:4px;left:calc(50% + 22px);width:24px;height:24px;border-radius:50%;background:#1E6B4A;color:#fff;font:600 13px/24px 'JetBrains Mono',monospace;z-index:2}
.jy-b b{font-size:18px;line-height:1.2}
.jy-b .jy-d{font-size:14.5px;line-height:1.35;color:#2E493D}
.jy-b:hover svg,.jy-b[aria-expanded="true"] svg{background:#1E6B4A}
.jy-b[aria-expanded="true"]{background:#FFFFFF;box-shadow:inset 0 -4px 0 #1E6B4A}
.jy-b:focus-visible{outline:3px solid #1E6B4A;outline-offset:2px}
.jy-p{margin-top:10px;background:#FFFFFF;border-left:5px solid #1E6B4A;padding:16px 20px;font-size:18px;line-height:1.5}
.jy-p p{margin:0}.jy-l{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:10px!important;font-weight:600;font-size:16px}
@media (max-width:760px){.jy-row{grid-template-columns:1fr}.jy-row::before{left:42px;right:auto;top:20px;bottom:20px;border-top:0;border-left:3px dashed #9AB3A6}
 .jy-b{display:grid;grid-template-columns:56px 1fr;grid-template-rows:auto auto;column-gap:14px;row-gap:2px;text-align:left;align-items:start;padding:10px 8px}.jy-b svg{width:56px;height:56px;grid-row:1/3;grid-column:1}
 .jy-b b{grid-column:2;align-self:end}.jy-b .jy-d{grid-column:2;align-self:start}.jy-b .jy-n{display:none}}
</style>'''
JS = '''<script>(function(){var r=document.getElementById("lc-journey");if(!r)return;r.addEventListener("click",function(e){var b=e.target.closest(".jy-b");if(!b)return;var o=b.getAttribute("aria-expanded")==="true";
r.querySelectorAll(".jy-b").forEach(function(x){x.setAttribute("aria-expanded","false")});r.querySelectorAll(".jy-p").forEach(function(p){p.hidden=true});
if(!o){b.setAttribute("aria-expanded","true");r.querySelector('.jy-p[data-j="'+b.dataset.j+'"]').hidden=false;}});})();</script>'''
BLOCK = (f'{CSS}<section id="lc-journey" aria-labelledby="jy-h"><h2 id="jy-h">Where are you now?</h2>'
         f'<p class="jy-sub">Tap the step that fits you. You will see what to do and where to get help.</p>'
         f'<div class="jy-row">{btns}</div>{panels}</section>{JS}\n')
anchor = '<ol class="rail" id="rail"'
assert anchor in s
s = s.replace(anchor, BLOCK + anchor, 1)
open(P, 'w', encoding='utf-8').write(s)
print('journey added')
