#!/usr/bin/env python3
"""Weekly source watch: look for new court decisions, laws and ratifications on
official sites, and list them for an editor.

    python3 tools/watch/watch.py              # run every source, update source-watch/
    python3 tools/watch/watch.py --dry-run    # try every source, change nothing
    python3 tools/watch/watch.py --only sg-elitigation-fmw

The sources are in source-watch/sources.json (see source-watch/README.md).
For each source the script reads one listing page, feed or search result (no
judgment texts are downloaded), picks out the items, and compares them with
what it saw before (source-watch/state/<source>.txt) and with every link
already in data/. New items that match the source's keywords go into
source-watch/found/new-<date>.csv for an editor to read and confirm.

The first time a source is read, everything on it is recorded as seen and
nothing is reported, so the list only ever shows what appeared since.

Sources the script cannot read (bot checks, logins, sites that refuse
automated visits, captchas) are listed in the report as work for a person.
It never tries to get round a bot check or captcha.
"""
import argparse
import csv
import datetime
import html
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
WATCH = ROOT / "source-watch"
UA = "Mozilla/5.0 (compatible; IMR-source-watch/1.0; +https://theimr.org/ai-use/)"
PAUSE = 4  # seconds between requests to the same host
FOUND_COLS = ["found_on", "source", "country", "kind", "body", "title", "date", "official_link",
              "matched_terms", "site_status", "note"]

_last_hit = {}


def fetch(url, data=None, timeout=60):
    host = urllib.parse.urlsplit(url).hostname
    wait = PAUSE - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en,*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(8_000_000)
            charset = r.headers.get_content_charset() or "utf-8"
            return r.status, r.geturl(), body.decode(charset, errors="replace")
    finally:
        _last_hit[host] = time.time()


def blocked(text):
    """Recognise bot checks and captchas, which only a person should get past."""
    t = text[:20000].lower()
    signs = ["cf-browser-verification", "challenge-platform", "just a moment...", "attention required! | cloudflare",
             "captcha", "incapsula", "_incapsula_resource", "access denied", "request unsuccessful",
             "please enable javascript and cookies", "ddos protection by"]
    return next((s for s in signs if s in t), None)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items, self._a, self._text, self.rows, self._tr = [], None, [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self._a, self._text = a["href"], []
        if tag == "tr":
            self._tr = []

    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None:
            self.items.append((self._a, " ".join("".join(self._text).split())))
            self._a = None
        if tag == "tr" and self._tr is not None:
            self.rows.append(" ".join(" ".join(self._tr).split()))
            self._tr = None

    def handle_data(self, data):
        if self._a is not None:
            self._text.append(data)
        if self._tr is not None:
            self._tr.append(data)


def dig(obj, path):
    for part in [p for p in (path or "").split(".") if p]:
        obj = obj.get(part, []) if isinstance(obj, dict) else []
    return obj


def expand(url):
    """Fill {year}, {month} (Jan..Dec), {mm} with this month's and last month's values."""
    today = datetime.date.today()
    last = (today.replace(day=1) - datetime.timedelta(days=1))
    out = []
    for d in (today, last) if "{" in url else (today,):
        u = url.replace("{year}", str(d.year)).replace("{month}", d.strftime("%b")).replace("{mm}", f"{d.month:02d}")
        if u not in out:
            out.append(u)
    return out


def read_source(src):
    """Return (items, status). items: list of dicts with url, title, date."""
    items = []
    secret = src.get("needs_secret")
    if secret and not os.environ.get(secret):
        return [], f"needs a key: add the repository secret {secret} (see source-watch/README.md)"
    for listing in [u for raw in src["listing"] if isinstance(src["listing"], list) for u in expand(raw)] or expand(src["listing"]):
        if secret:
            listing = listing.replace("{" + secret + "}", urllib.parse.quote(os.environ[secret]))
        status, final, text = fetch(listing, data=src.get("post", "").encode() or None)
        sign = blocked(text)
        if sign:
            return [], f"blocked ({sign})"
        mode = src.get("mode", "links")
        if mode == "links":
            p = Links()
            p.feed(text)
            pat = re.compile(src["item"])
            for href, title in p.items:
                if pat.search(href):
                    items.append({"url": urllib.parse.urljoin(final, html.unescape(href)), "title": title, "date": ""})
        elif mode == "rows":
            p = Links()
            p.feed(text)
            pat = re.compile(src["item"])
            for row in p.rows:
                if pat.search(row):
                    items.append({"url": listing, "title": row[:400], "date": "", "key": row})
        elif mode == "feed":
            root = ET.fromstring(text.encode())
            for el in root.iter():
                tag = el.tag.split("}")[-1]
                if tag not in ("item", "entry"):
                    continue
                get = {c.tag.split("}")[-1]: c for c in el}
                link = get.get("link")
                href = (link.get("href") or link.text or "").strip() if link is not None else ""
                items.append({"url": href, "title": " ".join((get["title"].text or "").split()) if "title" in get else "",
                              "date": ((get.get("pubDate") or get.get("updated") or get.get("published") or get.get("date"))
                                       .text or "")[:40] if any(k in get for k in ("pubDate", "updated", "published", "date")) else ""})
        elif mode == "json":
            data = json.loads(text)
            for it in dig(data, src.get("items_path")):
                url = str(dig(it, src["url_field"]) or "")
                items.append({"url": urllib.parse.urljoin(src.get("url_prefix", final), url),
                              "title": " ".join(str(dig(it, src.get("title_field", "")) or "").split()),
                              "date": str(dig(it, src.get("date_field", "")) or "")[:10]})
        elif mode == "xml-prec":  # law.go.kr Open API, court precedents
            root = ET.fromstring(text.encode())
            for el in root.iter("prec"):
                items.append({"url": "https://www.law.go.kr/LSW/precInfoP.do?precSeq=" + (el.findtext("판례일련번호") or ""),
                              "title": " ".join(filter(None, [el.findtext("법원명"), el.findtext("사건번호"), el.findtext("사건명")])),
                              "date": (el.findtext("선고일자") or "").replace(".", "-")})
        else:
            raise ValueError(f"unknown mode {mode}")
    if not items:
        return [], "read, but no items found (the page layout may have changed)"
    return items, "ok"


def known_links():
    links = set()
    for path in (ROOT / "data").rglob("*.csv"):
        try:
            for m in re.finditer(r"https?://[^\s,\"]+", path.read_text(encoding="utf-8", errors="ignore")):
                links.add(m.group(0).rstrip("/"))
        except OSError:
            pass
    return links


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="read the sources but write nothing")
    ap.add_argument("--only", help="run one source id")
    args = ap.parse_args()

    config = json.loads((WATCH / "sources.json").read_text(encoding="utf-8"))
    sources = [s for s in config["sources"] if not args.only or s["id"] == args.only]
    today = datetime.date.today().isoformat()
    known = known_links()
    status_file = WATCH / "state" / "_status.json"
    old_status = json.loads(status_file.read_text(encoding="utf-8")) if status_file.is_file() else {}
    new_status, found, report = {}, [], []

    for src in sources:
        sid = src["id"]
        state_file = WATCH / "state" / f"{sid}.txt"
        seen = set(state_file.read_text(encoding="utf-8").split("\n")) if state_file.is_file() else set()
        first = not state_file.is_file()
        try:
            items, status = read_source(src)
        except urllib.error.HTTPError as e:
            items, status = [], f"refused (HTTP {e.code})"
        except Exception as e:  # noqa: BLE001
            items, status = [], f"could not be read ({type(e).__name__}: {str(e)[:120]})"
        ok = status == "ok"
        new_status[sid] = {"status": "ok" if ok else "fail", "detail": status,
                           "since": old_status.get(sid, {}).get("since", today) if (old_status.get(sid, {}).get("status") == ("ok" if ok else "fail")) else today}
        kw = [k.lower() for k in src.get("keywords", [])]
        fresh = 0
        for it in items:
            key = it.get("key") or it["url"].rstrip("/")
            if not key or key in seen:
                continue
            seen.add(key)
            if first or it["url"].rstrip("/") in known and src.get("mode") != "rows":
                continue
            text = (it["title"] + " " + it["url"]).lower()
            hits = [k for k in kw if k in text]
            if kw and not hits:
                continue
            fresh += 1
            found.append({"found_on": today, "source": sid, "country": src["country"], "kind": src["kind"],
                          "body": src["name"], "title": it["title"][:400], "date": it["date"],
                          "official_link": it["url"], "matched_terms": ";".join(hits), "site_status": "new",
                          "note": "Change in the ratification table: compare with the site" if src.get("mode") == "rows" else ""})
        report.append((src, status, len(items), fresh, first))
        print(f"{sid}: {status}; {len(items)} items; {fresh} new" + (" (first run: recorded as seen)" if first and ok else ""), flush=True)
        if not args.dry_run and ok:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text("\n".join(sorted(s for s in seen if s)), encoding="utf-8")

    if args.dry_run:
        bad = [r for r in report if r[1] != "ok"]
        print(f"\n{len(report) - len(bad)} of {len(report)} sources read; {len(found)} new items would be listed.")
        return

    if found:
        out = WATCH / "found" / f"new-{today}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        exists = out.is_file()
        with out.open("a", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, FOUND_COLS)
            if not exists:
                w.writeheader()
            w.writerows(found)
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(new_status, indent=1, sort_keys=True), encoding="utf-8")

    # Report: what is new, and what a person has to do
    lines = [f"# Source watch, {today}", ""]
    lines.append(f"{sum(1 for r in report if r[1] == 'ok')} of {len(report)} sources read. "
                 f"{len(found)} new item(s)" + (f" in `source-watch/found/new-{today}.csv`." if found else "."))
    lines += ["", "## New items to read and confirm", ""]
    by_src = {}
    for f in found:
        by_src.setdefault(f["source"], []).append(f)
    if not by_src:
        lines.append("None this week.")
    for src, st, n, fresh, first in report:
        if src["id"] in by_src:
            lines.append(f"- **{src['country']} · {src['name']}** ({src['operator']}): {fresh} new")
            for f in by_src[src["id"]][:15]:
                lines.append(f"  - {f['title'][:140] or f['official_link']} {f['date']} <{f['official_link']}>")
            if fresh > 15:
                lines.append(f"  - … {fresh - 15} more in the CSV")
    lines += ["", "## Work for a person", "",
              "Sources the watch could not read. Items marked NEW stopped working this week "
              "(or are new to the watch) and should go into the follow-up list; the others are already known.", ""]
    any_fail = False
    for src, st, n, fresh, first in report:
        if st != "ok":
            any_fail = True
            was_ok = old_status.get(src["id"], {}).get("status") != "fail"
            lines.append(f"- {'NEW ' if was_ok else ''}{src['country']} · {src['name']} ({src['operator']}): {st}. "
                         f"Check by hand: <{src.get('home', src['listing'] if isinstance(src['listing'], str) else src['listing'][0])}>")
    if not any_fail:
        lines.append("None: every source could be read.")
    first_runs = [r[0]["id"] for r in report if r[4] and r[1] == "ok"]
    if first_runs:
        lines += ["", f"First run for: {', '.join(first_runs)}. What they list now was recorded as seen; new items show from next week."]
    rep = WATCH / "reports" / f"{today}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (WATCH / "reports" / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport: {rep.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
