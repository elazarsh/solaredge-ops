/* הסיפור: הגאון והשולחן */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  function person(cx, cy, r, extra) {
    return '<circle class="pp" cx="' + cx + '" cy="' + cy + '" r="' + r + '"/><path class="st" d="M' + (cx - r * 1.5) + ' ' + (cy + r * 3.4) + ' C' + (cx - r * 1.5) + ' ' + (cy + r * 1.6) + ' ' + (cx - r * 0.8) + ' ' + (cy + r * 1.2) + ' ' + cx + ' ' + (cy + r * 1.2) + ' C' + (cx + r * 0.8) + ' ' + (cy + r * 1.2) + ' ' + (cx + r * 1.5) + ' ' + (cy + r * 1.6) + ' ' + (cx + r * 1.5) + ' ' + (cy + r * 3.4) + '"/>' + (extra || '');
  }

  function sceneSvg() {
    return '<svg viewBox="0 0 400 340" role="img" aria-label="איור: גאון ליד שולחן עבודה, עם ארון קלסרים, ספרייה, אנשי צוות, פעמון ומורה אחראי">' +
      '<path class="st" d="M10 318 H390" opacity=".5"/>' +
      /* שולחן */
      '<g class="it on" id="sc-desk"><rect class="pp" x="70" y="214" width="260" height="12" rx="3"/><path class="st" d="M86 226 V318 M314 226 V318"/></g>' +
      /* הגאון */
      '<g class="it" id="sc-model"><circle class="pp" cx="200" cy="128" r="21"/><path class="st" d="M184 122 C186 108 214 108 216 122"/><path class="fl" d="M168 214 C168 172 178 154 200 154 C222 154 232 172 232 214 Z"/><path class="st" d="M188 176 h24 M188 184 h24 M200 170 v22"/><text x="200" y="96" text-anchor="middle">הגאון (המודל)</text></g>' +
      /* חלון הקשר */
      '<g class="it" id="sc-window"><rect x="88" y="176" width="224" height="44" rx="6" fill="none" stroke="var(--brand)" stroke-width="2" stroke-dasharray="6 5"/><text x="132" y="170" text-anchor="middle" style="fill:var(--brand);font-weight:600">חלון ההקשר</text></g>' +
      /* שולחן: פרומפט, פרויקט, עמודי RAG */
      '<g class="it" id="sc-context"><rect class="pp" x="236" y="192" width="30" height="22" rx="2"/><path class="st" d="M242 198 h18 M242 204 h12"/><rect class="pp" x="270" y="194" width="28" height="20" rx="2"/></g>' +
      '<g class="it" id="sc-prompt"><rect class="pp" x="100" y="186" width="32" height="28" rx="2"/><path class="st" d="M106 194 h20 M106 200 h20 M106 206 h12"/><text x="118" y="242" text-anchor="middle">כתב משימה</text></g>' +
      '<g class="it" id="sc-project"><path class="fl" d="M142 190 h14 l4 4 h24 v20 h-42 z"/><text x="180" y="242" text-anchor="middle">תיק פרויקט</text></g>' +
      /* קלסרים */
      '<g class="it" id="sc-skill"><rect class="fl" x="22" y="120" width="14" height="60" rx="2"/><rect class="fb" x="40" y="116" width="14" height="64" rx="2" opacity=".85"/><rect class="fl" x="58" y="124" width="14" height="56" rx="2"/><path class="st" d="M14 182 H80"/><text x="48" y="104" text-anchor="middle">קלסרי שיטות</text></g>' +
      /* ספרייה וספרן */
      '<g class="it" id="sc-rag"><path class="st" d="M286 104 H388 M286 62 H388"/><rect class="fl" x="292" y="72" width="10" height="30"/><rect class="fb" x="304" y="68" width="10" height="34"/><rect class="fl" x="316" y="74" width="10" height="28"/><rect class="fl" x="328" y="70" width="10" height="32"/><rect class="fb" x="340" y="72" width="10" height="30" opacity=".7"/><rect class="fl" x="352" y="66" width="10" height="36"/><rect class="fl" x="364" y="72" width="10" height="30"/>' +
        person(338, 132, 8, '<circle class="st" cx="360" cy="150" r="6"/><path class="st" d="M364 154 L371 161"/>') +
        '<path class="st" d="M330 170 C318 190 300 196 290 200" stroke-dasharray="4 4"/><text x="345" y="56" text-anchor="middle">ספרייה וספרן (RAG)</text></g>' +
      /* צוות */
      '<g class="it" id="sc-agents">' + person(60, 262, 6) + person(100, 262, 6) + person(140, 262, 6) + '<path class="st" d="M60 244 C64 232 90 224 112 218 M100 244 V226 M140 244 C136 232 128 226 118 220" stroke-dasharray="4 4"/><text x="100" y="302" text-anchor="middle">אנשי צוות (סוכנים)</text></g>' +
      /* פעמון */
      '<g class="it" id="sc-hook"><path class="st" d="M200 0 V0"/><path class="st" d="M44 0 V26"/><path class="fl" d="M30 52 C30 38 36 30 44 30 C52 30 58 38 58 52 L62 58 H26 Z"/><path class="st" d="M40 62 q4 6 8 0"/><text x="44" y="82" text-anchor="middle">פעמון (Hook)</text></g>' +
      /* מורה אחראי */
      '<g class="it" id="sc-qa">' + person(344, 262, 7) + '<circle class="fb" cx="372" cy="246" r="11"/><path d="M366 246 l4 4 l8 -9" fill="none" stroke="var(--brand-ink)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><text x="344" y="302" text-anchor="middle">המורה האחראי</text></g>' +
    '</svg>';
  }

  var SCENE_MAP = {
    model: ['model'], prompt: ['prompt'], context: ['prompt', 'project', 'context', 'rag-pages'],
    window: ['window', 'context', 'prompt', 'project'], project: ['project'], skill: ['skill'], rag: ['rag', 'context'],
    agents: ['agents'], hook: ['hook'], qa: ['qa']
  };

  function chapterHtml(c) {
    var tagHtml = c.tag === 'tool' ? '<span class="tag sec">תלוי בכלי</span>' : c.tag === 'adv' ? '<span class="tag brand">למתקדמים</span>' : '';
    var table = c.table ? '<div class="tbl-wrap" style="margin-top:12px"><table class="tbl"><thead><tr><th>מושג</th><th>מה זה</th></tr></thead><tbody>' + c.table.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + esc(r.v) + '</td></tr>'; }).join('') + '</tbody></table></div>' : '';
    var widget = c.widget === 'desk' ? deskWidget() : '';
    return '<article class="chapter" id="ch-' + c.id + '" data-ch="' + c.id + '" aria-labelledby="h-' + c.id + '">' +
      '<div class="term"><span class="ic">' + icon(c.icon) + '</span><span class="eyebrow">' + esc(c.term) + '</span>' + tagHtml + '</div>' +
      '<h3 id="h-' + c.id + '">' + esc(c.title) + '</h3>' +
      '<p class="parable">' + esc(c.parable) + '</p>' +
      '<h4>מה זה אומר בפועל</h4><p class="prose">' + esc(c.meaning) + '</p>' + table + widget +
      '<div class="for-teacher"><b>דוגמה למורה</b><p>' + esc(c.teacher) + '</p></div>' +
      '<details class="more"><summary>מה המשל מפשט?</summary><div><p class="prose">' + esc(c.simplifies) + '</p></div></details>' +
    '</article>';
  }

  function deskWidget() {
    var d = TS.story.desk;
    return '<div class="desk-widget" id="desk-widget"><b>הדמיית השולחן</b><p class="muted small">סמנו מה מונח על השולחן. הגדלים להמחשה בלבד: בכלים אמיתיים מדובר בטוקנים והגבול משתנה.</p>' +
      '<div class="stack" style="gap:4px">' + d.items.map(function (it) {
        return '<label class="chip" style="display:flex"><input type="checkbox" data-desk="' + it.id + '"' + (it.on ? ' checked' : '') + '><span style="width:100%;justify-content:space-between">' + esc(it.label) + ' <em>' + it.size + ' יחידות</em></span></label>';
      }).join('') + '</div>' +
      '<div class="desk-bar" id="desk-bar" role="img" aria-label="מילוי השולחן"></div>' +
      '<div class="row between"><span class="small muted">קיבולת השולחן: ' + d.capacity + ' יחידות</span><b id="desk-sum"></b></div>' +
      '<p class="desk-msg" id="desk-msg" role="status"></p></div>';
  }

  TS.views.story = function (param) {
    var S = TS.story;
    var html =
      '<div class="wrap page-head"><span class="eyebrow">הסיפור</span><h1>' + esc(S.intro.title) + '</h1><p class="lead">' + esc(S.intro.lead) + '</p><p class="muted prose">' + esc(S.intro.how) + '</p></div>' +
      '<div class="wrap"><nav class="chap-nav" aria-label="פרקי הסיפור">' + S.chapters.map(function (c) { return '<a href="#ch-' + c.id + '" data-chgo="' + c.id + '">' + esc(c.term) + '</a>'; }).join('') + '<a href="#glossary" data-chgo="glossary">מילון</a></nav></div>' +
      '<hr class="ruler">' +
      '<div class="wrap section tight"><div class="story-grid"><div>' + S.chapters.map(chapterHtml).join('') +
        '<section class="chapter" id="glossary" aria-labelledby="h-gl"><h3 id="h-gl">הכול ביחד, והמילון</h3><p class="prose" style="margin-top:12px">' + esc(S.mapNote) + '</p>' +
        '<div class="tbl-wrap" style="margin-top:16px"><table class="tbl gloss"><thead><tr><th>מושג</th><th>בקצרה</th><th>מה זה לא</th></tr></thead><tbody>' + S.glossary.map(function (g) { return '<tr><td>' + esc(g.term) + '</td><td>' + esc(g.short) + '</td><td>' + esc(g.notThis) + '</td></tr>'; }).join('') + '</tbody></table></div>' +
        '<div class="row" style="margin-top:20px"><a class="btn primary" href="#studio" data-route="studio">לכלי העבודה ' + icon('arrow-left') + '</a><a class="btn" href="#lab" data-route="lab">מעבדת הבקשה</a></div></section>' +
      '</div><aside class="scene" aria-label="איור הסיפור">' + sceneSvg() + '<p class="hint" style="margin-top:8px">האיור מתעדכן לפי הפרק שאתם קוראים.</p></aside></div></div>';

    return {
      title: 'הסיפור: הגאון והשולחן', html: html,
      after: function (root) {
        var svg = $('.scene svg', root);
        function setScene(id) {
          $$('.it', svg).forEach(function (g) { if (g.id !== 'sc-desk') g.classList.remove('on'); });
          (SCENE_MAP[id] || []).forEach(function (k) { var g = $('#sc-' + k, svg); if (g) g.classList.add('on'); });
          $$('.chap-nav a', root).forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-chgo') === id); });
        }
        setScene('model');
        if ('IntersectionObserver' in window) {
          var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (en) { if (en.isIntersecting) setScene(en.target.getAttribute('data-ch')); });
          }, { rootMargin: '-30% 0px -60% 0px' });
          $$('.chapter[data-ch]', root).forEach(function (c) { io.observe(c); });
        }
        $$('[data-chgo]', root).forEach(function (a) {
          a.addEventListener('click', function (e) {
            e.preventDefault();
            var t = $('#' + (a.getAttribute('data-chgo') === 'glossary' ? 'glossary' : 'ch-' + a.getAttribute('data-chgo')), root);
            if (t) { t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
          });
        });
        if (param) { var t = $('#ch-' + param, root); if (t) setTimeout(function () { t.scrollIntoView(); }, 50); }

        /* הדמיית השולחן */
        var w = $('#desk-widget', root);
        if (w) {
          var d = TS.story.desk;
          var draw = function () {
            var sum = 0, bar = $('#desk-bar', w), parts = '', i = 0;
            $$('[data-desk]', w).forEach(function (cb) {
              if (!cb.checked) return;
              var it = d.items.filter(function (x) { return x.id === cb.getAttribute('data-desk'); })[0];
              i++;
              var room = Math.max(0, d.capacity - sum), used = Math.min(room, it.size);
              if (used > 0) parts += '<span class="f' + Math.min(i, 5) + '" style="width:' + (used / d.capacity * 100) + '%" title="' + esc(it.label) + '">' + (used >= 8 ? esc(it.label.split(' ')[0]) : '') + '</span>';
              if (it.size > used) parts += '<span class="over" style="width:' + Math.max(2, (it.size - used) / d.capacity * 100) + '%" title="לא נכנס: ' + esc(it.label) + '">!</span>';
              sum += it.size;
            });
            bar.innerHTML = parts;
            $('#desk-sum', w).textContent = sum + ' מתוך ' + d.capacity;
            var m = $('#desk-msg', w);
            if (sum > d.capacity) { m.className = 'desk-msg bad'; m.textContent = 'השולחן מלא. משהו לא נכנס: הכלי יקצץ, יסכם או ישכח. מה עושים? שיחה חדשה למשימה חדשה, קובץ קצר יותר, והחומר החשוב קרוב לבקשה.'; }
            else if (sum > d.capacity * 0.8) { m.className = 'desk-msg'; m.textContent = 'השולחן כמעט מלא. עוד קצת והפרטים הראשונים עלולים להידחק החוצה.'; }
            else { m.className = 'desk-msg'; m.textContent = 'יש מקום על השולחן. הגאון רואה את הכול.'; }
          };
          w.addEventListener('change', draw); draw();
        }
      }
    };
  };

})(window.TS = window.TS || {});
