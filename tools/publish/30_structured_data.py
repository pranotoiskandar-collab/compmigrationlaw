"""schema.org and Google Scholar markup, added at publish time.

- Decision pages: richer JSON-LD (court, date, place, case number, official source,
  last checked) and a visible "Last checked" line.
- Database pages (JSON-LD Dataset): JSON downloads from the API, the catalogue they
  belong to, and Google Scholar citation_* tags (they are written as working papers).
- /databases/: the catalogue lists its datasets the way Dataset Search reads them.
- Country pages (/countries/<name>/, /id/negara/<nama>/), where they exist: a list of
  the country's laws as schema.org Legislation, and a box with its data downloads.
"""
import html as H
import json
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import BASE, COUNTRIES, DATA, SITE, iso2, ld_blocks, name, read_csv  # noqa: E402

ORG = {"@type": "Organization", "name": "Institute for Migrant Rights", "url": f"{BASE}/"}
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
CATALOG = {"@type": "DataCatalog", "name": "Migration Jurisprudence from the South", "url": f"{BASE}/databases/"}
e = H.escape


def replace_ld(html, fn):
    blocks = ld_blocks(html)
    for start, end, obj in reversed(blocks):
        new = fn(obj)
        if new is not None:
            html = html[:start] + json.dumps(new, ensure_ascii=False) + html[end:]
    return html


# ---------------------------------------------------------------- decision pages
decisions = {r["id"]: r for r in read_csv(DATA / "court-decisions" / "decisions.csv")}
TIER = {"national": "national court", "regional": "regional court or body", "international": "international court or body"}
n_dec = 0
for page in (SITE / "court-decisions" / "d").glob("*/index.html"):
    d = decisions.get(page.parent.name)
    if not d:
        continue
    html = page.read_text(encoding="utf-8")
    if "imr-checked" in html:
        continue
    code = iso2(d["country"])
    sources = [s.strip() for s in d["sources"].split("|") if s.strip()]

    def enrich(obj, d=d, code=code, sources=sources):
        if obj.get("@type") != "CreativeWork":
            return None
        obj["genre"] = "Court decision"
        obj["identifier"] = [x for x in [d["id"], d["citation"]] if x and "to be added" not in x]
        obj["creator"] = {"@type": "GovernmentOrganization", "name": d["court"]}
        if d["date"]:
            obj["dateCreated"] = d["date"]
        if code:
            obj["spatialCoverage"] = {"@type": "Place", "name": name(code)}
        if d["issues"]:
            obj["keywords"] = [k.strip() for k in re.split(r"[;|]", d["issues"]) if k.strip()] + ["migrant workers", "migration law", "court decision"]
        obj["dateModified"] = d.get("last_checked") or obj.get("dateModified")
        obj["license"] = LICENSE
        obj["isBasedOn"] = sources[:3]
        obj["isPartOf"] = {"@type": "Dataset", "name": "Court Decisions: Migration Jurisprudence from the South",
                           "url": f"{BASE}/court-decisions/", "includedInDataCatalog": CATALOG}
        obj["creativeWorkStatus"] = {"S": "Summary not yet checked against the judgment",
                                     "C": "Candidate entry: name, court, year and topic only",
                                     "P": "Checked against the judgment"}.get(d["status"], "")
        return obj

    html = replace_ld(html, enrich)
    if d.get("last_checked"):
        line = (f'<p class="g-note imr-checked">Last checked: <time datetime="{d["last_checked"]}">{d["last_checked"]}</time>'
                f' · <a href="/open-data/">Open data</a></p>')
        m = re.search(r"<p>Citation:.*?</p>", html, re.S) or re.search(r"</h1>", html)
        if m:
            html = html[:m.end()] + "\n" + line + html[m.end():]
    page.write_text(html, encoding="utf-8")
    n_dec += 1

# ---------------------------------------------------------------- database pages
n_ds = 0
for page in SITE.rglob("index.html"):
    rel = page.relative_to(SITE).parent
    if rel.parts[:1] in (("court-decisions",),) and len(rel.parts) > 1 or rel.parts[:1] in (("press",), ("api",)):
        continue
    html = page.read_text(encoding="utf-8")
    if '"Dataset"' not in html or "citation_title" in html:
        continue
    found = {}

    def dataset(obj):
        if obj.get("@type") != "Dataset":
            return None
        db = str(rel)
        dist = obj.setdefault("distribution", [])
        have = {x.get("contentUrl") for x in dist if isinstance(x, dict)}
        for x in list(dist):
            u = x.get("contentUrl", "") if isinstance(x, dict) else ""
            m = re.match(re.escape(BASE) + r"/(.+)/data/([^/]+)\.csv$", u)
            if m:
                j = f"{BASE}/api/v1/datasets/{m.group(1)}/{m.group(2)}.json"
                if j not in have and (SITE / "api" / "v1" / "datasets" / m.group(1) / f"{m.group(2)}.json").exists():
                    dist.append({"@type": "DataDownload", "encodingFormat": "application/json", "name": x.get("name", m.group(2)) + " (JSON)", "contentUrl": j})
        obj.setdefault("creator", ORG)
        obj.setdefault("license", LICENSE)
        obj.setdefault("isAccessibleForFree", True)
        obj["includedInDataCatalog"] = CATALOG
        obj.setdefault("publisher", ORG)
        found.update(obj)
        return obj

    html = replace_ld(html, dataset)
    if found:
        date = found.get("dateModified") or found.get("datePublished") or ""
        tags = [("citation_title", found.get("name", "")),
                ("citation_author", "Institute for Migrant Rights"),
                ("citation_publication_date", date.replace("-", "/")),
                ("citation_technical_report_institution", "Institute for Migrant Rights"),
                ("citation_publisher", "Institute for Migrant Rights"),
                ("citation_abstract_html_url", found.get("url", "")),
                ("citation_language", "en"),
                ("citation_keywords", "; ".join((found.get("keywords") or [])[:20]) if isinstance(found.get("keywords"), list) else ""),
                ("DC.title", found.get("name", "")), ("DC.creator", "Institute for Migrant Rights"),
                ("DC.date", date), ("DC.rights", "CC BY 4.0"), ("DC.type", "Dataset")]
        if found.get("version"):
            tags.append(("citation_technical_report_number", "Version " + str(found["version"])))
        meta = "".join(f'<meta name="{k}" content="{e(v)}">\n' for k, v in tags if v)
        html = html.replace("</head>", meta + "</head>", 1)
        n_ds += 1
    page.write_text(html, encoding="utf-8")

# The catalogue page lists its datasets under "dataset", which Dataset Search reads
cat_page = SITE / "databases" / "index.html"
if cat_page.exists():
    def catalog(obj):
        if obj.get("@type") != "DataCatalog" or "dataset" in obj:
            return None
        parts = obj.get("hasPart") or []
        obj["dataset"] = [p for p in parts if isinstance(p, dict) and p.get("@type") == "Dataset"] or parts
        obj.setdefault("license", LICENSE)
        obj.setdefault("creator", ORG)
        return obj
    cat_page.write_text(replace_ld(cat_page.read_text(encoding="utf-8"), catalog), encoding="utf-8")

# ---------------------------------------------------------------- the organisation
# IMR was founded in 2007 (oto, 2026-11-19); search engines had shown 2010.
FOUNDED = "2007"


def org(obj):
    if not isinstance(obj, dict):
        return obj
    for k, v in list(obj.items()):
        if isinstance(v, dict):
            obj[k] = org(v)
        elif isinstance(v, list):
            obj[k] = [org(x) for x in v]
    if obj.get("@type") in ("Organization", "NGO", "ResearchOrganization") and obj.get("name") == "Institute for Migrant Rights" and len(obj) > 3:
        obj["foundingDate"] = FOUNDED
    return obj


n_org = 0
for page in [SITE / "index.html", SITE / "contact.html", SITE / "people.html", SITE / "legal-clinic" / "how-we-work" / "index.html"]:
    if not page.exists():
        continue
    html = page.read_text(encoding="utf-8")
    new = replace_ld(html, lambda o: org(o) if "Institute for Migrant Rights" in json.dumps(o) else None)
    if '"foundingDate"' not in new and page.name == "index.html" and page.parent == SITE:
        ld = {"@context": "https://schema.org", "@type": "Organization", "name": "Institute for Migrant Rights",
              "alternateName": "IMR", "url": f"{BASE}/", "foundingDate": FOUNDED,
              "address": {"@type": "PostalAddress", "addressLocality": "Cianjur", "addressRegion": "Jawa Barat", "addressCountry": "ID"}}
        new = new.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
    if new != html:
        page.write_text(new, encoding="utf-8")
        n_org += 1
print(f"  organisation: foundingDate {FOUNDED} on {n_org} pages")

# ---------------------------------------------------------------- country pages
LAW_FILES = [("gcc", "domestic-laws.csv"), ("east-asia", "domestic-laws.csv"), ("southeast-asia", "domestic-laws.csv"),
             ("countries-of-origin", "laws-policies.csv")]
laws = {}
for db, f in LAW_FILES:
    p = DATA / db / f
    if p.exists():
        for r in read_csv(p):
            code = iso2(r.get("s", ""))
            if code:
                laws.setdefault(code, []).append((db, r))
api_index = {}
idx = SITE / "api" / "v1" / "countries" / "index.json"
if idx.exists():
    api_index = {c["iso2"]: c for c in json.loads(idx.read_text(encoding="utf-8"))["countries"]}


def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def law_ld(code):
    items = []
    for i, (db, r) in enumerate(laws.get(code, []), 1):
        url = r.get("url") or r.get("link") or ""
        item = {"@type": "Legislation", "name": r.get("title", ""), "legislationJurisdiction": name(code),
                "legislationIdentifier": r.get("id", "")}
        if r.get("orig"):
            item["alternateName"] = r["orig"]
        if re.match(r"\d{4}", r.get("year", "")):
            item["legislationDate"] = r["year"][:4]
        if r.get("type"):
            item["legislationType"] = r["type"]
        if url.startswith("http"):
            item["url"] = url
        if r.get("last_checked"):
            item["dateModified"] = r["last_checked"]
        items.append({"@type": "ListItem", "position": i, "item": item})
    return items


n_ct = 0
for lang, folder in (("en", SITE / "countries"), ("id", SITE / "id" / "negara")):
    if not folder.is_dir():
        continue
    for c in COUNTRIES:
        names = [c["id"]] if lang == "id" else [c["en"], *c["aliases"]]
        page = next((folder / slug(n) / "index.html" for n in names if (folder / slug(n) / "index.html").exists()), None)
        if not page:
            continue
        code = c["iso2"]
        html = page.read_text(encoding="utf-8")
        if "imr-country-data" in html:
            continue
        items = law_ld(code)
        if items:
            ld = {"@context": "https://schema.org", "@type": "ItemList",
                  "name": f"Laws on migrant workers in {name(code)} in the IMR databases", "numberOfItems": len(items), "itemListElement": items}
            html = html.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
        if code in api_index:
            box = (f'<div role="region" aria-label="Open data" class="imr-country-data" style="margin:32px 0;padding:16px 20px;max-width:100%;box-sizing:border-box;border:1px solid rgba(120,110,100,.45);border-radius:10px">'
                   f'<h2 style="margin:0 0 6px;font-size:22px">{"Unduh data negara ini" if lang == "id" else "Download the data for this country"}</h2>'
                   f'<p style="margin:0">{api_index[code]["records"]:,} {"baris dari semua basis data IMR" if lang == "id" else "rows from all IMR databases"}: '
                   f'<a href="/api/v1/countries/{code}.zip" data-goatcounter-click="event/open-data/csv/{code}">CSV (zip)</a> · '
                   f'<a href="/api/v1/countries/{code}.json" data-goatcounter-click="event/open-data/json/{code}">JSON</a> · '
                   f'<a href="/open-data/">{"Tentang data terbuka" if lang == "id" else "About the open data"}</a>. CC BY 4.0.</p></div>')
            m = re.search(r"<h2[^>]*>\s*(About this page|Tentang halaman ini)", html)
            if m:
                start = m.start()
                opener = re.search(r"<(section|div)\b[^>]*>\s*$", html[:start])
                if opener:
                    start = opener.start()
                html = html[:start] + box + html[start:]
            else:
                html = re.sub(r"(</div>\s*</main>)", lambda mm: box + mm.group(1), html, count=1)
        page.write_text(html, encoding="utf-8")
        n_ct += 1
print(f"  structured data: {n_dec} decision pages, {n_ds} database pages, {n_ct} country pages")
