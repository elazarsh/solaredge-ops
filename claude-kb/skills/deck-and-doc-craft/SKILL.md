---
name: deck-and-doc-craft
description: Craft presentations, reports, memos, meeting summaries, one-pagers, SOPs and briefs from source material - structure, one-idea-per-slide rules, source-only content, Hebrew RTL, preview QA for overlaps/cut-off/contrast, versioning and reusable templates. Use alongside any pptx/docx/pdf/doc skill whenever the user wants a deck, document, report, summary, minutes or handout (מצגת, מסמך, דוח, סיכום פגישה, תדריך).
---

# Deck & document craft

Pair with the file-format skills (pptx, docx, pdf, docs). This skill supplies the *thinking and QA*; those produce the file.

## Universal rules
- **Source-only:** content comes from supplied documents; no invented data, testimonials, quotes, owners or dates. Owners/dates only when explicitly stated. Gaps listed at the end as "missing information".
- **Audience + purpose + decision** stated first (who reads it, what they must decide/do).
- **Draft -> preview everything -> approve -> save as new file;** never overwrite the original.
- **Save version names** (`v1`, `v2-approved`) and keep source next to output.
- **Hebrew:** RTL for everything incl. numbers, punctuation, charts, tables (see `hebrew-rtl-output`).
- Before finishing: open the output file itself, read it, compare every fact with the source.

## Presentation (deck)
1. Audience + one-sentence message + desired action.
2. Outline first (title of each slide = its conclusion, not a topic label). Approve outline.
3. **One main idea and at most one practical example per slide.** Eight slides is a good default for a source doc summary; fewer for decisions.
4. Visual per slide chosen by `visual-codes` structure (timeline, comparison, funnel...) rather than bullet walls.
5. Design from the brand system (`design-system-first`): fonts, palette, logo placement, spacing consistent.
6. Speaker notes only for facts that are in the source.
7. **Preview every slide:** cut-off text, overlaps, contrast (4.5:1), orphan words, image resolution, RTL order of bullets and chart axes, correct slide numbers.
8. Export formats as needed; check the exported file, not only the editor view.

## Meeting summary / minutes
From transcript: summary (3 sentences), decisions, tasks (owner + date only if explicit), open questions for next meeting, optional content ideas based only on what was said. Don't attribute quotes to unidentified speakers.

## Report / memo / brief
Order: answer first (executive brief 5-8 lines) -> evidence -> options/trade-offs -> risks/assumptions -> recommended next actions -> appendix (sources table). Each recommendation tied to evidence; label fact / inference / recommendation.

## One-pagers and SOPs
Goal, trigger, owner, inputs, numbered steps, output, quality check, escalation/hand-off path, last reviewed date. For SOPs from recurring work: first do it once with the agent, verify, then save as a skill (see `claude-setup-architecture`).

## Spreadsheet / table work
Include a known-example check (a case with a known right answer) and state assumptions; keep original sheet untouched, write to a copy.

## Document QA checklist
- Facts reconcile with source (numbers, names, dates, units).
- Links work and go where labelled.
- No chat residue/placeholders (see `human-writing-hebrew`).
- Headings hierarchy correct; tables only where useful.
- Reading direction and fonts correct; fits page; accessible contrast.
- List of "verified / not verified / missing".

See also: `grounded-research`, `human-writing-hebrew`, `verify-and-safety-gates`.
