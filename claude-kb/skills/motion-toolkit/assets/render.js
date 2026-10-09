#!/usr/bin/env node
// Deterministic frame renderer with real motion blur (temporal supersampling) and parallel workers.
// Usage: node render.js <composition.html> <outDir> [--fps 30] [--duration 30] [--w 1080] [--h 1920]
//        [--sub 4] [--shutter 0.5] [--workers 4] [--only 1.5,6,12]   (--only = single stills for QA, no blur)
// Output: <outDir>/s_XXXXXX.png sub-frames (index = frame*sub + k), <outDir>/cues.json, <outDir>/meta.json
const path = require('path'), fs = require('fs'), { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const arg = (n, d) => { const i = process.argv.indexOf('--' + n); return i > -1 ? process.argv[i + 1] : d; };

if (isMainThread) {
  const [html, outDir] = process.argv.slice(2);
  if (!html || !outDir) { console.error('usage: render.js comp.html outDir [opts]'); process.exit(1); }
  const o = { fps: +arg('fps', 30), duration: +arg('duration', 30), w: +arg('w', 1080), h: +arg('h', 1920), sub: +arg('sub', 4),
    shutter: +arg('shutter', 0.5), workers: +arg('workers', 4), only: arg('only', '') };
  fs.mkdirSync(outDir, { recursive: true });
  const html_ = path.resolve(html);
  if (o.only) { // QA stills: exact times, no motion blur
    const times = o.only.split(',').map(Number);
    const w = new Worker(__filename, { workerData: { html: html_, outDir, o, jobs: times.map((t) => ({ t, name: `still_${t}.png` })), cues: true } });
    w.on('message', (m) => m.log && console.log(m.log)); w.on('exit', () => console.log('stills done')); return;
  }
  const total = Math.round(o.fps * o.duration), per = Math.ceil(total / o.workers); let done = 0, running = 0;
  for (let k = 0; k < o.workers; k++) {
    const a = k * per, b = Math.min(total, a + per); if (a >= b) continue; running++;
    const jobs = [];
    for (let f = a; f < b; f++) for (let s = 0; s < o.sub; s++) {
      const t = f / o.fps + ((s + 0.5) / o.sub - 0.5) * (o.shutter / o.fps);
      jobs.push({ t: Math.max(0, t), frame: f, name: `s_${String(f * o.sub + s).padStart(6, '0')}.png` });
    }
    const w = new Worker(__filename, { workerData: { html: html_, outDir, o, jobs, cues: k === 0 } });
    w.on('message', (m) => { if (m.tick) { done += m.tick; if (done % (o.fps * o.sub * 2) < m.tick) console.log(`progress ${(100 * done / (total * o.sub)).toFixed(0)}%`); } });
    w.on('error', (e) => { console.error('worker error', e); process.exit(1); });
    w.on('exit', () => { if (--running === 0) { fs.writeFileSync(path.join(outDir, 'meta.json'), JSON.stringify({ ...o, total })); console.log('render done'); } });
  }
} else {
  (async () => {
    const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
    const { html, outDir, o, jobs, cues } = workerData;
    const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--force-color-profile=srgb', '--disable-lcd-text', '--font-render-hinting=none'] });
    const page = await browser.newPage({ viewport: { width: o.w, height: o.h }, deviceScaleFactor: 1 });
    page.on('pageerror', (e) => parentPort.postMessage({ log: 'PAGE ERROR: ' + e.message }));
    page.on('console', (m) => { if (m.type() === 'error') parentPort.postMessage({ log: 'console.error: ' + m.text() }); });
    await page.goto('file://' + html); await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
    if (cues) fs.writeFileSync(path.join(outDir, 'cues.json'), JSON.stringify(await page.evaluate(() => window.__cues()), null, 1));
    for (const j of jobs) {
      await page.evaluate(([t, f]) => window.__seek(t, f), [j.t, j.frame === undefined ? Math.floor(j.t * o.fps) : j.frame]);
      await page.screenshot({ path: path.join(outDir, j.name) });
      parentPort.postMessage({ tick: 1 });
    }
    await browser.close();
  })().catch((e) => { console.error(e); process.exit(1); });
}
