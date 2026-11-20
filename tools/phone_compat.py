"""Make every published page read and work on cheap Android phones and older browsers.

Runs at publish time (see netlify.toml), after optimize_site.py, on the copy Netlify
publishes. Nothing in site/ is changed, so build scripts need no rerun step.

Who this is for: low-cost phones sold in Indonesia and other countries of origin
(Xiaomi Redmi, Oppo, Vivo, Realme, Infinix, Tecno, itel ...), often 320-360 px wide,
with little memory and slow mobile data, and browsers that lag behind current Chrome:
UC Browser and Mi Browser (older Chromium engines), Opera Mini, Android WebView in
the Facebook and Instagram apps, KaiOS.

For each page:

Layout
* Long words, links, case numbers and DOIs wrap instead of pushing the page sideways.
* Pictures, videos and form fields never grow wider than the screen.
* A table that is wider than the screen and is not already in a scrolling box is put
  in one (scrolls sideways on its own, reachable with the keyboard).

Touch
* The "Save this search" bar of the database pages sits under the page title on phones
  instead of floating over the bottom of the text.
* On touch screens, buttons, menus, check boxes and links in lists and tables get a
  larger touch area (WCAG 2.2 target size: at least 24 x 24 px).

Older browsers
* min(), max() and clamp() (Chrome 79+) get a plain fallback value just before them,
  so grids fall back to one column and headings to their smallest size, instead of
  the rule being dropped.
* :has() (Chrome 105+) rules, used to show which answer is picked in the Legal Clinic,
  get a class-based twin; a small script sets the classes where :has() is missing.
* Pages whose tables and charts are drawn by JavaScript show a short notice when
  JavaScript is off (Opera Mini data saving, some in-app browsers), in English and
  Indonesian, with a link to the open data downloads.

Idempotent. Usage:
    python3 tools/phone_compat.py [SITE_DIR]
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "site"
MARK = "<!-- imr-phone -->"

PHONE_CSS = (
    '<style id="imr-phone">'
    "html{-webkit-text-size-adjust:100%;text-size-adjust:100%}"
    "p,li,dd,dt,blockquote,figcaption,h1,h2,h3,h4,h5,h6,label,legend,summary,caption,address,cite{overflow-wrap:break-word;word-wrap:break-word}"
    "@supports (overflow-wrap:anywhere){p,li,dd,blockquote,figcaption,legend,address,code{overflow-wrap:anywhere}"
    "td p,th p,td li,th li{overflow-wrap:break-word}}"
    "pre{white-space:pre-wrap;overflow-x:auto}"
    "img,video,canvas,iframe,input,select,textarea{max-width:100%}"
    "img[width][height]{height:auto}"
    ".imr-tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}"
    ".imr-tscroll:focus-visible{outline:3px solid #172D24;outline-offset:2px}"
    "@media (pointer:coarse),(max-width:720px){"
    "button,select,summary,[role=button],input[type=submit],input[type=button],input[type=reset]{min-height:32px}"
    "input[type=checkbox],input[type=radio]{width:20px;height:20px}"
    "input[type=range]{min-height:32px}"
    "li>a,td a,th a,dd a,dt a,h3>a,nav a,footer a,.imr-report-foot a,.imr-research a,p.sp-lang a,p.g-note a,"
    ".ww-ds a,.g-toc a,.ft-small a,.ft-note a,.shead a,.eyebrow a,p>a:only-child,.toplist button,th button{padding-top:4px;padding-bottom:4px}"
    ".g-cell,.imr-rep-btn{padding-top:4px!important;padding-bottom:4px!important}"
    "}"
    "</style>"
)

PHONE_JS = """<script>(function(){
var d=document;
/* Wide tables that are not in a scrolling box: put them in one */
function wrap(){var ts=d.getElementsByTagName('table');for(var i=0;i<ts.length;i++){var t=ts[i];if(t.getAttribute('data-imr-tw'))continue;
var p=t.parentNode;if(!p||!p.clientWidth||t.offsetWidth<=p.clientWidth+1)continue;var a=t.parentElement,sc=false;
while(a&&a!==d.body){var o=getComputedStyle(a).overflowX;if(o==='auto'||o==='scroll'||o==='hidden'){sc=true;break;}a=a.parentElement;}
t.setAttribute('data-imr-tw','1');if(sc)continue;var w=d.createElement('div');w.className='imr-tscroll';w.tabIndex=0;w.setAttribute('role','region');
var c=t.querySelector('caption');w.setAttribute('aria-label',((c&&c.textContent)||'Table').trim().slice(0,120));p.insertBefore(w,t);w.appendChild(t);}}
var tw;function later(){clearTimeout(tw);tw=setTimeout(wrap,300);}
wrap();addEventListener('load',wrap);addEventListener('resize',later);
try{new MutationObserver(later).observe(d.body,{childList:true,subtree:true});}catch(e){}
/* "Save this search" bar (research.js): on a small screen it would cover the text at the bottom
   all the time, so it goes under the page title instead */
function bar(){if(innerWidth>=720)return;var b=d.querySelector('body>div.imr-research');var h=d.querySelector('main h1');
if(!b||!h||b.style.position!=='fixed')return;b.style.position='static';b.style.boxShadow='none';b.style.margin='12px 0 0';b.style.display='inline-block';h.insertAdjacentElement('afterend',b);}
bar();addEventListener('load',function(){setTimeout(bar,0);});
/* Browsers without :has() (Chrome before 105, UC Browser, Mi Browser, Opera Mini ...) */
var H=window.IMR_HAS;var ok=false;try{ok=CSS.supports('selector(:has(*))');}catch(e){}
if(H&&!ok){function q(el,s){try{return el.querySelector(s);}catch(e){try{return el.querySelector(s.replace(/:focus-visible/g,':focus'));}catch(e2){return null;}}}
function mark(){for(var i=0;i<H.length;i++){var els;try{els=d.querySelectorAll(H[i][0]);}catch(e){continue;}
for(var j=0;j<els.length;j++){var on=!!q(els[j],H[i][1]);if(els[j].classList.contains(H[i][2])!==on)els[j].classList.toggle(H[i][2]);}}}
mark();['change','click','input','focusin','focusout','keyup'].forEach(function(ev){d.addEventListener(ev,function(){setTimeout(mark,0);},true);});
try{new MutationObserver(function(){clearTimeout(H.t);H.t=setTimeout(mark,100);}).observe(d.body,{childList:true,subtree:true});}catch(e){}}
})();</script>"""

NOSCRIPT = (
    '<noscript><div data-noi18n style="margin:12px 16px;padding:12px 14px;border:2px solid #1E6B4A;border-radius:8px;'
    'background:#E5EEE8;color:#172D24;font:16px/1.5 Figtree,system-ui,sans-serif">'
    '<p style="margin:0 0 6px">This page draws its tables and charts with JavaScript, which is switched off in this browser '
    '(for example in Opera Mini data saving mode). Switch JavaScript on, or download the same data from '
    '<a href="/open-data/">Open data</a>.</p>'
    '<p style="margin:0" lang="id">Halaman ini menyusun tabel dan grafiknya dengan JavaScript, yang dimatikan di peramban ini '
    '(misalnya dalam mode hemat data Opera Mini). Aktifkan JavaScript, atau unduh data yang sama melalui '
    '<a href="/open-data/">Data terbuka</a>.</p></div></noscript>'
)

# Pages whose main content is built in the browser (measured 2026-11-20: under 40% of
# the text is there without JavaScript), plus any page that loads its own *-data.js.
JS_PAGES = (
    "compare/", "countries-of-origin/", "court-decisions/index.html", "coverage/", "domestic-workers/",
    "east-asia/", "embed/", "follow/", "gcc/", "laws/", "legal-help/", "ratifications/",
    "southeast-asia/", "timeline/", "migration-law/", "government-hate-speech/", "research/",
)
DATA_SCRIPT = re.compile(r'<script\b[^>]*\bsrc="[^"]*-data\.js[?"]')


# ---------------------------------------------------------------- CSS fallbacks

def split_args(s):
    """Split the inside of a CSS function call on top-level commas."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return out


FUNC = re.compile(r"(?<![\w-])(min|max|clamp)\(")


def plain(value):
    """Replace min()/max()/clamp() with one of their arguments, for browsers without them.
    clamp(a, b, c) -> a (the small value suits a phone); min(a, b) -> the % argument if any
    (min(240px,100%) -> 100%: one column), else the first; max(a, env(...)) -> a."""
    for _ in range(20):
        m = FUNC.search(value)
        if not m:
            return value
        start, i, depth = m.start(), m.end(), 1
        while i < len(value) and depth:
            depth += {"(": 1, ")": -1}.get(value[i], 0)
            i += 1
        if depth:
            return None
        args = split_args(value[m.end():i - 1])
        name = m.group(1)
        if name == "clamp" and len(args) == 3:
            pick = args[0]
        elif name == "min":
            pick = next((a for a in args if "%" in a), args[0])
        else:
            pick = next((a for a in args if "env(" not in a and "var(" not in a), args[0])
        value = value[:start] + pick + value[i:]
    return None


DECL = re.compile(r"(?P<pre>[{;\s])(?P<prop>-?[a-zA-Z][\w-]*)\s*:\s*(?P<val>[^;{}]*?(?<![\w-])(?:min|max|clamp)\([^;{}]*?)(?=\s*(?:;|}|$))")


def css_fallbacks(css):
    def sub(m):
        val = m.group("val")
        imp = ""
        if val.rstrip().endswith("!important"):
            imp = "!important"
            val = val.rstrip()[: -len("!important")].rstrip()
        fb = plain(val)
        if not fb or fb == val or "env(" in fb:
            return m.group(0)
        return "%s%s:%s%s;%s:%s%s" % (m.group("pre"), m.group("prop"), fb, imp, m.group("prop"), val, imp)
    return DECL.sub(sub, css)


STYLE_BLOCK = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.S)
STYLE_ATTR = re.compile(r'(\sstyle=")([^"]*)(")')


# ---------------------------------------------------------------- :has() twins

HAS_RULE = re.compile(r"([^{}@]*:has\([^{}]*)\{([^{}]*)\}")
HAS_SEL = re.compile(r"([^\s>+~,]*?):has\(([^()]*(?:\([^()]*\)[^()]*)*)\)")


def has_twins(css, pairs):
    """For every rule using A:has(B), add the same rule with A.imr-has-N; record (A, B, class)."""
    extra = []
    for m in HAS_RULE.finditer(css):
        selectors = m.group(1).strip()
        twin = selectors
        for s in HAS_SEL.finditer(selectors):
            subject = s.group(1) or "*"
            inner = s.group(2).strip()
            cls = "imr-has-" + hashlib.sha1((subject + "|" + inner).encode()).hexdigest()[:6]
            pairs[cls] = (subject, inner, cls)
            twin = twin.replace(s.group(0), (s.group(1) or "") + "." + cls, 1)
        if ":has(" not in twin:
            extra.append(twin + "{" + m.group(2) + "}")
    return extra


# ---------------------------------------------------------------- pages

def fix(page):
    html = page.read_text(encoding="utf-8")
    if MARK in html or "<head" not in html:
        return None
    name = page.relative_to(SITE).as_posix()
    stats = {"fallbacks": 0, "has": 0, "noscript": 0}

    pairs = {}
    twins = []

    def style_block(m):
        css = m.group(2)
        new = css_fallbacks(css)
        if ":has(" in new:
            twins.extend(has_twins(new, pairs))
        if new != css:
            stats["fallbacks"] += 1
        return m.group(1) + new + m.group(3)

    html = STYLE_BLOCK.sub(style_block, html)

    def style_attr(m):
        new = css_fallbacks(";" + m.group(2))[1:]
        if new != m.group(2):
            stats["fallbacks"] += 1
        return m.group(1) + new + m.group(3)

    html = STYLE_ATTR.sub(style_attr, html)

    head_add = PHONE_CSS
    body_add = ""
    if twins:
        head_add += '<style id="imr-has">' + "".join(twins) + "</style>"
        body_add += "<script>window.IMR_HAS=%s;</script>" % (
            "[" + ",".join('["%s","%s","%s"]' % tuple(x.replace("\\", "\\\\").replace('"', '\\"') for x in p) for p in pairs.values()) + "]")
        stats["has"] = len(twins)
    body_add += PHONE_JS

    h = html.find("</head>")
    html = html[:h] + head_add + html[h:]

    if (name.startswith(JS_PAGES) or DATA_SCRIPT.search(html)) and "imr-noscript" not in html:
        ns = NOSCRIPT.replace("<noscript>", '<noscript class="imr-noscript">', 1)
        m = re.search(r"<main\b[^>]*>", html) or re.search(r"<body\b[^>]*>", html)
        if m:
            html = html[: m.end()] + ns + html[m.end():]
            stats["noscript"] = 1

    b = html.rfind("</body>")
    if b > 0:
        html = html[:b] + body_add + MARK + html[b:]
    page.write_text(html, encoding="utf-8")
    return stats


def fix_css_files(report):
    for css in SITE.rglob("*.css"):
        if "vendor" in css.parts or "leaflet" in css.parts:
            continue
        text = css.read_text(encoding="utf-8")
        if "imr-phone fallbacks" in text:
            continue
        new = css_fallbacks(text)
        if new != text:
            css.write_text("/* imr-phone fallbacks */\n" + new, encoding="utf-8")
            report["css_files"] += 1


def main():
    report = {"pages": 0, "fallbacks": 0, "has_rules": 0, "noscript": 0, "css_files": 0}
    for page in sorted(SITE.rglob("*.html")):
        if "data" in page.relative_to(SITE).parts:
            continue
        s = fix(page)
        if s is None:
            continue
        report["pages"] += 1
        report["fallbacks"] += s["fallbacks"]
        report["has_rules"] += s["has"]
        report["noscript"] += s["noscript"]
    fix_css_files(report)
    print("phone_compat:", ", ".join("%s=%s" % kv for kv in report.items()))


if __name__ == "__main__":
    main()
