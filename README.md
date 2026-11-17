# Comparative migration law: theimr.org website and open data

This repository holds the website of the **Institute for Migrant Rights** ([theimr.org](https://theimr.org)) and every dataset it publishes under *Migration Jurisprudence from the South*. Netlify publishes the site automatically whenever the `main` branch changes.

## What is where

| Folder | What it holds |
|---|---|
| `site/` | The website exactly as published: HTML pages, styles, scripts and images. |
| `data/<database>/` | The downloadable data for each database (CSV and BibTeX). Each folder has a `codebook.csv` that explains every column and code. |
| `data/<database>/incoming/` | New material sent in for review. It is **not** published until an editor merges it into the database. |
| `build/` | The scripts that generated the pages and data. Kept for the record; they were written for the IMR working folder and refer to its paths. |
| `tools/` | `copy_data.py` copies `data/` into the site at publish time; `check_csv.py` checks that every CSV is well formed. |

When Netlify publishes, `data/<database>/<file>` appears at `https://theimr.org/<database>/data/<file>`. For example, `data/court-decisions/decisions.csv` is served at `https://theimr.org/court-decisions/data/decisions.csv`.

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

## Citing the data

Cite the database page on theimr.org and the date you downloaded it, for example: Institute for Migrant Rights, *Court Decisions* (theimr.org/court-decisions/, accessed 17 November 2026). The history of every file is visible on GitHub.

## Adding data

New legal sources from the Middle East, East Asia and other regions go into `data/<database>/incoming/` (for example `data/east-asia/incoming/` or `data/gcc/incoming/`), using the same columns as `data/court-decisions/decisions.csv` where they are court decisions, so rows can move into the database as they are.


See [CONTRIBUTING.md](CONTRIBUTING.md).
