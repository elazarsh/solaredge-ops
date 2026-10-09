---
name: code-driven-video
description: Produce explainer videos, motion-graphics b-roll, captioned/edited clips and animated ads as code (HTML + GSAP rendered to MP4 with HyperFrames/Remotion + FFmpeg + TTS + transcription). Use for any request to make, edit, caption, animate or re-format a video from a script, storyboard, screenshots or an existing talking-head recording; includes narration sync, Hebrew RTL, vertical conversion and QA (סרטון הסבר, מוטיון גרפיקס, כתוביות, אנימציה).
---

# Code-driven video

> **Want it to look stunning, not just correct?** Load `motion-design-wow` first (8-layer system), build with `motion-toolkit` (3D camera, real motion blur, procedural sound, Hebrew fonts), type with `kinetic-typography-hebrew`, and score the render with `video-wow-review`. This skill remains the reference for narrated/captioned pipelines (TTS, transcription, HyperFrames/Remotion).

The model writes the *description* of the video (script JSON, HTML, animation code); a renderer produces the MP4. Plan before building, verify the exported file, not the preview.

## Pipeline (explainer, ~1 min)

1. **Setup:** project folder; check Node, FFmpeg, renderer (e.g. `npx hyperframes check`). Install only from official docs; prove with a test file. Keys go in the terminal/env, never in prompts.
2. **Research:** one sentence for problem + audience. Collect verified facts, real screenshots, logos, 1-2 style references. Write a brief. Start from ONE process you know well (e.g. "inquiry -> booked appointment").
3. **Script as data:** JSON array of scenes: `id`, narration, on-screen text, visual directions. JSON only, no prose.
4. **Storyboard:** compare 3 concepts, pick one, save `STORYBOARD.md`: per scene time range, narration line, short on-screen text, visual action, assets. Review one frame per scene (contact sheet) - does the sequence make sense with no audio?
5. **Narration:** TTS with reliable Hebrew. Fix mispronunciation via diacritics, spelling or shorter sentences. Test a short sample first.
6. **Audio edit:** FFmpeg - trim long pauses, slightly speed up; gentler settings if cuts clip.
7. **Timestamps:** transcribe the *final* audio (Whisper etc.) to word-level start/end. Verify names, numbers, English words.
8. **HTML skeleton:** fixed-size frame = video resolution.
9. **Animation:** GSAP with a **paused timeline registered to the composition ID**; no time-based timers (not reproducible). Test by seeking to the same second repeatedly.
10. **Sync:** animate key words, not every word; tie visual actions to keywords (envelope moves when narrator says "incoming"). Captions and graphics are separate layers.
11. **Style:** one Hebrew-capable font, primary + accent colour, real screenshots, consistent across scenes.
12. **Browser QA:** play, check sync and smoothness, console errors.
13. **Render prep:** self-contained (local assets, correct paths, fonts bundled - an installed local font proves nothing).
14. **Render:** check -> preview -> render with quality flag; confirm it plays.
15. **Final QA:** watch with and without sound; timestamped notes ("0:12 text overlaps logo"); re-render only the flagged scenes.
16. **Platform adaptation:** vertical 9:16: change frame size, enlarge text, stack elements, keep narration timing. Treat as a separate layout, not a crop.

## Motion-graphics b-roll over a talking-head video

Requires: finished MP4 (simple English filename), exact SRT/VTT for that cut, Node 18+, Python 3, ffmpeg with ProRes (for transparent MOV), Playwright+Chromium, final assembly in DaVinci/Premiere.
1. Agent reads video+SRT, estimates word timing (SRT is sentence-level -> expect small manual fixes).
2. **Plan table first:** in/out time, narration line, graphic type, position, full-screen vs side panel. Never cover the speaker's face. Approve before any build.
3. Density default ~4-7 clips/min. Every animation must *explain* something; cut decoration. No invented numbers - use illustrative placeholders or supplied data.
4. Outputs: full-screen -> MP4; side panels -> ProRes-alpha MOV; plus `TIMING.md` with exact in/out; review via side-by-side compare page. Place on the timeline in the editor.
5. Fix only the failing clip: check a frame at a given second for placeholder "skeleton" lines, Hebrew font support, alpha channel.

## Ad variations (15 s, one variable)

- Fixed: duration, benefit (3-10 s), logo + CTA (10-15 s), motion rules, brand. Variable: **only the hook 0-3 s** (A question / B surprising claim / C direct problem statement).
- Copy lives in a variables file, separate from animation code -> adding a hook = adding a line.
- Spring/easing precomputed so render is identical on any machine.
- Contact sheet (frames at 2 s, 7 s, 12 s in one image) -> model reviews -> issues listed with timestamp, element, fix. A model's self-score is NOT independent QA.
- Separate 9:16 and 16:9 layouts; anchor per scene; shorten text rather than shrink.
- `manifest.json`: file name, variation id, hook, benefit, CTA, size, duration, fps; names like `A-vertical.mp4`; verify no overwrites and only the hook differs.
- Render one variant first, then the rest. Humans choose the winner by real results.

## Editing existing footage (cut + captions)

Remove silences and filler words, sync Hebrew captions to speech, place logo clear of the face, ask for a work plan first, review the localhost preview, then export. HyperFrames animates/captions existing material; it does not generate realistic footage (use a generator for that and treat it as a separate cost line).

## Troubleshooting

- **Black video:** does preview reach the target second? load errors, missing media, composition duration. Don't add arbitrary delays.
- **Reversed Hebrew:** RTL on containers; test mixed Hebrew/English/numbers.
- **Missing letters:** font lacks Hebrew or not loaded before frame capture.
- **Audio/caption drift:** compare narration version vs the version used for timestamps; fix the audio cut, don't nudge captions.
- **Cluttered scenes:** shorten text and remove secondary info before adding motion.
- **MOV black background:** probably the player; check alpha over a colour layer in an editor.
- Keep a working version before every major change.

See also: `hebrew-rtl-output`, `verify-and-safety-gates`, `video-camera-codes` (for generated footage), `ad-creative-workflow`.
