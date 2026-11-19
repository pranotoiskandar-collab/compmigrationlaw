# Monthly database update ("What's new in the databases")

A short monthly email and web page listing the court decisions, laws and instruments
added to the databases in the past month, in English and Indonesian. It is written
automatically from the history of `data/` in this repository, so no one has to draft it.

## How it runs each month

1. **1st of the month, 10:00 Jakarta time.** The GitHub Action *Monthly database update*
   runs `tools/digest/digest.py` for the month just ended and opens a pull request with:
   - `site/updates/<YYYY-MM>/index.html`: the issue as a web page (EN/ID switch)
   - `site/updates/index.html`, `site/updates/feed.xml`: the list of issues and an RSS feed
   - `newsletter/<YYYY-MM>/email.html`, `email.txt`, `subject.txt`: the email
2. **An editor merges the pull request.** Netlify publishes the page.
3. **If Buttondown is connected**, the Action *Put the monthly email in Buttondown* creates
   a **draft** from `email.html`. Someone opens Buttondown, reads it and presses **Send**.
   Nothing is ever sent automatically.

An editor may add a short note for an issue in `tools/digest/notes/<YYYY-MM>.json`:
`{"en": "One or two sentences.", "id": "Satu atau dua kalimat."}`, then re-run the Action.

## What counts as "new"

The script compares the published tables (never `incoming/` or `sources/`) at the last
commit before the month began with the last commit before it ended:

| Table | A row is new when this is new |
|---|---|
| `court-decisions/decisions.csv` | `id` (and an entry counts as "checked further" when its status moves C → S → P) |
| `migration-law/migration-norms.csv` | name + citation |
| `gcc/`, `east-asia/`, `southeast-asia/` `domestic-laws.csv`, `countries-of-origin/laws-policies.csv` | country + title |
| `domestic-workers/instruments.csv` | `id` |
| `*/developments.csv` | date + country + text |
| `*/incoming/*.csv` (not `raw/`) | new or changed files, counted only |

The wording is descriptive throughout: no rankings and no judgments about any state.

## Sign-up

`digest.py` also writes a small sign-up band (EN/ID) above the footer of the database
pages, and a fuller form on `/updates/`. While `buttondown_username` in `config.json`
is empty, the forms are Netlify forms (`database-updates`, `database-updates-id`) and
the addresses collect in Netlify under **Forms**. Once Buttondown is set up, put its
username in `config.json` and run `python3 tools/digest/digest.py --month <latest>`:
the forms then post to Buttondown, which handles confirmation and unsubscribing.

Only people who sign up themselves receive the email. Do not add scraped addresses.

## One-time setup

1. Create a free Buttondown account (buttondown.com) with secretariat@theimr.org.
   Set the sender name to *Institute for Migrant Rights* and turn on double opt-in.
2. Put the Buttondown username in `tools/digest/config.json` (`buttondown_username`).
3. Buttondown → Settings → API: copy the API key. In GitHub, this repository →
   Settings → Secrets and variables → Actions → New repository secret:
   name `BUTTONDOWN_API_KEY`, value the key.
4. GitHub → Settings → Actions → General → Workflow permissions: tick
   **Allow GitHub Actions to create and approve pull requests** (needed for step 1 above).
5. Import anyone who already signed up through the Netlify forms (Netlify → Forms →
   download CSV → Buttondown → Subscribers → Import).

## Running it by hand

```
python3 tools/digest/digest.py --month 2026-11
```
