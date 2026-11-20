# Drawing helpers copied from the flyer alt-layout script (flyer/alt-layouts/make_alts.py).
"""Three alternative 'nature / Puncak hills' layouts of the IMR flyer.
Reads ../imr-flyer-en.html, writes alt-a-tea-hills.html, alt-b-puncak-green.html, alt-c-photo-ridge.html here.
Each alternative = the same content + an override <style> + an illustrated SVG landscape (drawn here, no external art)."""
import os, re, math, random



def wave(y0, amp, w=2100, n=6, seed=1, phase=0.0):
    """smooth hill line from x=0..w around baseline y0"""
    rnd = random.Random(seed)
    pts = []
    for i in range(n + 1):
        x = w * i / n
        y = y0 - amp * (0.55 + 0.45 * math.sin(i * 1.7 + phase)) * (0.7 + 0.6 * rnd.random())
        pts.append((x, y))
    d = f"M0,{pts[0][1]:.0f}"
    for (x0, y0_), (x1, y1) in zip(pts, pts[1:]):
        cx = (x0 + x1) / 2
        d += f" C{cx:.0f},{y0_:.0f} {cx:.0f},{y1:.0f} {x1:.0f},{y1:.0f}"
    return d, pts


def landscape(W, H, c, rows=True, trees=True, sun=True, sky=True, peaks_x=1450, ground=None, uid="a", L=(0.86, 0.925, 0.985), A=(0.07, 0.07, 0.05)):
    """Gede–Pangrango twin peaks over rolling tea hills (Puncak). c = dict of colours."""
    s = [f'<svg class="land" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" aria-hidden="true"><defs>'
         f'<linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["sky0"]}"/><stop offset="1" stop-color="{c["sky1"]}"/></linearGradient>'
         f'<linearGradient id="mist{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["sky1"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["sky1"]}" stop-opacity=".85"/></linearGradient></defs>']
    if sky:
        s.append(f'<rect width="{W}" height="{H}" fill="url(#sky{uid})"/>')
    if sun:
        s.append(f'<circle cx="{peaks_x + 230}" cy="{H*0.30:.0f}" r="{H*0.075:.0f}" fill="{c["sun"]}" opacity=".9"/>')
    # Pangrango (left, rounder) and Gede (right, with crater notch)
    px, b = peaks_x, H * 0.84
    top_p, top_g = H * 0.22, H * 0.28
    mtn = (f"M{px-1000},{b} C{px-700},{b-40} {px-420},{top_p+170} {px-230},{top_p+40} "
           f"C{px-170},{top_p} {px-110},{top_p} {px-40},{top_p+50} "
           f"C{px+20},{top_p+95} {px+70},{top_g+40} {px+130},{top_g+8} "
           f"L{px+175},{top_g+32} L{px+215},{top_g} "
           f"C{px+330},{top_g+60} {px+520},{b-150} {px+900},{b-30} L{W},{b} L{W},{H} L{px-1000},{H} Z")
    s.append(f'<path d="{mtn}" fill="{c["far"]}"/>')
    s.append(f'<rect y="{H*0.45:.0f}" width="{W}" height="{H*0.3:.0f}" fill="url(#mist{uid})"/>')
    layers = [(H * L[0], H * A[0], c["h1"], 3, 0.3), (H * L[1], H * A[1], c["h2"], 5, 1.4), (H * L[2], H * A[2], c["h3"], 9, 2.2)]
    for k, (y0, amp, col, seed, ph) in enumerate(layers):
        d, pts = wave(y0, amp, W, n=5 + k, seed=seed, phase=ph)
        s.append(f'<path d="{d} L{W},{H} L0,{H} Z" fill="{col}"/>')
        if rows and k < 2:
            # tea rows: contour lines following the hill
            for j in range(1, 7 if k == 0 else 6):
                dd, _ = wave(y0 + j * (11 + 4 * k), amp * (1 - j * 0.07), W, n=5 + k, seed=seed, phase=ph)
                s.append(f'<path d="{dd}" fill="none" stroke="{c["row"]}" stroke-width="{3 + k}" stroke-linecap="round" opacity="{0.55 - j*0.05:.2f}"/>')
        if trees and k == 1:
            rnd = random.Random(seed + 7)
            for x in [180, 520, 600, 1180, 1690, 1960]:
                # shade trees (albizia) dotted on the tea hills
                y = min(p[1] for p in pts) + 30 + rnd.random() * 40
                for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                    if xa <= x <= xb:
                        t = (x - xa) / (xb - xa); y = ya + (yb - ya) * (3 * t * t - 2 * t * t * t) + 6
                h = 34 + rnd.random() * 22
                s.append(f'<path d="M{x},{y:.0f} L{x},{y-h:.0f}" stroke="{c["tree"]}" stroke-width="4"/>'
                         f'<ellipse cx="{x}" cy="{y-h:.0f}" rx="{30+rnd.random()*14:.0f}" ry="{9+rnd.random()*4:.0f}" fill="{c["tree"]}"/>')
    if ground:
        s.append(f'<rect y="{H-4}" width="{W}" height="4" fill="{ground}"/>')
    s.append("</svg>")
    return "".join(s)


def ridge(W, H, cols, seed=4):
    """thin hill silhouette band used as a section edge"""
    s = [f'<svg class="ridge" viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true">']
    for k, col in enumerate(cols):
        d, _ = wave(H * (0.55 + 0.2 * k), H * (0.45 - 0.1 * k), W, n=6 + k, seed=seed + k, phase=k)
        s.append(f'<path d="{d} L{W},{H} L0,{H} Z" fill="{col}"/>')
    return "".join(s) + "</svg>"


