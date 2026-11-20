# Feature pages (19 November 2026)

| Page | Built by | Data |
|---|---|---|
| `/ratifications/` Ratification tracker | `ratifications.py` (text); table drawn by `site/ratifications/rt.js` | `data/ratifications/`, refreshed every Monday by `.github/workflows/ratification-update.yml` running `tools/ratifications/update.py` |
| `/rights-checklist/` Know your rights before you go | `rights_checklist_data.py` → `checklist-data.json`, `rights_checklist.py` (page), `rights_checklist_pdfs.js` (38 PDFs) | domestic-workers, east-asia, southeast-asia codings; ratifications; `site/legal-help/places.js` |
| `/court-decisions/highlights/` Case of the month | `highlights.py` from `highlights_content.py` (one entry a month) | `data/court-decisions/decisions.csv` |
| `/research/` Saved searches and reading list | `research.py`; logic in `site/assets/research.js` and `site/research/rs.js` | browser localStorage only |

All pages share `shell-template.html` (header, menu, footer in the Puncak green look) through `shell.py`, plus
`site/assets/features.css` and `site/assets/features.js`.

Rebuild after data changes (from the repository root):

    cd build/feature-pages
    python3 rights_checklist_data.py && python3 rights_checklist.py && python3 ratifications.py && python3 highlights.py && python3 research.py
    # PDFs: serve the site with data copied in, then
    node rights_checklist_pdfs.js http://localhost:8765 ../../site/rights-checklist/pdf

`add_nav_links.py` adds the four pages to the menu on every other page; run it once after PR #19 is merged.
