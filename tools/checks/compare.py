#!/usr/bin/env python3
"""Compare the check results of a pull request with those of its base branch.

    python3 tools/checks/compare.py --head head.json [--head browser.json] \
        --base base.json [--base base-browser.json] [--external] [--hosts]

Only problems the pull request adds count. Older problems are listed as a
count, so they can be fixed some other day without holding anyone up.

* A new error (a broken internal link, a bad data row, a script error, English
  menu or heading text with no Indonesian version) fails the check.
* A new warning is listed but does not fail it.
* --external tries the external links the pull request adds (official
  sources). Government sites often refuse automated visitors, so these
  results are warnings only.
* --hosts checks that every theimr.org address the site sends visitors to
  (press.theimr.org and the like, from _redirects) answers. A host that does
  not answer is an error even if it was already broken, because visitors are
  being sent to a dead address (this is what took the press pages offline on
  19 November 2026).

The report goes to the GitHub job summary when run in GitHub Actions.
"""
import argparse
import collections
import concurrent.futures
import json
import os
import pathlib
import socket
import ssl
import sys
import urllib.error
import urllib.request

MAX_EXTERNAL = 150
UA = "Mozilla/5.0 (compatible; IMR-link-check/1.0; +https://theimr.org/)"


def load(paths):
    problems, ext, data_links, hosts = {}, {}, {}, set()
    for path in paths or []:
        d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        for p in d.get("problems", []):
            old = problems.get(p["key"])
            if not old or (old["level"] == "warning" and p["level"] == "error"):
                problems[p["key"]] = p
        ext.update(d.get("external_links", {}))
        data_links.update(d.get("data_links", {}))
        hosts.update(d.get("hosts", []))
    return problems, ext, data_links, hosts


def try_url(url):
    """Return (verdict, detail): verdict is ok, broken or unsure."""
    ctx = ssl.create_default_context()
    last = ""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
                return "ok", str(r.status)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (404, 410):
                if method == "GET":
                    return "broken", last
                continue
            if e.code in (405, 501) and method == "HEAD":
                continue
            if method == "GET" or e.code not in (400, 403):
                return "unsure", last
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, socket.gaierror):
                return "broken", "the address does not exist (DNS)"
            last = str(reason)[:120]
        except (TimeoutError, socket.timeout):
            last = "no answer within 25 seconds"
        except Exception as e:  # noqa: BLE001
            last = str(e)[:120]
    return "unsure", last


def check_hosts(hosts):
    out = []
    for host in sorted(hosts):
        if not host.endswith("theimr.org"):
            continue
        verdict, detail = "unsure", ""
        for _ in range(3):
            try:
                socket.getaddrinfo(host, 443)
            except socket.gaierror:
                verdict, detail = "broken", "has no DNS record"
                continue
            verdict, detail = try_url(f"https://{host}/")
            if verdict == "ok":
                break
            if detail.startswith("HTTP 4"):  # it answers; a 4xx on / is the site's business
                verdict = "ok"
                break
        if verdict != "ok":
            out.append({"check": "hosts", "level": "error", "key": f"hosts|{host}", "where": "site/_redirects",
                        "message": f"Visitors are sent to https://{host}/, but it {detail or 'does not answer'}. "
                                   "Set up its DNS record and the Netlify domain first, or take the redirect out."})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--head", action="append", required=True)
    ap.add_argument("--base", action="append")
    ap.add_argument("--external", action="store_true")
    ap.add_argument("--hosts", action="store_true")
    ap.add_argument("--report", help="also write the report to this file")
    args = ap.parse_args()

    head, h_ext, h_data, h_hosts = load(args.head)
    base, b_ext, b_data, _ = load(args.base) if args.base else ({}, {}, {}, set())
    have_base = bool(args.base)
    new = [p for k, p in head.items() if k not in base]
    fixed = [k for k in base if k not in head]
    old = [p for k, p in head.items() if k in base]

    if args.hosts:
        new += check_hosts(h_hosts)

    external_results = []
    if args.external and have_base:
        added = {**{u: w for u, w in h_ext.items() if u not in b_ext}, **{u: w for u, w in h_data.items() if u not in b_data}}
        urls = sorted(added)[:MAX_EXTERNAL]
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            for url, (verdict, detail) in zip(urls, pool.map(try_url, urls)):
                if verdict != "ok":
                    external_results.append((verdict, url, detail, added[url]))
        for verdict, url, detail, where in external_results:
            new.append({"check": "external", "level": "warning", "key": f"external|{url}", "where": where,
                        "message": ("Looks broken" if verdict == "broken" else "Could not confirm (the site may refuse automated visits)")
                        + f": {url} ({detail})"})
        if len(added) > MAX_EXTERNAL:
            new.append({"check": "external", "level": "warning", "key": "external|limit", "where": "",
                        "message": f"{len(added)} new external links; only the first {MAX_EXTERNAL} were tried."})

    errors = [p for p in new if p["level"] == "error"]
    warnings = [p for p in new if p["level"] != "error"]
    names = {"data": "Data files", "links": "Links", "i18n": "English and Indonesian", "browser": "Pages in a browser",
             "hosts": "Site addresses", "external": "External links (new in this pull request)"}

    lines = ["## Site checks", ""]
    if errors:
        lines.append(f"**{len(errors)} new problem(s) to fix before merging.** " if have_base else f"**{len(errors)} problem(s).**")
    else:
        lines.append("**No new problems.** " + ("This pull request does not add any broken links, bad data rows, script errors or untranslated menu text." if have_base else ""))
    if warnings:
        lines.append(f"{len(warnings)} new note(s) to look at; they do not block merging.")
    if have_base:
        lines.append(f"Problems already on the base branch: {len(old)} (not counted here). Fixed by this pull request: {len(fixed)}.")
    lines.append("")
    for title, items in (("Fix before merging", errors), ("Worth a look", warnings)):
        if not items:
            continue
        lines.append(f"### {title}")
        by = collections.defaultdict(list)
        for p in items:
            by[p["check"]].append(p)
        for check, ps in sorted(by.items()):
            lines.append(f"**{names.get(check, check)}** ({len(ps)})")
            lines.append("")
            for p in sorted(ps, key=lambda x: x["where"])[:60]:
                where = f"`{p['where']}` " if p["where"] else ""
                lines.append(f"- {where}{p['message']}")
            if len(ps) > 60:
                lines.append(f"- … and {len(ps) - 60} more")
            lines.append("")
    if have_base and old:
        counts = collections.Counter(names.get(p["check"], p["check"]) for p in old)
        lines.append("<details><summary>Older problems, already on the base branch</summary>\n")
        lines += [f"- {k}: {v}" for k, v in sorted(counts.items())]
        lines.append("\nRun the checks locally to list them (see tools/checks/README.md).\n</details>")
    report = "\n".join(lines) + "\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(report)
    if args.report:
        pathlib.Path(args.report).write_text(report, encoding="utf-8")
    if os.environ.get("GITHUB_ACTIONS"):
        for p in errors[:50] + warnings[:20]:
            kind = "error" if p["level"] == "error" else "warning"
            loc = ""
            if p["where"]:
                f, _, line = p["where"].partition(":")
                loc = f" file={f}" + (f",line={line}" if line.isdigit() else "")
            msg = p["message"].replace("%", "%25").replace("\r", "").replace("\n", " ")
            print(f"::{kind}{loc}::{msg}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
