"""Builds /domestic-workers/ into the site and links it everywhere (idempotent). Run: python3 deploy.py SITE_DIR
Afterwards rerun databases-build/nav.py and ai-use-build/ai_use.py."""
import glob, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/theimr-site"
for s in ["build_data.py", "build_page.py", "plain_entry.py"]: subprocess.run([sys.executable, os.path.join(HERE, s), SITE], check=True)
rd = lambda p: open(p, encoding="utf-8").read()
def wr(p, s): open(p, "w", encoding="utf-8").write(s)
# 1. menu item after Countries of Origin on every page
A = '<a href="/countries-of-origin/">Countries of Origin</a>\n'; B = '<a href="/countries-of-origin/" aria-current="page">Countries of Origin</a>\n'
ITEM = '<a href="/domestic-workers/">Migrant Domestic Workers</a>\n'; n = 0
for p in glob.glob(SITE + "/**/*.html", recursive=True):
    s = rd(p)
    if 'href="/domestic-workers/"' in s: continue
    o = s.replace(A, A + ITEM, 1).replace(B, B + ITEM, 1)
    if o != s: wr(p, o); n += 1
print("menu item added on", n, "pages")
# 2. card on /databases/
D = SITE + "/databases/index.html"; s = rd(D)
if 'href="/domestic-workers/"><b>' not in s:
    card = '<li><a href="/domestic-workers/"><b>Migrant Domestic Workers</b><span>International, regional, bilateral and national law on domestic workers who migrate, coded against ILO C189 for 44 countries.</span><i>Open →</i></a></li>'
    anchor = '<li><a href="/countries-of-origin/">'
    i = s.index(anchor); j = s.index("</li>", i) + 5
    s = s[:j] + card + s[j:]; wr(D, s); print("databases card added")
db = os.path.join(os.path.dirname(HERE), "databases-build", "databases.py")
if os.path.exists(db):
    x = rd(db)
    if "/domestic-workers/" not in x:
        a = "      ('/hate-speech-voting/', 'Hate Speech and Voting',"
        x = x.replace(a, "      ('/domestic-workers/', 'Migrant Domestic Workers', t('International, regional, bilateral and national law on domestic workers who migrate, coded against ILO C189 for 44 countries.', 'Hukum internasional, kawasan, bilateral, dan nasional tentang pekerja rumah tangga yang bermigrasi, dikodekan menurut ILO C189 untuk 44 negara.')),\n" + a, 1)
        wr(db, x); print("databases.py updated for future rebuilds")
# 3. lang.js strings
L = SITE + "/assets/lang.js"; s = rd(L); pre = 'window.SITE_I18N={"id":{'
add = {"Migrant Domestic Workers": "Pekerja Rumah Tangga Migran",
       "International, regional, bilateral and national law on domestic workers who migrate, coded against ILO C189 for 44 countries.": "Hukum internasional, kawasan, bilateral, dan nasional tentang pekerja rumah tangga yang bermigrasi, dikodekan menurut ILO C189 untuk 44 negara."}
add = {k: v for k, v in add.items() if json.dumps(k, ensure_ascii=False) + ":" not in s}
if add: wr(L, pre + "".join("%s:%s," % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in add.items()) + s[len(pre):])
# 4. sitemap and llms.txt
sm = rd(SITE + "/sitemap.xml")
if "/domestic-workers/" not in sm: wr(SITE + "/sitemap.xml", sm.replace("</urlset>", "  <url><loc>https://theimr.org/domestic-workers/</loc><lastmod>2026-11-11</lastmod></url>\n</urlset>"))
lt = rd(SITE + "/llms.txt")
if "/domestic-workers/" not in lt:
    a = "- [Countries of Origin](https://theimr.org/countries-of-origin/)"; i = lt.index(a); j = lt.index("\n", i) + 1
    wr(SITE + "/llms.txt", lt[:j] + "- [Migrant Domestic Workers](https://theimr.org/domestic-workers/): international, regional, bilateral and national instruments on migrant domestic workers; 44 jurisdictions coded against ILO C189, with corridors, timeline, statistics and CSV downloads\n" + lt[j:])
print("deploy done")
