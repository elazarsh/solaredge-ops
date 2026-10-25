/* RTL: בידוד אוטומטי של קטעי לטינית ושל ביטויים מספריים בתוך טקסט עברי.
   בלי זה, רצף כמו "Create skill ← Upload a skill" או "2/5 + 1/5" מסתדר בסדר הפוך. */
(function (TS) {
  'use strict';
  var B = TS.bidi = {};

  var LAT = '[A-Za-z][A-Za-z0-9]*(?:(?:[ ]|, |[.\\-_/:@+&\'’])[A-Za-z0-9]+)*';
  var MATH = '\\d[\\d.,/:%]*(?:\\s*[+\\-−–—×÷=*]\\s*\\d[\\d.,/:%]*)+';
  var RE = new RegExp('(' + MATH + ')|(' + LAT + ')', 'g');
  var SKIP = 'pre,code,kbd,samp,textarea,input,select,option,script,style,svg,bdi,[dir=ltr],.ltr,[contenteditable]';

  function wrapText(node) {
    var text = node.nodeValue;
    if (!text || !/[A-Za-z0-9]/.test(text)) return;
    var p = node.parentNode;
    if (!p || (p.closest && p.closest(SKIP))) return;
    RE.lastIndex = 0;
    var m, last = 0, frag = null;
    while ((m = RE.exec(text))) {
      if (!frag) frag = document.createDocumentFragment();
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      var b = document.createElement('bdi');
      b.setAttribute('dir', 'ltr');
      if (m[2]) b.setAttribute('lang', 'en');
      b.textContent = m[0];
      frag.appendChild(b);
      last = m.index + m[0].length;
    }
    if (!frag) return;
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    /* בתוך flex/grid כל צאצא הוא פריט נפרד עם רווח: עוטפים בפריט אחד כדי שהרווחים לא יתפצלו סביב הקטע הלטיני */
    var d = window.getComputedStyle(p).display;
    if (/flex|grid/.test(d)) { var box = document.createElement('span'); box.appendChild(frag); frag = box; }
    p.replaceChild(frag, node);
  }

  B.run = function (root) {
    root = root || document.body;
    if (root.nodeType === 3) { wrapText(root); return; }
    if (root.nodeType !== 1 || (root.closest && root.closest(SKIP))) return;
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n, list = [];
    while ((n = w.nextNode())) list.push(n);
    list.forEach(wrapText);
  };

  /* שדות טקסט: כיוון לפי התוכן. שדה ריק נשאר RTL כדי שהסמן והרמז יהיו מימין */
  var FIELD = 'input[type=text],input[type=search],input:not([type]),textarea';
  function fieldDir(el) { var d = el.value && el.value.trim() ? 'auto' : 'rtl'; if (el.getAttribute('dir') !== d) el.setAttribute('dir', d); }
  B.fields = function (root) { (root || document).querySelectorAll(FIELD).forEach(fieldDir); };

  /* דף HTML עצמאי בעברית (RTL): נפתח נכון בדפדפן וב־Word, בניגוד לקובץ Markdown בעורך טקסט פשוט */
  B.htmlDoc = function (title, text) {
    function e(x) { return String(x).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
    return '<!doctype html>\n<html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + e(title) + '</title>' +
      '<style>body{font:17px/1.75 Arial,Helvetica,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1.2rem;color:#1a1e27}h1{font-size:1.5rem}pre{white-space:pre-wrap;font:inherit}@media print{body{margin:0;max-width:none}}</style></head><body><h1>' + e(title) + '</h1><pre>' + e(text) + '</pre></body></html>\n';
  };

  B.init = function () {
    B.run(document.body); B.fields(document);
    document.addEventListener('input', function (e) { if (e.target.matches && e.target.matches(FIELD)) fieldDir(e.target); }, true);
    if (!window.MutationObserver) return;
    var queue = [], sched = false;
    function flush() {
      sched = false; var q = queue; queue = [];
      q.forEach(function (n) { if (n.isConnected) { B.run(n); if (n.nodeType === 1) B.fields(n); } });
    }
    new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        m.addedNodes.forEach(function (n) { if (n.nodeType === 1 || n.nodeType === 3) queue.push(n); });
        if (m.type === 'characterData') queue.push(m.target);
      });
      if (queue.length && !sched) { sched = true; (window.requestAnimationFrame || setTimeout)(flush); }
    }).observe(document.body, { childList: true, subtree: true, characterData: true });
  };
})(window.TS = window.TS || {});
