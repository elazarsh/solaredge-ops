---
name: video-mini-arena
description: One-reply tournament for hooks, headlines, scripts, titles, CTAs and short copy - six genuinely different variants, a harsh judge that finds each one's biggest weakness and scores it out of 100, repair the top three, rematch, deliver one winner. Use when the user wants the best hook/opening line/title/script for a video, is unhappy with an answer, or says "arena", "זירה", "תעשה זירה", "הוק הכי טוב".
---

# Video Mini Arena

A compact version of "make many agents compete". It runs inside one reply, works in any chat, and
finishes in about a minute. It is based on Brain's "mini arena" write-up; the full 100-agent version needs
subagents, takes over an hour and, in Brain's own test, a one-line hook did not justify it.

Reply in the user's language. Use the `video-concept-judge` agent for the judging round when subagents
are available; otherwise change hats yourself and say so.

## Why it works

Asked once, a model gives the most predictable answer. Forced to write six variants from different
angles, it leaves its comfort zone. Asked to switch role and attack its own work, it catches errors a
normal answer would have let through.

## Modes

| Say | Variants | Repair rounds |
|---|---|---|
| "quick arena" / זירה מהירה | 4 | 1 |
| "arena" / זירה (default) | 6 | 2 |
| "deep arena" / זירה עמוקה | 10 | 3 |

## Procedure

1. **Task and judge criteria (2 lines).** Restate the task, the audience and the one goal (e.g.
   "stop the scroll in 1 s", "get a sign-up"). If the goal is missing, state your assumption.
2. **Approach cards.** Deal one different approach to each variant, for example: curiosity gap,
   concrete number, contrarian claim, direct address, story fragment, pain first, outcome first,
   pattern interrupt, social proof, plain honesty. No two variants may share an approach.
3. **Write the variants.** Each is real, final-quality copy in the user's language, not an outline.
4. **Judge hat on.** For each variant: its single biggest weakness (specific, e.g. "claims a result
   it cannot support", "too long to read in 1 s", "sounds like every other ad"), then a score /100
   against the stated goal. Be harsh; a 90 must be earned.
5. **Repair.** Take the top three, fix exactly the named weakness, and rescore.
6. **Rematch.** Final judge picks one winner, shows the score table, and says in two lines why it
   beat the runner-up.
7. **Deliver:** the winner first, the table second, anything borrowed from the runner-up third.

## Hard rules

- **Never invent numbers, results or testimonials** to make a variant look stronger. If a number is
  needed and the user has not given it, leave a visible blank: `[YOUR NUMBER]`.
- Variants must differ in angle, not just wording. If two read like cousins, rewrite one.
- Ask for more context only if the goal or audience is impossible to infer; more context makes the
  judge sharper, so invite it at the end.
- The decision is still the user's. Offer to run another round on a different goal.

## Good uses

Opening line of a reel; title and thumbnail text; the call to action; a 30-second script angle;
choosing between two edits of a scene (describe both and judge them against the goal).
