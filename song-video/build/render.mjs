// Render composition frames with headless Chromium.
// usage: node render.mjs --out DIR (--times 1.5,60 | --from N --to M) [--q 92] [--png]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);                       // song-video/
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i < 0 ? d : (process.argv[i + 1] ?? true); };
const out = arg('out'); const fps = 24;
fs.mkdirSync(out, { recursive: true });
const mime = { '.html': 'text/html', '.json': 'application/json', '.jpg': 'image/jpeg', '.woff': 'font/woff', '.mp3': 'audio/mpeg' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.statusCode = 404; return res.end(); }
  res.setHeader('Content-Type', mime[path.extname(p)] || 'application/octet-stream');
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
const exe = fs.readdirSync('/opt/pw-browsers').filter(d => d.startsWith('chromium-')).map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`)[0];
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu', '--font-render-hinting=none', '--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('response', r => { if (r.status() >= 400) console.error('HTTP', r.status(), r.url()); });
page.on('pageerror', e => console.error('PAGEERROR', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
await page.goto(`http://127.0.0.1:${port}/build/index.html${arg('look', null) ? '?look=' + arg('look') : ''}`);
await page.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
const png = arg('png', false);
const q = Number(arg('q', 92));
async function shot(n, name) {
  await page.evaluate(t => window.seek(t), n / fps);
  const file = path.join(out, name);
  if (png) await page.screenshot({ path: file, type: 'png' });
  else await page.screenshot({ path: file, type: 'jpeg', quality: q });
}
if (arg('times', null)) {
  for (const t of String(arg('times')).split(',')) {
    const sec = Number(t);
    await shot(Math.round(sec * fps), `t${sec.toFixed(1).padStart(6, '0')}.${png ? 'png' : 'jpg'}`);
  }
} else {
  const a = Number(arg('from')), b = Number(arg('to'));
  const t0 = Date.now();
  for (let n = a; n < b; n++) {
    await shot(n, `f${String(n).padStart(5, '0')}.jpg`);
    if ((n - a) % 100 === 0) console.log(`frame ${n} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
}
await browser.close(); server.close();
