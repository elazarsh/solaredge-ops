---
name: content-engine
description: Systematic content creation for creators and businesses - audit-then-create, idea banks, hook library, 30-day calendar (80/20 value vs sell), funnel logic, brand voice document, repurposing one idea across platforms, three-pass editing, ready prompt patterns (meeting summary, email, SWOT, posts, problem solving). Use for LinkedIn/Instagram/TikTok/newsletter planning and writing, brand voice, content calendars, repurposing (תוכן, קלנדר תוכן, הוקים, פוסטים, ניוזלטר).
---

# Content engine

Specificity drives quality: one real detail about the audience beats clever wording. Output must be usable work, not inspiration. Honest critique over flattery. Human judgment owns strategy, relationships and final decisions.

## System
1. **Diagnose before creating:** audit existing profile/content (what works, gaps, voice).
2. **Brand voice document:** extracted from the creator's own writing (rhythm, vocabulary, structure, banned phrases, examples); attach to every future session (store in project/CLAUDE.md/skill).
3. **Idea bank:** generate batches (e.g. 100 ideas in 5 categories), store, draw from it - no blank page.
4. **Evergreen recycling:** timeless topics re-run every 3/6/12 months.
5. **Calendar:** 30 days, one weekly theme, ~80% value / 20% direct sell.
6. **Funnel logic:** trust -> bridge -> soft sell -> direct offer.
7. **Hook library:** generate from ~10 templates (numbers, mistakes, contrarian, confession, before/after, question, curiosity gap) then pick the strongest; hooks must land in ~3 s.
8. **Repurpose:** one idea -> LinkedIn post, carousel, reel script, message, newsletter; different angle per platform.
9. **Human edit pass:** read aloud; rewrite anything you wouldn't say to a friend; three passes: cut filler -> clarify -> fix flow (see `human-writing-hebrew`).

## Prompt skeleton (works across assistants)
`Role` (specific expert) + `[audience detail]` placeholders + `numbered output spec` (table columns / word caps / fixed sequence Hook -> context -> content -> CTA) + `hard rules` (no generic openers, no invented stats; write "needs verification" instead of fabricating) + `ask clarifying questions first` + optional `self-critique` ("what's still missing? rate 1-10 with reason").
Add one real example of past content that worked: "match structure and tone, not sentences".

## Ready patterns
| Prompt | Input -> Output |
|---|---|
| Meeting summary | transcript -> 3-sentence summary, tasks (owner/date), decisions, open questions |
| Email | bullets -> professional Hebrew email |
| Competitor research | company -> SWOT (sources, flag unknowns) |
| Content | idea -> 3 posts in your voice |
| Problem solving | problem -> 5 solutions with pros/cons |
| Staged brainstorm | diverge (many) -> filter -> pick |
| Socratic tutor | asks questions before teaching |

## Short-form / viral specifics
See `ai-influencer-ugc-video` (3-second recognisability test, nested documents method).

## Measurement
Track what gets saved/shared/rewatched, not only views; keep a log of hook -> result; reuse winners.

See also: `prompt-modifiers` (/hookstorm, /repurpose, /carousel), `ad-creative-workflow`, `design-system-first`.
