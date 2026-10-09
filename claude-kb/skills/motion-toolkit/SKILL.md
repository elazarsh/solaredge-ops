---
name: motion-toolkit
description: Ready-to-run toolkit for building premium animated videos as code - a deterministic seekable HTML/GSAP engine (HF.*) with masked text reveals, beat slams, counters, 3D camera with drift/shake, depth of field, orbit layouts, particles, glitch, aurora/dust/grain/vignette, velocity-matched transitions; a parallel renderer with REAL motion blur (temporal supersampling); a procedural sound-design engine (cue-driven SFX + beat-locked music); one-command build to MP4 with Hebrew fonts bundled. Use whenever you must actually produce a stunning animated video/ad/explainer/reel/intro (not just plan it), at 9:16 or 16:9, in Hebrew or English (בניית סרטון אנימציה, רינדור, מוטיון בלר, סאונד).
---

# motion-toolkit

Location after install: `~/.claude/skills/motion-toolkit/assets/` (also in the repo at `claude-kb/skills/motion-toolkit/assets/`). A complete reference composition is in `assets/examples/launch-ad.html` (30 s, 9:16, Hebrew, 6 scenes). Design thinking lives in `motion-design-wow`; QA in `video-wow-review`; Hebrew type in `kinetic-typography-hebrew`; audio theory in `sound-design-procedural`.

## Quick start
```bash
mkdir my-video && cd my-video
cp ~/.claude/skills/motion-toolkit/assets/examples/launch-ad.html index.html   # start from the reference, then rewrite scenes
DURATION=32 BPM=120 ENERGY="0:0.2,2.5:0.45,4:0.75,10:0.95,28:0.75" \
  ~/.claude/skills/motion-toolkit/assets/build.sh . index.html video.mp4
```
`build.sh` = `setup.sh` (npm: gsap + bundled Hebrew/Latin fonts, pinned Playwright 1.56.1 - it uses the preinstalled Chromium; never run `playwright install`) -> `render.js` (parallel workers, sub-frames) -> `sfx.py` (cues + music) -> ffmpeg (tmix blend = motion blur, x264 crf 16 + AAC).
Env: `FPS=30 DURATION W=1080 H=1920 SUB=4 SHUTTER=0.5 WORKERS=4 BPM ENERGY KEY`. Speed: ~2.5 sub-frames/s on 4 cores at 1080x1920 (32 s x SUB=4 ~ 25 min). Use `SUB=2` for drafts, `SUB=4` for finals. Run long builds in the background and monitor.

QA stills first (seconds, no blur): `node render.js index.html .qa --only 1.2,4.5,9,15` (set `PLAYWRIGHT_MODULE=$PWD/.deps/node_modules/playwright`), then contact-sheet them and fix layout BEFORE the full render. Final QA: `qa.sh video.mp4`.

## Composition contract (determinism)
- Page loads `vendor/fonts.css`, `vendor/gsap.min.js`, `vendor/engine.js`; calls `HF.init({fps,duration,bpm})`, builds timelines, ends with `HF.ready()`.
- Every visual is a **pure function of time**. Entrances: `HF.tl.fromTo(...)` only. Continuous effects: `HF.bind(at,dur,ease,cb)` / `HF.updaters.push(t=>...)` / `HF.post.push(...)`.
- FORBIDDEN: `Date.now`, `performance.now`, `Math.random` (use `HF.hash(n)`), CSS animations/transitions, timers, `requestAnimationFrame`, hover/scroll triggers, infinite repeats, iframes (don't seek), async DOM creation after `HF.ready()`.
- Prefer `fromTo()` over `from()`; no two tweens on the same property of one element at the same time (combine or use parent/child); never tween `top/left/width/height` (use `x,y,scale`), use `autoAlpha`/`opacity`.
- Fonts: use bundled families only (Heebo, Rubik, Secular One, Frank Ruhl Libre, Assistant, Karantina, Space Grotesk, JetBrains Mono); a locally installed font proves nothing about the render.
- Scenes: `HF.scene(el, show0, show1)` windows overlap at transitions; position everything absolutely on the 1080x1920 (or your size) canvas.

## API cheat sheet (`engine.js`)
| Group | Functions |
|---|---|
| Time | `HF.beat(n)`, `HF.bar(n)`, `HF.cue(t,type,opts)`, `HF.hash(n)`, `HF.ease(name)` |
| Text | `HF.splitWords(el)` -> word spans in masks; `HF.reveal(words,at,{stagger,dur,ease,y,rot,blur})`; `HF.slam(el,at,'scale'|'side'|'rise'|'drop',{dur,dx,power})`; `HF.counter(el,{to,at,dur,suffix,ticks,fmt})`; `HF.type(el,text,at,dur,{cues})`; `HF.shine(el,at,dur,{base,hi})`; `HF.rgbSplit(el,at,dur,{max})` |
| SVG | `HF.draw(path,at,dur,ease)` |
| Camera | `cam=HF.camera('#world',{drift})`; `HF.camTo(cam,to,at,dur,ease,from)`; `cam.shake(at,{amp,dur})`; `HF.dof(layers,focus)` |
| Atmosphere | `HF.aurora(el,blobs)`, `HF.dust(el,opts)`, `HF.vignette(strength)`, `HF.grain({opacity})`, `HF.flash(at,{dur,peak,color})`, `HF.burst(el,{at,n,colors,...})` |
| Transitions | `HF.whip(out,in,at,{dir,dur})`, `HF.zoomThrough`, `HF.risePush` (each also emits a whoosh cue) |
| Binding | `HF.bind(at,dur,ease,cb(e,p,t))` - e = eased progress |

Recipes used in the reference ad: orbit/constellation with depth-driven scale/blur/z-order (custom updater), ring fills via `stroke-dashoffset`, glass cards with 3D tilt entry, prompt typing + SVG wires + chips, logo assemble from deterministic-random offsets + burst + bloom, beat-pulsed background.

## Writing a new video
1. Strategy + beat list + style tokens (`motion-design-wow`). Pick BPM; scene boundaries on bars (`HF.bar`); hits on beats.
2. Copy `examples/launch-ad.html`; replace content; keep the structure: global atmosphere -> scenes -> camera legs -> per-scene blocks -> transitions at bar-0.35 s -> end fade.
3. Add a cue for every visible impact (slam/pop/tick/whoosh/riser/hit); set `ENERGY` so the music builds with the story.
4. Stills QA -> fix -> full build -> `qa.sh` -> `video-wow-review` score -> iterate the weakest layer.

## Gotchas learned the hard way
- Huge ghost text: tween opacity TO its target (e.g. .05), not to 1.
- `text-shadow` glow on masked words shows a clipped rectangle: glow only unmasked elements (or use a bloom div behind).
- Hebrew headlines are wide: 20 chars at 128 px overflow a 1080 canvas - break lines manually and test stills.
- `-webkit-text-fill-color: transparent` (shine) is inherited by children: don't use on parents with coloured spans.
- Filters/opacity on a `preserve-3d` parent flatten children; blur leaf layers.
- Playwright version must match the preinstalled browser (pinned 1.56.1); set `CHROMIUM_PATH` to override.
- Full-screen blend modes (screen/overlay) are expensive in software rendering; keep blobs few and use `SUB=2` for drafts.
- Grain re-seeds per FRAME (not sub-frame) so motion-blur averaging doesn't erase it.
- A CPU-bound render can starve other tasks: run it in the background, don't launch heavy work in parallel.

## Alternatives / complements
HyperFrames (HTML->MP4 CLI, 20 skills, shader transitions, captions, TTS) and Remotion (React) are heavier frameworks - see `community-skills-guide`. Use this toolkit when you need a dependency-light, Hebrew-ready, motion-blurred, sound-designed result immediately; use those when you need their catalogs (shader transitions, captions pipeline, studio preview).
