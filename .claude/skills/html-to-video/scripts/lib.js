// כלי משותף לסקריפטי הצילום: טעינת playwright-core, איתור Chromium, שרת סטטי.
// לא מריצים "playwright install": הסביבה מגדירה PLAYWRIGHT_BROWSERS_PATH (בדרך כלל /opt/pw-browsers).
const fs = require('fs'), path = require('path'), http = require('http'), cp = require('child_process');

function loadPlaywright() {
  const roots = [process.cwd() + '/node_modules', path.join(__dirname, '..', 'node_modules')];
  try { roots.push(cp.execSync('npm root -g', { encoding: 'utf8' }).trim()); } catch (e) {}
  for (const r of (process.env.NODE_PATH || '').split(':').filter(Boolean)) roots.push(r);
  roots.push('/opt/node-tools/node_modules');
  for (const name of ['playwright-core', 'playwright']) {
    try { return require(name); } catch (e) {}
    for (const r of roots) { try { return require(path.join(r, name)); } catch (e) {} }
  }
  throw new Error('playwright-core לא נמצא. הרץ: bash scripts/setup.sh (npm i playwright-core gsap @fontsource/heebo)');
}

function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  if (fs.existsSync(base)) {
    for (const d of fs.readdirSync(base).sort().reverse()) {
      if (!d.startsWith('chromium-')) continue;
      for (const sub of ['chrome-linux/chrome', 'chrome-linux64/chrome']) {
        const p = path.join(base, d, sub); if (fs.existsSync(p)) return p;
      }
    }
  }
  return undefined; // ברירת מחדל של playwright
}

async function launch(extra = []) {
  const { chromium } = loadPlaywright();
  return chromium.launch({ executablePath: findChromium(), args: ['--no-sandbox', '--force-color-profile=srgb', ...extra] });
}

const MIME = { '.html': 'text/html;charset=utf-8', '.js': 'text/javascript', '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.png': 'image/png', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
function serve(root, port) {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
      if (!p.startsWith(path.resolve(root)) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); r.end(); return; }
      r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r);
    }).listen(port, () => res(s));
  });
}
module.exports = { launch, serve, findChromium };
