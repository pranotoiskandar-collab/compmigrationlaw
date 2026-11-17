# Africa: incoming rows (2026-11-17)

Kept separate from the Gulf (`data/gcc/`) files at oto's request.

- `laws-2026-11-17.csv`: 62 laws, regulations, ministerial directives, bills and policies (South Africa, Kenya, Uganda, Ghana, Zimbabwe, Nigeria; SADC, AU, EAC). Columns follow CONTRIBUTING.md plus `regional_body`, `source_tier` and `site_status`.
- `court-decisions-2026-11-17.csv`: 87 decisions, with the columns of `data/court-decisions/decisions.csv` plus `official_link`, `source_tier`, `site_status`, `checked_on`, `note`. All rows are `status` C and marked Unverified. `tier` is national or regional. 25 rows are already on the site: for those, the new value is the Constitutional Court's own archive link (CCspace), which can replace a LII link.

`source_tier` says where each row comes from. "official" means the court, the law reporter or the ministry (Constitutional Court archive, Kenya Law, ULII, Home Affairs, NIS, SADC, AU). "LII" means a legal information institute (lawlibrary.org.za, GhaLII, ZimLII, NigeriaLII): free and reliable, but not the court's own site, so these rows need an official link later.
