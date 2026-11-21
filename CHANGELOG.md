# Releases

Each release of this repository is archived on Zenodo with its own DOI (see
[docs/RELEASING.md](docs/RELEASING.md)). Release tags use the year and month:
`v2026.11` is the November 2026 release; `v2026.11.1` corrects it.

The databases keep their own version numbers. Each release lists them, so a
reader can match a citation such as "Court Decisions, version 0.1" to the
archived files.

## v2026.11.1 (20 November 2026)

Zenodo: https://doi.org/10.5281/zenodo.24389324 (all versions). The DOI of this release is added once Zenodo has archived it.

| Database | Page | Version | Last updated |
|---|---|---|---|
| Migration Law Atlas (with farmworker view) | /migration-law/ | version of 20 November 2026 | 2026-11-20 |
| National migration laws (new table, part of the Atlas) | /migration-law/national-laws/ | version of 20 November 2026 | 2026-11-20 |
| Court Decisions | /court-decisions/ | 0.2 | 2026-11-20 |
| Migrant Workers in the Gulf States | /gcc/ | 1.4 | 2026-11-20 |
| Migrant Workers in East Asia | /east-asia/ | 1.5 | 2026-11-13 |
| Migrant Workers in Southeast Asia | /southeast-asia/ | 1.0 | 2026-11-13 |
| Countries of Origin | /countries-of-origin/ | 1.3 | 2026-11-20 |
| Migrant Domestic Workers | /domestic-workers/ | 1.3 | 2026-11-11 |
| Government Hate Speech: country data | /government-hate-speech/ | version of 31 October 2026 | 2026-10-31 |
| Hate Speech, Voting and the Legal Protection of Non-Citizens | /government-hate-speech/elections/ | 1.0 | 2026-10-31 |

- 20 November 2026: every incoming row waiting in `data/*/incoming/` was published.
  - Court Decisions: 1,540 → 1,912 decisions (372 new, all "Unverified: unchecked candidate"): Supreme Court of Chile 162, Nauru 144 (PacLII, a secondary source), Philippines unpaid wages 32, Fiji 12, UN treaty bodies 15, East African Court of Justice 1, Australia 3, New Zealand 2, Vanuatu 1.
  - New table `data/migration-law/national-laws.csv` (133 national laws of 25 states without a regional page), shown at /migration-law/national-laws/.
  - Migration Law Atlas: 14 regional instruments added (97 → 111 norms).
  - Countries of Origin: 8 laws added (44 → 52), 9 links to the official text. Gulf States: 5 Qatar labour agreements added, 15 official ratification-decree links.

## v2026.11 (20 November 2026)

Zenodo: https://doi.org/10.5281/zenodo.24389325 (this release); https://doi.org/10.5281/zenodo.24389324 (all versions).

| Database | Page | Version | Last updated |
|---|---|---|---|
| Migration Law Atlas (with farmworker view) | /migration-law/ | version of 11 November 2026 | 2026-11-11 |
| Court Decisions | /court-decisions/ | 0.1 | 2026-11-01 |
| Migrant Workers in the Gulf States | /gcc/ | 1.3.1 | 2026-11-12 |
| Migrant Workers in East Asia | /east-asia/ | 1.5 | 2026-11-13 |
| Migrant Workers in Southeast Asia | /southeast-asia/ | 1.0 | 2026-11-13 |
| Countries of Origin | /countries-of-origin/ | 1.2 | 2026-11-11 |
| Migrant Domestic Workers | /domestic-workers/ | 1.3 | 2026-11-11 |
| Government Hate Speech: country data | /government-hate-speech/ | version of 31 October 2026 | 2026-10-31 |
| Hate Speech, Voting and the Legal Protection of Non-Citizens | /government-hate-speech/elections/ | 1.0 | 2026-10-31 |

First archived release. Adds `CITATION.cff`, `.zenodo.json` and a "How to
cite" block on every database page.
