/* גשר לתוכניות הלימודים: כיתה, מקצוע, מקור רשמי, בחירת חומר ושליחה למחולל */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  TS.views.curriculum = function () {
    var C = TS.curriculum;
    var sel = TS.store.get('cur', { grade: '', subject: '' });
    var html =
      '<div class="wrap page-head"><span class="eyebrow">תוכניות לימודים</span><h1 data-words>מהמקור הרשמי להכנת תוצר</h1><p class="lead" data-rv>כיתה, מקצוע, מקור רשמי, ומשם אל המחולל.</p>' +
      '<details class="about" data-rv="1"><summary>' + icon('info') + 'מה האתר עושה כאן</summary><p>' + esc(C.note) + '</p></details></div>' +
      '<div class="wrap stack lg" style="padding-bottom:60px">' +
        '<section class="card stack" data-rv aria-labelledby="c1"><div class="row between"><h2 id="c1" style="font-size:1.6rem">1. כיתה ומקצוע</h2></div>' +
          '<fieldset><legend>כיתה (בחירה ידנית)</legend><div class="chips" id="cu-grade">' + TS.grades.map(function (g) { return '<label class="chip"><input type="radio" name="cg" value="' + esc(g) + '"' + (g === sel.grade ? ' checked' : '') + '><span>' + esc(g) + '</span></label>'; }).join('') + '</div></fieldset>' +
          '<fieldset><legend>מקצוע</legend><div class="chips" id="cu-subj">' + C.subjects.map(function (s) { return '<label class="chip"><input type="radio" name="cs" value="' + s.id + '"' + (s.id === sel.subject ? ' checked' : '') + '><span>' + esc(s.name) + (s.hemed ? ' <em>חמ״ד</em>' : '') + '</span></label>'; }).join('') + '</div></fieldset></section>' +
        '<section class="card stack" data-rv="1" aria-labelledby="c2"><h2 id="c2" style="font-size:1.6rem">2. המקור הרשמי</h2><div id="cu-source" class="stack"><p class="muted">בחרו מקצוע כדי לראות את הקישורים הרשמיים.</p></div>' +
          '<details class="acc"><summary><span>קישורים כלליים במרחב הפדגוגי</span><span class="pm">' + icon('plus') + '</span></summary><div class="acc-body"><ul class="plain">' + C.general.map(function (g) { return '<li><a href="' + esc(g.url) + '" target="_blank" rel="noopener">' + esc(g.label) + '</a></li>'; }).join('') + '</ul></div></details></section>' +
        '<section class="card stack" data-rv="2" aria-labelledby="c3" style="box-shadow:var(--shadow-2)"><h2 id="c3" style="font-size:1.6rem">3. מהמקור למחולל</h2>' +
          '<div class="form-grid"><div class="field"><label for="cu-topic">נושא או יחידה שבחרתם</label><input type="text" id="cu-topic" placeholder="לדוגמה: מחזור המים"></div>' +
          '<div class="field"><label for="cu-task">להכין</label><select id="cu-task">' + TS.tasks.map(function (t) { return '<option value="' + t.id + '"' + (t.id === 'lesson' ? ' selected' : '') + '>' + esc(t.title) + '</option>'; }).join('') + '</select></div>' +
          '<div class="field full"><label for="cu-text">קטע מהחומר (אופציונלי)</label><textarea id="cu-text" rows="5" placeholder="הדביקו קטע קצר שמותר לכם לשכפל, בלי מידע מזהה על תלמידים."></textarea><div class="warn-line" id="cu-pv" hidden></div><span class="hint">הקטע יועבר כמקור למחולל. לא נשלח לשום שרת.</span></div></div>' +
          '<div><button class="btn primary lg mag" type="button" id="cu-go">שליחה למחולל ' + icon('arrow-left', 'i-arrow') + '</button></div></section>' +
      '</div>';

    return {
      title: 'תוכניות לימודים', html: html,
      after: function (root) {
        function save() { TS.store.set('cur', { grade: ($('input[name=cg]:checked', root) || {}).value || '', subject: ($('input[name=cs]:checked', root) || {}).value || '' }); }
        function source() {
          var id = ($('input[name=cs]:checked', root) || {}).value, box = $('#cu-source', root);
          var s = C.subjects.filter(function (x) { return x.id === id; })[0];
          if (!s) { box.innerHTML = '<p class="muted">בחרו מקצוע כדי לראות את הקישורים הרשמיים.</p>'; return; }
          box.innerHTML = '<div class="rise stack"><p><b style="font-size:1.2rem">' + esc(s.name) + '</b> <span class="tag ok">קישור נבדק</span></p>' +
            '<div><a class="btn primary" href="' + esc(s.url) + '" target="_blank" rel="noopener">לעמוד המקצוע במרחב הפדגוגי ' + icon('external') + '</a></div>' +
            (s.links.length ? '<ul class="plain">' + s.links.map(function (l) { return '<li><a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + '</a></li>'; }).join('') + '</ul>' : '') +
            (s.tip ? '<p class="muted small">' + esc(s.tip) + '</p>' : '') + '<p class="hint">השיוך של הנושא לכיתה נקבע על ידכם: האתר אינו מאמת אותו.</p></div>';
        }
        $('#cu-subj', root).addEventListener('change', function () { save(); source(); });
        $('#cu-grade', root).addEventListener('change', save);
        $('#cu-text', root).addEventListener('input', function () {
          var r = TS.privacyScan(this.value), b = $('#cu-pv', root); b.hidden = !r.length; b.textContent = r.length ? r.join(' ') + ' אל תדביקו מידע מזהה.' : '';
        });
        $('#cu-go', root).addEventListener('click', function () {
          var task = TS.engine.byId($('#cu-task', root).value);
          var sid = ($('input[name=cs]:checked', root) || {}).value, subj = C.subjects.filter(function (x) { return x.id === sid; })[0];
          var st = TS.store.get('ws:' + task.id, null) || TS.engine.newState(task);
          st.values = st.values || {};
          var g = ($('input[name=cg]:checked', root) || {}).value; if (g) st.values.grade = g;
          if (subj && subj.studio) st.values.subject = subj.studio;
          var tp = $('#cu-topic', root).value.trim(); if (tp) st.values.topic = tp;
          var tx = $('#cu-text', root).value.trim(); if (tx) st.values.source = tx;
          TS.store.set('ws:' + task.id, st);
          TS.go('task-' + task.id);
        });
        source();
      }
    };
  };

})(window.TS = window.TS || {});
