/* ההדרכה: מסלול של שעה או שעה וחצי, הבוקר של המורה, ותמצית הסקר */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;
  var timerHandle = null;

  function tabs(cur) {
    var t = [['training', 'מסלול ההדרכה'], ['morning', 'הבוקר של המורה'], ['survey', 'מה למדנו מהסקר']];
    return '<div class="wrap"><div class="tabs" role="navigation" aria-label="אזורי ההדרכה">' + t.map(function (x) {
      return '<a href="#' + x[0] + '" data-route="' + x[0] + '"' + (x[0] === cur ? ' aria-current="page"' : '') + '>' + x[1] + '</a>';
    }).join('') + '</div></div>';
  }

  function agenda() {
    var T = TS.training;
    var mode = TS.store.get('len', 60);
    var html =
      '<div class="wrap page-head"><span class="eyebrow">ההדרכה</span><h1>מסלול ההדרכה</h1><p class="lead">' + esc(T.note) + '</p>' +
      '<div class="row" style="margin-top:8px"><div class="seg" role="group" aria-label="אורך ההדרכה"><button type="button" data-len="60" aria-pressed="' + (mode === 60) + '">60 דקות</button><button type="button" data-len="90" aria-pressed="' + (mode === 90) + '">90 דקות</button></div></div></div>' +
      tabs('training') +
      '<div class="wrap" style="padding-block:20px 50px"><div class="timer no-print" id="timer" aria-label="שעון מנחה"><span class="muted small">שעון מנחה</span><span id="tm-label" style="font-weight:600"></span><span class="clock" id="tm-clock">00:00</span>' +
        '<button class="btn sm primary" type="button" id="tm-go">' + icon('play') + 'הפעלה</button><button class="btn sm" type="button" id="tm-reset">' + icon('reset') + 'איפוס</button><button class="btn sm" type="button" id="tm-next">לתחנה הבאה ' + icon('arrow-left') + '</button></div>' +
        '<div id="stations"></div></div>';
    return {
      title: 'מסלול ההדרכה', html: html,
      after: function (root) {
        var idx = 0, left = 0, running = false;
        function mins(s) { return mode === 60 ? s.m60 : s.m90; }
        function draw() {
          var cum = 0;
          $('#stations', root).innerHTML = T.stations.map(function (s, i) {
            var start = cum; cum += mins(s);
            return '<section class="station' + (i === idx ? ' on' : '') + '" id="st-' + s.id + '" aria-labelledby="sh-' + s.id + '"><div class="time">' + mins(s) + '<small>דקות</small><small>דקה ' + start + '–' + cum + '</small></div>' +
              '<div class="stack"><h2 id="sh-' + s.id + '" style="font-size:1.5rem">' + (i + 1) + '. ' + esc(s.title) + '</h2><p>' + esc(s.what) + '</p>' +
              '<ul class="plain">' + s.steps.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
              '<p><b>תוצר:</b> ' + esc(s.deliver) + '</p><p class="muted small"><b>טיפ למנחה:</b> ' + esc(s.tip) + '</p>' +
              '<div class="row"><a class="btn" href="#' + s.route + '" data-route="' + s.route + '">למסך: ' + esc(s.routeLabel) + ' ' + icon('arrow-left') + '</a><button class="btn ghost sm no-print" type="button" data-pick="' + i + '">הפעלת השעון לתחנה</button></div></div></section>';
          }).join('') + '<p class="muted" style="margin-top:16px">סך הכול: ' + cum + ' דקות.</p>';
          label();
        }
        function fmt(sec) { var m = Math.floor(sec / 60), s = sec % 60; return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s; }
        function label() {
          var s = T.stations[idx];
          $('#tm-label', root).textContent = (idx + 1) + '. ' + s.title;
          var c = $('#tm-clock', root); c.textContent = fmt(left); c.classList.toggle('end', left === 0 && running === false && left !== mins(s) * 60);
          $('#tm-go', root).innerHTML = (running ? icon('pause') + 'השהיה' : icon('play') + 'הפעלה');
          $$('.station', root).forEach(function (el, i) { el.classList.toggle('on', i === idx); });
        }
        function stop() { clearInterval(timerHandle); timerHandle = null; running = false; }
        function setStation(i, auto) { stop(); idx = Math.max(0, Math.min(T.stations.length - 1, i)); left = mins(T.stations[idx]) * 60; label(); }
        function beep() { try { var C = window.AudioContext || window.webkitAudioContext, a = new C(), o = a.createOscillator(), g = a.createGain(); o.connect(g); g.connect(a.destination); o.frequency.value = 660; g.gain.value = .08; o.start(); setTimeout(function () { o.stop(); a.close(); }, 450); } catch (e) { /* בלי צליל */ } }
        function tick() { left--; if (left <= 0) { left = 0; stop(); beep(); TS.toast('הזמן לתחנה הסתיים'); } label(); }
        $('#tm-go', root).addEventListener('click', function () { if (running) { stop(); } else { if (left <= 0) left = mins(T.stations[idx]) * 60; running = true; timerHandle = setInterval(tick, 1000); } label(); });
        $('#tm-reset', root).addEventListener('click', function () { setStation(idx); });
        $('#tm-next', root).addEventListener('click', function () { setStation(idx + 1); });
        root.addEventListener('click', function (e) {
          var b = e.target.closest('[data-pick]'); if (b) { setStation(+b.getAttribute('data-pick')); $('#timer', root).scrollIntoView({ behavior: 'smooth', block: 'center' }); }
          var l = e.target.closest('[data-len]'); if (l) { mode = +l.getAttribute('data-len'); TS.store.set('len', mode); $$('[data-len]', root).forEach(function (x) { x.setAttribute('aria-pressed', String(+x.getAttribute('data-len') === mode)); }); setStation(idx); draw(); }
        });
        setStation(0); draw();
      }
    };
  }

  function morning() {
    var M = TS.training.morning;
    var html =
      '<div class="wrap page-head"><span class="eyebrow">ההדרכה</span><h1>הבוקר של המורה</h1><p class="lead">' + esc(M.lead) + '</p></div>' + tabs('morning') +
      '<div class="wrap stack lg" style="padding-block:24px 50px">' +
      M.phases.map(function (p, i) {
        return '<section class="panel stack" aria-labelledby="ph-' + p.id + '"><div class="row between"><h2 id="ph-' + p.id + '" style="font-size:1.6rem">' + esc(p.title) + '</h2><span class="tag brand">' + esc(p.time) + '</span></div>' +
          '<div class="cols c2"><div><ul class="plain">' + p.points.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
          '<p class="muted small" style="margin-top:10px">מסלולים מתאימים:</p><div class="row">' + p.tasks.map(function (id) { var t = TS.engine.byId(id); return '<a class="btn sm" href="#task-' + id + '" data-route="task-' + id + '">' + esc(t.title) + '</a>'; }).join('') + '</div></div>' +
          '<div class="codebox"><header><span>בקשה קצרה להעתקה</span><button class="btn sm" type="button" data-copy-sel="#mp-' + p.id + '">' + icon('copy') + 'העתקה</button></header><pre id="mp-' + p.id + '">' + esc(p.prompt) + '</pre></div></div></section>';
      }).join('') +
      '<section class="panel stack"><h2 style="font-size:1.4rem">' + esc(M.keep.title) + '</h2><p class="muted">שורות קצרות לסיום יום. אפשר לשמור בפרויקט, בקובץ ״יומן החלטות״ מערכת הפרויקט.</p><div class="codebox"><header><span>תבנית</span><button class="btn sm" type="button" data-copy-sel="#keep-pre">' + icon('copy') + 'העתקה</button></header><pre id="keep-pre">' + esc(M.keep.text) + '</pre></div></section></div>';
    return { title: 'הבוקר של המורה', html: html };
  }

  function survey() {
    var S = TS.training.survey, max = Math.max.apply(null, S.needs.map(function (n) { return n.count; }));
    function bars(arr, mx) { return '<div class="bars">' + arr.map(function (n) { return '<div class="bar-row"><span>' + esc(n.label || ('רמה ' + n.level)) + '</span><div class="bar" aria-hidden="true"><i style="width:' + (n.count / mx * 100) + '%"></i></div><b>' + n.count + '</b></div>'; }).join('') + '</div>'; }
    var html =
      '<div class="wrap page-head"><span class="eyebrow">ההדרכה</span><h1>מה למדנו מהסקר</h1><p class="lead">תמצית מצטברת של ' + S.n + ' תשובות לסקר הצרכים. בלי שמות, בלי ציטוטים מזהים ובלי נתונים גולמיים.</p></div>' + tabs('survey') +
      '<div class="wrap stack lg" style="padding-block:24px 50px"><div class="survey-grid">' +
        '<section class="panel stack"><h2 style="font-size:1.3rem">מה ביקשו להכין</h2>' + bars(S.needs, max) + '<p class="hint">' + esc(S.method) + '</p></section>' +
        '<section class="panel stack"><h2 style="font-size:1.3rem">' + esc(S.ratingScale) + '</h2>' + bars(S.rating, Math.max.apply(null, S.rating.map(function (r) { return r.count; }))) +
          '<h2 style="font-size:1.1rem;margin-top:12px">כלים שנזכרו</h2>' + bars(S.toolsAsked, max) + '</section></div>' +
      '<section class="panel stack"><h2 style="font-size:1.3rem">מה זה אומר על האתר</h2><ul class="plain">' + S.implications.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></section>' +
      '<div class="callout">' + icon('lock') + '<p>הסקר נקרא כדי לכוון את תוכן האתר. לא נשמרו בו נתונים אישיים, ולא מוצגות כאן תשובות בודדות.</p></div></div>';
    return { title: 'מה למדנו מהסקר', html: html };
  }

  TS.views.training = function (param) {
    if (timerHandle) { clearInterval(timerHandle); timerHandle = null; }
    if (param === 'morning') return morning();
    if (param === 'survey') return survey();
    return agenda();
  };

})(window.TS = window.TS || {});
