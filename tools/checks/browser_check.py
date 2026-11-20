#!/usr/bin/env python3
"""Open the main pages of a built site in a real browser (Chromium, via Playwright).

For each page, in English and then with the Indonesian switch on, it records:
  * script errors on the page
  * files on the site that fail to load (missing scripts, data files, images)
  * text the page's own scripts write that stays in English when Indonesian is
    chosen (the static check in site_check.py only sees text in the HTML)
and, on a 320 px wide touch phone (the narrowest cheap Android phones):
  * a page wider than the screen, so readers must scroll sideways

    python3 tools/checks/browser_check.py --site site --out browser.json

Court decision pages are all made from one template, so only a few are opened.
IMR Press pages are skipped: on the live site they are served from
press.theimr.org, which a local test server cannot copy.
GoatCounter is blocked so test visits are not counted.
"""
import argparse
import functools
import http.server
import json
import pathlib
import re
import socketserver
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from site_check import i18n_level, looks_indonesian, needs_translation, problem  # noqa: E402

SAMPLE_DECISIONS = 4

# Runs in the page after it has settled. Mirrors the rules in /assets/lang.js.
FIND_ENGLISH = r"""
() => {
  const D = (window.SITE_I18N && window.SITE_I18N.id) || {};
  const pats = (D.__pat || []).map(p => { try { return new RegExp(p[0]); } catch (e) { return null; } }).filter(Boolean);
  const values = new Set(Object.values(D).filter(v => typeof v === 'string'));
  const has = t => t !== '__pat' && Object.prototype.hasOwnProperty.call(D, t);
  const done = t => { if (has(t) || values.has(t)) return true; const m = /^(.+) \((\d+)\)$/.exec(t); if (m && has(m[1])) return true; return pats.some(p => p.test(t)); };
  const clinic = !!document.getElementById('langs');
  const INTERFACE = 'nav, header, footer, button, label, summary, h1, h2, h3, h4, th, option, legend, caption';
  const out = [];
  const visible = el => { const r = el.getClientRects(); return r.length && getComputedStyle(el).visibility !== 'hidden'; };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const el = n.parentElement;
    if (!el || el.closest('script,style,textarea,noscript,template,code,pre,[data-noi18n]')) continue;
    if (clinic && !el.closest('nav, footer, .imr-lang')) continue;
    const langEl = el.closest('[lang]');
    if (langEl && langEl !== document.documentElement && !/^(en|id)/.test(langEl.getAttribute('lang'))) continue;
    if (!visible(el)) continue;
    if (n._s != null && n.nodeValue !== n._s) continue;  // lang.js already translated it
    const t = n.nodeValue.replace(/\s+/g, ' ').trim();
    if (!t || done(t)) continue;
    const a = el.closest('a[href]');
    const isCase = !!(a && a.getAttribute('href').includes('/court-decisions/d/')) || (location.pathname.startsWith('/court-decisions/d/') && !!el.closest('h1'));
    out.push([t, !!el.closest(INTERFACE), isCase]);
  }
  return out;
}
"""


# Width of the page on a phone, and the element that sticks out furthest (not counting
# boxes that scroll or clip on their own).
PHONE_WIDTH = r"""
() => {
  const w = innerWidth, sw = document.documentElement.scrollWidth;
  if (sw <= w + 1) return null;
  const clipped = el => { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { if (getComputedStyle(a).overflowX !== 'visible') return true; } return false; };
  let what = '', far = w;
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
    const r = el.getBoundingClientRect();
    if (r.right > far && !clipped(el)) { far = r.right; what = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '') + ' "' + (el.textContent || '').trim().slice(0, 40) + '"'; }
  }
  return {width: sw, what: what || 'unknown'};
}
"""


def serve(site):
    handler = functools.partial(QuietHandler, directory=str(site))
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def pages_to_open(site):
    out = []
    for path in sorted(site.rglob("*.html")):
        rel = path.relative_to(site).as_posix()
        if rel.startswith("press/") or rel.startswith("court-decisions/d/"):
            continue
        out.append(rel)
    decisions = sorted(p.relative_to(site).as_posix() for p in (site / "court-decisions" / "d").glob("*/index.html"))
    if decisions:
        step = max(1, len(decisions) // SAMPLE_DECISIONS)
        out += decisions[::step][:SAMPLE_DECISIONS]
    return ["/" + (r[: -len("index.html")] if r.endswith("index.html") else r) for r in out]


def run(site, out_path):
    from playwright.sync_api import sync_playwright

    httpd, origin = serve(site)
    problems = []
    english = {}  # text -> [interface, count, where, case]
    urls = pages_to_open(site)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for url in urls:
            for lang in ("en", "id", "phone"):
                if lang == "phone":
                    ctx = browser.new_context(viewport={"width": 320, "height": 640}, is_mobile=True, has_touch=True)
                else:
                    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
                ctx.route(re.compile(r"https?://([^/]*\.)?(zgo\.at|goatcounter\.com)/.*"), lambda r: r.abort())
                page = ctx.new_page()
                errors, missing = [], []
                page.on("pageerror", lambda e: errors.append(str(e).split("\n")[0][:300]))

                def on_response(resp):
                    if resp.url.startswith(origin) and resp.status >= 400:
                        missing.append(resp.url[len(origin):])
                page.on("response", on_response)
                where = f"site{url}" + ("index.html" if url.endswith("/") else "")
                try:
                    page.goto(origin + url + ("?lang=id" if lang == "id" else ""), wait_until="load", timeout=45000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=8000)
                    except Exception:  # noqa: BLE001  (maps keep fetching tiles)
                        pass
                    page.wait_for_timeout(800)
                    if lang == "phone":
                        wide = page.evaluate(PHONE_WIDTH)
                        if wide:
                            problems.append(problem("phone", "error", f"wide|{url}", where,
                                                    f"{url} is {wide['width']} px wide on a 320 px phone, so readers must scroll sideways. Widest part: {wide['what']}"))
                    if lang == "id":
                        for t, inter, case in page.evaluate(FIND_ENGLISH):
                            if not needs_translation(t) or looks_indonesian(t):
                                continue
                            rec = english.setdefault(t, [False, 0, where, 0])
                            rec[0] = rec[0] or inter
                            rec[1] += 1
                            if case or url.startswith(("/court-decisions/d/", "/court-decisions/all/")):
                                rec[3] += 1
                except Exception as e:  # noqa: BLE001
                    problems.append(problem("browser", "error", f"load|{url}", where, f"Page did not load ({lang}): {str(e).splitlines()[0][:200]}"))
                for msg in sorted(set(errors)):
                    norm = re.sub(r"\d+", "N", msg)
                    problems.append(problem("browser", "error", f"jserror|{url}|{norm}", where, f"Script error on {url} ({lang}): {msg}"))
                for m in sorted(set(missing)):
                    problems.append(problem("browser", "error", f"missing|{m}", where, f"{url} asks for {m}, which does not exist."))
                ctx.close()
        browser.close()
    httpd.shutdown()
    for t, (inter, count, where, dec) in sorted(english.items()):
        level = i18n_level(t, inter, count, dec)
        kind = "Menu, heading, button or label text" if inter else "Text"
        # Same key as site_check.py, so text found by both checks is reported once
        problems.append(problem("i18n", level, t[:200], where,
                                f"{kind} shown in English when Indonesian is chosen: \"{t[:120]}\". Add it to site/assets/lang.js or the page's *-i18n.js file, or mark the element data-noi18n if it should stay in English."))
    pathlib.Path(out_path).write_text(json.dumps({"problems": problems, "pages_opened": len(urls)}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Opened {len(urls)} pages in English, in Indonesian and on a 320 px phone; {len(problems)} findings.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default="site")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    run(pathlib.Path(args.site).resolve(), args.out)


if __name__ == "__main__":
    main()
