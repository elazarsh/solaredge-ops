---
name: pixverse-generate
description: Generate and edit AI video with PixVerse through its official API (or its official MCP server) - text-to-video, image-to-video, first/last-frame transitions, extend, reference-based Fusion, restyle, lip sync, sound effects, motion mimic - with a credit estimate and approval before every spend. Use when the user asks for PixVerse, wants AI-generated clips, product or mascot shots, or says פיקסברס, תייצר לי סרטון ב-PixVerse.
---

# PixVerse generate

PixVerse has an official REST API (`https://app-api.pixverse.ai/openapi/v2/`) and an official MCP
server (`uvx pixverse-mcp`, env `PIXVERSE_API_KEY`). This skill wraps the API in a tested script and puts
a spend gate around it. Docs: `https://docs.platform.pixverse.ai` (append `.md` to a page URL, or fetch
`/llms.txt`, for an LLM-friendly version). Check the docs before relying on any detail in this file:
models, prices and fields change.

Reply in the user's language; prompts go to the model in English (see `video-prompt-craft`).

## Requirements (tell the user once, plainly)

1. A PixVerse **Platform** account (platform.pixverse.ai) and an **API key** from "API Keys" (shown once).
2. **API credits** bought on the Billing page. They are separate from the PixVerse web-app subscription.
3. The key stored as environment variable/secret `PIXVERSE_API_KEY` - never pasted into chat, never
   committed, never printed. If this runs in a cloud sandbox, `app-api.pixverse.ai` (and the CDN that
   serves the finished video) must be allowed by its network policy.

If the key is missing: stop, say exactly which of the three is missing, do the parts that do not need
it (prompts, storyboards, cost estimates) and do not mock results.

## Two ways to call it

- **Script (works anywhere with Python 3):** `scripts/pixverse.py` (standard library only).
- **Official MCP server:** if `mcp__pixverse__*` tools are already connected, you may use them. Setup
  config is in `video-studio/mcp/pixverse.mcp.json.example`. Same rules apply: estimate, approve, then run.

## Workflow

1. **Plan clips.** From the approved concept (`video-versions`), list clips: purpose, prompt
   (`video-prompt-craft`), model, duration, aspect ratio, quality.
2. **Estimate and show - GATE.** For each clip run a dry run; present one table with total credits
   (and approximate dollars) and ask for approval:

   ```bash
   python3 scripts/pixverse.py text --prompt "..." --aspect 9:16 --duration 5 --quality 720p --dry-run
   python3 scripts/pixverse.py estimate --model v6 --quality 720p --duration 5 --audio
   python3 scripts/pixverse.py balance
   ```
3. **Draft cheap, finish rich.** Explore at V6, 540p/720p, 5 s, no audio. Re-generate only the winner at
   1080p / with audio. Exploration seeds can be reused.
4. **Generate** after approval (the script refuses estimates above `--max-credits`, default 300; raise it
   only with the user's say-so):

   ```bash
   python3 scripts/pixverse.py text  --prompt "..." --aspect 9:16 --duration 5 --quality 720p --out clips/c1.mp4
   python3 scripts/pixverse.py image --image hero.png --prompt "..." --duration 5 --out clips/c2.mp4
   python3 scripts/pixverse.py transition --first a.png --last b.png --prompt "..." --out clips/c3.mp4
   python3 scripts/pixverse.py extend --source-video-id 123456 --prompt "..." --out clips/c1_long.mp4
   python3 scripts/pixverse.py wait 123456 --out clips/c1.mp4      # resume a timed-out job
   ```
   Independent clips can run in parallel (separate background shells). Free plan: 3 concurrent jobs.
5. **Review each clip** with `video-qa` against the beat list. Change one variable per retry.
6. **Assemble** in `video-edit-engine` (captions, Hebrew text, sound, loudness) or HyperFrames. Do not
   leave Hebrew text to the generator.

## Gotchas

- Every request needs a fresh UUID in `Ai-trace-id`; reusing it returns the old result (the script does this).
- Status codes: 1 done, 5 generating, 6 deleted, 7 blocked by moderation, 8 failed.
- Moderation errors (500054, 500063) mean change the input; do not retry the same input in a loop.
- 500044 = concurrency limit; 500090 = out of credits - report to the user, do not retry blindly.
- Image upload: JPG/PNG/WebP, max 20 MB, max 10000 px. Video/audio uploads have per-feature limits
  (see `reference/api-notes.md`).
- Generated people and likenesses: only the user's own face/voice or original characters; label AI content.
- The script is tested against a mock server only; it has not been run against the live API in this repo's
  CI. On the first real run, start with `balance` and a 1-second 360p test clip, and tell the user if
  anything differs from the docs.

## More features (use the docs for exact fields)

Fusion/reference-to-video (`/video/fusion/generate`), multi-transition 2-7 keyframes (`/video/multi_transition/generate`),
restyle, swap (needs mask), sound effects, lip sync (TTS or audio), motion mimic, modify, upscale, avatar,
image templates, webhooks. Add them to `pixverse.py` through `--extra '{"field": value}'` or extend the
script; keep the same estimate-and-approve rule.
