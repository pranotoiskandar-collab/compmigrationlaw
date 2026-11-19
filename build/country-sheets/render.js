// Renders each sheet HTML to an A4 PDF, a phone-width PNG (972 px wide) and a small thumbnail.
// Usage: node render.js HTML_DIR OUT_DIR name1 name2 ...
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [dir, out, ...names] = process.argv.slice(2);
  const browser = await chromium.launch();
  const a4 = await browser.newPage({ viewport: { width: 794, height: 1123 } });
  const phone = await browser.newPage({ viewport: { width: 432, height: 900 }, deviceScaleFactor: 2.25 });
  const thumb = await browser.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 0.38 });
  for (const n of names) {
    const url = 'file://' + path.resolve(dir, n + '.html');
    await a4.goto(url, { waitUntil: 'networkidle' });
    await a4.evaluate(() => document.fonts.ready);
    const over = await a4.evaluate(() => { const p = document.querySelector('.page'); return p.scrollHeight - 1123; });
    if (over > 0) console.warn(`${n}: ${over}px taller than one A4 page`);
    await a4.pdf({ path: path.join(out, n + '.pdf'), format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, pageRanges: '1' });
    await thumb.goto(url, { waitUntil: 'networkidle' });
    await thumb.evaluate(() => document.fonts.ready);
    await thumb.screenshot({ path: path.join(out, n + '-thumb.jpg'), type: 'jpeg', quality: 80, clip: { x: 0, y: 0, width: 794, height: 1123 } });
    await phone.goto(url, { waitUntil: 'networkidle' });
    await phone.evaluate(() => document.fonts.ready);
    await phone.screenshot({ path: path.join(out, n + '.jpg'), type: 'jpeg', quality: 78, fullPage: true });
  }
  await browser.close();
})();
