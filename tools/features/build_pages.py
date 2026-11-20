#!/usr/bin/env python3
"""Writes the static shells of the new pages: /compare/, /timeline/, /coverage/, /laws/, /follow/, /report/.
The header, menu and footer are copied from site/contact.html, so the pages follow whatever look the site has
(rerun after the site look changes, or rerun build/newspaper-build/puncak_green.py SITE, which recolours them).
The world map on /coverage/ is drawn here as plain SVG from tools/features/world-110m.topo.json (Natural Earth,
public domain), so the page needs no map library and works on slow phones.
Usage: python3 tools/features/build_pages.py [REPO_ROOT]
"""
import html, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import countries as CT

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, 'site')
E = html.escape


def shell():
    t = open(os.path.join(SITE, 'contact.html'), encoding='utf-8').read()
    a = t.index('<figure class="imr-band"') if '<figure class="imr-band"' in t else t.index('</header>') + len('</header>')
    b = t.index('<div class="imr-ridge"')
    head, tail = t[:a], t[b:]
    # band (photo or hills) kept as it is on Contact
    band = ''
    m = re.search(r'<figure class="imr-band.*?</figure>', t, re.S)
    if m:
        band = m.group(0)
    head = head.replace(' aria-current="page" style="color: #8F5E12; text-decoration: underline; text-underline-offset: 6px; padding: 10px 0"',
                        ' style="color: #2E2116; text-decoration: none; padding: 10px 0"')
    # relative links on Contact -> absolute, since the new pages live in folders
    for f in ('publications.html', 'people.html', 'contact.html', 'favicon.ico', 'favicon-32.png', 'apple-touch-icon.png'):
        head = head.replace(f'href="{f}"', f'href="/{f}"')
    return head, band, tail


def page(path, title, desc, body, scripts=(), noindex=False, band=True):
    head, bandhtml, tail = SHELL
    h = head
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)} · Institute for Migrant Rights</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h)
    url = 'https://theimr.org' + path
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(title)} · Institute for Migrant Rights">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h)
    if noindex:
        h = h.replace('</title>', '</title>\n<meta name="robots" content="noindex">', 1)
    h = h.replace('</head>', '<link rel="stylesheet" href="/features/ft.css">\n</head>', 1)
    if band and bandhtml and bandhtml not in h:
        h = h + bandhtml
    if not band and bandhtml:
        h = h.replace(bandhtml, '')
    js = ''.join(f'<script src="{s}" defer></script>\n' for s in scripts)
    t = h + '\n<main id="main" class="ft" data-noi18n>\n' + body + '\n</main>\n' + tail.replace('<script src="/assets/lang.js" defer></script>',
                                                                                    '<script src="/assets/lang.js" defer></script>\n' + js)
    out = os.path.join(SITE, path.strip('/'), 'index.html') if path.endswith('/') else os.path.join(SITE, path.strip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(t)
    return out


def T(en, idn, tag='span', cls='', extra=''):
    """Bilingual text: English in the page, Indonesian in data-id; ft.js swaps them with the site language switch."""
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-id="{E(idn)}"{extra}>{en}</{tag}>'


def intro(eye_en, eye_id, h_en, h_id, lede_en, lede_id):
    return ('<div class="ft-wrap ft-intro">' + T(eye_en, eye_id, 'p', 'ft-eye') + T(h_en, h_id, 'h1') +
            T(lede_en, lede_id, 'p', 'ft-lede') + '</div>')


# ---------- world map -----------------------------------------------------------------------------------------
def equal_earth(lon, lat):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    M = math.sqrt(3) / 2
    p = math.asin(M * math.sin(math.radians(lat)))
    p2 = p * p; p6 = p2 * p2 * p2
    x = math.radians(lon) * math.cos(p) / (M * (A1 + 3 * A2 * p2 + p6 * (7 * A3 + 9 * A4 * p2)))
    y = p * (A1 + A2 * p2 + p6 * (A3 + A4 * p2))
    return x, y


def world_svg():
    topo = json.load(open(os.path.join(HERE, 'world-110m.topo.json')))
    sx, sy = topo['transform']['scale']; tx, ty = topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    W = 960; S = W / (2 * equal_earth(180, 0)[0]); H0 = equal_earth(0, 90)[1]

    def P(lon, lat):
        x, y = equal_earth(lon, lat)
        return (W / 2 + x * S, H0 * S - y * S)

    def ring(r):
        pts = []
        for i in r:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        out = []; last = None
        for lon, lat in pts:
            q = P(lon, lat); q = (round(q[0], 1), round(q[1], 1))
            if q != last:
                out.append(q); last = q
        if len(out) < 3:
            return ''
        # break the outline where it jumps across the map (rings cut at the antimeridian)
        d = ''; prev = None
        for x, y in out:
            d += ('M' if prev is None or abs(x - prev[0]) > W / 3 else 'L') + f'{x:g},{y:g}'
            prev = (x, y)
        return d + ('Z' if abs(out[0][0] - out[-1][0]) <= W / 3 else '')

    paths = []
    for g in topo['objects']['countries']['geometries']:
        iso = CT.NUM.get(g.get('id') or '')
        if not iso:
            continue
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        d = ''.join(ring(r) for poly in polys for r in poly)
        if d:
            name = CT.BY2[iso][2]
            paths.append(f'<path data-c="{iso}" d="{d}"><title>{E(name)}</title></path>')
    dots = []
    for iso, (lon, lat) in CT.DOTS.items():
        x, y = P(lon, lat)
        dots.append(f'<circle data-c="{iso}" cx="{x:.1f}" cy="{y:.1f}" r="4.5"><title>{E(CT.BY2[iso][2])}</title></circle>')
    ys = [float(v) for v in re.findall(r'[ML][\d.]+,([\d.]+)', ''.join(paths))]
    H = round(max(ys) + 6)
    return (f'<svg class="ft-map" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ft-map-t" focusable="false">'
            f'<title id="ft-map-t">World map of data coverage</title><g class="ft-land">{"".join(paths)}</g>'
            f'<g class="ft-dots">{"".join(dots)}</g></svg>')


# ---------- pages ---------------------------------------------------------------------------------------------
NOTE_SUM = ('<p class="ft-flag">' + T('The plain summaries are written in simple Indonesian with the help of AI from the notes in the '
            'database, not from a fresh reading of the legal text. They are not legal advice. Read the official text, and ask for free '
            'legal help with your own problem.', 'Ringkasan dalam bahasa sederhana ini kami tulis dengan bantuan AI dari catatan di basis data, '
            'bukan dari membaca ulang teks hukumnya. Ringkasan ini bukan nasihat hukum. Bacalah teks resminya, dan mintalah bantuan '
            'hukum gratis untuk masalah anda.') + ' <a href="/ai-use/">' + T('How we use AI', 'Cara kami memakai AI') + '</a> · '
            '<a href="/legal-help/">' + T('Find free legal help', 'Cari bantuan hukum gratis') + '</a></p>')


def build():
    pages = []
    # Compare -------------------------------------------------------------------------------------------------
    body = intro('Migration Jurisprudence from the South', 'Yurisprudensi Migrasi dari Selatan',
                 'Compare two countries', 'Bandingkan dua negara',
                 'Pick two countries to see their rules side by side: the laws we list, coded features such as recruitment fees '
                 'or domestic-worker protection, treaties, agreements and court decisions. Every line links back to its source.',
                 'Pilih dua negara untuk melihat aturannya berdampingan, yakni undang-undang yang kami catat, fitur hukum yang dikodekan '
                 'seperti biaya rekrutmen atau pelindungan pekerja rumah tangga, perjanjian internasional, perjanjian bilateral, serta '
                 'putusan pengadilan. Setiap baris tertaut ke sumbernya.')
    body += ('<div class="ft-wrap"><form class="ft-pick" id="cmp-form" onsubmit="return false">'
             '<label>' + T('First country', 'Negara pertama') + '<select id="cmp-a"></select></label>'
             '<label>' + T('Second country', 'Negara kedua') + '<select id="cmp-b"></select></label>'
             '<label>' + T('Topic', 'Topik') + '<select id="cmp-topic"></select></label>'
             '</form><p class="ft-note" id="cmp-share"></p><div id="cmp-out" aria-live="polite"></div>' + NOTE_SUM + '</div>')
    pages.append(page('/compare/', 'Compare two countries’ migration laws',
                      'Pick two countries and see their migration and labor rules side by side: recruitment fees, domestic-worker protection, treaties, agreements and court decisions.',
                      body, ['/features/ft.js', '/features/compare.js']))

    # Timeline ------------------------------------------------------------------------------------------------
    body = intro('Migration Jurisprudence from the South', 'Yurisprudensi Migrasi dari Selatan',
                 'How the law changed', 'Bagaimana hukum berubah',
                 'A timeline for each country: when laws were adopted or amended, dated reforms, treaties ratified and court decisions. '
                 'Built from the same data as the database pages.',
                 'Lini masa untuk setiap negara, yakni kapan undang-undang disahkan atau diubah, reformasi bertanggal, perjanjian '
                 'internasional yang diratifikasi, dan putusan pengadilan. Disusun dari data yang sama dengan halaman basis data.')
    body += ('<div class="ft-wrap"><form class="ft-pick" onsubmit="return false">'
             '<label>' + T('Country', 'Negara') + '<select id="tl-c"></select></label>'
             '<fieldset class="ft-kinds"><legend>' + T('Show', 'Tampilkan') + '</legend>'
             + ''.join(f'<label class="ft-chk"><input type="checkbox" value="{k}" checked> {T(en, idn)}</label>'
                       for k, en, idn in [('law', 'Laws', 'Undang-undang'), ('change', 'Reforms', 'Reformasi'),
                                          ('treaty', 'Treaties', 'Perjanjian internasional'), ('agreement', 'Agreements', 'Perjanjian bilateral'),
                                          ('court', 'Court decisions', 'Putusan pengadilan')]) +
             '</fieldset></form><div id="tl-out" aria-live="polite"></div>'
             '<p class="ft-note">' + T('Dates are as recorded in each database. A year alone means the day is not yet confirmed. '
                                       'Court decisions not yet checked by an editor are counted per year, not listed.',
                                       'Tanggal sesuai catatan di setiap basis data. Tahun saja berarti tanggal persisnya belum dipastikan. '
                                       'Putusan yang belum diperiksa editor dihitung per tahun dan tidak didaftar satu per satu.') + '</p></div>')
    pages.append(page('/timeline/', 'How migration law changed, country by country',
                      'A timeline of migration and labor law for each country: laws adopted and amended, reforms, treaty ratifications and court decisions.',
                      body, ['/features/ft.js', '/features/timeline.js']))

    # Coverage ------------------------------------------------------------------------------------------------
    legend = ''.join(f'<span class="ft-key"><i class="k{n}"></i>{n}</span>' for n in range(0, 8))
    body = intro('Migration Jurisprudence from the South', 'Yurisprudensi Migrasi dari Selatan',
                 'How complete is our data?', 'Seberapa lengkap data kami?',
                 'The map shows how many of seven kinds of data we hold for each country. It measures our own work, not the '
                 'country: a pale country is one where we still need help. Tap a country to see what is there and what is missing.',
                 'Peta ini menunjukkan berapa dari tujuh jenis data yang sudah kami miliki untuk setiap negara. Yang diukur adalah '
                 'pekerjaan kami sendiri, bukan negaranya. Negara yang berwarna pucat adalah tempat kami masih membutuhkan bantuan. '
                 'Ketuk sebuah negara untuk melihat data yang ada dan yang belum ada.')
    body += ('<div class="ft-wrap"><div class="ft-mapbox">' + world_svg() + '</div>'
             '<p class="ft-legend">' + T('Kinds of data held (of 7):', 'Jenis data yang dimiliki (dari 7):') + ' ' + legend + '</p>'
             '<div id="cov-panel" class="ft-panel" aria-live="polite"></div>'
             '<h2>' + T('Every country, A to Z', 'Semua negara, A sampai Z') + '</h2>'
             '<p><label class="ft-inline">' + T('Find a country', 'Cari negara') + ' <input id="cov-q" type="search" autocomplete="off"></label> '
             '<label class="ft-chk"><input type="checkbox" id="cov-gaps"> ' + T('Only countries with gaps', 'Hanya negara yang datanya belum lengkap') + '</label></p>'
             '<div class="ft-scroll" tabindex="0" role="region" aria-label="Coverage table"><table class="ft-t" id="cov-t"></table></div>'
             '<div class="ft-help">' + T('Can you help fill a gap?', 'Bisakah anda membantu mengisi kekosongan?', 'h2') +
             T('Students, lawyers and volunteers can find official laws, court decisions and treaty records for the pale countries. '
               'Write to us and say which country and which kind of data you can help with.',
               'Mahasiswa, advokat, dan relawan dapat membantu mencari teks resmi undang-undang, putusan pengadilan, dan catatan '
               'perjanjian internasional untuk negara-negara yang masih pucat. Tulislah kepada kami, sebutkan negara dan jenis data '
               'yang dapat anda bantu.', 'p') +
             '<p><a class="ft-btn" href="mailto:secretariat@theimr.org?subject=Help%20with%20data%20coverage">secretariat@theimr.org</a></p></div>'
             '<p class="ft-note">' + T('The seven kinds: national laws listed; coded legal features; bilateral and regional agreements; '
                                       'treaty status (ILO and UN); court decisions; dated law changes; checked free legal help. A count says '
                                       'that something is recorded, not that it is complete or checked; the panel shows how many entries an '
                                       'editor has checked.',
                                       'Tujuh jenis data tersebut adalah undang-undang nasional, fitur hukum yang dikodekan, perjanjian '
                                       'bilateral dan kawasan, status perjanjian internasional (ILO dan PBB), putusan pengadilan, perubahan '
                                       'hukum bertanggal, serta bantuan hukum gratis yang sudah dicek. Angka hanya menunjukkan bahwa ada '
                                       'catatan, bukan bahwa catatan itu lengkap atau sudah diperiksa. Panel menunjukkan berapa entri yang '
                                       'sudah diperiksa editor.') + '</p></div>')
    pages.append(page('/coverage/', 'Data coverage map',
                      'A world map of how complete the IMR migration-law data is for each country, and where volunteers can help fill the gaps.',
                      body, ['/features/ft.js', '/features/coverage.js']))

    # Laws in plain words -------------------------------------------------------------------------------------
    body = intro('Migration Jurisprudence from the South', 'Yurisprudensi Migrasi dari Selatan',
                 'Laws in plain words', 'Hukum dalam bahasa sederhana',
                 'Every law and instrument in our databases, each with a two-line summary in simple Indonesian for migrant workers '
                 'and their families. Summaries marked “to be checked” still need a person to compare them with the official text.',
                 'Semua undang-undang dan instrumen di basis data kami, masing-masing dengan ringkasan dua baris dalam bahasa Indonesia '
                 'sederhana untuk pekerja migran dan keluarganya. Ringkasan yang bertanda “perlu dicek” masih harus dibandingkan '
                 'dengan teks resminya oleh seseorang.')
    body += ('<div class="ft-wrap">' + NOTE_SUM + '<form class="ft-pick" onsubmit="return false">'
             '<label>' + T('Country or group', 'Negara atau kelompok') + '<select id="lw-c"></select></label>'
             '<label>' + T('Search', 'Cari') + '<input id="lw-q" type="search" autocomplete="off"></label>'
             '<label class="ft-chk ft-chk-b"><input type="checkbox" id="lw-chk"> ' + T('Only summaries still to be checked', 'Hanya ringkasan yang perlu dicek') + '</label>'
             '</form><p class="ft-note" id="lw-count"></p><div id="lw-out"></div>'
             '<p class="ft-note"><a href="/plain-summaries/data/laws-id.csv" download>' + T('Download all summaries (CSV)', 'Unduh semua ringkasan (CSV)') + '</a></p></div>')
    pages.append(page('/laws/', 'Laws in plain words (Indonesian summaries)',
                      'Every law and instrument in the IMR databases with a two-line summary in simple Indonesian for migrant workers. Summaries, not legal advice.',
                      body, ['/features/ft.js', '/features/laws.js']))

    # Follow a country ----------------------------------------------------------------------------------------
    body = intro('Updates', 'Kabar terbaru', 'Follow a country', 'Ikuti sebuah negara',
                 'Choose the countries you care about. When we add a law, a court decision or a change for one of them, we send you '
                 'a short email. Nothing else, and you can stop at any time.',
                 'Pilih negara yang anda pedulikan. Setiap kali kami menambahkan undang-undang, putusan pengadilan, atau perubahan untuk '
                 'negara tersebut, kami mengirimkan surel singkat kepada anda. Hanya itu, dan anda dapat berhenti kapan saja.')
    body += ('<div class="ft-wrap"><form id="follow-form" class="ft-form" name="follow-country" method="POST" action="/follow/thanks/" '
             'data-netlify="true" netlify-honeypot="website">'
             '<input type="hidden" name="form-name" value="follow-country">'
             '<p hidden><label>Website <input name="website"></label></p>'
             '<fieldset><legend>' + T('Countries to follow', 'Negara yang diikuti') + '</legend>'
             '<p><input id="fl-q" type="search" autocomplete="off" aria-label="Find a country"></p>'
             '<div id="fl-list" class="ft-cgrid"></div><input type="hidden" name="countries" id="fl-countries"></fieldset>'
             '<label>' + T('Email', 'Surel') + '<input type="email" name="email" required autocomplete="email"></label>'
             '<label>' + T('Language of the email', 'Bahasa surel') + '<select name="language"><option value="en">English</option>'
             '<option value="id">Bahasa Indonesia</option></select></label>'
             '<label class="ft-chk"><input type="checkbox" name="consent" value="yes" required> ' +
             T('I ask IMR to email me about these countries. I can unsubscribe with one click in any email.',
               'Saya meminta IMR mengirimi saya surel tentang negara-negara ini. Saya dapat berhenti berlangganan dengan satu klik di setiap surel.') +
             '</label><p><button class="ft-btn" type="submit">' + T('Follow', 'Ikuti') + '</button></p>'
             '<p class="ft-note">' + T('We use your address only for these emails. We never add addresses we did not receive from you, and we never share them.',
                                       'Alamat anda hanya kami pakai untuk surel ini. Kami tidak pernah menambahkan alamat yang tidak anda berikan sendiri, '
                                       'dan tidak pernah membagikannya.') + '</p></form>'
             + '<h2>' + T('Or follow with a feed reader (RSS)', 'Atau ikuti melalui pembaca umpan (RSS)') + '</h2>'
             '<p class="ft-note">' + T('No email needed. Paste one of these addresses into a feed reader such as Feedly, Inoreader or Thunderbird.',
                                       'Tanpa surel. Tempelkan salah satu alamat ini ke aplikasi pembaca umpan (feed reader), misalnya Feedly, Inoreader, atau Thunderbird.') + '</p>'
             '<ul class="ft-note"><li><a href="/feeds/decisions.xml">' + T('New court decisions', 'Putusan pengadilan baru') + '</a></li>'
             '<li><a href="/updates/feed.xml">' + T('What is new in the databases (monthly)', 'Kabar baru di basis data (bulanan)') + '</a></li>'
             '<li><a href="/feed.xml">' + T('Migration and farmworker law news', 'Berita hukum migrasi dan buruh tani') + '</a></li></ul>'
             '<div class="ft-pick"><label>' + T('Feed for one country', 'Umpan untuk satu negara') + '<select id="fd-c"></select></label>'
             '<p class="ft-chk-b" style="margin:0 0 10px"><a id="fd-link" href="/feeds/c/ID.xml">/feeds/c/ID.xml</a></p></div>'
             + (('<p class="ft-note">' + T('Prefer one email a month about everything?', 'Lebih suka satu surel sebulan tentang semuanya?') +
                 ' <a href="/updates/">' + T('Monthly updates', 'Kabar bulanan') + '</a></p>') if os.path.isdir(os.path.join(SITE, 'updates')) else '')
             + '</div>')
    pages.append(page('/follow/', 'Follow a country: email alerts',
                      'Get a short email when IMR adds a law, court decision or change for the countries you follow. Opt-in only.',
                      body, ['/features/ft.js', '/features/follow.js']))
    body = intro('Updates', 'Kabar terbaru', 'Thank you', 'Terima kasih',
                 'Please check your inbox: we send one email to confirm the address before anything else.',
                 'Silakan periksa kotak masuk anda. Kami mengirim satu surel untuk memastikan alamat anda sebelum surel lainnya.')
    body += '<div class="ft-wrap"><p><a href="/compare/">' + T('Compare two countries', 'Bandingkan dua negara') + '</a></p></div>'
    pages.append(page('/follow/thanks/', 'Thank you', 'Thank you for following.', body, ['/features/ft.js'], noindex=True))

    # Report a problem ----------------------------------------------------------------------------------------
    body = intro('Data quality', 'Mutu data', 'Report a problem', 'Laporkan masalah',
                 'Did you see a wrong date, a broken link, a missing law or a poor translation? Tell us. An editor checks every '
                 'report against the official source.',
                 'Apakah anda melihat tanggal yang salah, tautan yang rusak, undang-undang yang belum tercatat, atau terjemahan '
                 'yang kurang tepat? Beri tahu kami. Editor memeriksa setiap laporan dengan sumber resminya.')
    kinds = [('wrong', 'Something is wrong (date, name, coding, summary)', 'Ada yang salah (tanggal, nama, kode, ringkasan)'),
             ('link', 'A link is broken or not official', 'Tautan rusak atau bukan tautan resmi'),
             ('missing', 'Something is missing', 'Ada yang belum tercatat'),
             ('outdated', 'The law has changed', 'Hukumnya sudah berubah'),
             ('translation', 'Translation problem', 'Masalah terjemahan'),
             ('other', 'Something else', 'Lainnya')]
    body += ('<div class="ft-wrap"><form id="report-form" class="ft-form" name="data-problem" method="POST" action="/report/thanks/" '
             'data-netlify="true" netlify-honeypot="website">'
             '<input type="hidden" name="form-name" value="data-problem">'
             '<p hidden><label>Website <input name="website"></label></p>'
             '<label>' + T('Page', 'Halaman') + '<input name="page" id="rp-page" inputmode="url"></label>'
             '<label>' + T('Entry (law, decision or country), if any', 'Entri (undang-undang, putusan, atau negara), jika ada') + '<input name="entry" id="rp-entry"></label>'
             '<fieldset><legend>' + T('What is the problem?', 'Apa masalahnya?') + '</legend>' +
             ''.join(f'<label class="ft-chk"><input type="radio" name="kind" value="{k}" required> {T(en, idn)}</label>' for k, en, idn in kinds) +
             '</fieldset>'
             '<label>' + T('Tell us more', 'Ceritakan lebih lanjut') + '<textarea name="details" rows="5" required></textarea></label>'
             '<label>' + T('Official source that shows the right answer (link), if you have one', 'Sumber resmi yang menunjukkan jawaban yang benar (tautan), jika ada') +
             '<input name="source" type="url" inputmode="url" placeholder="https://"></label>'
             '<label>' + T('Your email, only if you want a reply', 'Surel anda, hanya jika anda ingin dibalas') + '<input name="email" type="email" autocomplete="email"></label>'
             '<p class="ft-note">' + T('Please do not write personal details about a legal case here. For help with your own case, use the Legal Clinic.',
                                       'Mohon jangan menulis data pribadi tentang perkara hukum di sini. Untuk bantuan atas perkara anda sendiri, gunakan Klinik Hukum.') +
             ' <a href="/legal-clinic/">' + T('Legal Clinic', 'Klinik Hukum') + '</a></p>'
             '<input type="hidden" name="language" id="rp-lang" value="en">'
             '<p><button class="ft-btn" type="submit">' + T('Send the report', 'Kirim laporan') + '</button></p></form></div>')
    pages.append(page('/report/', 'Report a problem with the data',
                      'Tell the Institute for Migrant Rights about a wrong date, broken link, missing law or poor translation in its databases.',
                      body, ['/features/ft.js', '/features/report.js'], noindex=True))
    body = intro('Data quality', 'Mutu data', 'Thank you', 'Terima kasih',
                 'Your report has reached the editors. We check it against the official source and correct the database if needed. '
                 'Corrections show in the history of the data on GitHub.',
                 'Laporan anda sudah sampai ke editor. Kami memeriksanya dengan sumber resmi dan memperbaiki basis data bila perlu. '
                 'Perbaikan tercatat dalam riwayat data di GitHub.')
    body += '<div class="ft-wrap"><p><a href="/databases/">' + T('Back to the databases', 'Kembali ke basis data') + '</a></p></div>'
    pages.append(page('/report/thanks/', 'Thank you', 'Thank you for your report.', body, ['/features/ft.js'], noindex=True))
    for p in pages:
        print('build_pages:', os.path.relpath(p, ROOT))


SHELL = shell()
if __name__ == '__main__':
    build()
