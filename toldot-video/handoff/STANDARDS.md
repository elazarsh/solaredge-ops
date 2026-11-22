# STANDARDS — the quality bar for the art (what "good" means here)

The art is judged by these rules. They come from our video skills (`.claude/skills/keyframe-images`, `video-with-claude`) and from lessons of previous films.

## Hard fails (any one = the image is rejected)
1. **A face** of any kind: eyes, nose, mouth, face profile, or dots that read as eyes. People appear only from above, from behind, as shadow/silhouette, or as hands.
2. **Any text, letters, numerals or signatures** inside the image (Hebrew text drawn by image models is unreliable; all text is added in code later).
3. **A weapon or violence shown** (no bow, sword, blood, bodies, fighters). The black fist and its shadow are enough.
4. **Flags, logos, real people, organizations.**
5. **Wrong format:** not 9:16 vertical (2:3 is accepted only with the subject kept inside the central 80% of the width).

## Style lock
- Paste `handoff/style_block.txt` **verbatim** at the start of every prompt (`STYLE + Scene: ...`), prompts in English.
- The first approved image (T1) becomes the **style reference**: attach it (or describe it identically) to every later generation.
- One style for the whole film: layered cut/torn paper, riso print, flat spot colors, halftone, misregistration, paper grain. Not photographic, not 3D, no generic AI gradients/bokeh.

## Character and motif consistency
- Fixed signatures: Isaac cream + wool mantle + staff; Rebecca pink + long veil; Esau orange + hunter's fur-trimmed cloak + broad shoulders (no weapon); Jacob blue + slim; the dissenting brother green; Laban = only a heavy hand with a ring + ledger (cold green-grey). Crown = gold (healthy power). Fist = ink black + red (violent power).
- Three recurring motifs must look the same every time: (1) the crown's shadow = a fist (and at the end the same shadow = an open hand); (2) the thin gold ring around the round table; (3) the two different chairs (outside the ring / the green brother's chair).
- Keep reference sheets in `art/refs/` and reuse them. Do not drift between images.

## Designed for animation (so Claude can bring it to life)
- **Plates:** one scene, clear layers (background / main shapes / foreground), calm areas (top 10%, bottom 15%), main subject inside the central 70% of the height.
- **Sprites:** one object per file or a clean sheet; flat bright green background (#00FF00-ish), generous margin, no shadow or gradient on the green, no green inside the object. Needed: crown, fist, open hand, Isaac's hand with staff, veil, round table from above, chair, coins, loaf, ledger, ring (gold, broken and intact), crown-shadow fist, crown-shadow open hand.
- **Transition objects** (a flame, loaf, ink drop, circle of light, tent flap, open hand, ledger page) must be clear, large and isolated.
- **Variety:** at least 3 framings across the set (top-down, close-up of hands, wide landscape). Avoid a series of near-identical images: the film must not feel like a slideshow.

## Process
- Generate **one image first**, check it, show it, then continue. Batches of 3–4 only after approval.
- Save each image immediately. At most **one** retry per image; if still weak, mark it `weak` honestly in the manifest and move on.
- Record the exact prompt, tool/model and QA result for every image in `manifest.json`.
- Run `python3 toldot-video/art/validate_art.py` before each commit.
- Honesty: report what is weak, what was not checked, how many images were generated (cost). Never claim a check you did not do.

## Sensitive beats (handle with restraint)
- *Hand on a door handle from inside* (holiday-morning memory): dark room, only the wrist and hand, a thin line of pale light under the door. No people, no faces, no blood.
- *Pen over a blank signature line*: only a hand and a hanging ink drop. Nothing else.
- Esau's threat is shown only by the black fist/shadow breaking the gold ring, never by a weapon or a victim.

## What happens to your files next (so you deliver what is usable)
Claude removes the green from sprites, layers them over plates, adds stop-motion jitter, grain, halftone, torn-paper/ink transitions, voice-line animation and all Hebrew typography in code, then renders a 9:16 MP4. Anything that is not clean, isolated or consistent costs us time later.
