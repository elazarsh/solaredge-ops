// usage: node shot.mjs <page.html> <outPrefix> <width> <height> <scrollFraction|stationIndex:N|time:T> ...
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)); const root = path.dirname(here);
const { chromium } = await import(path.join(root, '..', 'build', 'node_modules', 'playwright-core', 'index.mjs'));
const [pg, out, w = '1440', h = '900', ...steps] = process.argv.slice(2);
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.jpg': 'image/jpeg', '.mp3': 'audio/mpeg' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.statusCode = 404; return r.end(); } r.setHeader('Content-Type', mime[path.extname(p)] || 'application/octet-stream'); fs.createReadStream(p).pipe(r); });
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const exe = fs.readdirSync('/opt/pw-browsers').filter(d => d.startsWith('chromium-')).map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`)[0];
const b = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu', '--autoplay-policy=no-user-gesture-required'] });
const pageObj = await b.newPage({ viewport: { width: +w, height: +h } });
pageObj.on('pageerror', e => console.error('PAGEERROR', e.message));
pageObj.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
pageObj.on('response', r => { if (r.status() >= 400) console.error('HTTP', r.status(), r.url()); });
await pageObj.goto(`http://127.0.0.1:${srv.address().port}/${pg}`);
await pageObj.waitForTimeout(1200);
let n = 0;
for (const s of steps) {
  if (s.startsWith('station:')) await pageObj.evaluate(i => { const e = document.querySelectorAll('.stn')[i] || document.querySelectorAll('.slide[data-k="0"]')[i]; if (e) window.scrollTo(0, e.offsetTop - 10); }, +s.slice(8));
  else if (s.startsWith('time:')) await pageObj.evaluate(t => { if (window.__setTime) window.__setTime(t); }, +s.slice(5));
  else await pageObj.evaluate(f => window.scrollTo(0, f * (document.documentElement.scrollHeight - innerHeight)), +s);
  await pageObj.waitForTimeout(1600);
  await pageObj.screenshot({ path: `${out}-${n++}.png` });
}
const info = await pageObj.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, h: document.documentElement.scrollHeight }));
console.log(JSON.stringify(info));
await b.close(); srv.close();
