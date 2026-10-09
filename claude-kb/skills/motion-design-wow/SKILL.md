---
name: motion-design-wow
description: The system for making videos and animations that look genuinely premium ("wow") - not one effect but eight layers - concept, art direction, composition and scale, motion language (easing, timing, choreography), camera and depth, light and texture, rhythm and sound, polish and QA. Use for ANY request for a stunning/impressive/cinematic/viral/launch/promo/explainer/kinetic-typography/motion-graphics video, ad, intro, reel or animated slide; and whenever a video "isn't wow enough". Includes the amateur-tells list, the wow ladder (how ambitious to go), style archetypes, and which skills/tools to chain (וואו, סרטון מרשים, פרסומת, אנימציה, מוטיון גרפיקס).
---

# Motion design: the "wow" system

"Wow" is not a filter you add at the end. It is the sum of eight layers, each done deliberately. If a video feels flat, one or more layers are missing - diagnose with `video-wow-review`, fix the weakest layer first.

Build with `motion-toolkit` (deterministic engine, 3D camera, real motion blur, procedural sound). Type in Hebrew: `kinetic-typography-hebrew`. Sound: `sound-design-procedural`. Review: `video-wow-review`. Hebrew/RTL rules: `hebrew-rtl-output`.

## The wow stack (8 layers)

**1. Concept & story - decide before pixels**
- Hook in the first 3 s: a recognisable human situation or a promise of outcome ("why should I care"), never the product name or a feature list.
- Value claim lands by beat 2; everything after is *evidence*. Test: delete evidence beats - the value must remain; delete value beats - if the video still "works", it is only a feature tour.
- One idea per scene. 3-6 scenes for 15-45 s. Declare the rhythm up front (e.g. fast-fast-SLOW-fast-HERO-hold).
- Every key visual traces to the source (its own numbers, names, metaphors). If a prop could appear unchanged in another product's video, replace it.
- Don't overfill short videos: hook + one strong beat + CTA beats five mediocre ones.

**2. Art direction - commit to a look**
- Name the style (see `references/styles.md`), define tokens: background, foreground, ONE accent hue, optional second accent, type pair, corner radius, motion character. Same tokens in every scene.
- Light/dark by content: tech/cinema/finance -> dark; food/wellness/kids -> light. Tint neutrals toward the accent hue; avoid pure `#000`/`#fff` ("dead" grey looks undesigned).
- Avoid the lazy AI defaults unless deliberate: gradient text everywhere, left-edge accent stripes on cards, cyan-on-dark/purple-blue gradients, identical same-size card grids, everything centred with equal weight, overused fonts.

**3. Composition & scale - video is not a web page**
- Scale up from web: headlines 64-120 px (1080-wide frame: 100-250 px for hero Hebrew), body 28-42 px, labels >=24 px, borders 2-4 px, padding 60-140 px, decorative opacity 12-25 % (below 10 % is invisible after compression).
- Hero text spans 60-80 % of frame width; anchor to edges and use zones (split frames, metadata bars) rather than floating centred stacks.
- >=2 focal points; >=3 depth layers per scene: background (glow, ghost type, grain, grid), midground (the message), foreground accents (rules, labels, data bars, particles). 6-10 visual roles for produced marketing frames.
- Structural rules/dividers that animate (`scaleX 0->1`, SVG draw) create visual paths. Every connector line needs a start anchor, an end anchor and a job - else cut it.
- Safe zones for vertical social: keep key content out of top ~220 px and bottom ~300 px (platform UI).
- Muted is fine; flat is not: each scene needs at least one colour that pulls the eye. On dark canvases avoid full-screen *linear* gradients (banding under H.264): use radial gradients or solid + localised glow.

**4. Motion language - the verb and the adverb**
- The transition is the verb; the easing is the adverb (slide-in: `expo.out` = confident, `sine.inOut` = dreamy, `elastic.out` = playful).
- Ease by intent: entrance `.out` (default `power3.out`/`power4.out`/`expo.out`), exit `.in`, reposition `.inOut`, camera `circ`/`sine.inOut`, ambient `sine`, typing/ticks `steps()`, linear (`none`) only for loops/constant-speed paths. Overshoot (`back`, `elastic`) only on playful beats; premium = 0 % overshoot, playful <=10 %.
- Durations: fast 0.15-0.3 s (energy), medium 0.3-0.5 s (professional default), slow 0.5-0.8 s (gravity/luxury), very slow 0.8-2.0 s (cinematic). Entrances longer than exits (0.4 vs 0.25 s). The slowest scene >= 3x the fastest.
- Scene shape: Build (0-30 %: staggered entrances) -> Breathe (30-70 %: content visible, ONE ambient motion) -> Resolve (70-100 %: exit/decisive end).
- Choreography: stagger by importance not DOM order; overlap entries; total stagger <= ~500 ms regardless of count; a different stagger rhythm per scene; vary entrance direction (left, right, scale, opacity-only, letter-spacing) - never the same `y:30, opacity:0` everywhere; >=3 different eases per composition; first animation offset 0.1-0.3 s (never at t=0).
- Anticipation only when it clarifies cause/direction; follow-through/secondary motion (label settles late, shadow lags) for physicality; three layers of motion: primary (hero), secondary (reactions), ambient (life).
- **Velocity-matched transitions:** exit with accelerating ease + blur ramp, enter with decelerating ease + blur clearing; fastest points meet at the cut (match within ~5 %). Crossfade = "this continues", hard cut = disruption, slow dissolve = "drift with me". Use 1-2 "shader-grade" transitions per 5-7 beats; more flattens them.
- Subtle motion reads as static at 30 fps - err toward more movement; every decorative element gets ambient motion (breathe/drift/pulse), a different pattern per scene.

**5. Camera & depth - sell space**
- Put everything in a world and move a camera: push-in (focus), pull-back/zoom-out reveal (context), orbit (multi-angle), tilt/pedestal (ritual reveal), whip (transition). Slow constant drift even on holds.
- Scale alone is fake depth. Real depth = perspective + z travel + layer order/occlusion + parallax + **depth of field** (blur & dim off-focus layers; rack focus between planes; keep the focal plane sharp; blur per depth step 3-6 px, cap 8-24 px).
- Camera moves must be motivated (reveal, emphasis, connection). Impact -> short decaying shake (6-30 px, 0.3-0.7 s). Hold >= 0.8 s between legs; final landing hold >= 1 s.
- Image/UI treatments: perspective tilt, Ken Burns (scale 1->1.04 over the beat), device frame, floating UI at different z, scroll reveal within a clipped window.

**6. Light & texture - make it feel photographed**
- Glow/bloom behind heroes (accent-tinted radial, opacity 0.15-0.30, max 0.45), blooming in as the hero settles then breathing; traveling light sweeps (one pass, off-screen to off-screen).
- Film grain (subtle, re-seeded per frame - static grain looks like a filter), soft vignette, light leaks/flashes on cuts, optional halation. Chromatic aberration/RGB-split only as a short accent that resolves to clean.
- Restraint wins: bloom only on real highlights; grain subtle; one or two controlled light sources. Overdone bloom washes out shapes.

**7. Rhythm & sound - half the perceived quality**
- Pick a BPM, place scene boundaries on bars and hits on beats. Visual impacts get a sound (slam = boom + crack, transitions = whoosh peaking mid-move, counters = ticks, typing = key ticks, reveals = shimmer/pop). Risers end exactly on the hit frame. Sidechain/pump the music under hits. Leave a beat of silence before the biggest hit.
- Audio-reactive visuals (if used): text/logo scale <= 3-6 %, glow <= 30 %, backgrounds 10-30 %; never equalizer bars, strobing, rainbow cycling.
- See `sound-design-procedural`.

**8. Polish & QA**
- Real motion blur (180-degree shutter via temporal supersampling) - the single biggest "this is rendered, not slideshow" fix.
- Check contact sheet + motion strips + contrast + safe zones + final hold + last frame; loudness ~ -14 LUFS for social. Never judge from the preview alone. Use `video-wow-review`.

## Amateur tells (check against every draft)
Default/linear easing everywhere; no motion blur on fast moves; everything starts and stops together; the same entrance for every element; no depth (flat layers, scale-only "zoom"); static or too-subtle backgrounds; web-sized type; low contrast / thin type on dark; too much text per scene (3 s of screen time must be readable in 2); everything animated (no hierarchy); constant speed; centered floating stacks; one effect used 20 times; hard-edged glows (mask clipping boxes); silence or generic stock music with no hits; cut/hit not on the beat; no final hold.

## The wow ladder (choose how far to go)
| Level | Adds | Typical use |
|---|---|---|
| 1 Clean | style tokens, masked word reveals, proper easing, bg glow | internal clip, quick social |
| 2 Polished | + counters/rings, staggered cards, transitions, grain/vignette | product explainers |
| 3 Cinematic | + 3D camera, DoF, parallax, particles, shake, real motion blur | launch/promo ads |
| 4 Signature | + custom shader/3D (Three.js), audio-reactive details, bespoke hero moment | brand reels, keynotes |
Default to level 3 when the user says "wow".

## Process
1. Brief: audience, one-sentence message, duration, format (9:16 / 16:9), tone, brand tokens, assets, language/direction.
2. Strategy line + beat list: "This video tells [audience] that [message]." Table: beat, time, on-screen, why (traceable to message). Pick BPM and rhythm pattern.
3. Style archetype + tokens (`references/styles.md`).
4. Choose techniques per beat from `references/techniques.md` and scene patterns from `references/blueprints.md` (>=2-3 techniques per scene, >=3 eases per piece).
5. Build with `motion-toolkit`; render stills at key times first -> fix layout; then full render.
6. Review with `video-wow-review` (score, fix the lowest layer, re-render only what changed).
7. Report honestly: what was verified (frames, loudness) and what was not (e.g. subjective audio taste).

## Related skills to chain
`design-system-first` (brand tokens), `kinetic-typography-hebrew`, `motion-toolkit`, `sound-design-procedural`, `video-wow-review`, `code-driven-video` (narrated/captioned pipelines), `video-camera-codes` (AI-generated footage), `ai-influencer-ugc-video`, `community-skills-guide` (HyperFrames, Remotion, GSAP, Three.js skills to install).
