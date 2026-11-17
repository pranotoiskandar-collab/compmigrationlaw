# Re-tints the old KITLV banner photos to the Soga palette (sepia duotone). Usage: python3 retint.py SITE
import os, sys
from PIL import Image, ImageOps
SITE = sys.argv[1]; D = os.path.join(SITE, 'images', 'cianjur-old')
for f in sorted(os.listdir(D)):
    if not f.endswith('.jpg'): continue
    p = os.path.join(D, f); im = Image.open(p).convert('L')
    im = ImageOps.autocontrast(im, cutoff=1)
    out = ImageOps.colorize(im, black='#2E2116', white='#F4ECDD', mid='#8C7258')
    out.save(p, quality=86, optimize=True, progressive=True); print('re-tinted', f)
