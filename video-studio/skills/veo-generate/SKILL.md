---
name: veo-generate
description: Generate AI video with Google Veo 3.1 (fast, standard, lite) through the Gemini API - text-to-video, image-to-video, first/last-frame transitions - with a USD estimate and spend cap before every call, safety-filter handling and download within Google's 2-day retention window. Use when the user asks for Veo, Gemini video, Google video generation, or says "תממש ב-Veo", "תייצר ב-Veo".
---

# Veo generate

Veo 3.1 runs on the Gemini API with the key in `GEMINI_API_KEY`. This skill wraps it in a tested script
(`scripts/veo.py`, standard library only) and puts a spend gate in front. Official docs:
`https://ai.google.dev/gemini-api/docs/veo` (append `.md.txt` for raw markdown). Re-check them before
relying on any number here; preview models change.

Reply in the user's language; write prompts in English.

## Facts that shape every plan (docs checked 2026-10-13)

| | |
|---|---|
| Models | `fast` = veo-3.1-fast-generate-preview, `standard` = veo-3.1-generate-preview, `lite` = veo-3.1-lite-generate-preview. Check with `veo.py models` (free call). |
| Length | **4, 6 or 8 s only.** 1080p and 4k only at 8 s. Extension and reference images need 8 s and 720p (extension). |
| Aspect | **9:16 or 16:9 only.** |
| Audio | Always generated natively and included in the price. Prompts can carry audio cues. |
| Price per second | fast 720p $0.10, 1080p $0.12 · standard $0.40 · lite 720p $0.05, 1080p $0.08. **No free tier.** |
| Retention | Google deletes the file after 2 days. Download immediately. |
| Watermark | Invisible SynthID on every video. |
| People | text-to-video allows people; image-to-video, transitions and references allow adults only. Some regions stricter. |

Draft at `fast` 720p 4 s ($0.40). Re-generate only winners at `standard` or 8 s/1080p.

## Workflow

1. **Plan clips** (purpose, beats, length of 4/6/8 s, aspect). If a scene must be shorter than the clip,
   generate 4 s and trim in the edit.
2. **Write prompts** with `video-prompt-craft` (seven parts, "before" for order, negatives). No text or
   Hebrew inside generated frames; add it later in code. Add audio cues only if you will keep Veo's audio.
3. **Dry run and gate:**
   ```bash
   python3 scripts/veo.py text --prompt "..." --aspect 9:16 --duration 4 --dry-run
   python3 scripts/veo.py estimate --model fast --resolution 720p --duration 4
   ```
   Show the total for all clips (and how many retries you assume). The script refuses above `--max-usd`
   (default $2.00 per call); raise it only with the user's yes. Total spend in a session is your
   responsibility: keep a running tally in the hand-over.
4. **Generate** (independent clips in parallel background shells):
   ```bash
   python3 scripts/veo.py text  --prompt "..." --aspect 9:16 --duration 4 --out clips/c1.mp4
   python3 scripts/veo.py image --image still.png --prompt "..." --out clips/c2.mp4
   python3 scripts/veo.py transition --first a.png --last b.png --prompt "..." --out clips/c3.mp4
   python3 scripts/veo.py wait operations/XXXX --out clips/c1.mp4      # resume after a timeout
   ```
5. **Review** each clip with `video-qa` against its beat list. Change one variable per retry.
6. **Assemble** in `video-edit-engine`. Strip Veo's audio with `-an` when you replace it with a designed mix.

## Gotchas

- A blocked prompt/result returns no sample and `raiMediaFilteredReasons`; the script prints them. Rephrase;
  do not loop on the same prompt. Content with children or real people is the most common cause.
- `durationSeconds`: docs show strings, SDKs send integers. The script tries integer first and retries once
  with a string if the API complains.
- `seed` slightly improves repeatability, it does not guarantee it.
- Never print or log the key; the script sends it as the `x-goog-api-key` header only.
- Tested against a mock server and against the live `models` endpoint. Generation paths run against the
  live API only when the user has asked for a real render.
- Veo cannot be trusted with Hebrew speech or text; for Hebrew narration use a voice tool.

## Not covered by the script yet

Video extension, reference images (up to 3), and 4k are in the docs. Add them to `veo.py` the same way
(same cost estimate and approval rules) when a project needs them.
