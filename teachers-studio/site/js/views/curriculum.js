/* גשר לתוכניות הלימודים: כיתה, מקצוע, מקור רשמי, בחירת חומר ושליחה למחולל */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  TS.views.curriculum = function () {
    var C = TS.curriculum;
    var sel = TS.store.get('cur', { grade: '', subject: '' });
    var html =
      '<div class="wrap page-head"><span class="eyebrow">חיבור לתוכניות הלימודים</span><h1>מהמקור הרשמי להכנת תוצר</h1>' +
      '<p class="lead">כיתה ← מקצוע ← מקור רשמי ← בחירת נושא או העתקת חומר ← הכנת תוצר בסטודיו.</p></div>' +
      '<div class="wrap stack lg" style="padding-bottom:40px">' +
        '<div class="callout">' + icon('info') + '<p>' + esc(C.note) + '</p></div>' +
        '<div class="how">' + C.steps.map(function (s) { return '<div><p>' + esc(s) + '</p></div>'; }).join('') + '</div>' +
        '<div class="cols c2"><section class="panel stack" aria-labelledby="c1"><h2 id="c1" style="font-size:1.4rem">1. כיתה ומקצוע</h2>' +
          '<div class="field"><label for="cu-grade">כיתה (בחירה ידנית)</label><select id="cu-grade"><option value="">בחרו כיתה</option>' + TS.grades.map(function (g) { return '<option' + (g === sel.grade ? ' selected' : '') + '>' + esc(g) + '</option>'; }).join('') + '</select></div>' +
          '<fieldset><legend>מקצוע</legend><div class="chips" id="cu-subj">' + C.subjects.map(function (s) { return '<label class="chip rad"><input type="radio" name="cs" value="' + s.id + '"' + (s.id === sel.subject ? ' checked' : '') + '><span>' + esc(s.name) + (s.hemed ? ' <em>חמ״ד</em>' : '') + '</span></label>'; }).join('') + '</div></fieldset>' +
          '<div class="stack"><h3 style="font-size:1.05rem">קישורים כלליים</h3><ul class="plain">' + C.general.map(function (g) { return '<li><a href="' + esc(g.url) + '" target="_blank" rel="noopener">' + esc(g.label) + '</a></li>'; }).join('') + '</ul></div>' +
        '</section>' +
        '<section class="panel stack" aria-labelledby="c2"><h2 id="c2" style="font-size:1.4rem">2. המקור הרשמי</h2><div id="cu-source" class="stack"><p class="muted">בחרו מקצוע כדי לראות את הקישורים הרשמיים.</p></div></section></div>' +
        '<section class="panel stack shadow" aria-labelledby="c3"><h2 id="c3" style="font-size:1.4rem">3. מהמקור למחולל</h2>' +
          '<div class="form-grid"><div class="field"><label for="cu-topic">נושא או יחידה שבחרתם</label><input type="text" id="cu-topic" placeholder="לדוגמה: מחזור המים"></div>' +
          '<div class="field"><label for="cu-task">להכין</label><select id="cu-task">' + TS.tasks.map(function (t) { return '<option value="' + t.id + '"' + (t.id === 'lesson' ? ' selected' : '') + '>' + esc(t.title) + '</option>'; }).join('') + '</select></div>' +
          '<div class="field full"><label for="cu-text">קטע מהחומר (אופציונלי)</label><textarea id="cu-text" rows="5" placeholder="הדביקו קטע קצר שמותר לכם לשכפל, בלי מידע מזהה על תלמידים."></textarea><div class="warn-line" id="cu-pv" hidden></div><span class="hint">הקטע יועבר כמקור למחולל. לא נשלח לשום שרת.</span></div></div>' +
          '<div class="row"><button class="btn primary lg" type="button" id="cu-go">שליחה למחולל ' + icon('arrow-left') + '</button></div></section>' +
      '</div>';

    return {
      title: 'תוכניות לימודים', html: html,
      after: function (root) {
        function source() {
          var id = ($('input[name=cs]:checked', root) || {}).value, box = $('#cu-source', root);
          var s = C.subjects.filter(function (x) { return x.id === id; })[0];
          if (!s) { box.innerHTML = '<p class="muted">בחרו מקצוע כדי לראות את הקישורים הרשמיים.</p>'; return; }
          box.innerHTML = '<p><b>' + esc(s.name) + '</b> <span class="tag ok">קישור נבדק ופתוח</span></p>' +
            '<a class="btn primary" href="' + esc(s.url) + '" target="_blank" rel="noopener">לעמוד המקצוע במרחב הפדגוגי ' + icon('external') + '</a>' +
            (s.links.length ? '<ul class="plain">' + s.links.map(function (l) { return '<li><a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + '</a></li>'; }).join('') + '</ul>' : '') +
            (s.tip ? '<p class="muted small">' + esc(s.tip) + '</p>' : '') +
            '<p class="hint">השיוך של הנושא לכיתה נקבע על ידכם: האתר אינו מאמת אותו.</p>';
        }
        $('#cu-subj', root).addEventListener('change', function () { TS.store.set('cur', { grade: $('#cu-grade', root).value, subject: ($('input[name=cs]:checked', root) || {}).value || '' }); source(); });
        $('#cu-grade', root).addEventListener('change', function () { TS.store.set('cur', { grade: this.value, subject: ($('input[name=cs]:checked', root) || {}).value || '' }); });
        $('#cu-text', root).addEventListener('input', function () {
          var r = TS.privacyScan(this.value), b = $('#cu-pv', root); b.hidden = !r.length; b.textContent = r.length ? r.join(' ') + ' אל תדביקו מידע מזהה.' : '';
        });
        $('#cu-go', root).addEventListener('click', function () {
          var task = TS.engine.byId($('#cu-task', root).value);
          var sid = ($('input[name=cs]:checked', root) || {}).value;
          var subj = C.subjects.filter(function (x) { return x.id === sid; })[0];
          var st = TS.store.get('ws:' + task.id, null) || TS.engine.newState(task);
          st.values = st.values || {};
          var g = $('#cu-grade', root).value; if (g) st.values.grade = g;
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
