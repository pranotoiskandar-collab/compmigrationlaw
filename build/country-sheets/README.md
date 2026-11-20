# Country sheets

One-page sheets for people going abroad to work, made from the repository's own data.
Output goes to `site/country-sheets/` (served at theimr.org/country-sheets/):

- `<cc>-en.pdf`, `<cc>-id.pdf`: A4, for printing
- `<cc>-en.jpg`, `<cc>-id.jpg`: one-column phone image, for WhatsApp
- `index.html`: the download page

Rebuild after the data changes:

```
pip install qrcode            # once
python3 build/country-sheets/build.py          # all eight countries
python3 build/country-sheets/build.py ID       # one country
```

Then, if the Puncak green look (PR #19) is on main, run `python3 build/newspaper-build/puncak_green.py site`
so the download page picks up the green palette (the sheets themselves are already green).

Where each part comes from:

| Part of the sheet | Source |
|---|---|
| "What the law says" (8 rows) | `data/countries-of-origin/codings.csv` and `protection.csv`; wording in `text.py` restates the codebook levels |
| Main laws | first three statutes per country in `data/countries-of-origin/laws-policies.csv` |
| Free help | `site/legal-help/places.js`; phone numbers only as listed there (checked) |
| Court decision | `data/court-decisions/decisions.csv`, picks in `CASE_PICKS` (outcome won, status S or P, both summaries) |
| QR codes | theimr.org/legal-help, /countries-of-origin, /updates |

The A4 sheet shows one court decision; the phone image shows up to two. `render.js` warns when a sheet runs past one A4 page.
