/* אפקטים: חשיפה בגלילה, זוהר עוקב עכבר, הטיה תלת־ממדית, כפתורים מגנטיים, ספירה, מילים עולות,
   אינדיקטור ניווט, פס התקדמות ופיצוץ חלקיקים בהעתקה. הכול מכבד הפחתת תנועה. */
(function (TS) {
  'use strict';
  var $ = TS.$, $$ = TS.$$;
  var fx = TS.fx = {};
  var io = null;

  fx.reduced = function () {
    try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return true; } catch (e) { /* בלי matchMedia */ }
    return document.documentElement.classList.contains('reduce');
  };

  function count(el) {
    var to = parseFloat(el.getAttribute('data-count')), suf = el.getAttribute('data-suffix') || '';
    if (isNaN(to)) return;
    if (fx.reduced()) { el.textContent = to + suf; return; }
    var t0 = performance.now(), dur = 1200;
    (function step(t) {
      var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(to * e) + suf;
      if (p < 1) requestAnimationFrame(step);
    })(t0);
  }

  function words(el) {
    if (el.getAttribute('data-split')) return;
    el.setAttribute('data-split', '1');
    var txt = el.textContent.trim().split(/\s+/);
    el.setAttribute('aria-label', el.textContent.trim());
    el.innerHTML = txt.map(function (w, i) { return '<span class="w" aria-hidden="true"><span style="--i:' + i + '">' + TS.esc(w) + '</span></span>'; }).join(' ');
    el.classList.add('words');
  }

  /* סורק קטע חדש אחרי כל מעבר מסך */
  fx.scan = function (root) {
    root = root || document;
    if (io) { io.disconnect(); io = null; }
    var rv = $$('[data-rv]', root);
    $$('[data-words]', root).forEach(words);
    $$('[data-rv]', root).forEach(function (el, i) { if (!el.style.getPropertyValue('--i')) el.style.setProperty('--i', el.getAttribute('data-rv') || 0); });
    if (fx.reduced() || !('IntersectionObserver' in window)) {
      rv.forEach(function (el) { el.classList.add('in'); });
      $$('[data-count]', root).forEach(count);
      return;
    }
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        if (en.target.hasAttribute('data-count')) count(en.target);
        io.unobserve(en.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    rv.forEach(function (el) { io.observe(el); });
    $$('[data-count]', root).forEach(function (el) { if (!el.hasAttribute('data-rv')) io.observe(el); });
  };

  /* מיקום האינדיקטור החלק מתחת לקישור הפעיל */
  fx.navInd = function () {
    var ind = $('#nav-ind'), a = $('.links a[aria-current="page"]');
    if (!ind) return;
    if (!a || getComputedStyle(ind).display === 'none') { ind.style.opacity = '0'; return; }
    ind.style.left = a.offsetLeft + 'px';
    ind.style.width = a.offsetWidth + 'px';
    ind.style.opacity = '1';
  };

  var ticking = false;
  fx.progress = function () {
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? Math.min(100, Math.max(0, (window.pageYOffset / max) * 100)) : 0;
    var bar = $('#progress'); if (bar) bar.style.setProperty('--p', p + '%');
    var w = $('#nav-wrap'); if (w) w.classList.toggle('scrolled', window.pageYOffset > 12);
  };

  fx.burst = function (el) {
    if (fx.reduced()) return;
    var r = el && el.getBoundingClientRect ? el.getBoundingClientRect() : { left: window.innerWidth / 2, top: window.innerHeight / 2, width: 0, height: 0 };
    var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    for (var i = 0; i < 12; i++) {
      var d = document.createElement('i'); d.className = 'burst';
      var ang = (Math.PI * 2 * i) / 12 + Math.random() * 0.5, dist = 40 + Math.random() * 44;
      d.style.left = cx + 'px'; d.style.top = cy + 'px';
      d.style.setProperty('--dx', Math.cos(ang) * dist + 'px'); d.style.setProperty('--dy', Math.sin(ang) * dist + 'px');
      d.style.background = i % 3 === 0 ? 'var(--aura-1)' : i % 3 === 1 ? '#F29A5C' : 'var(--brand)';
      document.body.appendChild(d);
      setTimeout((function (n) { return function () { if (n.parentNode) n.parentNode.removeChild(n); }; })(d), 950);
    }
  };

  fx.init = function () {
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { fx.progress(); ticking = false; }); } }, { passive: true });
    window.addEventListener('resize', function () { fx.navInd(); fx.progress(); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fx.navInd(); });

    /* זוהר שעוקב אחרי העכבר, הטיה ומגנטיות */
    document.addEventListener('pointermove', function (e) {
      if (e.pointerType === 'touch' || fx.reduced()) return;
      var s = e.target.closest && e.target.closest('.spot');
      if (s) { var r = s.getBoundingClientRect(); s.style.setProperty('--mx', (e.clientX - r.left) + 'px'); s.style.setProperty('--my', (e.clientY - r.top) + 'px'); }
      var t = e.target.closest && e.target.closest('.tilt');
      if (t) {
        var b = t.getBoundingClientRect(), x = (e.clientX - b.left) / b.width - 0.5, y = (e.clientY - b.top) / b.height - 0.5;
        t.style.transform = 'rotateY(' + (x * -10).toFixed(2) + 'deg) rotateX(' + (y * 8).toFixed(2) + 'deg)';
      }
      var m = e.target.closest && e.target.closest('.mag');
      if (m) {
        var q = m.getBoundingClientRect(), dx = (e.clientX - (q.left + q.width / 2)) * 0.18, dy = (e.clientY - (q.top + q.height / 2)) * 0.25;
        m.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
      }
    });
    document.addEventListener('pointerout', function (e) {
      var t = e.target.closest && e.target.closest('.tilt'); if (t && !t.contains(e.relatedTarget)) t.style.transform = '';
      var m = e.target.closest && e.target.closest('.mag'); if (m && !m.contains(e.relatedTarget)) m.style.transform = '';
    });
  };

})(window.TS = window.TS || {});
