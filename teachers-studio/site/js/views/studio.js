/* הסטודיו: בחירת משימה, מחולל ההנחיות בארבעה שלבים, ומעבדת הבקשה */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  /* ---------- בדיקת פרטיות מקומית בלבד ---------- */
  TS.privacyScan = function (text) {
    var out = [];
    if (/(^|\D)\d{9}(\D|$)/.test(String(text).replace(/[-\s]/g, ''))) out.push('נראה שיש כאן רצף של 9 ספרות, כמו מספר זהות.');
    if (/0\d{1,2}[-\s]?\d{7}/.test(text)) out.push('נראה שיש כאן מספר טלפון.');
    if (/[\w.+-]+@[\w-]+\.[\w.-]+/.test(text)) out.push('נראה שיש כאן כתובת דוא״ל.');
    if (/ת\.?\s?ז\.?(?![א-ת])/.test(text)) out.push('מופיעה האות ״ת.ז״. אל תכללו מספרי זהות.');
    return out;
  };

  /* ---------- רשימת משימות לפי קבוצות ---------- */
  function dirHtml() {
    return '<div class="dir">' + TS.groups.map(function (g) {
      var items = TS.tasks.filter(function (t) { return t.group === g.id; });
      return '<section class="dir-group"><h3>' + esc(g.label) + '<small>' + esc(g.hint) + '</small></h3><ul>' + items.map(function (t) {
        return '<li><a class="task-link" href="#task-' + t.id + '" data-route="task-' + t.id + '"><span><b>' + esc(t.title) + '</b><small>' + esc(t.short) + '</small></span>' + icon('arrow-left') + '</a></li>';
      }).join('') + '</ul></section>';
    }).join('') + '</div>';
  }

  /* ---------- מצב ושמירה ---------- */
  var NO_FORMAT = { analyze: 1, parents: 1, digital: 1 };

  function loadState(task) {
    var s = TS.store.get('ws:' + task.id, null);
    var base = TS.engine.newState(task);
    if (!s) return base;
    return Object.assign(base, s, { values: Object.assign({}, s.values || {}) });
  }
  function saveState(task, s) { TS.store.set('ws:' + task.id, s); }

  function stepsFor(task) {
    var st = [{ k: 'a', t: task.step2 === 'pedagogy' ? 'מה מלמדים ומה רוצים להשיג' : 'מה צריך להכין' }];
    if (task.step2 !== 'none') st.push({ k: 'b', t: task.step2 === 'pedagogy' ? 'איך מלמדים ולמי מתאימים' : (task.styleLabel || 'אופי') });
    if (!NO_FORMAT[task.id]) st.push({ k: 'c', t: 'איך התוצר ייראה' });
    st.push({ k: 'd', t: 'ההנחיה והמשך' });
    return st;
  }

  /* ---------- שדות ---------- */
  function fieldHtml(f, val) {
    var id = 'f-' + f.id, v = esc(val || '');
    var hint = f.hint ? '<span class="hint" id="h-' + f.id + '">' + esc(f.hint) + '</span>' : '';
    var req = '';
    var body;
    if (f.type === 'textarea') body = '<textarea id="' + id + '" data-f="' + f.id + '" rows="' + (f.rows || 3) + '" placeholder="' + esc(f.placeholder || '') + '"' + (f.hint ? ' aria-describedby="h-' + f.id + '"' : '') + '>' + v + '</textarea>';
    else if (f.type === 'select') body = '<select id="' + id + '" data-f="' + f.id + '"><option value="">' + esc(f.placeholder || 'בחרו') + '</option>' + f.options.map(function (o) { return '<option' + (o === val ? ' selected' : '') + '>' + esc(o) + '</option>'; }).join('') + '</select>';
    else if (f.type === 'combo') body = '<input type="text" id="' + id + '" data-f="' + f.id + '" list="dl-' + f.id + '" value="' + v + '" placeholder="' + esc(f.placeholder || '') + '" autocomplete="off"><datalist id="dl-' + f.id + '">' + f.options.map(function (o) { return '<option value="' + esc(o) + '">'; }).join('') + '</datalist>';
    else body = '<input type="text" id="' + id + '" data-f="' + f.id + '" value="' + v + '" placeholder="' + esc(f.placeholder || '') + '"' + (f.hint ? ' aria-describedby="h-' + f.id + '"' : '') + '>';
    var wide = (f.type === 'textarea') ? ' full' : '';
    return '<div class="field' + wide + '"><label for="' + id + '">' + esc(f.label) + req + '</label>' + body + hint + (f.privacyCheck ? '<div class="warn-line" id="pv-' + f.id + '" hidden></div>' : '') + '</div>';
  }

  function chipHtml(type, name, id, label, checked, extra) {
    return '<label class="chip ' + (type === 'radio' ? 'rad' : '') + '"><input type="' + type + '" name="' + name + '" value="' + esc(id) + '"' + (checked ? ' checked' : '') + '><span>' + esc(label) + (extra ? ' <em>' + esc(extra) + '</em>' : '') + '</span></label>';
  }

  /* ---------- תוכן כל שלב ---------- */
  function stepA(task, st) {
    var defs = TS.engine.fieldDefs(task);
    var commons = defs.filter(function (d) { return d.kind === 'common'; });
    var extras = defs.filter(function (d) { return d.kind === 'extra'; });
    var h = '';
    if (commons.length) h += '<div class="form-grid">' + commons.map(function (d) { return fieldHtml(d, st.values[d.id]); }).join('') + '</div>';
    if (extras.length) h += (commons.length ? '<hr class="ruler" style="margin-block:22px">' : '') + '<h3 style="margin-bottom:14px">' + (commons.length ? 'פרטים ייחודיים ל' + esc(task.title) : 'פרטי המשימה') + '</h3><div class="form-grid">' + extras.map(function (d) { return fieldHtml(d, st.values[d.id]); }).join('') + '</div>';
    return h;
  }

  function stepB(task, st) {
    var h = '';
    if (task.step2 === 'style') {
      h += '<fieldset><legend>' + esc(task.styleLabel) + '</legend><div class="chips">' + task.styleOptions.map(function (o) { return chipHtml('radio', 'style', o.id, o.label, st.style === o.id); }).join('') + '</div></fieldset>';
      return h;
    }
    if (task.showMethods !== false) {
      h += '<fieldset><legend>שיטות הוראה (אפשר לבחור כמה)</legend><div class="chips" data-group="methods">' + TS.methods.map(function (m) { return chipHtml('checkbox', 'methods', m.id, m.label, st.methods.indexOf(m.id) > -1, m.when); }).join('') + '</div><p class="hint" style="margin-top:8px">' + esc(TS.methodsNote) + '</p></fieldset><hr class="ruler" style="margin-block:22px">';
    }
    h += '<fieldset><legend>התאמות (אפשר לבחור כמה במקביל)</legend><div class="chips" data-group="adapt">' + TS.adaptations.map(function (a) { return chipHtml('checkbox', 'adapt', a.id, a.label, st.adapt.indexOf(a.id) > -1); }).join('') + '</div>' +
      '<p class="hint" style="margin-top:8px">' + esc(TS.adaptNote) + '</p></fieldset>' +
      '<fieldset style="margin-top:18px"><legend>על אילו חומרים להחיל את ההתאמה?</legend><div class="chips" data-group="applyTo">' + TS.applyTo.map(function (a) { return chipHtml('checkbox', 'applyTo', a.id, a.label, st.applyTo.indexOf(a.id) > -1); }).join('') + '</div></fieldset>';
    return h;
  }

  function stepC(task, st) {
    var h = '<fieldset><legend>סגנון התוצר</legend><div class="mode-row">' + TS.formats.map(function (f) { return chipHtml('radio', 'format', f.id, f.label, st.format === f.id, f.desc); }).join('') + '</div></fieldset>' +
      '<div class="stack" style="margin-top:18px">' +
      '<label class="chip"><input type="checkbox" id="opt-print" ' + (st.printExtra ? 'checked' : '') + '><span>הוסיפו גם גרסת הדפסה חסכונית</span></label>' +
      '<label class="chip"><input type="checkbox" id="opt-html" ' + (st.html ? 'checked' : '') + '><span>בקשו את התוצר כ־HTML לעריכה בסבבים <em>מומלץ לעיצוב</em></span></label></div>' +
      '<hr class="ruler" style="margin-block:22px"><fieldset><legend>אני רוצה לשלב בעיצוב</legend><div class="chips" data-group="brand">' + TS.brand.map(function (b) { return chipHtml('checkbox', 'brand', b.id, b.label, st.brand.indexOf(b.id) > -1); }).join('') + '</div></fieldset>' +
      '<div class="callout warn" style="margin-top:14px">' + icon('warn') + '<p><b>חשוב:</b> ההנחיה רק מציינת שצירפתם קבצים. עליכם לצרף את הלוגו, התמונות ודוגמת העיצוב גם בשיחה בכלי ה־AI שבו אתם עובדים, אחרת הוא לא יראה אותם.</p></div>';
    return h;
  }

  function toolAdvice(task) {
    return '<ul class="plain advice" style="list-style:none;padding:0">' + (task.tools || []).map(function (t) {
      var tool = TS.tools[t.id]; if (!tool) return '';
      return '<li><b><a href="#tool-' + t.id + '" data-route="tool-' + t.id + '">' + esc(tool.name) + '</a></b><span>' + esc(t.why) + '</span></li>';
    }).join('') + '</ul>';
  }

  function stepD(task, st) {
    var built = TS.engine.build(task, st);
    var checks = TS.store.get('chk:' + task.id, {});
    var all = (task.quality || []).concat(task.teacherChecks || []);
    var miss = built.missing.length ? '<div class="callout warn">' + icon('warn') + '<div><p><b>חסרים פרטים:</b> ' + esc(built.missing.join(', ')) + '. ההנחיה תסמן אותם בסוגריים מרובעים, ואפשר גם להשלים בשלב א׳.</p><p><button class="btn sm" type="button" data-step="a">חזרה לשלב א׳</button></p></div></div>' : '';
    var h = miss +
      '<fieldset><legend>איך תרצו לעבוד?</legend><div class="mode-row">' +
        '<label class="chip rad"><input type="radio" name="mode" value="ready"' + (st.mode !== 'ask' ? ' checked' : '') + '><span><b>יש לי מספיק פרטים</b><em>הכינו את התוצר עכשיו</em></span></label>' +
        '<label class="chip rad"><input type="radio" name="mode" value="ask"' + (st.mode === 'ask' ? ' checked' : '') + '><span><b>עזרו לי לדייק</b><em>שאלו עד שלוש שאלות ואז הכינו</em></span></label>' +
      '</div></fieldset>' +
      '<div class="codebox" style="margin-top:18px"><header><span>ההנחיה, מוכנה להעתקה <span class="muted small" id="wc"></span></span><button class="btn sm primary" type="button" data-act="copy">' + icon('copy') + 'העתקה</button></header><pre id="final-pre" tabindex="0"></pre></div>' +
      '<div class="row" style="margin-top:14px"><button class="btn primary lg" type="button" data-act="copy">' + icon('copy') + 'העתקת ההנחיה</button>' +
        '<button class="btn" type="button" data-act="md">' + icon('download') + 'הורדה כ־Markdown</button>' +
        '<button class="btn" type="button" data-act="kit">' + icon('kit') + 'שמירה בערכה שלי</button></div>' +
      '<hr class="ruler" style="margin-block:26px">' +
      '<div class="final-grid"><div class="stack">' +
        '<div><h3>הכלי המתאים, ולמה</h3>' + toolAdvice(task) + '<p class="hint">פותחים שיחה חדשה בכלי, מדביקים את ההנחיה ומצרפים קבצים אם צריך. <a href="#tools" data-route="tools">למדריך הכלים המלא</a></p></div>' +
        '<div><h3>רשימת בדיקת איכות</h3><ul class="checks" id="qa-list">' + all.map(function (q, i) {
          return '<li><label><input type="checkbox" data-qa="' + i + '"' + (checks[i] ? ' checked' : '') + '><span>' + esc(q) + '</span></label></li>';
        }).join('') + '</ul></div></div>' +
        '<div class="stack"><div class="panel"><h3>מה עושים אחרי התשובה</h3><ol class="plain" style="margin-top:8px">' + (task.next || []).map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ol></div>' +
        (task.printable ? '<div class="callout">' + icon('info') + '<p>רוצים לשפר את העיצוב בכמה סבבים ולייצא נכון? <a href="#adv-html" data-route="adv-html">עיצוב דרך HTML</a>.</p></div>' : '') +
        '<div class="callout">' + icon('lock') + '<p>לפני שמדביקים: בלי שמות, מספרי זהות או פרטים רגישים על תלמידים. <a href="#adv-privacy" data-route="adv-privacy">הנחיות הפרטיות</a></p></div></div>' +
      '</div>';
    return h;
  }

  /* ---------- אשף המשימה ---------- */
  function wizard(task) {
    var st = loadState(task);
    var steps = stepsFor(task);
    var cur = 0;
    TS.store.set('last', task.id);

    var head =
      '<div class="wrap studio-head stack"><div class="crumbs"><a href="#studio" data-route="studio">הסטודיו</a><span>›</span><span>' + esc(task.title) + '</span></div>' +
      '<h1 style="font-size:clamp(1.9rem,4.4vw,3rem)">' + esc(task.title) + '</h1>' +
      '<p class="lead">' + esc(task.about) + '</p>' +
      '<div class="row"><button class="btn" type="button" id="load-ex">' + icon('spark') + 'טעינת דוגמה מלאה</button><button class="btn ghost" type="button" id="reset">' + icon('reset') + 'ניקוי</button></div>' +
      '<p class="hint" id="ex-note" hidden></p></div>';

    var html = head + '<div class="wrap" style="padding-bottom:20px"><nav class="wiz-steps" id="wiz-steps" aria-label="שלבי המחולל"></nav></div>' +
      '<div class="wrap"><div class="wiz" id="wiz"><div class="panel shadow" id="wiz-main"></div>' +
      '<aside class="preview" id="preview" aria-label="תצוגה מקדימה של ההנחיה"><div class="codebox"><header><span>ההנחיה שנבנית <span class="muted small" id="wc-p"></span></span><button class="btn sm" type="button" data-act="copy">' + icon('copy') + 'העתקה</button></header><pre id="prev-pre" tabindex="0"></pre></div><p class="missing" id="missing"></p></aside></div></div>' +
      '<div class="sticky-copy no-print"><button class="btn primary" type="button" data-act="copy">' + icon('copy') + 'העתקת ההנחיה</button><button class="btn" type="button" data-step="d">לשלב האחרון</button></div>';

    return {
      title: task.title, html: html,
      after: function (root) {
        var main = $('#wiz-main', root), wiz = $('#wiz', root), nav = $('#wiz-steps', root);

        function updatePreview() {
          var b = TS.engine.build(task, st);
          var pre = $('#prev-pre', root), fin = $('#final-pre', root);
          if (pre) pre.textContent = b.text;
          if (fin) fin.textContent = b.text;
          var wc = TS.engine.wordCount(b.text) + ' מילים';
          if ($('#wc-p', root)) $('#wc-p', root).textContent = '· ' + wc;
          if ($('#wc', root)) $('#wc', root).textContent = '· ' + wc;
          var m = $('#missing', root);
          if (m) m.textContent = b.missing.length ? 'חסר: ' + b.missing.join(', ') : '';
          return b;
        }

        function renderNav() {
          nav.innerHTML = steps.map(function (s, i) {
            return '<button type="button" data-goto="' + i + '"' + (i === cur ? ' aria-current="step"' : '') + '><span class="n">' + (i + 1) + '</span>' + esc(s.t) + '</button>';
          }).join('');
        }

        function renderStep(focusHeading) {
          var k = steps[cur].k;
          var body = k === 'a' ? stepA(task, st) : k === 'b' ? stepB(task, st) : k === 'c' ? stepC(task, st) : stepD(task, st);
          var prevBtn = cur > 0 ? '<button class="btn" type="button" data-nav="prev">' + icon('arrow-right') + 'הקודם</button>' : '<span></span>';
          var nextBtn = cur < steps.length - 1 ? '<button class="btn primary" type="button" data-nav="next">הבא' + icon('arrow-left') + '</button>' : '<span></span>';
          main.innerHTML = '<h2 id="step-h" tabindex="-1" style="font-size:1.5rem;margin-bottom:18px">' + esc(steps[cur].t) + '</h2>' + body + '<div class="step-nav">' + prevBtn + nextBtn + '</div>';
          var fin = k === 'd';
          wiz.classList.toggle('final', fin);
          $('#preview', root).hidden = fin;
          renderNav();
          $$('[data-f]', main).forEach(function (el) { scanPrivacy(el); });
          updatePreview();
          if (focusHeading) { var h = $('#step-h', root); if (h) h.focus({ preventScroll: true }); var top = nav.getBoundingClientRect().top + window.pageYOffset - 80; window.scrollTo(0, Math.max(0, top)); }
        }

        function scanPrivacy(el) {
          var f = el.getAttribute('data-f');
          var box = $('#pv-' + f, root);
          if (!box) return;
          var r = TS.privacyScan(el.value);
          box.hidden = !r.length;
          box.innerHTML = r.length ? icon('warn') + '<span>' + esc(r.join(' ')) + ' אל תדביקו מידע מזהה. הבדיקה מתבצעת במכשיר שלכם בלבד.</span>' : '';
        }

        function toggle(arr, id, on) { var i = arr.indexOf(id); if (on && i < 0) arr.push(id); if (!on && i > -1) arr.splice(i, 1); }

        main.addEventListener('input', function (e) {
          var el = e.target;
          if (el.hasAttribute('data-f')) { st.values[el.getAttribute('data-f')] = el.value; scanPrivacy(el); saveState(task, st); updatePreview(); }
        });
        main.addEventListener('change', function (e) {
          var el = e.target;
          if (el.hasAttribute('data-f')) { st.values[el.getAttribute('data-f')] = el.value; saveState(task, st); updatePreview(); return; }
          if (el.name === 'methods') toggle(st.methods, el.value, el.checked);
          else if (el.name === 'adapt') toggle(st.adapt, el.value, el.checked);
          else if (el.name === 'applyTo') toggle(st.applyTo, el.value, el.checked);
          else if (el.name === 'brand') toggle(st.brand, el.value, el.checked);
          else if (el.name === 'style') st.style = el.value;
          else if (el.name === 'format') st.format = el.value;
          else if (el.name === 'mode') st.mode = el.value;
          else if (el.id === 'opt-print') st.printExtra = el.checked;
          else if (el.id === 'opt-html') st.html = el.checked;
          else if (el.hasAttribute('data-qa')) {
            var c = TS.store.get('chk:' + task.id, {}); c[el.getAttribute('data-qa')] = el.checked; TS.store.set('chk:' + task.id, c); return;
          } else return;
          saveState(task, st); updatePreview();
        });

        root.addEventListener('click', function (e) {
          var b;
          if ((b = e.target.closest('[data-nav]'))) { cur = Math.max(0, Math.min(steps.length - 1, cur + (b.getAttribute('data-nav') === 'next' ? 1 : -1))); renderStep(true); return; }
          if ((b = e.target.closest('[data-goto]'))) { cur = +b.getAttribute('data-goto'); renderStep(true); return; }
          if ((b = e.target.closest('[data-step]'))) { var want = b.getAttribute('data-step'); for (var i = 0; i < steps.length; i++) if (steps[i].k === want) cur = i; renderStep(true); return; }
          if ((b = e.target.closest('[data-act]'))) {
            var act = b.getAttribute('data-act'), built = TS.engine.build(task, st);
            if (act === 'copy') TS.copy(built.text, 'ההנחיה הועתקה. הדביקו אותה בכלי ה־AI.');
            else if (act === 'md') TS.save(task.id + '-prompt.md', TS.engine.markdown(task, st));
            else if (act === 'kit') { TS.kit.add({ taskId: task.id, title: task.title, topic: st.values.topic || st.values.purpose || st.values.docType || '', text: built.text }); TS.toast('נשמר בערכה שלי'); }
          }
        });

        $('#load-ex', root).addEventListener('click', function () {
          st = TS.engine.exampleState(task); saveState(task, st);
          var n = $('#ex-note', root); n.hidden = false; n.textContent = 'נטענה דוגמה מלאה: ' + (task.example.note || '') + ' אפשר לערוך כל שדה.';
          renderStep(false);
          TS.toast('נטענה דוגמה מלאה');
        });
        $('#reset', root).addEventListener('click', function () {
          st = TS.engine.newState(task); saveState(task, st); $('#ex-note', root).hidden = true; cur = 0; renderStep(false); TS.toast('הטופס נוקה');
        });

        renderStep(false);
      }
    };
  }

  /* ---------- מעבדת הבקשה ---------- */
  var LAYERS = [
    { id: 'role',   label: 'תפקיד',   text: 'פעל כמורה מנוסה למתמטיקה בבית ספר יסודי.', why: 'קובע את נקודת המבט והרמה המקצועית, ומונע תשובה כללית.' },
    { id: 'ctx',    label: 'הקשר',    text: 'כיתה ד׳, 30 דקות. התלמידים למדו שברים שקולים אך מתקשים בחיבור בין שבר לציר מספרים.', why: 'בלי הקשר ה־AI מנחש גיל ורמה. כאן הוא יודע מה כבר ידוע ואיפה הקושי.' },
    { id: 'source', label: 'מקור',    text: 'מקור: [הדביקו כאן קטע מספר הלימוד]. הסתמך עליו בלבד, וסמן ״לא מופיע במקור״ על כל מה שאינו בו.', why: 'מצמצם המצאות ומאפשר לבדוק את התוצר מול החומר שלכם.' },
    { id: 'goal',   label: 'מטרה',    text: 'מטרה: התלמידים יזהו שברים שקולים וינמקו את בחירתם במשפט אחד.', why: 'מגדיר מה נחשב הצלחה, וגם מה המבחן בודק.' },
    { id: 'struct', label: 'מבנה',    text: 'מבנה: טבלת מיפוי, 8 שאלות, מסיחים שמבוססים על טעויות נפוצות, ומפתח תשובות בעמוד נפרד.', why: 'התוצר מגיע בצורה שאפשר להשתמש בה, בלי לבנות מחדש.' },
    { id: 'limits', label: 'אילוצים', text: 'אילוצים: הדפסה בשחור־לבן, ללא שאלות שדורשות מחשבון.', why: 'מונע תוצאה יפה שאי אפשר ליישם בכיתה שלכם.' },
    { id: 'check',  label: 'בדיקה',   text: 'לפני שתמסור: ודא שבכל שאלה יש תשובה נכונה אחת, וסמן [לבדוק] על כל עובדה שאינה במקור.', why: 'מעביר ל־AI חלק מהבדיקה, ומסמן לכם איפה להסתכל.' }
  ];

  var PHRASES = [
    { g: 'קיצור ושינוי ממוקד', items: ['קצר ב־30% בלי לאבד את המושגים המרכזיים.', 'שנה רק את הפתיחה. את כל השאר השאר כמו שהוא.', 'כתוב מחדש בעברית פשוטה יותר לכיתה ג׳, ושמור על המונחים.', 'הצע שני ניסוחים חלופיים לשאלה 4.'] },
    { g: 'דיוק ובדיקה', items: ['איפה אתה לא בטוח בעובדות? רשום רשימה.', 'בדוק את עצמך מול המקור שהדבקתי, וציין כל משפט שאינו נתמך בו.', 'לכל טענה חשובה הוסף ציטוט קצר מהמקור עם מיקום (פסקה).', 'מה הטעויות הנפוצות שתלמידים עושים בנושא הזה, ואיפה התוצר שלך מתייחס אליהן?'] },
    { g: 'עיצוב ותצורה', items: ['הצג את התוכן בטבלה.', 'הגדל את הכותרות והוסף ריווח בין השאלות.', 'הפוך את הדף לחסכוני להדפסה: שחור־לבן, בלי רקעים כהים.', 'הוסף מקום לכתיבה אחרי כל שאלה.'] }
  ];

  var RULES = [
    ['הדביקו או צרפו את המקור', 'ה־AI אינו רואה את מה שלא הועבר אליו. אם הקטע חשוב, הדביקו אותו לתוך השיחה או צרפו את הקובץ.'],
    ['כתבו ״עבוד רק מהמקור״', 'והוסיפו: ״מה שאינו במקור, סמן ׳לא מופיע במקור׳״. כך אתם רואים מה הוא הוסיף מעצמו.'],
    ['בקשו ציטוט עם מיקום', 'לכל טענה חשובה: ״הוסף ציטוט קצר ומספר הפסקה״. קל לבדוק, וקשה להמציא.'],
    ['הפרידו בין ״מהמקור״ ל״מהידע שלך״', 'בקשו שני חלקים או שתי סימונים, כדי שתדעו על מה לסמוך ועל מה לחשוב פעמיים.'],
    ['בדקו בעצמכם שלושה ציטוטים', 'מודלים עלולים להמציא ציטוט או מראה מקום. בדיקה של שלושה נותנת תחושה למהימנות התוצר.'],
    ['העלו רק מה שמותר', 'חומר שמותר לכם לשכפל, וללא מידע מזהה על תלמידים או על הצוות.']
  ];

  function lab() {
    var html =
      '<div class="wrap studio-head stack"><div class="crumbs"><a href="#studio" data-route="studio">הסטודיו</a><span>›</span><span>מעבדת הבקשה</span></div>' +
      '<h1 style="font-size:clamp(1.9rem,4.4vw,3rem)">מעבדת הבקשה</h1><p class="lead">בקשה טובה נבנית בשכבות. התחילו מבקשה קצרה והפעילו שכבה אחר שכבה כדי לראות מה כל אחת מוסיפה.</p></div>' +
      '<div class="wrap section tight stack lg"><section class="stack" aria-labelledby="lab1"><h2 id="lab1">הבקשה שגדלה</h2>' +
        '<div class="cols c2"><div class="stack"><div class="panel"><p class="muted small">בקשה בסיסית</p><p style="font-size:1.15rem;font-weight:600">תכין לי מבחן על שברים</p></div>' +
        '<fieldset><legend>הוסיפו שכבות</legend><div class="chips" id="layers">' + LAYERS.map(function (l) { return '<label class="chip"><input type="checkbox" value="' + l.id + '"><span>' + esc(l.label) + '</span></label>'; }).join('') + '</div></fieldset>' +
        '<div><div class="row between"><span class="small muted">כמה מהמידע הועבר ל־AI</span><b id="lab-score">0 מתוך 7</b></div><div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="7" aria-valuenow="0" id="lab-meter"><i style="width:0"></i></div></div>' +
        '<div id="lab-why" class="stack"></div></div>' +
        '<div class="codebox"><header><span>הבקשה כפי שתישלח</span><button class="btn sm primary" type="button" data-copy-sel="#lab-pre">' + icon('copy') + 'העתקה</button></header><pre id="lab-pre" class="lab-out" tabindex="0"></pre></div></div>' +
      '</section>' +
      '<hr class="ruler"><section class="stack" aria-labelledby="lab2"><h2 id="lab2">עבודה עם מקורות</h2><div class="cols">' +
        RULES.map(function (r, i) { return '<div class="stack"><h3 style="font-size:1.1rem">' + (i + 1) + '. ' + esc(r[0]) + '</h3><p class="muted">' + esc(r[1]) + '</p></div>'; }).join('') + '</div>' +
        '<div class="codebox"><header><span>משפט להעתקה בתחילת עבודה עם מקור</span><button class="btn sm" type="button" data-copy-sel="#src-pre">' + icon('copy') + 'העתקה</button></header><pre id="src-pre">להלן המקור לעבודה. הסתמך עליו בלבד לכל עובדה. לכל טענה חשובה הוסף ציטוט קצר ומספר פסקה. מה שאינו במקור, סמן ״לא מופיע במקור״. בסוף ציין איפה אינך בטוח.</pre></div>' +
      '</section>' +
      '<hr class="ruler"><section class="stack" aria-labelledby="lab3"><h2 id="lab3">תיקון ממוקד: משפטים להעתקה</h2><p class="lead">אחרי התשובה הראשונה, בקשו שינוי אחד בכל פעם. כך קל להבין מה עבד.</p><div class="cols">' +
        PHRASES.map(function (g) { return '<div class="stack"><h3 style="font-size:1.1rem">' + esc(g.g) + '</h3><ul class="plain" style="list-style:none;padding:0;display:flex;flex-direction:column;gap:8px">' + g.items.map(function (p) { return '<li><button class="btn sm" type="button" data-copy-text="' + esc(p) + '" style="text-align:start;justify-content:flex-start;width:100%;font-weight:500">' + icon('copy') + esc(p) + '</button></li>'; }).join('') + '</ul></div>'; }).join('') +
      '</div></section>' +
      '<div class="callout">' + icon('info') + '<p>מוכנים לבנות בקשה אמיתית? <a href="#studio" data-route="studio">חזרה לבחירת משימה</a>.</p></div></div>';

    return {
      title: 'מעבדת הבקשה', html: html,
      after: function (root) {
        var box = $('#layers', root), pre = $('#lab-pre', root);
        function draw() {
          var on = $$('input:checked', box).map(function (i) { return i.value; });
          var lines = ['תכין לי מבחן על שברים'];
          var order = LAYERS.filter(function (l) { return on.indexOf(l.id) > -1; });
          order.forEach(function (l) { lines.push(l.text); });
          pre.textContent = lines.join('\n');
          $('#lab-score', root).textContent = on.length + ' מתוך 7';
          var m = $('#lab-meter', root); m.setAttribute('aria-valuenow', on.length); $('i', m).style.width = (on.length / 7 * 100) + '%';
          $('#lab-why', root).innerHTML = order.length ? order.map(function (l) { return '<p class="small"><b>' + esc(l.label) + ':</b> ' + esc(l.why) + '</p>'; }).join('') : '<p class="muted small">בלי שכבות, ה־AI יצטרך לנחש גיל, רמה, אורך ומבנה.</p>';
        }
        box.addEventListener('change', draw); draw();
      }
    };
  }

  TS.views.studio = function (param) {
    if (param === 'lab') return lab();
    if (param) return wizard(TS.engine.byId(param));
    var last = TS.store.get('last', null), lt = last && TS.engine.byId(last);
    return {
      title: 'הסטודיו',
      html: '<div class="wrap page-head"><span class="eyebrow">הסטודיו</span><h1>מה תרצו להכין?</h1><p class="lead">שישה־עשר מסלולים, לכל אחד היגיון מקצועי משלו. בכל מסלול עד ארבעה שלבים קצרים, ובסוף הנחיה מוכנה להעתקה.</p>' +
        '<div class="row" style="margin-top:6px">' + (lt ? '<a class="btn primary" href="#task-' + lt.id + '" data-route="task-' + lt.id + '">להמשיך: ' + esc(lt.title) + icon('arrow-left') + '</a>' : '') + '<a class="btn" href="#lab" data-route="lab">מעבדת הבקשה: איך לדייק</a><a class="btn ghost" href="#tools" data-route="tools">מדריך הכלים</a></div></div>' +
        '<hr class="ruler" style="margin-top:28px"><section class="section tight"><div class="wrap">' + dirHtml() + '</div></section>'
    };
  };

})(window.TS = window.TS || {});
