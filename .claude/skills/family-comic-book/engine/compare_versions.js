/* Required before sending PDFs: the portrait and landscape books must show the same texts, pictures and photos on every page (only layout may differ). Prints differences: 0 when they match. */
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://localhost:8765/layout/';   // node compare_versions.js http://localhost:PORT/layout/
async function grab(b, file, W, H) {
  const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto(BASE + file + '?print&lang=he');
  await p.waitForTimeout(2500);
  return await p.evaluate(() => [...document.querySelectorAll('#book > section')].map(s => ({
    id: s.id,
    texts: [...s.querySelectorAll('.tx, .sp h2, .sp .kick, .sp .sub, .sp .by, .sp q, .sp p, .sp li, .sp .cont, .sp .blurb div, .sp .for, .photo span')].map(e => e.textContent.replace(/⚠️/g, '').trim()).filter(Boolean).sort(),
    imgs: [...s.querySelectorAll('img')].filter(i => !i.classList.contains('blurfill')).map(i => decodeURIComponent(i.src.split('/').pop())).sort(),
    panels: s.querySelectorAll('.pw').length,
  })));
}
(async () => {
  const b = await chromium.launch();
  const a = await grab(b, 'sketch.html', 794, 1123), c = await grab(b, 'sketch-landscape.html', 1123, 794);
  const diffs = [];
  if (a.length !== c.length) diffs.push(`sections: ${a.length} vs ${c.length}`);
  for (let i = 0; i < Math.max(a.length, c.length); i++) {
    const x = a[i] || {}, y = c[i] || {};
    if (x.id !== y.id) { diffs.push(`section ${i}: ${x.id} vs ${y.id}`); continue; }
    if (x.panels !== y.panels) diffs.push(`${x.id}: panels ${x.panels} vs ${y.panels}`);
    const tx = JSON.stringify(x.texts), ty = JSON.stringify(y.texts);
    if (tx !== ty) diffs.push(`${x.id}: texts differ\n  P: ${x.texts.filter(t => !y.texts.includes(t)).join(' | ')}\n  L: ${y.texts.filter(t => !x.texts.includes(t)).join(' | ')}`);
    const ix = x.imgs.map(s => s.replace(/-wide(?=\.)/, '')), iy = y.imgs.map(s => s.replace(/-wide(?=\.)/, ''));
    if (JSON.stringify(ix) !== JSON.stringify(iy)) diffs.push(`${x.id}: pictures differ\n  P: ${x.imgs.join(', ')}\n  L: ${y.imgs.join(', ')}`);
  }
  const nt = a.reduce((s, x) => s + x.texts.length, 0), ni = a.reduce((s, x) => s + x.imgs.length, 0);
  console.log(JSON.stringify({ sections: a.length, texts: nt, pictures: ni, differences: diffs.length }));
  diffs.forEach(d => console.log(d));
  await b.close();
})();
