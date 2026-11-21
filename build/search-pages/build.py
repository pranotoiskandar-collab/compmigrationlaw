# Search-friendly landing pages for theimr.org, generated from the repo's open data (2026-11-19).
# Writes static English and Indonesian pages, each pair linked by hreflang:
#   /countries/<country>/            /id/negara/<negara>/              one page per country
#   /countries/<country>/<topic>/    /id/negara/<negara>/<topik>/      country x topic, where >= MIN_CT decisions
#   /topics/<topic>/                 /id/topik/<topik>/                one page per topic
#   /corridors/<origin>-to-<dest>/   /id/koridor/<asal>-ke-<tujuan>/   key migration corridors
# plus index pages for each group, sitemap entries, an /llms.txt section and links from /databases/ and /court-decisions/all/.
# Sources: data/court-decisions, data/gcc, data/east-asia, data/southeast-asia, data/countries-of-origin, data/atlas,
# site/legal-help/places.js. The page shell (header, menu, footer, styles) is copied from site/court-decisions/all/index.html,
# so the pages follow whatever look the site has when this runs.
# Idempotent. Usage (from the repo root): python3 build/search-pages/build.py
# Rerun after any change to these data files, after restructure.py/puncak_green.py, and before ai_use.py/analytics.py.
import csv, html, json, os, re, shutil, subprocess, sys, unicodedata
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from texts import TOPICS, ORIGINS, DESTS, GCC, EXTRA_CORRIDORS, INSTRUMENTS, ATLAS_NAME, EXTRA_COUNTRY

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SITE = os.path.join(ROOT, 'site'); DATA = os.path.join(ROOT, 'data')
BASE = 'https://theimr.org'
TODAY = '2026-11-20'
MIN_CT = 4          # decisions needed for a country x topic page
MIN_COUNTRY = 5     # decisions needed for a country page (coded countries always get one)
E = lambda x: html.escape(str(x if x is not None else ''), quote=True)

def rcsv(p):
    with open(os.path.join(DATA, p), encoding='utf-8-sig') as f: return list(csv.DictReader(f))

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

# ---------------------------------------------------------------- data
cdjs = open(os.path.join(SITE, 'court-decisions', 'cd.js'), encoding='utf-8').read()
COUNTRY = {k: [a, b] for k, a, b in re.findall(r'(\w\w): \["([^"]+)", "([^"]+)"\]', cdjs.split('var COUNTRY = ')[1].split('};')[0])}
for k, v in EXTRA_COUNTRY.items(): COUNTRY.setdefault(k, v)
def cn(c, L='en'): return COUNTRY.get(c, [c, c])[0 if L == 'en' else 1]

D = rcsv('court-decisions/decisions.csv')
HAS_PAGE = set(os.listdir(os.path.join(SITE, 'court-decisions', 'd')))
D = [d for d in D if d['id'] in HAS_PAGE]
for d in D:
    d['sits'] = [s for s in d['situations'].split(';') if s]
    d['text'] = ' '.join([d['name'], d['question'], d['holding'], d['plain_en'], d['sector'], d['issues']])
    d['year'] = d['date'][:4]
for t in TOPICS:
    if t['k'].startswith('sector:'): t['rx_c'] = re.compile(t['rx'], re.I)
def in_topic(d, t):
    return bool(t['rx_c'].search(d['sector'] + ' ' + d['name'] + ' ' + d['plain_en'])) if t['k'].startswith('sector:') else t['k'] in d['sits']
TOPIC = {t['k']: t for t in TOPICS}
def order(ds):  # full entries first, newest first
    return sorted(ds, key=lambda d: (d['status'] == 'C', -int(d['year'] or 0), d['name']))

# laws by state
LAWS = defaultdict(list)
for p, src in [('gcc/domestic-laws.csv', 'gcc'), ('east-asia/domestic-laws.csv', 'east-asia'),
               ('southeast-asia/domestic-laws.csv', 'southeast-asia'), ('countries-of-origin/laws-policies.csv', 'countries-of-origin'),
               ('migration-law/national-laws.csv', 'national-laws')]:
    for r in rcsv(p):
        r['db'] = src; LAWS[r['s']].append(r)

# coded features by state (feature name, value label, EN + ID)
CB_SEA = {r['feature']: r for r in rcsv('southeast-asia/codebook.csv')}
CB_OC = {r['k']: r for r in rcsv('countries-of-origin/codebook.csv')}
def val_id(cb, feat, v):
    r = cb.get(feat)
    if not r: return None, None
    if 'name_id' in r: return r['name_id'], r.get('value_%s_id' % v)
    return r.get('id'), r.get('l%s_id' % v)
CODED = defaultdict(list)
for p, db, cb in [('southeast-asia/codings.csv', 'southeast-asia', CB_SEA), ('east-asia/codings.csv', 'east-asia', CB_SEA)]:
    for r in rcsv(p):
        n_id, v_id = val_id(cb, r['feature'], r['value'])
        CODED[r['state']].append(dict(group=r['group_name'], f=r['feature_name'], v=r['value_label'], f_id=n_id, v_id=v_id, ev=r.get('evidence', ''), db=db))
for r in rcsv('countries-of-origin/codings.csv'):
    n_id, v_id = val_id(CB_OC, r['feature'], r['value'])
    CODED[r['country']].append(dict(group='', f=r['feature_name'], v=r['value_label'], f_id=n_id, v_id=v_id, ev=r.get('evidence', ''), db='countries-of-origin'))

# ratifications
RAT = defaultdict(dict)
for r in rcsv('atlas/ratifications.csv'): RAT[r['country']][r['instrument']] = r
def rat(c, inst):
    r = RAT.get(ATLAS_NAME.get(c, cn(c)), {}).get(inst)
    if not r: return None
    return r

# agreements between two states (bilateral rows in the destination and origin datasets)
NAME_ALIASES = {'VN': ['Viet Nam', 'Vietnam'], 'KR': ['South Korea', 'Korea', 'Republic of Korea'], 'AE': ['UAE', 'United Arab Emirates']}
def names(c): return set([cn(c)] + NAME_ALIASES.get(c, []))
AGR = []
for p, db in [('gcc/frameworks.csv', 'gcc'), ('east-asia/instruments.csv', 'east-asia'), ('southeast-asia/instruments.csv', 'southeast-asia'), ('countries-of-origin/instruments.csv', 'countries-of-origin')]:
    for r in rcsv(p):
        if r.get('level') == 'bilateral' or r.get('nature') in ('mou', 'agreement', 'contract', 'protocol'):
            r['db'] = db; AGR.append(r)
def agreements(o, d):
    out = []
    for r in AGR:
        if (r['s'] == d and r['partner'] in names(o)) or (r['s'] == o and r['partner'] in names(d)):
            out.append(r)
    seen, res = set(), []
    for r in sorted(out, key=lambda r: (r.get('signed') or r.get('in_force') or '')):
        k = r['title'].lower()[:60]
        if k not in seen: seen.add(k); res.append(r)
    return res

# corridors with numbers
NAME2CODE = {v[0]: k for k, v in COUNTRY.items()}; NAME2CODE.update({'Viet Nam': 'VN', 'Vietnam': 'VN', 'Myanmar': 'MM'})
CORR = {}
for r in rcsv('gcc/corridors.csv'):
    o = NAME2CODE.get(r['origin']); d = NAME2CODE.get(r['gcc'])
    if o in ORIGINS and d: CORR[(o, d)] = dict(n=int(r['stock']), en='migrants from %s living in %s in 2024 (UN DESA International Migrant Stock 2024; all migrants, not only workers)' % (cn(o), cn(d)),
                                                  id='migran asal %s yang tinggal di %s pada 2024 (UN DESA International Migrant Stock 2024; seluruh migran, tidak hanya pekerja)' % (cn(o, 'id'), cn(d, 'id')), db='gcc')
for r in rcsv('east-asia/corridors.csv'):
    o = NAME2CODE.get(r['origin']); d = NAME2CODE.get(r['destination'])
    if o in ORIGINS and d: CORR[(o, d)] = dict(n=int(r['workers']), en='%s in %s (%s)' % (r['population'].lower(), r['year'], 'official statistics of the destination, see East Asia corridors data'),
                                                  id='%s, %s (statistik resmi negara tujuan; lihat data koridor Asia Timur)' % (r['population'], r['year']), db='east-asia')
for r in rcsv('countries-of-origin/corridors.csv'):
    o = r['origin']; d = NAME2CODE.get(r['destination'])
    if o in ORIGINS and d and (o, d) not in CORR:
        CORR[(o, d)] = dict(n=int(r['workers']), en='workers leaving %s for %s in %s, as recorded by the country of origin (%s%% of its departures)' % (cn(o), cn(d), r['period'], r['share']),
                            id='pekerja yang berangkat dari %s ke %s pada %s menurut catatan negara asal (%s%% dari seluruh keberangkatan)' % (cn(o, 'id'), cn(d, 'id'), r['period'], r['share']), db='countries-of-origin')

# legal help places
LH = json.loads(subprocess.check_output(['node', '-e', "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.LEGAL_HELP))",
                                         os.path.join(SITE, 'legal-help', 'places.js')]))
PLACES = defaultdict(list)
for p in LH['places']: PLACES[p['c']].append(p)

# ---------------------------------------------------------------- which pages
cc_count = Counter(d['country'] for d in D)
CODED_STATES = set(CODED) | set(LAWS)
COUNTRIES = sorted({c for c, n in cc_count.items() if n >= MIN_COUNTRY and c in COUNTRY and not c.startswith('X')} |
                   {c for c in CODED_STATES if c in COUNTRY} | {c for c in ORIGINS if c in COUNTRY}, key=lambda c: cn(c))
CSLUG = {c: slug(cn(c)) for c in COUNTRIES}; CSLUG_ID = {c: slug(cn(c, 'id')) for c in COUNTRIES}
by_c = defaultdict(list)
for d in D: by_c[d['country']].append(d)
CT = {}  # (country, topic key) -> decisions
for c in COUNTRIES:
    for t in TOPICS:
        ds = [d for d in by_c[c] if in_topic(d, t)]
        if len(ds) >= MIN_CT: CT[(c, t['k'])] = ds
# corridors: origin x destination in the data, or listed as an extra; both ends need a country page
CORRS = sorted({k for k in CORR if k[1] in DESTS} | set(EXTRA_CORRIDORS), key=lambda k: (cn(k[0]), cn(k[1])))
CORRS = [k for k in CORRS if k[0] in COUNTRIES and k[1] in COUNTRIES]

def u_country(c, L): return '/countries/%s/' % CSLUG[c] if L == 'en' else '/id/negara/%s/' % CSLUG_ID[c]
def u_ct(c, t, L): return u_country(c, L) + (TOPIC[t]['en_slug'] if L == 'en' else TOPIC[t]['id_slug']) + '/'
def u_topic(t, L): return '/topics/%s/' % TOPIC[t]['en_slug'] if L == 'en' else '/id/topik/%s/' % TOPIC[t]['id_slug']
def u_corr(o, d, L): return '/corridors/%s-to-%s/' % (CSLUG[o], CSLUG[d]) if L == 'en' else '/id/koridor/%s-ke-%s/' % (CSLUG_ID[o], CSLUG_ID[d])
IDX = {'countries': ('/countries/', '/id/negara/'), 'topics': ('/topics/', '/id/topik/'), 'corridors': ('/corridors/', '/id/koridor/')}

# ---------------------------------------------------------------- shell
shell = open(os.path.join(SITE, 'court-decisions', 'all', 'index.html'), encoding='utf-8').read()
HEAD = shell[:shell.index('<main')]; FOOT = shell[shell.index('</main>') + 7:]
HEAD = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', HEAD, flags=re.S)
HEAD = re.sub(r'<meta (?:property|name)="(?:og|twitter):(?:title|description|url)"[^>]*>\s*', '', HEAD)
HEAD = re.sub(r'<link rel="alternate" hreflang[^>]*>\s*', '', HEAD)
HEAD = re.sub(r'\s*aria-current="[^"]*"', '', HEAD)
FOOT = re.sub(r'<section id="imr-research".*?</section>\s*', '', FOOT, flags=re.S)

# The court-decisions shell still carries an older menu (a doubled "Know your rights" link, no "Case of the month"
# or "Tools"); use the menu the homepage and earlier search pages carry (2026-11-20).
_KYR = '<a href="/rights-checklist/">Know your rights before you go</a>\n'
HEAD = HEAD.replace(_KYR + _KYR, _KYR)
if 'href="/court-decisions/highlights/"' not in HEAD:
    HEAD = HEAD.replace('<a href="/court-decisions/">Court Decisions</a>\n</div>', '<a href="/court-decisions/">Court Decisions</a>\n'
        '<a href="/court-decisions/highlights/" style="padding-left:28px">Case of the month</a>\n'
        '<span style="display:block;padding:12px 16px 2px;font:500 11px \'Figtree\',monospace;letter-spacing:.12em;text-transform:uppercase;color:#3D5A4D">Tools</span>\n'
        '<a href="/ratifications/">Ratification tracker</a>\n<a href="/research/">Saved searches and reading list</a>\n</div>', 1)
CSS = '''<style id="sp-css">
.sp-main{padding:40px 0 64px}.sp-main .g-wrap{max-width:960px}
.sp-main h1{font-weight:400;font-size:clamp(30px,5vw,46px);line-height:1.12;margin:10px 0 0}
.sp-main h2{font-weight:500;font-size:26px;line-height:1.2;margin:44px 0 10px;padding-top:18px;border-top:1px solid currentColor;border-top-color:rgba(127,127,127,.35)}
.sp-main h3{font-size:19px;font-weight:600;margin:22px 0 6px}
.sp-lede{font-size:18px;line-height:1.55;max-width:780px}
.sp-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(170px,100%),1fr));gap:10px;margin:22px 0 0;padding:0;list-style:none}
.sp-facts li{border-top:3px solid currentColor;padding:8px 0 0;font-size:15px;line-height:1.35}.sp-facts b{display:block;font-size:26px;font-weight:500}
.sp-list{padding-left:18px;line-height:1.5}.sp-list li{margin:0 0 10px}
.sp-dec p{margin:4px 0 0;font-size:15.5px;line-height:1.5;max-width:800px}
.sp-chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding:0;list-style:none}
.sp-chips a{display:inline-flex;align-items:center;min-height:40px;padding:0 12px;border:1px solid currentColor;text-decoration:none;font-size:15px}
.sp-lang{font-size:15px;margin:0 0 6px}
.sp-src{font-size:14px;opacity:.85}
@media (max-width:640px){.sp-main h2{font-size:22px}.g-t th,.g-t td{padding:8px}}
</style>
'''
ALT_JS = '''<script>
(function(){var A=%s,L=%s;
if(L==='id'){try{localStorage.setItem('imr-lang','id')}catch(e){}}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.imr-lang [data-sl]');if(!b)return;var t=b.getAttribute('data-sl');if(t!==L&&A[t]){e.stopPropagation();try{localStorage.setItem('imr-lang',t)}catch(x){}location.href=A[t];}},true);
})();
</script>
'''

def page(path, L, title, desc, body, alt=None, ld=None, crumbs=None):
    h = HEAD
    h = h.replace('<html lang="en">', '<html lang="%s">' % L, 1)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % E(title + ' · Institute for Migrant Rights'), h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % E(desc[:300]), h, count=1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s%s">' % (BASE, path), h, count=1)
    alts = {L: path}
    if alt: alts['id' if L == 'en' else 'en'] = alt
    extra = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">\n' % (k, BASE, v) for k, v in sorted(alts.items()))
    if alt: extra += '<link rel="alternate" hreflang="x-default" href="%s%s">\n' % (BASE, alts['en'])
    extra += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n<meta property="og:url" content="%s%s">\n' % (E(title), E(desc[:300]), BASE, path)
    extra += '<meta property="og:locale" content="%s">\n' % ('id_ID' if L == 'id' else 'en_US')
    graph = [{"@type": "WebPage", "@id": BASE + path, "url": BASE + path, "name": title, "description": desc[:300], "inLanguage": L,
              "dateModified": TODAY, "isPartOf": {"@type": "DataCatalog", "name": "Migration Jurisprudence from the South", "url": BASE + "/databases/"},
              "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": BASE + "/"},
              "license": "https://creativecommons.org/licenses/by/4.0/"}]
    if ld: graph[0].update(ld)
    if crumbs:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]})
    extra += '<script type="application/ld+json">%s</script>\n' % json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    h = h.replace('</head>', extra + CSS + ALT_JS % (json.dumps(alts), json.dumps(L)) + '</head>', 1)
    langlink = ''
    if alt:
        langlink = '<p class="sp-lang" lang="%s"><a href="%s" hreflang="%s">%s</a></p>' % (('id', alt, 'id', 'Baca dalam bahasa Indonesia') if L == 'en' else ('en', alt, 'en', 'Read in English'))
    cr = ''
    if crumbs:
        cr = '<p class="g-note">' + ' › '.join('<a href="%s">%s</a>' % (u, E(n)) for n, u in crumbs[:-1]) + '</p>'
    main = '<main class="sp-main" id="sp" data-noi18n><div class="g-wrap">%s%s%s</div></main>' % (langlink, cr, body)
    out = os.path.join(SITE, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(h + main + FOOT)
    URLS.append(path)

URLS = []
T = {  # fixed wording
    'en': dict(home='Home', db='Migration Jurisprudence from the South', countries='Countries', topics='Topics', corridors='Migration corridors',
               decisions='Court decisions', full='full summaries', cand='unchecked candidates', laws='laws and policies in the databases',
               unverified='Unverified', cand_l='Unchecked candidate', more='more', allc='All decisions from %s, as a list',
               note_ai='These pages are generated automatically from the IMR open data. Summaries marked “Unverified” were pre-written with AI assistance from secondary sources and are being checked against the judgments; “unchecked candidates” were found in official law databases but have not yet been read. See <a href="/ai-use/">How we use AI</a>.',
               legal='This page is for research and advocacy. It is not legal advice.',
               cite='Cite as: Institute for Migrant Rights (%s), Migration Jurisprudence from the South, %s%s. Data CC BY 4.0.' % (TODAY[:4], '%s', ''),
               won='worker side won', lost='worker side lost', adv='advisory', unk='outcome to be checked'),
    'id': dict(home='Beranda', db='Pandangan Hukum Migrasi dari Dunia Berkembang', countries='Negara', topics='Topik', corridors='Koridor migrasi',
               decisions='Putusan pengadilan', full='ringkasan lengkap', cand='kandidat yang belum diperiksa', laws='peraturan dan kebijakan dalam basis data',
               unverified='Belum diverifikasi', cand_l='Kandidat belum diperiksa', more='lainnya', allc='Semua putusan dari %s, dalam bentuk daftar',
               note_ai='Halaman ini kami susun secara otomatis dari data terbuka IMR. Ringkasan bertanda “Belum diverifikasi” merupakan ringkasan yang disusun dengan bantuan AI dari sumber sekunder dan sedang kami periksa terhadap teks putusan; “kandidat yang belum diperiksa” merupakan putusan yang ditemukan dalam basis data hukum resmi tetapi belum kami baca. Lihat <a href="/ai-use/">Cara kami memakai AI</a>.',
               legal='Halaman ini disusun untuk penelitian dan advokasi, dan bukan merupakan nasihat hukum.',
               cite='Kutip sebagai: Institute for Migrant Rights (%s), Migration Jurisprudence from the South, %s. Data CC BY 4.0.' % (TODAY[:4], '%s'),
               won='pihak pekerja menang', lost='pihak pekerja kalah', adv='nasihat', unk='hasil perlu diperiksa'),
}
DBNAME = {'gcc': ('Gulf States', 'Negara-Negara Teluk', '/gcc/'), 'east-asia': ('East Asia', 'Asia Timur', '/east-asia/'),
          'southeast-asia': ('Southeast Asia', 'Asia Tenggara', '/southeast-asia/'), 'countries-of-origin': ('Countries of Origin', 'Negara Asal', '/countries-of-origin/'),
          'national-laws': ('National laws: other regions', 'Undang-undang nasional: kawasan lain', '/migration-law/national-laws/')}
def tr(L, k): return T[L][k]

def dec_li(d, L, show_country=False):
    out = {'won': tr(L, 'won'), 'lost': tr(L, 'lost'), 'advisory': tr(L, 'adv')}.get(d['outcome'])
    meta = [E(d['court'])]
    if show_country: meta.append(E(cn(d['country'], L)))
    meta.append(E(d['year']))
    if d['status'] == 'C': meta.append('<em>%s</em>' % tr(L, 'cand_l'))
    elif out: meta.append(E(out))
    s = '<li class="sp-dec"><a href="/court-decisions/d/%s/">%s</a> <span class="g-note">%s</span>' % (E(d['id']), E(d['name']), ' · '.join(meta))
    plain = d['plain_id'] if L == 'id' and d['plain_id'] else d['plain_en']
    if d['status'] != 'C' and plain:
        s += '<p>%s%s</p>' % (E(plain[:420] + ('…' if len(plain) > 420 else '')), '' if L == 'en' or d['plain_id'] else ' <span class="g-note">(ringkasan dalam bahasa Inggris)</span>')
    return s + '</li>'

def dec_list(ds, L, n=12, show_country=False):
    ds = order(ds)
    s = '<ul class="sp-list">' + ''.join(dec_li(d, L, show_country) for d in ds[:n]) + '</ul>'
    return s

def counts(ds, L):
    full = sum(d['status'] != 'C' for d in ds)
    return '%d %s (%d %s, %d %s)' % (len(ds), tr(L, 'decisions').lower(), full, tr(L, 'full'), len(ds) - full, tr(L, 'cand'))

def law_rows(c, L, n=40):
    rows = sorted(LAWS.get(c, []), key=lambda r: (r.get('year') or '0'), reverse=True)
    if not rows: return ''
    hd = ('Law or policy', 'Year', 'Type', 'Subject', 'Source') if L == 'en' else ('Peraturan atau kebijakan', 'Tahun', 'Jenis', 'Pokok', 'Sumber')
    s = '<div class="g-scroll"><table class="g-t"><thead><tr>%s</tr></thead><tbody>' % ''.join('<th>%s</th>' % h for h in hd)
    for r in rows[:n]:
        title = E(r['title']) + ('<br><span class="g-note">%s</span>' % E(r['orig']) if r.get('orig') else '')
        src = '<a href="%s" rel="noopener">%s</a>' % (E(r['url']), 'official site' if L == 'en' else 'situs resmi') if r.get('url', '').startswith('http') else ''
        if r.get('link') == 'glmm': src = '<a href="%s" rel="noopener">GLMM</a>' % E(r['url'])
        if r.get('link') == 'secondary': src = '<a href="%s" rel="noopener">PacLII</a> (%s)' % (E(r['url']), 'secondary source' if L == 'en' else 'sumber sekunder')
        if r.get('link') == 'un': src = '<a href="%s" rel="noopener">UNODC SHERLOC</a> (%s)' % (E(r['url']), 'UN-hosted copy' if L == 'en' else 'salinan di situs PBB')
        if r.get('link') == 'guidance': src = '<a href="%s" rel="noopener">%s</a>' % (E(r['url']), 'official guidance' if L == 'en' else 'panduan resmi')
        if r.get('status') == 'Unverified': src += ' <span class="g-note">%s</span>' % ('Unverified' if L == 'en' else 'Belum diverifikasi')
        s += '<tr><td>%s</td><td class="c">%s%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            title, E(r.get('year', '')), (' (am. %s)' % E(r['amended'])) if r.get('amended') and L == 'en' else ((' (ubah %s)' % E(r['amended'])) if r.get('amended') else ''),
            E(r.get('type', '')), E((r.get('topic') or '')[:160]), src)
    s += '</tbody></table></div>'
    dbs = sorted({r['db'] for r in rows})
    s += '<p class="g-note">%s %s.</p>' % ('Full list, notes and downloads:' if L == 'en' else 'Daftar lengkap, catatan, dan unduhan:',
                                          ', '.join('<a href="%s#laws">%s</a>' % (DBNAME[b][2], DBNAME[b][0 if L == 'en' else 1]) for b in dbs))
    return s

def coded_table(c, L):
    rows = CODED.get(c)
    if not rows: return ''
    hd = ('Group', 'Feature', 'Coded value') if L == 'en' else ('Kelompok', 'Aspek', 'Nilai kode')
    s = '<div class="g-scroll"><table class="g-t"><thead><tr>%s</tr></thead><tbody>' % ''.join('<th>%s</th>' % h for h in hd)
    for r in rows:
        f = r['f_id'] if L == 'id' and r['f_id'] else r['f']; v = r['v_id'] if L == 'id' and r['v_id'] else r['v']
        grp = r['group'].split('·')[-1].strip() if r['group'] else ('all emigrant workers' if L == 'en' else 'semua pekerja migran')
        s += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (E(grp), E(f), E(v))
    s += '</tbody></table></div>'
    db = rows[0]['db']
    s += '<p class="g-note">%s <a href="%s#profiles">%s</a>.</p>' % (
        'Each value has a legal basis, an official source and a check status in' if L == 'en' else 'Setiap nilai memiliki dasar hukum, sumber resmi, dan status pemeriksaan dalam',
        DBNAME[db][2], DBNAME[db][0 if L == 'en' else 1])
    return s

def rat_cell(c, inst, L):
    r = rat(c, inst)
    if not r: return '<td>%s</td>' % ('not a party' if L == 'en' else 'bukan pihak')
    # UN treaty rows carry code P for every party (the UN collection gives no per-state entry into force), so they read "party"
    code = r['status_code']
    st = {'F': ('in force', 'berlaku'), 'W': ('withdrawn or denounced', 'ditarik atau didenonsiasi'), 'D': ('denounced', 'didenonsiasi'),
          'S': ('signed only', 'hanya ditandatangani'), 'P': ('party', 'pihak') if inst.startswith('IC') else ('ratified, not yet in force', 'diratifikasi, belum berlaku')}.get(code, (r['status'], r['status']))[0 if L == 'en' else 1]
    return '<td>%s (%s)</td>' % (E((re.search(r'\d{4}', r['date']) or [''])[0]), E(st))

def treaty_table(cs, L):
    if any(c in ('HK', 'MO', 'TW') for c in cs) and len(cs) == 1:
        return '<p>%s</p>' % ('Hong Kong and Macau are covered through China’s ratifications, with declarations for each territory; Taiwan cannot join UN or ILO treaties. See the <a href="/east-asia/#intl">East Asia</a> page for how each applies.' if L == 'en'
                              else 'Hong Kong dan Makau tercakup melalui ratifikasi Tiongkok dengan deklarasi untuk tiap wilayah; Taiwan tidak dapat menjadi pihak perjanjian PBB atau ILO. Lihat halaman <a href="/east-asia/#intl">Asia Timur</a> untuk penerapannya.')
    hd = ['Instrument' if L == 'en' else 'Instrumen'] + [cn(c, L) for c in cs]
    s = '<div class="g-scroll"><table class="g-t"><thead><tr>%s</tr></thead><tbody>' % ''.join('<th>%s</th>' % E(h) for h in hd)
    for code, en, idn in INSTRUMENTS:
        s += '<tr><td>%s</td>%s</tr>' % (E(en if L == 'en' else idn), ''.join(rat_cell(c, code, L) if c not in ('HK', 'MO', 'TW') else '<td>–</td>' for c in cs))
    s += '</tbody></table></div><p class="g-note">%s</p>' % (
        'Year of ratification or accession and current status, from ILO NORMLEX and the UN Treaty Collection (collected October–November 2026; see <a href="/migration-law/#h-cr">Migration Law Atlas</a>).' if L == 'en'
        else 'Tahun ratifikasi atau aksesi dan status saat ini, dari ILO NORMLEX dan UN Treaty Collection (dikumpulkan Oktober–November 2026; lihat <a href="/migration-law/#h-cr">Atlas Hukum Migrasi</a>).')
    return s

def help_list(c, L):
    ps = PLACES.get(c)
    if not ps: return ''
    s = '<ul class="sp-list">'
    for p in ps[:8]:
        d = p.get('d_id') if L == 'id' and p.get('d_id') else p.get('d', '')
        tel = ', '.join(p.get('tel') or [])
        s += '<li><b>%s</b>%s<br>%s%s%s</li>' % (E(p['n']), (' · ' + E(p.get('city_id') if L == 'id' and p.get('city_id') else p.get('city', ''))) if p.get('city') else '',
                                              E(d), ('<br>' + ('Phone' if L == 'en' else 'Telepon') + ': ' + E(tel)) if tel else '',
                                              (' · <a href="%s" rel="noopener">%s</a>' % (E(p['web']), 'website' if L == 'en' else 'situs web')) if p.get('web') else '')
    s += '</ul><p class="g-note">%s</p>' % (('Checked against the named source; phone numbers only where two sources agree. Map and more places: <a href="/legal-help/">Find free legal help</a>.') if L == 'en'
                                           else ('Diperiksa terhadap sumber yang disebutkan; nomor telepon hanya dicantumkan bila dua sumber sesuai. Peta dan tempat lain: <a href="/legal-help/">Cari bantuan hukum gratis</a>.'))
    return s

def foot_notes(L, path):
    return ('<h2>%s</h2><p class="g-note">%s</p><p class="g-note">%s</p><p class="g-note">%s</p>' % (
        'About this page' if L == 'en' else 'Tentang halaman ini', tr(L, 'note_ai'), tr(L, 'legal'), tr(L, 'cite') % (BASE + path)))

def research_box(L, kw):
    return '<section class="g-note" style="margin-top:28px"><b>%s</b> %s</section>' % ('For researchers:' if L == 'en' else 'Untuk peneliti:', E(kw))
KW_EN = 'Keywords: migration law; migrant workers’ rights; comparative law; empirical legal studies; court decisions; case law; open data; Global South.'
KW_ID = 'Kata kunci: hukum migrasi; hak pekerja migran; perbandingan hukum; studi hukum empiris; putusan pengadilan; yurisprudensi; data terbuka; negara berkembang.'

def role(c):
    r = []
    if c in ORIGINS: r.append('origin')
    if c in DESTS: r.append('dest')
    return r

# ---------------------------------------------------------------- clean old output
for d in ['countries', 'topics', 'corridors', os.path.join('id', 'negara'), os.path.join('id', 'topik'), os.path.join('id', 'koridor')]:
    p = os.path.join(SITE, d)
    if os.path.isdir(p): shutil.rmtree(p)

# ---------------------------------------------------------------- country pages
for c in COUNTRIES:
    ds = by_c[c]
    for L in ('en', 'id'):
        C = cn(c, L); path = u_country(c, L); alt = u_country(c, 'id' if L == 'en' else 'en')
        tops = [(t, [d for d in ds if in_topic(d, t)]) for t in TOPICS]; tops = [(t, x) for t, x in tops if x]
        corr = [k for k in CORRS if c in k]
        if L == 'en':
            title = 'Migrant workers’ rights in %s: court decisions, laws and treaties' % C
            r = role(c)
            what = ('a country of origin and of destination' if len(r) == 2 else 'a country of origin of migrant workers' if r == ['origin']
                    else 'a destination for migrant workers' if r == ['dest'] else 'a country whose courts have decided cases on migrants')
            lede = '%s is %s. This page brings together what the IMR databases hold on %s: %s%s%s.' % (
                C, what, C, counts(ds, L) if ds else 'no court decisions yet',
                (', %d %s' % (len(LAWS[c]), tr(L, 'laws'))) if LAWS.get(c) else '',
                (', and coded features of its migrant labor law' if CODED.get(c) else ''))
        else:
            title = 'Hak pekerja migran di %s: putusan pengadilan, peraturan, dan perjanjian internasional' % C
            r = role(c)
            what = ('negara asal sekaligus negara tujuan' if len(r) == 2 else 'negara asal pekerja migran' if r == ['origin']
                    else 'negara tujuan pekerja migran' if r == ['dest'] else 'negara yang pengadilannya telah memutus perkara tentang migran')
            lede = '%s merupakan %s. Halaman ini menghimpun data IMR tentang %s, yakni %s%s%s.' % (
                C, what, C, counts(ds, L) if ds else 'belum ada putusan pengadilan',
                (', %d %s' % (len(LAWS[c]), tr(L, 'laws'))) if LAWS.get(c) else '',
                (', serta kode aspek hukum ketenagakerjaan migran' if CODED.get(c) else ''))
        desc = lede
        b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede)]
        facts = [(len(ds), 'court decisions' if L == 'en' else 'putusan pengadilan'), (sum(d['status'] != 'C' for d in ds), 'with full summary' if L == 'en' else 'dengan ringkasan lengkap'),
                 (len(LAWS.get(c, [])), 'laws and policies' if L == 'en' else 'peraturan dan kebijakan'), (len(corr), 'corridor pages' if L == 'en' else 'halaman koridor')]
        b.append('<ul class="sp-facts">' + ''.join('<li><b>%d</b>%s</li>' % (n, E(l)) for n, l in facts if n) + '</ul>')
        if tops:
            b.append('<h2>%s</h2>' % ('Court decisions by topic' if L == 'en' else 'Putusan pengadilan menurut topik'))
            b.append('<ul class="sp-chips">' + ''.join('<li><a href="%s">%s (%d)</a></li>' % (u_ct(c, t['k'], L) if (c, t['k']) in CT else u_topic(t['k'], L), E(t[L]), len(x)) for t, x in tops) + '</ul>')
        if ds:
            b.append('<h2>%s</h2>' % ('Selected decisions' if L == 'en' else 'Putusan pilihan'))
            b.append(dec_list(ds, L, 12))
            b.append('<p><a href="/court-decisions/all/#c-%s">%s →</a></p>' % (re.sub(r'\W+', '-', cn(c).lower()), E(tr(L, 'allc') % C)))
        if CODED.get(c):
            b.append('<h2>%s</h2>' % ('How the law treats migrant workers: coded features' if L == 'en' else 'Perlakuan hukum terhadap pekerja migran: kode aspek'))
            b.append(coded_table(c, L))
        if LAWS.get(c):
            b.append('<h2>%s</h2>' % ('Laws and policies' if L == 'en' else 'Peraturan dan kebijakan'))
            b.append(law_rows(c, L))
        b.append('<h2>%s</h2>' % ('Treaties on migrant workers' if L == 'en' else 'Perjanjian internasional tentang pekerja migran'))
        b.append(treaty_table([c], L))
        if corr:
            b.append('<h2>%s</h2>' % ('Migration corridors' if L == 'en' else 'Koridor migrasi'))
            b.append('<ul class="sp-chips">' + ''.join('<li><a href="%s">%s → %s</a></li>' % (u_corr(o, d_, L), E(cn(o, L)), E(cn(d_, L))) for o, d_ in corr) + '</ul>')
        if PLACES.get(c):
            b.append('<h2>%s</h2>' % ('Free legal help in %s' % C if L == 'en' else 'Bantuan hukum gratis di %s' % C))
            b.append(help_list(c, L))
        b.append(foot_notes(L, path)); b.append(research_box(L, KW_EN if L == 'en' else KW_ID))
        crumbs = [(tr(L, 'home'), '/' if L == 'en' else '/?lang=id'), (tr(L, 'countries'), IDX['countries'][0 if L == 'en' else 1]), (C, path)]
        page(path, L, title, desc, '\n'.join(b), alt, {"about": {"@type": "Country", "name": cn(c)}}, crumbs)

# ---------------------------------------------------------------- country x topic pages
for (c, k), ds in CT.items():
    t = TOPIC[k]
    for L in ('en', 'id'):
        C = cn(c, L); path = u_ct(c, k, L); alt = u_ct(c, k, 'id' if L == 'en' else 'en')
        if L == 'en':
            title = '%s: migrant worker court decisions in %s' % (t['en'], C)
            lede = 'Court decisions from %s on %s: %s. %s' % (C, t['q_en'], counts(ds, L), t['d_en'])
        else:
            title = '%s: putusan pengadilan tentang pekerja migran di %s' % (t['id'], C)
            lede = 'Putusan pengadilan dari %s tentang %s: %s. %s' % (C, t['q_id'], counts(ds, L), t['d_id'])
        b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede)]
        b.append('<p class="g-note">%s %s</p>' % ('Relevant standards:' if L == 'en' else 'Standar terkait:', E(t['std'])))
        courts = Counter(d['court'] for d in ds)
        b.append('<h2>%s</h2>' % ('Decisions' if L == 'en' else 'Putusan'))
        b.append(dec_list(ds, L, 60))
        b.append('<h2>%s</h2><ul class="sp-list">%s</ul>' % ('Courts' if L == 'en' else 'Pengadilan', ''.join('<li>%s: %d</li>' % (E(k_), n) for k_, n in courts.most_common())))
        corr = [x for x in CORRS if c in x]
        b.append('<h2>%s</h2><ul class="sp-chips"><li><a href="%s">%s</a></li><li><a href="%s">%s</a></li>%s</ul>' % (
            'See also' if L == 'en' else 'Lihat juga', u_country(c, L), E(C), u_topic(k, L), E(t[L] + (' in all countries' if L == 'en' else ' di semua negara')),
            ''.join('<li><a href="%s">%s → %s</a></li>' % (u_corr(o, d_, L), E(cn(o, L)), E(cn(d_, L))) for o, d_ in corr[:8])))
        b.append(foot_notes(L, path)); b.append(research_box(L, KW_EN if L == 'en' else KW_ID))
        crumbs = [(tr(L, 'home'), '/' if L == 'en' else '/?lang=id'), (tr(L, 'countries'), IDX['countries'][0 if L == 'en' else 1]), (C, u_country(c, L)), (t[L], path)]
        page(path, L, title, lede, '\n'.join(b), alt, {"about": [{"@type": "Country", "name": cn(c)}, {"@type": "Thing", "name": t['en']}]}, crumbs)

# ---------------------------------------------------------------- topic pages
TOPIC_N = {}
for t in TOPICS:
    ds = [d for d in D if in_topic(d, t)]; TOPIC_N[t['k']] = len(ds)
    for L in ('en', 'id'):
        path = u_topic(t['k'], L); alt = u_topic(t['k'], 'id' if L == 'en' else 'en')
        if L == 'en':
            title = '%s: court decisions and law on migrant workers' % t['en']
            lede = '%s The IMR databases hold %s on %s, from national, regional and international courts.' % (t['d_en'], counts(ds, L), t['q_en'])
        else:
            title = '%s: putusan pengadilan dan hukum tentang pekerja migran' % t['id']
            lede = '%s Basis data IMR memuat %s tentang %s, dari pengadilan nasional, kawasan, dan internasional.' % (t['d_id'], counts(ds, L), t['q_id'])
        b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede)]
        b.append('<p class="g-note">%s %s</p>' % ('Relevant standards:' if L == 'en' else 'Standar terkait:', E(t['std'])))
        byc = defaultdict(list)
        for d in ds: byc[d['country']].append(d)
        tiers = Counter(d['tier'] for d in ds)
        TN = {'national': ('national courts', 'pengadilan nasional'), 'regional': ('regional courts and bodies', 'pengadilan dan badan kawasan'), 'international': ('international bodies', 'badan internasional')}
        b.append('<ul class="sp-facts">' + ''.join('<li><b>%d</b>%s</li>' % (tiers[k_], E(TN[k_][0 if L == 'en' else 1])) for k_ in ('national', 'regional', 'international') if tiers[k_]) +
                 '<li><b>%d</b>%s</li></ul>' % (len(byc), 'countries' if L == 'en' else 'negara'))
        b.append('<h2>%s</h2>' % ('Decisions with full summaries' if L == 'en' else 'Putusan dengan ringkasan lengkap'))
        full = [d for d in ds if d['status'] != 'C']
        b.append(dec_list(full, L, 25, True) if full else '<p>%s</p>' % ('None yet; see the candidates below.' if L == 'en' else 'Belum ada; lihat kandidat di bawah.'))
        b.append('<h2>%s</h2>' % ('By country' if L == 'en' else 'Menurut negara'))
        b.append('<p class="g-note">%s</p>' % ('Countries in alphabetical order. Pages per country open where at least %d decisions are recorded.' % MIN_CT if L == 'en'
                                             else 'Negara disusun menurut abjad. Halaman per negara tersedia bila tercatat sedikitnya %d putusan.' % MIN_CT))
        lis = []
        for c in sorted(byc, key=lambda c: cn(c, L)):
            name = E(cn(c, L)); n = len(byc[c])
            if (c, t['k']) in CT: lis.append('<li><a href="%s">%s</a> (%d)</li>' % (u_ct(c, t['k'], L), name, n))
            elif c in COUNTRIES: lis.append('<li><a href="%s">%s</a> (%d)</li>' % (u_country(c, L), name, n))
            else: lis.append('<li>%s (%d)</li>' % (name, n))
        b.append('<ul class="sp-list" style="columns:2 220px">' + ''.join(lis) + '</ul>')
        if t['k'] == 'sector:domestic': b.append('<p><a href="/domestic-workers/">%s →</a></p>' % ('Migrant Domestic Workers database' if L == 'en' else 'Basis data Pekerja Rumah Tangga Migran'))
        if t['k'] == 'sector:farm': b.append('<p><a href="/migration-law/?lens=farm">%s →</a></p>' % ('Migration Law Atlas: farmworker view' if L == 'en' else 'Atlas Hukum Migrasi: tampilan buruh tani'))
        b.append('<p><a href="/court-decisions/">%s →</a></p>' % ('Search and compare all decisions in Court Decisions' if L == 'en' else 'Cari dan bandingkan semua putusan di Putusan Pengadilan'))
        b.append(foot_notes(L, path)); b.append(research_box(L, KW_EN if L == 'en' else KW_ID))
        crumbs = [(tr(L, 'home'), '/' if L == 'en' else '/?lang=id'), (tr(L, 'topics'), IDX['topics'][0 if L == 'en' else 1]), (t[L], path)]
        page(path, L, title, lede, '\n'.join(b), alt, {"about": {"@type": "Thing", "name": t['en']}}, crumbs)

# ---------------------------------------------------------------- corridor pages
def matched(o, d_):
    ro = re.compile(ORIGINS[o]['rx']); rd = re.compile(DESTS[d_])
    return [x for x in D if (x['country'] == d_ and ro.search(x['text'])) or (x['country'] == o and rd.search(x['text']))]
CORR_TOPICS = ['wages', 'fees', 'passport', 'employer', 'dismissed', 'forced', 'injury', 'arrest', 'residence', 'discrimination']
for o, d_ in CORRS:
    m = matched(o, d_); ag = agreements(o, d_); num = CORR.get((o, d_))
    for L in ('en', 'id'):
        O, Dn = cn(o, L), cn(d_, L); path = u_corr(o, d_, L); alt = u_corr(o, d_, 'id' if L == 'en' else 'en')
        if L == 'en':
            title = '%s migrant workers in %s: law, court decisions and legal help' % (ORIGINS[o]['dem'], Dn)
            lede = 'What the law says for workers who migrate from %s to %s: agreements between the two states, the labor and migration law of each side, court decisions from both, the treaties each has joined, and where to find free legal help.' % (O, Dn)
            if num: lede += ' Size of the corridor: %s %s.' % (format(num['n'], ','), num['en'])
        else:
            title = 'Pekerja migran %s di %s: hukum, putusan pengadilan, dan bantuan hukum' % (O, Dn)
            lede = 'Ketentuan hukum bagi pekerja yang bermigrasi dari %s ke %s, yakni perjanjian antara kedua negara, hukum ketenagakerjaan dan migrasi di masing-masing negara, putusan pengadilan dari keduanya, perjanjian internasional yang telah diikuti, serta tempat memperoleh bantuan hukum gratis.' % (O, Dn)
            if num: lede += ' Besaran koridor: %s %s.' % (format(num['n'], ',').replace(',', '.'), num['id'])
        b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede)]
        b.append('<ul class="sp-chips"><li><a href="%s">%s</a></li><li><a href="%s">%s</a></li></ul>' % (u_country(o, L), E(O), u_country(d_, L), E(Dn)))
        b.append('<h2>%s</h2>' % ('Agreements between %s and %s' % (O, Dn) if L == 'en' else 'Perjanjian antara %s dan %s' % (O, Dn)))
        if ag:
            b.append('<ul class="sp-list">' + ''.join('<li>%s <span class="g-note">%s%s</span></li>' % (
                ('<a href="%s" rel="noopener">%s</a>' % (E(r['url']), E(r['title'])) if r.get('url', '').startswith('http') else E(r['title'])),
                E(r.get('nature', '')), (' · ' + E(r.get('signed') or r.get('in_force'))) if (r.get('signed') or r.get('in_force')) else '') for r in ag) + '</ul>')
            b.append('<p class="g-note">%s</p>' % ('From the bilateral records in the %s data.' % ', '.join(sorted({DBNAME[r['db']][0] for r in ag})) if L == 'en'
                                                 else 'Dari catatan bilateral dalam data %s.' % ', '.join(sorted({DBNAME[r['db']][1] for r in ag}))))
        else:
            b.append('<p>%s</p>' % ('No bilateral agreement or memorandum between the two states is recorded in the databases yet. This does not mean none exists; corrections are welcome.' if L == 'en'
                                    else 'Belum ada perjanjian atau nota kesepahaman bilateral antara kedua negara yang tercatat dalam basis data. Hal tersebut tidak berarti perjanjian tersebut tidak ada; kami menerima koreksi.'))
        b.append('<h2>%s</h2>' % ('Treaty status side by side' if L == 'en' else 'Status perjanjian internasional berdampingan'))
        b.append(treaty_table([o, d_], L) if d_ not in ('HK', 'MO', 'TW') else treaty_table([o], L) + treaty_table([d_], L))
        if m:
            b.append('<h2>%s</h2>' % ('Court decisions on this corridor' if L == 'en' else 'Putusan pengadilan tentang koridor ini'))
            b.append('<p class="g-note">%s</p>' % ('Decisions from courts in %s that name %s workers, and decisions from courts in %s that concern work in %s (found by text search of the summaries).' % (Dn, ORIGINS[o]['dem'], O, Dn) if L == 'en'
                                                 else 'Putusan pengadilan di %s yang menyebut pekerja asal %s, dan putusan pengadilan di %s tentang kerja di %s (ditemukan melalui penelusuran teks ringkasan).' % (Dn, O, O, Dn)))
            b.append(dec_list(m, L, 20, True))
        b.append('<h2>%s</h2>' % ('Court decisions by topic, in both countries' if L == 'en' else 'Putusan pengadilan menurut topik, di kedua negara'))
        any_t = False; shown = set(x['id'] for x in m)
        for k in CORR_TOPICS:
            t = TOPIC[k]
            for c in (d_, o):
                ds = [x for x in by_c[c] if in_topic(x, t)]
                top = [x for x in order(ds) if x['id'] not in shown][:3]
                if not top: continue
                any_t = True; shown.update(x['id'] for x in top)
                link = u_ct(c, k, L) if (c, k) in CT else u_topic(k, L)
                b.append('<h3>%s: %s <span class="g-note">(%d)</span></h3>' % (E(t[L]), E(cn(c, L)), len(ds)))
                b.append(dec_list(top, L, 3))
                if len(ds) > 3: b.append('<p class="g-note"><a href="%s">%s →</a></p>' % (link, 'All %d decisions' % len(ds) if L == 'en' else 'Semua %d putusan' % len(ds)))
        if not any_t: b.append('<p>%s</p>' % ('No decisions recorded yet.' if L == 'en' else 'Belum ada putusan yang tercatat.'))
        for c, h_en, h_id in ((d_, 'Law in %s (destination)', 'Hukum di %s (negara tujuan)'), (o, 'Law in %s (country of origin)', 'Hukum di %s (negara asal)')):
            if CODED.get(c) or LAWS.get(c):
                b.append('<h2>%s</h2>' % E((h_en if L == 'en' else h_id) % cn(c, L)))
                if CODED.get(c): b.append(coded_table(c, L))
                if LAWS.get(c): b.append(law_rows(c, L, 15))
        for c in (d_, o):
            if PLACES.get(c):
                b.append('<h2>%s</h2>' % ('Free legal help in %s' % cn(c, L) if L == 'en' else 'Bantuan hukum gratis di %s' % cn(c, L)))
                b.append(help_list(c, L))
        b.append('<p><a href="/legal-clinic/">%s →</a></p>' % ('IMR Legal Clinic: prepare a rights communication' if L == 'en' else 'Klinik Hukum IMR: siapkan pengaduan hak'))
        b.append(foot_notes(L, path)); b.append(research_box(L, KW_EN if L == 'en' else KW_ID))
        crumbs = [(tr(L, 'home'), '/' if L == 'en' else '/?lang=id'), (tr(L, 'corridors'), IDX['corridors'][0 if L == 'en' else 1]), ('%s → %s' % (O, Dn), path)]
        page(path, L, title, lede, '\n'.join(b), alt, {"about": [{"@type": "Country", "name": cn(o)}, {"@type": "Country", "name": cn(d_)}]}, crumbs)

# ---------------------------------------------------------------- index pages
for L in ('en', 'id'):
    o_ = 0 if L == 'en' else 1; other = 1 - o_
    # countries
    title = 'Migrant workers’ rights by country' if L == 'en' else 'Hak pekerja migran menurut negara'
    lede = ('One page per country, with court decisions, laws and policies, treaty status, migration corridors and free legal help, drawn from the IMR open databases.' if L == 'en'
            else 'Satu halaman untuk setiap negara, berisi putusan pengadilan, peraturan dan kebijakan, status perjanjian internasional, koridor migrasi, dan bantuan hukum gratis, yang kami susun dari basis data terbuka IMR.')
    groups = [('Countries of origin', 'Negara asal', [c for c in COUNTRIES if c in ORIGINS]),
              ('Destinations in Asia and the Gulf', 'Negara tujuan di Asia dan Teluk', [c for c in COUNTRIES if c in DESTS and c not in ORIGINS]),
              ('Other countries with court decisions', 'Negara lain dengan putusan pengadilan', [c for c in COUNTRIES if c not in ORIGINS and c not in DESTS])]
    b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede)]
    for en, idn, cs in groups:
        b.append('<h2>%s</h2><ul class="sp-chips">%s</ul>' % (E(en if L == 'en' else idn), ''.join('<li><a href="%s">%s</a></li>' % (u_country(c, L), E(cn(c, L))) for c in sorted(cs, key=lambda c: cn(c, L)))))
    b.append('<p><a href="%s">%s →</a> · <a href="%s">%s →</a></p>' % (IDX['topics'][o_], E(tr(L, 'topics')), IDX['corridors'][o_], E(tr(L, 'corridors'))))
    page(IDX['countries'][o_], L, title, lede, '\n'.join(b), IDX['countries'][other], {"@type": "CollectionPage"}, [(tr(L, 'home'), '/'), (tr(L, 'countries'), IDX['countries'][o_])])
    # topics
    title = 'Migrant workers’ rights by topic' if L == 'en' else 'Hak pekerja migran menurut topik'
    lede = ('Court decisions on migrant workers grouped by the problem a worker faces, from unpaid wages and recruitment fees to detention and deportation.' if L == 'en'
            else 'Putusan pengadilan tentang pekerja migran yang kami kelompokkan menurut masalah yang dihadapi pekerja, mulai dari upah tidak dibayar dan biaya rekrutmen hingga penahanan dan deportasi.')
    b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede), '<ul class="sp-list">']
    for t in TOPICS:
        b.append('<li><a href="%s"><b>%s</b></a> <span class="g-note">(%d)</span><br>%s</li>' % (u_topic(t['k'], L), E(t[L]), TOPIC_N[t['k']], E(t['d_en'] if L == 'en' else t['d_id'])))
    b.append('</ul>')
    page(IDX['topics'][o_], L, title, lede, '\n'.join(b), IDX['topics'][other], {"@type": "CollectionPage"}, [(tr(L, 'home'), '/'), (tr(L, 'topics'), IDX['topics'][o_])])
    # corridors
    title = 'Migration corridors: law for migrant workers from origin to destination' if L == 'en' else 'Koridor migrasi: hukum bagi pekerja migran dari negara asal ke negara tujuan'
    lede = ('One page per origin–destination pair, with the agreements between the two states, the law on each side, court decisions and free legal help.' if L == 'en'
            else 'Satu halaman untuk setiap pasangan negara asal dan tujuan, berisi perjanjian antara kedua negara, hukum di masing-masing pihak, putusan pengadilan, dan bantuan hukum gratis.')
    b = ['<h1 class="g-h1">%s</h1>' % E(title), '<p class="sp-lede">%s</p>' % E(lede)]
    byo = defaultdict(list)
    for o, d_ in CORRS: byo[o].append(d_)
    for o in sorted(byo, key=lambda c: cn(c, L)):
        b.append('<h2>%s</h2><ul class="sp-chips">%s</ul>' % (E(('From %s' if L == 'en' else 'Dari %s') % cn(o, L)),
                 ''.join('<li><a href="%s">%s</a></li>' % (u_corr(o, d_, L), E(cn(d_, L))) for d_ in sorted(byo[o], key=lambda c: cn(c, L)))))
    page(IDX['corridors'][o_], L, title, lede, '\n'.join(b), IDX['corridors'][other], {"@type": "CollectionPage"}, [(tr(L, 'home'), '/'), (tr(L, 'corridors'), IDX['corridors'][o_])])

# ---------------------------------------------------------------- sitemap
sp = os.path.join(SITE, 'sitemap.xml'); s = open(sp, encoding='utf-8').read()
s = re.sub(r'\s*<url><loc>https://theimr\.org/(?:countries|topics|corridors|id/negara|id/topik|id/koridor)/[^<]*</loc>[^\n]*</url>', '', s)
s = s.replace('</urlset>', ''.join('\n  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>' % (BASE, u, TODAY) for u in URLS) + '\n</urlset>')
open(sp, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- llms.txt
lp = os.path.join(SITE, 'llms.txt'); s = open(lp, encoding='utf-8').read()
s = re.sub(r'\n## Browse by country, topic and corridor\n.*?(?=\n## |\Z)', '', s, flags=re.S)
sec = ['\n## Browse by country, topic and corridor',
       '- [Countries](%s/countries/): one page per country (%d) with court decisions, laws, treaty status, corridors and free legal help. Indonesian: %s/id/negara/' % (BASE, len(COUNTRIES), BASE),
       '- [Topics](%s/topics/): court decisions by problem (%d topics), e.g. unpaid wages, recruitment fees, passport confiscation, detention and deportation. Indonesian: %s/id/topik/' % (BASE, len(TOPICS), BASE),
       '- [Migration corridors](%s/corridors/): %d origin–destination pages, e.g. [Indonesian workers in Malaysia](%s%s). Indonesian: %s/id/koridor/' % (BASE, len(CORRS), BASE, u_corr('ID', 'MY', 'en') if ('ID', 'MY') in CORRS else '/corridors/', BASE)]
sec += ['- [%s](%s%s)' % (t['en'], BASE, u_topic(t['k'], 'en')) for t in TOPICS]
s = s.rstrip('\n') + '\n' + '\n'.join(sec) + '\n'
open(lp, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- links from existing pages
ap = os.path.join(SITE, 'court-decisions', 'all', 'index.html'); s = open(ap, encoding='utf-8').read()
s = re.sub(r' <a class="sp-cl" href="[^"]*">[^<]*</a>', '', s)
for c in COUNTRIES:
    a = re.sub(r'\W+', '-', cn(c).lower())
    s = re.sub(r'(<h2 id="c-%s">.*?)(</h2>)' % re.escape(a), lambda m: m.group(1) + ' <a class="sp-cl" href="%s">Laws, treaties and corridors for %s →</a>' % (u_country(c, 'en'), E(cn(c))) + m.group(2), s, count=1)
s = s.replace('<a class="sp-cl" ', '<a class="sp-cl" style="font-size:15px;font-weight:400;margin-left:8px" ')
open(ap, 'w', encoding='utf-8').write(s)

dp = os.path.join(SITE, 'databases', 'index.html'); s = open(dp, encoding='utf-8').read()
s = re.sub(r'<section id="sp-browse".*?</section>', '', s, flags=re.S)
block = ('<section id="sp-browse" style="max-width:1120px;margin:40px auto 0;padding:0 24px"><h2 style="font-weight:400">Browse by country, topic or corridor</h2>'
         '<p>Plain pages that bring the databases together for one country, one problem or one migration route.</p>'
         '<ul class="sp-chips" style="display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0">'
         '<li><a href="/countries/" style="display:inline-flex;min-height:40px;align-items:center;padding:0 12px;border:1px solid currentColor;text-decoration:none">Countries (%d)</a></li>'
         '<li><a href="/topics/" style="display:inline-flex;min-height:40px;align-items:center;padding:0 12px;border:1px solid currentColor;text-decoration:none">Topics (%d)</a></li>'
         '<li><a href="/corridors/" style="display:inline-flex;min-height:40px;align-items:center;padding:0 12px;border:1px solid currentColor;text-decoration:none">Migration corridors (%d)</a></li></ul></section>') % (len(COUNTRIES), len(TOPICS), len(CORRS))
s = s.replace('</main>', block + '</main>', 1)
open(dp, 'w', encoding='utf-8').write(s)

# Indonesian strings for the two hub links (the site switch translates them on /databases/ and /court-decisions/all/)
LP = os.path.join(SITE, 'assets', 'lang.js'); Ls = open(LP, encoding='utf-8').read()
ADD = {"Browse by country, topic or corridor": "Telusuri menurut negara, topik, atau koridor",
       "Plain pages that bring the databases together for one country, one problem or one migration route.": "Halaman sederhana yang menghimpun basis data untuk satu negara, satu masalah, atau satu jalur migrasi."}
PATS = [["^Countries \\((\\d+)\\)$", "Negara ($1)"], ["^Topics \\((\\d+)\\)$", "Topik ($1)"], ["^Migration corridors \\((\\d+)\\)$", "Koridor migrasi ($1)"],
        ["^Laws, treaties and corridors for (.+) →$", "Peraturan, perjanjian, dan koridor untuk $1 →"]]
add = ''.join(json.dumps(k, ensure_ascii=False) + ':' + json.dumps(v, ensure_ascii=False) + ',' for k, v in ADD.items() if json.dumps(k, ensure_ascii=False) + ':' not in Ls)
if add: Ls = Ls.replace('window.SITE_I18N={"id":{', 'window.SITE_I18N={"id":{' + add, 1)
new = [p for p in PATS if json.dumps(p[0], ensure_ascii=False) not in Ls]
if new: Ls = Ls.replace('"__pat":[', '"__pat":[' + ','.join(json.dumps(p, ensure_ascii=False) for p in new) + ',', 1)
open(LP, 'w', encoding='utf-8').write(Ls)

print('countries', len(COUNTRIES), '| country x topic', len(CT), '| topics', len(TOPICS), '| corridors', len(CORRS), '| pages written', len(URLS))
