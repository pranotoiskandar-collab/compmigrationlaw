"""Make sure every published page carries the GoatCounter counter (site "theimr").

Pages added later (new sections, generated pages) get it automatically, so nobody
has to remember to rerun build/analytics-build/analytics.py. No cookies, no
personal data; see /ai-use/ and the privacy note on the Contact page.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import SITE  # noqa: E402

TAG = "<!-- imr-analytics -->"
SNIP = (TAG + '\n<script data-goatcounter="https://theimr.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n'
        '<script src="/assets/imr-events.js" defer></script>\n')
added = 0
for page in SITE.rglob("*.html"):
    if page.relative_to(SITE).parts[0] == "api":
        continue
    html = page.read_text(encoding="utf-8")
    if TAG in html or "goatcounter" in html or "</head>" not in html:
        continue
    page.write_text(html.replace("</head>", SNIP + "</head>", 1), encoding="utf-8")
    added += 1
print(f"  analytics: counter added to {added} pages that lacked it")
