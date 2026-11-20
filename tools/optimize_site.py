"""Make the published site faster on cheap phones and weak networks, and easier to use
with a screen reader. Runs at publish time (see netlify.toml), on the copy Netlify
publishes, so every build script that writes site/ keeps working unchanged.

For each page in site/ (decision pages included):

Speed
* Figtree comes from this site (/assets/fonts/, SIL Open Font License) instead of
  Google Fonts: two fewer connections to open before text can be drawn. It is not
  preloaded, so on a slow line text appears at once in a system font (swap).
* d3 and topojson (Migration Law Atlas) come from /assets/vendor/ instead of the
  jsDelivr CDN, which is slow or blocked on some networks.
* Every local script and stylesheet gets ?v=<content hash>, so phones keep a saved
  copy until the file really changes (see sw.js and the headers in netlify.toml).
* A small service worker (/sw.js) is registered: pages already opened work offline,
  and the Legal Clinic is saved for offline use when someone opens it.
* The web app manifest is linked, so phones offer to install the site as an app
  (see /app/), and /assets/research.js adds "Save this search" and "Add to reading
  list" to the database and decision pages.

Accessibility
* A "Skip to main content" link at the top of every page (Indonesian when the page
  is switched to ID).
* Exactly one <main> landmark per page: added around the content between the
  header and the footer where it was missing; a second <main> becomes a <div>.
* Wide tables that scroll sideways can be reached and scrolled with the keyboard.
* Animations and smooth scrolling are switched off for people who ask their phone
  for reduced motion.

The script is idempotent and prints a short report. Usage:
    python3 tools/optimize_site.py [SITE_DIR]
"""
import hashlib
import os
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "site"
MARK = "<!-- imr-optimized -->"

FONT_FILES = {
    ("normal", "latin"): "figtree-latin.woff2",
    ("normal", "latin-ext"): "figtree-latin-ext.woff2",
    ("italic", "latin"): "figtree-italic-latin.woff2",
    ("italic", "latin-ext"): "figtree-italic-latin-ext.woff2",
}
RANGES = {
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
    "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF",
}


def file_hash(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()[:10]


FONT_V = {k: file_hash(SITE / "assets" / "fonts" / f) for k, f in FONT_FILES.items()}


def font_block():
    faces = []
    for (style, subset), name in FONT_FILES.items():
        weight = "400 700" if style == "normal" else "400 500"
        faces.append(
            "@font-face{font-family:'Figtree';font-style:%s;font-weight:%s;font-display:swap;"
            "src:url(/assets/fonts/%s?v=%s) format('woff2');unicode-range:%s}"
            % (style, weight, name, FONT_V[(style, subset)], RANGES[subset])
        )
    # No preload: on a slow line the text should not wait for the font; the browser fetches
    # it as soon as it lays out the first text, and shows a system font until then (swap).
    return '<style id="imr-fonts">%s</style>' % "".join(faces)


GF_PRECONNECT = re.compile(r'<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\s*')
GF_SHEET = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Figtree[^"]*">')
VENDOR = {
    "https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js": "/assets/vendor/d3-7.8.5.min.js",
    "https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js": "/assets/vendor/topojson-client-3.1.0.min.js",
}
SCRIPT_SRC = re.compile(r'(<script\b[^>]*?\bsrc=")([^"?#]+\.js)(")')
CSS_HREF = re.compile(r'(<link\b[^>]*?\bhref=")([^"?#]+\.css)(")')

# Site icon (tea hills, 2026-11-20): scalable tab icon, install manifest and phone bar colour.
# Pages already link favicon.ico, favicon-32.png and apple-touch-icon.png themselves.
ICON_HEAD = (
    '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'
    '<link rel="manifest" href="/site.webmanifest">'
)
THEME_COLOR = '<meta name="theme-color" content="#1E6B4A">'

HEAD_EXTRA = (
    '<style id="imr-a11y">'
    ".imr-skip{position:absolute;left:8px;top:-80px;z-index:1000;background:#fff;color:#172D24;padding:12px 16px;"
    "border:2px solid #172D24;border-radius:6px;font:600 16px/1.2 'Figtree',system-ui,sans-serif;text-decoration:none}"
    ".imr-skip:focus{top:8px}"
    "#main:focus{outline:none}"
    "[data-imr-scroll]:focus-visible{outline:3px solid #172D24;outline-offset:2px}"
    "@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}"
    "*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}"
    "</style>"
)

# Installable app (see site/manifest.webmanifest and /app/), and the research tools (saved searches, reading list).
APP_HEAD = ('<link rel="manifest" href="/manifest.webmanifest">'
            '<meta name="theme-color" content="#172D24">'
            '<meta name="apple-mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-title" content="IMR">')
RESEARCH = '<script src="/assets/research.js" defer></script>'

SKIP = '<a class="imr-skip" href="#%s" data-noi18n>Skip to main content</a>'

BODY_SCRIPT = """<script>(function(){
var d=document;
/* Skip link in the page's language */
var s=d.querySelector('.imr-skip');function sl(){if(s)s.textContent=d.documentElement.lang==='id'?'Langsung ke isi utama':'Skip to main content';}
sl();try{new MutationObserver(sl).observe(d.documentElement,{attributes:true,attributeFilter:['lang']});}catch(e){}
/* Tables that scroll sideways: reachable and scrollable with the keyboard */
var seen={};
function fix(){d.querySelectorAll('.g-scroll:not([data-imr-scroll]),.st-tw:not([data-imr-scroll])').forEach(function(el){el.setAttribute('data-imr-scroll','');
if(el.querySelector('a[href],button,input,select,textarea,[tabindex]'))return;el.tabIndex=0;
if(!el.hasAttribute('role')){el.setAttribute('role','region');var h=el.previousElementSibling;while(h&&!/^H[2-6]$/.test(h.tagName))h=h.previousElementSibling;
var c=el.querySelector('caption'),l=((c&&c.textContent)||(h&&h.textContent)||'Table').trim().slice(0,120);
seen[l]=(seen[l]||0)+1;el.setAttribute('aria-label',seen[l]>1?l+' ('+seen[l]+')':l);}});}
var t;function later(){clearTimeout(t);t=setTimeout(fix,200);}
fix();try{new MutationObserver(later).observe(d.body,{childList:true,subtree:true});}catch(e){}
/* Offline support: saved pages and the Legal Clinic (see /sw.js) */
if('serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost')&&!/^press\\./.test(location.hostname)){
addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});});}
})();</script>"""

TRACK = {"body", "header", "footer", "main", "div", "section", "article", "nav", "aside", "figure", "form", "ol", "ul", "table"}


class Landmarks(HTMLParser):
    """Finds body-level elements and <main> elements with their offsets in the source."""

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.line_start = [0]
        for m in re.finditer("\n", text):
            self.line_start.append(m.end())
        self.stack = []
        self.elements = []  # dicts: tag, attrs, start, open_end, end_start, end, parent
        self.body_open_end = None
        self.role_main = False

    def off(self):
        line, col = self.getpos()
        return self.line_start[line - 1] + col

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("role") == "main":
            self.role_main = True
        if tag not in TRACK:
            return
        start = self.off()
        open_end = self.text.index(">", start) + 1
        if tag == "body" and self.body_open_end is None:
            self.body_open_end = open_end
        parent = self.stack[-1] if self.stack else None
        el = {"tag": tag, "attrs": a, "start": start, "open_end": open_end, "end_start": None, "end": None, "parent": parent}
        self.stack.append(el)
        self.elements.append(el)

    def handle_startendtag(self, tag, attrs):
        if dict(attrs).get("role") == "main":
            self.role_main = True

    def handle_endtag(self, tag):
        if tag not in TRACK:
            return
        if not any(e["tag"] == tag for e in self.stack):
            return
        while self.stack:
            el = self.stack.pop()
            if el["tag"] == tag:
                el["end_start"] = self.off()
                el["end"] = self.text.index(">", el["end_start"]) + 1
                break


def fix_main(html, report, name):
    p = Landmarks(html)
    try:
        p.feed(html)
        p.close()
    except Exception as e:  # noqa: BLE001 - keep publishing even if one page is odd
        report["main_skipped"].append(f"{name} (parse: {e})")
        return html, None
    if p.role_main:
        return html, None
    mains = [e for e in p.elements if e["tag"] == "main"]
    if len(mains) == 1:
        m = mains[0]
        mid = m["attrs"].get("id")
        if mid:
            return html, mid
        tag_text = html[m["start"]:m["open_end"]]
        new = tag_text.replace("<main", '<main id="main"', 1)
        report["main_id"] += 1
        return html[: m["start"]] + new + html[m["open_end"]:], "main"

    edits = []  # (start, end, replacement)

    def ancestors(e):
        while e["parent"] is not None:
            e = e["parent"]
            yield e

    if len(mains) > 1:
        parents = {id(m["parent"]) for m in mains}
        if len(parents) != 1 or not all(m["end"] for m in mains):
            report["main_skipped"].append(f"{name} (several nested <main>)")
            return html, None
        for m in mains:
            edits.append((m["start"], m["start"] + 5, "<div"))
            edits.append((m["end_start"], m["end"], "</div>"))
        report["main_merged"] += 1

    if p.body_open_end is None:
        report["main_skipped"].append(f"{name} (no <body>)")
        return html, None
    # The site header: the first <header> that is not inside an article, section or main.
    header = next((e for e in p.elements if e["tag"] == "header" and e["end"]
                   and not any(x["tag"] in ("main", "article", "section", "aside") for x in ancestors(e))), None)
    container = header["parent"] if header else next((e for e in p.elements if e["tag"] == "body"), None)
    if mains and container is not mains[0]["parent"]:
        container = mains[0]["parent"]
    if container is None:
        report["main_skipped"].append(f"{name} (no container)")
        return html, None
    kids = [e for e in p.elements if e["parent"] is container]
    if header and header["parent"] is container:
        a = header["end"]
    else:
        lead = [e for e in kids if e["tag"] == "nav" and e["end"] and "imr-bentham" in (e["attrs"].get("class") or "")]
        a = lead[0]["end"] if lead else container["open_end"]
    after = [e for e in kids if e["start"] >= a and (e["tag"] == "footer" or "imr-ridge" in (e["attrs"].get("class") or ""))]
    if after:
        b = after[0]["start"]
    elif container["tag"] == "body" or not container["end_start"]:
        b = html.rfind("</body>")
    else:
        b = container["end_start"]
    if b <= a:
        report["main_skipped"].append(f"{name} (no content between header and footer)")
        return html, None
    edits.append((a, a, '\n<main id="main">'))
    edits.append((b, b, "</main>\n"))
    for s, e, r in sorted(edits, key=lambda x: x[0], reverse=True):
        html = html[:s] + r + html[e:]
    report["main_added"] += 1
    return html, "main"


def stamp(html, page):
    def resolve(ref):
        if ref.startswith(("http:", "https:", "//", "data:")):
            return None
        target = (SITE / ref.lstrip("/")) if ref.startswith("/") else (page.parent / ref)
        try:
            target = target.resolve()
            target.relative_to(SITE)
        except (ValueError, OSError):
            return None
        return target if target.is_file() else None

    cache = {}

    def sub(m):
        ref = m.group(2)
        target = resolve(ref)
        if not target:
            return m.group(0)
        if target not in cache:
            cache[target] = file_hash(target)
        return m.group(1) + ref + "?v=" + cache[target] + m.group(3)

    html = SCRIPT_SRC.sub(sub, html)
    html = CSS_HREF.sub(sub, html)
    return html


def optimize(page, report):
    html = page.read_text(encoding="utf-8")
    if MARK in html or "<head" not in html:
        return False
    name = str(page.relative_to(SITE))

    if GF_SHEET.search(html):
        html = GF_PRECONNECT.sub("", html)
        html = GF_SHEET.sub(font_block(), html, count=1)
        html = GF_SHEET.sub("", html)
        report["fonts"] += 1
    for cdn, local in VENDOR.items():
        if cdn in html:
            html = html.replace(cdn, local)
            report["vendor"] += 1
    if 'rel="manifest"' not in html:
        html = html.replace("</head>", APP_HEAD + "</head>", 1)
    if "/assets/research.js" not in html and not name.startswith("press/") and "</body>" in html:
        html = html.replace("</body>", RESEARCH + "</body>", 1)
    html = stamp(html, page)

    # Landmarks for blocks that sit outside <main>, and a map whose countries can be focused.
    html = html.replace('<section id="imr-research" style=', '<section id="imr-research" role="complementary" aria-label="For researchers" style=', 1)
    html = html.replace('<svg id="map" role="img"', '<svg id="map" role="group"', 1)

    html, main_id = fix_main(html, report, name)
    head_end = html.find("</head>")
    if head_end > 0:
        extra = HEAD_EXTRA
        if "site.webmanifest" not in html:
            extra = ICON_HEAD + extra
        if 'name="theme-color"' not in html:
            extra = THEME_COLOR + extra
        html = html[:head_end] + extra + html[head_end:]
    m = re.search(r"<body\b[^>]*>", html)
    if m and main_id:
        html = html[: m.end()] + SKIP % main_id + html[m.end():]
        report["skip"] += 1
    end = html.rfind("</body>")
    if end > 0:
        html = html[:end] + BODY_SCRIPT + MARK + html[end:]
    page.write_text(html, encoding="utf-8")
    return True


def main():
    report = {"pages": 0, "fonts": 0, "vendor": 0, "skip": 0, "main_id": 0, "main_added": 0, "main_merged": 0, "main_skipped": []}
    for page in sorted(SITE.rglob("*.html")):
        rel = page.relative_to(SITE).parts
        if "data" in rel or page.name in ("offline.html",):
            continue
        if optimize(page, report):
            report["pages"] += 1
    # Each publish gets its own service worker version, so old saved files are dropped.
    sw = SITE / "sw.js"
    if sw.is_file():
        text = sw.read_text(encoding="utf-8")
        build = os.environ.get("COMMIT_REF", "")[:10] or hashlib.sha1(str(sorted((str(p), p.stat().st_mtime) for p in (SITE / "assets").rglob("*"))).encode()).hexdigest()[:10]
        sw.write_text(re.sub(r"var BUILD = '[^']*';", "var BUILD = '%s';" % build, text, count=1), encoding="utf-8")
    skipped = report.pop("main_skipped")
    print("optimize_site:", ", ".join(f"{k}={v}" for k, v in report.items()))
    for s in skipped:
        print("  main landmark not changed:", s)


if __name__ == "__main__":
    main()
