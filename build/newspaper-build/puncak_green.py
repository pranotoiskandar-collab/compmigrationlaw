# "Puncak green" look for theimr.org (Pranoto chose look B on 2026-11-19).
# 1. Turns the Soga browns back into the Puncak tea-garden greens (inverse of palette.py soga; status colours untouched).
# 2. Replaces the old-photo banners (figure.imr-band) with drawn Gede-Pangrango tea-hill bands (/images/puncak/hills-N.svg).
# 3. Legal Clinic: the hills band replaces the banana leaves in the hero. Homepage: a large hills band under the hero.
# Idempotent. Usage: python3 puncak_green.py SITE       Rerun last, after palette.py (or instead of palette.py SITE soga).
import colorsys, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P
from hills_lib import landscape

INV = {v: k for k, v in P.cmap('soga').items()}
INV['#3D5A4C'] = '#3D5A4D'
INV.update({'#F9F7F6': '#F4F8F5'})
RGBA = {'rgba(46,33,22,': 'rgba(23,45,36,'}

def stray(h):
    # leftover low-saturation browns (hue 18-34) follow the green neutral hue
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5)); hh, l, s = colorsys.rgb_to_hls(r, g, b)
    if 18 <= hh * 360 <= 34 and 0.06 < s < 0.45:
        r, g, b = colorsys.hls_to_rgb(152 / 360, l, s / 1.05)
        return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))
    return h

def recolour(t):
    t = re.sub(r'#[0-9A-Fa-f]{6}\b', lambda m: INV.get(m.group(0).upper()) or stray(m.group(0).upper()), t)
    for a, b in RGBA.items(): t = t.replace(a, b)
    return t

GREEN = dict(sky0="#EEF4F0", sky1="#D7E6DC", sun="#F2E3B3", far="#B2C7BC", h1="#7FA08C", h2="#3F6E55", h3="#24493A", row="#CFE2D3", tree="#24493A")
# four variants so pages don't all look the same: (peaks_x, seed offset, trees, sun)
VARIANTS = {1: (1750, 0, False, False), 2: (650, 3, False, False), 3: (1450, 6, True, False), 4: (1750, 0, True, True)}

def svgs(site):
    d = os.path.join(site, 'images', 'puncak'); os.makedirs(d, exist_ok=True)
    for n, (px, sd, trees, sun) in VARIANTS.items():
        H = 520 if n == 4 else 340
        L, A = ((0.62, 0.76, 0.92), (0.12, 0.10, 0.08)) if n == 4 else ((0.70, 0.82, 0.94), (0.12, 0.10, 0.08))
        s = landscape(2400, H, GREEN, peaks_x=px, uid=f"h{n}", trees=trees, sun=sun, L=L, A=A)
        s = s.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1).replace('class="land" ', '')
        s = s.replace('xMidYMax slice', 'xMaxYMax slice' if px > 1200 else 'xMinYMax slice')
        open(os.path.join(d, f'hills-{n}.svg'), 'w').write(s)

PHOTO_VARIANT = {'cianjur-railway-station': 1, 'sawah-priangan': 2, 'gede-rice-fields': 1, 'sindanglaya-plain': 3,
                 'pasir-nangka-tea-fields': 3, 'pasir-nangka-tea-estate': 2, 'cimacan-road': 3, 'cisokan-bridge': 2, 'cianjur-alun-alun': 1}

def band(n, h='clamp(96px,13vw,190px)', extra=''):
    return (f'<figure class="imr-band imr-hills" aria-hidden="true" style="margin:0;position:relative;line-height:0;background:#EEF4F0{extra}">'
            f'<img src="/images/puncak/hills-{n}.svg" alt="" decoding="async" width="2400" height="340" '
            f'style="display:block;width:100%;height:{h};object-fit:cover;object-position:{"left" if n == 2 else "right"} bottom"></figure>')

FIG = re.compile(r'<figure class="imr-band"[^>]*><img src="/images/cianjur-old/([a-z-]+)\.jpg".*?</figure>', re.S)

def patch(p, t):
    t = FIG.sub(lambda m: band(PHOTO_VARIANT.get(m.group(1), 1)), t)
    rel = p.replace('\\', '/')
    if rel.endswith('legal-clinic/index.html') and 'lc-hero has-banana' in t:
        t = re.sub(r'<div class="banana"[^>]*></div>', '', t)
        t = t.replace('<section class="lc-hero has-banana">', band(3) + '<section class="lc-hero">', 1)
    if re.search(r'(^|/)site/index\.html$', rel) and 'data-hills="home"' not in t:
        i = t.index('<section class="hero split">'); j = t.index('</section>', i) + len('</section>')
        t = t[:j] + '<style>html{overflow-x:clip}</style>' + band(4, 'clamp(150px,20vw,290px)', ';width:100vw;margin-left:calc(50% - 50vw);margin-bottom:28px').replace('<figure ', '<figure data-hills="home" ', 1) + t[j:]
    return t

if __name__ == '__main__':
    SITE = sys.argv[1]; svgs(SITE); n = 0
    for root, _, files in os.walk(SITE):
        for f in files:
            if not f.endswith(('.html', '.css', '.js', '.svg')) or '/images/puncak' in root.replace('\\', '/'): continue
            p = os.path.join(root, f); s = open(p, encoding='utf-8').read(); t = recolour(s)
            if f.endswith('.html'): t = patch(os.path.abspath(p), t)
            if t != s: open(p, 'w', encoding='utf-8').write(t); n += 1
    print('puncak green applied to', n, 'files')
