/* Shared helpers for the three lyric-reading pages. Needs data.js (window.SONG). */
(function () {
  var S = window.SONG;
  var E = (window.E = { S: S, listeners: {}, t: 0, playing: false, audioOK: true });

  E.esc = function (s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  };
  E.clamp = function (x, a, b) { return Math.max(a, Math.min(b, x)); };
  E.lerp = function (a, b, t) { return a + (b - a) * t; };
  E.smooth = function (t) { t = E.clamp(t, 0, 1); return t * t * (3 - 2 * t); };
  E.fmt = function (t) { t = Math.max(0, Math.round(t)); return Math.floor(t / 60) + ":" + String(t % 60).padStart(2, "0"); };

  /* colours: "#rrggbb" <-> [r,g,b] */
  E.rgb = function (h) { h = h.replace("#", ""); return [0, 2, 4].map(function (i) { return parseInt(h.substr(i, 2), 16); }); };
  E.mix = function (a, b, t) { return a.map(function (v, i) { return v + (b[i] - v) * t; }); };
  E.css = function (c, a) { return a == null ? "rgb(" + c.map(Math.round).join(",") + ")" : "rgba(" + c.map(Math.round).join(",") + "," + a + ")"; };

  /* ---- events */
  E.on = function (ev, fn) { (E.listeners[ev] = E.listeners[ev] || []).push(fn); };
  E.emit = function (ev, a) { (E.listeners[ev] || []).forEach(function (f) { f(a); }); };

  /* ---- station lookup */
  E.stationAt = function (t) {
    var st = S.stations, k = 0;
    for (var i = 0; i < st.length; i++) if (t >= st[i].t0 - 0.6) k = i;
    return k;
  };

  /* ---- markup builders (each page styles the classes itself) */
  E.lyricsHTML = function (st) {
    return st.ids.map(function (id) {
      var z = S.stanzas[id];
      var lines = z.lines.map(function (line) {
        var ws = line.map(function (w) {
          return '<span class="w' + (w[3] ? " em" : "") + '" data-s="' + w[1] + '" data-e="' + w[2] + '">' + E.esc(w[0]) + "</span>";
        }).join(" ");
        return '<span class="ln">' + ws + "</span>";
      }).join("");
      return '<p class="stz ' + z.kind + '" data-seek="' + z.t0 + '" tabindex="0" title="לחצו כדי לשמוע את הבית הזה">' + lines + "</p>";
    }).join("");
  };

  E.bodyHTML = function (st) {
    return st.body.map(function (p) { return "<p>" + E.esc(p) + "</p>"; }).join("");
  };

  E.refHTML = function (r) {
    return '<li class="ref"><span class="ref-src">' + E.esc(r.src) + '</span><span class="ref-kind">' + E.esc(r.kind) + "</span>" +
      '<q class="ref-q">' + E.esc(r.text) + "</q>" +
      (r.why ? '<span class="ref-why">' + E.esc(r.why) + "</span>" : "") +
      '<a class="ref-link" href="' + E.esc(r.url) + '" target="_blank" rel="noopener">לפתוח בספריא</a></li>';
  };
  E.refsHTML = function (list) {
    return '<ul class="refs">' + list.map(E.refHTML).join("") + "</ul>";
  };

  E.samplesIn = function (st) {
    return S.samples.filter(function (s) { return s.at >= st.t0 - 0.5 && s.at < st.t1 + 0.5; });
  };
  E.workName = function (k) { return S.inspirations.filter(function (i) { return i.key === k; })[0].title; };

  E.inspHTML = function (ins) {
    var spots = S.samples.filter(function (s) { return s.work === ins.key; }).map(function (s) {
      return '<li><b>' + E.fmt(s.at) + "</b> " + E.esc(s.note) + "</li>";
    }).join("");
    return '<div class="insp-head"><h3>' + E.esc(ins.title) + '</h3><div class="insp-sub">' + E.esc(ins.sub) + "</div></div>" +
      '<div class="insp-grid">' +
      '<div class="insp-col"><h4>מה זה</h4><p>' + E.esc(ins.what) + "</p>" +
      '<h4>מה השיר לוקח ומה הוא משנה</h4><p>' + E.esc(ins.takes) + "</p>" +
      '<h4>איך זה נשמע</h4><p>' + E.esc(ins.place) + "</p>" +
      '<div class="creator-only"><h4>מיקומים מוצעים לדוגמית</h4><ul class="spots">' + spots + "</ul></div>" +
      '<p class="unv"><span>לא אומת</span> ' + E.esc(ins.unverified) + "</p>" +
      '<div class="insp-links">' + ins.links.map(function (l) { return '<a href="' + E.esc(l[1]) + '" target="_blank" rel="noopener">' + E.esc(l[0]) + "</a>"; }).join("") + "</div></div>" +
      '<div class="insp-col"><h4>השראות נוספות לציטוטים</h4>' + E.refsHTML(ins.also) + "</div></div>";
  };

  /* ---- audio */
  var a = (E.audio = new Audio());
  a.preload = "none";
  a.src = "song.mp3";
  a.addEventListener("error", function () { E.audioOK = false; E.emit("audioerror"); });
  a.addEventListener("play", function () { E.playing = true; E.emit("play"); });
  a.addEventListener("pause", function () { E.playing = false; E.emit("pause"); });
  a.addEventListener("ended", function () { E.playing = false; E.emit("pause"); E.emit("ended"); });
  E.play = function () { var p = a.play(); if (p && p.catch) p.catch(function () { E.audioOK = false; E.emit("audioerror"); }); };
  E.pause = function () { a.pause(); };
  E.toggle = function () { E.playing ? E.pause() : E.play(); };
  E.seek = function (t) { a.currentTime = t; E.t = t; };

  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-seek]");
    if (!el || e.target.closest("a")) return;
    E.seek(parseFloat(el.getAttribute("data-seek")) - 0.2);
    E.play();
  });
  document.addEventListener("keydown", function (e) {
    if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches("[data-seek]")) {
      e.preventDefault();
      E.seek(parseFloat(e.target.getAttribute("data-seek")) - 0.2);
      E.play();
    }
  });

  /* ---- word highlighting + frame loop */
  var words = null, wstate = [];
  E.indexWords = function () {
    words = Array.prototype.map.call(document.querySelectorAll(".w[data-s]"), function (el) {
      return { el: el, s: +el.dataset.s, e: +el.dataset.e };
    });
    wstate = words.map(function () { return 0; });
  };
  function paintWords(t, live) {
    if (!words) return;
    for (var i = 0; i < words.length; i++) {
      var w = words[i], st = !live ? 0 : t >= w.e ? 1 : t >= w.s ? 2 : 0;
      if (wstate[i] !== st) {
        wstate[i] = st;
        w.el.classList.toggle("past", st === 1);
        w.el.classList.toggle("now", st === 2);
      }
    }
  }
  E.frameFns = [];
  var lastLive = false;
  function frame() {
    E.t = a.currentTime;
    var live = E.playing || (a.currentTime > 0.05 && !a.ended && a.currentTime < S.dur - 0.05);
    if (live || lastLive) paintWords(E.t, live);
    lastLive = live;
    for (var i = 0; i < E.frameFns.length; i++) E.frameFns[i](E.t, live);
    requestAnimationFrame(frame);
  }
  E.start = function () { E.indexWords(); requestAnimationFrame(frame); };

  /* ---- creator mode (shows where the quiet samples sit) */
  E.setCreator = function (on) {
    document.body.classList.toggle("creator", !!on);
    try { localStorage.setItem("hineh-ayil-creator", on ? "1" : ""); } catch (e) {}
    E.emit("creator", on);
  };
  E.initCreator = function () {
    var on = false;
    try { on = !!localStorage.getItem("hineh-ayil-creator"); } catch (e) {}
    if (location.hash === "#creator") on = true;
    E.setCreator(on);
  };

  /* ---- continuous position over a list of sections: returns {i, f, u} (u = i + f) */
  E.position = function (els, anchor) {
    var y = window.scrollY + window.innerHeight * (anchor == null ? 0.5 : anchor);
    var i = 0;
    for (var k = 0; k < els.length; k++) { if (els[k].offsetTop <= y) i = k; }
    var top = els[i].offsetTop, h = els[i].offsetHeight || 1;
    var f = E.clamp((y - top) / h, 0, 1);
    return { i: i, f: f, u: i + f };
  };

  /* follow the audio by scrolling (pauses for a moment when the reader scrolls) */
  E.followScroll = function (els) {
    var manual = 0;
    ["wheel", "touchmove", "keydown"].forEach(function (ev) { window.addEventListener(ev, function () { manual = performance.now() + 5000; }, { passive: true }); });
    var cur = -1;
    E.frameFns.push(function (t, live) {
      if (!E.playing) { cur = -1; return; }
      var k = E.stationAt(t);
      if (k !== cur) {
        cur = k;
        if (performance.now() > manual) els[k].scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  };
})();
