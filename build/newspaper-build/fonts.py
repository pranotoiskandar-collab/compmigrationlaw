# Site font swap (Pranoto 2026-11-17: "less robotic"). Idempotent. Run LAST, after responsive.py.
# Usage: python3 fonts.py SITE A|B|C
#  A = Familjen Grotesk everywhere (typewriter labels removed); B = Figtree; C = Source Sans 3.
import os, re, sys
SITE, OPT = sys.argv[1], sys.argv[2]
NAME = {'A': 'Familjen Grotesk', 'B': 'Figtree', 'C': 'Source Sans 3'}[OPT]
GF = 'family=' + NAME.replace(' ', '+') + ':ital,wght@0,400;0,500;0,600;0,700;1,400;1,500'
URL = re.compile(r'family=Familjen\+Grotesk[^&"\']*(?:(?:&amp;|&)family=JetBrains\+Mono[^&"\']*)?')
n = 0
for root, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith(('.html', '.css', '.js', '.svg')): continue
        p = os.path.join(root, f); s = open(p, encoding='utf-8').read()
        t = URL.sub(GF, s).replace('JetBrains Mono', NAME).replace('Familjen Grotesk', NAME)
        if f.endswith('.html') and 'font-variant-numeric:tabular-nums' not in t:
            t = t.replace('</head>', '<style>body{font-variant-numeric:tabular-nums}</style>\n</head>', 1)
        if t != s: open(p, 'w', encoding='utf-8').write(t); n += 1
print(NAME, 'applied to', n, 'files')
