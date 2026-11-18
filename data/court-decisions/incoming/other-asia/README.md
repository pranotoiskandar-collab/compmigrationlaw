# Other Asia: incoming migration cases

Migration cases from Singapore, the Philippines and Nepal, waiting for review before they are merged into the Court Decisions database. They are kept apart from the East Asia material.

- `migration-cases-all-2026-11-17.csv`: 3,124 cases found by keyword search on the courts' own sites and not yet read (Philippines 2,525, Singapore 489, Nepal 110).
- `migration-cases-top-courts-2026-11-17.csv`: the 398 of those proposed as unchecked candidates (status C), in the `decisions.csv` columns.
- `raw/`: the search results as exported from each site.

How they were collected, what was left out and why, and the script that rebuilds them are in [build/other-asia-cases/](../../../../build/other-asia-cases/README.md).

## Unpaid wages, Philippines (2026-11-18)

- `unpaid-wages-ph-2026-11-18.csv`: 32 Supreme Court of the Philippines decisions (1996-2021) where an overseas Filipino worker's claim for unpaid wages, salaries for the unexpired portion of the contract, salary differentials or overtime pay is at issue. Before this the site had only 12 origin-state decisions on unpaid wages.
- How they were found: 150 Supreme Court labour cases (NLRC or Court of Appeals in the title) from `migration-cases-all-2026-11-17.csv` that are not yet in `decisions.csv`. Each page on the Court's E-Library was opened and searched for wage terms and overseas-work terms. 37 matched strongly; 5 were dropped (mainly about placement fees, already covered by the recruitment cases, or death benefits).
- Every row is `Unverified`. The `topic_first_read` line was written from the facts and dispositive part, not from an official summary. Holdings, outcome and Indonesian summaries still need a reader before the rows go into `decisions.csv`.
- Links are to the official Supreme Court E-Library (`elibrary.judiciary.gov.ph`).
