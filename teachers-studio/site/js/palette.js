/* פלטת חיפוש ופקודות (Ctrl+K או /): קפיצה מהירה לכל משימה, מושג, כלי ועמוד */
(function (TS) {
  'use strict';
  var $ = TS.$, $$ = TS.$$, esc = TS.esc, icon = TS.icon;
  var P = TS.palette = {};
  var items = null, shown = [], sel = 0;

  function build() {
    var it = [];
    var pages = [['home', 'בית', 'מה תרצו להכין היום', 'spark'], ['story', 'הסיפור: הגאון והשולחן', 'מושגי יסוד של AI בסיפור אחד', 'brain'], ['studio', 'הסטודיו', 'שישה־עשר מסלולי עבודה', 'note'],
      ['lab', 'מעבדת הבקשה', 'איך לדייק בקשה ולעבוד עם מקורות', 'layers'], ['tools', 'מדריך כלים', 'מתי לבחור כל כלי', 'table'], ['curriculum', 'תוכניות לימודים', 'חיבור למקור הרשמי', 'map'],
      ['library', 'ספריית הורדות', 'ערכות, Skills ותבניות', 'folder'], ['training', 'מסלול ההדרכה', 'שעה או שעה וחצי', 'team'], ['morning', 'הבוקר של המורה', 'לפני, במהלך ואחרי השיעור', 'book'],
      ['adv-projects', 'פרויקטים וקובצי ידע', 'העמקה', 'folder'], ['adv-html', 'עיצוב דרך HTML', 'העמקה', 'window'], ['adv-assess', 'הערכה דיגיטלית', 'העמקה', 'check'],
      ['adv-skills', 'Skills, סוכנים ו־Hooks', 'העמקה', 'binder'], ['adv-privacy', 'פרטיות ואחריות', 'העמקה', 'lock']];
    pages.forEach(function (p) { it.push({ g: 'עמודים', t: p[1], s: p[2], ic: p[3], go: p[0], k: p[1] + ' ' + p[2] }); });
    TS.tasks.forEach(function (t) { it.push({ g: 'משימות', t: t.title, s: t.short, ic: 'note', go: 'task-' + t.id, k: t.title + ' ' + t.short + ' ' + t.output }); });
    TS.story.chapters.forEach(function (c) { it.push({ g: 'מושגים', t: c.term, s: c.title + ' · ' + c.hook, ic: c.icon, go: 'ch-' + c.id, k: c.term + ' ' + c.title + ' ' + c.hook }); });
    TS.toolIds.forEach(function (id) { var t = TS.tools[id]; it.push({ g: 'כלים', t: t.name, s: t.tagline, ic: 'spark', go: 'tool-' + id, k: t.name + ' ' + t.tagline + ' ' + t.kind }); });
    it.push({ g: 'פעולות', t: 'הערכה שלי', s: 'ההנחיות ששמרתם', ic: 'kit', act: function () { TS.kit.render(); TS.openDialog($('#kit')); }, k: 'הערכה שמורות kit' });
    it.push({ g: 'פעולות', t: 'החלפת ערכת צבעים', s: 'אוטומטי, בהיר, כהה', ic: 'sliders', act: function () { $('#pf-theme').click(); }, k: 'כהה בהיר מצב לילה theme dark' });
    it.push({ g: 'פעולות', t: 'תצוגת הקרנה', s: 'טקסט גדול לכיתה', ic: 'window', act: function () { $('#pf-size').click(); }, k: 'הקרנה גדול' });
    it.push({ g: 'פעולות', t: 'הפחתת תנועה', s: 'כיבוי אנימציות', ic: 'sliders', act: function () { $('#pf-motion').click(); }, k: 'תנועה אנימציה נגישות' });
    return it;
  }

  function filter(q) {
    q = q.trim().toLowerCase();
    if (!q) {
      var seen = {}, base = [];
      items.forEach(function (x) { if (x.g === 'משימות' || x.g === 'עמודים') { if (base.length < 9) base.push(x); } });
      return base;
    }
    var toks = q.split(/\s+/);
    return items.map(function (x) {
      var h = x.k.toLowerCase(), score = 0;
      for (var i = 0; i < toks.length; i++) { var at = h.indexOf(toks[i]); if (at < 0) return null; score += at === 0 ? 3 : (x.t.toLowerCase().indexOf(toks[i]) > -1 ? 2 : 1); }
      return { x: x, s: score };
    }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).map(function (r) { return r.x; }).slice(0, 24);
  }

  function draw() {
    var list = $('#cmd-list'), last = '';
    if (!shown.length) { list.innerHTML = '<div class="cmd-empty">לא נמצאה תוצאה. נסו מילה אחרת.</div>'; return; }
    list.innerHTML = shown.map(function (x, i) {
      var head = x.g !== last ? '<div class="cmd-group" role="presentation">' + esc(x.g) + '</div>' : ''; last = x.g;
      return head + '<button type="button" class="cmd-item" role="option" id="cmd-' + i + '" data-i="' + i + '" aria-selected="' + (i === sel) + '"><span class="ic">' + icon(x.ic) + '</span><span><b>' + esc(x.t) + '</b><small>' + esc(x.s) + '</small></span></button>';
    }).join('');
    var cur = $('#cmd-' + sel); if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest' });
    $('#cmd-q').setAttribute('aria-activedescendant', 'cmd-' + sel);
  }

  function run(i) {
    var x = shown[i]; if (!x) return;
    TS.closeDialog($('#cmd'));
    if (x.act) x.act(); else TS.go(x.go);
  }

  P.open = function (pre) {
    if (!items) items = build();
    var d = $('#cmd'), q = $('#cmd-q');
    q.value = pre || ''; sel = 0; shown = filter(q.value); draw();
    TS.openDialog(d); setTimeout(function () { q.focus(); }, 20);
  };

  P.init = function () {
    $('#btn-cmd').addEventListener('click', function () { P.open(); });
    $('#cmd-q').addEventListener('input', function () { sel = 0; shown = filter(this.value); draw(); });
    $('#cmd-q').addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(shown.length - 1, sel + 1); draw(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(0, sel - 1); draw(); }
      else if (e.key === 'Enter') { e.preventDefault(); run(sel); }
    });
    $('#cmd-list').addEventListener('click', function (e) { var b = e.target.closest('.cmd-item'); if (b) run(+b.getAttribute('data-i')); });
    $('#cmd-list').addEventListener('pointermove', function (e) { var b = e.target.closest('.cmd-item'); if (b && +b.getAttribute('data-i') !== sel) { sel = +b.getAttribute('data-i'); $$('.cmd-item').forEach(function (n, i) { n.setAttribute('aria-selected', String(i === sel)); }); } });
    document.addEventListener('keydown', function (e) {
      var tag = (e.target.tagName || '').toLowerCase();
      var typing = tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable;
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); P.open(); }
      else if (e.key === '/' && !typing && !e.ctrlKey && !e.metaKey) { e.preventDefault(); P.open(); }
    });
  };

})(window.TS = window.TS || {});
