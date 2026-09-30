---
name: motion-craft
description: Premium, "Dribbble-level" motion design in code — the After-Effects-replacement method. Beat-synced UI/brand motion where one element morphs continuously (never cut), a cursor drives real clicks and drags, springs are closed-form functions of time, the camera reframes each state, and the video loops seamlessly with real motion blur. Use when the user wants polished UI animation, product/app motion, logo or shape morphs, "make it look like After Effects / Dribbble / Apple", beat-synced motion to a song, seamless loops, or asks to improve motion quality of any HyperFrames/Remotion piece (including ads from /ad-creative).
---

# Motion craft

Premium motion comes from **constraints + physics + rhythm + verification**, not from effects.
This skill is the working method; the math lives in `video-studio/tools/lib/motion.js`
and the audio/render tooling in `video-studio/tools/`.

## 1. Intake — ask, then plan on the beat grid before any code

Ask (one message):
1. **The states / story beats** (8–12 for a UI morph piece; for an ad, the storyboard beats).
2. **Palette:** pure black & white, or one accent color. (Brand colors only if given.)
3. **Music:** a royalty-free track the user supplies (e.g. Mixkit / Pixabay with a commercial
   license) — BPM around 100–128 works best for UI motion. Never pick music yourself for paid ads
   without a license.
4. **Format:** 1440×1440 (loop/showcase), 1080×1920 (Reels), 1920×1080.
5. **Language of on-screen text** — Hebrew by default in this repo (`/hebrew-video`).

Then run `python3 video-studio/tools/beat-grid.py song.mp3 --bpm <hint> --bars <n> -o grid.json`
and **show the user a table: bar · beat · time · what happens** (something on every beat, the
big changes on downbeats). Get approval on that table before writing code.

## 2. Write the spec as constraints (put it at the top of the composition as a comment)

- **Continuity:** one hero element, never cut. Every state is the same element changing size,
  radius and color; content swaps inside it.
- **Canvas & type:** light warm-gray canvas (#EDEAE4-ish), black/white components, one clean UI
  font. Geist has no Hebrew → use **Heebo** (UI) or **Rubik** (rounded); one family only.
- **Physics:** springs everywhere, damping ≈ 0.85–0.9 (tiny overshoot at most, <1%).
- **Camera:** zooms/pans so each state fills the frame (scale the stage wrapper, not the text).
- **Loop:** last frame identical to the first — position *and* velocity, cursor included.
- **Banned list (write it explicitly):** bouncy easing (damping < 0.7), particle bursts, glows,
  gradients on UI chrome, mismatched icon stroke widths, dead time (a beat with nothing moving),
  stock "template" looks, random colors, more than one font family.

## 3. Architecture: every frame is a pure function of time

- One `render(t)` computes **every** style from `t`. No CSS transitions, no timers, no state
  carried between frames. Hook it to HyperFrames with `Motion.bind(tl, DURATION, render)`
  (a proxy tween whose `onUpdate` calls `render(t)` — seek-safe in preview and render).
- **Springs are closed-form step responses:** `Motion.spring(t, response, damping)`.
- **A value that changes target many times = the sum of one spring per change:**
  `Motion.track(t, [{t, v}, …])` — still a pure function of t.
- **Stretch:** two edges on different springs (leading faster than trailing):
  `Motion.edges(t, [{t, left, right}, …])` → liquid tab indicator, toggle knob, progress fill.
- **Direct manipulation:** while the cursor is held, the value comes from the cursor position;
  on release it springs back *from wherever it was*: `Motion.drag(t, {down, up, follow, rest})`.
  Past a limit use `Motion.rubber(x, min, max)` (e.g. volume slider stretching past max).
- **Text inside a morphing container** gets its own exit and enter timing (exit → tiny gap →
  enter, short blur): `Motion.swap(t, at)`. Never cross-fade two texts in the same spot.
- **Seamless loop:** wrap values in `Motion.loop(t, DURATION, fn)` so the tail blends into t=0.
- **Cursor:** a real cursor element with its own path (springs, not linear), a press state
  (scale 0.9 + darker) on clicks, and it must be at the same place and speed at t=0 and t=end.

## 4. Sound on the grid

- Start the piece on a **downbeat** (trim the song so `first_downbeat` = 0, or offset the timeline).
- UI sounds (click, pop, whoosh) are placed by their **measured peak**, not their file start:
  `python3 video-studio/tools/beat-grid.py --peak sfx/*.mp3` → `data-start = beat_time − peak`.
- Master to −14 LUFS (`tools/loudnorm.sh`), music ducked under any VO.

## 5. Verify before the full render

1. `npx hyperframes check` → 0 errors.
2. **One frame per beat:** `bash video-studio/tools/beat-frames.sh grid.json` then Read the contact
   sheet. Fix anything off the grid, cramped, clipped or hard to read (Hebrew: see `/hebrew-video`).
3. Check the first and last frame are identical (snapshot `--at 0,<duration-0.001>`).
4. Only then the full render.

## 6. Render with real motion blur

`bash video-studio/tools/motion-blur.sh out/final.mp4 60 4` renders 4 subframes per frame and
averages them (ffmpeg `tmix`). For very fast moves use `30 8` (smoother blur, 30 fps output).
For Reels delivery 30 fps is fine; 60 fps for showcase loops.

## Gotchas (each one has bitten someone)

- **Never put `will-change` on anything the camera scales** — text renders blurry. Scale a wrapper.
- Text swapping inside a morphing container without separate enter/exit timing → overlap.
- Last frame ≠ first frame (even cursor speed) → the loop stutters.
- A spring with damping < 0.7 reads as "bouncy" and cheap.
- Motion blur on thin 1px strokes smears them — use ≥ 2px strokes for moving icons.
- Timings must be computed from the beat grid (`Motion.beats(grid).at(n)`), never typed by ear.

## Prompt template (Hebrew UI morph piece)

See `references/prompt-template.md` for a ready-to-use brief in the style that produced these
results, adapted to Hebrew and to this repo's tools.
