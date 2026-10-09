---
name: visual-codes
description: Turn an idea, process, product or piece of text into a visual (infographic, x-ray, exploded view, blueprint, mind map, timeline, comparison, dashboard, storyboard, carousel, mockup) using short "/visual code" directions and the 4-layer method. Use whenever the user wants an image, infographic, diagram, slide visual, carousel, product shot, or asks "how would this idea look" - in Hebrew or English (קודים חזותיים, אינפוגרפיקה, תמונה, קרוסלה, מפת חשיבה).
---

# Visual codes

A visual code is a one-word creative direction written with a slash (`/xray`, `/blueprint`). It is **not** a built-in command of any tool. It is a compact art-director brief. Treat it as shorthand that you expand into a real prompt for whichever image tool is available (image-gen tool, Canva, Napkin, HTML/SVG you write yourself).

Think like a creative director: do not ask for "an image of X". Ask "how would this idea *look*?"

## The 4-layer method (use for every visual)

1. **Subject** - what is being illustrated (one idea only).
2. **Structure** - how the information is arranged: timeline, mind map, flowchart, comparison, roadmap, funnel, dashboard, storyboard, network, ecosystem.
3. **Rendering** - how it looks: handwritten notebook, blueprint, sticky notes, lego, sketch, isometric miniature, figurine.
4. **Viewpoint** - how we look at it: x-ray, cutaway, exploded view, cross-section, layers, anatomy.

Basic prompt = `code + short subject`. Advanced = `style + format + subject + instructions`. Stack 2-3 codes (more muddies the result).

## Workflow

1. Pick ONE idea and ONE audience. If the user's text has several ideas, split into several visuals.
2. Choose structure first (what does the viewer need to understand?), then rendering, then viewpoint.
3. Write the expanded prompt with: size/aspect ratio, number of items, exact text strings, colors, language + direction (Hebrew -> RTL, see `hebrew-rtl-output`), what must NOT appear.
4. Generate. Verify (see QA). Fix text/connections with one targeted edit at a time.
5. Log the winning prompt (code stack + wording) so the visual language stays consistent across a campaign.

## Techniques

- **One idea, ten images:** run the same idea through ~10 different codes, keep the best 1-2.
- **Text to visual:** turn one written sentence into 4 content assets: handwritten note, x-ray, sticky-notes board, roadmap.
- **Guiding question:** replace "how do I explain this?" with "what would this look like?".
- **Custom brand code:** define `/mybrand` = colors (hex), fonts, logo style, preferred composition; reuse it as a suffix on every prompt. Store it in the project's design system (see `design-system-first`).
- **Product photo variations:** one source photo, one command per attempt, same aspect ratio, a new chat per variation (avoids carry-over), check fidelity (shape/logo/colors) *before* judging drama. Change one requirement per attempt.
- **Exploded/breakdown views:** list the parts and assembly order explicitly; warn that internals may be invented and are not engineering-accurate.
- **Reels/carousel storytelling:** original photo first -> each result with its code label -> end with "which would you choose?".

## Good combinations (starting points)

| Goal | Stack |
|---|---|
| Hidden mechanism behind an idea | `/xray` + `/infographic` |
| Brainstorm | `/mindmap` + `/handwritten` |
| Product / AI system explainer | `/explodedview` + `/blueprint` |
| Company structure | `/cutaway` + `/isometric` |
| Change over time | `/beforeafter` + `/xray` |
| Many layers at once | `/explodedview` + `/blueprint` + `/infographic` + `/handwritten` |
| Process | `/flowchart` + `/sticky-notes` |
| Market map | `/ecosystem` + `/isometric` |
| Story | `/storyboard` + `/sketch` |

Full catalog of codes (style, viewpoint, structure, plus ~200 categorised commands for people, products, ads, branding, social, mockups, food/real estate, illustration, infographics, video): `references/catalog.md`.

## QA checklist (before showing the user)

- Outline and part proportions preserved vs. the source?
- Logo, text, colors match the source? Hebrew spelled correctly, RTL, not mirrored?
- Does it show only features the real product has?
- Shadows/reflections/parts logical? No extra limbs, no garbled text?
- Is the prompt that produced it the one recorded?
- Say what was and was not verified. Results vary between runs and tools - do not promise reproducibility.
