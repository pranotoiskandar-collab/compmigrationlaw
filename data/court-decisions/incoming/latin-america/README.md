# Court decisions: incoming, Latin America

## Chile Supreme Court migration compendium (2026-11-18)

`cl-supreme-court-migration-2026-11-18.csv` has 162 decisions of the Third Chamber of the Corte Suprema de Chile, from 2023 to 2026. Before this, the site had one Chilean decision.

**Source.** The Poder Judicial publishes these itself as the "Compendio Extranjería" in its unified judgment search (juris.pjud.cl). The rows are protection appeals (recursos de protección) against the migration service, on four topics:

- permanent residence
- temporary visas
- naturalisation
- regularisation

The compendium tags each decision with the respondent agency and the applicant's nationality. Most applicants are from Venezuela, Haiti, Colombia, Peru, Bolivia and China. A few are from Asia and Africa.

**What to know before merging:**

- **No per-decision link.** The portal opens decisions through a form, so it has no web address for each one. `official_link` points to the compendium, and `case_no` gives the Rol number to search.
- **Outcome not coded.** "Confirmed" or "reversed" refers to the appeals court ruling, which may have granted or refused the appeal. Whether the migrant won needs a first read of each text.
- **No applicant names.** They are left out on purpose. The name column uses the Rol number, the topic and the nationality.
- **Status.** Every row is Unverified.
