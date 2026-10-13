---
name: video-hooks-real-action
description: Build scroll-stopping reel openers by filming a real action against empty air (lighting a lighter, crumpling a card, spraying and wiping, a pin, a finger press) and adding the app-style element in code - tracked, depth-ordered, with material-matched sound. Use when the user wants a strong hook, an opener that stops the scroll, "hook" videos for Instagram/TikTok, or says הוק, ריל שעוצר גלילה, לשרוף/לקמט/לנגב/לפוצץ.
---

# Real-action hooks

Everyone now edits with the same tools, so everything looks alike. A hook that stops a thumb is a
moment the viewer does not expect: a familiar app element (story sticker, notification, follow button)
floating in the room, and the creator burning, crumpling, wiping, popping or pressing it. Based on
Brain's "5 crazy hooks" guide; the recipes in `reference/hook-recipes.md` are written as reusable
templates in our own words.

**Key idea: do not ask a video model to invent the motion. Film the real action against an empty point
in the air and add the element in code.** The hand, the gaze and the flinch are real, so it reads as real.
Hebrew text stays razor sharp because no model has to guess it.

Reply in the user's language.

## Structure that worked

- Three hooks, then the ending where the code word is written in the air, then two bonus hooks for
  those who stayed. Each hook 2.5-3.5 s. A small counter in a corner (1/5, 2/5...) keeps people to the end.
- Each hook raises the stakes of the previous one ("could be your hook" -> "this too" -> "and this, seriously").
- Cuts: 2-3 frame white flash plus a whoosh with a low thud. Music light and cheerful, ducked under effects.
- Everything important inside the reel safe zone (not in the top part the feed crops).

## Step 1: shooting brief for the user (give it as a short list)

- Tripod, camera never moves. Same outfit, place and light for all shots.
- Leave an **empty wall area above the head**; that is where the element floats.
- Each shot 4-5 s: start just before the action, end just after.
- Look at the empty point as if something is there. The gaze sells the illusion.
- Props: lighter, blank white paper card, spray bottle + cloth, pin, closed marker. One per hook.
- No camera? Offer generated alternatives: a still of the creator (their own image only) animated
  with `pixverse-generate`; real footage still gives the most natural motion. Label AI content.

## Step 2: build one hook at a time (each with a visible check)

For every hook, follow `reference/hook-recipes.md`:

1. Build the element (Hebrew, sharp, app-style but drawn by us; never real app screenshots/logos).
2. **Track** the prop/hand frame by frame (find the exact contact frame). Show the user the 3-4 key
   frames: before, contact, mid-effect, end.
3. Animate the effect in code with realistic physics, partial and slow where the recipe says (an
   instant burn looks fake).
4. **Depth order: hand/prop > element > wall.** Occlude correctly, or it looks pasted.
5. Export at 1080x1920, then continue only after the key frames look right.

## Step 3: sound, assembly, QA

1. Sound per hook on its exact frames (use `video-sound-designer`): late rather than early.
2. Assemble the reel in the order above; show one frame per clip and the cut-time list; render the
   final only after approval.
3. Run `video-qa`. Specific checks: element never floats in front of the hand; text sharp in every
   frame; effect starts on the contact frame; the ending lets the code word sit for 2 full seconds.

## Limits to say out loud

- Tracking needs the prop visible; motion blur and reflections break it. Reshoot if the key frame
  is blurred.
- Crumple and wipe are the hardest to composite. Use real paper for the crumple (the folds and
  shadows are real) and a reflective-free background for the wipe.
- Do not overuse. Three to five hooks is plenty; the idea fades when every video does it.
- Be honest in the post: AI-generated personas must be labelled where the platform requires it.
