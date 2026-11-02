/* Print edition of the v0.8 sketch: one A4 sheet per section (cover, title, 48 story pages, closing card, back cover).
   Serve the book folder (python3 -m http.server 8765) and run:
     node revisions/book1-v08/print_pdf.js http://localhost:8765/revisions/book1-v08/sketch.html OUT_DIR [he|en] [dpi]
   Then: python3 revisions/book1-v08/print_pdf.py OUT_DIR  ->  OUT_DIR/*-A4-print.pdf (300dpi) and *-A4-screen.pdf (150dpi). */
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const [url, out, lang = 'he', dpi = '300', orient = 'portrait'] = process.argv.slice(2);
  const land = orient === 'landscape', W = land ? 1123 : 794, Hh = land ? 794 : 1123, mm = land ? 297 : 210;
  fs.mkdirSync(out, { recursive: true });
  const scale = (+dpi * mm / 25.4) / W;   // css px width = page width in mm
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: Hh }, deviceScaleFactor: scale });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(url + '?print&lang=' + lang, { waitUntil: 'load' });
  await p.evaluate(() => document.querySelectorAll('img').forEach(i => i.loading = 'eager'));
  await p.waitForTimeout(2500);
  const ids = await p.evaluate(() => [...document.querySelectorAll('#book > section')].map(s => s.id));
  let n = 0;
  for (const id of ids) {
    const el = await p.$('#' + id); await el.scrollIntoViewIfNeeded();
    await p.waitForFunction(id => [...document.querySelectorAll('#' + id + ' img')].every(i => i.complete && i.naturalWidth), id, { timeout: 15000 }).catch(() => {});
    await p.evaluate(id => Promise.all([...document.querySelectorAll('#' + id + ' img')].map(i => i.decode().catch(() => {}))), id);
    await p.waitForTimeout(600);
    const box = await el.$('.page, .sp');
    await box.screenshot({ path: `${out}/sheet-${String(++n).padStart(2, '0')}-${id}.jpg`, type: 'jpeg', quality: 90 });
  }
  console.log(JSON.stringify({ sheets: n, errs, qa: await p.evaluate(() => window.__qa ? window.__qa() : []) }));
  await b.close();
})();
