# Makes the 529 court-decision pages reachable by plain links, so Google can crawl them (2026-11-17).
# Search Console showed 514 pages "Discovered - currently not indexed": the decision pages were linked only by JavaScript.
# Adds: /court-decisions/all/ (static list by country), "More decisions from X" on each decision page,
# a link to the list on /court-decisions/, and the new page in sitemap.xml. Idempotent.
# Usage: python3 seo_links.py SITE
import os, re, sys, json, html, subprocess
SITE = sys.argv[1]; CD = os.path.join(SITE, 'court-decisions')
data = json.loads(subprocess.check_output(['node', '-e', "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.CD.decisions))", os.path.abspath(os.path.join(CD, 'cd-data.js'))]))
E = html.escape
pages = {}
for d in data:
    p = os.path.join(CD, 'd', d['id'], 'index.html')
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<a href="/court-decisions/">Court Decisions</a> › ([^<]+)</p>', s)
    d['country'] = m.group(1).strip() if m else d['cc']; d['year'] = d['date'][:4]; pages[d['id']] = (p, s)
docs = [d for d in data if d['id'] in pages]
REG = {'asia': 'Asia', 'africa': 'Africa', 'mena': 'Middle East and North Africa', 'latam': 'Latin America and the Caribbean', 'europe': 'Europe', 'namerica': 'North America', 'oceania': 'Oceania', 'intl': 'International bodies'}
def li(d): return '<li><a href="/court-decisions/d/%s/">%s</a> <span class="g-note">%s · %s</span></li>' % (d['id'], E(d['name']), E(d['court']), d['year'])

# 1) decision pages: related links
n = 0
for d in docs:
    p, s = pages[d['id']]
    if 'id="cd-more"' in s: continue
    same = [x for x in docs if x['cc'] == d['cc'] and x['id'] != d['id']]
    title = 'More decisions from %s' % d['country']
    if len(same) < 3:
        same += [x for x in docs if x['region'] == d['region'] and x['cc'] != d['cc']]; title = 'More decisions from the same region'
    same = sorted(same[:200], key=lambda x: x['date'], reverse=True)[:8]
    block = ('<section id="cd-more" style="margin-top:40px;border-top:1px solid #B2C7BC;padding-top:16px"><h2>%s</h2><ul style="padding-left:18px;line-height:1.5">%s</ul>'
             '<p><a href="/court-decisions/all/">All decisions, listed by country →</a></p></section>') % (E(title), ''.join(li(x) for x in same))
    s = s.replace('</div></main>', block + '</div></main>', 1); open(p, 'w', encoding='utf-8').write(s); n += 1
print('related links on', n, 'decision pages')

# 2) /court-decisions/all/ built from one decision page's shell
tp, ts = pages[docs[0]['id']]
head_end = ts.index('<main'); main_end = ts.index('</main>') + 7
by = {}
for d in docs: by.setdefault(d['country'], []).append(d)
body = ['<main style="padding: 48px 0 72px" id="cd-all"><div class="g-wrap" style="max-width:820px;margin:0 auto;padding:0 24px">',
        '<p class="g-note"><a href="/court-decisions/">Court Decisions</a> › All decisions</p>',
        '<h1>All court decisions, by country</h1>',
        '<p>%d decisions on migrant workers from national, regional and international courts. For search and filters, use the <a href="/court-decisions/">Court Decisions</a> page.</p>' % len(docs),
        '<p class="g-note">' + ' · '.join('<a href="#c-%s">%s</a>' % (re.sub(r'\W+', '-', c.lower()), E(c)) for c in sorted(by)) + '</p>']
for c in sorted(by):
    body.append('<h2 id="c-%s">%s <span class="g-note">(%d)</span></h2><ul style="padding-left:18px;line-height:1.5">%s</ul>' % (re.sub(r'\W+', '-', c.lower()), E(c), len(by[c]), ''.join(li(x) for x in sorted(by[c], key=lambda x: x['date'], reverse=True))))
body.append('</div></main>')
head = ts[:head_end]
head = re.sub(r'<title>[^<]*</title>', '<title>All court decisions on migrant workers, by country · Institute for Migrant Rights</title>', head, count=1)
head = re.sub(r'(<link rel="canonical" href=")[^"]+', r'\1https://theimr.org/court-decisions/all/', head, count=1)
head = re.sub(r'(<meta name="description" content=")[^"]*', r'\1Every court decision in the IMR Court Decisions database, listed by country with court and year.', head, count=1)
head = re.sub(r'(<meta property="og:(?:url)" content=")[^"]*', r'\1https://theimr.org/court-decisions/all/', head)
head = re.sub(r'(<meta (?:property|name)="(?:og|twitter):title" content=")[^"]*', r'\1All court decisions on migrant workers, by country', head)
head = re.sub(r'(<meta (?:property|name)="(?:og|twitter):description" content=")[^"]*', r'\1Every court decision in the IMR Court Decisions database, listed by country with court and year.', head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
os.makedirs(os.path.join(CD, 'all'), exist_ok=True)
open(os.path.join(CD, 'all', 'index.html'), 'w', encoding='utf-8').write(head + '\n'.join(body) + ts[main_end:])

# 3) link from the Court Decisions page (static, before </main>)
ip = os.path.join(CD, 'index.html'); s = open(ip, encoding='utf-8').read()
if 'href="/court-decisions/all/"' not in s:
    s = s.replace('</main>', '<p style="max-width:1120px;margin:32px auto 0;padding:0 24px"><a href="/court-decisions/all/">Browse all %d decisions as a list, by country →</a></p></main>' % len(docs), 1)
    open(ip, 'w', encoding='utf-8').write(s)
# 4) sitemap
sp = os.path.join(SITE, 'sitemap.xml'); s = open(sp, encoding='utf-8').read()
if '/court-decisions/all/' not in s:
    s = s.replace('</urlset>', '<url><loc>https://theimr.org/court-decisions/all/</loc><changefreq>monthly</changefreq></url>\n</urlset>'); open(sp, 'w', encoding='utf-8').write(s)
print('list page with', len(docs), 'decisions in', len(by), 'countries')

# 5) Indonesian strings (lang.js)
LP = os.path.join(SITE, 'assets', 'lang.js'); L = open(LP, encoding='utf-8').read()
ADD = {"More decisions from the same region": "Putusan lain dari kawasan yang sama", "All decisions, listed by country →": "Semua putusan, menurut negara →",
       "All court decisions, by country": "Semua putusan pengadilan, menurut negara", "All decisions": "Semua putusan"}
PATS = [["^More decisions from (.+)$", "Putusan lain dari $1"], ["^Browse all (\\d+) decisions as a list, by country →$", "Lihat daftar semua $1 putusan, menurut negara →"],
        ["^(\\d+) decisions on migrant workers from national, regional and international courts\\. For search and filters, use the$", "$1 putusan tentang pekerja migran dari pengadilan nasional, kawasan, dan internasional. Untuk pencarian dan penyaringan, buka halaman"]]
add = ''.join(json.dumps(k, ensure_ascii=False) + ':' + json.dumps(v, ensure_ascii=False) + ',' for k, v in ADD.items() if json.dumps(k, ensure_ascii=False) + ':' not in L)
if add: L = L.replace('window.SITE_I18N={"id":{', 'window.SITE_I18N={"id":{' + add, 1)
new = [p for p in PATS if json.dumps(p[0], ensure_ascii=False) not in L]
if new: L = L.replace('"__pat":[', '"__pat":[' + ','.join(json.dumps(p, ensure_ascii=False) for p in new) + ',', 1)
open(LP, 'w', encoding='utf-8').write(L)
