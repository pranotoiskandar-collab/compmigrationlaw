# Model F masthead for every page of theimr.org (oto chose it 2026-11-16). Idempotent.
# Usage: python3 masthead.py SITE
# Replaces the old one-line <header> (brand left, nav right) with the compact F header: IMR square + name + subtitle,
# the page's own <nav aria-label="Main"> block (untouched, so restructure.py and lang.js keep working).
# Copies editorial.css to SITE/assets/ and links it after notebook.css.
# Order after rebuilds: restructure.py -> home_f.py -> masthead.py -> clinic_journey.py -> i18n.py -> ai_use.py -> analytics.py -> apply_guide.py
import os, re, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
LINK = '<link rel="stylesheet" href="/assets/editorial.css">'
HDR = re.compile(r'<header\b([^>]*)>\s*<div[^>]*>\s*<a [^>]*>\s*Institute for Migrant Rights\s*</a>\s*(<nav aria-label="Main".*?</nav>)\s*</div>\s*</header>', re.S)

def new_header(nav, extra_cls=''):
    nav = re.sub(r'(<nav aria-label="Main")[^>]*>', r'\1 class="nav">', nav, count=1)
    nav = re.sub(r'<a class="cta-clinic"[^>]*>', '<a class="cta-clinic" href="/legal-clinic/">', nav)
    return ('<header class="%sed-mast">\n<div class="ed-in">\n'
            '<a class="ed-brand" href="/"><i>IMR</i><span><b>Institute for Migrant Rights</b><small>Migration Jurisprudence from the South</small></span></a>\n'
            '<div class="ed-navrow">\n%s\n</div>\n</div>\n</header>') % (extra_cls, nav)

def add_link(s):
    if LINK in s: return s
    if '/assets/notebook.css">' in s: return s.replace('/assets/notebook.css">', '/assets/notebook.css">\n' + LINK, 1)
    return s.replace('</head>', LINK + '\n</head>', 1)

def main(SITE):
    shutil.copy(os.path.join(HERE, 'editorial.css'), os.path.join(SITE, 'assets', 'editorial.css'))
    n = skip = 0
    for root, _, files in os.walk(SITE):
        for f in files:
            if not f.endswith('.html'): continue
            p = os.path.join(root, f); s = o = open(p, encoding='utf-8').read()
            if 'ed-mast' not in s:
                m = HDR.search(s)
                if not m: skip += 1; continue
                s = s[:m.start()] + new_header(m.group(2), 'imr-hd ' if 'imr-hd' in m.group(1) else '') + s[m.end():]
            s = add_link(s)
            if s != o: open(p, 'w', encoding='utf-8').write(s); n += 1
    print('masthead applied to', n, 'pages; no header found on', skip)

if __name__ == '__main__':
    main(sys.argv[1])
