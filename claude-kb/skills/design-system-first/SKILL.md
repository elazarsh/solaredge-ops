---
name: design-system-first
description: Build and use a brand design system before producing any deck, landing page, carousel, prototype, document or video, so every output looks like one designer made it. Covers brand inputs, design tokens, prompting rules for design tools (Claude Design, Canva, Figma, Gamma), token-saving habits and design review. Use at the start of any visual/branding/presentation/website project or when outputs look generic (מערכת עיצוב, מיתוג, מצגת, דף נחיתה, קרוסלה).
---

# Design system first

Build ONE good design system, then generate everything "on the basis of" it. Don't accept tool defaults - generic output comes from missing inputs.

## Brand inputs to gather
- Website URL (a real codebase beats a visual guess), logo file, fonts, screenshots of past work, social posts, Figma file, free-text notes ("I like blue, keep all in blue shades").
- A **brand concept file** (`brand.md`) = the spec for everything: concept, audience, mission, positioning, voice, palette (hex), typography (fonts, sizes, weights, hierarchy), buttons (shape, size), voice & tone incl. Hebrew usage, CTAs, emoji policy, logo clear-space, imagery rules, forbidden elements.
- Don't upload a whole codebase; logo + colours + type + a few buttons is enough.

## Ways to build the system (cheapest first)
1. **Coding agent** builds it from site/images/logo/fonts and extracts palette, type, buttons, voice, CTAs, emoji policy, then sync into the design tool (e.g. `/Design` -> Design Sync in Claude).
2. **Inside the design tool**: add URL/Figma/assets/notes, generate (~minutes), review each element.
3. **Fallback**: any LLM writes the system doc -> PDF -> upload (less accurate).

## Prompting rules for design tools
- **Reference, don't describe** (screenshots, sketches, named products/styles).
- **Be specific**; replace vague adjectives with a concrete reference.
- **Use negatives** (no fonts/colours/styles you reject).
- **Supply your own copy**; ask the tool to *interview you first* for new pages: business name, mood, language, products/services, primary visitor action, number of versions. Mark missing images as placeholders.
- **One major visual change per prompt.** Five changes in one prompt -> one or two done well.
- Plan/brainstorm in normal chat, bring a finished plan into the design tool.
- Strong model for planning and big changes; light model for tweaks.
- Prefer manual edits (inline edit, comments, tweak panels) for small fixes; do logos in Canva when faster than prompting.
- Fresh session when threads get long. Mobile optimisation must be requested explicitly.
- Logos: tools tend to redraw them; simple wordmarks survive, complex icons need manual fix.

## Using the system
- Request deliverables "based on the design system": deck, landing page, carousel, social set, prototype, launch video.
- Check each new output against the system's colours, fonts, buttons, tone before accepting.
- Export options: PDF/PPTX/HTML-ZIP/video. For publishing: hand HTML/ZIP to a coding agent, build locally, review, approve, then deploy.
- No native MP4 export in some tools -> animate via code (see `code-driven-video`) or screen-record.

## Design-system minimums for code (Figma -> code iron rules)
Auto Layout everywhere; meaningful layer names (`Button-Primary`, `Section-Hero`); Variables for colours/fonts/spacing -> CSS variables; Frames not Groups; icons as SVG/components; exact values instead of adjectives (right column, 320px, #FFFFFF). Add a Critic pass: hierarchy, responsiveness, accessibility, contrast (WCAG 4.5:1 normal, 3:1 large), system fidelity.

## Token tiers for a project
```
colors:   action, text, bg, bg-secondary, status(success/warn/error), border
type:     font family (Hebrew-capable), scale, weights, line-height
space:    8px scale
radius/shadow/motion: one set only
voice:    tone words, banned phrases, CTA verbs, emoji policy
```
Store as `brand.md` + `tokens.css` in the repo; reference from CLAUDE.md (see `claude-setup-architecture`).

See also: `visual-codes` (custom `/mybrand` code), `web-build-harden`, `deck-and-doc-craft`, `hebrew-rtl-output`.
