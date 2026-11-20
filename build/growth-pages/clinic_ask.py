"""Put the Ask IMR (Tanya IMR) box on the Legal Clinic page, right after "Where are you now?".

Idempotent: running it again changes nothing. Rerun after any rebuild of legal-clinic/index.html.
Usage from the repository root: python3 build/growth-pages/clinic_ask.py site
"""
import pathlib
import sys

SITE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site")
page = SITE / "legal-clinic" / "index.html"
html = page.read_text(encoding="utf-8")

BLOCK = ('<!-- ask-imr -->\n<section id="ask-imr" data-noi18n aria-labelledby="ai-h2"><noscript><p>Ask IMR needs JavaScript. '
         'You can still <a href="/legal-help/">find free legal help</a> or browse the <a href="/databases/">databases</a>.</p></noscript></section>\n'
         '<script src="/assets/ask-imr.js" defer></script>\n<!-- /ask-imr -->\n')
CSS = '<link rel="stylesheet" href="/assets/ask-imr.css">\n'

if "<!-- ask-imr -->" in html:
    print("Ask IMR already on the Clinic page")
    sys.exit(0)
anchor = html.find('<section id="lc-journey"')
if anchor < 0:
    sys.exit("Could not find the journey section on the Clinic page")
end = html.find("</script>", html.find("</section>", anchor)) + len("</script>")
html = html[:end] + "\n" + BLOCK + html[end:]
html = html.replace("</head>", CSS + "</head>", 1)
page.write_text(html, encoding="utf-8")
print("Added Ask IMR to", page)
