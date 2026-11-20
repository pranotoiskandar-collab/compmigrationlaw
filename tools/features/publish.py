#!/usr/bin/env python3
"""Publish-time step for the comparison, timeline, coverage, laws, follow and report pages.

1. Rebuilds site/features/*.json from data/ (build_data.py), so the pages always match the published tables.
2. Writes site/features/alerts-config.json with the Buttondown username, if one is set in tools/digest/config.json
   (the monthly digest, PR #23) or tools/alerts/config.json. Empty username = the follow form stays a Netlify form.
3. Adds <script src="/assets/report-link.js" defer> before </body> on every page, once. The HTML in site/ is not
   changed in the repository; this runs on the copy Netlify publishes. Idempotent.
4. Builds the RSS feeds in site/feeds/ (feeds.py) and adds feed links (<link rel="alternate">) to the <head> of every
   page that has none, so feed readers find them.
Run from the Netlify build command (or as tools/publish/60_features.py once that folder exists).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, 'site')
TAG = '<script src="/assets/report-link.js" defer></script>'
SKIP = ('report/', 'legal-clinic/review.html')

subprocess.run([sys.executable, os.path.join(HERE, 'build_data.py'), ROOT], check=True)
subprocess.run([sys.executable, os.path.join(HERE, 'feeds.py'), ROOT], check=True)
FEEDS = ('<link rel="alternate" type="application/rss+xml" title="IMR: what\u2019s new in the databases (monthly)" href="/updates/feed.xml">'
         '<link rel="alternate" type="application/rss+xml" title="IMR: new court decisions" href="/feeds/decisions.xml">'
         '<link rel="alternate" type="application/rss+xml" title="IMR: migration and farmworker law news" href="/feed.xml">')

user = ''
for p in ('tools/digest/config.json', 'tools/alerts/config.json'):
    try:
        user = user or json.load(open(os.path.join(ROOT, p))).get('buttondown_username', '')
    except (OSError, ValueError):
        pass
json.dump({'buttondown_username': user}, open(os.path.join(SITE, 'features', 'alerts-config.json'), 'w'))

n = 0
for d, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith('.html'):
            continue
        p = os.path.join(d, f)
        rel = os.path.relpath(p, SITE).replace(os.sep, '/')
        if rel.startswith(SKIP):
            continue
        t = open(p, encoding='utf-8').read()
        t0 = t
        if 'application/rss+xml' not in t and '</head>' in t:
            i = t.index('</head>')
            t = t[:i] + FEEDS + '\n' + t[i:]
        if 'report-link.js' not in t and '</body>' in t:
            i = t.rindex('</body>')
            t = t[:i] + TAG + '\n' + t[i:]
            n += 1
        if t != t0:
            open(p, 'w', encoding='utf-8').write(t)
print(f'features publish: report link added to {n} pages; Buttondown {"on" if user else "off (Netlify form)"}')
