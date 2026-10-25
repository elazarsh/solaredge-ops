/* ליבת האתר: כלי עזר, אחסון, העתקה, הורדה, ניתוב עם מעברים, תפריט תצוגה, דיאלוגים וערכת העבודה האישית */
(function (TS) {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  TS.$ = $; TS.$$ = $$;

  TS.esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var esc = TS.esc;

  TS.icon = function (name, cls) {
    return '<svg class="i ' + (cls || '') + '" aria-hidden="true" focusable="false"><use href="#i-' + name + '"/></svg>';
  };

  /* ---------- אחסון מקומי: אופציונלי, נכשל בשקט ---------- */
  var mem = {};
  TS.store = {
    get: function (k, d) {
      try {
        var raw = window.localStorage.getItem('ts1:' + k);
        if (raw == null) return k in mem ? mem[k] : d;
        return JSON.parse(raw);
      } catch (e) { return k in mem ? mem[k] : d; }
    },
    set: function (k, v) {
      mem[k] = v;
      try { window.localStorage.setItem('ts1:' + k, JSON.stringify(v)); } catch (e) { /* אין אחסון */ }
    },
    del: function (k) {
      delete mem[k];
      try { window.localStorage.removeItem('ts1:' + k); } catch (e) { /* אין אחסון */ }
    }
  };

  /* ---------- הודעה קצרה ---------- */
  var toastTimer = null;
  TS.toast = function (msg) {
    var t = $('#toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('on'); }, 2600);
  };

  /* ---------- העתקה ---------- */
  TS.copy = function (text, doneMsg, srcEl) {
    function ok() { TS.toast(doneMsg || 'הועתק'); if (TS.fx) TS.fx.burst(srcEl); }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var done = false;
      try { done = document.execCommand('copy'); } catch (e) { done = false; }
      document.body.removeChild(ta);
      if (done) ok(); else TS.toast('ההעתקה נחסמה. סמנו את הטקסט והעתיקו ידנית.');
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, fallback);
    else fallback();
  };

  /* ---------- הורדה: יכולת ה־downloads של claude.ai אם קיימת, אחרת קישור הורדה רגיל ---------- */
  TS.caps = { downloads: null };
  TS.initCaps = function () {
    try {
      if (window.claude && typeof window.claude.use === 'function') {
        window.claude.use('downloads').then(function (d) { TS.caps.downloads = d || null; }, function () { TS.caps.downloads = null; });
      }
    } catch (e) { TS.caps.downloads = null; }
  };

  TS.save = function (filename, data, mime) {
    mime = mime || 'text/plain;charset=utf-8';
    if (TS.caps.downloads) {
      return TS.caps.downloads.save({ filename: filename, data: data }).then(function () {
        TS.toast('נשמר: ' + filename);
      }, function (err) {
        var code = err && err.code;
        if (code === 'declined') { TS.toast('ההורדה בוטלה'); return; }
        TS.toast('ההורדה לא זמינה כאן. השתמשו בכפתור ״העתקה״ או פתחו את האתר בכתובת הרגילה.');
      });
    }
    try {
      var blob = data instanceof Blob ? data : new Blob([data], { type: mime });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url; a.download = filename; a.rel = 'noopener';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      TS.toast('ההורדה החלה: ' + filename);
    } catch (e) {
      TS.toast('ההורדה נחסמה בדפדפן. נסו ״העתקה״.');
    }
    return Promise.resolve();
  };

  TS.fetchFile = function (path, binary) {
    return fetch(path, { cache: 'no-cache' }).then(function (r) {
      if (!r.ok) throw new Error('missing ' + path);
      return binary ? r.arrayBuffer() : r.text();
    });
  };

  /* מוריד קובץ שפורסם יחד עם האתר. קובצי ZIP נבנים בדפדפן מהקבצים המפורסמים. */
  TS.downloadPublished = function (path, filename) {
    var rec = /\.zip$/i.test(path) && TS.library && TS.library.recipe ? TS.library.recipe(path) : null;
    if (rec && window.JSZip) {
      return Promise.all(rec.map(function (e) { return TS.fetchFile(e[1]).then(function (t) { return [e[0], t]; }); }))
        .then(function (entries) {
          var z = new window.JSZip();
          entries.forEach(function (e) { z.file(e[0], e[1]); });
          return z.generateAsync({ type: 'blob', mimeType: 'application/zip' });
        })
        .then(function (blob) { return TS.save(filename || path.split('/').pop(), blob, 'application/zip'); })
        .catch(function () { TS.toast('יצירת ה־ZIP נכשלה. הורידו את הקבצים אחד אחד מהספרייה.'); });
    }
    var binary = /\.(zip|png)$/i.test(path);
    return TS.fetchFile(path, binary).then(function (data) {
      return TS.save(filename || path.split('/').pop(), data, /\.png$/i.test(path) ? 'image/png' : binary ? 'application/zip' : 'text/plain;charset=utf-8');
    }, function () {
      TS.toast('הקובץ לא נמצא. אם פתחתם את האתר מקובץ מקומי, השתמשו בכתובת המפורסמת.');
    });
  };

  /* ---------- דיאלוגים ---------- */
  TS.openDialog = function (d) {
    if (typeof d.showModal === 'function') { if (!d.open) d.showModal(); } else { d.setAttribute('open', ''); }
  };
  TS.closeDialog = function (d) {
    if (typeof d.close === 'function') d.close(); else d.removeAttribute('open');
  };
  TS.openViewer = function (title, text, actionsHtml, onActions) {
    $('#viewer-title').textContent = title;
    $('#viewer-text').textContent = text;
    $('#viewer-actions').innerHTML = actionsHtml || '';
    if (onActions) onActions($('#viewer-actions'));
    TS.openDialog($('#viewer'));
  };

  /* ---------- הערכה שלי: הנחיות ששמרתם, מקומי בדפדפן ---------- */
  TS.kit = {
    list: function () { return TS.store.get('kit', []); },
    add: function (item) {
      var l = TS.kit.list();
      item.id = 'k' + Date.now();
      item.date = new Date().toLocaleDateString('he-IL');
      l.unshift(item);
      TS.store.set('kit', l.slice(0, 40));
      TS.kit.badge();
      return item;
    },
    remove: function (id) {
      TS.store.set('kit', TS.kit.list().filter(function (x) { return x.id !== id; }));
      TS.kit.badge();
    },
    badge: function () {
      var n = TS.kit.list().length, b = $('#kit-count');
      if (!b) return;
      b.textContent = n; b.hidden = n === 0;
    },
    markdown: function () {
      var l = TS.kit.list();
      var out = ['# הערכה האישית שלי', '', '> נוצר ב״' + TS.meta.siteName + '״. נשמר בדפדפן בלבד.', ''];
      l.forEach(function (x) {
        out.push('## ' + x.title + (x.topic ? ': ' + x.topic : ''));
        out.push('', '~~~text', x.text, '~~~', '');
      });
      return out.join('\n');
    },
    render: function () {
      var l = TS.kit.list(), body = $('#kit-body'), acts = $('#kit-actions');
      if (!l.length) {
        body.innerHTML = '<p class="muted">עדיין לא שמרתם הנחיות. בסוף כל מסלול בסטודיו יש כפתור ״שמירה בערכה שלי״.</p><p class="muted small" style="margin-top:8px">הערכה נשמרת בדפדפן הזה בלבד. כדי לשמור לצמיתות, הורידו קובץ.</p>';
        acts.innerHTML = '';
        return;
      }
      body.innerHTML = '<ul class="kit-list">' + l.map(function (x) {
        return '<li><div><b>' + esc(x.title) + '</b><span class="muted small">' + esc(x.topic || '') + ' · ' + esc(x.date) + '</span></div>' +
          '<div class="row" style="gap:6px"><button class="btn sm" type="button" data-kit-copy="' + x.id + '">' + TS.icon('copy') + 'העתקה</button>' +
          '<button class="btn sm" type="button" data-kit-open="' + x.id + '">פתיחה בסטודיו</button>' +
          '<button class="btn sm ghost" type="button" data-kit-del="' + x.id + '" aria-label="מחיקה">' + TS.icon('trash') + '</button></div></li>';
      }).join('') + '</ul><p class="muted small" style="margin-top:14px">הערכה נשמרת בדפדפן הזה בלבד ולא עוברת בין מכשירים. הורדה לקובץ שומרת עותק קבוע.</p>';
      acts.innerHTML = '<button class="btn primary" type="button" id="kit-dl">' + TS.icon('download') + 'הורדת כל הערכה (Markdown)</button>';
      $('#kit-dl').addEventListener('click', function () { TS.save('teacher-kit.md', TS.kit.markdown()); });
    }
  };

  /* ---------- ניתוב ---------- */
  TS.views = {};
  var current = { token: null };

  function parse(token) {
    token = (token || '').replace(/^#/, '') || 'home';
    var m;
    if ((m = /^task-([a-z]+)$/.exec(token)) && TS.engine.byId(m[1])) return { view: 'studio', param: m[1], section: 'studio' };
    if ((m = /^adv-([a-z]+)$/.exec(token))) return { view: 'advanced', param: m[1], section: 'advanced' };
    if ((m = /^tool-([a-z]+)$/.exec(token)) && TS.tools[m[1]]) return { view: 'tools', param: m[1], section: 'tools' };
    if ((m = /^ch-([a-z]+)$/.exec(token))) return { view: 'story', param: m[1], section: 'story' };
    if (token === 'lab') return { view: 'studio', param: 'lab', section: 'studio' };
    if (token === 'morning') return { view: 'training', param: 'morning', section: 'training' };
    if (token === 'survey') return { view: 'training', param: 'survey', section: 'training' };
    if (TS.views[token]) return { view: token, param: null, section: token };
    return { view: 'home', param: null, section: 'home' };
  }

  function reduced() { return !!(TS.fx && TS.fx.reduced()); }

  TS.render = function (token, opts) {
    opts = opts || {};
    var r = parse(token);
    var main = $('#main');
    function swap() {
      /* מחליפים את האלמנט עצמו כדי שמאזיני אירועים של מסך קודם לא יישארו פעילים */
      var fresh = main.cloneNode(false); main.parentNode.replaceChild(fresh, main); main = fresh;
      var out = TS.views[r.view](r.param);
      main.innerHTML = out.html;
      document.title = (out.title ? out.title + ' · ' : '') + TS.meta.siteName;
      $$('.links a').forEach(function (a) {
        var on = a.getAttribute('data-section') === r.section;
        if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
      });
      TS.closeMenu();
      if (out.after) out.after(main);
      if (!opts.keepScroll) window.scrollTo(0, 0);
      if (!opts.noFocus) main.focus({ preventScroll: true });
      if (TS.fx) { TS.fx.scan(main); TS.fx.navInd(); TS.fx.progress(); }
    }
    current.token = (token || '').replace(/^#/, '') || 'home';
    if (document.startViewTransition && !opts.instant && !reduced() && current.booted) {
      try { document.startViewTransition(swap); } catch (e) { swap(); }
    } else { swap(); }
    current.booted = true;
  };

  TS.go = function (token, opts) {
    token = token || 'home';
    try { if (location.hash !== '#' + token) { history.replaceState(null, '', '#' + token); } } catch (e) { /* בלי היסטוריה */ }
    TS.render(token, opts);
  };

  window.addEventListener('hashchange', function () {
    var t = (location.hash || '').replace(/^#/, '') || 'home';
    if (t !== current.token) TS.render(t);
  });

  /* ---------- תפריט נייד ---------- */
  TS.closeMenu = function () {
    var nav = $('#site-nav'), b = $('#btn-menu');
    if (nav) nav.classList.remove('open');
    if (b) b.setAttribute('aria-expanded', 'false');
    document.documentElement.style.overflow = '';
  };

  /* ---------- אירועים כלליים ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-route]');
    if (a && !e.defaultPrevented && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      TS.go(a.getAttribute('data-route'));
      return;
    }
    var c = e.target.closest('[data-close]');
    if (c) { var d = c.closest('dialog'); if (d) TS.closeDialog(d); return; }
    var cp = e.target.closest('[data-copy-text]');
    if (cp) { TS.copy(cp.getAttribute('data-copy-text'), null, cp); return; }
    var cs = e.target.closest('[data-copy-sel]');
    if (cs) { var el = $(cs.getAttribute('data-copy-sel')); if (el) TS.copy(el.textContent, null, cs); return; }
    var kc = e.target.closest('[data-kit-copy]');
    if (kc) { var it = TS.kit.list().filter(function (x) { return x.id === kc.getAttribute('data-kit-copy'); })[0]; if (it) TS.copy(it.text, null, kc); return; }
    var kd = e.target.closest('[data-kit-del]');
    if (kd) { TS.kit.remove(kd.getAttribute('data-kit-del')); TS.kit.render(); return; }
    var ko = e.target.closest('[data-kit-open]');
    if (ko) {
      var it2 = TS.kit.list().filter(function (x) { return x.id === ko.getAttribute('data-kit-open'); })[0];
      TS.closeDialog($('#kit'));
      if (it2) TS.go('task-' + it2.taskId);
      return;
    }
    var dl = e.target.closest('[data-dl]');
    if (dl) { TS.downloadPublished(dl.getAttribute('data-dl'), dl.getAttribute('data-name')); return; }
    var vw = e.target.closest('[data-view]');
    if (vw) {
      var p = vw.getAttribute('data-view'), nm = vw.getAttribute('data-name') || p.split('/').pop();
      TS.fetchFile(p).then(function (txt) {
        TS.openViewer(nm, txt,
          '<button class="btn" type="button" id="v-copy">' + TS.icon('copy') + 'העתקה</button><button class="btn primary" type="button" id="v-dl">' + TS.icon('download') + 'הורדה</button>',
          function (box) {
            $('#v-copy', box).addEventListener('click', function () { TS.copy(txt); });
            $('#v-dl', box).addEventListener('click', function () { TS.save(nm, txt); });
          });
      }, function () { TS.toast('הקובץ לא נמצא. פתחו את האתר בכתובת המפורסמת.'); });
      return;
    }
    if (!e.target.closest('#prefs, #btn-prefs')) { var pf = $('#prefs'); if (pf && !pf.hidden) { pf.hidden = true; $('#btn-prefs').setAttribute('aria-expanded', 'false'); } }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var pf = $('#prefs');
      if (pf && !pf.hidden) { pf.hidden = true; $('#btn-prefs').setAttribute('aria-expanded', 'false'); $('#btn-prefs').focus(); }
      var nav = $('#site-nav.open');
      if (nav) { TS.closeMenu(); $('#btn-menu').focus(); }
    }
  });

  /* ---------- מעטפת: ערכת צבעים, הקרנה, תנועה, תפריטים ---------- */
  TS.chrome = function () {
    var root = document.documentElement;
    root.classList.add('js');
    var THEMES = ['auto', 'light', 'dark'], THEME_LABEL = { auto: 'אוטומטי', light: 'בהיר', dark: 'כהה' };

    function applyTheme() {
      var t = TS.store.get('theme', 'auto');
      if (t === 'auto') { if (TS.store.get('theme-touched', false)) root.removeAttribute('data-theme'); }
      else root.setAttribute('data-theme', t);
      $('#pf-theme-st').textContent = THEME_LABEL[t] || 'אוטומטי';
    }
    function applyFlag(key, cls, stId) {
      var on = !!TS.store.get(key, false);
      root.classList.toggle(cls, on);
      $('#' + stId).textContent = on ? 'פעיל' : 'כבוי';
      return on;
    }
    applyTheme(); applyFlag('proj', 'proj', 'pf-size-st'); applyFlag('reduce', 'reduce', 'pf-motion-st');

    $('#pf-theme').addEventListener('click', function () {
      var t = TS.store.get('theme', 'auto'), n = THEMES[(THEMES.indexOf(t) + 1) % THEMES.length];
      TS.store.set('theme', n); TS.store.set('theme-touched', true); applyTheme();
    });
    $('#pf-size').addEventListener('click', function () { TS.store.set('proj', !TS.store.get('proj', false)); applyFlag('proj', 'proj', 'pf-size-st'); setTimeout(function () { TS.fx.navInd(); }, 60); });
    $('#pf-motion').addEventListener('click', function () { TS.store.set('reduce', !TS.store.get('reduce', false)); applyFlag('reduce', 'reduce', 'pf-motion-st'); TS.fx.scan($('#main')); });

    $('#btn-prefs').addEventListener('click', function (e) {
      e.stopPropagation();
      var p = $('#prefs'); p.hidden = !p.hidden;
      this.setAttribute('aria-expanded', p.hidden ? 'false' : 'true');
    });
    $('#btn-menu').addEventListener('click', function () {
      var nav = $('#site-nav'), open = !nav.classList.contains('open');
      nav.classList.toggle('open', open);
      this.setAttribute('aria-expanded', open ? 'true' : 'false');
      root.style.overflow = open ? 'hidden' : '';
    });
    $('#btn-kit').addEventListener('click', function () { TS.kit.render(); TS.openDialog($('#kit')); });
    $$('dialog').forEach(function (d) {
      d.addEventListener('click', function (e) { if (e.target === d) TS.closeDialog(d); });
    });
    TS.kit.badge();
  };

})(window.TS = window.TS || {});
