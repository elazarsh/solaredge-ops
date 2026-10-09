// Deterministic frame renderer: seeks window.render(t) for each frame and screenshots it.
// Usage: node render.js <promo.html> <outDir> [fps=30] [duration=30] [onlyTimes=comma list in seconds]
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

(async () => {
  const [html, outDir, fpsArg, durArg, only] = process.argv.slice(2);
  const fps = +(fpsArg || 30), dur = +(durArg || 30);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(html));
  await page.evaluate(() => document.fonts.ready);
  const frames = only
    ? only.split(',').map(s => ({ i: Math.round(+s * fps), t: +s }))
    : Array.from({ length: Math.round(fps * dur) }, (_, i) => ({ i, t: i / fps }));
  for (const f of frames) {
    await page.evaluate(t => window.render(t), f.t);
    await page.screenshot({ path: path.join(outDir, `f_${String(f.i).padStart(5, '0')}.png`) });
    if (f.i % 90 === 0) console.log('frame', f.i);
  }
  await browser.close();
})();
