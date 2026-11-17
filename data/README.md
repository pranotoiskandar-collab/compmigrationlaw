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
