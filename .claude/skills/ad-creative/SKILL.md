---
name: ad-creative
description: Plan and produce an original, high-quality video ad (Reels / TikTok / Stories / WhatsApp status / YouTube Shorts), especially in Hebrew, for a selectable age band (kids, teens, young, adults, parents, mature, seniors). Every concept is indirect — built on a surprising twist, never pushing the message upfront. Covers the whole path — brief intake, problem and audience analysis, strategy (single-minded proposition), 3 distinct concepts, hook variants, script, storyboard, production through HyperFrames/Remotion/media-use, and a QA pass on the rendered file. Use whenever the user asks for a פרסומת, מודעה, קמפיין, סרטון שיווקי/גיוס/תדמית, promo, ad, commercial, or "make it more creative/viral/young". Not for pure code-change videos (/pr-to-video) or plain captions on existing footage (/embedded-captions).
---

# Ad Creative — from problem to a finished ad

The goal is an ad that **stops the thumb, is understood with sound off, and makes one
clear ask** — and does it *smartly*: **house rule — every concept is indirect and built on a
twist** (`references/twist.md`). The message is the payoff, never the opening line. Code-built video (HyperFrames / Remotion) is the production layer; this
skill is the thinking layer that comes before it and the QA layer after it.

Work in stages. Each stage ends in a small written artifact the user can approve.
Never jump to code before the user has approved a concept and script.

| Stage | Output file (in `video-studio/ads/<slug>/`) | Reference |
|---|---|---|
| 0. Intake | `brief.md` | `templates/brief.md` |
| 1. Diagnose the problem | `brief.md` → "Problem" section | `references/strategy.md` |
| 2. Strategy | `strategy.md` (insight + proposition + angles) | `references/strategy.md` |
| 3. Concepts | `concepts.md` (3 twist concepts × 3 hooks) | `references/twist.md`, `references/audiences.md`, `templates/concepts.md`, `references/hooks-he.md` |
| 4. Script + storyboard | `storyboard.md` | `templates/storyboard.md`, `references/platforms.md` |
| 5. Compliance | checklist inside `storyboard.md` | `references/legal-il.md` |
| 6. Production | HyperFrames / Remotion project + audio | `/hyperframes`, `/media-use`, `/hebrew-video` |
| 7. QA + variants | `qa.md`, renders in `out/` | `references/review.md`, `video-studio/tools/` |

Create the folder with `bash video-studio/tools/new-ad.sh <slug> <age>`; it copies the templates with the age band filled in.

## Stage 0 — Intake (ask, don't assume)

Ask only what you can't infer, in one message, max ~6 questions. Must-haves:
1. **Business goal + the one action** (call / WhatsApp / sign up / visit / buy).
2. **Audience + age band** — one of `kids · teens · young · adults · parents · mature · seniors`
   (`references/audiences.md`; if the user didn't choose, ask — offer the list). Who exactly, where, daily life.
3. **What is true and specific** — real numbers, real perks, real place names, real people.
4. **Where it runs** (Instagram Reels, TikTok, FB, WhatsApp status, YouTube) → sizes and length.
5. **Assets** — logo, photos/video (no children's faces without consent), brand colors, voice.
6. **Constraints** — budget for paid voice/music, deadline, what the client hates.

If the user is short on time, fill gaps with explicit assumptions marked `[הנחה]` and proceed.

If the user brings existing scripts, decks or notes (even ones they dislike), run
`references/script-doctor.md`: harvest facts into `facts.md` (marked unverified), keep real insights,
flag risky claims, then rebuild the facts as reveals inside twist concepts. Never polish the old script.

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

## Stage 3 — Three twist concepts that are actually different

Load `references/audiences.md` (the chosen age band) and `references/twist.md` first.

1. Write the **obvious ad** in one line — this is what we will *not* make.
2. Each concept = a **twist technique** + a **format** + a **visual idea** only this client could own.
   Use a different twist technique and a different format for each of the three
   (formats: `references/strategy.md`; twists: `references/twist.md`).
3. Write each concept as **setup → misdirection → reveal → link (SMP + brand) → button/CTA**,
   with the reveal as a clear *visual* moment (sound-off).
4. For each concept write **3 hooks** (`references/hooks-he.md`) that set up the misdirection
   without giving it away. Adapt humor, pace and type size to the age band.
5. Run the five twist tests (surprise · clarity · truth · ownable · kind) and score every concept
   1–5 on: surprise · clarity after reveal · stops scroll · clear on mute · ownable · feasible · fits age.
   Anything ≤2 on clarity, feasible or kind is out. Recommend one; let the user pick.

Never present a concept that states the offer in the first 3 seconds, unless the user explicitly
asks for a direct-response version — then offer it *in addition* to the twist concepts.

## Stage 4 — Script and storyboard

- 15–30 s for direct response, 6–10 s for bumpers; shot changes every 1.5–3 s.
- Structure: **Hook/setup (0–3 s) → Misdirection → Reveal → Link (the message + brand) → CTA (≥3 s on screen)**.
- Pace, type size and VO speed from the age band's row in `references/audiences.md`.
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
- Recreating a familiar app (WhatsApp, Instagram, notifications) → `references/ui-mockups.md`.
- For premium motion use `/motion-craft`: beat grid from the music (`tools/beat-grid.py`), reveal on a
  downbeat, springs as pure functions of time (`tools/lib/motion.js`), one-frame-per-beat preflight,
  motion-blur render (`tools/motion-blur.sh`).
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
