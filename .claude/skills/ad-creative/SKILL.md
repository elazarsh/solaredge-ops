---
name: ad-creative
description: Plan and produce an original, high-quality video ad (Reels / TikTok / Stories / WhatsApp status / YouTube Shorts), especially in Hebrew and for a young audience. Covers the whole path — brief intake, problem and audience analysis, strategy (single-minded proposition), 3 distinct concepts, hook variants, script, storyboard, production through HyperFrames/Remotion/media-use, and a QA pass on the rendered file. Use whenever the user asks for a פרסומת, מודעה, קמפיין, סרטון שיווקי/גיוס/תדמית, promo, ad, commercial, or "make it more creative/viral/young". Not for pure code-change videos (/pr-to-video) or plain captions on existing footage (/embedded-captions).
---

# Ad Creative — from problem to a finished ad

The goal is an ad that **stops the thumb, is understood with sound off, and makes one
clear ask**. Code-built video (HyperFrames / Remotion) is the production layer; this
skill is the thinking layer that comes before it and the QA layer after it.

Work in stages. Each stage ends in a small written artifact the user can approve.
Never jump to code before the user has approved a concept and script.

| Stage | Output file (in `video-studio/ads/<slug>/`) | Reference |
|---|---|---|
| 0. Intake | `brief.md` | `templates/brief.md` |
| 1. Diagnose the problem | `brief.md` → "Problem" section | `references/strategy.md` |
| 2. Strategy | `strategy.md` (insight + proposition + angles) | `references/strategy.md` |
| 3. Concepts | `concepts.md` (3 concepts × 3 hooks) | `templates/concepts.md`, `references/hooks-he.md`, `references/youth-tone.md` |
| 4. Script + storyboard | `storyboard.md` | `templates/storyboard.md`, `references/platforms.md` |
| 5. Compliance | checklist inside `storyboard.md` | `references/legal-il.md` |
| 6. Production | HyperFrames / Remotion project + audio | `/hyperframes`, `/media-use`, `/hebrew-video` |
| 7. QA + variants | `qa.md`, renders in `out/` | `references/review.md`, `video-studio/tools/` |

Create the folder with `bash video-studio/tools/new-ad.sh <slug>`; it copies the templates.

## Stage 0 — Intake (ask, don't assume)

Ask only what you can't infer, in one message, max ~6 questions. Must-haves:
1. **Business goal + the one action** (call / WhatsApp / sign up / visit / buy).
2. **Audience** — who exactly, where they live, age, what they do all day.
3. **What is true and specific** — real numbers, real perks, real place names, real people.
4. **Where it runs** (Instagram Reels, TikTok, FB, WhatsApp status, YouTube) → sizes and length.
5. **Assets** — logo, photos/video (no children's faces without consent), brand colors, voice.
6. **Constraints** — budget for paid voice/music, deadline, what the client hates.

If the user is short on time, fill gaps with explicit assumptions marked `[הנחה]` and proceed.

## Stage 1 — Diagnose before creating

An ad solves a **behavior problem**, not a design problem. Write down:
- **Job to be done:** what is the audience trying to get done in their life when this ad reaches them?
- **Barrier:** why don't they already do the action? (don't know / don't believe / don't care / too hard / fear)
- **Current alternative:** what do they do instead? Who is the real competitor?
- **Proof we have:** facts that remove the barrier.

The barrier chooses the ad type: *don't know* → awareness, clear news; *don't believe* → proof, testimonials, demo; *don't care* → emotion, identity; *too hard* → show how easy, one step; *fear* → reassurance, faces, guarantees.

## Stage 2 — Strategy on one page

- **Insight:** one human truth in the audience's own words (see how to mine it in `references/strategy.md`).
- **Single-minded proposition (SMP):** one sentence, one benefit. If it has "and", cut.
- **Angles:** 3 different ways into the SMP (e.g. identity, FOMO, problem→solution, social proof, behind-the-scenes, challenge/trend).
- **Tone words:** 3 adjectives + 1 "never" (e.g. חם, אנרגטי, אמיתי — never מתיילד).

## Stage 3 — Three concepts that are actually different

Each concept = a **format** + an **angle** + a **visual idea** that could only belong to this client.
Use different formats across the three (see format menu in `references/strategy.md`):
kinetic typography, fake-UGC/POV, "day in the life", list/countdown, before→after, text-message/chat
simulation, quiz/challenge, testimonial quote cards, map/place reveal.

For each concept write **3 hooks** (first 1.5–3 s) using different hook patterns from
`references/hooks-he.md`. Score every concept 1–5 on: stops scroll · clear with sound off ·
ownable (only this brand) · feasible with our assets · fits tone. Recommend one; let the user pick.

Originality check before presenting: *if you swap the logo for a competitor's, does the ad still work?*
If yes, it's generic — add a specific place, person, number, or ritual.

## Stage 4 — Script and storyboard

- 15–30 s for direct response, 6–10 s for bumpers; shot changes every 1.5–3 s.
- Structure: **Hook (0–3 s) → Value (proof, 1 idea per beat) → Emotional beat → CTA (≥3 s on screen)**.
- Every beat has: on-screen text (≤ 6 words), VO line, visual, motion, sound cue.
- Design for **sound-off first**: burned-in captions + large on-screen text; VO is a bonus.
- Keep all important text inside the safe zone (`references/platforms.md`).
- Hebrew specifics (gender, niqqud for TTS, RTL, fonts) → `/hebrew-video`.

## Stage 5 — Compliance

Run the checklist in `references/legal-il.md` (job ads must address both genders, no
misleading claims, image consent, music licensing, platform policies). Flag issues to the user;
do not silently rewrite their offer.

## Stage 6 — Production

Route through `/hyperframes` (default) or Remotion (`video-studio/remotion`). Rules:
- Build the **storyboard frames first** as stills, show them, then animate.
- Voiceover: `/media-use` Gemini TTS with fully vocalized Hebrew text.
- Music: royalty-free file from the user or generated; duck under VO; master ≈ −14 LUFS, −1 dBTP.
- Keep copy, colors and durations in one data object/variables so variants are a one-line change.

## Stage 7 — QA and variants

1. `bash video-studio/tools/ad-qa.sh out/final.mp4` — specs, loudness, duration, black frames.
2. `bash video-studio/tools/contact-sheet.sh out/final.mp4` — then **Read the PNG** and review it
   visually against `references/review.md` (hook legible at 0.5 s? text in safe zone? CTA readable?).
3. `bash video-studio/tools/safe-zone-check.sh out/final.mp4` — frames with the Reels UI zones drawn on.
4. Fix, re-render, repeat. Then render variants: 3 hooks × same body, and 9:16 + 1:1 (+ 16:9 if YouTube).
5. Write `qa.md`: what was checked, what's left, and the recommended A/B test.
