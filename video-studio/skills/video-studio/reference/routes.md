# Routes: what each needs, what it gives, what it costs

## A. Edit your own footage as code (`video-edit-engine`)

- **Needs:** the recording, ffmpeg, Python with Pillow(+RAQM), a Hebrew font file. For frame-level
  effects also OpenCV/numpy and `rembg` (person mask). For Hebrew speech: whisper.cpp with an
  ivrit.ai model (local, free); otherwise any word-level transcriber.
- **Gives:** silence cuts, animated word-synced captions, titles, 17 catalogued effects, sound, loudness
  normalisation.
- **Costs:** your plan's usage and render time. No per-video fee.
- **Limits:** person cut-outs are imperfect on hair, moving hands and busy backgrounds. A steady camera
  and plain background help most. Transcripts are never 100% (English names in Hebrew speech).
- **Engine options:** (1) the Python/OpenCV frame-compositor described in `video-edit-engine`;
  (2) HyperFrames by HeyGen (open source, HTML to video, local render; install per its official guide);
  (3) Remotion (free for individuals and companies up to 3 people; check its licence).

## B. Real-action hooks (`video-hooks-real-action`)

- **Needs:** a tripod and a phone camera; one cheap prop per hook (lighter, paper card, spray bottle,
  pin, marker). Same outfit, place and light for all shots.
- **Gives:** 2.5-3.5 s openers where an app-style element floats in the air and is burned, crumpled,
  wiped, popped or pressed, plus a code-word ending.
- **Costs:** an hour of shooting; render time.
- **Limits:** tracking depends on a clear view of the prop; keep the wall above your head empty.

## C. Generate clips with AI (`pixverse-generate`, `video-prompt-craft`)

- **Needs:** a PixVerse Platform account, an API key (shown once), **API credits** (separate from the
  PixVerse web-app subscription). Optional: official PixVerse MCP (`uvx pixverse-mcp`).
- **Gives:** text-to-video, image-to-video, first/last-frame transitions, multi-frame transitions,
  reference-based generation (Fusion), extend (V6), restyle, swap, lip sync, sound effects, motion
  mimic, upscale. Models: C1 (cinematic, reference-based) and V6 (general, multi-clip, extend); up to
  15 s per clip, up to 1080p.
- **Costs (checked 2026-10-13, per second, no audio / with audio):** V6 720p 9 / 12 credits; C1 720p
  10 / 13 credits. Docs example: $1 buys about five 5-second V6 720p clips without audio.
  Re-check `https://docs.platform.pixverse.ai/pricing-796039m0` - prices change.
- **Limits:** Free plan = 3 concurrent generations. Content moderation can reject inputs (status 7).
  Text inside generated video is unreliable; add text in code. Hebrew text in video models is
  especially unreliable.
- **Other generators the same prompts work for:** Higgsfield (many models, Cinema Studio),
  Gemini Omni (video editing by conversation, native audio, lip sync), Veo, Kling, Sora, Seedance.

## D. HTML motion graphics

- **When:** titles, kinetic type, charts, product explainers, anything where every pixel should be
  exact and Hebrew must be sharp.
- **How:** HyperFrames. In a hosted chat client use its MCP (`compose`, `render_video`; creates a
  cloud project with a share link). In a local agent use its local skills instead
  (`npx skills add heygen-com/hyperframes`, then `/hyperframes`). Do not mix them up: the MCP's
  compose/render tools are disabled for local CLI agents by design.

## E. Hybrid (recommended for ads)

1. Generate 3-5 hero clips (C), 5 s each, 9:16, 720p, no audio (cheapest, you add sound yourself).
2. Assemble, caption and score them (A or D) so Hebrew text and sound are exact.
3. Run `video-qa`, fix, export.

## Choosing quickly

- "Make my talking video better" - A.
- "I want people to stop scrolling in the first second" - B (or an A-effect on the key word).
- "I have no video, only a product photo" - C image-to-video, then finish with A/D.
- "Explain this data" - D.
- Unsure about budget - start with `pixverse.py estimate` and the free routes first.
