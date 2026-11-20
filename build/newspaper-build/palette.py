# Colour palette swap for theimr.org (2026-11-17, Pranoto asked for a different palette). Idempotent per palette.
# Usage: python3 palette.py SITE laut|soga|navy     (or: python3 palette.py --map NAME  -> prints JSON map)
# Every colour of the Puncak green family is moved to the new hue, keeping its lightness, so contrast stays the same.
# Status/chart colours (yellows, reds, the won/lost greens of badges) are left alone.
import colorsys, json, os, re, sys
GREEN = ['#172D24','#1E6B4A','#3D5A4D','#3D5A4C','#2E493D','#B2C7BC','#DCE8E1','#E5EEE8','#EEF4F0','#F6FAF7','#9CC9B2','#134A33',
         '#D8E5DE','#BCCFC5','#C7D8CE','#7F9A8C','#D6E3DC','#6F8A7D','#E8F2EC','#F3F7F4','#9AB3A6','#DCE6E0','#FBFCFA']
ACCENT = {'#1E6B4A', '#134A33', '#9CC9B2'}
# name: (neutral hue, neutral saturation factor, accent hue, accent saturation factor)
PAL = {'laut': (205, 1.0, 195, 1.15), 'soga': (28, 1.05, 14, 1.35), 'navy': (218, 1.1, 12, 1.6)}
def conv(h, hue, sf):
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5))
    _, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hue / 360, l, min(1, s * sf))
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))
FIX = {'navy': {'#1E6B4A': '#B4472A', '#134A33': '#8C3218', '#9CC9B2': '#E6B3A3'}, 'soga': {'#1E6B4A': '#8F5E12', '#134A33': '#6B450B', '#9CC9B2': '#E3C58F'}}
def cmap(name):
    nh, ns, ah, as_ = PAL[name]
    m = {g: conv(g, ah, as_) if g in ACCENT else conv(g, nh, ns) for g in GREEN}
    m.update(FIX.get(name, {})); return m
def rgba(name):
    c = cmap(name)['#172D24']; return {'rgba(23,45,36,': 'rgba(%d,%d,%d,' % tuple(int(c[i:i+2], 16) for i in (1, 3, 5))}
STATUS = {'#2E6B27', '#D5E6D0', '#CFE3D8', '#1F4D1A'}  # 'won' badges on decision pages keep their green
def other(h, name):
    # stray tints and shades of the old green family (hue 120-165, low saturation) follow the neutral hue
    if h in STATUS: return h
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5)); hh, l, sat = colorsys.rgb_to_hls(r, g, b)
    if 120 <= hh * 360 <= 165 and sat > 0.06 and (sat < 0.4 or l > 0.8): return conv(h, PAL[name][0], PAL[name][1])
    return h
def apply_text(t, name):
    m = cmap(name)
    t = re.sub(r'#[0-9A-Fa-f]{6}\b', lambda x: m.get(x.group(0).upper()) or other(x.group(0).upper(), name), t)
    for a, b in rgba(name).items(): t = t.replace(a, b)
    return t
if __name__ == '__main__':
    if sys.argv[1] == '--map': print(json.dumps({'map': cmap(sys.argv[2]), 'rgba': rgba(sys.argv[2])})); sys.exit()
    SITE, NAME = sys.argv[1], sys.argv[2]; n = 0
    for root, _, files in os.walk(SITE):
        for f in files:
            if not f.endswith(('.html', '.css', '.js', '.svg')): continue
            p = os.path.join(root, f); s = open(p, encoding='utf-8').read(); t = apply_text(s, NAME)
            if t != s: open(p, 'w', encoding='utf-8').write(t); n += 1
    print(NAME, 'palette applied to', n, 'files')
