// Writes the static CSV downloads that the Dataset JSON-LD points to. Usage: node gen_data.js <site dir>
const fs = require('fs'), path = require('path');
const site = process.argv[2];
const load = f => fs.readFileSync(path.join(__dirname, f), 'utf8').replace(/^const /gm, 'var ');
eval(load('data_block.js') + load('migration_block.js') + load('impl_block.js') + load('cases_block.js') + load('cov_block.js'));
const q = v => { if (v == null) return ''; const s = Array.isArray(v) ? v.join('; ') : String(v); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
const csv = (head, rows) => [head.join(','), ...rows.map(r => r.map(q).join(','))].join('\n') + '\n';
const write = (dir, name, text) => { fs.mkdirSync(path.join(site, dir), {recursive: true}); fs.writeFileSync(path.join(site, dir, name), text); };
const NH = ['name', 'citation', 'family', 'authority_B', 'relevance_R', 'adopted', 'in_force', 'provisions', 'drivers', 'link'];
write('atlas/data', 'farmworker-norms.csv', csv(['tier', ...NH], [...D.map(r => ['international or regional', ...r]), ...DN.map(r => ['national', ...r])]));
write('migration-law/data', 'migration-norms.csv', csv([...NH, 'tier', 'relevance_RM', 'topics'], DM));
const rats = JSON.parse(fs.readFileSync(path.join(__dirname, 'rats.json'), 'utf8')), ST = {F: 'in force', P: 'ratified, not yet in force', W: 'withdrawn or denounced', D: 'denounced'};
const rr = []; Object.keys(rats).forEach(k => rats[k].forEach(x => rr.push([k, x[0], x[1], x[2], ST[x[2]] || ''])));
write('atlas/data', 'ratifications.csv', csv(['instrument', 'country', 'date', 'status_code', 'status'], rr));
const C = JSON.parse(fs.readFileSync(path.join(__dirname, 'countries.json'), 'utf8'));
const K = ['income', 'gdppc', 'remit_gdp', 'migstock', 'agri_emp', 'rule_of_law', 'pop'];
write('atlas/data', 'country-indicators.csv', csv(['country', 'ratification_score', 'breadth', 'enthusiasm', 'instruments_ratified', 'farm_conventions_ratified', ...K],
  C.map(d => [d.c, d.sc, d.br, d.en, d.n, d.nf, ...K.map(k => (COV[d.c] || {})[k])])));
const SN = {F: 'implemented', P: 'partly implemented', G: 'gap', D: 'national law without ratification'}, ir = [];
Object.keys(IMPL).forEach(c => IMPL[c].rows.forEach(r => ir.push([c, r[0], r[2], r[3], SN[r[3]] || '', r[4], r[5] ? 'yes' : 'no'])));
write('atlas/data', 'implementation.csv', csv(['country', 'instrument', 'domestic_measures', 'status_code', 'status', 'note', 'farm_relevant'], ir));
write('atlas/data', 'cases.csv', csv(['case', 'forum', 'year', 'country', 'farm_relevant', 'decision', 'norms_applied', 'link'], CASES.map(r => [r[0], r[1], r[2], r[3], r[4] ? 'yes' : 'no', r[5], r[6], r[7]])));
console.log('csv written', rr.length, 'ratifications,', ir.length, 'implementation rows');
