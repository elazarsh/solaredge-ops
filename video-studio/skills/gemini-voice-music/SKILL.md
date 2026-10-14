---
name: gemini-voice-music
description: Create a narrator voice (Gemini TTS) and background music (Google Lyria 3 Clip) for a video with the Gemini API key, with the failure modes learned on a real Hebrew job - slow pace, 429 quotas, unstable proper nouns, comic pauses - and a transcription-based verification loop. Use when a video needs a Hebrew or English narrator, a trailer voice, or licensed-to-use generated music. Hebrew triggers - קריין, הקראה, קול, מוזיקה לסרטון, TTS.
---

# Gemini voice and music

Needs `GEMINI_API_KEY` (environment variable, never pasted in chat). Working code from a real job:
`examples/prague-petrin/voice_tools.py`, `make_voice.py`, `pick_l6.py`, `make_music.py`. Docs:
`https://ai.google.dev/gemini-api/docs/speech-generation`, `.../music-generation` (append `.md.txt`).

## Models (checked 2026-10-14)

- TTS: `gemini-2.5-flash-preview-tts` (used; Hebrew works), also `gemini-2.5-pro-preview-tts`, `gemini-3.1-flash-tts-preview`, `gemini-3.8-flash-tts`.
  Output is 24 kHz PCM in `candidates[0].content.parts[0].inlineData.data`.
- Music: `lyria-3-clip-preview` (30 s, $0.04) and `lyria-3.5` (full song, $0.08) through `POST /v1beta/interactions`;
  audio at `steps[type=model_output].content[type=audio].data` (base64 mp3).
- Transcription for checks: `gemini-flash-latest` (the exact name `gemini-2.5-flash` returned 404 on this key; list models first).

## Rules that saved the job

1. **Verify every line by transcribing it back** and comparing to the exact wording. Never trust a take unheard-or-unchecked.
   Run the transcription 3 times: one pass can be noise (a stable 3/3 is the bar for a punchline).
2. **Pace:** a "dramatic trailer voice" prompt came out at 1.1-1.5 words/s. A prompt for a "30-second TV commercial announcer,
   very fast, about 3.5 words per second, tiny pauses" gave natural trailer pace (about 2.4-2.8 w/s). Generate best-of-N takes
   against a per-line time budget; gentle `atempo` 1.08-1.10 is safe, beyond ~1.3 it degrades.
3. **Quotas:** the TTS preview returns HTTP 429 fast. Generate sequentially, sleep 6 s between calls, back off 25 s x attempt, cache every
   good take on disk, and make the script resumable.
4. **One-word lines are unreliable** (repeats, stutters). Generate the whole sentence and, if you need a comic pause, insert silence in
   editing at the measured gap before the last word (`silencedetect`), then re-verify.
5. **Foreign proper nouns drift** (Petřín became "פטריז'ין"). Accept the closest stable pronunciation or add niqqud to that word only; keep
   the on-screen spelling as the client wrote it and tell the client what the voice says.
6. **Mix for intelligibility, then re-transcribe the final mix.** Duck music under the voice (about -0.7 gain), add a presence band
   (1.8-4.2 kHz), and where a loud score masks consonants, pull the score back further and low-pass it (2.8 kHz) under that line.
   A line that transcribes correctly alone but wrongly in the mix is a mix problem, not a voice problem.
7. **Music prompts:** say "instrumental only, no vocals", the instrumentation, tempo and "begins immediately at full intensity".
   Measure the energy envelope before choosing where to cut. Label music as AI-generated where a platform asks.
8. **Rights:** use only voices and music you generated or own; do not clone a real person's voice.

## Cost

TTS and transcription are cents; Lyria Clip is $0.04 per 30 s. Tell the user the running total in the hand-over.
