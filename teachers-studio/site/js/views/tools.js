/* מדריך כלים: מתי לבחור, איך מתחילים, מגבלות, ומה אומת */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  function li(arr) { return '<ul class="plain">' + arr.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>'; }
  function tag(s) { return '<span class="tag ' + s + '">' + esc(TS.statusLabels[s]) + '</span>'; }

  var TABS = [['when', 'מתי לבחור'], ['start', 'איך מתחילים'], ['limits', 'מגבלות'], ['facts', 'מה אומת']];
  function panel(t, k) {
    if (k === 'when') return '<h4>מתי לבחור בו</h4>' + li(t.when) + '<h4 style="margin-top:20px">מה להכין מראש</h4>' + li(t.prepare) + '<h4 style="margin-top:20px">דוגמה למורה</h4><p class="prose">' + esc(t.example) + '</p>';
    if (k === 'start') return '<h4>איך מתחילים</h4><ol class="plain">' + t.start.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ol>';
    if (k === 'limits') return '<h4>מגבלות</h4>' + li(t.limits) + '<h4 style="margin-top:20px">עברית</h4><p>' + tag(t.hebrew.s) + '</p><p class="small muted" style="margin-top:6px">' + esc(t.hebrew.note) + '</p>';
    return '<h4>מה אומת ומה לא</h4>' + t.facts.map(function (f) { return '<div class="fact">' + tag(f.s) + '<span>' + esc(f.t) + '</span></div>'; }).join('') +
      '<div class="row" style="margin-top:18px"><a class="btn primary sm" href="' + esc(t.url) + '" target="_blank" rel="noopener">לאתר הכלי ' + icon('external') + '</a>' + t.sources.map(function (s) { return '<a class="btn sm" href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.label) + ' ' + icon('external') + '</a>'; }).join('') + '</div>';
  }

  function toolHtml(id, open) {
    var t = TS.tools[id];
    return '<details class="tool" id="tool-' + id + '"' + (open ? ' open' : '') + ' data-rv><summary><div><h3>' + esc(t.name) + ' <small>' + esc(t.maker) + ' · ' + esc(t.kind) + '</small></h3><p>' + esc(t.tagline) + '</p></div><span class="pm">' + icon('plus') + '</span></summary>' +
      '<div class="tool-body"><div class="tabs-line" role="tablist" aria-label="פרטי הכלי">' + TABS.map(function (x, i) { return '<button type="button" role="tab" data-tt="' + x[0] + '" aria-selected="' + (i === 0) + '">' + x[1] + '</button>'; }).join('') + '</div><div class="tool-panels"><div data-pane>' + panel(t, 'when') + '</div></div></div></details>';
  }

  TS.views.tools = function (param) {
    var html =
      '<div class="wrap page-head"><span class="eyebrow">כלים</span><h1 data-words>איזה כלי מתאים לי?</h1><p class="lead" data-rv>תשעה כלים: מתי לבחור, איך מתחילים, ומה בדקנו. נבדק ב־' + TS.meta.checkedOn + '.</p>' +
      '<div class="row" data-rv="1" style="gap:8px"><span class="small muted">רמת אימות:</span>' + tag('ok') + tag('sec') + tag('chk') + '</div></div>' +
      '<div class="wrap stack lg" style="padding-bottom:50px">' +
        '<div class="card flat stack" data-rv><h2 style="font-size:1.5rem">לפי המשימה</h2><div class="field" style="max-width:420px"><label for="pick-task">מה אתם מכינים?</label><select id="pick-task"><option value="">בחרו משימה</option>' + TS.tasks.map(function (t) { return '<option value="' + t.id + '">' + esc(t.title) + '</option>'; }).join('') + '</select></div><div id="pick-out" class="muted small" aria-live="polite">בחרו משימה כדי לראות כלים מומלצים ולמה.</div></div>' +
        '<div>' + TS.toolIds.map(function (id) { return toolHtml(id, param === id); }).join('') + '</div>' +
        '<details class="acc" data-rv><summary><span>כלים נוספים שהוזכרו (לא נבדקו לעומק)</span><span class="pm">' + icon('plus') + '</span></summary><div class="acc-body"><ul class="plain">' + TS.moreTools.map(function (m) { return '<li><a href="' + esc(m.url) + '" target="_blank" rel="noopener">' + esc(m.name) + '</a>: ' + esc(m.note) + '</li>'; }).join('') + '</ul></div></details>' +
        '<div class="callout warn" data-rv>' + icon('lock') + '<p>לא הבטחנו מחיר, מגבלות שימוש, תמיכה בעברית או תכונה שלא אומתו במקור. לשימוש תלמידים בכלי AI יש הנחיות של משרד החינוך לפי כיתה. <a href="#adv-privacy" data-route="adv-privacy">לעמוד הפרטיות</a></p></div>' +
      '</div>';
    return {
      title: 'כלים', html: html,
      after: function (root) {
        if (param) { var t = $('#tool-' + param, root); if (t) setTimeout(function () { t.scrollIntoView({ behavior: 'auto', block: 'center' }); }, 80); }
        root.addEventListener('click', function (e) {
          var b = e.target.closest('[data-tt]'); if (!b) return;
          var box = b.closest('.tool'), id = box.id.replace('tool-', '');
          $$('[data-tt]', box).forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
          $('[data-pane]', box).innerHTML = panel(TS.tools[id], b.getAttribute('data-tt'));
        });
        $('#pick-task', root).addEventListener('change', function () {
          var task = TS.engine.byId(this.value), out = $('#pick-out', root);
          if (!task) { out.innerHTML = 'בחרו משימה כדי לראות כלים מומלצים ולמה.'; return; }
          out.className = '';
          out.innerHTML = '<ul style="list-style:none;padding:0;margin:0">' + task.tools.map(function (x) {
            var t = TS.tools[x.id];
            return '<li class="rise" style="display:flex;gap:14px;padding:10px 0;border-bottom:1px solid var(--line)"><b style="min-width:7.5em"><a href="#tool-' + x.id + '" data-route="tool-' + x.id + '">' + esc(t.name) + '</a></b><span class="muted">' + esc(x.why) + '</span></li>';
          }).join('') + '</ul>';
        });
      }
    };
  };

})(window.TS = window.TS || {});
