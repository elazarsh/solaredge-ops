/* טוען את קבצי התוכן לתוך מרחב TS ב־Node (לבדיקות ולבנייה) */
const vm = require('vm'), fs = require('fs'), path = require('path');
module.exports = function load(siteDir) {
  const ctx = { console };
  ctx.window = ctx; vm.createContext(ctx);
  const dir = path.join(siteDir, 'js', 'content');
  const order = JSON.parse(fs.readFileSync(path.join(__dirname, 'content-order.json'), 'utf8'));
  for (const f of order) vm.runInContext(fs.readFileSync(path.join(dir, f), 'utf8'), ctx, { filename: f });
  return ctx.TS;
};
