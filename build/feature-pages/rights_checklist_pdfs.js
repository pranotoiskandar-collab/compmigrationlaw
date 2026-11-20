// Print every rights checklist sheet (each country x job, in Indonesian and English) to
// site/rights-checklist/pdf/. Needs a local copy of the site served with its data, for example:
//   python3 tools/copy_data.py && (cd site && python3 -m http.server 8765) &
//   node build/feature-pages/rights_checklist_pdfs.js http://localhost:8765 site/rights-checklist/pdf
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const base = process.argv[2] || 'http://localhost:8765', out = process.argv[3] || 'site/rights-checklist/pdf';
  fs.mkdirSync(out, {recursive: true});
  const b = await chromium.launch();
  const p = await b.newPage();
  const data = await (await fetch(base + '/rights-checklist/checklist-data.json')).json();
  let n = 0;
  for (const c of data.countries) for (const g of c.groups) for (const l of ['id', 'en']) {
    await p.goto(`${base}/rights-checklist/?c=${c.iso2}&g=${g.k}&l=${l}`, {waitUntil: 'networkidle'});
    await p.waitForSelector('html[data-rc-ready]');
    await p.emulateMedia({media: 'print'});
    const file = path.join(out, `${c.iso2.toLowerCase()}-${g.k.toLowerCase()}-${l}.pdf`);
    await p.pdf({path: file, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="width:100%;font-size:8px;color:#555;text-align:center;font-family:sans-serif"><span class="pageNumber"></span> / <span class="totalPages"></span> · theimr.org/rights-checklist</div>',
      margin: {top: '12mm', bottom: '14mm', left: '12mm', right: '12mm'}});
    n++;
  }
  await b.close();
  console.log(n + ' PDFs written to ' + out);
})();
