"""Serve the IMR Press pages at press.theimr.org.

The pages stay in site/press/ in this repository, so every existing build
script keeps working on them. At publish time (see netlify.toml) this script
adjusts the published copy:

* Pages in site/press/: links to other press pages become /<book>/ (the root
  of press.theimr.org), and every other root-relative link, image, stylesheet
  and script points to https://theimr.org/... so it still loads on the
  subdomain. Canonical and social links name press.theimr.org.
* Every other page: links to /press/... point to https://press.theimr.org/...
  so visitors skip the redirect.
* sitemap.xml and llms.txt list the press pages under press.theimr.org; the
  press pages get their own sitemap.xml and robots.txt.
* GoatCounter keeps counting press pages under /press/... as before.
* A visitor's language choice (EN/ID) is carried across the two addresses.

site/_redirects (top rules) serves press.theimr.org/* from /press/* and sends
theimr.org/press/* there with a 301.

Safe to run more than once.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PRESS = SITE / "press"
MAIN = "https://theimr.org"
SUB = "https://press.theimr.org"

ATTR = re.compile(r'(\s(?:href|src|action|poster|content|data-src)=")(/(?!/)[^"]*)"')
SRCSET = re.compile(r'(\ssrcset=")([^"]*)"')
CSSURL = re.compile(r"url\((['\"]?)(/(?!/)[^)'\"]*)\1\)")

MARK = "<!-- press-subdomain -->"
LANG_CARRY = (
    "<script>(function(){document.addEventListener('click',function(e){"
    "var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;"
    "var h=a.hostname;if(h===location.hostname||!/(^|\\.)theimr\\.org$/.test(h))return;"
    "var l;try{l=localStorage.getItem('imr-lang')}catch(x){}"
    "if(l&&l!=='en'){var u=new URL(a.href);u.searchParams.set('lang',l);a.href=u.href}},true)})();</script>"
)
GOAT_PREFIX = (
    "<script>if(location.hostname==='press.theimr.org')"
    "window.goatcounter={path:function(p){return '/press'+p}};</script>"
)


def press_path(path):
    """Map a root-relative path for use on a press page."""
    if path == "/press" or path.startswith("/press/") or path.startswith("/press?") or path.startswith("/press#"):
        return path[len("/press"):] or "/"
    return MAIN + path


def fix_press_page(html):
    if MARK in html:  # already adjusted in this publish
        return html
    html = html.replace(MAIN + "/press/", SUB + "/").replace(MAIN + "/press\"", SUB + "/\"")
    html = ATTR.sub(lambda m: m.group(1) + press_path(m.group(2)) + '"', html)
    html = SRCSET.sub(lambda m: m.group(1) + re.sub(r"(^|,\s*)(/(?!/)\S+)", lambda n: n.group(1) + press_path(n.group(2)), m.group(2)) + '"', html)
    html = CSSURL.sub(lambda m: "url(" + m.group(1) + press_path(m.group(2)) + m.group(1) + ")", html)
    if MARK not in html:
        html = html.replace("<script data-goatcounter=", MARK + GOAT_PREFIX + LANG_CARRY + "<script data-goatcounter=", 1)
        if MARK not in html:
            html = html.replace("</body>", MARK + LANG_CARRY + "</body>", 1)
    return html


def fix_main_page(html):
    html = re.sub(r'(=")/press/', r'\1' + SUB + "/", html)
    html = html.replace(MAIN + "/press/", SUB + "/")
    if MARK not in html and SUB in html:
        html = html.replace("</body>", MARK + LANG_CARRY + "</body>", 1)
    return html


def main():
    if not PRESS.is_dir():
        print("press_subdomain: no site/press/, nothing to do")
        return
    pages = 0
    press_urls = []
    for page in sorted(SITE.rglob("*.html")):
        rel = page.relative_to(SITE)
        html = page.read_text(encoding="utf-8")
        if rel.parts[0] == "press":
            new = fix_press_page(html)
            sub_path = "/" + "/".join(rel.parts[1:-1])
            press_urls.append(SUB + (sub_path.rstrip("/") + "/" if sub_path != "/" else "/"))
        else:
            new = fix_main_page(html)
        if new != html:
            page.write_text(new, encoding="utf-8")
            pages += 1

    sitemap = SITE / "sitemap.xml"
    if sitemap.exists():
        text = sitemap.read_text(encoding="utf-8")
        text = re.sub(r"\s*<url><loc>https://theimr\.org/press/[^<]*</loc>.*?</url>", "", text)
        sitemap.write_text(text, encoding="utf-8")
    llms = SITE / "llms.txt"
    if llms.exists():
        llms.write_text(llms.read_text(encoding="utf-8").replace(MAIN + "/press/", SUB + "/"), encoding="utf-8")

    urls = "\n".join("  <url><loc>%s</loc></url>" % u for u in press_urls)
    (PRESS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n",
        encoding="utf-8")
    (PRESS / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SUB, encoding="utf-8")
    for icon in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
        if (SITE / icon).exists():
            shutil.copy2(SITE / icon, PRESS / icon)
    print("press_subdomain: %d pages adjusted, %d press pages in press sitemap" % (pages, len(press_urls)))


if __name__ == "__main__":
    main()
