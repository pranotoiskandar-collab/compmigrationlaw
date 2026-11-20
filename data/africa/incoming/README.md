# Africa: incoming rows (2026-11-17)

Kept separate from the Gulf (`data/gcc/`) files at Pranoto's request.

- `laws-2026-11-17.csv`: 62 laws, regulations, ministerial directives, bills and policies (South Africa, Kenya, Uganda, Ghana, Zimbabwe, Nigeria; SADC, AU, EAC). Columns follow CONTRIBUTING.md plus `regional_body`, `source_tier` and `site_status`.
- `court-decisions-2026-11-17.csv`: 87 decisions, with the columns of `data/court-decisions/decisions.csv` plus `official_link`, `source_tier`, `site_status`, `checked_on`, `note`. All rows are `status` C and marked Unverified. `tier` is national or regional. 25 rows are already on the site: for those, the new value is the Constitutional Court's own archive link (CCspace), which can replace a LII link.

`source_tier` says where each row comes from. "official" means the court, the law reporter or the ministry (Constitutional Court archive, Kenya Law, ULII, Home Affairs, NIS, SADC, AU). "LII" means a legal information institute (lawlibrary.org.za, GhaLII, ZimLII, NigeriaLII): free and reliable, but not the court's own site, so these rows need an official link later.

## 2026-11-19: South Africa Gazette check

14 South African rows in `laws-2026-11-17.csv` were checked against Government Gazette copies (and signed directives) that the research assistant saved in the shared Drive folder (ZA). For those rows `checked_on` is 2026-11-19 and the `note` gives the Gazette number, notice number and date. Five titles or dates were corrected to match the official text (Directive 9 of 2024, Directive 11 of 2026, Directive 2 of 2022, the 2025 draft Revised White Paper, and the Employment Services Amendment Bill, now B 16-2026). Still open: the Third Amendment of the Immigration Regulations, the 2017 White Paper Gazette copy, the Lesotho Exemption Permit notice, the quota work permit notice and the date of the Operation Vulindlela report.

## 2026-11-20: Kenya, Uganda, Ghana, Zimbabwe, Nigeria and regional check

The research assistant saved copies for lines 22 to 63 of `laws-2026-11-17.csv` in the shared Drive folders (KE, UG, GH, ZW, NG, XR), numbered by CSV line. 37 rows were checked against those copies: `checked_on` is 2026-11-20 and the `note` gives the Gazette supplement, number and date where the copy shows them, and the Drive file name.

Two rows are new, because the saved copy was a different instrument from the one on that line:

- Kenya Citizenship and Immigration (Amendment) Regulations, 2025 (LN 93 of 2025, eTA exemptions), saved as file 24.
- Kenya Refugees Act, 2006 (No. 13 of 2006, repealed by the Refugees Act, 2021), saved as file 42 in the Uganda folder. Its `official_link` is empty: Kenya Law no longer has a page for the repealed Act.

Still open: no copy yet for lines 24 (Kenya LN 1 of 2024), 28 (Kenya LN 143 of 2023), 42 (Uganda Refugees Act 2006), 57 (Nigeria Trafficking in Persons Act 2015) and 59 (Nigeria National Diaspora Policy); scans without text for lines 30, 40 and 54; the Zimbabwe Refugees Act year (1978 or 1983, line 52); and the signed text of the EAC Common Market Protocol (the saved copy is headed "Draft").
