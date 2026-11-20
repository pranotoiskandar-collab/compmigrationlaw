// Work out the Indonesian dictionary each page gets in the browser.
//
// Reads a JSON list of jobs on stdin. Each job is a list of script texts in page
// order (the page's own Indonesian files, then the first line of /assets/lang.js,
// which assigns window.SITE_I18N). Prints, for each job, the strings the page adds
// on top of /assets/lang.js, so the output stays small.
const vm = require("vm");
let input = "";
process.stdin.on("data", (c) => (input += c));
process.stdin.on("end", () => {
  const { base, jobs } = JSON.parse(input);
  const out = jobs.map((scripts) => {
    const window = {};
    const ctx = vm.createContext({ window, console: { log() {}, warn() {}, error() {} } });
    ctx.self = window;
    for (const code of scripts) {
      try { vm.runInContext(code.replace(/^\s*window\./, "window."), ctx, { timeout: 2000 }); } catch (e) { /* a script that needs the DOM: skip it */ }
    }
    const d = (window.SITE_I18N && window.SITE_I18N.id) || {};
    const extra = {};
    for (const k of Object.keys(d)) if (k !== "__pat" && base[k] !== d[k]) extra[k] = d[k];
    const pat = (d.__pat || []).map((p) => [p[0], p[1]]);
    return { extra, pat };
  });
  process.stdout.write(JSON.stringify(out));
});
