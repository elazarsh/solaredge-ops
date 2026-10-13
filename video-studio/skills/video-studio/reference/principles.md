# Principles learned from brainai.co.il, and where they live in this toolkit

Sources read on 2026-10-13 (all by Brain, in Hebrew; summarised here in our own words):

- `guides/claude-code-lead-designer-method` - the five-versions method and the free `design-versions` skill
  (the skill's SKILL.md was read from its public release zip).
- `guides/claude-code-video-editing` and `guides/claude-video-edited-itself` - editing video as code.
- `guides/crazy-ai-hooks` - real-action hooks with code-built elements.
- `guides/dont-trust-every-ai-video-mini-arena` - the "mini arena" one-reply tournament.
- `guides/higgsfield-guide`, `guides/video-geminy-omny`, `guides/gemini-omni`,
  `guides/earth-zoom-video`, `guides/ai-motion-transfer-character` - prompting AI video models.
- `guides/scroll-craft-skill` - interview, build, verification-pass pattern (skimmed).

Not read: the remaining ~55 guides on the site (mostly ChatGPT, Gemini, business topics), and the
YouTube talk itself. The method is known only through Brain's write-up.

| # | Principle | Source | Implemented in |
|---|---|---|---|
| 1 | One sentence in; assumptions in two lines; no questionnaire | lead-designer | `video-studio` rule 1 |
| 2 | Five versions, not one; any two differ in 3 of 5 dimensions; avoid recognisable "AI default" looks | lead-designer | `video-versions` |
| 3 | The model picks first and explains in 3 points tied to the job; the human decides; changes touch only the chosen version | lead-designer | `video-versions`, `video-concept-judge` |
| 4 | Verify in the real thing (browser/frames), record it, and say plainly when you could not | lead-designer | `video-qa`, `video-qa-reviewer` |
| 5 | Run several tasks in parallel because the model takes time | lead-designer | `video-studio` "Parallel work" |
| 6 | Approve the transcript and cut list before rendering | video-editing | `video-edit-engine` gate |
| 7 | Word-level timestamps make "on the word X" possible; one time map keeps picture, effects and sound in sync | edited-itself | `timemap.py` |
| 8 | Hebrew: shape text with Pillow+RAQM and a real font file; never `cv2.putText`; keep English runs whole; Hebrew-specific transcription model | edited-itself, video-editing | `hebrew_text.py`, `reference/hebrew-text.md` |
| 9 | Compute the person mask once and reuse it; build a clean plate for effects that remove the person | edited-itself | `reference/effects-catalog.md` |
| 10 | Request = what / when / feel / sound | edited-itself | `video-studio` Step 1 |
| 11 | Check with contact sheets: 6 fps with timecodes plus one full frame at each effect's peak | edited-itself | `contact_sheet.py` |
| 12 | Shoot the real action in empty air; add the element in code; depth order hand > element > wall; 2.5-3.5 s per hook; counter; loop ending | crazy-ai-hooks | `video-hooks-real-action` |
| 13 | Sound is half the effect: a material-matched sound on the exact frame, music ducked, loudness ~-14 LUFS | crazy-ai-hooks, edited-itself | `video-sound-designer`, `reference/sound-design.md` |
| 14 | Prompt for video models in 7 parts; use "before" to force order; start and end frames for consistency; image first | higgsfield, omni | `video-prompt-craft` |
| 15 | One-take camera moves need timestamps plus explicit "do NOT cut" bans | earth-zoom | `video-prompt-craft/reference/templates.md` |
| 16 | Motion transfer: re-create the first frame with a long keep-identical list, change only the subject | motion-transfer | `video-prompt-craft/reference/templates.md` |
| 17 | Mascot ad in 5 scenes (problem, product, action, relief, CTA); lock the character with a base image | video-geminy-omny | `video-prompt-craft/reference/templates.md` |
| 18 | Six variants, harsh judge, top three repaired, rematch; never invent numbers to make a variant look strong | mini-arena | `video-mini-arena` |
| 19 | Be honest about cost, limits and what does not work; a tip you cannot use tomorrow is not a tip | mini-arena | every skill's "limits" section; `pixverse.py` spend guard |
| 20 | The first version is a draft; fix in small rounds | video-editing | `video-studio` rule 5 |
| 21 | Permissions on manual at first so you can see what the agent does | video-editing | `START-HERE.he.md` |

## What the site claims that I could not verify

- That Opus 5.5 is needed for the effect-heavy edits. Treat as a recommendation, not a requirement; the
  scripts here do not depend on a model.
- Render speeds, HyperFrames behaviour and person-segmentation quality: not tested here (no footage, no GPU,
  no OpenCV in the sandbox). The tested parts are listed in `README.md`.
