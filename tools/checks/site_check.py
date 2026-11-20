#!/usr/bin/env python3
"""Static checks on one built copy of the site and its data.

Run it on a checkout after the Netlify build command has run there
(tools/copy_data.py, then tools/press_subdomain.py). It writes a JSON file of
problems. compare.py then compares the problems in a pull request with those
already on the base branch, so a pull request is only held up by problems it
adds.

    python3 tools/checks/site_check.py --root . --out problems.json

Checks:
  data   every CSV under data/: readable, same width as the header, and (outside
         raw/ and sources/ folders) dates, country codes, links and ids in the
         forms CONTRIBUTING.md asks for
  links  every link, image, script and stylesheet on every page, every URL in
         sitemap.xml, llms.txt and robots.txt, every file path named in the
         site's own scripts, and every local target in _redirects
  i18n   visible English text on pages with the EN/ID switch that has no
         Indonesian entry in /assets/lang.js or the page's own *-i18n.js file
It also lists the external links on pages and in data, so compare.py can test
the new ones, and the hosts named in _redirects.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse
from html.parser import HTMLParser

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from iso_codes import ISO2, ISO3, EXTRA2  # noqa: E402

MAIN_HOSTS = {"theimr.org", "www.theimr.org", "theimr.netlify.app"}
PRESS_HOST = "press.theimr.org"


def problem(check, level, key, where, message):
    return {"check": check, "level": level, "key": f"{check}|{key}", "where": where, "message": message}


# --------------------------------------------------------------------------- data

DATE_COLS = {"date", "adopted", "in_force", "checked_on", "retrieved", "signed", "decided",
             "decision_date", "date_of_judgment", "amended", "latest_amendment_date_official"}
URL_COLS = {"url", "official_link", "english_version_url", "official_url_found", "pdf_url", "detail_url"}
COUNTRY_COLS = {"country", "iso2", "country_code", "gcc_state"}
DATE_RE = re.compile(r"\d{4}(-\d{2}(-\d{2})?)?")
URL_RE = re.compile(r"https?://[^\s/$.?#][^\s]*")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def valid_date(value):
    if not DATE_RE.fullmatch(value):
        return "not in YYYY-MM-DD form (or YYYY / YYYY-MM)"
    parts = [int(x) for x in value.split("-")]
    try:
        datetime.date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)
    except ValueError:
        return "not a real date"
    if parts[0] < 1600:
        return "year before 1600"
    if value[:10] > (datetime.date.today() + datetime.timedelta(days=1)).isoformat()[: len(value)]:
        return "date in the future"
    return None


def check_data(root):
    out = []
    data = root / "data"
    for path in sorted(data.rglob("*.csv")):
        rel = str(path.relative_to(root))
        strict = "incoming" in path.parts
        loose = {"raw", "sources"} & set(path.parts)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            out.append(problem("data", "error", f"{rel}|utf8", rel, "File is not UTF-8. Save it as CSV UTF-8."))
            continue
        rows = list(csv.reader(text.lstrip("﻿").splitlines()))
        if not rows:
            out.append(problem("data", "error", f"{rel}|empty", rel, "File is empty."))
            continue
        header = [h.strip() for h in rows[0]]
        width = len(header)
        seen_cols = collections.Counter(h.lower() for h in header)
        for name, n in seen_cols.items():
            if not name:
                out.append(problem("data", "error", f"{rel}|blank-header", f"{rel}:1", "A column has no name."))
            elif n > 1:
                out.append(problem("data", "error", f"{rel}|dup-header|{name}", f"{rel}:1", f"Column '{name}' appears {n} times."))
        occurrences = collections.Counter()

        def add(level, rule, col, value, line, message):
            base = f"{rel}|{rule}|{col}|{value[:80]}"
            occurrences[base] += 1
            out.append(problem("data", level, f"{base}|#{occurrences[base]}", f"{rel}:{line}", message))

        # line numbers: csv rows can span lines, so count them as the reader does
        line_of = []
        reader = csv.reader(text.lstrip("﻿").splitlines(keepends=True))
        line = 1
        for row in reader:
            line_of.append(line)
            line = 1 + reader.line_num
        cols = [h.lower() for h in header]
        # In published files the country column is held to ISO codes only if it mostly uses them already
        iso_share = {}
        for i, c in enumerate(cols):
            if c in COUNTRY_COLS:
                vals = [r[i].strip() for r in rows[1:] if i < len(r) and r[i].strip()]
                iso_share[i] = (sum(1 for v in vals if re.fullmatch(r"[A-Z]{2}", v)) / len(vals)) if vals else 1
        ids = collections.Counter()
        for n, row in enumerate(rows[1:], start=1):
            ln = line_of[n] if n < len(line_of) else n + 1
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) != width:
                add("error", "width", "", str(len(row)), ln,
                    f"Row has {len(row)} columns; the header has {width}. Check for an unquoted comma or a missing value.")
                continue
            if loose:
                continue
            for i, cell in enumerate(row):
                col, value = cols[i], cell.strip()
                if not value:
                    continue
                if col in DATE_COLS or col.endswith("_date"):
                    if col in ("amended", "latest_amendment_date_official", "signed") and not strict:
                        continue  # these hold notes in some published files
                    why = valid_date(value)
                    if why:
                        add("error", "date", col, value, ln, f"{col} '{value[:40]}': {why}.")
                elif col in URL_COLS:
                    if not URL_RE.fullmatch(value):
                        add("error", "url", col, value, ln, f"{col} '{value[:60]}' is not a full web address (https://...).")
                elif col in COUNTRY_COLS:
                    if re.fullmatch(r"[A-Z]{2}", value):
                        if value not in ISO2 and value not in EXTRA2:
                            add("error", "country", col, value, ln, f"{col} '{value}' is not an ISO 3166 country code.")
                    elif strict or iso_share.get(i, 0) >= 0.8:
                        add("error", "country", col, value, ln, f"{col} '{value[:40]}' should be a two-letter ISO code (for example JP, AE).")
                elif col == "iso3":
                    if value not in ISO3 and value not in ("XKX", "EUU", "WLD"):
                        add("error", "iso3", col, value, ln, f"iso3 '{value[:20]}' is not an ISO 3166 alpha-3 code.")
                if col == "id":
                    ids[value] += 1
                    if ids[value] == 2:
                        add("error", "dup-id", col, value, ln, f"id '{value[:40]}' is used more than once in this file.")
                if EMAIL_RE.search(value) and col not in URL_COLS and "mailto" not in value:
                    add("warning", "email", col, EMAIL_RE.search(value).group(0), ln,
                        "Cell holds an email address. Keep personal contact details out of the data.")
    return out


# --------------------------------------------------------------------------- pages

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_TEXT = {"script", "style", "textarea", "noscript", "template", "code", "pre"}
INTERFACE = {"nav", "header", "footer", "button", "label", "summary", "h1", "h2", "h3", "h4", "th", "option", "legend", "caption"}
I18N_ATTRS = ("placeholder", "aria-label", "title")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, attrs)
        self.links = []  # (tag, attr, value, line)
        self.ids = set()
        self.texts = []  # (text, interface, in_switch_area, case_name)
        self.scripts = []  # ("src", value) or ("inline", code)
        self.clinic = False
        self.decision_page = False
        self._script = None

    def _skip(self):
        for tag, attrs in self.stack:
            if tag in SKIP_TEXT or "data-noi18n" in attrs:
                return True
            lang = attrs.get("lang")
            if lang and not lang.startswith("en") and tag != "html":
                return True
        return False

    def _ctx(self):
        tags = {t for t, _ in self.stack}
        cls = " ".join(a.get("class") or "" for _, a in self.stack)
        # A link to a decision page, or a decision page's own title, shows the case name
        case = any(t == "a" and "/court-decisions/d/" in (a.get("href") or "") for t, a in self.stack) or (
            self.decision_page and "h1" in tags)
        return bool(tags & INTERFACE), bool({"nav", "footer"} & tags or "imr-lang" in cls), case

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: (v if v is not None else "") for k, v in attrs_list}
        line = self.getpos()[0]
        if attrs.get("id"):
            self.ids.add(attrs["id"])
            if attrs["id"] == "langs":
                self.clinic = True
        if attrs.get("name") and tag == "a":
            self.ids.add(attrs["name"])
        for attr in ("href", "src"):
            if attrs.get(attr) is not None and attr in attrs:
                if tag == "link" and attrs.get("rel") in ("preconnect", "dns-prefetch"):
                    continue
                self.links.append((tag, attr, attrs[attr], line))
        if attrs.get("srcset"):
            for part in attrs["srcset"].split(","):
                if part.strip():
                    self.links.append((tag, "srcset", part.strip().split()[0], line))
        if tag == "script":
            if attrs.get("src"):
                self.scripts.append(("src", attrs["src"]))
            elif attrs.get("type", "text/javascript") in ("", "text/javascript", "module"):
                self._script = []
        if tag not in VOID:
            self.stack.append((tag, attrs))
        if not self._skip():
            inter, area, case = self._ctx()
            for a in I18N_ATTRS:
                if attrs.get(a):
                    self.texts.append((attrs[a], True, area, case))

    def handle_startendtag(self, tag, attrs_list):
        self.handle_starttag(tag, attrs_list)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            self.scripts.append(("inline", "".join(self._script)))
            self._script = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._script is not None:
            self._script.append(data)
            return
        if not data.strip() or self._skip():
            return
        self.texts.append((data, *self._ctx()))


def page_url(site, path):
    """The URL path a file is served at, and its host."""
    rel = path.relative_to(site).as_posix()
    host = "theimr.org"
    if rel.startswith("press/"):
        host, rel = PRESS_HOST, rel[len("press/"):]
    url = "/" + rel
    if url.endswith("/index.html"):
        url = url[: -len("index.html")]
    return host, url


def load_redirects(site):
    rules = []
    f = site / "_redirects"
    if f.is_file():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            parts = line.split()
            if len(parts) >= 2 and not parts[0].startswith("#"):
                rules.append((parts[0], parts[1], n))
    return rules


class Resolver:
    def __init__(self, site):
        self.site = site
        self.redirects = load_redirects(site)

    def fs_exists(self, host, path):
        root = self.site / "press" if host == PRESS_HOST else self.site
        path = urllib.parse.unquote(path)
        p = root / path.lstrip("/")
        if path.endswith("/") or path == "":
            return (p / "index.html").is_file()
        return p.is_file() or (p / "index.html").is_file() or p.with_name(p.name + ".html").is_file()

    def redirected(self, host, path):
        for src, _dst, _n in self.redirects:
            if src.startswith("http"):
                u = urllib.parse.urlsplit(src)
                if u.hostname != host and not (host == "theimr.org" and u.hostname == "www.theimr.org"):
                    continue
                src = u.path or "/"
            elif host == PRESS_HOST:
                continue
            if src.endswith("*") and path.startswith(src[:-1]):
                return True
            if path == src or path.rstrip("/") == src.rstrip("/"):
                return True
        return False

    def ok(self, host, path):
        if host == PRESS_HOST and (self.fs_exists(host, path) or self.fs_exists("theimr.org", "/press" + path)):
            return True
        return self.fs_exists(host, path) or self.redirected(host, path)


def split_local(href, host, base_url):
    """Return (host, path, fragment) for a link to this site, or None for external/other links."""
    href = href.strip()
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:", "#", "{", "${")) or "{{" in href:
        return None
    if href.startswith("//"):
        href = "https:" + href
    u = urllib.parse.urlsplit(href)
    if u.scheme in ("http", "https"):
        h = (u.hostname or "").lower()
        if h in MAIN_HOSTS:
            return "theimr.org", u.path or "/", u.fragment
        if h == PRESS_HOST:
            return PRESS_HOST, u.path or "/", u.fragment
        return None
    if u.scheme:
        return None
    full = urllib.parse.urljoin("https://x" + base_url, href)
    v = urllib.parse.urlsplit(full)
    return host, v.path, v.fragment


JS_PATH_RE = re.compile(r"""["'`](/?(?:[\w.-]+/)*[\w.-]+\.(?:csv|json|geojson|bib|pdf|xlsx|zip|txt|xml|js|css|png|jpe?g|svg|webp))["'`]""")


def check_pages(root):
    site = root / "site"
    res = Resolver(site)
    problems, external = [], {}
    pages = {}
    for path in sorted(site.rglob("*.html")):
        try:
            html = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(problem("links", "error", f"utf8|{path.relative_to(root)}", str(path.relative_to(root)), "Page is not UTF-8."))
            continue
        p = Page()
        p.decision_page = path.relative_to(site).as_posix().startswith("court-decisions/d/")
        try:
            p.feed(html)
        except Exception as e:  # noqa: BLE001
            problems.append(problem("links", "error", f"parse|{path.relative_to(root)}", str(path.relative_to(root)), f"Page could not be read: {e}"))
            continue
        pages[path] = p

    ids_by_target = {}
    for path, p in pages.items():
        ids_by_target[page_url(site, path)] = p.ids

    broken = collections.defaultdict(list)
    for path, p in pages.items():
        host, url = page_url(site, path)
        rel = str(path.relative_to(root))
        for tag, attr, value, line in p.links:
            if tag == "a" and value.startswith("http") and attr == "href":
                h = (urllib.parse.urlsplit(value).hostname or "").lower()
                if h and h not in MAIN_HOSTS and h != PRESS_HOST:
                    external.setdefault(value.strip(), f"{rel}:{line}")
            loc = split_local(value, host, url)
            if not loc:
                continue
            h2, target, frag = loc
            if not res.ok(h2, target):
                shown = ("https://press.theimr.org" if h2 == PRESS_HOST else "") + target
                broken[(shown, "error")].append(f"{rel}:{line}")
            elif frag and tag == "a":
                key_url = target if target.endswith("/") or target.endswith(".html") else target + "/"
                ids = ids_by_target.get((h2, key_url))
                if ids is not None and frag not in ids and not re.search(r"[/=!&]", frag):
                    broken[(f"{target}#{frag}", "warning")].append(f"{rel}:{line}")

    # URLs listed in sitemap.xml, llms.txt and robots.txt
    for name in ("sitemap.xml", "llms.txt", "robots.txt", "press/sitemap.xml", "feed.xml"):
        f = site / name
        if not f.is_file():
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            for m in re.finditer(r"https?://(?:www\.)?(?:press\.)?theimr\.org[^\s<>\"')\]]*", line):
                loc = split_local(m.group(0).rstrip(".,;"), "theimr.org", "/")
                if loc and not res.ok(loc[0], loc[1]):
                    broken[(m.group(0), "error")].append(f"site/{name}:{n}")

    # File paths named in the site's own scripts (data files, other scripts)
    for js in sorted(site.rglob("*.js")):
        if "leaflet" in js.parts:
            continue
        host, url = page_url(site, js)
        rel = str(js.relative_to(root))
        text = js.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), start=1):
            if len(line) > 5000:
                continue  # data blobs
            for m in JS_PATH_RE.finditer(line):
                value = m.group(1)
                if not value.startswith("/"):
                    continue  # relative paths depend on the page that loads the script
                loc = split_local(value, host, url)
                if loc and not res.ok(loc[0], loc[1]):
                    broken[(value, "error")].append(f"{rel}:{n}")

    # Local targets of redirects
    for src, dst, n in res.redirects:
        if dst.startswith("/"):
            path = urllib.parse.urlsplit(dst).path
            if ":splat" in path:
                continue
            if not res.fs_exists("theimr.org", path):
                broken[(dst, "error")].append(f"site/_redirects:{n}")

    for (target, level), wheres in sorted(broken.items()):
        more = f" (and {len(wheres) - 1} more places)" if len(wheres) > 1 else ""
        what = "Link to a part of a page that does not exist" if level == "warning" else "Link to a page or file that does not exist"
        problems.append(problem("links", level, target, wheres[0], f"{what}: {target}{more}"))
    return problems, external, pages


# --------------------------------------------------------------------------- i18n

def js_regex(pattern):
    try:
        return re.compile(pattern)
    except re.error:
        return None


def needs_translation(text):
    if not re.search(r"[A-Za-z]{3}", text) or not re.search(r"[a-z]", text):
        return False  # numbers, codes, all-caps case names
    if re.fullmatch(r"(https?://|www\.|doi:|10\.\d{4,}/)\S+|[\w.+-]+@[\w.-]+", text):
        return False
    if re.fullmatch(r"[\W\d_]*[A-Z]{2,6}[\W\d_]*", text):
        return False
    return True


ID_WORDS = set("dan yang di ke dari untuk dengan dalam pada atau tidak ini itu kami anda sebuah oleh bagi tentang hukum negara pekerja putusan buka semua bagian".split())
EN_WORDS = set("the of and to in for with on by from or not this that is are a an".split())


def looks_indonesian(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    return bool(words & ID_WORDS) and not words & EN_WORDS


def looks_like_name(text):
    """Two or more capitalised words and nothing else: a person's or a book's name."""
    words = re.findall(r"[^\s]+", text)
    return len(words) >= 2 and all(w[0].isupper() or not w[0].isalpha() for w in words)


def i18n_level(text, interface, count, decision_count):
    # Case names, and text that appears on only a few court decision pages, are a decision's own
    # content. Template text appears on many of them.
    only_decisions = 0 < decision_count and (decision_count < 10 or decision_count >= count * 0.9)
    return "error" if interface and not only_decisions and not looks_like_name(text) else "warning"


def check_i18n(root, pages):
    site = root / "site"
    lang_js = site / "assets" / "lang.js"
    if not lang_js.is_file():
        return [problem("i18n", "error", "lang.js", "site/assets/lang.js", "The language switch script is missing.")]
    first = lang_js.read_text(encoding="utf-8").split("\n", 1)[0]
    m = re.match(r"\s*window\.SITE_I18N\s*=\s*(\{.*\})\s*;?\s*$", first)
    out = []
    if not m:
        return [problem("i18n", "error", "lang.js-format", "site/assets/lang.js:1",
                        "The first line of lang.js must be window.SITE_I18N={...}; (the checks read the dictionary from it).")]
    try:
        pairs = json.loads(m.group(1), object_pairs_hook=lambda kv: kv)
    except json.JSONDecodeError as e:
        return [problem("i18n", "error", "lang.js-json", "site/assets/lang.js:1", f"The Indonesian dictionary is not valid JSON: {e}")]
    base = {}
    for lang, entries in pairs:
        if lang != "id":
            continue
        counts = collections.Counter(k for k, _ in entries)
        for k, v in entries:
            if k == "__pat":
                continue
            if counts[k] > 1:
                out.append(problem("i18n", "warning", f"dup|{k}", "site/assets/lang.js:1", f"English text listed twice in the dictionary: \"{k[:80]}\""))
            if not isinstance(v, str) or not v.strip():
                out.append(problem("i18n", "error", f"empty|{k}", "site/assets/lang.js:1", f"Empty Indonesian text for \"{k[:80]}\""))
            base[k] = v
        base_pat = dict(entries).get("__pat", [])

    # Group pages by the extra Indonesian scripts they load, then ask node for each group's dictionary
    groups = collections.defaultdict(list)
    for path, p in pages.items():
        if not any(kind == "src" and value.split("?")[0].endswith("/assets/lang.js") for kind, value in p.scripts):
            continue
        host, url = page_url(site, path)
        codes = []
        for kind, value in p.scripts:
            if kind == "src":
                loc = split_local(value, host, url)
                if not loc or loc[1].endswith("/assets/lang.js"):
                    continue
                f = (site / "press" if loc[0] == PRESS_HOST else site) / urllib.parse.unquote(loc[1]).lstrip("/")
                if f.is_file():
                    code = f.read_text(encoding="utf-8", errors="replace")
                    if "SITE_I18N" in code:
                        codes.append(code)
            elif "SITE_I18N" in value:
                codes.append(value)
        key = hashlib.sha1("\0".join(codes).encode()).hexdigest()
        groups[key].append((path, p, codes))
    keys = list(groups)
    jobs = [groups[k][0][2] + [first] for k in keys]
    dicts = {}
    try:
        res = subprocess.run(["node", str(HERE / "i18n_dicts.js")], input=json.dumps({"base": base, "jobs": jobs}),
                             capture_output=True, text=True, timeout=600, check=True)
        for k, d in zip(keys, json.loads(res.stdout)):
            dicts[k] = d
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        out.append(problem("i18n", "warning", "node", "tools/checks/i18n_dicts.js",
                           f"Could not read the pages' own Indonesian files ({e}); only lang.js was used."))
    values = set(base.values())
    seen = {}  # text -> [interface?, pages, first where]
    for k in keys:
        extra = dicts.get(k, {}).get("extra", {})
        pats = [js_regex(p[0]) for p in (dicts.get(k, {}).get("pat") or base_pat)]
        pats = [p for p in pats if p]
        vals = values | set(extra.values())

        def has(t):
            return t in base or t in extra

        def translated(t):
            if has(t):
                return True
            m2 = re.match(r"^(.+) \((\d+)\)$", t)
            if m2 and has(m2.group(1)):
                return True
            return any(p.search(t) for p in pats)

        for path, p, _ in groups[k]:
            rel = str(path.relative_to(root))
            decision = path.relative_to(site).as_posix().startswith(("court-decisions/d/", "court-decisions/all/"))
            for raw, inter, area, case in p.texts:
                if p.clinic and not area:
                    continue
                t = re.sub(r"\s+", " ", raw).strip()
                if not t or t in vals or not needs_translation(t) or translated(t) or looks_indonesian(t):
                    continue
                rec = seen.setdefault(t, [False, 0, rel, 0])
                rec[1] += 1
                if decision or case:
                    rec[3] += 1
                if inter:
                    rec[0] = rec[0] or True
    for t, (inter, count, where, dec) in sorted(seen.items()):
        level = i18n_level(t, inter, count, dec)
        more = f" (on {count} pages)" if count > 1 else ""
        kind = "Menu, heading, button or label text" if inter else "Text"
        out.append(problem("i18n", level, t[:200], where,
                           f"{kind} without an Indonesian version{more}: \"{t[:120]}\". Add it to site/assets/lang.js or the page's *-i18n.js file, or mark the element data-noi18n if it should stay in English."))
    return out


# --------------------------------------------------------------------------- data URLs, hosts

def data_urls(root):
    urls = {}
    for path in sorted((root / "data").rglob("*.csv")):
        if {"raw", "sources"} & set(path.parts):
            continue
        try:
            with path.open(encoding="utf-8-sig", newline="") as fh:
                reader = csv.reader(fh)
                header = [h.strip().lower() for h in next(reader, [])]
                cols = [i for i, h in enumerate(header) if h in URL_COLS]
                for row in reader:
                    for i in cols:
                        if i < len(row) and URL_RE.fullmatch(row[i].strip()):
                            urls.setdefault(row[i].strip(), f"{path.relative_to(root)}:{reader.line_num}")
        except (UnicodeDecodeError, csv.Error):
            continue
    return urls


def redirect_hosts(root):
    hosts = set()
    for src, dst, _ in load_redirects(root / "site"):
        for u in (src, dst):
            if u.startswith("http"):
                hosts.add(urllib.parse.urlsplit(u).hostname)
    return sorted(h for h in hosts if h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repository checkout, already built")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    problems = check_data(root)
    link_problems, external, pages = check_pages(root)
    problems += link_problems
    problems += check_i18n(root, pages)
    result = {
        "problems": problems,
        "external_links": external,
        "data_links": data_urls(root),
        "hosts": redirect_hosts(root),
        "pages": len(pages),
    }
    pathlib.Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    by = collections.Counter((p["check"], p["level"]) for p in problems)
    print(f"{len(pages)} pages read. " + ", ".join(f"{c} {lv}: {n}" for (c, lv), n in sorted(by.items())))


if __name__ == "__main__":
    main()
