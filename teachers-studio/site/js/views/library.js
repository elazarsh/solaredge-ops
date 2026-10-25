/* ספריית ההורדות: לשוניות, שורות נקיות, הורדה וצפייה */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  function item(title, desc, tags, actions) {
    return '<li><div class="row-item" style="display:contents"><div><h4>' + esc(title) + tags + '</h4><p>' + esc(desc) + '</p></div><div class="row-actions">' + actions + '</div></div></li>';
  }
  function own() { return ' <span class="tag own">תבנית מקורית</span>'; }
  function viewBtn(path, name) { return '<button class="btn sm" type="button" data-view="' + esc(path) + '" data-name="' + esc(name) + '">צפייה</button>'; }
  function dlBtn(path, name, label, primary) { return '<button class="btn sm' + (primary ? ' primary' : '') + '" type="button" data-dl="' + esc(path) + '" data-name="' + esc(name) + '">' + icon('download') + esc(label || 'הורדה') + '</button>'; }

  var TABS = [['kit', 'ערכת פרויקט'], ['skills', 'Skills'], ['prompts', 'תבניות הנחיות'], ['guides', 'מדריכים'], ['logo', 'לוגו'], ['ext', 'משאבים קיימים']];

  function pane(k) {
    var L = TS.library;
    if (k === 'kit') return '<p class="prose" style="margin-bottom:10px">שבעה קבצים להקמת פרויקט קבוע ב־ChatGPT או ב־Claude. <a href="#adv-projects" data-route="adv-projects">מדריך ההקמה</a></p><ul class="rows">' +
      item('ערכת הפרויקט המלאה (ZIP)', 'כל הקבצים יחד, כולל הוראות הקמה.', own(), dlBtn(L.zips.kit, 'project-kit.zip', 'הורדת ZIP', true)) +
      L.kitFiles.map(function (f) { return item(f[1], f[2], '', viewBtn('downloads/project-kit/' + f[0], f[0]) + dlBtn('downloads/project-kit/' + f[0], f[0])); }).join('') + '</ul>';
    if (k === 'skills') return '<div class="callout warn" style="margin-bottom:14px">' + icon('warn') + '<p>התקינו Skills רק ממקורות מהימנים, וקראו את התוכן לפני הפעלה. אלה Skills מקוריים של הסטודיו, ארוזים לפי המפרט: תיקייה בשם ה־Skill ובתוכה <code>SKILL.md</code>. ב־Claude: Customize › Skills › + › Create skill › Upload a skill. <a href="#adv-skills" data-route="adv-skills">פרטים</a></p></div><ul class="rows">' +
      L.skills.map(function (s) { return item(s.title, s.desc + ' (' + s.id + ')', own(), viewBtn('downloads/skills/' + s.id + '/SKILL.md', s.id + '/SKILL.md') + dlBtn('downloads/skills/' + s.id + '.zip', s.id + '.zip', 'ZIP', true)); }).join('') + '</ul>';
    if (k === 'prompts') return '<p class="prose" style="margin-bottom:10px">קובץ Markdown לכל מסלול: הנחיה לדוגמה, הכלי המומלץ, בדיקת איכות והמשך עבודה. את ההנחיה המותאמת אליכם בונים בסטודיו.</p><ul class="rows">' +
      item('כל התבניות (ZIP)', 'שישה־עשר קבצי Markdown בקובץ אחד.', own(), dlBtn(L.zips.prompts, 'prompts.zip', 'הורדת ZIP', true)) +
      TS.tasks.map(function (t) { return item(t.title, t.short, '', viewBtn('downloads/prompts/' + t.id + '.md', t.id + '.md') + dlBtn('downloads/prompts/' + t.id + '.md', t.id + '-template.md') + '<a class="btn sm ghost" href="#task-' + t.id + '" data-route="task-' + t.id + '">למחולל</a>'); }).join('') + '</ul>';
    if (k === 'guides') return '<ul class="rows">' + L.guides.map(function (g) { return item(g[1], g[2], own(), viewBtn('downloads/' + g[0], g[0].split('/').pop()) + dlBtn('downloads/' + g[0], g[0].split('/').pop())); }).join('') + '</ul>';
    if (k === 'logo') return '<ul class="rows">' + item('לוגו חמ״ד בנים הר ברכה (PNG)', 'לשימוש בתוצרים. רקע שקוף מחוץ לעיגול. הלוגו הוא של בית הספר, ואינו תבנית של הסטודיו. מצרפים אותו לשיחה בכלי ה־AI כשמבקשים עיצוב עם לוגו.', '', '<img src="assets/logo.png" alt="" width="64" height="59" style="background:#fff;border-radius:50%;box-shadow:0 0 0 1px var(--line)">' + dlBtn('assets/logo.png', 'har-bracha-logo.png', 'הורדה', true)) + '</ul>';
    return '<p class="prose" style="margin-bottom:10px">חומרים של אחרים, לא תוצרים שלנו. הרישיון והתנאים הם של בעליהם. נבדק ב־' + TS.meta.checkedOn + '.</p><ul class="rows">' +
      L.external.map(function (e) { return '<li><div class="row-item" style="display:contents"><div><h4>' + esc(e.title) + ' <span class="tag">משאב קיים</span> <span class="tag chk">' + esc(e.by) + '</span></h4><p>' + esc(e.note) + '</p></div><div class="row-actions"><a class="btn sm" href="' + esc(e.url) + '" target="_blank" rel="noopener">למקור ' + icon('external') + '</a></div></div></li>'; }).join('') + '</ul>' +
      '<p class="hint" style="margin-top:14px">דווח במקורות משניים: ב־14.7.2026 הושקה תוכנית ״Claude for Teachers״ לבעלי תפקיד מאומת בארה״ב. לא נמצאה אינדיקציה לזמינות בישראל.</p>';
  }

  TS.views.library = function () {
    var L = TS.library, cur = TS.store.get('libtab', 'kit');
    var html =
      '<div class="wrap page-head"><span class="eyebrow">ספרייה</span><h1 data-words>הכול להורדה</h1><p class="lead" data-rv>הנחיות, תבניות, ערכת פרויקט ו־Skills. כל קובץ מסומן: תבנית מקורית שלנו, או משאב קיים של אחרים.</p>' +
      '<div class="row" data-rv="1">' + dlBtn(L.zips.everything, 'teachers-studio-kit.zip', 'הורדת הכול (ZIP)', true).replace('btn sm', 'btn lg mag') + '</div></div>' +
      '<div class="wrap" style="padding-bottom:60px"><div class="tabs-line" id="ltabs" role="tablist" aria-label="סוגי קבצים">' + TABS.map(function (t) { return '<button type="button" role="tab" data-t="' + t[0] + '" aria-selected="' + (t[0] === cur) + '">' + t[1] + '</button>'; }).join('') + '</div><div id="lpane" style="padding-top:18px">' + pane(cur) + '</div></div>';
    return {
      title: 'ספריית הורדות', html: html,
      after: function (root) {
        $('#ltabs', root).addEventListener('click', function (e) {
          var b = e.target.closest('[data-t]'); if (!b) return;
          cur = b.getAttribute('data-t'); TS.store.set('libtab', cur);
          $$('[data-t]', root).forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
          var p = $('#lpane', root); p.innerHTML = pane(cur); p.classList.remove('rise'); void p.offsetWidth; p.classList.add('rise');
        });
      }
    };
  };

})(window.TS = window.TS || {});
