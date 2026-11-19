"""Write the "How to cite" block on every database page.

Settings live in tools/citation.json (authors, titles, DOI). The version and
date of each database are read from the page's own Dataset metadata
(the JSON-LD "version" and "dateModified"), so a page that bumps its version
gets a matching citation the next time this script runs.

    python3 tools/cite_blocks.py           # update the pages
    python3 tools/cite_blocks.py --check   # exit 1 if any page is out of date

The script is idempotent. The block sits between <!-- imr-cite:start --> and
<!-- imr-cite:end -->; on the first run it replaces each page's older citation
line (see FIRST_RUN below), afterwards it only rewrites what is between the
markers. Run it again after rebuilding a page with the older build scripts,
and after setting the DOI.
"""
import datetime
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CFG = json.loads((ROOT / "tools" / "citation.json").read_text(encoding="utf-8"))

START, END = "<!-- imr-cite:start -->", "<!-- imr-cite:end -->"
TOP_START, TOP_END = "<!-- imr-citeas:start -->", "<!-- imr-citeas:end -->"
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

# Where the block goes the first time: (pattern, mode). "replace" swaps the
# match for the block; "after"/"before" insert it next to the match.
FIRST_RUN = {
    "migration-law": (r'<h3>How to cite</h3>\s*<p class="citebox" id="citation">.*?</p>', "replace"),
    "court-decisions": (r'<p class="g-note">Cite as: .*?</p>', "replace"),
    "gcc": (r'<h3[^>]*>How to cite</h3>\s*<div id="g-cite" data-noi18n></div>', "replace"),
    "east-asia": (r'<h3[^>]*>How to cite</h3>\s*<div id="g-cite" data-noi18n></div>', "replace"),
    "southeast-asia": (r'<h3[^>]*>How to cite</h3>\s*<div id="g-cite" data-noi18n></div>', "replace"),
    "countries-of-origin": (r'<h3[^>]*>How to cite</h3>\s*<div id="g-cite" data-noi18n></div>', "replace"),
    "domestic-workers": (r'<h3[^>]*>How to cite</h3>\s*<p class="g-mono" id="g-cite" data-noi18n></p>', "replace"),
    "government-hate-speech": (r'Please cite the Institute for Migrant Rights when you use this data\.</p>', "after"),
    "government-hate-speech/elections": (r'<h3[^>]*>How to cite</h3>\s*<p class="g-note" style="margin:0">Institute for Migrant Rights \(2026\)\. Hate Speech.*?</p>', "replace"),
    "databases": (r'<p style="margin: 48px 0 0; font-size: 16px"><b>Need help with a case\?</b>', "before"),
}
# The Gulf page also has a one-line "Cite as" under its title.
TOP_LINE = {"gcc": r'<p class="g-citeas">Cite as: .*?</p>'}

CSS = (
    "<style>.imr-cite{margin:32px 0 0;padding:20px 22px;border:1px solid rgba(120,110,100,.45);border-radius:10px;"
    "background:rgba(120,110,100,.07);font-family:'Figtree',system-ui,sans-serif;font-size:16px;line-height:1.55;text-align:left;scroll-margin-top:12px}"
    ".imr-cite h3{margin:0 0 6px;font-weight:500;font-size:24px}"
    ".imr-cite .imr-cite-lab{margin:16px 0 4px;font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;opacity:.8}"
    ".imr-cite .imr-cite-txt{margin:10px 0 0;overflow-wrap:anywhere}"
    ".imr-cite pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,Menlo,Consolas,monospace;background:rgba(255,255,255,.55);"
    "border:1px solid rgba(120,110,100,.35);border-radius:6px;padding:10px 12px;margin:8px 0 0}"
    ".imr-cite details{margin-top:10px}.imr-cite summary{cursor:pointer;font-weight:600}"
    ".imr-cite .imr-cite-btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}"
    ".imr-cite button{font:600 14px 'Figtree',system-ui,sans-serif;padding:7px 14px;border-radius:999px;border:1px solid currentColor;background:transparent;color:inherit;cursor:pointer}"
    ".imr-cite .imr-cite-note{margin:14px 0 0;font-size:14.5px;opacity:.9}</style>"
)
SCRIPT = (
    "<script>document.addEventListener('click',function(e){var b=e.target.closest('[data-imr-copy]');if(!b)return;"
    "var el=document.getElementById(b.getAttribute('data-imr-copy'));if(!el)return;"
    "var t=(el.innerText||el.textContent).trim(),l=b.textContent;"
    "try{navigator.clipboard.writeText(t).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent=l;},1500);});}catch(x){}});</script>"
)


def esc(s):
    return html.escape(s, quote=False)


def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def author_apa():
    parts = []
    for a in CFG["authors"]:
        parts.append(a["organization"] if "organization" in a else f'{a["family"]}, {a["initials"]}')
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + ", & " + parts[-1]


def author_bib():
    return " and ".join("{" + a["organization"] + "}" if "organization" in a else f'{a["family"]}, {a["given"]}' for a in CFG["authors"])


def doi_url():
    return f'https://doi.org/{CFG["doi"]}' if CFG["doi"] else ""


def citation(page, meta):
    """Return (apa_html, apa_plain, bibtex) for one page."""
    year = (meta.get("dateModified") or "2026")[:4]
    url = "https://theimr.org/" + page["path"] + "/"
    doi = doi_url()
    if page.get("collection"):
        title = CFG["collection_title"]
        ver = CFG["collection_version"]
        tail = "Zenodo. " + doi if doi else url
        vtxt = f" (Version {ver})" if ver else ""
        plain = f"{author_apa()} ({year}). {title}{vtxt} [Data set]. {tail}"
        htm = f"{esc(author_apa())} ({year}). <i>{esc(title)}</i>{esc(vtxt)} [Data set]. {esc(tail)}"
        bib_key, bib_title, bib_ver = "imr_mjs_" + year, title, ver
    else:
        title = page["title"]
        ver = meta.get("version")
        vtxt = f"Version {ver}" if ver else f"Version of {long_date(meta['dateModified'])}" if meta.get("dateModified") else ""
        vpart = f" ({vtxt})" if vtxt else ""
        coll = "Migration Jurisprudence from the South"
        tail = url + (f" (archived at {doi})" if doi else "")
        plain = f"{author_apa()} ({year}). {title}{vpart} [Data set]. {coll}. {tail}"
        htm = f"{esc(author_apa())} ({year}). <i>{esc(title)}</i>{esc(vpart)} [Data set]. {coll}. {esc(tail)}"
        bib_key = "imr_" + page["key"] + "_" + year
        bib_title, bib_ver = title, ver or (meta.get("dateModified") or "")
    lines = [f"@misc{{{bib_key},", f"  author = {{{author_bib()}}},", f"  title = {{{{{bib_title}}}}},"]
    if not page.get("collection"):
        lines.append("  howpublished = {Migration Jurisprudence from the South, Institute for Migrant Rights},")
    lines.append(f"  year = {{{year}}},")
    if bib_ver:
        lines.append(f"  version = {{{bib_ver}}},")
    if doi:
        lines.append(f"  doi = {{{CFG['doi']}}},")
    lines += [f"  url = {{{url}}},", "  note = {Data set. License: CC BY 4.0}", "}"]
    return htm, plain, "\n".join(lines)


def block(page, meta, collection_meta):
    pid = page["key"].replace("_", "-")
    htm, _, bib = citation(page, meta)
    out = [START, CSS, f'<section class="imr-cite" id="cite" aria-labelledby="imr-cite-h-{pid}">',
           f'<h3 id="imr-cite-h-{pid}">How to cite</h3>']
    if page.get("collection"):
        out.append('<p style="margin:0">Each database has its own version number and citation on its page. To cite the collection as a whole, use:</p>')
    elif CFG["doi"]:
        out.append('<p style="margin:0">Please cite the database name, its version and the DOI. The DOI leads to the latest archived release on Zenodo. Each release also has its own DOI, listed on Zenodo; use that one when others need to find exactly the data you used.</p>')
    else:
        out.append('<p style="margin:0">Please cite the database name, its version and the web address, with the date you consulted it.</p>')
    out += [f'<p class="imr-cite-txt" id="imr-cite-{pid}" data-noi18n>{htm}</p>',
            '<div class="imr-cite-btns">'
            f'<button type="button" data-imr-copy="imr-cite-{pid}">Copy citation</button>'
            f'<button type="button" data-imr-copy="imr-bib-{pid}">Copy BibTeX</button></div>',
            f'<details><summary>Show BibTeX</summary><pre id="imr-bib-{pid}" data-noi18n>{esc(bib)}</pre></details>']
    if not page.get("collection"):
        chtm, _, _ = citation({"path": "databases", "collection": True}, collection_meta)
        out += ['<p class="imr-cite-lab">The whole collection</p>', f'<p class="imr-cite-txt" data-noi18n>{chtm}</p>']
    out.append('<p class="imr-cite-note">License: CC BY 4.0. You may reuse and adapt the data if you give credit. '
               f'Reference managers can read the citation file <a href="{CFG["github"]}/blob/main/CITATION.cff">CITATION.cff</a> on GitHub.</p>')
    out += ["</section>", SCRIPT, END]
    return "".join(out)


def update_ld(text):
    """Name the authors (and the DOI, once there is one) in the Dataset metadata."""
    def fix(m):
        try:
            d = json.loads(m.group(2))
        except ValueError:
            return m.group(0)
        if d.get("@type") not in ("Dataset", "DataCatalog"):
            return m.group(0)
        creators = []
        for a in CFG["authors"]:
            if "organization" in a:
                creators.append({"@type": "Organization", "name": a["organization"], "url": "https://theimr.org/"})
            else:
                creators.append({"@type": "Person", "name": f'{a["given"]} {a["family"]}', "givenName": a["given"],
                                 "familyName": a["family"], "affiliation": [{"@type": "Organization", "name": x.strip()} for x in a["affiliation"].split(";")]})
        d["creator"] = creators
        d.setdefault("license", "https://creativecommons.org/licenses/by/4.0/")
        if CFG["doi"]:
            d["identifier"] = doi_url()
        else:
            d.pop("identifier", None)
        return m.group(1) + json.dumps(d, ensure_ascii=False) + m.group(3)
    return LD.sub(fix, text, count=1)


def meta_of(text):
    m = LD.search(text)
    try:
        return json.loads(m.group(2)) if m else {}
    except ValueError:
        return {}


def process(page, collection_meta):
    f = SITE / page["path"] / "index.html"
    text = f.read_text(encoding="utf-8")
    meta = meta_of(text)
    new_block = block(page, meta, collection_meta)
    if START in text:
        new = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda m: new_block, text, count=1, flags=re.S)
    else:
        pat, mode = FIRST_RUN[page["path"]]
        m = re.search(pat, text, re.S)
        if not m:
            raise SystemExit(f"{f}: could not find where to put the citation block")
        rep = {"replace": new_block, "after": m.group(0) + new_block, "before": new_block + m.group(0)}[mode]
        new = text[:m.start()] + rep + text[m.end():]
    if page["path"] in TOP_LINE:
        htm, _, _ = citation(page, meta)
        line = (f'{TOP_START}<p class="g-citeas"><span>Cite as:</span> <span data-noi18n>{htm}</span> '
                f'<span>(<a href="#cite">more formats</a>). Paragraphs are numbered for pinpoint citation (for example, ¶ 5.2).</span></p>{TOP_END}')
        if TOP_START in new:
            new = re.sub(re.escape(TOP_START) + ".*?" + re.escape(TOP_END), lambda m: line, new, count=1, flags=re.S)
        else:
            new = re.sub(TOP_LINE[page["path"]], lambda m: line, new, count=1, flags=re.S)
    new = update_ld(new)
    return f, text, new


def sync_cff():
    """Keep the DOI line of CITATION.cff in step with tools/citation.json."""
    f = ROOT / "CITATION.cff"
    if not f.exists():
        return None
    old = f.read_text(encoding="utf-8")
    line = f'doi: "{CFG["doi"]}"' if CFG["doi"] else '# doi: added after the first Zenodo release (see docs/RELEASING.md)'
    new = re.sub(r'^#? ?doi:.*$', lambda m: line, old, count=1, flags=re.M)
    return f, old, new


def main():
    check = "--check" in sys.argv
    collection_meta = meta_of((SITE / "databases" / "index.html").read_text(encoding="utf-8"))
    stale = []
    for page in CFG["pages"]:
        f, old, new = process(page, collection_meta)
        if new != old:
            stale.append(str(f.relative_to(ROOT)))
            if not check:
                f.write_text(new, encoding="utf-8")
    cff = sync_cff()
    if cff and cff[1] != cff[2]:
        stale.append("CITATION.cff")
        if not check:
            cff[0].write_text(cff[2], encoding="utf-8")
    if check:
        if stale:
            print("Citation blocks out of date; run python3 tools/cite_blocks.py:\n  " + "\n  ".join(stale))
            sys.exit(1)
        print("Citation blocks up to date")
    else:
        print(f"Updated {len(stale)} page(s)" + (": " + ", ".join(stale) if stale else ""))


if __name__ == "__main__":
    main()
