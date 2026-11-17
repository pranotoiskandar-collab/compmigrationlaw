# Adding data

Other IMR projects and researchers add data through **pull requests**. Nothing reaches theimr.org until an editor has looked at it and merged it.

## The short version

1. Put new rows in a CSV file in `data/<database>/incoming/`, named `<what>-<YYYY-MM-DD>.csv` (for example `data/east-asia/incoming/judgments-jp-kr-2026-11-17.csv`).
2. Open a pull request that says where the rows came from and how they were checked.
3. An automatic check makes sure the CSV can be read. An editor reviews the content, then merges it into the database files and rebuilds the page.

Corrections to a published file (`data/<database>/*.csv`) are welcome too. Edit the file directly in the pull request and give the source for each change. Note that these files go live as soon as the pull request is merged.

## File rules

- **CSV, UTF-8, comma separated**, with one header row. Every row has the same number of columns as the header.
- **Column names** in lowercase with underscores (`case_no`, `official_link`).
- **Dates** as `YYYY-MM-DD`. If only the year is known, write `YYYY`.
- **Countries** as two-letter ISO 3166 codes (`JP`, `KR`, `AE`).
- **One source link per row**, pointing to the official text (court, legislature, ministry, ILO, UN). Secondary sources are allowed only when no official one exists; say so in a `note` column.
- Use the column names and codes in that database's `codebook.csv` wherever they fit. New columns are fine in `incoming/`; explain them in the pull request.
- No personal data about workers or litigants beyond what the official source already publishes, and no passwords, keys or private contact details.

## Columns for incoming court decisions

These match the East Asia starting file and suit any country:

| Column | Meaning |
|---|---|
| `country` | ISO code of the state whose court decided |
| `court` | Court name in English, with branch |
| `date` | Date of judgment, `YYYY-MM-DD` |
| `case_no` | Case number as the court writes it |
| `topic_from_official_summary` | One line, taken from the court's own summary |
| `official_link` | Link to the judgment on the court's site |
| `site_status` | `new`, or `ON SITE` with a note if theimr.org already lists it |

## Columns for incoming laws and regulations

| Column | Meaning |
|---|---|
| `country` | ISO code |
| `title` | Official English title, or a translation in brackets |
| `number` | Official number (for example `Federal Decree-Law No. 33 of 2021`) |
| `adopted` | `YYYY-MM-DD` |
| `in_force` | `YYYY-MM-DD`, or blank if unknown |
| `amended` | Latest amendment date, if any |
| `covers_farm_or_domestic_work` | `yes`, `no`, or `excluded` (the law names them as outside its scope) |
| `official_link` | Link to the official text |
| `checked_on` | Date someone opened the official link and confirmed the details |
| `note` | Anything an editor should know |

## Working with git

You can do all of this in the browser: open the folder on GitHub, choose **Add file → Upload files**, and select **Create a new branch and start a pull request**.
