# Technique catalog (pick >=2-3 per scene)

Recipes name the technique, the key parameters and the pitfalls. Most are implemented in `motion-toolkit` (`HF.*`); others are patterns to write with GSAP/CSS/SVG/Canvas/Three.js. Inspired by HyperFrames' rule library (Apache-2.0) and general motion-design craft.

## Text & type
| Technique | Recipe | Notes |
|---|---|---|
| Masked word reveal | words in `overflow:hidden` masks, `yPercent 118 -> 0`, rot 3 -> 0, stagger 0.07-0.15, `expo.out` 0.9 s | Hebrew: split by WORD only. Add mask padding .16em/.2em so descenders and niqqud aren't clipped |
| Beat slam | one tempo grid; each phrase slams on a beat with a *different* entrance (scale+blur, side snap, rise+rotate, drop); 0.35-0.6 s attacks; spacing 1.2-1.8 s | one accent hue on the verbs; heavy display type 150 px+; use >=3 eases |
| Kinetic center-build | statement builds word by word, final word pop with spring | for manifesto/hook beats |
| Typewriter / key ticks | `steps()` per char, caret blink square wave, key-tick cues | code/terminal/prompt UIs |
| Counter with scale growth | number scales up as it counts (`expo.out` 1.2-1.6 s) + tick cues | `tabular-nums`; ring/bar fill in sync |
| Scramble / decode | per-glyph substitution that resolves | latin/mono UI; avoid on Hebrew |
| RGB-split glitch | quantized-time jitter on 2 ghost copies (red/cyan, `screen`), amplitude decays, hard reset to clean | 0.25-0.6 s; loud/tech register only; deterministic hash, no CSS keyframes |
| Gradient/light sweep through glyphs | `background-clip:text`, move gradient 0.9-1.4 s | don't mix with per-child colours (fill is inherited) |
| Ghost type | giant theme word at 3-8 % (video: 5-12 %) opacity drifting slowly | gives emptiness a texture; tween TO the target opacity, not 1 |
| 3D extruded text | stacked offset copies fading | big display type only |
| Variable-font axis animation | animate `wght`/`opsz` over ~0.45 s | needs a bundled variable font |
| Marker highlight | hand-drawn underline/circle via SVG path draw | emphasis on one key word |

## Camera & space
| Technique | Recipe |
|---|---|
| World camera | all content in `#world`; camera state {x,y,z,rx,ry,rz,s}; single writer; drift sinusoid (14 px / 12 s) + shake on hits |
| Push-in / pull-out | scale 1.0 <-> 1.06-1.12 over 4-6 s `sine.inOut`/`power2.out` |
| Multi-phase camera | pull-back, focus, push with continuous subtle drift |
| 3D flight | `perspective` 700-1400 px on a static stage, world `preserve-3d`, dive tilt 30-55 deg (cap 65), 0.6-1.0 s legs, holds >= 0.8 s; filters/opacity on the 3D parent flatten it - blur leaf layers instead |
| Coordinate-target zoom | outer scale wrapper + inner counter-translation to zoom into off-centre targets |
| Rack focus / DoF | per-layer `--dof` blur 3-6 px per depth step (cap 8-24), dim 0.55; focal plane sharp; handoff plane-to-plane in the same window |
| Orbit / constellation | nodes on an ellipse; depth d = (sin a + 1)/2 drives scale (.74-1.04), opacity (.55-1), blur (0-5.5 px), z-order; center-outward expansion first |
| Parallax | layers drift at different factors; foreground faster |
| Ken Burns on images | scale 1 -> 1.04 over the beat + tiny translate |
| Whip pan | exit `x:-400, power3.in 0.3 s` + enter `x:+400 -> 0, power3.out 0.3-0.5 s`, blur from supersampling |

## Light, texture, atmosphere
| Technique | Recipe |
|---|---|
| Aurora/mesh background | 3-4 big radial blobs (screen blend) drifting on sin/cos; avoids linear-gradient banding |
| Bloom behind hero | radial glow, opacity .15-.30 (max .45), blooms in over 0.6-1.4 s ending at hero settle, then 2.5-4 s breathing |
| Light sweep | narrow highlight crosses a surface once; 0.8-1.6 s; peak .10-.25 |
| Grain | pre-generated noise tile re-offset per frame, `overlay`, opacity .07-.12 |
| Vignette | radial transparent 52 % -> black .5-.65 |
| Light leak / flash at cut | full-frame warm flash .35-.5 s, peak .5-.8 |
| Dust/bokeh | 30-60 soft particles drifting up, twinkling; blur on a few for depth |
| Scan lines / registration marks / hairline grids | structural texture for tech/Swiss looks |

## Data & UI
| Technique | Recipe |
|---|---|
| Ring/bar fills | SVG `stroke-dashoffset` bound to time; pair every number with a visual |
| Stat cards | glass cards with 3D tilt entry (`rotationY -26 -> 0`, `transformPerspective 1300`) staggered on beats |
| Chart scrub / race | draw chart with SVG/CSS (not chart libs), playhead moves, tooltip follows; avoid pie charts, multi-axis, 6+ panel dashboards, gridlines/legends |
| Cursor UI demo | visible cursor moves, clicks (ripple), UI reacts; camera chases the interaction |
| Prompt -> answer theater | prompt types into a real input, answer streams, result card lands |
| Agent progress theater | checklist rows check off (SVG check draw), conversation builds to confirmation |
| Panel <-> target live sync | control change and bound surface change on the same beat |
| Press/release spring | button compresses then springs back with glow/burst |
| FLIP / shared element | same subject changes box: one continuous tween |
| Path travel / stroke draw / morph | `MotionPath`, `DrawSVG`, `MorphSVG` (all free in GSAP) |
| Wires / connectors | SVG paths drawn with `draw()`, ease `power2.inOut`, with a job (route/validate/reveal) |

## Particles & punctuation
Ballistic burst (confetti chips/dots) `x = vx*t, y = vy*t + .5*g*t^2`, 12-40 particles, 0.7-1.5 s, tied to a cause (hero settle, click, lockup), fades in last 25-30 %. Never uncaused. Fixed pool built at setup; positions analytic in t. Glyph dissolve for exits (<=40 DOM particles; use canvas for per-pixel).

## Logo & brand moments
Assemble from parts (letters fly in from deterministic-random offsets, `expo.out`, stagger .045), lock with an impact + shake + burst, bloom behind, optional light sweep, then tagline mask reveal and CTA. Hold >= 1.5 s.

## Energy -> technique guide
High impact (launch/promo): beat slam, velocity transitions, counters, shake, bursts. Cinematic (tours/stories): 3D camera, DoF, SVG drawing, slow dissolves. Technical (dev tools): typewriter, canvas 2D, motion paths, cursor demos. Premium (luxury/enterprise): variable-font motion, long holds, slow velocity transitions, 0 % overshoot. Data-driven: counters, ring/bar fills, chart scrub.

## Audio-reactive (only when music-driven)
Pre-extract per-frame bands (e.g. 16 bands @ 30 fps), sample them per frame; bass -> scale pulse, treble -> glow, amplitude -> breathing; text <=3-6 % scale, glow <=30 %, backgrounds 10-30 %. Determinism: pre-extracted data only (no Web Audio at render).
