/* Screenshot one HTML file (a map, a sticker) to PNG:  node shot.js IN.html OUT.png WIDTH HEIGHT */
const { chromium } = require('playwright');
(async () => { const [i, o, w, h] = process.argv.slice(2); const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: +h } }); await p.goto('file://' + require('path').resolve(i));
  await p.waitForTimeout(2500); await p.screenshot({ path: o }); await b.close(); })();
