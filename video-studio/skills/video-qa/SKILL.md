---
name: video-qa
description: Review a video like a professional editor before the user sees it - contact sheets at 6 fps with timecodes, a full-size frame at each effect's peak, checks for effect timing, Hebrew/RTL errors, captions covering faces, cut-out edges, safe zones, sound sync and loudness - then fix and report honestly. Use after any render or generation, or when the user asks to check, review, QA or "תבדוק את הסרטון".
---

# Video QA

The user should never be the first reviewer. Look at the actual frames, fix what you find, re-check, and
report exactly what was and was not checked. Based on the verification habits in Brain's write-ups
(Meaghan Choi: "I look at the output with a recording, not at everything Claude wrote").

Reply in the user's language. For deeper independent review hand the files to the `video-qa-reviewer` agent.

## Procedure

1. **Probe.** `ffprobe` the file: duration, resolution, fps, audio present, rotation. Compare with the brief
   (aspect ratio, length). Mismatch = stop and fix.
2. **Contact sheets.** Whole video at 6 fps; zoom to 12 fps around each effect:

   ```bash
   python3 scripts/contact_sheet.py final.mp4 --fps 6 --out-dir qa/
   python3 scripts/contact_sheet.py final.mp4 --start 12 --end 15 --fps 12 --out-dir qa/fx1
   python3 scripts/contact_sheet.py final.mp4 --moments 3.4,9.1 --out-dir qa/peaks
   ```
   Open every sheet image and actually look (read the PNGs). A sheet you did not open is not a check.
3. **Per-effect table.** For every effect: planned word and time, the frame where it actually lands,
   verdict. Landing means within about 2 frames of the planned frame.
4. **Checklist** (tick each, note the timecode of any miss):
   - Effect lands on its word; no residue one frame after it ends
   - Sound hits the same frame (from the cue sheet; if audio cannot be inspected, say so)
   - No clipped text; nothing outside the safe zone for 9:16
   - Hebrew: no mirrored letters, English runs intact, numbers/times/prices in order
   - Captions never cover the mouth or face; max two lines; readable at phone size
   - Cut-out edges clean (hair, hands); no flicker of the mask between frames
   - Continuity: same character, outfit, light between generated clips
   - Transitions smooth; no black or duplicate frames at cut points
   - Loop point (if intended): last frame equals first
5. **Audio check.** Loudness (`ffmpeg -i f.mp4 -af ebur128=peak=true -f null -` and read integrated LUFS and
   true peak; target about -14 LUFS, peak below -1 dBTP), silence gaps, clipping.
6. **Fix, then re-check the fixed spans.** Do not hand over a known defect.
7. **Report:** a short table (effect, word, landed at, verdict), what you checked, what you could not (and why),
   and up to three improvement proposals tied to the video's job. Apply only what the user approves.

## Rules

- Never claim a check you did not do. If no frame viewing is possible (no image tool), say it and give
  the user a 30-second phone checklist instead.
- A browser or screen recording, when available, beats screenshots for interactive pages.
- For generated clips, check against the beat list from `video-prompt-craft`, one variable per retry.
- Keep QA artifacts in `qa/` next to the video so the user can open them.
