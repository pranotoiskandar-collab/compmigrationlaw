# Source watch

Every Monday at 01:17 UTC, `.github/workflows/source-watch.yml` reads the official sources listed in `sources.json` and looks for court decisions, laws and ratification changes that are new since the week before. It never downloads judgment texts: it reads one listing, search result or feed per source, with a pause of several seconds between requests to the same site, and it does not try to get past bot checks, logins or captchas.

When it finds something, it commits to the branch `source-watch` and opens a pull request called **Source watch: new items to check** (or updates the one already open).

| Path | What it holds |
|---|---|
| `sources.json` | The sources: official court, legislature, ministry, UN and ILO sites only |
| `found/new-<date>.csv` | New items: one row per decision, law or ratification change. These are search hits, not read documents. |
| `reports/<date>.md`, `reports/latest.md` | What was read, what is new, and which sources a person has to check by hand |
| `state/<source>.txt` | Everything the watch has already seen on each source (so nothing is reported twice) |
| `state/_status.json` | Whether each source could be read, and since when |

## What happens next

1. An editor or research assistant reads each row in `found/`, opens the official link, and confirms the details.
2. Confirmed rows go into the right `data/<database>/incoming/` file, in the columns described in [CONTRIBUTING.md](../CONTRIBUTING.md).
3. Merging the source-watch pull request records what was seen. If it is left open, next week's items are added to it.

The weekly report's **Work for a person** list is copied into the follow-up list for IMR's research assistant (new items only, so nothing is listed twice).

## Adding a source

Add an entry to `sources.json`. A pull request that changes the file tries every source once and shows the result in its checks, without saving anything.

| Field | Meaning |
|---|---|
| `id` | Short name, letters and hyphens |
| `country` | ISO code; `XR` for regional and international bodies |
| `kind` | `courts`, `laws` or `ratifications` |
| `name`, `operator` | What the source is and who runs it |
| `home` | Page a person opens to check the source by hand |
| `listing` | The page to read: a list, search result or feed, newest first. `{year}` and `{month}` (Jan to Dec) are filled with this month and last month. Can be a list of addresses. |
| `mode` | `links` (links on an HTML page whose address matches `item`), `feed` (RSS or Atom), `json` (with `items_path`, `url_field`, `title_field`, `date_field`, `url_prefix`), `rows` (table rows matching `item`, for ratification tables), `xml-prec` (law.go.kr Open API) |
| `item` | Regular expression for item links (`links`) or rows (`rows`) |
| `keywords` | Optional. Keep only items whose title or link contains one of these words (any language). Leave it out for sources that are already about migration. |
| `needs_secret` | Name of a repository secret the source needs (an API key) |

The first run of a new source records what it lists now and reports nothing, so the list only shows what appears afterwards.

## Korean precedents (law.go.kr)

The Korean source uses the government's Open API, which needs a free key (the "OC" value) from [open.law.go.kr](https://open.law.go.kr/). Add it in the repository settings, **Secrets and variables → Actions → New repository secret**, named `LAWGO_OC`. Until then the report lists the source as waiting for a key.
