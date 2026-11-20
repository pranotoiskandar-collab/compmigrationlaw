# Pacific: incoming

Crawl of 2026-11-20. Covers the Pacific Island countries (Fiji, Papua New Guinea, Samoa, Tonga, Vanuatu, Solomon Islands, Kiribati, Tuvalu, Nauru) and the two destination schemes that matter most for them: Australia's Pacific Australia Labour Mobility (PALM) scheme and New Zealand's Recognised Seasonal Employer (RSE) scheme. All rows are Unverified until an editor places them.

## Files

| File | Rows | What it holds |
| --- | --- | --- |
| `laws-2026-11-20.csv` | 45 | 34 Pacific Island laws (immigration, work permits, employment, labour placement, refugees), 8 Australian instruments (Migration Act amendments, Migration Regulations, Pacific Engagement Visa, Falepili Union visa, Fair Work Act, Modern Slavery Act, PALM Deed) and 3 New Zealand instruments (Immigration Act 2009, Worker Protection Act 2023, RSE instructions) |
| `court-decisions-2026-11-20.csv` | 163 | 145 Nauru refugee appeals (Supreme Court, Court of Appeal, High Court of Australia appeals from Nauru), 12 Fiji cases (trafficking, immigration detention and removal, work permits), 1 Vanuatu trafficking case, 2 NZ Employment Court rulings on RSE workers (Soapi v Pick Hawkes Bay), 3 Australian Fair Work Ombudsman cases on PALM/seasonal workers |

## Sources and how to read `source_tier`

- **Pacific Island laws and decisions** link to PacLII (Pacific Islands Legal Information Institute, University of the South Pacific). PacLII is **not a government site**; it is a secondary source, flagged in every row. Most Pacific governments publish no searchable database of their own. Where an official site exists (Fiji laws.gov.fj, Samoa legislation.gov.ws) it could not be reached; see `unreachable-portals-2026-11-20.md`.
- **Australia** rows link to the Federal Register of Legislation (official) and palmscheme.gov.au (official guidance).
- **New Zealand** rows link to legislation.govt.nz (official) and the Immigration New Zealand Operational Manual (official guidance).
- **FWO cases** link to the Fair Work Ombudsman media releases (official guidance), because the judgment citations were not found yet. `case_no` says "[citation to be added]".

## Notes for editors

- The 145 Nauru appeals were taken from the PacLII case lists by title. `checked_on` is blank for them: they were not opened one by one. The topic is inferred from the court list; the issue and outcome still need reading (follow-up doc).
- Appellant names in the Nauru cases are anonymised codes as published by the court. Keep them as they are.
- Rows that were opened carry `checked_on` 2026-11-20 and a note saying so.
- Some years in the Pacific consolidations are not in the index; the note says "check" where that applies.
