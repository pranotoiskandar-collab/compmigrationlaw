# Phone menu for the model F masthead (2026-11-17). Idempotent. Run after masthead.py.
# Usage: python3 mobile_menu.py SITE
# Under 720px the header shows: IMR name, a Menu button, the Clinic button and EN/ID. Menu opens the full list.
import os, sys
SITE = sys.argv[1]
BTN = ('<button type="button" class="ed-burger" aria-expanded="false" aria-label="Menu" '
       'onclick="var h=this.closest(\'header\');var o=h.classList.toggle(\'ed-open\');this.setAttribute(\'aria-expanded\',o)">'
       '<span aria-hidden="true"></span>Menu</button>')
CSS = '''
/* phone menu (mobile_menu.py) */
.ed-burger{display:none}
@media (max-width:720px){
 .ed-mast .ed-in{padding:8px 16px;gap:4px 12px}
 .ed-brand{flex:1;min-width:0}
 .ed-brand b{font-size:17px}
 .ed-brand small{font-size:10px;letter-spacing:.04em}
 .ed-burger{display:inline-flex;align-items:center;gap:8px;background:#FFFFFF;border:1px solid #172D24;color:#172D24;font:600 14px 'Familjen Grotesk',system-ui,sans-serif;padding:8px 12px;cursor:pointer;border-radius:0}
 .ed-burger span,.ed-burger span::before,.ed-burger span::after{display:block;width:16px;height:2px;background:#172D24;position:relative;content:""}
 .ed-burger span::before{position:absolute;top:-5px}.ed-burger span::after{position:absolute;top:5px}
 .ed-open .ed-burger span{background:transparent}.ed-open .ed-burger span::before{top:0;transform:rotate(45deg)}.ed-open .ed-burger span::after{top:0;transform:rotate(-45deg)}
 .ed-burger:focus-visible{outline:3px solid #1E6B4A;outline-offset:2px}
 .ed-navrow{flex-basis:100%}
 .ed-mast:not(.ed-open) .ed-navrow>nav>details,.ed-mast:not(.ed-open) .ed-navrow>nav>a:not(.cta-clinic){display:none!important}
 .ed-open .ed-navrow>nav>details,.ed-open .ed-navrow>nav>a:not(.cta-clinic){flex-basis:100%;border-top:1px solid #DCE6E0}
 .ed-open .ed-navrow>nav{padding-bottom:8px}
 .ed-open .ed-mast .nav .menu,.ed-open .nav .menu{position:static!important;box-shadow:none;max-height:none!important;margin:0 0 8px}
 .ed-navrow>nav>a.cta-clinic{margin:4px 0}
}
'''
p = os.path.join(SITE, 'assets', 'editorial.css'); s = open(p, encoding='utf-8').read()
if 'mobile_menu.py' not in s: open(p, 'a', encoding='utf-8').write(CSS)
n = 0
for root, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith('.html'): continue
        q = os.path.join(root, f); t = open(q, encoding='utf-8').read()
        if 'ed-burger' in t or 'class="ed-brand"' not in t: continue
        i = t.index('class="ed-brand"'); j = t.index('</a>', i) + 4
        t = t[:j] + '\n' + BTN + t[j:]
        open(q, 'w', encoding='utf-8').write(t); n += 1
print('menu button on', n, 'pages')
