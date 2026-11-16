// צילום פריימים מדף HTML דטרמיניסטי (window.seek(t), window.preload(), window.TOTAL).
// שימוש (worker אחד): node render_frames.js <dir עם page.html> <worker> <numWorkers> <port> [--page page.html] [--out frames] [--fps 24]
// בדרך כלל לא קוראים לזה ישירות אלא דרך render.sh (4 workers במקביל, ~22 פריימים בשנייה במצטבר).
// משתני סביבה: MAXF=מספר פריימים מקסימלי (בדיקה קצרה), FORCE=1 לצלם שוב קבצים קיימים.
const fs = require('fs'), path = require('path');
const { launch, serve } = require('./lib');
const args = process.argv.slice(2), pos = args.filter((a, i) => !a.startsWith('--') && !(args[i - 1] || '').startsWith('--'));
const opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
const [dir, w, nw, port] = [path.resolve(pos[0] || '.'), +pos[1] || 0, +pos[2] || 1, +pos[3] || 8800];
const page = opt('page', 'page.html'), out = path.resolve(opt('out', 'frames')), FPS = +opt('fps', 24);
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const srv = await serve(dir, port), b = await launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto(`http://localhost:${port}/${page}`); await p.evaluate(() => window.preload());
  const total = await p.evaluate(() => window.TOTAL), N = Math.ceil(total * FPS), MAXF = process.env.MAXF ? +process.env.MAXF : N;
  for (let f = w; f < Math.min(N, MAXF); f += nw) {
    const o = path.join(out, String(f).padStart(5, '0') + '.jpg');
    if (fs.existsSync(o) && !process.env.FORCE) continue;
    await p.evaluate(t => window.seek(t), f / FPS);
    await p.screenshot({ path: o, type: 'jpeg', quality: 90 });
  }
  console.log('worker', w, 'done'); await b.close(); srv.close();
})();
