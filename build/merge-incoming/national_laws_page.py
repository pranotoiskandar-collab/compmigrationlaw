"""Write /migration-law/national-laws/: the national laws of states without a regional page of their own.

Usage (from the repository root): python3 build/merge-incoming/national_laws_page.py
Reads data/migration-law/national-laws.csv. The page shell (header, menu, footer, look) is copied from
site/court-decisions/all/index.html, like build/search-pages/build.py does, so it follows the current look.
Indonesian for the headings and labels goes into site/assets/lang.js. Adds the page to sitemap.xml and llms.txt
and links it from /migration-law/ and /databases/. Idempotent: rerun after any change to the table.
Descriptive only: no scores or rankings.
"""
import csv, html, json, os, re
from collections import OrderedDict, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = os.path.join(ROOT, "site")
DATE = "2026-11-20"
PATH = "/migration-law/national-laws/"
E = lambda x: html.escape(str(x or ""), quote=True)

R = list(csv.DictReader(open(os.path.join(ROOT, "data/migration-law/national-laws.csv"), encoding="utf-8")))
NAMES = {"ZA": "South Africa", "KE": "Kenya", "UG": "Uganda", "GH": "Ghana", "NG": "Nigeria", "ZW": "Zimbabwe",
         "EG": "Egypt", "LB": "Lebanon", "IQ": "Iraq", "IL": "Israel", "JO": "Jordan", "MO": "Macau", "MN": "Mongolia",
         "CN": "China", "FJ": "Fiji", "PG": "Papua New Guinea", "WS": "Samoa", "TO": "Tonga", "VU": "Vanuatu",
         "SB": "Solomon Islands", "KI": "Kiribati", "TV": "Tuvalu", "NR": "Nauru", "AU": "Australia", "NZ": "New Zealand"}
REG = OrderedDict([("africa", ("Africa", "Afrika")), ("mideast", ("Middle East (outside the Gulf States)", "Timur Tengah (di luar Negara-Negara Teluk)")),
                   ("asia", ("East Asia (outside the East Asia page)", "Asia Timur (di luar halaman Asia Timur)")),
                   ("pacific", ("Pacific, with Australia and New Zealand", "Pasifik, dengan Australia dan Selandia Baru"))])
TYPE = {"statute": "Statute", "regulation": "Regulation", "decision": "Ministerial decision", "policy": "Policy",
        "guidance": "Official guidance", "agreement": "Agreement", "draft": "Bill"}
LINK = {"text": "Official text", "guidance": "Official guidance", "db": "Official database", "secondary": "PacLII (secondary source)",
        "un": "UNODC SHERLOC (UN-hosted copy)"}
ID = {
    "National laws: other regions": "Undang-undang nasional: kawasan lain",
    "Migration Law Atlas": "Atlas Hukum Migrasi",
    "Statute": "Undang-undang", "Regulation": "Peraturan", "Ministerial decision": "Keputusan menteri", "Policy": "Kebijakan",
    "Official guidance": "Panduan resmi", "Agreement": "Perjanjian", "Bill": "Rancangan undang-undang",
    "Official text": "Teks resmi", "Official database": "Basis data resmi", "PacLII (secondary source)": "PacLII (sumber sekunder)",
    "UNODC SHERLOC (UN-hosted copy)": "UNODC SHERLOC (salinan di situs PBB)",
    "Law or policy": "Peraturan atau kebijakan", "Year": "Tahun", "Type": "Jenis", "Subject": "Pokok", "Source": "Sumber",
    "Unverified": "Belum diverifikasi", "Download the table (CSV)": "Unduh tabel (CSV)", "Codebook (CSV)": "Buku kode (CSV)",
    "How to read this table": "Cara membaca tabel ini", "Jump to": "Langsung ke",
    "Find free legal help": "Cari bantuan hukum gratis", "How we use AI": "Cara kami memakai AI",
    "Court decisions from these countries": "Putusan pengadilan dari negara-negara ini",
    "This page is for research and advocacy. It is not legal advice.": "Halaman ini disusun untuk penelitian dan advokasi, dan bukan merupakan nasihat hukum.",
}
for k, (en, idn) in REG.items():
    ID[en] = idn

shell = open(os.path.join(SITE, "court-decisions", "all", "index.html"), encoding="utf-8").read()
HEAD = shell[:shell.index("<main")]; FOOT = shell[shell.index("</main>") + 7:]
HEAD = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", HEAD, flags=re.S)
HEAD = re.sub(r'<meta (?:property|name)="(?:og|twitter):(?:title|description|url)"[^>]*>\s*', "", HEAD)
HEAD = re.sub(r'<link rel="alternate" hreflang[^>]*>\s*', "", HEAD)
HEAD = re.sub(r'\s*aria-current="[^"]*"', "", HEAD)
FOOT = re.sub(r'<section id="imr-research".*?</section>\s*', "", FOOT, flags=re.S)

# The court-decisions shell still carries an older menu (a doubled "Know your rights" link, no "Case of the month"
# or "Tools"); use the menu the homepage and earlier search pages carry (2026-11-20).
_KYR = '<a href="/rights-checklist/">Know your rights before you go</a>\n'
HEAD = HEAD.replace(_KYR + _KYR, _KYR)
if 'href="/court-decisions/highlights/"' not in HEAD:
    HEAD = HEAD.replace('<a href="/court-decisions/">Court Decisions</a>\n</div>', '<a href="/court-decisions/">Court Decisions</a>\n'
        '<a href="/court-decisions/highlights/" style="padding-left:28px">Case of the month</a>\n'
        '<span style="display:block;padding:12px 16px 2px;font:500 11px \'Figtree\',monospace;letter-spacing:.12em;text-transform:uppercase;color:#3D5A4D">Tools</span>\n'
        '<a href="/ratifications/">Ratification tracker</a>\n<a href="/research/">Saved searches and reading list</a>\n</div>', 1)

title = "National laws: other regions"
n_c = len({r["s"] for r in R})
desc = (f"{len(R)} national migration, labour and trafficking laws from {n_c} states in Africa, the Middle East outside the Gulf, "
        "East Asia and the Pacific, each with a link to its source. Gathered with AI help from official portals; not yet read by a person.")
h = re.sub(r"<title>.*?</title>", f"<title>{E(title)} · Institute for Migrant Rights</title>", HEAD, count=1, flags=re.S)
h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h, count=1)
h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://theimr.org{PATH}">', h, count=1)
ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "National laws: other regions", "description": desc,
      "url": "https://theimr.org" + PATH, "version": "2026.11.20", "dateModified": DATE, "inLanguage": ["en", "id"],
      "isPartOf": {"@type": "DataCatalog", "name": "Migration Jurisprudence from the South", "url": "https://theimr.org/databases/"},
      "creator": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                        "contentUrl": "https://theimr.org/migration-law/data/national-laws.csv"}]}
extra = (f'<meta property="og:title" content="{E(title)}">\n<meta property="og:description" content="{E(desc)}">\n'
         f'<meta property="og:url" content="https://theimr.org{PATH}">\n'
         f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
         '<style id="nl-css">.nl-main{padding:40px 0 64px}.nl-main .g-wrap{max-width:1060px}'
         '.nl-main h1{font-weight:400;font-size:clamp(30px,5vw,46px);line-height:1.12;margin:10px 0 0}'
         '.nl-main h2{font-weight:500;font-size:26px;margin:44px 0 6px;padding-top:18px;border-top:1px solid rgba(127,127,127,.35)}'
         '.nl-main h3{font-size:19px;font-weight:600;margin:24px 0 6px}.nl-lede{font-size:18px;line-height:1.55;max-width:800px}'
         '.nl-jump{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:15px}</style>\n')
h = h.replace("</head>", extra + "</head>", 1)

by = defaultdict(lambda: defaultdict(list))
for r in R:
    by[r["region"]][r["s"]].append(r)


def table(rs):
    s = ('<div class="g-scroll"><table class="g-t"><thead><tr><th>Law or policy</th><th>Year</th><th>Type</th><th>Subject</th>'
         "<th>Source</th></tr></thead><tbody>")
    for r in sorted(rs, key=lambda r: (r["year"] or "0"), reverse=True):
        t = f'<span data-noi18n>{E(r["title"])}</span>'
        if r["orig"]:
            t += f'<br><span class="g-note" data-noi18n>{E(r["orig"])}</span>'
        if r["no"] and r["no"] not in r["title"]:
            t += f'<br><span class="g-note" data-noi18n>{E(r["no"])}</span>'
        subj = r["topic"] + (f" · {r['farm_domestic']}" if r["farm_domestic"] else "")
        s += (f'<tr><td>{t}</td><td class="c">{E(r["year"])}</td><td>{TYPE.get(r["type"], E(r["type"]))}</td>'
              f'<td data-noi18n>{E(subj)}</td><td><a href="{E(r["url"])}" rel="noopener">{LINK.get(r["link"], "Source")}</a>'
              f'<br><span class="g-note">{E(r["status"])}</span></td></tr>')
    return s + "</tbody></table></div>"


cn = lambda c: NAMES.get(c, c)
body = ['<p class="g-note"><a href="/databases/">Migration Jurisprudence from the South</a> › <a href="/migration-law/">Migration Law Atlas</a></p>',
        f"<h1>{E(title)}</h1>",
        f'<p class="nl-lede" data-noi18n>{E(desc)}</p>',
        '<p data-noi18n>The Gulf States, East Asia (Taiwan, South Korea, Japan, Hong Kong), Southeast Asia and the countries of origin '
        'have their own pages with coded comparisons. This table lists laws of other states that the databases cite or that came up in '
        'our searches of official portals, so that they can be found and checked. Global and regional instruments are in the '
        '<a href="/migration-law/">Migration Law Atlas</a>.</p>',
        '<h2 id="read">How to read this table</h2>',
        '<ul data-noi18n><li><b>Unverified</b>: the row was found with AI help on the source named and has not yet been read by a person. '
        'Titles, years and subjects come from the source listing. See <a href="/ai-use/">How we use AI</a>.</li>'
        '<li><b>PacLII (secondary source)</b>: the Pacific Islands Legal Information Institute (University of the South Pacific) is not a '
        'government site. Most Pacific governments publish no searchable database of their own.</li>'
        '<li><b>UNODC SHERLOC (UN-hosted copy)</b>: the text as filed with the UN Office on Drugs and Crime legislation database, '
        'not the national gazette.</li>'
        '<li><b>Official guidance</b>: a ministry or agency page that explains the law; not the legislation itself.</li></ul>',
        '<p><a href="/migration-law/data/national-laws.csv" data-goatcounter-click="event/download/national-laws-csv">Download the table (CSV)</a> · '
        '<a href="/migration-law/data/national-laws-codebook.csv">Codebook (CSV)</a></p>',
        '<p class="nl-jump"><b>Jump to</b> ' + " · ".join(f'<a href="#{k}">{E(v[0])}</a>' for k, v in REG.items() if by.get(k)) + "</p>",
        '<div id="laws">']
for k, (en, _) in REG.items():
    if not by.get(k):
        continue
    body.append(f'<h2 id="{k}">{E(en)}</h2>')
    for c in sorted(by[k], key=cn):
        body.append(f'<h3 id="c-{c.lower()}" data-noi18n>{E(cn(c))} <span class="g-note">({len(by[k][c])})</span></h3>')
        body.append(table(by[k][c]))
body.append("</div>")
body.append('<p class="g-note">This page is for research and advocacy. It is not legal advice.</p>')
body.append('<p><a href="/legal-help/">Find free legal help</a> · <a href="/court-decisions/all/">Court decisions from these countries</a> · '
            '<a href="/ai-use/">How we use AI</a></p>')
main = '<main class="nl-main" id="national-laws"><div class="g-wrap">' + "\n".join(body) + "</div></main>"
out = os.path.join(SITE, PATH.strip("/"), "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(h + main + FOOT)

# Indonesian strings
LP = os.path.join(SITE, "assets", "lang.js"); Ls = open(LP, encoding="utf-8").read()
add = "".join(f"{json.dumps(k, ensure_ascii=False)}:{json.dumps(v, ensure_ascii=False)}," for k, v in ID.items()
              if json.dumps(k, ensure_ascii=False) + ":" not in Ls)
if add:
    Ls = Ls.replace('window.SITE_I18N={"id":{', 'window.SITE_I18N={"id":{' + add, 1)
    open(LP, "w", encoding="utf-8").write(Ls)

# sitemap and llms.txt
sp = os.path.join(SITE, "sitemap.xml"); s = open(sp, encoding="utf-8").read()
if f"https://theimr.org{PATH}<" not in s:
    s = s.replace("</urlset>", f"  <url><loc>https://theimr.org{PATH}</loc><lastmod>{DATE}</lastmod></url>\n</urlset>")
    open(sp, "w", encoding="utf-8").write(s)
lp = os.path.join(SITE, "llms.txt"); s = open(lp, encoding="utf-8").read()
if PATH not in s:
    line = f"- [National laws: other regions](https://theimr.org{PATH}): {len(R)} national laws from Africa, the Middle East, East Asia and the Pacific (unverified, with source links)\n"
    k = s.find("https://theimr.org/migration-law/")
    if k > 0:
        k = s.index("\n", k) + 1; s = s[:k] + line + s[k:]
    else:
        s += "\n" + line
    open(lp, "w", encoding="utf-8").write(s)
else:
    s = re.sub(r"\): \d+ national laws from Africa", f"): {len(R)} national laws from Africa", s)
    open(lp, "w", encoding="utf-8").write(s)

# links from the Atlas (register of norms) and the databases page
SNIP = (f'<p class="muted" id="nl-link"><a href="{PATH}">National laws: other regions</a>: {len(R)} national laws from Africa, '
        'the Middle East, East Asia and the Pacific, with source links.</p>')
p = os.path.join(SITE, "migration-law/index.html"); t = open(p, encoding="utf-8").read()
if 'id="nl-link"' in t:
    t = re.sub(r'<p class="muted" id="nl-link">.*?</p>', SNIP, t, count=1, flags=re.S)
else:
    t = t.replace('<p class="muted" id="normsintro"></p>', '<p class="muted" id="normsintro"></p>' + SNIP, 1)
open(p, "w", encoding="utf-8").write(t)
CARD = (f'<li id="nl-card"><a href="{PATH}"><b>National laws: other regions</b><span>{len(R)} national laws from Africa, the Middle East, '
        'East Asia and the Pacific that have no regional page yet, each with its source. Unverified.</span><i>Open →</i></a></li>')
p = os.path.join(SITE, "databases/index.html"); t = open(p, encoding="utf-8").read()
if 'id="nl-card"' in t:
    t = re.sub(r'<li id="nl-card">.*?</li>', CARD, t, count=1, flags=re.S)
else:
    k = t.index('<a href="/migration-law/"><b>Migration Law Atlas</b>'); k = t.index("</li>", k) + 5
    t = t[:k] + CARD + t[k:]
open(p, "w", encoding="utf-8").write(t)
ID[f"{len(R)} national laws from Africa, the Middle East, East Asia and the Pacific that have no regional page yet, each with its source. Unverified."] = (
    f"{len(R)} undang-undang nasional dari Afrika, Timur Tengah, Asia Timur, dan Pasifik yang belum memiliki halaman kawasan sendiri, masing-masing dengan sumbernya. Belum diverifikasi.")
ID["Open →"] = "Buka →"
Ls = open(LP, encoding="utf-8").read()
add = "".join(f"{json.dumps(k, ensure_ascii=False)}:{json.dumps(v, ensure_ascii=False)}," for k, v in ID.items()
              if json.dumps(k, ensure_ascii=False) + ":" not in Ls)
if add:
    Ls = Ls.replace('window.SITE_I18N={"id":{', 'window.SITE_I18N={"id":{' + add, 1)
    open(LP, "w", encoding="utf-8").write(Ls)
print("national laws page:", len(R), "laws,", n_c, "states")
