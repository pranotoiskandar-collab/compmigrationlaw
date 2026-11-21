# Adds the GoatCounter snippet (site code "theimr", set up by Pranoto 2026-11-12) and /assets/imr-events.js to every HTML page. Idempotent: rerun after any page rebuild.
import os, sys
SITE = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/theimr-site'
TAG = '<!-- imr-analytics -->'
SNIP = TAG + '\n<script data-goatcounter="https://theimr.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n<script src="/assets/imr-events.js" defer></script>\n'
n = skip = 0
for root, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith('.html'): continue
        p = os.path.join(root, f)
        if '/embed/' in p or f == 'offline.html': skip += 1; continue  # embeddable widgets on partner sites stay bare
        s = open(p, encoding='utf-8').read()
        if TAG in s or '</head>' not in s: skip += 1; continue
        i = s.index('</head>'); s = s[:i] + SNIP + s[i:]
        open(p, 'w', encoding='utf-8').write(s); n += 1
print('added to', n, 'pages; skipped', skip)
