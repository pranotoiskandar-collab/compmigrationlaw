# Plain Indonesian summaries of the laws (`laws-id.csv`)

Two lines in simple Indonesian for every law and instrument in the databases, for migrant workers and their families.
They are shown on [/laws/](https://theimr.org/laws/), in the comparison tool and on the timeline.

- **They are summaries, not legal advice.** Each page says so and links to the official text and to free legal help.
- **How they were written (19 November 2026):** drafted with AI from the notes already in each database row (the
  coverage, topic or provisions column), not from a new reading of the legal text. Line 1 (kind of instrument, country,
  year) is generated from the row; line 2 was written for each row separately.
- **`check = yes` (126 rows):** the database row itself says something is unverified, or the official text has not
  been read yet (for those rows line 2 comes from the title only). A person should compare these with the official
  text first.
- **When someone checks a summary**, write their name or initials in `reviewed_by` and correct the lines if needed.
- **New laws:** `python3 tools/features/build_data.py` prints how many laws have no summary yet. Add a row here with the
  same `key` as in `site/features/laws.json`.
