/* ספריית ההורדות */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon;

  function item(title, desc, tags, actions) {
    return '<div class="lib-item"><div><h4>' + esc(title) + tags + '</h4><p>' + esc(desc) + '</p></div><div class="row-actions">' + actions + '</div></div>';
  }
  function own() { return ' <span class="tag own">תבנית מקורית</span>'; }
  function viewBtn(path, name) { return '<button class="btn sm" type="button" data-view="' + esc(path) + '" data-name="' + esc(name) + '">צפייה</button>'; }
  function dlBtn(path, name, label) { return '<button class="btn sm primary" type="button" data-dl="' + esc(path) + '" data-name="' + esc(name) + '">' + icon('download') + esc(label || 'הורדה') + '</button>'; }

  TS.views.library = function () {
    var L = TS.library;
    var html =
      '<div class="wrap page-head"><span class="eyebrow">ספריית ההורדות</span><h1>הכול להורדה</h1>' +
      '<p class="lead">הנחיות, תבניות, ערכת פרויקט ו־Skills. כל קובץ מסומן: ״תבנית מקורית״ נוצרה בסטודיו, ו״משאב קיים״ הוא קישור לחומר של אחרים, עם הרישיון שלו.</p>' +
      '<div class="row" style="margin-top:6px">' + dlBtn(L.zips.everything, 'teachers-studio-kit.zip', 'הורדת הכול (ZIP)') + '<a class="btn" href="#kit-anchor" data-lib-go="kit-anchor">לערכת הפרויקט</a><a class="btn ghost" href="#skills-anchor" data-lib-go="skills-anchor">ל־Skills</a></div></div>' +
      '<div class="wrap" style="padding-bottom:50px">' +

      '<section class="lib-group" id="kit-anchor"><h2>ערכת פרויקט למורה</h2><p class="lead" style="margin-block:6px 10px">שבעה קבצים להקמת פרויקט קבוע ב־ChatGPT או ב־Claude. <a href="#adv-projects" data-route="adv-projects">מדריך ההקמה</a></p>' +
        item('ערכת הפרויקט המלאה (ZIP)', 'כל הקבצים יחד, כולל הוראות הקמה.', own(), dlBtn(L.zips.kit, 'project-kit.zip', 'הורדת ZIP')) +
        L.kitFiles.map(function (f) { return item(f[1], f[2], '', viewBtn('downloads/project-kit/' + f[0], f[0]) + dlBtn('downloads/project-kit/' + f[0], f[0])); }).join('') +
      '</section>' +

      '<section class="lib-group" id="skills-anchor"><h2>Skills מוכנים להעלאה</h2>' +
        '<div class="callout warn" style="margin-block:10px">' + icon('warn') + '<p>התקינו Skills רק ממקורות מהימנים, ועברו על התוכן לפני הפעלה. אלה Skills מקוריים של הסטודיו, ארוזים לפי מפרט ה־Skill: תיקייה אחת בשם ה־Skill ובתוכה קובץ <code>SKILL.md</code>. ב־Claude: Customize ← Skills ← + ← Create skill ← Upload a skill. <a href="#adv-skills" data-route="adv-skills">פרטים נוספים</a></p></div>' +
        L.skills.map(function (s) { return item(s.title + ' (' + s.id + ')', s.desc, own(), viewBtn('downloads/skills/' + s.id + '/SKILL.md', s.id + '/SKILL.md') + dlBtn('downloads/skills/' + s.id + '.zip', s.id + '.zip', 'הורדת ZIP')); }).join('') +
      '</section>' +

      '<section class="lib-group"><h2>תבניות הנחיות לשישה־עשר המסלולים</h2><p class="lead" style="margin-block:6px 10px">קובץ Markdown לכל מסלול: הנחיה לדוגמה (תבנית ריקה), הכלי המומלץ, בדיקת איכות והמשך עבודה. את ההנחיה המותאמת אליכם בונים בסטודיו.</p>' +
        item('כל התבניות (ZIP)', 'שישה־עשר קבצי Markdown בקובץ אחד.', own(), dlBtn(L.zips.prompts, 'prompts.zip', 'הורדת ZIP')) +
        TS.tasks.map(function (t) { return item(t.title, t.short, '', viewBtn('downloads/prompts/' + t.id + '.md', t.id + '.md') + dlBtn('downloads/prompts/' + t.id + '.md', t.id + '-template.md') + '<a class="btn sm" href="#task-' + t.id + '" data-route="task-' + t.id + '">למחולל</a>'); }).join('') +
      '</section>' +

      '<section class="lib-group"><h2>מדריכים וסקריפטים</h2>' +
        L.guides.map(function (g) { return item(g[1], g[2], own(), viewBtn('downloads/' + g[0], g[0].split('/').pop()) + dlBtn('downloads/' + g[0], g[0].split('/').pop())); }).join('') +
      '</section>' +

      '<section class="lib-group"><h2>משאבים קיימים שמצאנו</h2><p class="lead" style="margin-block:6px 10px">אלה קישורים לחומרים של אחרים, לא לתוצרים שלנו. הרישיון והתנאים הם של בעליהם.</p>' +
        L.external.map(function (e) {
          return '<div class="lib-item"><div><h4>' + esc(e.title) + ' <span class="tag">משאב קיים</span> <span class="tag chk">' + esc(e.by) + '</span></h4><p>' + esc(e.note) + '</p></div><div class="row-actions"><a class="btn sm" href="' + esc(e.url) + '" target="_blank" rel="noopener">למקור ' + icon('external') + '</a></div></div>';
        }).join('') +
        '<p class="hint" style="margin-top:12px">נבדק ב־' + TS.meta.checkedOn + '. דווח במקורות משניים: ב־14.7.2026 הושקה תוכנית ״Claude for Teachers״ לבעלי תפקיד מאומת בארה״ב. לא נמצאה אינדיקציה לזמינות בישראל.</p>' +
      '</section></div>';

    return {
      title: 'ספריית ההורדות', html: html,
      after: function (root) {
        TS.$$('[data-lib-go]', root).forEach(function (a) {
          a.addEventListener('click', function (e) { e.preventDefault(); var t = TS.$('#' + a.getAttribute('data-lib-go'), root); if (t) t.scrollIntoView({ behavior: 'smooth' }); });
        });
      }
    };
  };

})(window.TS = window.TS || {});
