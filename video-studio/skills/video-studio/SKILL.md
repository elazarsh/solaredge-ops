---
name: video-studio
description: Entry point for any video job - make, edit, generate or plan a video, reel, short, ad or hook (Hebrew or English). Picks the right route (edit existing footage, real-action hooks, AI-generated clips with PixVerse, HTML motion graphics), runs the five-versions method, gates every spend, and ends with an editor-grade check. Use when the user says video, reel, clip, ad, hook, subtitles, edit my footage, PixVerse, סרטון, ריל, פרסומת, הוק, כתוביות, תערוך לי.
---

# Video Studio (entry point)

This skill is the director's chair. It decides what to build, in what order, and what the user must
approve first. The craft lives in the sibling skills it hands off to. Reply in the user's language
(Hebrew by default for this user), keep technical words in English.

The method is adapted from public write-ups by Brain (brainai.co.il) of Meaghan Choi's talk on how
Claude Code's lead designer works, plus their video-editing guides. It is an independent
summary, not an official Anthropic method. See `reference/principles.md` for the full list and where each
principle came from.

## Core rules (apply to every route)

1. **One sentence is enough.** Infer the goal, audience, platform and the single thing the viewer
   should do. State assumptions in two lines and continue. Ask a question only when you cannot tell
   what the video is about. Never send a questionnaire.
2. **Versions before pixels.** For anything creative, plan five genuinely different directions at
   storyboard level first (`video-versions`). It costs words, not credits or render time.
3. **You pick first, the human decides.** Choose the best direction, explain in three points tied to
   the video's job, name one thing to borrow from the runner-up. The user takes it, switches, or
   remixes. Apply their decision to the chosen version only.
4. **Approve before you spend.** Anything that costs money, quota or a long render needs a visible
   gate (table below). A correction before rendering is cheap; after rendering it is a whole round.
5. **The first render is a draft.** Say so. Plan two or three small fix rounds (one or two changes per
   round, described by what is said at that moment, not by timestamps).
6. **Verify like an editor, then report honestly.** Use `video-qa`. Never claim a check you did not run.
   If you have no way to look at frames, say that and tell the user what to check on their phone.
7. **The human keeps the taste.** You produce options and do the heavy lifting; direction and final
   call stay with the user. Short manual tweaks are often faster by hand: say so when true.

## Step 0: preflight (one command block, report in one line)

Run what applies and tell the user only what is missing and the single next action:

```bash
ffmpeg -version | head -1; ffprobe -version | head -1
python3 -c "from PIL import features; print('RAQM', features.check('raqm'))"   # Hebrew text needs True
python3 -c "import cv2, numpy" 2>&1 | tail -1                                   # only for frame-level effects
echo "PixVerse key set: ${PIXVERSE_API_KEY:+yes}"                               # never print the key
```

Also note: is a browser tool available (for screenshots/recording), and is the HyperFrames MCP or its
local skills available (`npx skills add heygen-com/hyperframes`)? Missing optional tools never block
planning; they only change which route is possible.

## Step 1: the request, in four questions

A good request answers **what happens, when, how it feels, how it sounds.** Fill gaps yourself with
sensible defaults and show them. For effects tied to speech, "when" means "on the word X", which
requires a word-level transcript (see `video-edit-engine`).

## Step 2: choose the route

| The user has / wants | Route | Skill |
|---|---|---|
| Own talking-head footage to cut, caption, add effects | A. Edit as code | `video-edit-engine` |
| Own footage + scroll-stopping opener ("hook") | B. Real action + code element | `video-hooks-real-action` |
| No footage; wants AI-made clips (product shot, mascot, cinematic b-roll) | C. Generate | `pixverse-generate` + `video-prompt-craft` |
| Titles, charts, data stories, kinetic text, no camera footage | D. HTML motion graphics | HyperFrames (MCP or local skills) |
| Several of the above | E. Hybrid: generate clips (C), assemble and finish (A/D) | all |

Details, limits and costs of each route are in `reference/routes.md`. If the user is unsure, propose
the route that needs the least money and the least setup, and say what the alternative would add.

## Step 3: concept stage (free)

- New idea or unclear direction: run `video-versions` (five directions, pick, decide).
- Only a headline, hook line or script is needed: run `video-mini-arena` (six variants, hard judge,
  one winner) - one reply, no files.
- Delegate judging to the `video-concept-judge` agent when you want an unbiased second opinion.

## Step 4: gates (stop and show before continuing)

| Before | Show | Why |
|---|---|---|
| Any paid generation | Prompt, model, quality, duration, **credit estimate** (`pixverse.py --dry-run`) | Money is not reversible |
| Using generated images in a video | The images | Cheaper to reject an image than a render |
| Rendering an edit | Word table, cut list, effect-to-word table | Fixing a transcript is seconds; fixing a render is a round |
| Final export | Contact-sheet findings from `video-qa` | The user should not be the first reviewer |

## Step 5: build, then check, then hand over

Hand over with: the file path, what was checked (and what was not), anything that is a draft-level
compromise, how many credits/minutes it cost, and up to three concrete improvements (what to change and
why, tied to the video's job). Apply only the ones the user approves.

## Parallel work

Renders and generation are slow. When several clips or versions are independent, start them together
(background shell jobs or subagents) and keep working on the next step. Mind the user's plan quota
and PixVerse's concurrency limit (Free plan: 3 at once).

## Rights and labelling

Use only footage, music, fonts and images the user has rights to. Do not clone a real person's likeness
or voice that is not the user's own. Generated people and scenes should be labelled "AI content" where
the platform asks for it. If a request depends on impersonating someone, decline that part and offer an
original character instead.

## Agents you can hand work to

`video-director` (runs this whole workflow end to end), `video-concept-judge` (blind, harsh scoring),
`video-qa-reviewer` (frame-level review), `video-sound-designer` (sound cue sheet and mix plan),
`video-prompt-writer` (turns an idea into model-ready prompts).
