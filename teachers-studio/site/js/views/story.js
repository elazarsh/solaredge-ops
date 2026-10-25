/* הסיפור: הגאון והשולחן. לכל מושג משל, הדגמה אינטראקטיבית והרחבה בשכבות. */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  /* ---------- איור הפתיחה ---------- */
  function person(cx, cy, r) {
    return '<circle class="pp" cx="' + cx + '" cy="' + cy + '" r="' + r + '"/><path class="st" d="M' + (cx - r * 1.5) + ' ' + (cy + r * 3.4) + ' C' + (cx - r * 1.5) + ' ' + (cy + r * 1.6) + ' ' + (cx - r * 0.8) + ' ' + (cy + r * 1.2) + ' ' + cx + ' ' + (cy + r * 1.2) + ' C' + (cx + r * 0.8) + ' ' + (cy + r * 1.2) + ' ' + (cx + r * 1.5) + ' ' + (cy + r * 1.6) + ' ' + (cx + r * 1.5) + ' ' + (cy + r * 3.4) + '"/>';
  }
  function art() {
    return '<svg viewBox="0 0 440 300" role="img" aria-label="איור: גאון ליד שולחן עבודה, עם תיק פרויקט, קלסרי שיטות, ספרייה, צוות, פעמון ומורה אחראי">' +
      '<ellipse class="sc-ring" cx="220" cy="150" rx="150" ry="104" fill="none" stroke="var(--brand)" stroke-width="1.5" stroke-dasharray="4 8" opacity=".5"/>' +
      '<path class="st" d="M20 276 H420" opacity=".4"/>' +
      '<rect class="pp" x="90" y="200" width="260" height="12" rx="4"/><path class="st" d="M108 212 V276 M332 212 V276"/>' +
      '<g class="sc-float d2"><circle class="pp" cx="220" cy="110" r="22"/><path class="st" d="M203 104 C206 88 234 88 237 104"/><path class="fl" d="M186 200 C186 154 196 136 220 136 C244 136 254 154 254 200 Z"/><path class="st" d="M208 160 h24 M208 168 h24 M220 154 v22"/></g>' +
      '<g class="sc-float"><rect class="pp" x="116" y="168" width="34" height="32" rx="3"/><path class="st" d="M122 177 h22 M122 184 h22 M122 191 h12"/></g>' +
      '<g class="sc-float d3"><path class="fl" d="M284 176 h16 l5 5 h26 v19 h-47 z"/></g>' +
      '<g class="sc-float d3"><rect class="fl" x="36" y="96" width="14" height="62" rx="2"/><rect class="fb" x="54" y="90" width="14" height="68" rx="2" opacity=".85"/><rect class="fl" x="72" y="100" width="14" height="58" rx="2"/><path class="st" d="M28 160 H94"/></g>' +
      '<g class="sc-float d2"><path class="st" d="M330 62 H424 M330 106 H424"/><rect class="fl" x="336" y="72" width="10" height="32"/><rect class="fb" x="348" y="68" width="10" height="36"/><rect class="fl" x="360" y="74" width="10" height="30"/><rect class="fl" x="372" y="70" width="10" height="34"/><rect class="fb" x="384" y="74" width="10" height="30" opacity=".7"/><rect class="fl" x="396" y="66" width="10" height="38"/>' + person(386, 138, 8) + '</g>' +
      '<g class="sc-float">' + person(60, 222, 7) + person(100, 222, 7) + person(140, 222, 7) + '</g>' +
      '<g class="sc-float d3"><path class="st" d="M52 0 V26"/><path class="fl" d="M38 52 C38 38 44 30 52 30 C60 30 66 38 66 52 L70 58 H34 Z"/></g>' +
      '<g class="sc-float d2">' + person(380, 232, 8) + '<circle class="fb" cx="410" cy="214" r="12"/><path d="M404 214 l4 4 l8 -10" fill="none" stroke="var(--brand-ink)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>' +
    '</svg>';
  }

  /* ---------- מסך מדומה ---------- */
  function mock(m) {
    var side = m.side ? '<div class="mk-side"><b>' + esc(m.sideTitle || 'בצד') + '</b>' + m.side.map(function (s) { return '<div class="mk-row' + (s.on ? ' on' : '') + '">' + esc(s.t) + '</div>'; }).join('') + '</div>' : '';
    return '<div class="mock" aria-label="הדמיית מסך"><div class="mk-bar"><i></i><i></i><i></i><span>' + esc(m.title) + '</span></div><div class="mk-body' + (m.side ? '' : ' one') + '">' + side +
      '<div class="mk-main">' + m.msgs.map(function (x) { return '<div class="mk-msg ' + x.r + '">' + esc(x.t) + '</div>'; }).join('') + '</div></div><div class="mk-foot mk-note">' + esc(m.note) + '</div></div>';
  }

  /* ---------- שכבות ההרחבה ---------- */
  var TABS = [['plain', 'במילים פשוטות'], ['see', 'איך זה נראה במסך'], ['class', 'בכיתה'], ['not', 'מה זה לא'], ['deep', 'למעמיקים']];
  function tabBody(c, k) {
    if (k === 'plain') {
      var t = c.table ? '<div class="tbl-wrap" style="margin-top:18px"><table class="tbl"><thead><tr><th>מושג</th><th>מה זה</th></tr></thead><tbody>' + c.table.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + esc(r.v) + '</td></tr>'; }).join('') + '</tbody></table></div>' : '';
      return '<div class="prose"><p>' + esc(c.plain) + '</p></div>' + t;
    }
    if (k === 'see') return mock(c.see);
    if (k === 'class') return '<h4>איך משתמשים בזה</h4><ul class="plain prose">' + c.classroom.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    if (k === 'not') return '<h4>שלוש הבהרות שחוסכות בלבול</h4><ul class="plain prose">' + c.notThis.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    return '<h4>קצת יותר לעומק</h4><p class="prose">' + esc(c.deep) + '</p><h4 style="margin-top:22px">מה המשל מפשט?</h4><p class="prose">' + esc(c.simplifies) + '</p>';
  }

  /* ---------- הדגמות ---------- */
  var demos = {};

  demos.finderr = function (el, D) {
    var tries = 0, done = false;
    el.innerHTML = '<p>' + esc(D.intro) + '</p><p class="rtl-par" style="line-height:2.1">' + D.sentences.map(function (s, i) { return '<span class="sent" tabindex="0" role="button" data-i="' + i + '">' + esc(s) + '</span> '; }).join('') + '</p><div class="dm-out" role="status" aria-live="polite">לחצו על משפט.</div>';
    function pick(n) {
      if (done) return;
      var out = $('.dm-out', el), s = $('.sent[data-i="' + n + '"]', el);
      tries++;
      if (n === D.wrong) { done = true; s.classList.add('wrong'); out.className = 'dm-out good'; out.textContent = D.why + (tries === 1 ? ' מצאתם בניסיון הראשון.' : ' ניסיונות: ' + tries + '.'); }
      else { s.classList.add('right'); out.className = 'dm-out'; out.textContent = 'המשפט הזה נכון. נסו עוד אחד.'; }
    }
    el.addEventListener('click', function (e) { var s = e.target.closest('.sent'); if (s) pick(+s.getAttribute('data-i')); });
    el.addEventListener('keydown', function (e) { var s = e.target.closest('.sent'); if (s && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); pick(+s.getAttribute('data-i')); } });
  };

  demos.guess = function (el, D) {
    var set = {};
    function draw() {
      var left = D.unknowns.filter(function (u) { return !set[u.id]; }).length;
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="dm-out"><b>' + esc(D.request) + '</b><div class="dm-btns" style="margin-top:12px">' +
        D.unknowns.map(function (u) { return '<button type="button" class="unk' + (set[u.id] ? ' set' : '') + '" data-u="' + u.id + '">' + esc(set[u.id] ? u.a : u.q) + '</button>'; }).join('') + '</div></div>' +
        '<div class="row between"><span>ניחושים שהגאון צריך לעשות: <b>' + left + '</b></span><button class="btn sm ghost" type="button" data-reset>איפוס</button></div>' +
        '<div class="meter" aria-hidden="true"><i style="width:' + (100 - left * 20) + '%"></i></div>' +
        '<p class="small muted" role="status" aria-live="polite">' + (left === 0 ? 'עכשיו הוא לא צריך לנחש. בסטודיו כל מסלול שואל בדיוק את השאלות האלה.' : 'כל סימן שאלה הוא החלטה שהמודל יקבל במקומכם.') + '</p>';
    }
    el.addEventListener('click', function (e) {
      var u = e.target.closest('[data-u]'); if (u) { set[u.getAttribute('data-u')] = !set[u.getAttribute('data-u')]; draw(); }
      if (e.target.closest('[data-reset]')) { set = {}; draw(); }
    });
    draw();
  };

  demos.newchat = function (el, D) {
    var s = { proj: true, mem: false, msgs: 3 };
    function draw() {
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="layers">' + D.layers.map(function (l) {
        var on = l.id === 'train' || (l.id === 'proj' && s.proj) || (l.id === 'mem' && s.mem) || (l.id === 'chat' && s.msgs > 0);
        var sub = l.id === 'chat' ? (s.msgs + ' הודעות בשיחה') : l.s;
        return '<div class="layer' + (on ? '' : ' off') + '"><span><b>' + esc(l.t) + '</b><br><small>' + esc(sub) + '</small></span><span class="tag ' + (on ? 'ok' : '') + '">' + (on ? 'על השולחן' : 'לא כאן') + '</span></div>';
      }).join('') + '</div><div class="dm-btns"><button class="dm-btn' + (s.proj ? ' on' : '') + '" data-a="proj">פרויקט</button><button class="dm-btn' + (s.mem ? ' on' : '') + '" data-a="mem">זיכרון מוצר</button><button class="dm-btn" data-a="msg">הודעה בשיחה</button><button class="dm-btn" data-a="new">שיחה חדשה</button></div>' +
        '<p class="small muted" role="status" aria-live="polite">' + (s.msgs === 0 ? 'השולחן נוקה: מה שנשאר הוא רק מה שנשמר מחוץ לשיחה.' : 'כל ההודעות בשיחה חלק מהקונטקסט כל עוד יש מקום.') + '</p>';
    }
    el.addEventListener('click', function (e) {
      var b = e.target.closest('[data-a]'); if (!b) return; var a = b.getAttribute('data-a');
      if (a === 'proj') s.proj = !s.proj; if (a === 'mem') s.mem = !s.mem; if (a === 'msg') s.msgs++; if (a === 'new') s.msgs = 0; draw();
    });
    draw();
  };

  demos.desk = function (el) {
    var d = TS.story.desk;
    el.innerHTML = '<p>סמנו מה מונח על השולחן וראו מתי משהו נופל.</p><div class="stack" style="gap:6px">' + d.items.map(function (it) {
      return '<label class="chip" style="display:flex"><input type="checkbox" data-desk="' + it.id + '"' + (it.on ? ' checked' : '') + '><span style="width:100%;justify-content:space-between">' + esc(it.label) + ' <em>' + it.size + '</em></span></label>';
    }).join('') + '</div><div class="desk-bar" id="desk-bar" role="img" aria-label="מילוי השולחן"></div><div class="row between"><span class="small muted">קיבולת: ' + d.capacity + ' יחידות להמחשה</span><b id="desk-sum"></b></div><p id="desk-msg" role="status" aria-live="polite" style="font-weight:600"></p>';
    function draw() {
      var sum = 0, parts = '', i = 0;
      $$('[data-desk]', el).forEach(function (cb) {
        if (!cb.checked) return;
        var it = d.items.filter(function (x) { return x.id === cb.getAttribute('data-desk'); })[0];
        i++;
        var room = Math.max(0, d.capacity - sum), used = Math.min(room, it.size);
        if (used > 0) parts += '<span class="f' + Math.min(i, 5) + '" style="width:' + (used / d.capacity * 100) + '%" title="' + esc(it.label) + '">' + (used >= 10 ? esc(it.label.split(' ')[0]) : '') + '</span>';
        if (it.size > used) parts += '<span class="over" style="width:' + Math.max(3, (it.size - used) / d.capacity * 100) + '%" title="לא נכנס: ' + esc(it.label) + '">!</span>';
        sum += it.size;
      });
      $('#desk-bar', el).innerHTML = parts; $('#desk-sum', el).textContent = sum + ' מתוך ' + d.capacity;
      var m = $('#desk-msg', el);
      if (sum > d.capacity) { m.style.color = 'var(--bad)'; m.textContent = 'השולחן מלא. משהו לא נכנס: הכלי יקצץ, יסכם או ישכח. שיחה חדשה, קובץ קצר יותר, והחומר החשוב קרוב לבקשה.'; }
      else if (sum > d.capacity * 0.8) { m.style.color = 'var(--warn)'; m.textContent = 'כמעט מלא. עוד קצת, והפרטים הראשונים ייעלמו.'; }
      else { m.style.color = 'var(--ok)'; m.textContent = 'יש מקום. הגאון רואה הכול.'; }
    }
    el.addEventListener('change', draw); draw();
  };

  demos.project = function (el, D) {
    var a = 0, b = 0, chats = 0;
    function draw() {
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="cols" style="gap:14px"><div class="layer"><span><b>בלי פרויקט</b><br><small>מקלידים את ההוראות בכל שיחה</small></span><b style="font-size:1.6rem">' + a + '</b></div><div class="layer"><span><b>עם פרויקט</b><br><small>מגדירים פעם אחת</small></span><b style="font-size:1.6rem;color:var(--ok)">' + b + '</b></div></div>' +
        '<div class="dm-out">הוראות קבועות: ' + D.lines.map(esc).join(' · ') + '</div><div class="row"><button class="btn sm primary" type="button" data-a="chat">פתחו שיחה חדשה (' + chats + ')</button><button class="btn sm ghost" type="button" data-a="reset">איפוס</button></div>' +
        '<p class="small muted" role="status" aria-live="polite">' + (chats === 0 ? 'פתחו כמה שיחות במהלך שבוע וספרו כמה פעמים הקלדתם הוראות.' : 'אחרי ' + chats + ' שיחות: ' + a + ' שורות מול ' + b + '. התיק משותף, והשיחות נשארות נפרדות.') + '</p>';
    }
    el.addEventListener('click', function (e) {
      var x = e.target.closest('[data-a]'); if (!x) return;
      if (x.getAttribute('data-a') === 'chat') { chats++; a += D.lines.length; if (chats === 1) b += D.lines.length; } else { a = 0; b = 0; chats = 0; }
      draw();
    });
    draw();
  };

  demos.skill = function (el, D) {
    var cur = null;
    function draw() {
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="dm-btns">' + D.asks.map(function (q, i) { return '<button class="dm-btn' + (cur === i ? ' on' : '') + '" data-q="' + i + '">' + esc(q.t) + '</button>'; }).join('') + '</div>' +
        '<div class="layers">' + D.skills.map(function (s) {
          var on = cur !== null && D.asks[cur].s === s.id;
          return '<div class="layer' + (cur !== null && !on ? ' off' : '') + '"><span><b>' + esc(s.name) + '</b><br><small>' + esc(s.does) + '</small></span><span class="tag ' + (on ? 'ok' : '') + '">' + (on ? 'נטען' : 'בארון') + '</span></div>';
        }).join('') + '</div><p class="small muted" role="status" aria-live="polite">' + (cur === null ? 'בחרו בקשה.' : D.asks[cur].s ? 'ה־Skill המתאים נטען, ושאר הקלסרים נשארו סגורים.' : 'שום קלסר לא מתאים, ולכן לא נטען אף Skill.') + '</p>';
    }
    el.addEventListener('click', function (e) { var b = e.target.closest('[data-q]'); if (b) { cur = +b.getAttribute('data-q'); draw(); } });
    draw();
  };

  demos.rag = function (el, D) {
    var cur = -1;
    function draw() {
      var q = cur >= 0 ? D.qs[cur] : null;
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="dm-btns">' + D.qs.map(function (x, i) { return '<button class="dm-btn' + (cur === i ? ' on' : '') + '" data-q="' + i + '">' + esc(x.t) + '</button>'; }).join('') + '</div>' +
        '<div class="books">' + D.snippets.map(function (s) { var hit = q && q.hit.indexOf(s.id) > -1; return '<div class="book' + (hit ? ' hit' : q ? ' dim' : '') + '">' + esc(s.t) + '</div>'; }).join('') + '</div>' +
        '<p class="small muted" role="status" aria-live="polite">' + (!q ? 'בחרו שאלה.' : q.miss.length ? 'הספרן הביא רק את הקטע הראשון. פרק ' + q.miss[0] + ' קשור לשאלה ולא הגיע, ולכן תמיד בודקים.' : 'הקטעים המסומנים הגיעו לשולחן. התשובה תיבנה מהם.') + '</p>';
    }
    el.addEventListener('click', function (e) { var b = e.target.closest('[data-q]'); if (b) { cur = +b.getAttribute('data-q'); draw(); } });
    draw();
  };

  demos.agents = function (el, D) {
    var n = 3;
    function total(k) { return D.base / k + D.overhead * k; }
    function draw() {
      var best = 1, t; for (var k = 1; k <= 6; k++) if (total(k) < total(best)) best = k;
      var max = total(1) + 4;
      el.innerHTML = '<p>' + esc(D.intro) + '</p><label class="lbl" for="ag-n">מספר סוכנים: <b>' + n + '</b></label><input id="ag-n" class="range" type="range" min="1" max="6" value="' + n + '"><div class="agents-chart" aria-hidden="true">' +
        [1, 2, 3, 4, 5, 6].map(function (k) { return '<div class="' + (k === n ? 'on ' : '') + (k === best ? 'best' : '') + '"><i style="height:' + Math.round(total(k) / max * 100) + '%"></i>' + k + '</div>'; }).join('') + '</div>' +
        '<p role="status" aria-live="polite"><b>זמן כולל: ' + total(n).toFixed(0) + ' דקות.</b> עבודה: ' + (D.base / n).toFixed(0) + ', תיאום וסיכום: ' + (D.overhead * n) + '. ' + (n === best ? 'זו הנקודה היעילה ביותר בהדגמה.' : 'יש מספר יעיל יותר: ' + best + '.') + '</p><p class="small muted">ההדמיה היא מודל פשוט להמחשה, לא מדידה של כלי אמיתי.</p>';
      $('#ag-n', el).addEventListener('input', function () { n = +this.value; draw(); $('#ag-n', el).focus(); });
    }
    draw();
  };

  demos.hook = function (el, D) {
    var r = 0, on = true, fired = false;
    function draw() {
      var x = D.rules[r];
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="dm-btns">' + D.rules.map(function (y, i) { return '<button class="dm-btn' + (r === i ? ' on' : '') + '" data-r="' + i + '">' + esc(y.ev) + '</button>'; }).join('') + '</div>' +
        '<div class="layer"><span><b>כלל: כש' + esc(x.ev) + '</b><br><small>תבוצע פעולה: ' + esc(x.act) + '</small></span><button class="dm-btn' + (on ? ' on' : '') + '" data-t>' + (on ? 'פעיל' : 'כבוי') + '</button></div>' +
        '<button class="btn sm primary" type="button" data-fire>' + icon('bell') + 'הדמיית האירוע: ' + esc(x.ev) + '</button><div class="dm-out' + (fired ? (on ? ' good' : ' bad') : '') + '" role="status" aria-live="polite">' + (fired ? (on ? esc(x.out) : 'הכלל כבוי, ולכן לא קרה כלום.') : 'לחצו על הדמיית האירוע.') + '</div>';
    }
    el.addEventListener('click', function (e) {
      var a = e.target.closest('[data-r]'), t = e.target.closest('[data-t]'), f = e.target.closest('[data-fire]');
      if (a) { r = +a.getAttribute('data-r'); fired = false; } if (t) { on = !on; fired = false; } if (f) fired = true; draw();
    });
    draw();
  };

  demos.qa = function (el, D) {
    var picked = {}, shown = false;
    function draw() {
      var found = 0;
      el.innerHTML = '<p>' + esc(D.intro) + '</p><div class="stack" style="gap:8px">' + D.lines.map(function (l, i) {
        var cls = ''; if (shown) { if (l.bad && picked[i]) { cls = ' found'; found++; } else if (l.bad) cls = ' miss'; else if (picked[i]) cls = ' miss'; } else if (picked[i]) cls = ' found';
        return '<button type="button" class="err-line' + cls + '" data-l="' + i + '" aria-pressed="' + !!picked[i] + '"><span>' + (picked[i] ? '⚑' : '○') + '</span><span>' + esc(l.t) + '</span>' + (shown && l.bad ? '<small class="muted"> ' + esc(l.why) + '</small>' : '') + '</button>';
      }).join('') + '</div><div class="row"><button class="btn sm primary" type="button" data-check>בדקו אותי</button><button class="btn sm ghost" type="button" data-reset>איפוס</button></div>' +
        '<p role="status" aria-live="polite" class="dm-out' + (shown ? (found === 3 ? ' good' : ' bad') : '') + '">' + (shown ? 'מצאתם ' + found + ' מתוך 3. בעבודה אמיתית: פותרים שלושה תרגילים בעצמכם.' : 'סמנו שורות חשודות ולחצו ״בדקו אותי״.') + '</p>';
    }
    el.addEventListener('click', function (e) {
      var l = e.target.closest('[data-l]'); if (l && !shown) { var i = +l.getAttribute('data-l'); picked[i] = !picked[i]; draw(); return; }
      if (e.target.closest('[data-check]')) { shown = true; draw(); }
      if (e.target.closest('[data-reset]')) { picked = {}; shown = false; draw(); }
    });
    draw();
  };

  /* ---------- בניית המסך ---------- */
  function chapterHtml(c, i) {
    var n = (i + 1 < 10 ? '0' : '') + (i + 1);
    var tag = c.tag === 'tool' ? '<span class="tag sec">תלוי בכלי</span>' : c.tag === 'adv' ? '<span class="tag brand">למתקדמים</span>' : '';
    return '<section class="concept" id="ch-' + c.id + '" data-ch="' + c.id + '" aria-labelledby="h-' + c.id + '"><div class="wrap"><span class="no" aria-hidden="true">' + n + '</span>' +
      '<div class="concept-grid"><div data-rv>' +
        '<div class="term"><span class="ic">' + icon(c.icon) + '</span><span class="eyebrow">' + esc(c.term) + '</span>' + tag + '</div>' +
        '<h2 id="h-' + c.id + '">' + esc(c.title) + '</h2><p class="hook">' + esc(c.hook) + '</p><p class="parable">' + esc(c.parable) + '</p>' +
        '<div class="concept-actions"><button class="btn" type="button" data-deep="' + c.id + '" aria-expanded="false" aria-controls="deep-' + c.id + '">' + icon('layers') + 'להעמיק במושג</button></div></div>' +
      '<div class="card demo spot tilt-soft" data-rv="2"><span class="demo-label">נסו בעצמכם</span><div class="demo-body" data-demo="' + c.demo + '"></div></div>' +
      '<div class="deep" id="deep-' + c.id + '" hidden></div></div></div></section>';
  }

  TS.views.story = function (param) {
    var S = TS.story;
    var html =
      '<section class="story-hero"><div class="wrap">' +
        '<span class="eyebrow">הסיפור</span><h1 data-words style="margin-top:16px">' + esc(S.intro.title) + '</h1><p class="lead" data-rv>' + esc(S.intro.lead) + '</p>' +
        '<p class="hint" data-rv="1" style="margin-top:14px">' + esc(S.intro.how) + '</p><div class="story-art" data-rv="2">' + art() + '</div></div></section>' +
      '<div class="cnav-wrap"><nav class="cnav glass" aria-label="מושגי הסיפור">' + S.chapters.map(function (c) { return '<a href="#ch-' + c.id + '" data-chgo="' + c.id + '">' + esc(c.term) + '</a>'; }).join('') + '<a href="#glossary" data-chgo="glossary">מילון</a></nav></div>' +
      S.chapters.map(chapterHtml).join('') +
      '<section class="concept" id="glossary" data-ch="glossary" aria-labelledby="h-gl"><div class="wrap narrow stack lg"><h2 id="h-gl" data-rv>הכול ביחד</h2><p class="prose" data-rv="1">' + esc(S.mapNote) + '</p>' +
        '<div class="tbl-wrap" data-rv="2"><table class="tbl gloss-table"><thead><tr><th>מושג</th><th>בקצרה</th><th>מה זה לא</th></tr></thead><tbody>' + S.glossary.map(function (g) { return '<tr><td>' + esc(g.term) + '</td><td>' + esc(g.short) + '</td><td>' + esc(g.notThis) + '</td></tr>'; }).join('') + '</tbody></table></div>' +
        '<div class="row" data-rv="3"><a class="btn primary lg" href="#studio" data-route="studio">לכלי העבודה ' + icon('arrow-left', 'i-arrow') + '</a><a class="btn lg" href="#lab" data-route="lab">מעבדת הבקשה</a></div></div></section>';

    return {
      title: 'הסיפור: הגאון והשולחן', html: html,
      after: function (root) {
        $$('[data-demo]', root).forEach(function (el) { var k = el.getAttribute('data-demo'); if (demos[k]) demos[k](el, S.demos[k]); });
        var open = {};
        root.addEventListener('click', function (e) {
          var d = e.target.closest('[data-deep]'); if (d) {
            var id = d.getAttribute('data-deep'), c = S.chapters.filter(function (x) { return x.id === id; })[0], box = $('#deep-' + id, root);
            var isOpen = !box.hidden;
            if (isOpen) { box.hidden = true; d.setAttribute('aria-expanded', 'false'); return; }
            box.hidden = false; d.setAttribute('aria-expanded', 'true');
            box.innerHTML = '<div class="deep-panel"><div class="deep-tabs" role="tablist" aria-label="שכבות הסבר">' + TABS.map(function (t, i) { return '<button type="button" role="tab" data-tab="' + t[0] + '" aria-selected="' + (i === 0) + '">' + t[1] + '</button>'; }).join('') + '</div><div class="deep-body" role="tabpanel">' + tabBody(c, 'plain') + '</div></div>';
            box.scrollIntoView({ block: 'nearest', behavior: TS.fx.reduced() ? 'auto' : 'smooth' });
            return;
          }
          var t = e.target.closest('[data-tab]'); if (t) {
            var sec = t.closest('.concept'), cid = sec.getAttribute('data-ch'), ch = S.chapters.filter(function (x) { return x.id === cid; })[0];
            $$('[data-tab]', sec).forEach(function (b) { b.setAttribute('aria-selected', String(b === t)); });
            $('.deep-body', sec).innerHTML = tabBody(ch, t.getAttribute('data-tab'));
          }
        });
        var navLinks = $$('.cnav a', root);
        function setOn(id) { navLinks.forEach(function (a) { var on = a.getAttribute('data-chgo') === id; a.classList.toggle('on', on); if (on && a.scrollIntoView) { var nav = a.parentNode; nav.scrollLeft = a.offsetLeft - nav.clientWidth / 2 + a.clientWidth / 2; } }); }
        if ('IntersectionObserver' in window) {
          var io = new IntersectionObserver(function (entries) { entries.forEach(function (en) { if (en.isIntersecting) setOn(en.target.getAttribute('data-ch')); }); }, { rootMargin: '-35% 0px -55% 0px' });
          $$('.concept[data-ch]', root).forEach(function (c) { io.observe(c); });
        }
        $$('[data-chgo]', root).forEach(function (a) {
          a.addEventListener('click', function (e) {
            e.preventDefault();
            var id = a.getAttribute('data-chgo'), t = $('#' + (id === 'glossary' ? 'glossary' : 'ch-' + id), root);
            if (t) t.scrollIntoView({ behavior: TS.fx.reduced() ? 'auto' : 'smooth', block: 'start' });
          });
        });
        if (param) { var tg = $('#ch-' + param, root); if (tg) setTimeout(function () { tg.scrollIntoView({ behavior: 'auto' }); }, 80); }
      }
    };
  };

})(window.TS = window.TS || {});
