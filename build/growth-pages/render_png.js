// Render PNG copies (2x) of the partner badges. Run from the repo root: node build/growth-pages/render_png.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.resolve('site/partners/badge');
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 264, height: 56 } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    await p.setContent('<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@700&display=block"></head><body style="margin:0;background:transparent">' + svg + '</body></html>');
    await p.waitForTimeout(600);
    await p.screenshot({ path: path.join(dir, f.replace('.svg', '.png')), omitBackground: true, clip: { x: 0, y: 0, width: 264, height: 56 } });
  }
  await b.close();
})();
