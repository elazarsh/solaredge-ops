---
name: prompt-modifiers
description: Library of 100 short slash-style thinking and writing modifiers (/humanize, /sharpen, /pre-mortem, /redteam, RICE, ICE, 80/20, /hookstorm, /sop, /first-principles, /masterprompt ...) that set the response mode, plus rules for placing and stacking them. Use when the user types a modifier like "/redteam" or "RICE", asks to sharpen/prioritise/stress-test/repurpose/teach/summarise something, or wants a reusable prompt shortcut (קיצורי פרומפט).
---

# Prompt modifiers ("100 Claude codes")

Plain natural-language instructions in slash form - not built-in commands. When the user uses one, apply its meaning immediately; if it's ambiguous, apply the closest meaning and say which.

## Placement and stacking
- **Style/output modifiers go BEFORE the content** (they set the mode): /humanize, /sharpen, /editor, /plainspoken.
- **Analysis/display modifiers go AFTER** (they act on what exists): XRAY, RICE, ICE, EISENHOWER, /table.
- Stack 2-4 max (e.g. `/sharpen /humanize /cta`). More confuses.
- Slash optional. Keep modifier names in English, content may be Hebrew. If a modifier doesn't land, add one clarifying sentence.

## Catalog (meaning)

**Writing & voice:** humanize (remove robotic/corporate tone) | stealth (imitate the user's natural style) | plainspoken (clear, direct, simple) | voiceprint (learn style/rhythm/vocabulary first) | sharpen (compact, stronger, persuasive) | anti-fluff (cut filler/vague claims) | editor (act as professional editor) | ghostwrite (write as if from the user) | say-it-better | clean-copy (polish, keep meaning)

**Thinking & strategy:** tripwire (one hidden small problem that sinks the idea) | XRAY (look beneath the surface) | rootcause | crowbar (open the problem from an unexpected angle) | blindspot | second-order (consequences after the immediate result) | redteam (attack as skeptical expert) | steelman | decision-lens | pre-mortem (assume it failed - why)

**Prioritisation:** ICE (Impact, Confidence, Ease) | RICE (Reach, Impact, Confidence, Effort) | 80/20 | EISENHOWER (urgent/important) | leverage | ROI | cut-list | priority-stack | bottleneck | quickwin

**Marketing & sales:** fomo | hookstorm (many openings) | painfinder | offer-lift | cta | objection-map | landing-page | conversion | desire-gap | sales-angle

**Content creation:** content-engine (one idea -> many pieces) | viral-angle | reel-script | carousel | thread | linkedin | caption | storyboard | repurpose | newsletter

**Learning & teaching:** teach-me | explain-like-12 | workshop | lesson-plan | homework | exercise | examples | quiz | beginner-mode | analogy

**Document & research:** summarize | extract | decisions | actions | questions | risks | brief | compare | memo | table

**Business & product:** business-model | mvp | positioning | pricing | value-prop | audience | retention | go-to-market | upsell | churn-risk

**Productivity & workflow:** workflow | sop | delegate | automation | simplify | checklist | systemize | timecut | next-action | batch

**Advanced reasoning:** mental-models | assumption-check | scenario-plan (best/realistic/worst) | first-principles | tradeoffs | constraints | diagnose (before advising) | clarify (ask questions first) | operator-mode (performance-focused operator) | masterprompt (turn into a reusable prompt)

## Scoring helpers
- **ICE:** Score 1-10 each; ICE = (I x C x E)/... or average - state formula used. **RICE:** (Reach x Impact x Confidence) / Effort. Show table + ranking + what assumptions drive the order.
- **Impact/Effort matrix:** Quick wins (impact 3-4, effort 1-2), Major projects (3-4 / 3-4), Fill-ins (1-2 / 1-2), Thankless (1-2 / 3-4).

## Custom modifiers
Users can define their own (e.g. `/mybrand`, `/sheli`). Store definitions in CLAUDE.md or a skill so they persist (see `claude-setup-architecture`).

See also: `human-writing-hebrew`, `automation-scoping`, `visual-codes`.
