# Government hate speech: incoming official links (2026-11-18)

`official-links-2026-11-18.csv` gives an official link for 59 of the coded cells in `elections/codings.csv` (34 countries; features `adl`, `hsl`, `mig`, `const`). Before this, no cell linked to an official text.

- `iso3` + `feature` match `elections/codings.csv`. `law` is the instrument the cell cites.
- Every link was opened on 2026-11-18 in an ordinary browser on oto's computer, and the page title matched the law. `page_title_seen` is what the page showed.
- Sources are the state's own legislation portal (legislation.gov.uk, gesetze-im-internet.de, wetten.overheid.nl, boe.es, normattiva.it, riksdagen.se, retsinformation.dk, diariodarepublica.pt, irishstatutebook.ie, laws-lois.justice.gc.ca, govinfo.gov, legislation.gov.au, legislation.govt.nz, laws.e-gov.go.jp, law.go.kr, law.moj.gov.tw, gov.za, kenyalaw.org, infoleg.gob.ar, bcn.cl, secretariasenado.gov.co) or the court's own site (scc-csc.lexum.com).
- Only the page was opened. The section-level wording behind each coding was not re-read, so `checked_official_text` in `codings.csv` should stay `no` until an editor does that.
- 32 cells could not be linked yet (Cloudflare or security checks on legifrance, RIS Austria, peraturan.bpk.go.id, planalto; slow pages on fedlex, indiacode, diputados.gob.mx; two wrong guesses). They are on the assistant's follow-up list.
