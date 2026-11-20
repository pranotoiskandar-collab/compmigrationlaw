# Site checks

Every pull request, and every push to `main`, runs `.github/workflows/site-checks.yml`. It builds the site the way Netlify does and then checks it. **A pull request fails only for problems it adds.** The same checks run on the branch it would merge into, and anything already there is counted but does not hold the pull request up.

| Check | Fails the pull request when it adds… | Only a note when… |
|---|---|---|
| Build | `tools/copy_data.py` or `tools/press_subdomain.py` stops with an error, or a Python script under `tools/` does not compile | |
| Data files (`data/**/*.csv`) | a file that is not UTF-8, a row with more or fewer columns than the header, a repeated column name or `id`; outside `raw/` and `sources/` folders also a date not in `YYYY-MM-DD` (or `YYYY`) form, an impossible or future date, a country that is not a two-letter ISO code, a link in `official_link`/`url` that is not a full `https://` address | a cell holds an email address |
| Links | a link, image, script or stylesheet on a page that points to a page or file on theimr.org or press.theimr.org that does not exist; the same for URLs in `sitemap.xml`, `llms.txt`, `robots.txt`, for file paths named in the site's scripts, and for the local targets in `_redirects` | a link to a part of a page (`#id`) that is not there |
| Site addresses | `_redirects` sends visitors to a theimr.org address that has no DNS record or does not answer (this is what took the press pages offline on 19 November 2026). This is checked even if it was already broken. | |
| English and Indonesian | English menu, heading, button, label or table-header text with no Indonesian entry in `site/assets/lang.js` or the page's own `*-i18n.js`, either in the HTML or written by the page's scripts | other untranslated text, case names, people's names, book titles |
| Pages in a browser | a script error on a page, or a page asking for a file that is missing (each main page and a sample of decision pages, in English and in Indonesian) | |
| External links | | a new external link (on a page or in a data file) that does not answer. Government sites often turn away automated visitors, so these are never errors. |

To keep a piece of text in English on purpose (a name, a quotation, a legal term), add `data-noi18n` to its element.

## The result

Open the pull request's **Checks** tab, then **Site checks**. The summary lists each new problem with its file and line; the same lines appear as notes on the pull request's **Files changed** tab. The full results (including older problems) are attached to the run as `site-check-results`.

## Running the checks on your own computer

```
python3 tools/copy_data.py && python3 tools/press_subdomain.py
python3 tools/checks/site_check.py --root . --out head.json
python3 tools/checks/compare.py --head head.json          # lists every problem, old and new
```

`browser_check.py` needs `pip install playwright` and `python -m playwright install chromium`. The build scripts change files in `site/`; use a spare copy of the repository, or throw the changes away afterwards (`git checkout site`).
