# East Asia: incoming material

New East Asia material waits here for review before it is merged into the East Asia and Court Decisions databases.

- `judgments-jp-kr-2026-11-17.csv`: 36 judgments (20 Japan, 16 Korea) on migrant workers, found on the official court sites (courts.go.jp for Japan, law.go.kr for Korea). 33 are new to theimr.org; 3 are already listed and need their case numbers or lower-court instances added. Columns are described in [CONTRIBUTING.md](../../../CONTRIBUTING.md).
- `migration-cases-all-2026-11-17.csv`: 6,340 migration cases (immigration, refugees and non-refoulement, migrant workers, deportation, nationality, trafficking) from Hong Kong (HKLII), Japan (courts.go.jp), Korea (law.go.kr) and Macau (court.gov.mo), found by keyword search and not yet read.
- `migration-cases-top-courts-2026-11-17.csv`: the 287 of those proposed for the Court Decisions database as unchecked candidates (top courts plus farm and fishing cases), in the `decisions.csv` columns. Three of them (2010Du6496, 2018Du66869, 2018Do3690) are also in `judgments-jp-kr-2026-11-17.csv`.
- `migration-statutes-2026-11-17.csv`: 31 migration statutes for Korea, Japan, Taiwan, Hong Kong, Macau, Mongolia and China.
- `raw/`: the search results as exported from each court site.

How these were collected, and the scripts that rebuild them, are in [build/east-asia-cases/](../../../build/east-asia-cases/README.md).

Further East Asia laws, decisions and corrections from other projects go in this folder as new CSV files.
