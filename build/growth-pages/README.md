# Growth pages: Ask IMR, partner badge, impact, materials

| What | Where | Built by |
|---|---|---|
| Ask IMR (Tanya IMR) on the Legal Clinic page | `site/assets/ask-imr.js`, `ask-imr.css`, index in `site/legal-clinic/ask/` | `build_ask_index.py` (also run at publish), `clinic_ask.py` puts the box on the Clinic page |
| Partner badge, country box, reuse terms | `site/partners/`, badges in `site/partners/badge/`, widget in `site/embed/country/` | `build_pages.py`, `badges.py`, `render_png.js` |
| Impact page | `site/impact/` | `build_pages.py`, figures in `impact-figures.json` |
| Materials page | `site/materials/`, files in `site/materials/files/` (teaching packs go in `files/teaching/`) | `build_pages.py` (copies from /mnt/project-files when mounted) |
| Indonesian for these pages | `site/assets/lang-growth.js` | `build_pages.py` |

Ask IMR uses no AI model and no paid service: it matches the question to a country and a topic
in the browser and shows database records with their sources. Only country and topic are counted
(GoatCounter event `event/ask/<country>/<topic>`), never the question.

At publish, `publish.py` (in netlify.toml) rebuilds the Ask IMR index from `data/`, adds
"Materials · Partner badge · Our impact" to every footer, and adds the pages to sitemap.xml and llms.txt.
Page HTML in the repository is not changed by that step.

Impact figures: fill `impact-figures.json` (never estimate; null shows "Being collected"), then run
`python3 build/growth-pages/build_pages.py`.

Rerun after a rebuild of the Clinic page: `python3 build/growth-pages/clinic_ask.py site`.
