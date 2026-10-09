---
name: image-generation-playbook
description: Practical techniques for AI image generation and editing (Nano Banana/Gemini, GPT Image, Midjourney, Ideogram, Higgsfield) - prompt anatomy, aspect ratios, lighting, exclusions, step-wise edits, consistency across images, text-in-image (Hebrew), packshots, storyboards grids, photo enhancement/upscale prompts, Gems for repeatable image workflows. Use whenever generating, editing, restoring or batch-producing images (תמונה, עריכת תמונה, שיפור תמונה, packshot, סטוריבורד).
---

# Image generation playbook

For *conceptual* directions (xray, blueprint, infographics) use `visual-codes`. This skill is the technique layer.

## Prompt anatomy
`subject + composition/framing + aspect ratio + lighting/mood + style/lens + exact text + exclusions`
- Write prompts in **English** (more precise), keep the target Hebrew strings verbatim in quotes.
- Aspect ratio explicitly in every prompt (1:1, 9:16, 16:9). Long product images can flip the frame ratio.
- Lighting vocabulary: soft top light, sharp light from above, soft shadow underneath, golden hour, cinematic.
- Exclusions stated explicitly: "no logo, no text, no captions, no watermark, no models, no overlay graphics".
- Tell the model which tool the prompt is for when another LLM drafts it.

## Editing discipline
- **Break complex edits into steps** (background -> lighting -> text), one action per step.
- Start from a raw, well-shot source (natural light); tools cannot rescue a bad source.
- Background swap, single-item recolor, wardrobe change (preserve face/hair/skin/body), multi-image composition (merge >10 inputs into one board in Canva/Figma first), 2D floor plan -> 3D isometric (keep walls/dimensions), old photo restoration/upscale.
- After ~6-7 edits quality decays: open a new chat, upload the latest image, continue.
- Beware **reference bleed**: mark references "style reference only, do not copy elements" or remove from knowledge.

## Consistency
- 3-4 photos of a product from different angles; 2-3 photos of a person; "keep face, hair, features unchanged".
- Brand rules in a reusable assistant: knowledge = brand doc (colours, fonts, style), instructions = hex colours, font class, style.
- Repeat invariant details in each prompt; derive sets from one master image.

## Text in images
- Put text in quotes with placement and font class; verify Hebrew letter-by-letter (RTL, no mirror).
- Best practice: generate **without text** and add typography as a vector/HTML/Canva layer.
- Different tools differ in Hebrew quality (some GPT image models are strong with Hebrew text and complex scenes) - test.
- Free tiers may add watermarks: use an API/studio tier if a clean file is needed.

## Reusable "Gem"/assistant recipes
- **Packshot assistant:** every upload returns centred product on white seamless background, soft top light, subtle shadow; refuses off-task requests.
- **Storyboard assistant:** one 9:16 image with a 3x3 grid of numbered frames for a ~10 s ad (hook, reveal, benefits, social proof, CTA), each with a one-line director note (action, camera, light, mood); feeds a video model.
- **Prompt-from-reference assistant:** analyses a reference image and returns a prompt that reproduces its style.

## Enhancement / upscale prompt structure (portrait or product)
1. Identity preservation (accurate geometry, no change to expression/face shape/background/objects) 2. Camera simulation (e.g. 85mm f/1.4, shallow depth of field, low ISO) 3. Lighting & colour (soft directional, warm highlights, cool shadows, neutral premium tone, match original light direction) 4. Skin/texture realism, subtle grain, no plastic smoothing 5. Output (4K, portrait crop) 6. Negatives (no background change, no face morph, no fake glow). Run 2-3 times; change one word (indoor vs studio) for variants. For products replace "facial geometry" with "preserve product shape and details". Resolution claims need independent verification.

## Product-photo variation protocol
One source photo, one command per attempt, same aspect ratio, new chat per variant, log exact prompt + model; judge **fidelity first** (shape/logo/colours), drama second; record a result only if it can be traced to its prompt.

## Cost & quality
Draft low-res, finalize high-res; generate prompts in an external LLM before spending credits; cheaper direct APIs exist for many models (check pricing); avoid trial-and-error inside premium UIs.

## QA
Outline/proportions preserved, logo/text/colours match, no invented features, plausible shadows/reflections, Hebrew correct, 9:16 (or intended ratio) kept, source + prompt archived.

See also: `ai-influencer-ugc-video`, `design-system-first`, `hebrew-rtl-output`, `verify-and-safety-gates`.
