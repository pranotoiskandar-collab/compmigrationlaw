"""Add a "Volunteer" link after "People" in the main menu of every page.

Idempotent. Rerun after any rebuild that rewrites the menu:

    python3 build/volunteer-build/nav_link.py site
"""
import pathlib, re, sys

site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site")
pat = re.compile(r'(<a href="[^"]*people\.html"([^>]*)>People</a>)')
changed = 0
for p in site.rglob("*.html"):
    s = p.read_text(encoding="utf-8")
    if 'href="/volunteer/"' in s and ">Volunteer</a>" in s:
        continue
    nav = s.find('aria-label="Main"')
    if nav < 0:
        continue
    end = s.find("</nav>", nav)
    m = pat.search(s, nav, end)
    if not m:
        continue
    link = f'{m.group(1)}\n<a href="/volunteer/"{m.group(2)}>Volunteer</a>'
    s = s[: m.start()] + link + s[m.end():]
    p.write_text(s, encoding="utf-8")
    changed += 1
print(f"Volunteer menu link added to {changed} pages")
