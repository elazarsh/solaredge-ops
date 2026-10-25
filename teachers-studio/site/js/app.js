/* הפעלת האתר */
(function (TS) {
  'use strict';
  function boot() {
    TS.chrome();
    TS.initCaps();
    var t = (location.hash || '').replace(/^#/, '') || 'home';
    TS.render(t, { noFocus: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})(window.TS = window.TS || {});
