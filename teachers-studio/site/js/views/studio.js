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

  var NO_FORMAT = { analyze: 1, parents: 1, digital: 1 };

  function loadState(task) {
    var s = TS.store.get('ws:' + task.id, null);
    var base = TS.engine.newState(task);
    if (!s) return base;
    return Object.assign(base, s, { values: Object.assign({}, s.values || {}) });
  }
  function saveState(task, s) { TS.store.set('ws:' + task.id, s); }

  function stepsFor(task) {
    var st = [{ k: 'a', t: task.step2 === 'pedagogy' ? 'מה מלמדים' : 'מה מכינים' }];
    if (task.step2 !== 'none') st.push({ k: 'b', t: task.step2 === 'pedagogy' ? 'איך ולמי' : (task.styleLabel || 'אופי') });
    if (!NO_FORMAT[task.id]) st.push({ k: 'c', t: 'איך ייראה' });
    st.push({ k: 'd', t: 'ההנחיה' });
    return st;
  }
  var STEP_TITLE = { a: null, b: null, c: 'איך התוצר ייראה?', d: 'ההנחיה שלכם מוכנה' };

  /* ---------- שדות ---------- */
  function fieldHtml(f, val) {
    var id = 'f-' + f.id, v = esc(val || '');
    var hint = f.hint ? '<span class="hint" id="h-' + f.id + '">' + esc(f.hint) + '</span>' : '';
    var body;
    if (f.type === 'textarea') body = '<textarea id="' + id + '" data-f="' + f.id + '" rows="' + (f.rows || 3) + '" placeholder="' + esc(f.placeholder || '') + '"' + (f.hint ? ' aria-describedby="h-' + f.id + '"' : '') + '>' + v + '</textarea>';
    else if (f.type === 'select') body = '<select id="' + id + '" data-f="' + f.id + '"><option value="">' + esc(f.placeholder || 'בחרו') + '</option>' + f.options.map(function (o) { return '<option' + (o === val ? ' selected' : '') + '>' + esc(o) + '</option>'; }).join('') + '</select>';
    else if (f.type === 'combo') body = '<input type="text" id="' + id + '" data-f="' + f.id + '" list="dl-' + f.id + '" value="' + v + '" placeholder="' + esc(f.placeholder || '') + '" autocomplete="off"><datalist id="dl-' + f.id + '">' + f.options.map(function (o) { return '<option value="' + esc(o) + '">'; }).join('') + '</datalist>';
    else body = '<input type="text" id="' + id + '" data-f="' + f.id + '" value="' + v + '" placeholder="' + esc(f.placeholder || '') + '"' + (f.hint ? ' aria-describedby="h-' + f.id + '"' : '') + '>';
    return '<div class="field' + (f.type === 'textarea' ? ' full' : '') + '"><label for="' + id + '">' + esc(f.label) + '</label>' + body + hint + (f.privacyCheck ? '<div class="warn-line" id="pv-' + f.id + '" hidden></div>' : '') + '</div>';
  }

  function chipHtml(type, name, id, label, checked, extra) {
    return '<label class="chip ' + (type === 'radio' ? 'rad' : '') + '"><input type="' + type + '" name="' + name + '" value="' + esc(id) + '"' + (checked ? ' checked' : '') + '><span>' + esc(label) + (extra ? ' <em>' + esc(extra) + '</em>' : '') + '</span></label>';
  }

  /* מפצל שדות: עיקריים גלויים, שאר השדות מאחורי ״עוד פרטים״ */
  function split(task) {
    var defs = TS.engine.fieldDefs(task), req = task.required || [];
    var main = defs.filter(function (d) { return req.indexOf(d.id) > -1; });
    defs.forEach(function (d) { if (main.length < 4 && main.indexOf(d) < 0 && d.kind === 'common') main.push(d); });
    var order = defs.filter(function (d) { return main.indexOf(d) > -1; });
    var rest = defs.filter(function (d) { return main.indexOf(d) < 0; });
    return { main: order, rest: rest };
  }

  function stepA(task, st) {
    var sp = split(task);
    var restOpen = sp.rest.some(function (d) { return (st.values[d.id] || '').trim(); });
    var h = '<div class="form-grid">' + sp.main.map(function (d) { return fieldHtml(d, st.values[d.id]); }).join('') + '</div>';
    if (sp.rest.length) h += '<details class="acc more-fields"' + (restOpen ? ' open' : '') + '><summary>עוד פרטים (אופציונלי)<span class="pm">' + icon('plus') + '</span></summary><div class="acc-body"><div class="form-grid">' + sp.rest.map(function (d) { return fieldHtml(d, st.values[d.id]); }).join('') + '</div></div></details>';
    return h;
  }

  function stepB(task, st) {
    if (task.step2 === 'style') {
      return '<fieldset><legend>' + esc(task.styleLabel) + '</legend><div class="chips">' + task.styleOptions.map(function (o) { return chipHtml('radio', 'style', o.id, o.label, st.style === o.id); }).join('') + '</div></fieldset>';
    }
    var h = '';
    if (task.showMethods !== false) {
      h += '<fieldset><legend>שיטות הוראה (אפשר כמה)</legend><div class="chips">' + TS.methods.map(function (m) { return chipHtml('checkbox', 'methods', m.id, m.label, st.methods.indexOf(m.id) > -1); }).join('') + '</div><p class="hint" style="margin-top:10px">' + esc(TS.methodsNote) + '</p></fieldset>';
    }
    h += '<details class="acc more-fields"' + ((st.adapt.length || st.applyTo.length) ? ' open' : '') + '><summary>התאמות ללומדים (אופציונלי)<span class="pm">' + icon('plus') + '</span></summary><div class="acc-body stack lg">' +
      '<fieldset><legend>אפשר לבחור כמה התאמות במקביל</legend><div class="chips">' + TS.adaptations.map(function (a) { return chipHtml('checkbox', 'adapt', a.id, a.label, st.adapt.indexOf(a.id) > -1); }).join('') + '</div><p class="hint" style="margin-top:10px">' + esc(TS.adaptNote) + '</p></fieldset>' +
      '<fieldset><legend>על אילו חומרים להחיל את ההתאמה?</legend><div class="chips">' + TS.applyTo.map(function (a) { return chipHtml('checkbox', 'applyTo', a.id, a.label, st.applyTo.indexOf(a.id) > -1); }).join('') + '</div></fieldset></div></details>';
    return h;
  }

  function stepC(task, st) {
    return '<fieldset><legend>סגנון התוצר</legend><div class="mode-row">' + TS.formats.map(function (f) { return chipHtml('radio', 'format', f.id, f.label, st.format === f.id, f.desc); }).join('') + '</div></fieldset>' +
      '<div class="chips" style="margin-top:20px"><label class="chip"><input type="checkbox" id="opt-html" ' + (st.html ? 'checked' : '') + '><span>HTML לעריכה בסבבים <em>מומלץ</em></span></label>' +
      '<label class="chip"><input type="checkbox" id="opt-print" ' + (st.printExtra ? 'checked' : '') + '><span>גרסת הדפסה חסכונית נוספת</span></label></div>' +
      '<details class="acc more-fields"' + (st.brand.length ? ' open' : '') + '><summary>לוגו, תמונות וצבעי מותג<span class="pm">' + icon('plus') + '</span></summary><div class="acc-body stack"><fieldset><legend>אני רוצה לשלב בעיצוב</legend><div class="chips">' + TS.brand.map(function (b) { return chipHtml('checkbox', 'brand', b.id, b.label, st.brand.indexOf(b.id) > -1); }).join('') + '</div></fieldset>' +
      '<div class="callout warn">' + icon('warn') + '<p><b>חשוב:</b> ההנחיה רק מציינת שצירפתם קבצים. צרפו את הלוגו, התמונות ודוגמת העיצוב גם בשיחה בכלי ה־AI. לוגו בית הספר נמצא ב<a href="#library" data-route="library">ספרייה</a>.</p></div></div></details>';
  }

  function toolAdvice(task) {
    return '<ul class="plain" style="list-style:none;padding:0">' + (task.tools || []).map(function (t) {
      var tool = TS.tools[t.id]; if (!tool) return '';
      return '<li style="display:flex;gap:14px;padding:10px 0;border-bottom:1px solid var(--line)"><b style="min-width:7.5em"><a href="#tool-' + t.id + '" data-route="tool-' + t.id + '">' + esc(tool.name) + '</a></b><span class="muted">' + esc(t.why) + '</span></li>';
    }).join('') + '</ul><p class="hint" style="margin-top:10px">פותחים שיחה חדשה בכלי, מדביקים את ההנחיה ומצרפים קבצים אם צריך. <a href="#tools" data-route="tools">למדריך הכלים</a></p>';
  }

  function acc(title, count, body) {
    return '<details class="acc"><summary><span>' + esc(title) + (count ? ' <span class="tag">' + count + '</span>' : '') + '</span><span class="pm">' + icon('plus') + '</span></summary><div class="acc-body">' + body + '</div></details>';
  }

  function stepD(task, st) {
    var built = TS.engine.build(task, st);
    var checks = TS.store.get('chk:' + task.id, {});
    var all = (task.quality || []).concat(task.teacherChecks || []);
    var miss = built.missing.length ? '<div class="callout warn" style="margin-bottom:22px">' + icon('warn') + '<div><p><b>חסרים פרטים:</b> ' + esc(built.missing.join(', ')) + '. ההנחיה תסמן אותם בסוגריים מרובעים.</p><p><button class="btn sm" type="button" data-step="a">חזרה להשלמה</button></p></div></div>' : '';
    return miss +
      '<fieldset><legend>איך תרצו לעבוד?</legend><div class="mode-row">' +
        '<label class="chip rad"><input type="radio" name="mode" value="ready"' + (st.mode !== 'ask' ? ' checked' : '') + '><span><b>יש לי מספיק פרטים</b><em>הכינו את התוצר עכשיו</em></span></label>' +
        '<label class="chip rad"><input type="radio" name="mode" value="ask"' + (st.mode === 'ask' ? ' checked' : '') + '><span><b>עזרו לי לדייק</b><em>שאלו עד שלוש שאלות ואז הכינו</em></span></label></div></fieldset>' +
      '<div class="codebox final-prompt" style="margin-top:24px"><header><span>ההנחיה <span class="muted small" id="wc"></span></span><button class="btn sm" type="button" data-act="copy">' + icon('copy') + 'העתקה</button></header><pre id="final-pre" tabindex="0"></pre></div>' +
      '<div class="final-actions"><button class="btn primary lg mag" type="button" data-act="copy">' + icon('copy') + 'העתקת ההנחיה</button><button class="btn" type="button" data-act="md">' + icon('download') + 'הורדה כ־Markdown</button><button class="btn" type="button" data-act="html" title="דף עצמאי שנפתח נכון בעברית בדפדפן וב־Word">' + icon('download') + 'הורדה כדף HTML</button><button class="btn" type="button" data-act="kit">' + icon('kit') + 'שמירה בערכה שלי</button></div>' +
      '<div style="margin-top:44px">' +
        acc('הכלי המתאים, ולמה', '', toolAdvice(task)) +
        acc('רשימת בדיקת איכות', all.length, '<ul class="checks" id="qa-list">' + all.map(function (q, i) { return '<li><label><input type="checkbox" data-qa="' + i + '"' + (checks[i] ? ' checked' : '') + '><span>' + esc(q) + '</span></label></li>'; }).join('') + '</ul>') +
        acc('מה עושים אחרי התשובה', (task.next || []).length, '<ol class="plain">' + (task.next || []).map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ol>' + (task.printable ? '<p class="hint" style="margin-top:12px">לשיפור העיצוב בסבבים ולייצוא נכון: <a href="#adv-html" data-route="adv-html">עיצוב דרך HTML</a>.</p>' : '')) +
        acc('לפני שמדביקים', '', '<p>בלי שמות, מספרי זהות או פרטים רגישים על תלמידים. <a href="#adv-privacy" data-route="adv-privacy">הנחיות הפרטיות</a></p>') +
      '</div>';
  }

  /* ---------- אשף המשימה ---------- */
  function wizard(task) {
    var st = loadState(task);
    var steps = stepsFor(task);
    var cur = 0, revealed = false;
    TS.store.set('last', task.id);

    var html =
      '<div class="wrap"><div class="wz-head"><div class="crumbs"><a href="#studio" data-route="studio">הסטודיו</a><span>›</span><span>' + esc(task.title) + '</span></div>' +
      '<h1 data-words>' + esc(task.title) + '</h1><p class="lead" data-rv>' + esc(task.short) + '</p>' +
      '<details class="about" data-rv="1"><summary>' + icon('info') + 'מה זה התוצר הזה</summary><p>' + esc(task.about) + '</p></details>' +
      '<div class="row" data-rv="2"><button class="btn sm" type="button" id="load-ex">' + icon('spark') + 'טעינת דוגמה מלאה</button><button class="btn sm ghost" type="button" id="reset">' + icon('reset') + 'ניקוי</button></div><p class="hint" id="ex-note" hidden></p></div>' +
      '<nav class="stepper" id="stepper" aria-label="שלבי המחולל"></nav>' +
      '<div class="wz" id="wiz"><div class="card wz-main" id="wiz-main"></div>' +
      '<aside class="preview" id="preview" aria-label="תצוגה מקדימה של ההנחיה"><div class="card glass"><header><span>ההנחיה שנבנית <span class="muted small" id="wc-p"></span></span><button class="btn sm ghost" type="button" data-act="full">הצגה מלאה</button></header><pre id="prev-pre" tabindex="0"></pre><footer><span class="missing" id="missing"></span><button class="btn sm primary" type="button" data-act="copy">' + icon('copy') + 'העתקה</button></footer></div></aside></div></div>' +
      '<div class="sheet-bottom no-print"><button class="btn" type="button" data-act="full">תצוגה</button><button class="btn primary" type="button" data-act="copy">' + icon('copy') + 'העתקת ההנחיה</button></div>';

    return {
      title: task.title, html: html,
      after: function (root) {
        var main = $('#wiz-main', root), wiz = $('#wiz', root), nav = $('#stepper', root);

        function updatePreview() {
          var b = TS.engine.build(task, st);
          var pre = $('#prev-pre', root), fin = $('#final-pre', root);
          if (pre) pre.textContent = b.text;
          if (fin && revealed) fin.textContent = b.text;
          var wc = TS.engine.wordCount(b.text) + ' מילים';
          if ($('#wc-p', root)) $('#wc-p', root).textContent = '· ' + wc;
          if ($('#wc', root)) $('#wc', root).textContent = '· ' + wc;
          var m = $('#missing', root);
          if (m) m.textContent = b.missing.length ? 'חסר: ' + b.missing.length + ' שדות' : '';
          return b;
        }

        function renderNav() {
          nav.style.setProperty('--prog', steps.length > 1 ? cur / (steps.length - 1) : 0);
          nav.style.gridTemplateColumns = 'repeat(' + steps.length + ', 1fr)';
          nav.innerHTML = steps.map(function (s, i) {
            return '<button type="button" data-goto="' + i + '"' + (i === cur ? ' aria-current="step"' : '') + (i < cur ? ' class="done"' : '') + '><span class="n">' + (i < cur ? icon('check') : (i + 1)) + '</span><span class="lbl">' + esc(s.t) + '</span></button>';
          }).join('');
        }

        function typeIn(text) {
          var pre = $('#final-pre', root); if (!pre) return;
          if (TS.fx.reduced()) { pre.textContent = text; revealed = true; return; }
          var lines = text.split('\n'), i = 0;
          pre.textContent = '';
          (function tick() {
            if (!$('#final-pre', root)) return;
            i = Math.min(lines.length, i + 4);
            pre.textContent = lines.slice(0, i).join('\n');
            pre.scrollTop = pre.scrollHeight;
            if (i < lines.length) setTimeout(tick, 28); else { revealed = true; pre.scrollTop = 0; }
          })();
        }

        function renderStep(focusHeading) {
          var k = steps[cur].k;
          var body = k === 'a' ? stepA(task, st) : k === 'b' ? stepB(task, st) : k === 'c' ? stepC(task, st) : stepD(task, st);
          var title = STEP_TITLE[k] || (k === 'a' ? (task.step2 === 'pedagogy' ? 'מה מלמדים ומה רוצים להשיג?' : 'מה צריך להכין?') : (task.step2 === 'pedagogy' ? 'איך מלמדים ולמי מתאים?' : task.styleLabel));
          var prevBtn = cur > 0 ? '<button class="btn" type="button" data-nav="prev">' + icon('arrow-right') + 'הקודם</button>' : '<span></span>';
          var nextBtn = cur < steps.length - 1 ? '<button class="btn primary" type="button" data-nav="next">הבא' + icon('arrow-left', 'i-arrow') + '</button>' : '<span></span>';
          revealed = false;
          main.innerHTML = '<div class="step-enter"><h2 id="step-h" class="step-title" tabindex="-1">' + esc(title) + '</h2>' + body + '<div class="step-nav">' + prevBtn + nextBtn + '</div></div>';
          var fin = k === 'd';
          wiz.classList.toggle('final', fin);
          $('#preview', root).hidden = fin;
          renderNav();
          $$('[data-f]', main).forEach(function (el) { scanPrivacy(el); });
          var b = updatePreview();
          if (fin) typeIn(b.text);
          if (focusHeading) { var h = $('#step-h', root); if (h) h.focus({ preventScroll: true }); var top = nav.getBoundingClientRect().top + window.pageYOffset - 110; window.scrollTo({ top: Math.max(0, top), behavior: TS.fx.reduced() ? 'auto' : 'smooth' }); }
        }

        function scanPrivacy(el) {
          var f = el.getAttribute('data-f'), box = $('#pv-' + f, root);
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
          else if (el.name === 'mode') { st.mode = el.value; saveState(task, st); revealed = true; var f = $('#final-pre', root); if (f) f.textContent = TS.engine.build(task, st).text; return; }
          else if (el.id === 'opt-print') st.printExtra = el.checked;
          else if (el.id === 'opt-html') st.html = el.checked;
          else if (el.hasAttribute('data-qa')) { var c = TS.store.get('chk:' + task.id, {}); c[el.getAttribute('data-qa')] = el.checked; TS.store.set('chk:' + task.id, c); return; }
          else return;
          saveState(task, st); updatePreview();
        });

        root.addEventListener('click', function (e) {
          var b;
          if ((b = e.target.closest('[data-nav]'))) { cur = Math.max(0, Math.min(steps.length - 1, cur + (b.getAttribute('data-nav') === 'next' ? 1 : -1))); renderStep(true); return; }
          if ((b = e.target.closest('[data-goto]'))) { cur = +b.getAttribute('data-goto'); renderStep(true); return; }
          if ((b = e.target.closest('[data-step]'))) { var want = b.getAttribute('data-step'); for (var i = 0; i < steps.length; i++) if (steps[i].k === want) cur = i; renderStep(true); return; }
          if ((b = e.target.closest('[data-act]'))) {
            var act = b.getAttribute('data-act'), built = TS.engine.build(task, st);
            if (act === 'copy') TS.copy(built.text, 'ההנחיה הועתקה. הדביקו אותה בכלי ה־AI.', b);
            else if (act === 'md') TS.save(task.id + '-prompt.md', TS.engine.markdown(task, st));
            else if (act === 'html') TS.save(task.id + '-prompt.html', TS.bidi.htmlDoc(task.title + ': הנחיה', built.text), 'text/html;charset=utf-8');
            else if (act === 'kit') { TS.kit.add({ taskId: task.id, title: task.title, topic: st.values.topic || st.values.purpose || st.values.docType || '', text: built.text }); TS.toast('נשמר בערכה שלי'); }
            else if (act === 'full') TS.openViewer('ההנחיה: ' + task.title, built.text, '<button class="btn primary" type="button" id="v-copy">' + icon('copy') + 'העתקה</button>', function (box) { $('#v-copy', box).addEventListener('click', function () { TS.copy(built.text, 'ההנחיה הועתקה.', this); }); });
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
    { id: 'role',   label: 'תפקיד',   text: 'פעל כמורה מנוסה למתמטיקה בבית ספר יסודי.', why: 'קובע נקודת מבט ורמה מקצועית, ומונע תשובה כללית.' },
    { id: 'ctx',    label: 'הקשר',    text: 'כיתה ד׳, 30 דקות. התלמידים למדו שברים שקולים אך מתקשים בחיבור בין שבר לציר מספרים.', why: 'בלי הקשר ה־AI מנחש גיל ורמה. כאן הוא יודע מה כבר ידוע ואיפה הקושי.' },
    { id: 'source', label: 'מקור',    text: 'מקור: [הדביקו כאן קטע מספר הלימוד]. הסתמך עליו בלבד, וסמן ״לא מופיע במקור״ על כל מה שאינו בו.', why: 'מצמצם המצאות ומאפשר לבדוק את התוצר מול החומר שלכם.' },
    { id: 'goal',   label: 'מטרה',    text: 'מטרה: התלמידים יזהו שברים שקולים וינמקו את בחירתם במשפט אחד.', why: 'מגדיר מה נחשב הצלחה, וגם מה המבחן בודק.' },
    { id: 'struct', label: 'מבנה',    text: 'מבנה: טבלת מיפוי, 8 שאלות, מסיחים שמבוססים על טעויות נפוצות, ומפתח תשובות בעמוד נפרד.', why: 'התוצר מגיע בצורה שאפשר להשתמש בה, בלי לבנות מחדש.' },
    { id: 'limits', label: 'אילוצים', text: 'אילוצים: הדפסה בשחור־לבן, ללא שאלות שדורשות מחשבון.', why: 'מונע תוצאה יפה שאי אפשר ליישם בכיתה שלכם.' },
    { id: 'check',  label: 'בדיקה',   text: 'לפני שתמסור: ודא שבכל שאלה יש תשובה נכונה אחת, וסמן [לבדוק] על כל עובדה שאינה במקור.', why: 'מעביר ל־AI חלק מהבדיקה, ומסמן לכם איפה להסתכל.' }
  ];

  var PHRASES = [
    { g: 'קיצור ושינוי ממוקד', items: ['קצר ב־30% בלי לאבד את המושגים המרכזיים.', 'שנה רק את הפתיחה. את כל השאר השאר כמו שהוא.', 'כתוב מחדש בעברית פשוטה יותר לכיתה ג׳, ושמור על המונחים.', 'הצע שני ניסוחים חלופיים לשאלה 4.'] },
    { g: 'דיוק ובדיקה', items: ['איפה אתה לא בטוח בעובדות? רשום רשימה.', 'בדוק את עצמך מול המקור שהדבקתי, וציין כל משפט שאינו נתמך בו.', 'לכל טענה חשובה הוסף ציטוט קצר מהמקור עם מיקום (פסקה).', 'מהן הטעויות הנפוצות שתלמידים עושים בנושא, ואיפה התוצר שלך מתייחס אליהן?'] },
    { g: 'עיצוב ותצורה', items: ['הצג את התוכן בטבלה.', 'הגדל את הכותרות והוסף ריווח בין השאלות.', 'הפוך את הדף לחסכוני להדפסה: שחור־לבן, בלי רקעים כהים.', 'הוסף מקום לכתיבה אחרי כל שאלה.'] }
  ];

  var RULES = [
    ['הדביקו או צרפו את המקור', 'ה־AI אינו רואה את מה שלא הועבר אליו. אם הקטע חשוב, הדביקו אותו לשיחה או צרפו את הקובץ.'],
    ['כתבו ״עבוד רק מהמקור״', 'והוסיפו: ״מה שאינו במקור, סמן ׳לא מופיע במקור׳״. כך אתם רואים מה הוא הוסיף מעצמו.'],
    ['בקשו ציטוט עם מיקום', 'לכל טענה חשובה: ״הוסף ציטוט קצר ומספר הפסקה״. קל לבדוק, וקשה להמציא.'],
    ['הפרידו בין ״מהמקור״ ל״מהידע שלך״', 'בקשו שני חלקים או שני סימונים, כדי לדעת על מה לסמוך ועל מה לחשוב פעמיים.'],
    ['בדקו בעצמכם שלושה ציטוטים', 'מודלים עלולים להמציא ציטוט או מראה מקום. בדיקה של שלושה נותנת תחושה למהימנות התוצר.'],
    ['העלו רק מה שמותר', 'חומר שמותר לכם לשכפל, וללא מידע מזהה על תלמידים או על הצוות.']
  ];

  function lab() {
    var html =
      '<div class="wrap"><div class="wz-head"><div class="crumbs"><a href="#studio" data-route="studio">הסטודיו</a><span>›</span><span>מעבדת הבקשה</span></div>' +
      '<h1 data-words>מעבדת הבקשה</h1><p class="lead" data-rv>בקשה טובה נבנית בשכבות. הפעילו שכבה אחר שכבה וראו מה כל אחת מוסיפה.</p></div></div>' +
      '<div class="wrap stack lg" style="padding-bottom:60px">' +
        '<section class="cols" aria-labelledby="lab1" style="gap:36px"><div class="stack" data-rv><h2 id="lab1" style="font-size:1.8rem">הבקשה שגדלה</h2><div class="card flat"><p class="muted small">בקשה בסיסית</p><p style="font-size:1.25rem;font-weight:600">תכין לי מבחן על שברים</p></div>' +
          '<fieldset><legend>הוסיפו שכבות</legend><div class="chips" id="layers">' + LAYERS.map(function (l) { return '<label class="chip"><input type="checkbox" value="' + l.id + '"><span>' + esc(l.label) + '</span></label>'; }).join('') + '</div></fieldset>' +
          '<div><div class="row between"><span class="small muted">כמה מהמידע הועבר ל־AI</span><b id="lab-score">0 מתוך 7</b></div><div class="meter" id="lab-meter" role="progressbar" aria-valuemin="0" aria-valuemax="7" aria-valuenow="0"><i style="width:0"></i></div></div>' +
          '<div id="lab-why" class="stack" style="gap:8px"></div></div>' +
          '<div class="codebox" data-rv="1"><header><span>הבקשה כפי שתישלח</span><button class="btn sm primary" type="button" data-copy-sel="#lab-pre">' + icon('copy') + 'העתקה</button></header><pre id="lab-pre" tabindex="0" style="min-height:200px"></pre></div></section>' +
        '<div class="stack"><h2 style="font-size:1.8rem" data-rv>עבודה עם מקורות</h2><div class="stack" style="gap:0">' + RULES.map(function (r, i) {
          return '<details class="acc" data-rv="' + (i % 3) + '"><summary>' + (i + 1) + '. ' + esc(r[0]) + '<span class="pm">' + icon('plus') + '</span></summary><div class="acc-body"><p class="prose">' + esc(r[1]) + '</p></div></details>';
        }).join('') + '</div>' +
          '<div class="codebox" data-rv><header><span>משפט להעתקה בתחילת עבודה עם מקור</span><button class="btn sm" type="button" data-copy-sel="#src-pre">' + icon('copy') + 'העתקה</button></header><pre id="src-pre">להלן המקור לעבודה. הסתמך עליו בלבד לכל עובדה. לכל טענה חשובה הוסף ציטוט קצר ומספר פסקה. מה שאינו במקור, סמן ״לא מופיע במקור״. בסוף ציין איפה אינך בטוח.</pre></div></div>' +
        '<div class="stack"><h2 style="font-size:1.8rem" data-rv>תיקון ממוקד: משפטים להעתקה</h2><p class="lead" data-rv>אחרי התשובה הראשונה, בקשו שינוי אחד בכל פעם. כך קל להבין מה עבד.</p><div class="cols">' +
          PHRASES.map(function (g, gi) { return '<div class="stack" style="gap:10px" data-rv="' + gi + '"><h3 style="font-size:1.1rem">' + esc(g.g) + '</h3>' + g.items.map(function (p) { return '<button class="btn sm" type="button" data-copy-text="' + esc(p) + '" style="justify-content:flex-start;text-align:start;border-radius:16px;font-weight:500">' + icon('copy') + esc(p) + '</button>'; }).join('') + '</div>'; }).join('') + '</div></div>' +
      '</div>';

    return {
      title: 'מעבדת הבקשה', html: html,
      after: function (root) {
        var box = $('#layers', root), pre = $('#lab-pre', root);
        function draw() {
          var on = $$('input:checked', box).map(function (i) { return i.value; });
          var order = LAYERS.filter(function (l) { return on.indexOf(l.id) > -1; });
          pre.textContent = ['תכין לי מבחן על שברים'].concat(order.map(function (l) { return l.text; })).join('\n');
          $('#lab-score', root).textContent = on.length + ' מתוך 7';
          var m = $('#lab-meter', root); m.setAttribute('aria-valuenow', on.length); $('i', m).style.width = (on.length / 7 * 100) + '%';
          $('#lab-why', root).innerHTML = order.length ? order.map(function (l) { return '<p class="small rise"><b>' + esc(l.label) + ':</b> ' + esc(l.why) + '</p>'; }).join('') : '<p class="muted small">בלי שכבות, ה־AI יצטרך לנחש גיל, רמה, אורך ומבנה.</p>';
        }
        box.addEventListener('change', draw); draw();
      }
    };
  }

  /* ---------- בחירת משימה ---------- */
  function chooser() {
    var last = TS.store.get('last', null), lt = last && TS.engine.byId(last);
    var group = TS.store.get('grp', 'all');
    function list(g) {
      var items = TS.tasks.filter(function (t) { return g === 'all' || t.group === g; });
      return '<ul class="task-list">' + items.map(function (t, i) {
        return '<li data-rv="' + Math.min(i, 5) + '"><a class="task-link" href="#task-' + t.id + '" data-route="task-' + t.id + '"><span><b>' + esc(t.title) + '</b><small>' + esc(t.short) + '</small></span><span class="arr">' + icon('arrow-left') + '</span></a></li>';
      }).join('') + '</ul>';
    }
    var html =
      '<div class="wrap page-head"><span class="eyebrow">הסטודיו</span><h1 data-words>מה תרצו להכין?</h1><p class="lead" data-rv>שישה־עשר מסלולים, לכל אחד היגיון משלו. ארבעה שלבים קצרים ובסוף הנחיה מוכנה.</p>' +
      '<div class="row" data-rv="1">' + (lt ? '<a class="btn primary mag" href="#task-' + lt.id + '" data-route="task-' + lt.id + '">להמשיך: ' + esc(lt.title) + icon('arrow-left', 'i-arrow') + '</a>' : '') + '<a class="btn" href="#lab" data-route="lab">מעבדת הבקשה</a><a class="btn ghost" href="#tools" data-route="tools">מדריך הכלים</a></div></div>' +
      '<section class="section tight"><div class="wrap stack lg"><div class="group-tabs" id="gtabs" role="tablist" aria-label="קבוצות משימות"><button type="button" role="tab" data-g="all" aria-selected="' + (group === 'all') + '">הכול ' + TS.tasks.length + '</button>' +
        TS.groups.map(function (g) { return '<button type="button" role="tab" data-g="' + g.id + '" aria-selected="' + (group === g.id) + '">' + esc(g.label) + '</button>'; }).join('') + '</div><div id="glist">' + list(group) + '</div></div></section>';
    return {
      title: 'הסטודיו', html: html,
      after: function (root) {
        $('#gtabs', root).addEventListener('click', function (e) {
          var b = e.target.closest('[data-g]'); if (!b) return;
          group = b.getAttribute('data-g'); TS.store.set('grp', group);
          $$('[data-g]', root).forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
          $('#glist', root).innerHTML = list(group); TS.fx.scan($('#glist', root));
        });
      }
    };
  }

  TS.views.studio = function (param) {
    if (param === 'lab') return lab();
    if (param) return wizard(TS.engine.byId(param));
    return chooser();
  };

})(window.TS = window.TS || {});
