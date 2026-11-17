# Adds /hate-speech-voting/ to a site root: copies the page folder, patches the comparison menu, lang.js and sitemap.
import re, os, sys, glob, shutil
root, new = sys.argv[1], sys.argv[2]
dst = os.path.join(root, "hate-speech-voting")
if os.path.abspath(new) != os.path.abspath(dst):
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(new, dst)
pat = re.compile(r'(<a href="/countries-of-origin/"(?: aria-current="page")?>Countries of Origin</a>)(?!\s*<a href="/hate-speech-voting/")')
n = 0
for f in glob.glob(root + "/**/*.html", recursive=True):
    if "/hate-speech-voting/" in f: continue
    s = open(f).read(); t = pat.sub(r'\1\n<a href="/hate-speech-voting/">Hate Speech and Voting</a>', s)
    if t != s: open(f, "w").write(t); n += 1
print("nav patched", n)
lj = os.path.join(root, "assets/lang.js"); s = open(lj).read()
if '"Hate Speech and Voting"' not in s:
    s = s.replace('"Countries of Origin":"Negara Asal"', '"Countries of Origin":"Negara Asal","Hate Speech and Voting":"Ucapan Kebencian dan Pemilu"', 1); open(lj, "w").write(s)
print("lang", '"Hate Speech and Voting"' in s)
sm = os.path.join(root, "sitemap.xml"); s = open(sm).read()
if "hate-speech-voting" not in s:
    s = s.replace("</urlset>", "  <url><loc>https://theimr.org/hate-speech-voting/</loc><lastmod>2026-10-31</lastmod></url>\n</urlset>"); open(sm, "w").write(s)
print("sitemap", "hate-speech-voting" in s)
# Remove duplicate links inside each dropdown menu (keeps the first; the aria-current copy wins).
def _dedupe(m):
    links = re.findall(r'<a href="([^"]+)"[^>]*>[^<]*</a>', m.group(0)); seen, out = set(), []
    for a in re.findall(r'<a href="[^"]+"[^>]*>[^<]*</a>', m.group(0)):
        href = re.search(r'href="([^"]+)"', a).group(1)
        if href in seen: continue
        seen.add(href)
        cur = [b for b in re.findall(r'<a href="' + re.escape(href) + r'" aria-current="page">[^<]*</a>', m.group(0))]
        out.append(cur[0] if cur else a)
    return '<div class="menu">\n' + "\n".join(out) + "\n</div>"
d = 0
for f in glob.glob(root + "/**/*.html", recursive=True):
    s = open(f).read(); t = re.sub(r'<div class="menu">\s*(?:<a [^>]*>[^<]*</a>\s*)+</div>', _dedupe, s)
    if t != s: open(f, "w").write(t); d += 1
print("menus deduped in", d, "files")
