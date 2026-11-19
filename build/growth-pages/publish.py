"""Publish-time step for the growth pages (run by netlify.toml after tools/copy_data.py).

1. Rebuild the Ask IMR index from data/ so it always matches the published data.
2. Add "Materials · Partner badge · Our impact" next to "How we use AI" in every page footer.
3. Make sure the new pages are in sitemap.xml and llms.txt.
The HTML files in the repository are not changed by this step; only the published copy is.
Usage from the repository root: python3 build/growth-pages/publish.py [site]
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site"

subprocess.run([sys.executable, str(ROOT / "build" / "growth-pages" / "build_ask_index.py")], check=True)

OLD = '<a href="/ai-use/" style="color: #FFFFFF">How we use AI</a>'
NEW = (OLD + ' · <a href="/materials/" style="color: #FFFFFF">Materials</a>'
       ' · <a href="/partners/" style="color: #FFFFFF">Partner badge</a>'
       ' · <a href="/impact/" style="color: #FFFFFF">Our impact</a>')
# Link the data-quality page (another pull request) only once it is published.
HAS_DQ = (SITE / "data-quality" / "index.html").exists()
DQ = ' · <a href="/data-quality/" style="color: #FFFFFF">How we check our data</a>'
changed = 0
for f in SITE.rglob("*.html"):
    text = f.read_text(encoding="utf-8")
    if OLD in text and 'href="/partners/" style="color: #FFFFFF"' not in text:
        text = text.replace(OLD, NEW + (DQ if HAS_DQ and 'href="/data-quality/"' not in text else ""), 1)
        if HAS_DQ:
            text = text.replace("<!-- data-quality-link -->", '<li><a href="/data-quality/">How we find, code and check the data</a></li>')
        # Indonesian for the three new footer words
        lang = '<script src="/assets/lang.js" defer></script>'
        if lang in text and "/assets/lang-growth.js" not in text:
            text = text.replace(lang, lang + '\n<script src="/assets/lang-growth.js" defer></script>', 1)
        f.write_text(text, encoding="utf-8")
        changed += 1
print(f"footer links added to {changed} pages")

PAGES = ["materials/", "partners/", "impact/"]
sm = SITE / "sitemap.xml"
if sm.exists():
    xml = sm.read_text(encoding="utf-8")
    add = "".join(f"<url><loc>https://theimr.org/{p}</loc></url>\n" for p in PAGES if f"https://theimr.org/{p}<" not in xml)
    if add:
        sm.write_text(xml.replace("</urlset>", add + "</urlset>"), encoding="utf-8")
llms = SITE / "llms.txt"
if llms.exists() and "theimr.org/partners/" not in llms.read_text(encoding="utf-8"):
    with llms.open("a", encoding="utf-8") as f:
        f.write("\n## Reuse and impact\n"
                "- [Partner badge and country box](https://theimr.org/partners/): show IMR data on your site; terms of reuse (CC BY 4.0, credit with the badge)\n"
                "- [Materials](https://theimr.org/materials/): flyers, country sheets, volunteer briefs and teaching packs to download\n"
                "- [Impact](https://theimr.org/impact/): what IMR has built and who uses it\n")
print("sitemap and llms.txt checked")
