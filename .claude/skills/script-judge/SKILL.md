---
name: script-judge
description: Score and QA ad scripts with TypeSafe (Jev) — hook curiosity gap, twist strength, audience fit by age band, clarity after the reveal, warmth, offer-in-first-3s, clarity on mute, claims not in facts.md, and per-line role/clarity/gendered-address. Use inside /ad-creative at stage 3 (rank concepts), stage 4 (check the storyboard), stage 5 (compliance pre-check) and stage 7 (rank hook variants), or whenever the user asks to "score / rate / compare scripts" or "is this good for audience X". Needs TYPESAFE_API_KEY. Not a substitute for the user's taste: it ranks and flags, the user decides.
---

# Script judge (TypeSafe)

TypeSafe's System One model (Jev) returns **typed judgments with probabilities** instead of prose.
Code keeps the workflow; the model supplies the "does this feel right to this audience" call.
Docs (read before changing the rubrics): https://docs.typesafe.ai/llms.txt , `primitives/score.md`,
`patterns/composite-scoring.md`, `confidence.md`, `api.md`.

## What it checks

| Question | Type | Maps to |
|---|---|---|
| hook_gap, twist_strength | Score | `ad-creative/references/twist.md`, `hooks-he.md` |
| audience_fit (uses the age band profile) | Score | `references/audiences.md` |
| clarity_after_reveal, warmth | Score | SMP rule, "warm humor, not biting" preference |
| offer_in_first_3s | Noul | house rule: never state the offer in the first 3 s |
| needs_sound | Noul | sound-off-first rule |
| unverified_claim | Noul | `facts.md` — a number not in facts never goes on screen |
| per line: role, clarity, single-gender address | Choice / Score / Noul | beat structure, `legal-il.md` (both genders) |

Rubric text lives in `rubrics.json`. Each Score level describes a concrete situation and stands
alone (per the TypeSafe guidance). Edit the levels, not the code, to tune taste.

## How to use

1. Put the script in JSON: `{"hook", "body", "lines": [...], "facts": [...]}` (`facts` = items from `facts.md`).
2. `TYPESAFE_API_KEY=… python3 -I .claude/skills/script-judge/judge.py script.json --age mature --save raw.json`
   (`--dry-run` prints the request without calling the API).
3. Change emphasis without re-running inference: `--load raw.json --weights weights.json`.
4. Read the table: composite, flags, per-line roles. Run once per concept (stage 3) and per hook variant (stage 7).

## Rules of use

- **Rank, don't veto.** The composite is a sort key for choosing between concepts. A flag is a prompt
  to look, not a verdict. Calibrate on 5–10 scripts the user already liked or disliked
  (the MAON episodes are a ready set) before trusting thresholds.
- **Low confidence = review by hand.** The script prints it as a flag. Confidence measures how concentrated
  the answer is, not whether the ad is good.
- **Hebrew is passed as-is.** Rubric instructions are English; the state is the Hebrew script.
- **Keep policy in code.** "Any single-gender line in a job ad" is a rule over `line_gendered`, not a weighted score.
- **API key stays server/env side.** Never write it into files or commits.
- Judging is advisory; the user's approval gates (script table → "תפיק") are unchanged.

## Other places TypeSafe fits in this studio (build when asked)

- **Comment mining:** classify comments on published ads by topic/sentiment → next episode ideas (Choice + Score, run in bulk).
- **Hook bank selection:** score 30 hook candidates per age band, keep the top 3 for A/B.
- **QA of captions vs. VO:** Noul per caption line — "does this caption say the same as the VO line?"
- **Fact check:** Noul per claim against `facts.md` entries with a "verified" mark.
- **Footage selection:** pick the best Veo take per shot by Noul/Score on its description.
