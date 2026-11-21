"""Visible founding year in the site footer, added at publish time.

Search engines had shown 2010; IMR was founded in Cianjur in 2007 (Pranoto,
2026-11-19). Until now the year appeared only in hidden markup, so this adds one
line under "and IMR Press" in every page footer. The Indonesian text comes from
id-extra.json through /assets/lang.js.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import SITE  # noqa: E402

OLD = '<p style="margin: 6px 0 0; color: #BCCFC5">and IMR Press</p>'
NEW = OLD + '<p style="margin: 6px 0 0; color: #BCCFC5">Founded in Cianjur in 2007</p>'

n = 0
for page in SITE.rglob("*.html"):
    html = page.read_text(encoding="utf-8")
    if OLD in html and "Founded in Cianjur in 2007" not in html:
        page.write_text(html.replace(OLD, NEW, 1), encoding="utf-8")
        n += 1
print(f"  footer: founding year on {n} pages")
