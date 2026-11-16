// צילום פריימים בזמנים נבחרים (שניות) לבדיקה ויזואלית מהירה. פלט: <out>/<t>.jpg (ברירת מחדל tmp/q).
// שימוש: node snap.js <dir> [--page page.html] [--out tmp/q] t1 t2 t3 ...
const fs = require('fs'), path = require('path');
const { launch, serve } = require('./lib');
const args = process.argv.slice(2), opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
const flagVals = new Set(['--page', '--out']);
const rest = args.filter((a, i) => !a.startsWith('--') && !flagVals.has(args[i - 1]));
const dir = path.resolve(rest[0] || '.'), times = rest.slice(1).map(Number), out = path.resolve(opt('out', 'tmp/q'));
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const srv = await serve(dir, 8796), b = await launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
  await p.goto(`http://localhost:8796/${opt('page', 'page.html')}`); await p.evaluate(() => window.preload());
  for (const t of times) { await p.evaluate(t => window.seek(t), t); await p.waitForTimeout(40); await p.screenshot({ path: path.join(out, t.toFixed(1) + '.jpg'), type: 'jpeg', quality: 82 }); }
  console.log('saved', times.length, 'frames to', out); await b.close(); srv.close();
})();
