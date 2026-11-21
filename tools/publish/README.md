# Publish-time steps

`tools/copy_data.py` (the Netlify build command) runs every `NN_*.py` file in this
folder, in number order, after copying `data/` into `site/`. Each step edits only
the build copy that Netlify publishes; nothing is committed. That keeps the source
pages free of generated additions, so page rebuilds never clash with them.

| Step | What it adds to the published site |
|---|---|
| `10_duplicates.py` | Removes pages of merged duplicate decisions (`data/court-decisions/duplicates.csv`) and redirects their addresses to the kept record |
| `20_open_api.py` | `/api/v1/` static JSON + CSV per database and per country, and the `/open-data/` page (EN/ID) |
| `30_structured_data.py` | schema.org markup for Google Dataset Search (Dataset, DataCatalog, DataDownload), `Legislation` lists on country pages, richer markup and a "Last checked" line on each decision page, and Google Scholar `citation_*` tags on the working-paper pages, and one Organization block for IMR with its founding year (2007) and `sameAs` links to Wikidata, ROR, Zenodo and GitHub |
| `35_founded_footer.py` | Adds "Founded in Cianjur in 2007" under "and IMR Press" in every page footer |
| `40_indonesian.py` | Merges `id-extra.json` into `/assets/lang.js` (more Indonesian for decision pages and other gaps) |
| `50_analytics.py` | Makes sure every page, including new ones, carries the GoatCounter counter |
| `60_home_cases.py` | Redraws the homepage map of court decisions by country (and the split by court level and outcome) from `data/court-decisions/decisions.csv`, so the homepage numbers always match the data |
| `90_sitemap.py` | Adds the new pages to `sitemap.xml` and drops redirected ones |

Run locally to preview:  `python3 tools/copy_data.py && python3 -m http.server -d site`
(then `git checkout site && git clean -fd site` to undo the build changes).

`common.py` holds shared helpers; `countries.json` is the ISO 3166 table
(English and Indonesian names) generated once from the `pycountry` package.
