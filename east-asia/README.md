# Migration cases and laws: East Asia

Court decisions on migration (immigration, refugees and non-refoulement, migrant workers, deportation, nationality, trafficking) from Hong Kong, Japan, South Korea and Macau, with the main migration statutes of the region. Collected for IMR's [Court Decisions database](https://theimr.org/court-decisions/) and the farmworker view of the [Migration Law Atlas](https://theimr.org/migration-law/?lens=farm) (Global Farmworker Law).

Collected 17 November 2026. The cases are search hits, not read judgments: every row still has to be checked against the judgment.

## What is here

| File | What it holds |
|---|---|
| `tables/candidates.csv` | Every migration case found, one row per case (see counts below). Columns: `jurisdiction`, `source`, `court`, `case_no`, `date`, `title`, `url`, `lang`, `matched_terms`, `farm_terms`, `retrieved`. |
| `tables/imr_candidates.csv`, `.json` | The subset that goes onto theimr.org as unchecked candidates (status C): 287 cases from the top courts (Supreme Courts and Constitutional Court of Korea and Japan, Courts of Final Appeal of Hong Kong and Macau), plus every farm or fishing case. Two Hong Kong Court of Final Appeal hits that are not about migration are left out (see `scripts/sitefilter.py`). Same columns as IMR's `decisions.csv`; the JSON uses the site's own field names. English names are translations of the court's title, not the parties' names. |
| `tables/decisions.csv` | Cases that have been read and coded (empty for now). Rows start at status S. |
| `tables/legislation.csv` | Migration statutes for KR, JP, TW, HK, MO, MN and CN, with official sources. |
| `tables/raw/` | The search results as exported from each site, before filtering. |
| `keywords.json` | Search terms per jurisdiction in the court's own language. `farm` terms flag farm, livestock and fishing cases. |
| `scripts/build_candidates.py` | Builds `candidates.csv` from `tables/raw/`. |
| `scripts/imr_candidates.py` | Builds the theimr.org subset (uses `sitefilter.py` and `names_en.py`). |
| `scripts/kr_lawgo.py` | Alternative for Korea through the law.go.kr Open API, if an API key is obtained later. |

Run `python3 scripts/build_candidates.py` and then `python3 scripts/imr_candidates.py` to rebuild the tables.

## Sources and coverage

| Jurisdiction | Source | Searched | Notes |
|---|---|---|---|
| South Korea | law.go.kr: precedents and Constitutional Court decisions | 13 migration terms (출입국관리법, 난민, 강제퇴거, 고용허가, 국적법 …) plus targeted searches for foreign farm, livestock and fishing workers | The site searches full text, so hits were filtered by case title. Some Constitutional Court panel decisions have no date in the listing. |
| Japan | courts.go.jp judgment search | 9 terms (出入国管理及び難民認定法, 難民, 退去強制, 在留資格, 技能実習 …) | Intellectual property cases dropped. Farm flags come from titles only. |
| Hong Kong | HKLII | "non-refoulement", "foreign domestic helper", "deportation order", "removal order", "right of abode", "trafficking" | HKLII shows at most 2,500 results per search, so the non-refoulement list holds the most recent 2,500 (from 2021). Many "domestic helper" hits are non-refoulement claims by former helpers. |
| Macau | court.gov.mo | 11 subject terms (居留許可, 驅逐出境, 非本地勞工 …) in the Court of Final Appeal; residence and expulsion only in the Court of Second Instance | Partial: the site's search stopped answering during the Second Instance crawl. |
| Taiwan | Judicial Yuan | not crawled | Bots are disallowed; the open-data bulk files must be downloaded by hand and filtered. |
| Mongolia | shuukh.mn | not crawled | |
| China | China Judgements Online | not crawled | Requires login and forbids scraping. |

robots.txt was checked for every site on 17 November 2026. The sites cannot be reached from the cloud sessions behind this repository, so the searches ran in the Claude app's browser on a personal computer, one results page at a time with pauses of three to five seconds. Only listing pages were read; no judgment texts were downloaded.

## Farmworker view

`farm_terms` marks cases whose title (or targeted search) involves farm, livestock or fishing work. Titles rarely say so, so this flag misses most farm cases; a full-text pass over the judgments is the next step.
