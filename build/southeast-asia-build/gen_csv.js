// Writes the static CSV downloads for /southeast-asia/ from sea-data.js and the Countries of Origin data.
// Usage: node gen_csv.js <site-root>
const fs = require("fs"), path = require("path");
const root = process.argv[2];
global.window = {};
for (const f of ["countries-of-origin/oc-data.js", "countries-of-origin/oc-sea.js", "southeast-asia/sea-data.js", "southeast-asia/sea-check.js"]) eval(fs.readFileSync(path.join(root, f), "utf8"));
const G = window.SEA, O = window.OC, out = path.join(root, "southeast-asia/data");
fs.mkdirSync(out, {recursive: true});
const q = v => { v = v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
const csv = (rows, cols) => "﻿" + cols.join(",") + "\n" + rows.map(r => cols.map(c => q(r[c])).join(",")).join("\n") + "\n";
const w = (n, rows, cols) => fs.writeFileSync(path.join(out, n), csv(rows, cols));
const CB = G.codebook, codings = [];
G.groups.forEach(g => CB.forEach(d => { const c = g.codes[d.k] || []; const ck = G.checked[g.k + "." + d.k];
  codings.push({group: g.k, group_name: g.n, state: g.s, feature: d.k, feature_name: d.en, value: c[0] == null ? "" : c[0], value_label: c[0] == null ? "unclear" : d["l" + c[0]], note: c[1], source: c[2], evidence: ck ? "P" : "S", coded: "2026-11-13", checked_official_text: ck ? G.checked_on + " (" + ck + ")" : ""}); }));
w("codings.csv", codings, ["group", "group_name", "state", "feature", "feature_name", "value", "value_label", "note", "source", "evidence", "coded", "checked_official_text"]);
w("codebook.csv", CB.map(d => ({feature: d.k, name: d.en, name_id: d.id, value_2: d.l2, value_1: d.l1, value_0: d.l0, value_2_id: d.l2_id, value_1_id: d.l1_id, value_0_id: d.l0_id})), ["feature", "name", "name_id", "value_2", "value_1", "value_0", "value_2_id", "value_1_id", "value_0_id"]);
w("treaty-status.csv", G.treaties.map(x => { const r = {instrument: x[1], description: x[2]}; G.states.forEach(s => r[s.k] = (G.intl[s.k] || {})[x[0]] || ""); return r; }), ["instrument", "description"].concat(G.states.map(s => s.k)));
w("instruments.csv", G.frameworks, ["s", "partner", "title", "level", "nature", "signed", "in_force", "scope"]);
w("domestic-laws.csv", G.laws, ["s", "title", "orig", "year", "amended", "type", "topic", "groups", "url", "link"]);
const OK = ["ID", "PH", "VN", "MM", "KH", "LA", "TL"], orig = [];
OK.forEach(k => O.codebook.forEach(d => { const c = (O.codes[k] || {})[d.k] || []; orig.push({country: k, feature: d.k, feature_name: d.en, value: c[0] == null ? "" : c[0], note: c[1], source: c[2], evidence: (O.checked && O.checked[k + "." + d.k]) ? "P" : "S"}); }));
w("origins.csv", orig, ["country", "feature", "feature_name", "value", "note", "source", "evidence"]);
w("developments.csv", G.reforms.map(r => ({date: r[0], state: r[1], change: r[2], change_id: r[3], kind: r[4]})), ["date", "state", "change", "change_id", "kind"]);
console.log("csv written", codings.length, orig.length);
