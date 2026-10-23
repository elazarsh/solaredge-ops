import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)); const root = path.dirname(here);
const { chromium } = await import(path.join(root, '..', 'build', 'node_modules', 'playwright-core', 'index.mjs'));
const [pg, out] = process.argv.slice(2);
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.jpg': 'image/jpeg', '.mp3': 'audio/mpeg' };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]); const p = path.join(root, u); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.statusCode = 404; return r.end(); }
  const st = fs.statSync(p); const rg = q.headers.range; r.setHeader('Content-Type', mime[path.extname(p)] || 'application/octet-stream'); r.setHeader('Accept-Ranges', 'bytes');
  if (rg) { const m = /bytes=(\d+)-(\d*)/.exec(rg); const s = +m[1], e = m[2] ? +m[2] : st.size - 1; r.statusCode = 206; r.setHeader('Content-Range', `bytes ${s}-${e}/${st.size}`); r.setHeader('Content-Length', e - s + 1); fs.createReadStream(p, { start: s, end: e }).pipe(r); }
  else { r.setHeader('Content-Length', st.size); fs.createReadStream(p).pipe(r); } });
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const exe = fs.readdirSync('/opt/pw-browsers').filter(d => d.startsWith('chromium-')).map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`)[0];
const b = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu', '--autoplay-policy=no-user-gesture-required'] });
const page = await b.newPage({ viewport: { width: 1440, height: 900 } });
page.on('pageerror', e => console.error('PAGEERROR', e.message));
await page.goto(`http://127.0.0.1:${srv.address().port}/${pg}`); await page.waitForTimeout(800);
await page.click('#play'); await page.waitForTimeout(500);
await page.evaluate(() => { E.seek(111.0); }); await page.waitForTimeout(3500);
console.log(JSON.stringify(await page.evaluate(() => ({ t: E.t, playing: E.playing, ok: E.audioOK, now: [...document.querySelectorAll('.w.now')].map(e => e.textContent), past: document.querySelectorAll('.w.past').length, sy: scrollY, label: document.querySelector('#pl').textContent }))));
await page.screenshot({ path: out });
await b.close(); srv.close();
