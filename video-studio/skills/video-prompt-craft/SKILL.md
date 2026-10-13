---
name: video-prompt-craft
description: Write prompts that AI video models actually obey - PixVerse, Higgsfield, Gemini Omni, Veo, Kling, Sora, Seedance. Seven-part formula, ordering with "before", start/end frames for consistency, mascot ad in five scenes, one-take camera moves with timestamps and bans, motion-transfer character swaps, storyboard-to-video. Use when the user wants to generate video with AI, needs a prompt, a shot list, or says פרומפט לוידאו, תכתוב לי פרומפט, סרטון AI, מסקוט, סטוריבורד.
---

# Video prompt craft

Most disappointing AI video comes from a lazy prompt. The model cannot read your mind: describe what
matters. Based on Brain's guides on Higgsfield, Gemini Omni, the Earth-zoom one-take and motion
transfer; templates are in `reference/templates.md`.

Write the **prompt in English** for the model (models follow it best), and explain choices to the user in
their language. Keep any on-screen text out of the generated video if it is Hebrew; add it afterwards in code
(`video-edit-engine/reference/hebrew-text.md`).

## The seven parts

1. **Shot type** - wide, medium, close-up, macro, top-down, over-the-shoulder; lens or camera if it matters.
2. **Subject** - the person/product/creature in concrete detail (age, clothing, colours, materials).
3. **Action** - what happens, as a sequence. Use **"before"** to force order: "before she drinks, she opens the bottle".
4. **Environment and context** - place, time of day, weather, props, what is in the background.
5. **Style and mood** - photoreal / 3D Pixar-like / 2D animation / stop-motion; light; colour world.
6. **Audio** - ambience, effects, music, speech (if the model generates audio).
7. **On-screen text** - only if truly needed and short (never Hebrew in generated frames).

Then **camera movement** (one clear move), **duration** and **aspect ratio** go in parameters, not prose.

## Consistency toolbox

- **Image first.** Generate or choose the still, check it, then animate it. You see the character before paying for motion.
- **Start frame and end frame** (first/last-frame video, "transition" in PixVerse) lock the character between two known images.
- **Base character image.** Create the character once, attach it to every scene prompt, and say "keep the character identical".
- **Seed** helps repeat a result you liked; change one thing at a time.
- **Storyboard vs separate images:** one storyboard image is faster; separate images are easier to repair
  when one frame is bad. Default to separate images for anything that matters.

## Patterns

- **Mascot ad (5 scenes, ~10 s):** frustrated customer; product/mascot activated; mascot fixes the
  problem; relief and smile; clean end card with call to action. Lock one mascot design first.
- **One-take impossible camera move:** timestamped beats plus explicit bans (`do NOT cut, do NOT
  cross-dissolve, do NOT fade`); describe acceleration and deceleration; match the final frame to a
  supplied photo. Orbit-to-street and street-to-orbit templates are in the reference.
- **Motion-transfer character swap:** first make the new first frame (same pose, same room, only the
  subject changes), with a very long "keep identical" list, then animate with the person's own motion.
  Original characters, or the user themself - never a real person who is not them.
- **Product ad from a URL/photo:** write the sequence of actions with "before"; keep 1 hero shot, 1
  detail shot, 1 usage shot, 1 end card.
- **Edit by conversation (Gemini Omni style):** upload a clip and ask for one change at a time ("change
  only the watch", "switch to close-up"), keeping everything else identical.

## Working with PixVerse specifically

- Models: **C1** cinematic/reference-based; **V6** general, multi-clip, extend. Duration 1-15 s.
- Cheapest useful draft: V6, 540p or 720p, 5 s, no audio. Upgrade only the winner (1080p, audio).
- Use text-to-video for exploration, image-to-video for control, first/last frame for continuity,
  Fusion (reference-to-video) for subject consistency, Extend (V6) for longer shots.
- Run through `pixverse-generate` (cost estimate and approval first).

## Prompt-writing procedure

1. State the video's single job and length in one line.
2. Draft the beat list (what the viewer sees second by second).
3. Convert each beat into the seven parts; merge into one prompt per clip (<= 5000 characters for PixVerse).
4. Add negatives: `no text, no logo, no watermark, no extra people, no morphing, no camera shake`.
5. For several clips, write all prompts and show them with the cost estimate before generating any.
6. After generation: judge the result against the beat list with `video-qa`, change one variable at a time.

If the user asks only for prompts, deliver them ready to paste, in a code block each, with the intended
model, duration, aspect ratio and quality listed above the block. The `video-prompt-writer` agent can do this
in parallel for many clips.
