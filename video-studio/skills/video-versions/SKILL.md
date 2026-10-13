---
name: video-versions
description: Concept stage for any video. From one sentence, plan five genuinely different video directions as storyboards (no rendering, no credits), pick one and explain why, let the user decide or remix, then refine only the chosen one. Use when the user asks for a video, reel, ad or intro idea, asks for options or versions, or says "make it look good". Hebrew triggers - רעיונות לסרטון, כמה גרסאות, סטוריבורד, קונספט.
---

# Video Versions

Adapted from the five-versions method (Meaghan Choi via Brain's `design-versions` skill) for video. The
point: people who ask for one video get something plausible and then bounce between "more colourful"
and "less busy" without ever seeing the alternatives. Show five real alternatives first, at storyboard
cost.

Reply in the user's language. Storyboards are cheap text and (optionally) HTML; no paid generation.

## 1. One sentence is enough

From the user's sentence work out and state in two lines (do not ask, unless you cannot tell the subject):

- **What** the video is and its **single job** (what the viewer should do or feel at the end).
- **Who** watches, and **where** (Reels/TikTok 9:16, YouTube 16:9, ad, internal).
- **Length** (default 15-30 s for social, 6-10 s for hooks/ads) and **language** (Hebrew: RTL captions,
  see `video-edit-engine/reference/hebrew-text.md`).
- **Real material**: footage, logos, product photos, copy that exist. If none, invent realistic details
  and say they are placeholders.

## 2. Five directions, not one

Pick five rows from `reference/directions.md`. Give each a short name and a one-line concept.

**Difference contract:** any two versions differ in at least three of five dimensions:
1. **Structure** (how the story is told: hook-proof-CTA, one-take, before/after, list, loop)
2. **Look** (color world and typography)
3. **Pacing** (cuts per 10 s, on-screen text density)
4. **Sound world** (voice only, music-driven, sound-effect-driven, silence)
5. **Signature moment** (the one thing remembered afterwards)

If two plans feel like siblings, replace one before going on. Avoid the defaults that make video look
generic: a dark screen with one neon accent word, auto-captions in white bold with a yellow highlight on
every line, glitch transitions on every cut, the same upbeat stock track. Use one only when the user
asks. If a row pulls toward a default, change the colours and keep the idea.

For each version write a **storyboard card** (6-8 beats max):

```
V3 "Neighbours' Morning" - concept: one continuous shot, the shop wakes up
Structure: single take, 3 text beats | Look: warm natural, rounded sans | Pacing: slow, 5 cuts
Sound: street ambience + one piano note | Signature: the shutter opens exactly on the logo word
Beat 1 (0-3s) ... Beat 2 (3-8s) ... Beat 3 (8-12s, CTA) ...
Needs: footage? / generated clips (n x 5s) / graphics only  |  Est. cost: free / ~N credits
```

Where to put them:
- **With a file system:** `video-versions/v1.md ... v5.md` plus `video-versions/index.md` (a table of
  all five). Use a new folder (`video-versions-2/`) if one exists. Optionally render a one-page HTML
  gallery with a contact-sheet style grid. Keep the files so the user can come back.
- **In a chat app:** one message, five collapsible-looking sections, or one artifact with five tabs.

## 3. You pick first, then the human decides

Before asking anything, choose the version that best serves the video's single job. Give **three short
reasons tied to that job and audience, not to taste**, and name **one thing to borrow from the
runner-up**. Write the pick to `PICK.md` when you have files.

For an unbiased check, you may hand the five cards to the `video-concept-judge` agent and compare its
ranking with yours; if they disagree, say so and explain which you trust and why.

Then hand over the decision: take the pick, choose another, or remix ("2, with the opening of 4").
The final decision is theirs.

## 4. Refine the chosen one

Apply the decision as a new version of the chosen card (`v3b`), not as five new options. Keep its
identity. Then route to the build skill: `video-edit-engine` (own footage), `video-hooks-real-action`,
or `pixverse-generate` + `video-prompt-craft` (generated clips). Small wording tweaks are often faster
for the user to do by hand; say so when it applies.

## 5. Output checklist

- [ ] Assumptions in two lines (or one question, only if the subject was unclear)
- [ ] Five storyboards that pass the difference contract
- [ ] Real or clearly-marked placeholder content in all five
- [ ] Cost and material needs on every card
- [ ] Your pick, three job-based reasons, one idea borrowed from the runner-up
- [ ] The user's decision applied to the chosen version only
- [ ] Next skill named, and the first gate (cost / transcript / images) stated
