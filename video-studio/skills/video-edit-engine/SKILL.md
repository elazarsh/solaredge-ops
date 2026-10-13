---
name: video-edit-engine
description: Edit the user's own footage as code - transcribe with word timestamps, cut silences and takes, add animated Hebrew-safe captions, place effects on exact spoken words, mix sound, normalise loudness, render and verify. Use when the user has a recorded video and wants cuts, subtitles, effects, a reel from a talking-head clip, or says "edit my video", "add captions", "תערוך לי את הסרטון", "כתוביות בעברית", "אפקט על המילה".
---

# Video Edit Engine

Claude does not drag clips on a timeline. It writes the edit as code, looks at frames, and renders. This
skill is the reusable engine plus the working rules. Based on Brain's video-editing guides; the
scripts in `scripts/` are original and tested (see the repo README for what is and is not tested).

Reply in the user's language. Work in a dedicated folder per video; whatever is in the folder, you
can see. Ask the user to put there: the video, the logo, a Hebrew font file, music they own.

## The engine (build once per project, reuse for every video)

| Part | What | How |
|---|---|---|
| Frames | Compose every frame yourself | Python + Pillow (+ numpy; OpenCV for warps, optional) |
| Picture+sound | Join frames and audio | `ffmpeg` (frames in, filter graph for audio) |
| Words | Transcript with a timestamp for every word | whisper.cpp or similar; **Hebrew: an ivrit.ai model** (e.g. ivrit-large-v3-turbo), local and free |
| Time map | Original time to final time after cuts/holds | `scripts/timemap.py` (`TimeMap`, `segments_from_words`, `audio_filtergraph`) |
| Hebrew text | Correct RTL shaping | `scripts/hebrew_text.py` (Pillow + RAQM; never `cv2.putText`) |
| Person mask | Who is in each frame | `rembg` with `u2net_human_seg`, computed **once** and saved to disk |
| Render | One function `frame(t) -> image` | parallel over CPU cores, then encode high quality with audio |

Install what is missing yourself, tell the user in one sentence what you installed and why, and run the
preflight in `video-studio` first. HyperFrames (HTML-to-video, open source) is an alternative engine; see
`video-studio/reference/routes.md`.

## Workflow (with gates)

1. **Look and listen.** Probe with `ffprobe`; extract frames across the whole clip; transcribe with
   word-level timestamps. Save the word table as JSON (`words.json`: word, start, end).
2. **Show the transcript and the plan - GATE.** Show the transcript, the proposed cut list
   (`timemap.py words.json` suggests keep-segments: silence gap 0.45 s, pad 0.08 s), and a table of
   *effect -> word -> original second*. Wait for approval. A fix here takes seconds; after rendering it
   takes a round. Warn about English names in Hebrew speech: no transcriber is 100%.
3. **Build the first draft** in the original aspect ratio unless told otherwise: cuts with soft
   transitions, animated captions, music at low volume under speech. State that it is a draft.
4. **Effects.** For each approved effect read `reference/effects-catalog.md`, place it by *original* time
   of its word via `TimeMap.to_final`, and render only what is approved. Effects that need the person
   mask or a clean plate say so in the catalog.
5. **Sound.** Plan with the `video-sound-designer` agent or `reference/sound-design.md`: a sound per
   effect on its exact frame, music ducked under speech and silent in blackouts, loudness to about
   -14 LUFS for social. Cut the original audio with `TimeMap.audio_filtergraph()` so it stays in sync.
6. **Verify like an editor** with `video-qa` (contact sheets, effect landing, Hebrew, captions vs faces).
   Fix and re-verify before the user sees it.
7. **Hand over** the file path, a table "effect, word, final second", what was verified and what was not,
   and up to three improvement proposals. Apply only approved ones. Corrections come in rounds of one
   or two changes, described by what is said at that moment ("when I say *price*, slow the zoom").

## Hebrew rules (non-negotiable)

- Text is drawn with `hebrew_text.render_text` using the user's font file. If no font is provided, find
  a free Hebrew font (e.g. Heebo, Rubik, Assistant, Noto Sans Hebrew) and say which.
- Keep every English/Latin sequence as one unit inside Hebrew lines; check it did not come out reversed.
- Times, prices and phone numbers must read in the right order; check them on a frame.
- Details and pitfalls: `reference/hebrew-text.md`.

## Limits to say out loud

- The first render is a draft; good effects take a few rounds.
- Person cut-outs are imperfect (hair, hands in motion, busy backgrounds). Good light and a plain
  background help.
- Rendering takes time (machine, length, layer count) and uses plan quota; work on short sections when
  iterating.
- Generated images or sounds from external services cost money and need the user's API key; ask first.
- Never claim a check you did not run. If frames cannot be viewed, say so.

## Quick commands

```bash
python3 scripts/timemap.py words.json --duration 62.4            # suggested keep-segments as JSON
python3 scripts/hebrew_text.py "שלום Falafel" --font Heebo.ttf --out sample.png

# Cut the original audio by the very same map that cuts the picture:
python3 - <<'PY' > audio_graph.txt
import sys; sys.path.insert(0, "scripts")
from timemap import TimeMap
print(TimeMap([(0.0, 8.2), (9.1, 21.7)], holds=[(14.3, 0.7)]).audio_filtergraph())
PY
ffmpeg -i in.mp4 -filter_complex_script audio_graph.txt -map "[aout]" cut_audio.wav
```
