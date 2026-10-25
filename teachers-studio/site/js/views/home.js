/* מסך הבית: ״מה תרצו להכין היום?״ */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$;

  function peek() {
    var t = TS.engine.byId('lesson');
    var full = TS.engine.build(t, TS.engine.exampleState(t)).text.split('\n');
    var want = ['פעל כמורה', '## הקשר', '- כיתה:', '- מקצוע:', '- נושא', '## מטרות', '## שלבי עבודה', '## מבנה התוצר', '## בדיקת איכות', '## אופן העבודה'];
    var keep = [];
    full.forEach(function (ln) { for (var k = 0; k < want.length; k++) { if (ln.indexOf(want[k]) === 0) { keep.push(ln); break; } } });
    return keep.map(function (ln, i) {
      var h = ln.indexOf('## ') === 0;
      return '<div class="pk' + (h ? ' h' : '') + '" style="animation-delay:' + (0.9 + 0.11 * i).toFixed(2) + 's">' + esc(h ? ln.slice(3) : ln) + '</div>';
    }).join('');
  }

  var QUICK = ['lesson', 'worksheet', 'test', 'parents', 'song', 'presentation'];

  TS.views.home = function () {
    var marquee = TS.tasks.concat(TS.tasks).map(function (t) { return '<a href="#task-' + t.id + '" data-route="task-' + t.id + '" tabindex="-1" aria-hidden="true">' + esc(t.title) + '</a>'; }).join('');

    var html =
      '<section class="hero"><div class="wrap hero-grid">' +
        '<div>' +
          '<img class="hero-logo" src="assets/logo.png" alt="לוגו חמ״ד בנים הר ברכה: מקום שהלב חפץ" width="80" height="73" data-rv>' +
          '<span class="eyebrow" data-rv="1">הסטודיו של חדר המורים</span>' +
          '<h1 data-words style="margin-top:14px">מה תרצו להכין היום?</h1>' +
          '<p class="lead" data-rv="2">בחרו משימה, ענו על כמה שאלות, וקבלו הנחיה מקצועית מוכנה להעתקה לכלי ה־AI שלכם.</p>' +
          '<div class="finder" data-rv="3"><button class="finder-in mag" id="home-find" type="button">' + icon('search') + '<span>חפשו: מבחן, שיר, הודעה להורים…</span><kbd>Ctrl K</kbd></button>' +
            '<div class="quick">' + QUICK.map(function (id) { var t = TS.engine.byId(id); return '<a href="#task-' + id + '" data-route="task-' + id + '">' + esc(t.title) + '</a>'; }).join('') + '<a href="#studio" data-route="studio">כל המסלולים ' + icon('arrow-left') + '</a></div></div>' +
          '<p class="fine" data-rv="4">האתר מכין הנחיות. את התוצר עצמו מקבלים בכלי ה־AI שלכם. בלי הרשמה ובלי איסוף נתונים.</p>' +
        '</div>' +
        '<div class="peek-wrap" data-rv="3" aria-hidden="true"><div class="card glass peek tilt"><div class="bar"><i></i><i></i><i></i></div><div class="pk-list">' + peek() + '</div></div></div>' +
      '</div></section>' +

      '<div class="marquee" aria-label="משימות לדוגמה"><div class="marquee-track">' + marquee + '</div></div>' +

      '<section class="section"><div class="wrap stack lg"><h2 data-rv>שלושה צעדים</h2><div class="steps3">' +
        '<div data-rv="1"><span class="n" aria-hidden="true">1</span><h3>בוחרים צורך</h3><p class="muted">שישה־עשר מסלולים, לכל אחד היגיון משלו.</p></div>' +
        '<div data-rv="2"><span class="n" aria-hidden="true">2</span><h3>עונים בקצרה</h3><p class="muted">אפשר לטעון דוגמה מלאה ולערוך אותה.</p></div>' +
        '<div data-rv="3"><span class="n" aria-hidden="true">3</span><h3>מעתיקים ומשפרים</h3><p class="muted">מדביקים בכלי ה־AI, בודקים, ומבקשים תיקון ממוקד.</p></div>' +
      '</div></div></section>' +

      '<section class="section tight"><div class="wrap stack lg"><div class="row between"><h2 data-rv>לאן ממשיכים</h2></div><div class="bento">' +
        '<a class="tile hl w4 spot" href="#story" data-route="story" data-rv><span class="ic">' + icon('brain') + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>הסיפור: הגאון והשולחן</h3><p>עשרה מושגים בסיפור אחד, עם משלים והדגמות שאפשר לנסות.</p></div></a>' +
        '<a class="tile spot" href="#studio" data-route="studio" data-rv="1"><span class="ic">' + icon('note') + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>הסטודיו</h3><p>כלי העבודה והמשימות.</p></div></a>' +
        '<a class="tile spot" href="#curriculum" data-route="curriculum" data-rv="1"><span class="ic">' + icon('map') + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>תוכניות לימודים</h3><p>מהמקור הרשמי אל המחולל.</p></div></a>' +
        '<a class="tile spot" href="#library" data-route="library" data-rv="2"><span class="ic">' + icon('folder') + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>ספריית הורדות</h3><p>ערכות, Skills ותבניות.</p></div></a>' +
        '<a class="tile spot" href="#training" data-route="training" data-rv="3"><span class="ic">' + icon('team') + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>מסלול ההדרכה</h3><p>שעה או שעה וחצי, ועוד ״הבוקר של המורה״.</p></div></a>' +
        '<a class="tile w3 spot" href="#advanced" data-route="advanced" data-rv="2" style="grid-column: span 6"><span class="ic">' + icon('spark') + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>העמקה למתקדמים</h3><p>פרויקטים וקובצי ידע, עיצוב דרך HTML, הערכה דיגיטלית ו־Skills.</p></div></a>' +
      '</div></div></section>' +

      '<section class="section tight"><div class="wrap"><div class="stats">' +
        '<div data-rv><b data-count="' + TS.tasks.length + '">0</b><span>מסלולי עבודה</span></div>' +
        '<div data-rv="1"><b data-count="' + TS.story.chapters.length + '">0</b><span>מושגים בסיפור</span></div>' +
        '<div data-rv="2"><b data-count="' + TS.library.skills.length + '">0</b><span>Skills מוכנים</span></div>' +
        '<div data-rv="3"><b data-count="' + TS.toolIds.length + '">0</b><span>כלים שנבדקו</span></div>' +
      '</div></div></section>';

    return {
      title: 'מה תרצו להכין היום', html: html,
      after: function (root) { $('#home-find', root).addEventListener('click', function () { TS.palette.open(); }); }
    };
  };

})(window.TS = window.TS || {});
