"""Help browser reading modes (Safari Reader, Chrome and Edge reading view) find each page's text.

Reading modes look for an <article> holding the main text. Most pages had only <main>, and the
lists are filled in by script, so Safari often offered no Reader button. This step wraps the
contents of <main> in <article> on every page that has no <article> yet. Pages look the same:
<article> has no default styling. Safe to run more than once.
"""
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import SITE  # noqa: E402

OPEN = re.compile(r"(<main\b[^>]*>)", re.I)
changed = 0
for f in SITE.rglob("*.html"):
    s = f.read_text(encoding="utf-8")
    if "<article" in s or s.count("<main") != 1 or "</main>" not in s:
        continue
    s2 = OPEN.sub(r'\1<article style="display:contents">', s, count=1)
    s2 = s2.replace("</main>", "</article></main>", 1)
    f.write_text(s2, encoding="utf-8")
    changed += 1
print(f"  reading mode: <article> added on {changed} pages")
