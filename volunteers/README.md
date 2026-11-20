# Volunteer starter kit

Welcome, and thank you. IMR (the Institute for Migrant Rights) is a small team, so this kit is written to let you start on your own. Read this page once (about ten minutes), pick a task pack, and send us your first result.

*Bahasa Indonesia: [README.id.md](README.id.md).*

## How it works

1. **Sign up** at [theimr.org/volunteer](https://theimr.org/volunteer/), or write to secretariat@theimr.org with the subject `Volunteer: [language or skill]`.
2. **We reply with a first task** from one of the four packs below. Each first task is small, so we can see how you work and you can see whether you like it.
3. **You send the result** the way the pack says: a spreadsheet by email, a file in the shared Drive folder, or a pull request on GitHub.
4. **An editor checks it** and either publishes it or writes back with questions. Then you can take a bigger task.

## Ground rules

- **You will never see Legal Clinic submissions**, or any personal information about people who ask IMR for help. No volunteer gets access to the Clinic inbox, the Netlify form dashboard or the secretariat mailbox. If you come across personal information by accident, stop, close it, and tell us.
- **No legal advice.** If someone asks you for help with their own case, point them to [the Legal Clinic](https://theimr.org/legal-clinic/) or [free legal help near them](https://theimr.org/legal-help/).
- **Official sources first.** Every law or judgment needs a link to the official text (court, legislature, ministry, ILO, UN). A news report or NGO page can lead you there, but on its own it counts as *secondary*, and you must say so.
- **Say what you checked.** Write the date you opened the source, and mark anything you are unsure of. "I could not find it" is a useful answer.
- **Credit.** With your permission, contributors are named on the website and in the change log when their work is published.
- **Speaking for IMR.** Please do not speak to the press or post on social media in IMR's name. Sharing our pages is welcome.

## The four task packs

Pick the pack that matches what you signed up for. The time shown is for the first task.

### Pack 1. Spread and spot (anyone, about 30 minutes)

| First task | What to send |
|---|---|
| **Broken link hunt.** Open ten pages on theimr.org from the [Court Decisions list](https://theimr.org/court-decisions/all/) and click the "official source" link on each. | A list of the links that do not open, or open the wrong document, with the page address. Email it to us. |
| **News spotter.** Search the news in a language you read for a new law, regulation or court ruling about migrant workers from the last three months. | One line per item: country, what changed, date, the news link and, if you can find it, the official link. |
| **Share a page** with a group that could use it (a union, a student law clinic, a community group). | Tell us where you shared it, so we know who reads us. |

### Pack 2. Translate and review (fluent speakers, 1 to 2 hours)

The site has English and Indonesian today. The Legal Clinic also runs in Arabic, Bengali, Dari, Nepali, Tagalog and Vietnamese, but those translations have **not yet been checked by a native speaker**. That check is the most useful first task.

1. Ask us for the review spreadsheet in your language. It lists every sentence with the English and the current translation.
2. For each row, choose OK or Fix in the **Check** column, and write your wording in **Your correction**.
3. Keep the words simple. Many readers have limited literacy and read on a phone.
4. A second speaker checks your corrections before they go live. You may be asked to check someone else's work in return.

Starting a **new language** (Spanish, Hindi, Urdu, Chinese, Bengali, Nepali, Vietnamese, or one we have not listed)? Use [translation-memory-en-id.csv](translation-memory-en-id.csv): it has every sentence on the site in English, with the reviewed Indonesian beside it. Add a column for your language.

**Fixed terms.** [glossary-en-id.csv](glossary-en-id.csv) lists the terms our Indonesian editors have settled, with notes on why. The `status` column says `fixed` (always use it), `preferred` (use unless the context needs otherwise), `style` (general wording rules) or `open` (not decided yet: ask). Translators of other languages: the notes explain which English terms are sensitive. For example, the Clinic helps people prepare a *rights communication*, never a "complaint".

### Pack 3. Legal research (law students and lawyers, 2 to 4 hours)

Most entries in our Court Decisions database were collected from reports and still need someone to find and read the official judgment.

| First task | What to send |
|---|---|
| **Confirm one decision.** We send you one row from the verification worksheet: the case name, the court, the date and what we say it decided. Find the judgment on the court's own website, read it, and tick each column: citation, date, type of case, holding, outcome. | The filled row, plus the official link. Save the judgment PDF in the shared Drive folder, named `COUNTRY_Court_YYYY-MM-DD_Number.pdf`. |
| **Find a missing official link.** We send you up to five entries whose source is a search page or a news report. | The direct link to the official text, or a note on why there isn't one (for example, the court does not publish online). |
| **Check a law.** Pick a law in [`data/<database>/`](../data) that has no `checked_on` date. Open the official text and confirm the number, adoption date and whether it covers farm or domestic work. | The corrected row. See the column list in [CONTRIBUTING.md](../CONTRIBUTING.md). |

Law students who need academic credit or a supervisor's letter: tell us at sign-up. We prefer to work with a campus clinic or a named supervisor.

### Pack 4. Data and code (data science, statistics, programming)

| First task | Skills |
|---|---|
| **Second coding (inter-coder reliability).** The East Asia, Southeast Asia and Countries of Origin pages promise a second, independent coding of a sample of our cells, with Cohen's kappa. We send you a worksheet of about 50 cells. For each, you read the statutes listed and give a code of 0, 1 or 2 using the definitions on the sheet. **Do not look at our codes on the website first**: the point is that you code blind. We compute kappa with [`build/second-coding/kappa.py`](../build/second-coding/). | Careful reading; legal background helps. About 4 to 6 hours. |
| **Data checks.** Run `python3 tools/check_csv.py` and suggest further checks: duplicate cases, dates in the future, country codes that do not match the court, links that return errors. | Python. Open a pull request. |
| **Court website scraper.** Write a small, polite scraper (respect robots.txt, one request every few seconds) that lists new judgments on one official court portal that mention migrant workers. | Python. Output a CSV in the format in CONTRIBUTING.md. |
| **Statistics.** Reproduce a figure from one of our data pages from the CSV downloads, and tell us if you get a different number. | R, Python or Stata. |

Code and data go in through **pull requests** on GitHub. Read [CONTRIBUTING.md](../CONTRIBUTING.md) before your first one. New rows go in `data/<database>/incoming/`, never straight into the published files.

## Where things live

| What | Where | Who can see it |
|---|---|---|
| Website and published data | This GitHub repository | Everyone |
| Documents you find (judgment PDFs, gazettes) | Shared Drive folder for research assistants (link sent with your first task) | Volunteers working on research |
| Review spreadsheets and second-coding worksheets | Sent to you by email | You and the editors |
| Legal Clinic submissions | Not shared with volunteers | IMR staff only |

## Questions

Write to secretariat@theimr.org. Put `Volunteer:` at the start of the subject so we see it quickly.
