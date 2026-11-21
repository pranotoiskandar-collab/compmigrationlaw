#!/usr/bin/env python3
"""Draw the homepage picture of the Court Decisions database from the data itself.

A world map with one circle per country, sized by the number of decisions that
concern it, plus the split by court level and by outcome. Every number is
counted from data/court-decisions/decisions.csv, so the picture cannot fall
behind the data: tools/publish/60_home_cases.py runs this at every deploy.

The figure sits in site/index.html between <!-- imr-home-cases:start --> and
<!-- imr-home-cases:end -->. Its Indonesian text is added to site/assets/lang.js.

Usage: python3 tools/home_cases.py [SITE_DIR]   (default: site/)
"""
import collections
import csv
import html
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'site')
FEAT = os.path.join(ROOT, 'tools', 'features')
sys.path.insert(0, FEAT)
import countries as CT  # noqa: E402

START, END = '<!-- imr-home-cases:start -->', '<!-- imr-home-cases:end -->'
E = html.escape
W = 960


def equal_earth(lon, lat):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    M = math.sqrt(3) / 2
    p = math.asin(M * math.sin(math.radians(lat)))
    p2 = p * p; p6 = p2 * p2 * p2
    x = math.radians(lon) * math.cos(p) / (M * (A1 + 3 * A2 * p2 + p6 * (7 * A3 + 9 * A4 * p2)))
    y = p * (A1 + A2 * p2 + p6 * (A3 + A4 * p2))
    return x, y


S = W / (2 * equal_earth(180, 0)[0])
H0 = equal_earth(0, 90)[1]


def P(lon, lat):
    x, y = equal_earth(lon, lat)
    return W / 2 + x * S, H0 * S - y * S


def land():
    """Land outline (whole numbers, Antarctica left out) and a point inside each country."""
    topo = json.load(open(os.path.join(FEAT, 'world-110m.topo.json')))
    sx, sy = topo['transform']['scale']; tx, ty = topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    d_all, centre = [], {}
    for g in topo['objects']['countries']['geometries']:
        iso = CT.NUM.get(g.get('id') or '')
        if iso == 'AQ':
            continue
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        best = None
        for poly in polys:
            for k, r in enumerate(poly):
                pts = []
                for i in r:
                    a = arcs[i] if i >= 0 else arcs[~i][::-1]
                    pts.extend(a if not pts else a[1:])
                q = []
                for lon, lat in pts:
                    xy = tuple(round(v) for v in P(lon, lat))
                    if not q or xy != q[-1]:
                        q.append(xy)
                if len(q) < 3:
                    continue
                d, prev = '', None
                for x, y in q:
                    d += ('M' if prev is None or abs(x - prev[0]) > W / 3 else 'L') + f'{x},{y}'
                    prev = (x, y)
                d_all.append(d + 'Z')
                if k == 0:  # outer ring: keep the largest one for the label point
                    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                    if max(xs) - min(xs) > 180:
                        continue
                    area = (max(xs) - min(xs)) * (max(ys) - min(ys))
                    if not best or area > best[0]:
                        best = (area, pts)
        if iso and best:
            pts = best[1]
            centre[iso] = P(sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    for iso, (lon, lat) in CT.DOTS.items():
        centre[iso] = P(lon, lat)
    # places where the average of the outline falls badly (long coasts, far islands)
    for iso, (lon, lat) in {'CL': (-71, -33), 'US': (-98, 39), 'CA': (-100, 56), 'RU': (60, 56), 'NZ': (174, -40),
                            'ID': (113, -2), 'PH': (122, 12), 'JP': (138, 36), 'NO': (9, 61), 'FR': (2.5, 46.5),
                            'MY': (102, 4), 'GB': (-1.5, 52.5), 'FJ': (178, -17.8), 'KI': (173, 1.4)}.items():
        centre[iso] = P(lon, lat)
    return ''.join(d_all), centre


def fmt(n, lang):
    s = f'{n:,}'
    return s.replace(',', '.') if lang == 'id' else s


def build():
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'court-decisions', 'decisions.csv'), encoding='utf-8')))
    n = len(rows)
    by_c = collections.Counter(r['country'] for r in rows if r['country'])
    tiers = collections.Counter(r['tier'] for r in rows)
    out = collections.Counter(r['outcome'] for r in rows)
    d, centre = land()
    k = 30 / math.sqrt(max(by_c.values()))
    circles, labels = [], []
    placed = [(iso, c) for iso, c in by_c.items() if iso in centre]
    for iso, c in sorted(placed, key=lambda t: -t[1]):  # big circles first, small ones on top
        x, y = centre[iso]
        r = max(2.2, k * math.sqrt(c))
        names = CT.BY2.get(iso)
        en = names[2] if names else iso
        idn = names[3] if names else iso
        word = 'decision' if c == 1 else 'decisions'
        circles.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"><title>{E(en)}: {c:,} {word}</title></circle>')
    for iso, c in by_c.most_common(6):
        if iso not in centre:
            continue
        x, y = centre[iso]
        r = k * math.sqrt(c)
        names = CT.BY2.get(iso)
        labels.append((iso, x, y, r, names[2] if names else iso, names[3] if names else iso, c))
    ys = [int(v) for v in re.findall(r'[ML]\d+,(\d+)', d)]
    H = max(ys) + 4
    # place each label right, left, below or above its circle, whichever first stays clear of the
    # labels already placed, the big circles and the map edge
    boxes, lab_svg = [], ''
    big = [(centre[i][0], centre[i][1], k * math.sqrt(c)) for i, c in by_c.most_common(12) if i in centre]
    for _, x, y, r, en, _, c in labels:
        text = f'{en} {c:,}'
        w, h = 10.5 * len(text), 20
        tries = [(x + r + 5, y - h / 2, 'start'), (x - r - 5 - w, y - h / 2, 'end'),
                 (x - w / 2, y + r + 3, 'middle'), (x - w / 2, y - r - 3 - h, 'middle')]
        def clear(bx, by):
            if bx < 0 or bx + w > W or by < 0:
                return False
            if any(bx < X + WW and bx + w > X and by < Y + HH and by + h > Y for X, Y, WW, HH in boxes):
                return False
            return not any(cx + cr > bx and cx - cr < bx + w and cy + cr > by and cy - cr < by + h
                           for cx, cy, cr in big if (cx, cy) != (x, y))
        bx, by, anchor = next((t for t in tries if clear(t[0], t[1])), tries[0])
        boxes.append((bx, by, w, h))
        tx = {'start': bx, 'end': bx + w, 'middle': bx + w / 2}[anchor]
        lab_svg += (f'<text x="{tx:.0f}" y="{by + 15:.0f}" text-anchor="{anchor}">{E(en)} <tspan>{c:,}</tspan></text>')
    svg = (f'<svg class="hc-map" viewBox="0 0 {W} {H}" role="img" aria-labelledby="hc-t" focusable="false">'
           f'<title id="hc-t">World map: court decisions in the database by country</title>'
           f'<path class="hc-land" d="{d}"/><g class="hc-dots">{"".join(circles)}</g>'
           f'<g class="hc-lab" data-noi18n>{lab_svg}</g></svg>')
    countries = len(by_c)
    coded = out['won'] + out['lost'] + out['advisory']
    T = {  # English -> Indonesian; numbers are filled in for both
        'cap': (f'{fmt(n, "en")} court decisions on migrant workers, from {countries} countries',
                f'{fmt(n, "id")} putusan pengadilan tentang pekerja migran, dari {countries} negara'),
        'sub': ('Each circle is one country, sized by the number of its decisions in the database.',
                'Setiap lingkaran merupakan satu negara; ukurannya mengikuti jumlah putusannya dalam basis data.'),
        'nat': ('national courts', 'pengadilan nasional'),
        'reg': ('regional courts', 'pengadilan kawasan'),
        'int': ('international bodies', 'badan internasional'),
        'won': ('worker side won', 'pihak pekerja menang'),
        'lost': ('worker side lost', 'pihak pekerja kalah'),
        'adv': ('advisory', 'nasihat hukum'),
        'tbc': ('still to be read and coded', 'belum dibaca dan dikodekan'),
        'coded': (f'Read and coded so far: {fmt(coded, "en")}.', f'Sudah dibaca dan dikodekan: {fmt(coded, "id")}.'),
        'src': ('Source: IMR Court Decisions database, counted when this page was published.',
                'Sumber: basis data Putusan Pengadilan IMR, dihitung saat halaman ini diterbitkan.'),
        'more': ('Explore the decisions →', 'Jelajahi putusan →'),
    }
    t = {k: v[0] for k, v in T.items()}
    bar_total = n or 1
    seg = [('won', out['won'], '#1E6B4A'), ('lost', out['lost'], '#172D24'), ('adv', out['advisory'], '#9CC9B2'),
           ('tbc', n - coded, 'transparent')]
    bar = ''.join(f'<i style="width:{100 * v / bar_total:.2f}%;background:{c}" title="{E(t[key])}: {v:,}"></i>'
                  for key, v, c in seg if v)
    fig = (
        f'{START}<figure class="hc" style="margin:0">'
        f'<figcaption class="hc-cap">{E(t["cap"])}</figcaption>'
        f'<p class="hc-sub">{E(t["sub"])}</p>{svg}'
        f'<div class="hc-tiers"><div><b>{fmt(tiers["national"], "en")}</b><span>{t["nat"]}</span></div>'
        f'<div><b>{fmt(tiers["regional"], "en")}</b><span>{t["reg"]}</span></div>'
        f'<div><b>{fmt(tiers["international"], "en")}</b><span>{t["int"]}</span></div></div>'
        f'<div class="hc-bar" aria-hidden="true">{bar}</div>'
        f'<p class="hc-legend"><span>{E(t["coded"])}</span> '
        f'<span style="--c:#1E6B4A">{t["won"]}</span> <b data-noi18n>{out["won"]}</b> · '
        f'<span style="--c:#172D24">{t["lost"]}</span> <b data-noi18n>{out["lost"]}</b> · '
        f'<span style="--c:#9CC9B2">{t["adv"]}</span> <b data-noi18n>{out["advisory"]}</b> · '
        f'<span style="--c:transparent;--b:1">{t["tbc"]}</span> <b data-noi18n>{fmt(n - coded, "en")}</b></p>'
        f'<p class="src" style="font-size:11.5px;margin-top:8px">{E(t["src"])} <a href="/court-decisions/">{E(t["more"])}</a></p>'
        f'<style>.hc-cap{{margin:0 0 4px;font:700 17px/1.3 var(--sans)}}.hc p.hc-sub{{margin:0 0 8px;font-size:13.5px;line-height:1.45;color:#3D5A4D}}'
        f'.hc-map{{display:block;width:100%;height:auto;max-width:640px}}.hc-land{{fill:#DCE8E0;stroke:#fff;stroke-width:.6}}'
        f'.hc-dots circle{{fill:rgba(30,107,74,.55);stroke:#1E6B4A;stroke-width:.8}}.hc-dots circle:hover{{fill:#1E6B4A}}'
        f'.hc-lab text{{font:600 19px var(--sans,sans-serif);fill:#172D24;paint-order:stroke;stroke:#F6F8F5;stroke-width:4px}}'
        f'.hc-lab tspan{{font-weight:800}}'
        f'.hc-tiers{{display:flex;gap:8px;margin:10px 0 8px;max-width:640px}}.hc-tiers div{{flex:1;background:#EEF4F0;padding:8px 10px;border-radius:6px}}'
        f'.hc-tiers b{{display:block;font:800 20px/1.1 var(--sans)}}.hc-tiers span{{font-size:12px;color:#3D5A4D}}'
        f'.hc-bar{{display:flex;height:10px;max-width:640px;box-shadow:inset 0 0 0 1px #9AB3A6;border-radius:3px;overflow:hidden}}'
        f'.hc-bar i{{display:block;height:100%}}.hc p.hc-legend{{font-size:13px;margin:6px 0 0;max-width:640px;line-height:1.6}}'
        f'.hc-legend span[style]::before{{content:"";display:inline-block;width:10px;height:10px;margin-right:4px;vertical-align:-1px;'
        f'background:var(--c);box-shadow:inset 0 0 0 calc(var(--b,0)*1px) #9AB3A6}}</style>'
        f'</figure>{END}')
    return fig, {v[0]: v[1] for v in T.values()}


def main():
    fig, id_pairs = build()
    p = os.path.join(SITE, 'index.html')
    s = open(p, encoding='utf-8').read()
    if START in s:
        s = s[:s.index(START)] + fig + s[s.index(END) + len(END):]
    else:  # first run: replace the old square chart
        m = re.search(r'<figure style="margin:0"><figcaption[^>]*>[^<]*Each square is one\..*?</figure>', s, re.S)
        if not m:
            sys.exit('home_cases: could not find the decisions figure on the homepage')
        s = s[:m.start()] + fig + s[m.end():]
    s = re.sub(r'\.units\{[^}]*\}\n?|\.units i[^{]*\{[^}]*\}\n?|@media \(max-width:600px\)\{\.units\{[^}]*\}\}\n?', '', s)
    open(p, 'w', encoding='utf-8').write(s)
    # the other places that state the number of decisions (plain digits: lang.js matches them with \\d+)
    n = len(list(csv.DictReader(open(os.path.join(ROOT, 'data', 'court-decisions', 'decisions.csv'), encoding='utf-8'))))
    for rel, pat in (('index.html', r'\d+(?= decisions, searchable by situation)'),
                     ('court-decisions/index.html', r'(?<=Browse all )\d+(?= decisions as a list)'),
                     ('court-decisions/all/index.html', r'(?<=<p>)\d+(?= decisions on migrant workers from national)')):
        fp = os.path.join(SITE, rel)
        if os.path.exists(fp):
            t = open(fp, encoding='utf-8').read()
            t2 = re.sub(pat, str(n), t)
            if t2 != t:
                open(fp, 'w', encoding='utf-8').write(t2)
    lp = os.path.join(SITE, 'assets', 'lang.js')
    js = open(lp, encoding='utf-8').read()
    pre = 'window.SITE_I18N={"id":{'
    add = {k: v for k, v in id_pairs.items() if json.dumps(k, ensure_ascii=False) + ':' not in js}
    if add and js.startswith(pre):
        js = pre + ''.join(f'{json.dumps(k, ensure_ascii=False)}:{json.dumps(v, ensure_ascii=False)},' for k, v in add.items()) + js[len(pre):]
        open(lp, 'w', encoding='utf-8').write(js)
    print(f'home_cases: homepage figure updated ({len(fig) // 1024} KB), {len(add)} Indonesian strings added')


if __name__ == '__main__':
    main()
