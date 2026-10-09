---
name: video-wow-review
description: Objective review of a rendered video/animation - the 30-point "wow score" rubric (10 criteria with observable checks), the mute / freeze / 5-second / blur tests, contact-sheet and motion-strip inspection, loudness and sync checks, and a diagnose-to-fix map so the weakest layer gets fixed first. Use after rendering ANY video, when the user says a video is "not wow enough"/"flat"/"amateur", or when they can't say what's wrong (בדיקת איכות סרטון, ציון וואו, למה זה לא מרשים).
---

# Video wow review

The user often can't articulate "better". Replace taste-by-feel with observable checks. Never review from code or preview - review **rendered pixels and audio** (`motion-toolkit/assets/qa.sh video.mp4`).

## Procedure
1. `qa.sh` -> `contact.png` (8 key moments), `strip.png` (12 consecutive frames at a motion-heavy moment), `wave.png`, loudness, black/freeze report.
2. View the images (Read tool). For each scene check: hierarchy at a glance, clipping/overlap, safe zones, contrast, depth layers, last frame.
3. Run the four tests below, score the rubric, list the 3 lowest criteria, fix in that order, re-render only what changed (stills first).
4. Report: score before/after, what was verified (frames/loudness) and what was NOT (audio taste, real-device playback).

## The four tests
- **Mute test:** with the sound off, is the story still clear and the rhythm visible (motion lands on a pulse)? 
- **5-second test:** do the first 3 s give a reason to keep watching (hook) and by second 5 the value claim?
- **Freeze test:** pause on 6 random frames - is each one a designed frame (hierarchy, depth, accent colour), or an empty/slide-like one?
- **Strip test (12 frames):** is there ease (spacing differs frame to frame), overlap (parts start at different times), blur on fast moves, anything popping/teleporting?

## Rubric (0 = missing, 1 = weak, 2 = good, 3 = excellent) - total /30
| # | Criterion | Observable check |
|---|---|---|
| 1 | Hook & story | hook <= 3 s in outcome language; value by beat 2; one idea per scene; ends on a CTA/hold |
| 2 | Art direction | one named style, tokens consistent in every scene, one accent hue, tinted neutrals, no lazy-default tells |
| 3 | Composition & scale | video-scale type (hero 60-80 % width), edge-anchored zones, >= 2 focal points, >= 3 layers/scene, safe zones respected |
| 4 | Typography | extreme weight contrast, display tracking tightened, Hebrew unclipped/unflipped, readable in 2 s |
| 5 | Motion language | easing by intent (>= 3 eases), entrance variety, stagger by importance, asymmetric in/out, Build/Breathe/Resolve per scene |
| 6 | Camera & depth | real perspective/z/parallax/DoF (not scale-only), motivated moves, drift on holds, shake decays on hits |
| 7 | Light & texture | glow/bloom restrained (<= .45), animated grain, vignette, atmosphere (aurora/dust), no banding |
| 8 | Transitions | velocity-matched, direction-consistent, 1-2 hero transitions, no dead cuts to black |
| 9 | Sound & rhythm | cuts on bars, hits on beats, SFX for every impact, riser into hits, ducking, loudness ~ -14 LUFS, no clipping |
| 10 | Polish | real motion blur, no pops/glitches, final hold >= 1 s, last frame designed, file specs correct |

Bands: <= 14 amateur; 15-21 decent but template-like; 22-26 premium; 27+ standout. Default target for "wow": >= 24 with no criterion below 2.

## Diagnose -> fix map
| Symptom | Likely weak criterion | Fix |
|---|---|---|
| "Looks like slides" | 3, 6 | add layers (ghost type, glow, rules), camera push + parallax, DoF, asymmetric zones |
| "Cheap / stock-y" | 2, 7 | commit to one style; tinted palette; grain + vignette; remove default-AI tells |
| "Boring" | 1, 5 | sharper hook; vary entrances/eases; add 1 hero moment (3D flight, assemble, burst); cut scenes |
| "Chaotic / too much" | 3, 5 | fewer elements per scene, one focal point first, hold times, stagger <= 500 ms |
| "Doesn't feel connected" | 8, 9 | velocity-matched transitions; cuts on the beat; riser->hit |
| "Hebrew looks off" | 4 | word-level splits only, RTL, bundled fonts, check clipping/niqqud, islands for latin/numbers |
| "Feels laggy / jittery" | 10 | motion blur (SUB=4), no overlapping tweens, check strip for pops |
| "Sounds flat" | 9 | add cues, energy map, sidechain, whoosh/riser/hit layers, gains |
| "Ends weakly" | 1, 10 | final lock-up with hit + burst + hold >= 1.5 s, then fade |

## Review output template
```
Wow score: 23/30  (target 24+)
Strong: camera depth (3), transitions (3) ...
Weakest: Sound (1) - no riser before the CTA; Typography (1) - Hebrew subline clipped at 0:12
Fixes (in order): 1) ... 2) ... 3) ...
Verified: contact sheet, strip, loudness -14.2 LUFS, no black frames. Not verified: audio taste, phone playback.
```

See also: `motion-design-wow` (what good looks like), `motion-toolkit`, `kinetic-typography-hebrew`, `sound-design-procedural`, `verify-and-safety-gates`.
