# Migration cases: other Asian destination and origin countries

Court decisions on migration (migrant workers, recruitment for work abroad, trafficking, immigration and deportation, refugees, citizenship) from Singapore, the Philippines and Nepal, collected for IMR's [Court Decisions database](https://theimr.org/court-decisions/) and the farmworker view of the [Migration Law Atlas](https://theimr.org/migration-law/?lens=farm). Kept separate from East Asia (`build/east-asia-cases/`).

Collected 17 November 2026. The cases are search hits, not read judgments: every row still has to be checked against the judgment. The data waits in `data/court-decisions/incoming/other-asia/` for review; this folder holds the script.

## What is where

| File | What it holds |
|---|---|
| `data/court-decisions/incoming/other-asia/migration-cases-all-2026-11-17.csv` | Every case kept: 3,124 (Philippines 2,525, Singapore 489, Nepal 110). Columns: `jurisdiction`, `source`, `court`, `case_no`, `date`, `date_local` (Nepal's Bikram Sambat date), `title`, `url`, `lang`, `matched_terms`, `farm_terms`, `retrieved`. |
| `data/court-decisions/incoming/other-asia/migration-cases-top-courts-2026-11-17.csv` | The 398 proposed for Court Decisions as unchecked candidates (status C), in the `decisions.csv` columns: Philippines 275, Nepal 110, Singapore 13. All are apex courts (see the rules below). |
| `data/court-decisions/incoming/other-asia/raw/` | The search results as exported from each site. `ph_elibrary.csv` has one row per decision with the highest hit count and the search terms that found it; `ph_titles.csv` holds the case titles from the E-Library's monthly lists. |
| `build_candidates.py` | Builds both lists and `imr_candidates.json` (the site's own field names, for `build/east-asia-cases/patch_imr_site.py`). Run `python3 build/other-asia-cases/build_candidates.py` from the repository root. |

## Sources and coverage

| Country | Source | Searched | Notes |
|---|---|---|---|
| Singapore | eLitigation (elitigation.sg), all courts | "Employment of Foreign Manpower Act", "Immigration Act", "foreign domestic worker", "work permit", "migrant worker", "foreign worker", "foreign employee", "special pass", "Prevention of Human Trafficking Act", "Employment Agencies Act", "Employment Claims Act", "banishment" | Full-text search, so many hits mention a term only in passing (for example a drug appeal by a work-permit holder). Only Court of Appeal decisions that hit a statute-specific term, or three or more terms, are proposed for the site. |
| Philippines | Supreme Court E-Library (elibrary.judiciary.gov.ph) | Migrant Workers and Overseas Filipinos Act (RA 8042, RA 10022), illegal recruitment, POEA, OFW, overseas employment, seafarer, Overseas Workers Welfare Administration, Department of Migrant Workers, Anti-Trafficking (RA 9208), trafficking in persons, deportation, Bureau of Immigration | Search results give only the case number and date, so titles and links come from the E-Library's monthly lists; 834 older decisions (mostly before 2000) have no title or link yet. A decision is proposed for the site if a core term occurs at least 30 times in it (the E-Library's hit count) or the title names farm or fishing work. Seafarers' disability and death claims are a large share. |
| Nepal | Nepal Kanoon Patrika (nkp.gov.np), Supreme Court | वैदेशिक रोजगार (foreign employment), वैदेशिक रोजगार ऐन, मानव बेचबिखन (trafficking), शरणार्थी (refugees), नागरिकता (citizenship), अध्यागमन (immigration) | Full-text search. Kept only decisions whose subject line is about migration, plus writ petitions (habeas corpus, certiorari, mandamus) whose parties include the Department of Immigration, the Department of Foreign Employment, refugees or foreigners. Dates are Bikram Sambat; `date` gives the approximate Gregorian year. Names are English labels made from the subject line. |

Not crawled, and why:

| Country | Reason |
|---|---|
| Malaysia | kehakiman.gov.my disallows all bots in robots.txt; the e-filing judgment pages returned errors. |
| India | Indian Kanoon sits behind a Cloudflare bot check (not bypassed). The Supreme Court's own site (scr.sci.gov.in) was not tried yet. |
| Pakistan | supremecourt.gov.pk blocked the browser (Akamai 403). |
| Sri Lanka, Thailand | The Supreme Court judgment sites did not load. |
| Indonesia | Constitutional Court data is already in the imrdata repository; the Supreme Court directory disallows bots. |
| Vietnam, Cambodia, Myanmar, Brunei, Bangladesh | Not tried this round. |
| All | AsianLII and CommonLII disallow AI crawlers in robots.txt, so they were not used. |

robots.txt was checked for every site used on 17 November 2026. The searches ran in the Claude app's browser on a personal computer, one results page at a time with pauses of several seconds. Only listing pages were read; no judgment texts were downloaded.

## Farmworker view

`farm_terms` marks cases whose title names farm, plantation or fishing work. Only 3 do, all in the Philippines; Philippine seafarer cases are marked by topic (`sector` = seafarers) instead. A full-text pass over the judgments is the next step.
