/* מסך הבית: ״מה תרצו להכין היום?״ */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon;

  function taskLink(t) {
    return '<li class="task" data-q="' + esc(t.title + ' ' + t.short + ' ' + t.output) + '">' +
      '<a class="task-link" href="#task-' + t.id + '" data-route="task-' + t.id + '"><span><b>' + esc(t.title) + '</b><small>' + esc(t.short) + '</small></span>' + icon('arrow-left') + '</a></li>';
  }

  function peek() {
    var t = TS.engine.byId('lesson');
    var s = TS.engine.exampleState(t);
    var full = TS.engine.build(t, s).text.split('\n');
    var keep = [];
    var want = ['פעל כמורה', '## הקשר', '- כיתה:', '- מקצוע:', '- נושא', '## מטרות', '## שלבי עבודה', '## מבנה התוצר', '## בדיקת איכות', '## אופן העבודה'];
    full.forEach(function (ln, i) {
      for (var k = 0; k < want.length; k++) { if (ln.indexOf(want[k]) === 0) { keep.push(ln); break; } }
    });
    return keep.map(function (ln, i) {
      var h = ln.indexOf('## ') === 0;
      return '<div class="pk ' + (h ? 'h' : '') + ' rise" style="animation-delay:' + (0.08 * i) + 's">' + esc(h ? ln.slice(3) : ln) + '</div>';
    }).join('');
  }

  var paths = [
    { r: 'story', ic: 'brain', t: 'הסיפור שמסביר איך AI עובד', d: 'הגאון והשולחן: עשרה מושגים בסיפור אחד' },
    { r: 'studio', ic: 'note', t: 'כלי העבודה והמשימות', d: 'שישה־עשר מסלולים ומעבדה לשיפור בקשות' },
    { r: 'curriculum', ic: 'map', t: 'חיבור לתוכניות הלימודים', d: 'כיתה, מקצוע, מקור רשמי ומשם למחולל' },
    { r: 'library', ic: 'folder', t: 'ספריית ההורדות', d: 'הנחיות, תבניות, ערכת פרויקט ו־Skills' },
    { r: 'training', ic: 'team', t: 'מסלול ההדרכה', d: 'שעה או שעה וחצי, תחנה אחר תחנה' },
    { r: 'advanced', ic: 'spark', t: 'העמקה למתקדמים', d: 'פרויקטים, HTML, הערכה דיגיטלית ו־Skills' }
  ];

  TS.views.home = function () {
    var groups = TS.groups.map(function (g) {
      var items = TS.tasks.filter(function (t) { return t.group === g.id; });
      return '<section class="dir-group" aria-labelledby="g-' + g.id + '"><h3 id="g-' + g.id + '">' + esc(g.label) + '<small>' + esc(g.hint) + '</small></h3><ul>' + items.map(taskLink).join('') + '</ul></section>';
    }).join('');

    var html =
      '<div class="hero"><div class="wrap hero-in" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));align-items:center">' +
        '<div class="stack lg">' +
          '<div class="stack"><img class="hero-logo rise" src="assets/logo.png" alt="לוגו חמ״ד בנים הר ברכה: מקום שהלב חפץ" width="120" height="110"><span class="eyebrow rise">הסטודיו של חדר המורים · חמ״ד בנים הר ברכה</span>' +
          '<h1 class="rise d1">מה תרצו להכין היום?</h1>' +
          '<p class="lead rise d2">בחרו משימה אמיתית מהשבוע שלכם, ענו על כמה שאלות, וקבלו הנחיה מקצועית מוכנה להעתקה לכלי הבינה המלאכותית שלכם.</p></div>' +
          '<div class="search rise d3" role="search">' + icon('search') + '<label class="sr" for="task-q">חיפוש משימה</label><input id="task-q" type="search" placeholder="חפשו: מבחן, שיר, הודעה להורים…" autocomplete="off"></div>' +
        '</div>' +
        '<aside class="panel shadow peek" aria-label="דוגמה להנחיה מוכנה"><div class="row between"><b>כך נראית הנחיה מוכנה</b><span class="tag brand">דוגמה: תכנון שיעור</span></div><div class="pk-list" aria-hidden="true">' + peek() + '</div><p class="hint">ההנחיה המלאה מתקבלת אחרי ארבעה שלבים קצרים.</p></aside>' +
      '</div></div>' +
      '<hr class="ruler">' +
      '<section class="section tight" aria-labelledby="pick"><div class="wrap stack lg">' +
        '<div class="row between"><h2 id="pick">בחרו משימה</h2><a class="btn ghost" href="#lab" data-route="lab">מעבדת הבקשה: איך לדייק ' + icon('arrow-left') + '</a></div>' +
        '<div class="dir" id="dir">' + groups + '</div><p class="no-results" id="no-results" hidden>לא נמצאה משימה כזו. נסו מילה אחרת, או עיינו ברשימה המלאה.</p>' +
      '</div></section>' +
      '<section class="section alt" aria-labelledby="how"><div class="wrap stack lg">' +
        '<h2 id="how">איך זה עובד</h2>' +
        '<div class="how"><div><b>בוחרים צורך</b><p class="muted">משימה אחת מתוך שישה־עשר מסלולים, לכל אחד היגיון משלו.</p></div>' +
        '<div><b>עונים בקצרה</b><p class="muted">מה מלמדים, איך ולמי, ואיך התוצר ייראה. אפשר לטעון דוגמה מלאה ולערוך אותה.</p></div>' +
        '<div><b>מעתיקים וממשיכים</b><p class="muted">מדביקים בכלי ה־AI שלכם, בודקים מול רשימת האיכות, ומבקשים תיקון ממוקד.</p></div></div>' +
        '<div class="callout">' + icon('info') + '<div><p><b>מה האתר עושה ומה לא.</b> האתר בונה לכם הנחיות מדויקות ומלמד את הרעיונות שמאחוריהן. הוא <b>אינו מפעיל מודל AI</b>. את התוצר עצמו מקבלים בכלי שאתם בוחרים (למשל ChatGPT, Claude או Gemini).</p><p>האתר אינו דורש הרשמה ואינו אוסף נתונים. בחירות ושמירות נשארות בדפדפן שלכם בלבד.</p></div></div>' +
      '</div></section>' +
      '<section class="section" aria-labelledby="six"><div class="wrap stack lg"><h2 id="six">ששה שבילים</h2><div class="paths">' +
        paths.map(function (p) { return '<a class="path" href="#' + p.r + '" data-route="' + p.r + '"><span class="ic">' + icon(p.ic) + '</span><span><b>' + esc(p.t) + '</b><small>' + esc(p.d) + '</small></span>' + icon('arrow-left') + '</a>'; }).join('') +
      '</div></div></section>' +
      '<section class="section alt" aria-labelledby="mor"><div class="wrap stack"><h2 id="mor">הבוקר של המורה</h2>' +
        '<p class="lead">שגרה קצרה סביב כל שיעור: לפני, במהלך ואחרי.</p>' +
        '<div class="cols">' + TS.training.morning.phases.map(function (p) {
          return '<div class="stack"><h3>' + esc(p.title) + '</h3><p class="muted small">' + esc(p.time) + '</p><ul class="plain">' + p.points.slice(0, 3).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
        }).join('') + '</div>' +
        '<div><a class="btn" href="#morning" data-route="morning">לשגרה המלאה ' + icon('arrow-left') + '</a></div>' +
      '</div></section>';

    return {
      title: 'מה תרצו להכין היום',
      html: html,
      after: function (root) {
        var q = TS.$('#task-q', root), none = TS.$('#no-results', root);
        q.addEventListener('input', function () {
          var term = q.value.trim().toLowerCase(), shown = 0;
          TS.$$('.task', root).forEach(function (li) {
            var ok = !term || li.getAttribute('data-q').toLowerCase().indexOf(term) > -1;
            li.hidden = !ok; if (ok) shown++;
          });
          TS.$$('.dir-group', root).forEach(function (g) { g.hidden = !TS.$$('.task:not([hidden])', g).length; });
          none.hidden = shown > 0;
        });
      }
    };
  };

})(window.TS = window.TS || {});
