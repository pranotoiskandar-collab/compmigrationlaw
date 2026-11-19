# Comparative migration law: theimr.org website and open data

This repository holds the website of the **Institute for Migrant Rights** ([theimr.org](https://theimr.org)) and every dataset it publishes under *Migration Jurisprudence from the South*. Netlify publishes the site automatically whenever the `main` branch changes.

## What is where

| Folder | What it holds |
|---|---|
| `site/` | The website exactly as published: HTML pages, styles, scripts and images. |
| `data/<database>/` | The downloadable data for each database (CSV and BibTeX). Each folder has a `codebook.csv` that explains every column and code. |
| `data/<database>/incoming/` | New material sent in for review. Not offered as a download until an editor merges it into the database. |
| `data/<database>/sources/` | The working files each database was built from: raw portal listings, verification worksheets, ratification extracts and editors' notes. Kept for transparency; not offered as downloads on the site. |
| `build/` | The scripts that generated the pages and data. Kept for the record; they were written for the IMR working folder and refer to its paths. |
| `tools/` | `copy_data.py` copies `data/` into the site at publish time; `press_subdomain.py` prepares the IMR Press pages for press.theimr.org; `check_csv.py` checks that every CSV is well formed; `cite_blocks.py` writes the "How to cite" block on each database page from `citation.json`. |

When Netlify publishes, `data/<database>/<file>` appears at `https://theimr.org/<database>/data/<file>`. For example, `data/court-decisions/decisions.csv` is served at `https://theimr.org/court-decisions/data/decisions.csv`.

## IMR Press (press.theimr.org)

The book pages are kept in `site/press/` like any other page. At publish time `tools/press_subdomain.py` points their links, styles and images at theimr.org, and the top rules in `site/_redirects` serve them at `https://press.theimr.org/` and send old `theimr.org/press/...` links there.

## Databases

| Folder | Page |
|---|---|
| `data/migration-law/` | Migration law across tiers (global, regional, national) |
| `data/atlas/` | Farmworker Norms Atlas (farmworker view of the migration-law data) |
| `data/court-decisions/` | Court Decisions |
| `data/gcc/` | Gulf States |
| `data/east-asia/` | East Asia |
| `data/southeast-asia/` | Southeast Asia |
| `data/countries-of-origin/` | Countries of origin |
| `data/domestic-workers/` | Migrant domestic workers |
| `data/government-hate-speech/` | Government hate speech, with the elections comparison in `elections/` |
| `data/africa/` | African migration laws and court decisions (incoming and sources only; decisions are shown in Court Decisions) |

## Licence

Data and site text: CC BY 4.0. See [LICENSE.md](LICENSE.md) for the details and the exceptions.

## Citing the data

Every database page on theimr.org has a "How to cite" block with a citation, BibTeX and the database's version number. To cite the collection as a whole:

> Institute for Migrant Rights (2026). *Migration Jurisprudence from the South: databases of migration and labor law* [Data set]. https://theimr.org/databases/

Each GitHub release is archived on Zenodo with a DOI; see [docs/RELEASING.md](docs/RELEASING.md) and [CHANGELOG.md](CHANGELOG.md). GitHub's "Cite this repository" button reads [CITATION.cff](CITATION.cff).

## Adding data

New legal sources from the Middle East, East Asia and other regions go into `data/<database>/incoming/` (for example `data/east-asia/incoming/` or `data/gcc/incoming/`), using the same columns as `data/court-decisions/decisions.csv` where they are court decisions, so rows can move into the database as they are.


See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licences of third-party material

Files in `sources/` that come from other datasets keep their own terms. The V-Dem and V-Party extracts in `data/government-hate-speech/elections/sources/` are under CC BY-SA 4.0 (cite V-Dem). ODIHR hate-crime figures come from hatecrime.osce.org. Books, articles and agency reports used as sources (for example the ILO FAIRWAY country profiles) are cited but not copied into this repository.
