"""Keep sitemap.xml in step with the publish-time changes: add /open-data/ and
drop the addresses of merged duplicate decisions."""
import datetime
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import BASE, DATA, SITE, read_csv  # noqa: E402

path = SITE / "sitemap.xml"
xml = path.read_text(encoding="utf-8")
today = datetime.date.today().isoformat()
for r in read_csv(DATA / "court-decisions" / "duplicates.csv"):
    xml = re.sub(r"\s*<url><loc>%s/court-decisions/d/%s/</loc>.*?</url>" % (re.escape(BASE), re.escape(r["removed_id"])), "", xml)
added = 0
for url in [f"{BASE}/open-data/"]:
    if f"<loc>{url}</loc>" not in xml:
        xml = xml.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{today}</lastmod></url>\n</urlset>")
        added += 1
path.write_text(xml, encoding="utf-8")
print(f"  sitemap: {xml.count('<url>')} addresses ({added} added)")
