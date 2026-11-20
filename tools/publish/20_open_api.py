"""Static open API and per-country downloads.

/api/v1/index.json                     what is available
/api/v1/datasets/<db>/<file>.json      every published CSV as JSON
/api/v1/countries/index.json           every country with its record counts
/api/v1/countries/<ISO2>.json          all rows about one country, from every database
/api/v1/countries/<ISO2>.zip           the same as CSV files, one per source file
/open-data/                            the page that explains it (EN/ID)
"""
import datetime
import html as H
import io
import re
import sys
import zipfile

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import BASE, BY_ISO2, DATA, SITE, iso2, name, read_csv, write_json  # noqa: E402
from pagekit import make_page  # noqa: E402

TODAY = datetime.date.today().isoformat()
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
CITE = "Institute for Migrant Rights (2026). Migration Jurisprudence from the South [Data set]. https://theimr.org/databases/"
API = SITE / "api" / "v1"
TITLES = {
    "atlas": "Farmworker law view (Migration Law Atlas)", "migration-law": "Migration Law Atlas",
    "court-decisions": "Court Decisions", "gcc": "Gulf States", "east-asia": "East Asia",
    "southeast-asia": "Southeast Asia", "countries-of-origin": "Countries of Origin",
    "domestic-workers": "Migrant Domestic Workers", "government-hate-speech": "Government Hate Speech",
    "government-hate-speech/elections": "Elections and non-citizens", "africa": "Africa",
    "ratifications": "Ratification tracker",
}
# Columns that name a state. Values may be names, ISO-2 or ISO-3 codes, or lists.
COUNTRY_COLS = ["country", "iso3", "s", "state", "gcc", "gcc_state", "origin", "destination", "jurisdiction", "o",
                "partner", "countries"]
SKIP_FILES = {"codebook.csv", "protection-codebook.csv", "argument-codes.csv", "reasoning-tools.csv", "duplicates.csv",
              "sources.csv", "demography-sources.csv"}


def published_csvs():
    for path in sorted(DATA.rglob("*.csv")):
        rel = path.relative_to(DATA)
        if {"incoming", "sources"} & set(rel.parts):
            continue
        yield path, str(rel.parent), rel.name


def countries_in(row, file_codes):
    found = set()
    for col in COUNTRY_COLS:
        value = row.get(col)
        if not value:
            continue
        if value.strip().lower() == "all" and file_codes:
            found |= file_codes
            continue
        parts = [value] if iso2(value) else re.split(r"\s*[,;/]\s*|\s+and\s+", value)
        for p in parts:
            code = iso2(p)
            if code:
                found.add(code)
    return found


datasets, per_country = {}, {}
decision_country = {}
for path, db, fname in published_csvs():
    rows = read_csv(path)
    columns = list(rows[0].keys()) if rows else []
    stem = fname[:-4]
    write_json(API / "datasets" / db / f"{stem}.json", {
        "dataset": TITLES.get(db, db), "file": fname, "license": LICENSE, "cite": CITE,
        "csv": f"{BASE}/{db}/data/{fname}", "generated": TODAY, "rows": rows})
    datasets.setdefault(db, []).append({"file": fname, "rows": len(rows), "columns": columns,
                                        "csv": f"{BASE}/{db}/data/{fname}",
                                        "json": f"{BASE}/api/v1/datasets/{db}/{stem}.json"})
    if fname in SKIP_FILES or not rows:
        continue
    key = f"{db}/{fname}"
    wide = [c for c in columns if len(c) == 2 and c.isupper() and c in BY_ISO2]
    if fname == "decisions.csv":
        decision_country = {r["id"]: r["country"] for r in rows}
    file_codes = {iso2(r.get("country") or r.get("s") or "") for r in rows} - {None}
    for r in rows:
        if wide:  # one column per state: give each state its own row
            for c in wide:
                rec = {k: v for k, v in r.items() if k not in wide}
                rec["state"], rec["value"] = c, r[c]
                per_country.setdefault(c, {}).setdefault(key, []).append(rec)
            continue
        codes = countries_in(r, file_codes)
        if not codes and "decision_id" in r and r["decision_id"] in decision_country:
            codes = {iso2(decision_country[r["decision_id"]])} - {None}
        for c in codes:
            per_country.setdefault(c, {}).setdefault(key, []).append(r)

country_index = []
for code in sorted(per_country):
    files = per_country[code]
    info = BY_ISO2.get(code, {"iso3": "", "en": name(code), "id": name(code, "id")})
    counts = {k: len(v) for k, v in files.items()}
    write_json(API / "countries" / f"{code}.json", {
        "iso2": code, "iso3": info.get("iso3", ""), "name": {"en": name(code), "id": name(code, "id")},
        "license": LICENSE, "cite": CITE, "generated": TODAY,
        "note": "Rows from every IMR database that name this state, as the state concerned, a party, an origin or a destination. "
                "Columns follow each database's codebook.csv. last_checked is the date IMR last checked or updated the row.",
        "counts": counts, "records": files})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for k, rows in files.items():
            cols = list(dict.fromkeys(c for r in rows for c in r))
            s = io.StringIO()
            import csv
            w = csv.DictWriter(s, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
            z.writestr(k.replace("/", "--"), s.getvalue())
        z.writestr("README.txt", f"IMR data on {name(code)} ({code}), generated {TODAY}.\nLicense: CC BY 4.0. Cite as: {CITE}\n"
                   "Each CSV holds the rows of one IMR database file that name this state. See codebook.csv in each database.\n")
    (API / "countries" / f"{code}.zip").write_bytes(buf.getvalue())
    country_index.append({"iso2": code, "iso3": info.get("iso3", ""), "name_en": name(code), "name_id": name(code, "id"),
                          "records": sum(counts.values()),
                          "decisions": counts.get("court-decisions/decisions.csv", 0),
                          "json": f"{BASE}/api/v1/countries/{code}.json", "zip": f"{BASE}/api/v1/countries/{code}.zip"})

write_json(API / "countries" / "index.json", {"generated": TODAY, "license": LICENSE, "countries": country_index})
write_json(API / "index.json", {
    "name": "Migration Jurisprudence from the South: open data API", "publisher": "Institute for Migrant Rights",
    "version": "v1", "generated": TODAY, "license": LICENSE, "cite": CITE, "documentation": f"{BASE}/open-data/",
    "source": "https://github.com/pranotoiskandar-collab/compmigrationlaw",
    "endpoints": {"countries": f"{BASE}/api/v1/countries/index.json", "country": f"{BASE}/api/v1/countries/{{ISO2}}.json",
                  "country_zip": f"{BASE}/api/v1/countries/{{ISO2}}.zip",
                  "dataset_file": f"{BASE}/api/v1/datasets/{{database}}/{{file}}.json"},
    "datasets": [{"database": db, "title": TITLES.get(db, db), "files": files} for db, files in datasets.items()]})
(API / "README").write_text("IMR open data API v1. Static, read-only JSON; no key needed. See https://theimr.org/open-data/\n", encoding="utf-8")

headers = SITE / "_headers"
rule = "/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n"
text = headers.read_text(encoding="utf-8") if headers.exists() else ""
if "/api/*" not in text:
    headers.write_text(text + ("\n" if text else "") + rule, encoding="utf-8")

# ---------------------------------------------------------------- the /open-data/ page
e = H.escape
rows_html = "".join(
    f'<tr data-q="{e((c["name_en"] + " " + c["name_id"] + " " + c["iso2"] + " " + c["iso3"]).lower())}">'
    f'<td>{e(c["name_en"])}</td><td data-noi18n>{c["iso2"]}</td><td style="text-align:right">{c["records"]:,}</td>'
    f'<td style="text-align:right">{c["decisions"]:,}</td>'
    f'<td><a href="/api/v1/countries/{c["iso2"]}.json" data-goatcounter-click="event/open-data/json/{c["iso2"]}">JSON</a> · '
    f'<a href="/api/v1/countries/{c["iso2"]}.zip" data-goatcounter-click="event/open-data/csv/{c["iso2"]}">CSV</a></td></tr>'
    for c in sorted(country_index, key=lambda c: c["name_en"]))
ds_html = "".join(
    f'<h3 style="margin:26px 0 6px;font-size:20px;font-weight:600">{e(TITLES.get(db, db))}</h3><ul style="margin:0;padding-left:20px">'
    + "".join(f'<li><span data-noi18n>{e(f["file"])}</span> ({f["rows"]:,} rows): <a href="/{db}/data/{e(f["file"])}">CSV</a> · '
              f'<a href="/api/v1/datasets/{db}/{e(f["file"][:-4])}.json">JSON</a></li>' for f in files) + "</ul>"
    for db, files in datasets.items())
total = sum(c["records"] for c in country_index)
body = f"""
<p class="g-note"><a href="/databases/">Migration Jurisprudence from the South</a> › <span>Open data</span></p>
<h1>Open data and API</h1>
<p>Every database on this site is free to download and reuse under the CC BY 4.0 licence. You can take the data for one country, for one database, or read it from a simple web address in your own software.</p>
<h2>Data for one country</h2>
<p>Each file brings together every row from every database that concerns the country: its laws, its agreements, its court decisions, coded features and treaty status. JSON keeps the rows grouped by database; the CSV download is a zip with one spreadsheet per database.</p>
<p><label for="od-q">Find a country</label><br><input id="od-q" type="search" placeholder="Type a country name or code" style="font:inherit;padding:8px 10px;width:100%;max-width:360px;box-sizing:border-box;border:1px solid #C8BCB1;border-radius:6px"></p>
<div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;font-size:16px;line-height:1.4" id="od-t">
<thead><tr style="text-align:left;border-bottom:2px solid #C8BCB1"><th scope="col">Country</th><th scope="col">Code</th><th scope="col" style="text-align:right">Rows</th><th scope="col" style="text-align:right">Court decisions</th><th scope="col">Download</th></tr></thead>
<tbody>{rows_html}</tbody></table></div>
<p class="g-note">{len(country_index)} countries and international bodies, {total:,} rows in all. Codes are ISO 3166-1; XA, XF, XI and XM are international and regional courts.</p>
<h2>Data by database</h2>
<p>The same files offered on each database page, as CSV and as JSON. Each database has a codebook.csv that explains its columns and codes.</p>
{ds_html}
<h2>For developers</h2>
<p>The API is a set of static JSON files: read-only, no key, no sign-up, open to any website (CORS). It is rebuilt from the repository each time the data changes.</p>
<ul>
<li><a href="/api/v1/index.json" data-noi18n>/api/v1/index.json</a>: what is available</li>
<li><a href="/api/v1/countries/index.json" data-noi18n>/api/v1/countries/index.json</a>: every country with its row counts</li>
<li><span data-noi18n>/api/v1/countries/&lt;ISO2&gt;.json</span>: all rows for one country, for example <a href="/api/v1/countries/ID.json" data-noi18n>/api/v1/countries/ID.json</a></li>
<li><span data-noi18n>/api/v1/datasets/&lt;database&gt;/&lt;file&gt;.json</span>: one database file, for example <a href="/api/v1/datasets/court-decisions/decisions.json" data-noi18n>/api/v1/datasets/court-decisions/decisions.json</a></li>
</ul>
<pre data-noi18n style="white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,Menlo,Consolas,monospace;background:rgba(255,255,255,.55);border:1px solid #C8BCB1;border-radius:6px;padding:10px 12px">import pandas as pd, requests
d = requests.get("https://theimr.org/api/v1/countries/ID.json").json()
decisions = pd.DataFrame(d["records"]["court-decisions/decisions.csv"])</pre>
<p>The source files, their history and every correction are public on <a href="https://github.com/pranotoiskandar-collab/compmigrationlaw">GitHub</a>. You can propose new rows or corrections there.</p>
<h2>About the records</h2>
<ul>
<li>Every law, instrument and decision has a stable id, which does not change once published.</li>
<li>Dates are written as YYYY-MM-DD (or YYYY when only the year is known).</li>
<li>The column last_checked gives the date IMR last checked or updated each row.</li>
<li>Duplicate entries that were found are merged; the list is in <a href="/court-decisions/data/duplicates.csv">duplicates.csv</a>.</li>
</ul>
<h2>Licence and citation</h2>
<p>CC BY 4.0: you may copy, share and adapt the data, also commercially, if you give credit. Please cite:</p>
<p data-noi18n style="padding:10px 14px;border-left:3px solid #C8BCB1">{e(CITE)}</p>
<script>(function(){{var q=document.getElementById('od-q'),r=[].slice.call(document.querySelectorAll('#od-t tbody tr'));q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase();r.forEach(function(t){{t.hidden=v&&t.getAttribute('data-q').indexOf(v)<0;}});}});}})();</script>
<style>#od-t td,#od-t th{{padding:7px 10px 7px 0;border-bottom:1px solid rgba(120,110,100,.25);vertical-align:top}}</style>
"""
ld = {"@context": "https://schema.org", "@type": "DataCatalog", "name": "Migration Jurisprudence from the South: open data",
      "url": f"{BASE}/open-data/", "description": "Open data from the Institute for Migrant Rights databases on migration and labor law, "
      "court decisions on migrants' rights, and treaty status, downloadable per country and per database as CSV and JSON, with a static read-only API.",
      "license": LICENSE, "isAccessibleForFree": True, "inLanguage": ["en", "id"],
      "creator": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": f"{BASE}/"},
      "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": f"{BASE}/"},
      "dateModified": TODAY,
      "dataset": [{"@type": "Dataset", "name": f"IMR data on {c['name_en']}", "url": f"{BASE}/open-data/#{c['iso2']}",
                   "description": f"All rows on {c['name_en']} from the IMR databases on migration and labor law: laws, agreements, court decisions, coded features and treaty status ({c['records']} rows).",
                   "license": LICENSE, "creator": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": f"{BASE}/"},
                   "spatialCoverage": {"@type": "Place", "name": c["name_en"]},
                   "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": c["json"]},
                                    {"@type": "DataDownload", "encodingFormat": "application/zip", "contentUrl": c["zip"]}]}
                  for c in country_index if c["records"] >= 20]}
make_page("open-data", f"{BASE}/open-data/", "Open data and API",
          "Download the IMR databases on migration law and court decisions per country or per database, as CSV or JSON, or read them through a free static API. CC BY 4.0.",
          body, ld)
print(f"  API: {len(datasets)} databases, {len(country_index)} countries, {total} country rows; /open-data/ written")
