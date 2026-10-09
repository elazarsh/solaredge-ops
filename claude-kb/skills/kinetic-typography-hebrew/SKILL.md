---
name: kinetic-typography-hebrew
description: Professional kinetic typography for Hebrew (RTL) and bilingual video - word-level masked reveals, beat-synced slams, number animation, tracking and weight contrast for video encoding, font choice from bundled Hebrew families, line breaking/overflow math for a 1080 canvas, niqqud/shaping safety, mixed Hebrew-English-number islands, readability timing. Use whenever animated text appears in a video, slide animation, GIF, title card, caption or lower-third in Hebrew (טיפוגרפיה קינטית, כותרות מונפשות, עברית בוידאו).
---

# Kinetic typography for Hebrew

Typography is hierarchy in time: the first thing to move is read as most important; entry style changes meaning (0.1 s slam vs 2 s fade).

## Rules that prevent the classic Hebrew failures
1. **Split by word only.** Never animate Hebrew letter-by-letter (niqqud marks and shaping break; per-glyph reveals look broken). Arabic must never be split at all. Latin/mono text can be split per character.
2. **RTL everywhere:** `dir="rtl"` on the canvas; stagger order follows reading order (first word = rightmost); right-anchored text boxes (`right:80px`), not left. Slides/reveals should travel in the reading direction (from right) for natural flow.
3. **Islands:** wrap latin words, numbers, URLs, code in `direction:ltr` spans (`unicode-bidi:isolate`) so punctuation doesn't flip; test "Claude כבר יודע" style mixes and `%`, `₪`, `+`.
4. **Mask padding:** masks clip descenders/niqqud: `padding .16em top, .2em bottom` with equal negative margins (built into `HF.splitWords`). `line-height 1` clips; verify a *settled* frame.
5. **Width math:** Hebrew display at 128 px ~0.55-0.6 em per glyph -> ~70 px/char. A 1080 canvas with 80 px margins fits ~13 chars at 128 px, ~16 at 100 px. Break headlines manually (`<br>`), keep <= 2-3 lines of <= 14 chars for heroes. Always render a still and look.
6. **Bundled fonts only** (offline, deterministic): Heebo 400/700/900, Rubik 400/500/800/900, Secular One, Frank Ruhl Libre 400/900 (serif), Assistant 300-800, Karantina (condensed display), plus Space Grotesk / JetBrains Mono for Latin. An unbundled font silently falls back at render.

## Typography for video encoding
- Display tracking -0.03 to -0.05 em (compression eats detail); +0.01 em on dark at display sizes; dark backgrounds: body weight ~350 instead of 400, line-height +0.05-0.1.
- Weight contrast must be extreme: ~300 vs 900 (Assistant 300 / Rubik 900), not 400 vs 700. One expressive face per scene, one quiet.
- Pair across axes: serif + sans, condensed + wide, display + mono. Don't pair two similar sans.
- Sizes on a 1080-wide frame: hero 100-250 px, headline >=90 px (in-feed), body >=32 px, labels >=24 px. Nothing below 24 px without a reason. 60-80 % of frame width for the hero line.
- `font-variant-numeric: tabular-nums` for counters/stacked numbers; big counters with `direction:ltr`.
- Accent: one hue on the verbs/numbers; everything else near-white (tinted) - never pure #fff on pure #000.

## Motion vocabulary (pick a different one per phrase)
| Verb | Recipe | Feel |
|---|---|---|
| Rise from baseline | mask + `yPercent 118->0`, rot 3->0, `expo.out` .9 s, stagger .07-.15 | editorial, confident |
| Slam | scale 1.7->1 + blur 18->0, `power4.out` .5 s, on a beat, + impact cue | percussive |
| Side snap | `x:+/-420->0`, `expo.out` .45 s | hard, directional |
| Drop | `y:-160->0` + scale 1.15->1, `expo.out` | weight |
| Circ rise | `y:110, rot 5 -> 0`, `circ.out` .55 s | heavy with momentum |
| Blur-in | `filter blur(14px)->0` + `x:220`, `expo.out` .8 s | soft, premium |
| Typewriter | `steps()`, caret, key ticks | code/terminal |
| Counter | count + scale growth, `expo.out` 1.2-1.6 s, ticks | proof |
| RGB split | quantized jitter 0.25-0.6 s resolving clean | tech/loud |
| Light sweep | gradient through glyphs 0.9-1.4 s | polish on a hero word |
Rhythm: spacing between phrases 1.2-1.8 s (under 0.8 s = frantic, over 2.5 s = lost pulse); entrance 0.35-0.6 s; finale holds >= 1 s with a tiny breath (scale 1.01). Use >= 3 distinct eases; reserve overshoot for the one playful moment.

## Readability timing
Text on screen 3 s must be readable in 2: fewer words, bigger type. Hero lines hold >= 1.2 s after settle. Don't animate body copy and background at once. Captions: sync to word timestamps from the FINAL audio; animate key words, not all.

## QA checklist (stills at settle frames)
All words visible and unclipped (descenders, niqqud); line breaks intentional; no overlap with safe-zone UI (top ~220 / bottom ~300 px); contrast >= 4.5:1 with decoratives removed; numbers/latin not flipped; weights/tracking as specified; glows not boxed by masks.

See also: `motion-toolkit` (`HF.splitWords/reveal/slam/counter/type/shine/rgbSplit`), `hebrew-rtl-output`, `motion-design-wow`, `design-system-first`.
