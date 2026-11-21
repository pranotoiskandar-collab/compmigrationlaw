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

## South and Southeast Asia round (2026-11-21)

- `court-decisions-2026-11-21.csv`: 378 decisions. 376 are from the Supreme Court of the Philippines (E-Library) and 2 are High Court Division writs from Bangladesh (Umrah pilgrims overstaying in Saudi Arabia).
- Philippine rows: candidates from `migration-cases-all-2026-11-17.csv` that were not yet on the site. Each E-Library page was opened and keyword counts were taken (seafarer, disability, death, trafficking, illegal recruitment, dismissal, wages). A case was kept when the counts were strong: 304 seafarer disability claims, 42 seafarer death claims, 21 trafficking, 7 illegal recruitment, 3 others. 24 more were dropped because their G.R. number is already on the site. The judgments were not read: every row is `Unverified` and the topic in `note` is a guess from the counts. About 180 candidates were not screened yet.
- Bangladesh rows: from the Supreme Court website's judgment notes, years 2000 to 2026.
