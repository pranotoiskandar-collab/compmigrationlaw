"""Add the new pages to the site menu on every page. Run once AFTER PR #19 (Puncak green) is merged, then commit:
    python3 build/feature-pages/add_nav_links.py
Kept out of the feature PR on purpose: it touches every page, and doing it before #19 merges would collide with
#19's colour changes on the neighbouring menu lines. Idempotent."""
import pathlib
import re

SITE = pathlib.Path(__file__).resolve().parents[2] / "site"
SEC = re.compile(r'(<span style="display:block;padding:12px 16px 2px;font:500 11px \'Figtree\',monospace;letter-spacing:\.12em;text-transform:uppercase;color:#[0-9A-Fa-f]{6}">)Courts</span>')
n = 0
for f in SITE.rglob("*.html"):
    s = f.read_text(encoding="utf-8")
    if "/ratifications/" in s and "Case of the month" in s:
        continue
    t = s.replace('<a href="/legal-help/">Find free legal help</a>\n',
                  '<a href="/legal-help/">Find free legal help</a>\n<a href="/rights-checklist/">Know your rights before you go</a>\n', 1)
    m = SEC.search(t)
    if m:
        t = t.replace('<a href="/court-decisions/">Court Decisions</a>\n',
                      '<a href="/court-decisions/">Court Decisions</a>\n<a href="/court-decisions/highlights/" style="padding-left:28px">Case of the month</a>\n'
                      + m.group(1) + 'Tools</span>\n<a href="/ratifications/">Ratification tracker</a>\n<a href="/research/">Saved searches and reading list</a>\n', 1)
    if t != s:
        f.write_text(t, encoding="utf-8")
        n += 1
print("menu updated on %d pages" % n)
