/* הפעלת האתר */
(function (TS) {
  'use strict';
  function boot() {
    TS.chrome();
    TS.fx.init();
    TS.palette.init();
    TS.initCaps();
    var t = (location.hash || '').replace(/^#/, '') || 'home';
    TS.render(t, { noFocus: true, instant: true });
    TS.bidi.init();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})(window.TS = window.TS || {});
