import re, os, sys, glob, shutil
root = sys.argv[1]; new = sys.argv[2]
dst = os.path.join(root, 'countries-of-origin')
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(new, dst)
pat = re.compile(r'(<a href="/east-asia/"(?: aria-current="page")?>East Asia</a>)(?!\s*<a href="/countries-of-origin/")')
n = 0
for f in glob.glob(root + '/**/*.html', recursive=True):
    if '/countries-of-origin/' in f: continue
    s = open(f).read()
    t = pat.sub(r'\1\n<a href="/countries-of-origin/">Countries of Origin</a>', s)
    if t != s: open(f, 'w').write(t); n += 1
print('nav patched', n)
lj = os.path.join(root, 'assets/lang.js'); s = open(lj).read()
if '"Countries of Origin"' not in s:
    s = s.replace('"East Asia":"Asia Timur"', '"East Asia":"Asia Timur","Countries of Origin":"Negara Asal"', 1); open(lj, 'w').write(s)
print('lang', '"Countries of Origin":"Negara Asal"' in s)
sm = os.path.join(root, 'sitemap.xml'); s = open(sm).read()
if 'countries-of-origin' not in s:
    s = s.replace('</urlset>', '  <url><loc>https://theimr.org/countries-of-origin/</loc><lastmod>2026-10-31</lastmod></url>\n</urlset>'); open(sm, 'w').write(s)
print('sitemap', 'countries-of-origin' in s)
