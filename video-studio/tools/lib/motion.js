/*
 * motion.js — pure-function-of-time motion helpers (springs, beat grid, drags, text swaps).
 * Every function takes the current time t and returns a value; nothing is stored between
 * frames, so any frame can be rendered in any order (seek-safe, loop-safe).
 *
 * Use in a HyperFrames composition:
 *   <script src="vendor/motion.js"></script>          // copy from video-studio/tools/lib/
 *   const M = window.Motion;
 *   M.bind(tl, DURATION, (t) => { el.style.width = M.track(t, widthKeys) + "px"; ... });
 */
(function (root) {
  // ---- springs -----------------------------------------------------------------------------
  // Step response of a damped spring from 0 to 1, closed form.
  // response = seconds for one undamped oscillation (≈ perceived speed); damping = ratio ζ.
  // ζ 0.85–0.9 → a tiny overshoot (<1%). ζ 1 → none. Below 0.7 starts to look "bouncy" (banned).
  function spring(t, response = 0.45, damping = 0.86) {
    if (t <= 0) return 0;
    const w = (2 * Math.PI) / response;
    const z = damping;
    if (z < 1) {
      const wd = w * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
    }
    if (z === 1) return 1 - Math.exp(-w * t) * (1 + w * t);
    const r1 = -w * (z - Math.sqrt(z * z - 1));
    const r2 = -w * (z + Math.sqrt(z * z - 1));
    return 1 + (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r1 - r2);
  }

  // A value whose target changes many times = start value + one spring per change.
  // keys: [{ t: seconds, v: target, response?, damping? }, ...] sorted by t; keys[0] is the start.
  function track(t, keys, response, damping) {
    let v = keys[0].v;
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i];
      if (t <= k.t) break;
      v += (k.v - keys[i - 1].v) * spring(t - k.t, k.response ?? response, k.damping ?? damping);
    }
    return v;
  }

  // Two edges on different springs: the leading edge is faster, so the shape stretches
  // while moving and settles back (liquid tab indicator, toggle knob).
  // keys: [{ t, left, right }] → { left, right, width }
  function edges(t, keys, lead = 0.32, trail = 0.55, damping = 0.9) {
    let left = keys[0].left, right = keys[0].right;
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i], p = keys[i - 1];
      if (t <= k.t) break;
      const movingRight = k.left + k.right > p.left + p.right;
      const rResp = movingRight ? lead : trail, lResp = movingRight ? trail : lead;
      left += (k.left - p.left) * spring(t - k.t, lResp, damping);
      right += (k.right - p.right) * spring(t - k.t, rResp, damping);
    }
    return { left, right, width: right - left };
  }

  // ---- direct manipulation -----------------------------------------------------------------
  // While held (t in [down, up]) the value follows the pointer: follow(t) → value.
  // After release it springs from wherever it was to `rest` (or stays if rest is undefined).
  function drag(t, { down, up, follow, rest, response = 0.4, damping = 0.88, before }) {
    if (t < down) return before ?? follow(down);
    if (t <= up) return follow(t);
    const at = follow(up);
    if (rest === undefined) return at;
    return at + (rest - at) * spring(t - up, response, damping);
  }

  // Rubber band past a limit (volume slider pulled past max): stretch decays logarithmically.
  function rubber(x, min, max, give = 0.55, span = 120) {
    if (x > max) return max + span * give * Math.log1p((x - max) / span);
    if (x < min) return min - span * give * Math.log1p((min - x) / span);
    return x;
  }

  // ---- easing / interpolation ---------------------------------------------------------------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const progress = (t, start, dur) => clamp((t - start) / dur);
  const easeOut = (p) => 1 - Math.pow(1 - p, 3);
  const easeInOut = (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
  function mixColor(a, b, p) { // hex → rgb string
    const h = (c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
    const A = h(a), B = h(b);
    return `rgb(${A.map((x, i) => Math.round(lerp(x, B[i], p))).join(",")})`;
  }

  // Content swap inside a morphing container: the old content exits BEFORE the new enters,
  // each with its own timing, so text never overlaps. Returns styles for both layers.
  function swap(t, at, { exit = 0.12, gap = 0.04, enter = 0.18, blur = 8, rise = 10 } = {}) {
    const pOut = progress(t, at - exit, exit);
    const pIn = easeOut(progress(t, at + gap, enter));
    return {
      out: { opacity: 1 - pOut, filter: `blur(${blur * pOut}px)`, y: -rise * pOut },
      in: { opacity: pIn, filter: `blur(${blur * (1 - pIn)}px)`, y: rise * (1 - pIn) },
    };
  }

  // ---- beat grid -----------------------------------------------------------------------------
  // grid from tools/beat-grid.py (-o grid.json) or { bpm, first_downbeat }.
  function beats(grid) {
    const b = grid.beat_seconds ?? 60 / grid.bpm;
    const t0 = grid.first_downbeat ?? 0;
    return { at: (n) => t0 + n * b, bar: (n, beat = 0) => t0 + (n * (grid.beats_per_bar ?? 4) + beat) * b, seconds: b };
  }

  // ---- loop ----------------------------------------------------------------------------------
  // Blend the last `tail` seconds back into the first frame so the loop is seamless
  // (position AND velocity match): value(t) for t near the end → value(t - duration) near 0.
  function loop(t, duration, fn, tail = 0.4) {
    const p = easeInOut(progress(t, duration - tail, tail));
    return p === 0 ? fn(t) : lerp(fn(t), fn(t - duration), p);
  }

  // ---- HyperFrames glue -------------------------------------------------------------------------
  // Drive a pure render(t) from the paused GSAP timeline: seeking calls onUpdate with the time.
  function bind(tl, duration, render) {
    const clock = { t: 0 };
    tl.fromTo(clock, { t: 0 }, { t: duration, duration, ease: "none", onUpdate: () => render(clock.t) }, 0);
    render(0);
    return clock;
  }

  const api = { spring, track, edges, drag, rubber, clamp, lerp, progress, easeOut, easeInOut, mixColor, swap, beats, loop, bind };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Motion = api;
})(typeof window !== "undefined" ? window : globalThis);
