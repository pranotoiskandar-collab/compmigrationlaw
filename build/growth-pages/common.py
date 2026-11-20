"""Shared helpers for the growth pages (partners, impact, materials, embed).

Every page reuses the header, menu and footer of /ai-use/ so it looks like the rest of the
site, and gets its Indonesian through /assets/lang-growth.js (keyed by the English text,
like /assets/lang.js).
"""
import csv
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DATA = ROOT / "data"

# English -> Indonesian strings for every growth page. Filled by the page builders.
ID = {}


def tr(en, idn):
    """Register an Indonesian translation and return the English text."""
    ID[re.sub(r"\s+", " ", en).strip()] = idn
    return en


def esc(s):
    return html.escape(str(s), quote=True)


def rows(path):
    with open(DATA / path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


CSS = """
<style>
.gp{max-width:1040px;margin:0 auto;padding:0 24px;box-sizing:border-box;font-family:'Figtree',system-ui,sans-serif;color:#172D24}
.gp-hero{padding:72px 0 28px;text-align:center}
.gp-eb{margin:0;font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#1E6B4A;font-weight:600}
.gp-hero h1{margin:14px 0 0;font-weight:500;font-size:clamp(34px,5vw,52px);line-height:1.1}
.gp-hero p{margin:18px auto 0;max-width:720px;color:#2E493D}
.gp-sec{padding:30px 0;border-top:1px solid #B2C7BC;scroll-margin-top:24px}
.gp-sec h2{margin:0 0 8px;font-weight:500;font-size:28px;line-height:1.2}
.gp-sec h3{margin:22px 0 6px;font-size:20px;font-weight:600}
.gp-sec p{margin:10px 0 0}
.gp-num{margin:0 0 6px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#1E6B4A;font-weight:600}
.gp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(260px,100%),1fr));gap:14px;margin-top:16px}
.gp-card{background:#FFFFFF;border:1px solid #B2C7BC;border-radius:6px;padding:16px 18px;font-size:16.5px;line-height:1.5}
.gp-card h3{margin:0 0 6px;font-size:18px}
.gp-card p{margin:0 0 8px}
.gp-card .gp-meta{color:#3D5A4D;font-size:14.5px}
.gp-btn{display:inline-block;margin:4px 8px 4px 0;padding:8px 14px;border-radius:6px;background:#1E6B4A;color:#FFFFFF!important;text-decoration:none;font-weight:600;font-size:15.5px}
.gp-btn:hover{background:#134A33}
.gp-btn.ghost{background:#FFFFFF;color:#1E6B4A!important;border:1px solid #1E6B4A}
.gp-thumb{display:block;width:100%;height:auto;border:1px solid #B2C7BC;border-radius:4px;margin-bottom:10px;background:#EEF4F0}
.gp-stat{background:#FFFFFF;border:1px solid #B2C7BC;border-radius:6px;padding:16px 18px}
.gp-stat b{display:block;font-size:34px;line-height:1.1;font-weight:600;color:#1E6B4A;font-variant-numeric:tabular-nums}
.gp-stat span{display:block;margin-top:6px;font-size:15.5px;line-height:1.4}
.gp-stat small{display:block;margin-top:6px;color:#3D5A4D;font-size:13.5px;line-height:1.4}
.gp-stat.pending b{font-size:20px;color:#8A5A00}
.gp-code{position:relative;margin:10px 0 0}
.gp-code textarea{width:100%;box-sizing:border-box;min-height:92px;font:14px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:10px 12px;border:1px solid #7F9A8C;border-radius:6px;background:#F6FAF7;color:#172D24;resize:vertical}
.gp-copy{font:inherit;font-size:15px;font-weight:600;margin-top:6px;padding:7px 14px;border:0;border-radius:6px;background:#1E6B4A;color:#FFFFFF;cursor:pointer}
.gp-copy:hover{background:#134A33}
.gp-form{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:end;margin-top:12px}
.gp-form label{display:flex;flex-direction:column;font-size:14.5px;color:#3D5A4D;gap:4px}
.gp-form select{font:inherit;font-size:16px;padding:8px 10px;border:1px solid #7F9A8C;border-radius:6px;background:#FFFFFF;color:#172D24}
.gp-frame{width:100%;max-width:420px;height:560px;border:1px solid #B2C7BC;border-radius:6px;background:#FFFFFF;margin-top:14px}
.gp-note{margin-top:14px!important;padding:10px 12px;background:#E5EEE8;border-radius:4px;font-size:15px;color:#2E493D}
.gp-list{margin:10px 0 0;padding-left:22px}
.gp-list li{margin:6px 0}
.gp code{word-break:break-all;font-size:14px}
.gp-tag{display:inline-block;padding:2px 8px;border-radius:999px;background:#F3E6CC;color:#6B4500;font-size:13px;font-weight:600;vertical-align:2px}
.gp-badges{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin-top:14px}
.gp-badges .dark{background:#172D24;padding:12px;border-radius:6px}
@media print{.ed-mast,.imr-bentham,.imr-ridge,footer,.gp-noprint{display:none!important}.gp-sec{break-inside:avoid}}
</style>
"""


def page(slug, title, description, main_html, extra_head="", ld_type="WebPage"):
    """Write site/<slug>/index.html using the /ai-use/ page as the frame."""
    frame = (SITE / "ai-use" / "index.html").read_text(encoding="utf-8")
    url = f"https://theimr.org/{slug}/"
    head_end = frame.index("<style>body{font-variant-numeric")
    head = frame[:head_end]
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)} · Institute for Migrant Rights</title>", head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(description), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(description), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title) + " · Institute for Migrant Rights", head)
    head = head.replace("https://theimr.org/ai-use/", url)
    ld = {"@context": "https://schema.org", "@type": ld_type, "name": title, "url": url, "description": description,
          "inLanguage": ["en", "id"], "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"}}
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", head, flags=re.S)
    rest = frame[head_end:]
    start = rest.index("<main")
    end = rest.index("</main>") + len("</main>")
    body = rest[:start] + f'<main id="{slug.replace("/", "-")}">\n' + main_html + "\n</main>" + rest[end:]
    body = body.replace('<script src="/assets/lang.js" defer></script>',
                        '<script src="/assets/lang-growth.js" defer></script>\n<script src="/assets/lang.js" defer></script>')
    out = SITE / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + CSS + extra_head + body, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


def write_lang():
    """Indonesian dictionary for these pages, loaded just before /assets/lang.js (same pattern as oc-i18n.js):
    the dictionary lang.js assigns to window.SITE_I18N is extended at the moment it is assigned."""
    js = ("/* Indonesian for the partner, impact and materials pages, the embed box and the new footer links.\n"
          "   Built by build/growth-pages/build_pages.py. Loaded just before /assets/lang.js. */\n"
          "(function () {\n  var A = " + json.dumps(ID, ensure_ascii=False, sort_keys=True, indent=0) + ";\n"
          "  function merge(D) { D.id = D.id || {}; for (var k in A) if (!Object.prototype.hasOwnProperty.call(D.id, k)) D.id[k] = A[k]; return D; }\n"
          "  if (window.SITE_I18N) { merge(window.SITE_I18N); return; }\n"
          "  var cur;\n"
          "  try { Object.defineProperty(window, \"SITE_I18N\", {configurable: true, enumerable: true, get: function () { return cur; }, set: function (v) { cur = merge(v || {}); }}); }\n"
          "  catch (e) { window.SITE_I18N = merge({}); }\n"
          "})();\n")
    (SITE / "assets" / "lang-growth.js").write_text(js, encoding="utf-8")
    print("wrote site/assets/lang-growth.js with", len(ID), "strings")
