"""Make a new page in the site's current look by reusing a decision page as the frame."""
import html as H
import re

from common import SITE

FRAME = SITE / "court-decisions" / "d" / "mk-127-2023" / "index.html"


def frame():
    path = FRAME if FRAME.exists() else next((SITE / "court-decisions" / "d").glob("*/index.html"))
    return path.read_text(encoding="utf-8")


def make_page(path, url, title, description, body, ld=None, extra_head=""):
    """Write site/<path>/index.html with the shared header, banner and footer."""
    page = frame()
    esc = H.escape
    page = re.sub(r"<title>.*?</title>", f"<title>{esc(title)} · Institute for Migrant Rights</title>", page, count=1, flags=re.S)
    page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(description)}">', page, count=1)
    page = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(description)}">', page, count=1)
    page = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', page, count=1)
    page = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', page, count=1)
    page = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', page, count=1)
    page = re.sub(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="website">', page, count=1)
    page = re.sub(r'<meta name="(keywords|citation_[a-z_]+)" content="[^"]*">\n?', "", page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", page, flags=re.S)
    if ld:
        import json
        extra_head = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n' + extra_head
    page = page.replace("</head>", extra_head + "</head>", 1)
    page = page.replace(' aria-current="page"', "")
    page = re.sub(r"(<main\b[^>]*?)\s+id=\"[^\"]*\"", r"\1", page, count=1)
    page = re.sub(r"<main\b[^>]*>.*?</main>",
                  '<main id="main" style="padding: 48px 0 72px"><div class="g-wrap" style="max-width:920px;margin:0 auto;padding:0 24px">'
                  + body + "</div></main>", page, 1, flags=re.S)
    page = re.sub(r'<section id="imr-research".*?</section>\n?', "", page, count=1, flags=re.S)
    page = re.sub(r'<script type="application/json" id="imr-i18n-page">.*?</script>\n?', "", page, flags=re.S)
    out = SITE / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out
