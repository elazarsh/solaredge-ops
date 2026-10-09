/*  motion-toolkit engine  -  deterministic, seekable, no wall-clock.
 *  Contract: every visual is a pure function of time t (seconds) so the renderer can seek to any t
 *  (and to sub-frames for real motion blur) and get the same pixels.
 *  - GSAP timeline (HF.tl, paused) drives DOM entrances.  Use fromTo() only.
 *  - HF.bind / updaters drive continuous effects as pure functions of t.
 *  - Never use Date.now / performance.now / Math.random / CSS animations / timers.
 */
(() => {
  const HF = (window.HF = {});
  const $ = (s, r = document) => (typeof s === 'string' ? r.querySelector(s) : s);
  const $$ = (s, r = document) => Array.from(typeof s === 'string' ? r.querySelectorAll(s) : s);
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  HF.$ = $; HF.$$ = $$; HF.clamp = clamp;
  HF.lerp = (a, b, t) => a + (b - a) * t;
  HF.map = (x, a, b, c, d) => c + (d - c) * clamp((x - a) / (b - a));
  HF.hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  HF.cfg = { w: 1080, h: 1920, fps: 30, duration: 30, bpm: 120 };
  HF.cues = []; HF.updaters = []; HF.post = []; HF.scenes = [];
  HF.beat = (n) => (n * 60) / HF.cfg.bpm;           // time of beat n
  HF.bar = (n) => HF.beat(n * 4);                    // time of bar n (4/4)
  HF.cue = (t, type, o = {}) => { HF.cues.push(Object.assign({ t, type }, o)); };
  HF.ease = (name) => (typeof name === 'function' ? name : gsap.parseEase(name || 'power3.out'));

  // ---------- base css ----------
  const css = document.createElement('style');
  css.textContent = `
  .hf-m{display:inline-block;overflow:hidden;vertical-align:top;padding:.16em .08em .2em;margin:-.16em -.08em -.2em}
  .hf-i{display:inline-block;will-change:transform}
  .hf-caret{display:inline-block;width:.09em;height:.9em;background:currentColor;vertical-align:-.08em;margin-inline-start:.08em}
  .hf-fixed{position:absolute;inset:0;pointer-events:none}
  `;
  document.head.appendChild(css);

  // ---------- init / seek ----------
  HF.init = (o = {}) => { Object.assign(HF.cfg, o); HF.tl = gsap.timeline({ paused: true }); return HF; };
  HF.scene = (el, show0, show1) => { el = $(el); HF.scenes.push({ el, show0, show1 }); return el; };
  HF.bind = (at, dur, ease, cb) => { const e = HF.ease(ease || 'power3.out'); HF.updaters.push((t) => cb(e(clamp((t - at) / dur)), clamp((t - at) / dur), t)); };
  HF.seek = (t, frame = Math.floor(t * HF.cfg.fps)) => {
    HF.tl.time(t, false);
    for (const s of HF.scenes) s.el.style.display = t >= s.show0 && t < s.show1 ? '' : 'none';
    for (const u of HF.updaters) u(t, frame);
    for (const u of HF.post) u(t, frame);
  };
  window.__seek = (t, f) => HF.seek(t, f);
  window.__cues = () => HF.cues;

  // ---------- text ----------
  // Split into words wrapped in overflow masks (rise-from-baseline reveals). Words only: never split Hebrew by letter
  // (niqqud/shaping) and never split Arabic. Inline child elements (e.g. <span class=acc>) are preserved.
  HF.splitWords = (el) => {
    el = $(el); const out = [];
    const walk = (node, parent) => {
      node.childNodes.forEach((c) => {
        if (c.nodeType === 3) {
          const parts = c.textContent.split(/(\s+)/);
          parts.forEach((p) => {
            if (!p) return;
            if (/^\s+$/.test(p)) { parent.appendChild(document.createTextNode(' ')); return; }
            const m = document.createElement('span'); m.className = 'hf-m';
            const i = document.createElement('span'); i.className = 'hf-i'; i.textContent = p;
            m.appendChild(i); parent.appendChild(m); out.push(i);
          });
        } else if (c.nodeType === 1) {
          if (c.tagName === 'BR') { parent.appendChild(c.cloneNode()); return; }
          const shell = c.cloneNode(false); parent.appendChild(shell); walk(c, shell);
        }
      });
    };
    const frag = el.cloneNode(false); walk(el, frag);
    el.innerHTML = ''; while (frag.firstChild) el.appendChild(frag.firstChild);
    return out;
  };
  HF.reveal = (words, at, o = {}) => {
    const { stagger = 0.07, dur = 0.95, ease = 'expo.out', y = 118, rot = 3, from = 'start', blur = 0 } = o;
    const from_ = { yPercent: y, rotation: rot, opacity: 0 }, to_ = { yPercent: 0, rotation: 0, opacity: 1, duration: dur, ease, stagger: { each: stagger, from } };
    if (blur) { from_.filter = `blur(${blur}px)`; to_.filter = 'blur(0px)'; }
    return HF.tl.fromTo(words, from_, to_, at);
  };
  // Beat-synced slam entrance. kinds: scale | side | rise | drop
  HF.slam = (el, at, kind = 'scale', o = {}) => {
    const d = o.dur ?? 0.55, k = { scale: [{ scale: 1.7, opacity: 0, filter: 'blur(18px)' }, { scale: 1, opacity: 1, filter: 'blur(0px)', ease: 'power4.out' }],
      side: [{ x: (o.dx ?? -420), opacity: 0 }, { x: 0, opacity: 1, ease: 'expo.out' }],
      rise: [{ y: 110, rotation: 5, opacity: 0 }, { y: 0, rotation: 0, opacity: 1, ease: 'circ.out' }],
      drop: [{ y: -160, opacity: 0, scale: 1.15 }, { y: 0, opacity: 1, scale: 1, ease: 'expo.out' }] }[kind];
    HF.tl.fromTo(el, k[0], Object.assign({ duration: d }, k[1]), at);
    if (o.cue !== false) HF.cue(at, 'slam', { power: o.power ?? 0.8 });
  };
  HF.counter = (el, { to, at, dur = 1.4, from = 0, fmt = (v) => Math.round(v), ease = 'expo.out', suffix = '', ticks = 0 } = {}) => {
    el = $(el);
    HF.bind(at, dur, ease, (e, p, t) => { el.textContent = fmt(from + (to - from) * e) + suffix; el.style.opacity = t < at ? 0 : 1; });
    for (let i = 0; i < ticks; i++) HF.cue(at + (dur * 0.8 * i) / Math.max(1, ticks - 1), 'tick', { pitch: 0.8 + 0.5 * (i / ticks) });
  };
  HF.type = (el, text, at, dur, o = {}) => {
    el = $(el);
    HF.bind(at, dur, 'none', (e, p, t) => {
      const n = Math.floor(p * text.length); const caret = o.caret === false ? '' : (Math.floor(t * 2) % 2 === 0 || p < 1 ? '<span class="hf-caret"></span>' : '');
      el.innerHTML = (t < at ? '' : text.slice(0, n)) + (t < at ? '' : caret);
    });
    if (o.cues) for (let i = 0; i < text.length; i++) HF.cue(at + (dur * i) / text.length, 'key');
  };
  // Moving highlight through glyphs (background-clip). Set base/hi colors via o.
  HF.shine = (el, at, dur, o = {}) => {
    el = $(el); const base = o.base ?? '#fff', hi = o.hi ?? '#ffd9a8';
    el.style.cssText += `;background-image:linear-gradient(105deg,${base} 38%,${hi} 50%,${base} 62%);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;`;
    HF.bind(at, dur, o.ease ?? 'power2.inOut', (e) => { el.style.backgroundPosition = `${(1 - e) * 100}% 50%`; });
  };
  // RGB-split glitch (quantized time, deterministic). Apply to an UN-split element.
  HF.rgbSplit = (el, at, dur, o = {}) => {
    el = $(el); el.style.position = el.style.position || 'relative';
    const mk = (color) => { const g = document.createElement('span'); g.setAttribute('aria-hidden', 'true'); g.innerHTML = el.innerHTML;
      g.style.cssText = `position:absolute;inset:0;color:${color};mix-blend-mode:screen;pointer-events:none;opacity:0;`; el.appendChild(g); return g; };
    const a = mk(o.a ?? '#ff3b5c'), b = mk(o.b ?? '#2ee6ff'); const max = o.max ?? 14, step = 1 / 20;
    HF.bind(at, dur, 'power3.in', (e, p, t) => {
      const amp = t < at || t > at + dur ? 0 : 1 - e, q = Math.floor(t / step);
      a.style.opacity = b.style.opacity = amp > 0 ? 0.85 : 0;
      a.style.transform = `translate(${(HF.hash(q * 13) * 2 - 1) * max * amp}px,${(HF.hash(q * 29) * 2 - 1) * max * 0.35 * amp}px)`;
      b.style.transform = `translate(${(HF.hash(q * 17 + 5) * 2 - 1) * max * amp}px,${(HF.hash(q * 31 + 3) * 2 - 1) * max * 0.35 * amp}px)`;
    });
    HF.cue(at, 'glitch', { dur });
  };

  // ---------- svg ----------
  HF.draw = (path, at, dur, ease = 'power2.out') => { path = $(path); const L = path.getTotalLength(); path.style.strokeDasharray = L;
    HF.bind(at, dur, ease, (e) => { path.style.strokeDashoffset = L * (1 - e); }); };

  // ---------- camera rig (3D, with drift + shake) ----------
  HF.camera = (world, o = {}) => {
    world = $(world); const cam = { x: 0, y: 0, z: 0, rx: 0, ry: 0, rz: 0, s: 1 }; const shakes = [];
    const dr = Object.assign({ ax: 16, ay: 12, az: 0.35, period: 11 }, o.drift || {});
    cam.shake = (at, { amp = 16, dur = 0.5 } = {}) => shakes.push({ at, amp, dur });
    HF.post.push((t) => {
      const w = (2 * Math.PI) / dr.period; let sx = 0, sy = 0, sr = 0;
      for (const s of shakes) { const p = (t - s.at) / s.dur; if (p >= 0 && p < 1) { const d = Math.pow(1 - p, 2.2) * s.amp; sx += Math.sin(t * 71 + s.at) * d; sy += Math.sin(t * 89 + s.at * 3) * d * 0.7; sr += Math.sin(t * 53) * d * 0.02; } }
      world.style.transform = `translate3d(${cam.x + Math.sin(t * w) * dr.ax + sx}px,${cam.y + Math.cos(t * w * 0.8) * dr.ay + sy}px,${cam.z}px) rotateX(${cam.rx}deg) rotateY(${cam.ry}deg) rotateZ(${cam.rz + Math.sin(t * w * 0.6) * dr.az + sr}deg) scale(${cam.s})`;
    });
    return cam;
  };
  // Tween the camera state with GSAP (use fromTo for the first leg of a shot).
  HF.camTo = (cam, to, at, dur, ease = 'power3.inOut', from) => HF.tl.fromTo(cam, from || Object.assign({}, cam), Object.assign({ duration: dur, ease, immediateRender: !!from }, to), at);
  // Depth of field: blur radius from each layer's distance to the focus plane. layers: [{el, z}] focus: number or fn(t)
  HF.dof = (layers, focus, { perPx = 0.012, max = 14 } = {}) => HF.post.push((t) => {
    const f = typeof focus === 'function' ? focus(t) : focus;
    layers.forEach((l) => { l.el.style.filter = `blur(${Math.min(max, Math.abs(l.z - f) * perPx).toFixed(2)}px)`; });
  });

  // ---------- atmosphere ----------
  // Moving color blobs (cheap radial gradients, no blur filters). blobs: [{c,x,y,r,sx,sy,ph,a}] positions in px on the stage.
  HF.aurora = (el, blobs) => { el = $(el); const nodes = blobs.map((b) => { const d = document.createElement('div');
      d.style.cssText = `position:absolute;left:0;top:0;width:${b.r * 2}px;height:${b.r * 2}px;border-radius:50%;background:radial-gradient(circle,${b.c} 0%,transparent 68%);mix-blend-mode:${b.blend || 'screen'};opacity:${b.a ?? 0.6};will-change:transform;`;
      el.appendChild(d); return d; });
    HF.updaters.push((t) => nodes.forEach((d, i) => { const b = blobs[i]; const w = (2 * Math.PI) / (b.period || 14);
      d.style.transform = `translate(${b.x - b.r + Math.sin(t * w + (b.ph || 0)) * (b.sx || 180)}px,${b.y - b.r + Math.cos(t * w * 0.83 + (b.ph || 0)) * (b.sy || 220)}px) scale(${1 + Math.sin(t * w * 1.3 + i) * 0.12})`; })); };
  // Floating bokeh/dust for depth. Drifts upward, wraps, twinkles. Pure function of t.
  HF.dust = (el, { n = 40, seed = 3, colors = ['#fff'], size = [3, 14], speed = [8, 40], alpha = [0.15, 0.6], w = HF.cfg.w, h = HF.cfg.h, blur = 0 } = {}) => {
    el = $(el); const ps = [];
    for (let i = 0; i < n; i++) { const d = document.createElement('div'); const s = size[0] + HF.hash(i * 5 + seed) * (size[1] - size[0]);
      d.style.cssText = `position:absolute;left:0;top:0;width:${s}px;height:${s}px;border-radius:50%;background:${colors[i % colors.length]};will-change:transform,opacity;${blur ? `filter:blur(${blur * HF.hash(i * 3 + seed)}px);` : ''}`;
      el.appendChild(d); ps.push({ d, s, x: HF.hash(i * 7 + seed) * w, y: HF.hash(i * 11 + seed) * h, v: speed[0] + HF.hash(i * 13 + seed) * (speed[1] - speed[0]), a: alpha[0] + HF.hash(i * 17 + seed) * (alpha[1] - alpha[0]), ph: HF.hash(i * 19) * 6.28 }); }
    HF.updaters.push((t) => ps.forEach((p) => { const y = (((p.y - p.v * t) % h) + h) % h; p.d.style.transform = `translate(${p.x + Math.sin(t * 0.4 + p.ph) * 18}px,${y}px)`; p.d.style.opacity = p.a * (0.55 + 0.45 * Math.sin(t * 1.3 + p.ph)); })); };
  HF.vignette = (strength = 0.55) => { const v = document.createElement('div'); v.className = 'hf-fixed'; v.style.zIndex = 9000;
    v.style.background = `radial-gradient(ellipse at 50% 46%,transparent 52%,rgba(0,0,0,${strength}) 100%)`; document.body.appendChild(v); return v; };
  // Film grain from a pre-generated noise tile, re-positioned per FRAME (not per sub-frame, so motion-blur averaging keeps it).
  HF.grain = ({ opacity = 0.09, tile = 256, blend = 'overlay' } = {}) => {
    const t = document.createElement('canvas'); t.width = t.height = tile; const tc = t.getContext('2d'); const id = tc.createImageData(tile, tile);
    for (let i = 0; i < tile * tile; i++) { const v = Math.floor(HF.hash(i * 0.731) * 255); id.data[i * 4] = id.data[i * 4 + 1] = id.data[i * 4 + 2] = v; id.data[i * 4 + 3] = 255; } tc.putImageData(id, 0, 0);
    const c = document.createElement('canvas'); c.width = HF.cfg.w; c.height = HF.cfg.h; c.className = 'hf-fixed'; c.style.cssText += `;z-index:9500;mix-blend-mode:${blend};opacity:${opacity}`; document.body.appendChild(c);
    const g = c.getContext('2d'); const pat = g.createPattern(t, 'repeat'); let last = -1;
    HF.post.push((tm, f) => { if (f === last) return; last = f; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, c.width, c.height);
      g.translate(Math.floor(HF.hash(f * 3.1) * tile), Math.floor(HF.hash(f * 5.7) * tile)); g.fillStyle = pat; g.fillRect(-tile, -tile, c.width + 2 * tile, c.height + 2 * tile); });
    return c; };
  // Full-frame flash / light leak at a cut.
  HF.flash = (at, { dur = 0.4, color = '#fff', peak = 0.8 } = {}) => { const f = document.createElement('div'); f.className = 'hf-fixed'; f.style.cssText += `;z-index:8000;background:${color};opacity:0`; document.body.appendChild(f);
    HF.tl.fromTo(f, { opacity: 0 }, { opacity: peak, duration: dur * 0.25, ease: 'power2.in' }, at).to(f, { opacity: 0, duration: dur * 0.75, ease: 'power2.out' }, at + dur * 0.25); };
  // One-shot ballistic burst (confetti/dots/sparks). Positions are analytic in t.
  HF.burst = (el, { at, n = 28, colors = ['#fff'], speed = [300, 900], gravity = 1300, dur = 1.3, size = [6, 14], cone = Math.PI * 2, angle = -Math.PI / 2, seed = 1, x = 0, y = 0, spin = 540, shape = 'chip' } = {}) => {
    el = $(el); const ps = [];
    for (let i = 0; i < n; i++) { const d = document.createElement('div'); const s = size[0] + HF.hash(i * 3 + seed) * (size[1] - size[0]);
      d.style.cssText = `position:absolute;left:0;top:0;width:${s}px;height:${shape === 'chip' ? s * 0.65 : s}px;background:${colors[i % colors.length]};border-radius:${shape === 'chip' ? 2 : 50}%;opacity:0;will-change:transform,opacity;`;
      el.appendChild(d); const a = angle + (HF.hash(i * 5 + seed) * 2 - 1) * (cone / 2), v = speed[0] + HF.hash(i * 7 + seed) * (speed[1] - speed[0]);
      ps.push({ d, vx: Math.cos(a) * v, vy: Math.sin(a) * v, sp: (HF.hash(i * 11 + seed) * 2 - 1) * spin }); }
    HF.updaters.push((t) => { const tt = t - at; ps.forEach((p) => { if (tt < 0 || tt > dur) { p.d.style.opacity = 0; return; }
      p.d.style.transform = `translate(${x + p.vx * tt}px,${y + p.vy * tt + 0.5 * gravity * tt * tt}px) rotate(${p.sp * tt}deg)`; p.d.style.opacity = Math.min(1, (dur - tt) / (dur * 0.3)); }); });
    HF.cue(at, 'pop', { power: 0.7 });
  };

  // ---------- transitions (velocity-matched: exits accelerate, entrances decelerate; blur comes from supersampling) ----------
  HF.whip = (out, inn, at, { dir = 1, dur = 0.6, skew = 8 } = {}) => {
    const W = HF.cfg.w;
    HF.tl.fromTo(out, { x: 0, skewX: 0 }, { x: -dir * W * 1.05, skewX: dir * skew, duration: dur * 0.5, ease: 'power3.in' }, at);
    HF.tl.fromTo(inn, { x: dir * W * 1.05, skewX: -dir * skew }, { x: 0, skewX: 0, duration: dur * 0.75, ease: 'power3.out' }, at + dur * 0.28);
    HF.cue(at, 'whoosh', { dur: dur, dir });
  };
  HF.zoomThrough = (out, inn, at, { dur = 0.7 } = {}) => {
    HF.tl.fromTo(out, { scale: 1, opacity: 1 }, { scale: 1.9, opacity: 0, duration: dur * 0.5, ease: 'power3.in' }, at);
    HF.tl.fromTo(inn, { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: dur * 0.8, ease: 'expo.out' }, at + dur * 0.3);
    HF.cue(at, 'whoosh', { dur, dir: 0 });
  };
  HF.risePush = (out, inn, at, { dur = 0.7 } = {}) => {
    const H = HF.cfg.h;
    HF.tl.fromTo(out, { y: 0 }, { y: -H * 0.6, opacity: 0, duration: dur * 0.5, ease: 'power3.in' }, at);
    HF.tl.fromTo(inn, { y: H * 0.5, opacity: 0 }, { y: 0, opacity: 1, duration: dur * 0.85, ease: 'power3.out' }, at + dur * 0.25);
    HF.cue(at, 'whoosh', { dur, dir: 2 });
  };
  // Seeking the first frame after build.
  HF.ready = async () => { if (document.fonts && document.fonts.ready) await document.fonts.ready; HF.seek(0, 0); window.__ready = true; };
})();
