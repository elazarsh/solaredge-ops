/* מדריך כלים: מתי לבחור, מה להכין, איך מתחילים, מגבלות, ומה אומת */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  function li(arr) { return '<ul class="plain">' + arr.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>'; }
  function tag(s) { return '<span class="tag ' + s + '">' + esc(TS.statusLabels[s]) + '</span>'; }

  function toolHtml(id, open) {
    var t = TS.tools[id];
    return '<details class="tool" id="tool-' + id + '"' + (open ? ' open' : '') + '><summary><div><h3>' + esc(t.name) + ' <small>' + esc(t.maker) + ' · ' + esc(t.kind) + '</small></h3><small>' + esc(t.tagline) + '</small></div>' + icon('arrow-left') + '</summary>' +
      '<div class="tool-body">' +
        '<div><h4>מתי לבחור בו</h4>' + li(t.when) + '</div>' +
        '<div><h4>מה צריך להכין מראש</h4>' + li(t.prepare) + '</div>' +
        '<div><h4>איך מתחילים</h4><ol class="plain">' + t.start.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ol></div>' +
        '<div><h4>דוגמה למורה</h4><p>' + esc(t.example) + '</p></div>' +
        '<div><h4>מגבלות</h4>' + li(t.limits) + '</div>' +
        '<div><h4>עברית</h4><p>' + tag(t.hebrew.s) + '</p><p class="small" style="margin-top:6px">' + esc(t.hebrew.note) + '</p></div>' +
        '<div style="grid-column:1/-1"><h4>מה אומת ומה לא</h4>' + t.facts.map(function (f) { return '<div class="fact">' + tag(f.s) + '<span>' + esc(f.t) + '</span></div>'; }).join('') + '</div>' +
        '<div style="grid-column:1/-1" class="row"><a class="btn primary" href="' + esc(t.url) + '" target="_blank" rel="noopener">לאתר הכלי ' + icon('external') + '</a>' +
          t.sources.map(function (s) { return '<a class="btn sm" href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.label) + ' ' + icon('external') + '</a>'; }).join('') + '</div>' +
      '</div></details>';
  }

  TS.views.tools = function (param) {
    var html =
      '<div class="wrap page-head"><span class="eyebrow">כלים</span><h1>איזה כלי מתאים לי?</h1>' +
      '<p class="lead">תשעה כלים, מתי לבחור בכל אחד, מה להכין ואיך מתחילים. נבדק ב־' + TS.meta.checkedOn + '.</p></div>' +
      '<div class="wrap stack lg" style="padding-bottom:40px">' +
        '<div class="callout">' + icon('info') + '<div><p><b>איך לקרוא את הסימונים.</b> לכל טענה יש סימון שאומר עד כמה בדקנו אותה:</p><p class="row" style="margin-top:6px">' + tag('ok') + tag('sec') + tag('chk') + '</p><p class="small" style="margin-top:6px">לא הבטחנו מחיר, מגבלות שימוש, תמיכה בעברית או תכונה שלא אומתו במקור. מחירים ומגבלות משתנים: בדקו באתר הכלי.</p></div></div>' +
        '<section class="panel stack" aria-labelledby="pickt"><h2 id="pickt" style="font-size:1.4rem">לפי המשימה</h2><div class="field" style="max-width:420px"><label for="pick-task">מה אתם מכינים?</label><select id="pick-task"><option value="">בחרו משימה</option>' + TS.tasks.map(function (t) { return '<option value="' + t.id + '">' + esc(t.title) + '</option>'; }).join('') + '</select></div><div id="pick-out" class="muted small">בחרו משימה כדי לראות כלים מומלצים ולמה.</div></section>' +
        '<div class="stack">' + TS.toolIds.map(function (id) { return toolHtml(id, param === id); }).join('') + '</div>' +
        '<section class="stack"><h2 style="font-size:1.4rem">כלים נוספים שהוזכרו (לא נבדקו לעומק)</h2><ul class="plain">' + TS.moreTools.map(function (m) { return '<li><a href="' + esc(m.url) + '" target="_blank" rel="noopener">' + esc(m.name) + '</a>: ' + esc(m.note) + '</li>'; }).join('') + '</ul></section>' +
        '<div class="callout warn">' + icon('lock') + '<p><b>לפני שבוחרים:</b> לשימוש תלמידים בכלי AI יש הנחיות של משרד החינוך לפי כיתה, וכלים ברשימה מאושרת. <a href="#adv-privacy" data-route="adv-privacy">לעמוד הפרטיות</a>.</p></div>' +
      '</div>';
    return {
      title: 'כלים', html: html,
      after: function (root) {
        if (param) { var t = $('#tool-' + param, root); if (t) setTimeout(function () { t.scrollIntoView(); }, 60); }
        $('#pick-task', root).addEventListener('change', function () {
          var task = TS.engine.byId(this.value), out = $('#pick-out', root);
          if (!task) { out.innerHTML = 'בחרו משימה כדי לראות כלים מומלצים ולמה.'; return; }
          out.innerHTML = '<ul class="plain advice" style="list-style:none;padding:0">' + task.tools.map(function (x) {
            var t = TS.tools[x.id];
            return '<li><b><a href="#tool-' + x.id + '" data-route="tool-' + x.id + '">' + esc(t.name) + '</a></b><span>' + esc(x.why) + '</span></li>';
          }).join('') + '</ul>';
        });
      }
    };
  };

})(window.TS = window.TS || {});
