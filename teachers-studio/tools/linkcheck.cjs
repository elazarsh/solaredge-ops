/* בודק שכל כתובות ה־https שבקבצי התוכן מחזירות סטטוס תקין */
const fs = require('fs'), path = require('path'), cp = require('child_process');
const dir = path.join(__dirname, '..', 'site');
function walk(d, out = []) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); fs.statSync(p).isDirectory() ? walk(p, out) : out.push(p); } return out; }
const urls = new Set();
for (const f of walk(dir).filter(f => /\.(js|html|md)$/.test(f))) {
  const t = fs.readFileSync(f, 'utf8');
  (t.match(/https:\/\/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%\-]+/g) || []).forEach(u => urls.add(u.replace(/[.,;:'")\]]+$/, '')));
}
const TS = require('./load.cjs')(dir);
(function collect(o) { if (typeof o === 'string') { if (/^https:\/\//.test(o)) urls.add(o); } else if (o && typeof o === 'object') Object.values(o).forEach(collect); })(TS);
const skip = /fonts\.(googleapis|gstatic)|cdnjs\.cloudflare|^https:\/\/(\$|\.)/;
const list = [...urls].filter(u => !skip.test(u)).sort();
const res = [];
for (const u of list) {
  let code = '000';
  try { code = cp.execFileSync('curl', ['-sS', '-m', '20', '-L', '-o', '/dev/null', '-w', '%{http_code}', '-A', 'Mozilla/5.0', u], { encoding: 'utf8' }); } catch (e) { code = 'ERR'; }
  res.push([code, u]);
}
res.sort((a, b) => a[0].localeCompare(b[0]));
for (const [c, u] of res) console.log(c, u);
