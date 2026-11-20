# Data folders

Each folder is one database or region. Inside it:

- the published files (CSV, BibTeX, JSON), served on theimr.org at `/<folder>/data/<file>`;
- `codebook.csv`, which explains the columns and codes;
- `incoming/`, new rows waiting for review (see `../CONTRIBUTING.md`);
- `sources/`, the working files the database was built from.

| Folder | Region or theme | sources/ holds |
|---|---|---|
| `migration-law/`, `atlas/` | Global, regional and national migration norms; farmworker view | NORMLEX ratification extracts, country indicators, notes on farm conventions |
| `court-decisions/` | Court decisions from every region | verification worksheet, links to check, national court repositories registry, databases for research assistants |
| `gcc/` | Gulf States | official portal listings (2026-11-17), notes on law changes |
| `east-asia/` | Taiwan, South Korea, Japan, Hong Kong (plus Macau, Mongolia, China in incoming/) | official-text checks of cells and laws (2026-11-13) |
| `southeast-asia/` | Thailand, Malaysia, Singapore, Brunei and origin states | cell, law and coding checks, editor questions |
| `africa/` | African states and regional bodies | official portal listings (2026-11-17) |
| `countries-of-origin/` | Origin states | |
| `domestic-workers/` | Migrant domestic workers | list of cited documents (not copied) |
| `government-hate-speech/` | Government hate speech; `elections/` for votes and non-citizens | ODIHR, V-Dem and V-Party extracts |

## Columns every record file shares

Since 2026-11-19 (see `build/records-cleanup/clean.py`):

- **`id`**: a stable identifier for the row, unique within the file, in lower case with hyphens. Laws and instruments use `<state>-<year>-<short title>` (for example `sa-1992-basic-law-of-governance`), with `nd` when no year is recorded. Court decisions keep their existing ids, which are also their web addresses (`/court-decisions/d/<id>/`). Do not change an id once published: other sites and citations point to it.
- **`last_checked`**: the date (`YYYY-MM-DD`) the row was last checked or updated by IMR. It is the check date written in the row if there is one (`checked_official_text`); otherwise the date the row last changed in this repository; for rows unchanged since the first import, the date the database version was released (or `coded`, if earlier). When you check a row against its official source, set this to that day.
- **Dates** are ISO 8601: `YYYY-MM-DD`, or `YYYY-MM` / `YYYY` when only that much is known. A few text columns (for example `in_force` in `gcc/frameworks.csv`, or `date` in `court-decisions/timeline.csv` for events like "later") keep words where no date exists.
- Files are UTF-8 **without** a byte-order mark.

Removed duplicates are listed in `court-decisions/duplicates.csv` with the record they were merged into; the old web address redirects to the kept one.

The same rows are also published as JSON and per-country files: see `/open-data/` on the site and `site/api/README` once published.
