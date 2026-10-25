/* בנייה: יוצר את קבצי ההורדה של האתר (site/downloads) מתוך kit/ ומתוך מנוע ההנחיות,
   ומכין גרסת קטע (fragment) לפרסום כ־Artifact.
   שימוש: node build.mjs            ← קבצי הורדה
          node build.mjs --artifact <dir>  ← בנוסף, חבילת פרסום ל־Artifact בתיקייה <dir> */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const root = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(root, 'site');
const out = path.join(site, 'downloads');
const kit = path.join(root, 'kit');
const TS = require('./tools/load.cjs')(site);

const rm = (p) => fs.rmSync(p, { recursive: true, force: true });
const mk = (p) => fs.mkdirSync(p, { recursive: true });
const write = (p, t) => { mk(path.dirname(p)); fs.writeFileSync(p, t, 'utf8'); };
const copyDir = (a, b, o = {}) => fs.cpSync(a, b, { recursive: true, ...o });
function zip(cwd, target, ...inputs) {
  rm(target); mk(path.dirname(target));
  execFileSync('zip', ['-r', '-X', '-q', target, ...inputs], { cwd });
}

rm(out); mk(out);

/* ערכת הפרויקט */
copyDir(path.join(kit, 'project-kit'), path.join(out, 'project-kit'));
zip(out, path.join(out, 'project-kit.zip'), 'project-kit');

/* Skills: תיקייה לצפייה, ו־ZIP שבו התיקייה היא השורש */
for (const s of TS.library.skills) {
  const src = path.join(kit, 'skills', s.id);
  copyDir(src, path.join(out, 'skills', s.id));
  zip(path.join(kit, 'skills'), path.join(out, 'skills', s.id + '.zip'), s.id);
}

/* תבניות הנחיות לכל מסלול */
for (const t of TS.tasks) write(path.join(out, 'prompts', t.id + '.md'), TS.engine.template(t));
zip(out, path.join(out, 'prompts.zip'), 'prompts');

/* מדריכים */
copyDir(path.join(kit, 'guides'), path.join(out, 'guides'));
const status = TS.statusLabels;
const sheet = ['# כלים במבט אחד', '', `> ${TS.meta.siteName} · נבדק ב־${TS.meta.checkedOn}. כל טענה מסומנת לפי רמת האימות. מחירים, מגבלות ותמיכה בעברית משתנים: בדקו באתר הכלי.`, ''];
for (const id of TS.toolIds) {
  const t = TS.tools[id];
  sheet.push(`## ${t.name} (${t.maker})`, '', t.tagline, '', '**מתי לבחור**');
  t.when.forEach((x) => sheet.push(`- ${x}`));
  sheet.push('', '**איך מתחילים**');
  t.start.forEach((x, i) => sheet.push(`${i + 1}. ${x}`));
  sheet.push('', '**מגבלות**');
  t.limits.forEach((x) => sheet.push(`- ${x}`));
  sheet.push('', `**עברית:** ${t.hebrew.note} (${status[t.hebrew.s]})`, '', '**מה אומת ומה לא**');
  t.facts.forEach((f) => sheet.push(`- [${status[f.s]}] ${f.t}`));
  sheet.push('', '**מקורות**');
  t.sources.forEach((s) => sheet.push(`- ${s.label}: ${s.url}`));
  sheet.push(`- אתר הכלי: ${t.url}`, '');
}
write(path.join(out, 'guides', 'tools-cheatsheet.md'), sheet.join('\n'));

/* הכול ב־ZIP אחד */
const all = path.join(root, '.build-all');
rm(all); mk(path.join(all, 'teachers-studio-kit'));
copyDir(path.join(out, 'project-kit'), path.join(all, 'teachers-studio-kit', 'project-kit'));
copyDir(path.join(out, 'prompts'), path.join(all, 'teachers-studio-kit', 'prompts'));
copyDir(path.join(out, 'guides'), path.join(all, 'teachers-studio-kit', 'guides'));
for (const s of TS.library.skills) copyDir(path.join(kit, 'skills', s.id), path.join(all, 'teachers-studio-kit', 'skills', s.id));
const kitReadme =
  `# ערכת העבודה של ״${TS.meta.siteName}״\n\n- project-kit: שבעה קבצים להקמת פרויקט ב־ChatGPT או ב־Claude\n- skills: חמישה Skills, כל תיקייה אפשר לארוז ל־ZIP ולהעלות ל־Claude (Customize ← Skills)\n- prompts: תבניות הנחיות לשישה־עשר מסלולים\n- guides: מדריכים, סקריפטים ל־Google Forms ושימוש בטוח\n\nתבניות מקוריות של הסטודיו. נבדק ב־${TS.meta.checkedOn}.\n`;
write(path.join(all, 'teachers-studio-kit', 'README.md'), kitReadme);
write(path.join(out, 'kit-README.md'), kitReadme);
zip(all, path.join(out, 'teachers-studio-kit.zip'), 'teachers-studio-kit');
rm(all);

/* בדיקת שלמות: כל קובץ שהאתר מפנה אליו קיים */
const needed = [];
const L = TS.library;
needed.push(L.zips.kit, L.zips.prompts, L.zips.everything);
L.kitFiles.forEach((f) => needed.push('downloads/project-kit/' + f[0]));
L.skills.forEach((s) => needed.push(`downloads/skills/${s.id}/SKILL.md`, `downloads/skills/${s.id}.zip`));
TS.tasks.forEach((t) => needed.push(`downloads/prompts/${t.id}.md`));
L.guides.forEach((g) => needed.push('downloads/' + g[0]));
needed.push('downloads/kit-README.md');
const missing = needed.filter((p) => !fs.existsSync(path.join(site, p)));
if (missing.length) { console.error('חסרים קבצים:', missing); process.exit(1); }
console.log(`downloads OK: ${needed.length} קבצים נבדקו, כולם קיימים`);

/* גרסת Artifact: קטע בלי doctype/html/head/body (העטיפה נוספת בפרסום) */
const ai = process.argv.indexOf('--artifact');
if (ai > -1) {
  const dest = path.resolve(process.argv[ai + 1]);
  rm(dest); mk(dest);
  const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8');
  const head = html.match(/<head>([\s\S]*?)<\/head>/)[1].replace(/<meta charset="utf-8">\s*/i, '').replace(/<meta name="viewport"[^>]*>\s*/i, '');
  const body = html.match(/<body>([\s\S]*?)<\/body>/)[1];
  fs.writeFileSync(path.join(dest, 'index.html'), head.trim() + '\n' + body.trim() + '\n', 'utf8');
  for (const d of ['css', 'js', 'assets', 'downloads']) copyDir(path.join(site, d), path.join(dest, d), { filter: (f) => !f.endsWith('.zip') });
  console.log('artifact bundle:', dest);
}
