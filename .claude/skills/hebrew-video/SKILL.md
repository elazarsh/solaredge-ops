---
name: hebrew-video
description: Rules for any Hebrew video, ad, motion graphic or caption work in this repo — RTL layout in HyperFrames/Remotion, bundled Hebrew fonts and pairings, typography sizes for phones, bidi with numbers/English/phone numbers, caption line-breaking, gendered address (לשון פנייה), fully vocalized (niqqud) text for Gemini TTS, and Hebrew-specific QA. Load it together with /hyperframes, /ad-creative, /media-use or Remotion whenever on-screen text or voiceover is in Hebrew.
---

# Hebrew video rules

## Layout / RTL
- **HyperFrames:** never put `dir="rtl"` on `<html>` (renders black). Put `direction: rtl;
  unicode-bidi: isolate;` on each text element or a text wrapper.
- **Remotion:** `style={{direction: 'rtl'}}` on text containers; the canvas stays LTR.
- Motion reads right→left: entrances slide in from the right, lists stagger right→left,
  progress bars fill right→left, "next" arrows point left.
- Text alignment: right or centered. Never left-aligned Hebrew.

## Fonts (local, in `video-studio/remotion/public/fonts`; Google Fonts is blocked at render time)
| Role | Young / warm | Clean / pro | Bold statement |
|---|---|---|---|
| Headline | Rubik 800–900, Fredoka (Latin+Hebrew rounded) | Heebo 800 | Secular One, Karantina Bold, Suez One |
| Body / captions | Heebo 500–700 | Assistant 600 | Heebo 700 |
| Soft / kids | Varela Round | | |
Latin UI fonts in English prompts (Geist, Inter, SF) have **no Hebrew** — swap to Heebo (UI) or Rubik.
Max 2 families per ad. Hebrew needs ~10% larger size than Latin for the same legibility; add
word spacing if needed, **never letter-spacing** (breaks letter shapes).

Phone sizes on 1080×1920: hook 110–160 px, headlines 80–110 px, captions 56–72 px (weight ≥ 600),
small legal note ≥ 32 px. Use a text shadow or a solid plate on photos.

## Bidi: numbers, English, phones, punctuation
- Wrap LTR runs in their own span with `direction: ltr; unicode-bidi: isolate;` — phone numbers,
  URLs, @handles, English brand names, prices with ₪.
- Phone numbers: write `050-123-4567` inside an LTR-isolated span; check it isn't reversed.
- Punctuation at line end (?, !, .) belongs on the **left** end visually — if it shows on the
  right, the element is missing `direction: rtl`.
- Hebrew quotes: use ״ ׳ or regular " with `rtl`; gershayim in acronyms (צה״ל, ת״א).
- Hyphen/maqaf: use regular hyphen in UI text; avoid splitting words across lines.

## Captions
- 1–2 lines, 2–5 words per card, ≤ 32 characters per line, min 1 s on screen.
- Break at phrase boundaries (never between a preposition-prefix word and its noun, or inside a
  name/number). Keep the caption track on one fixed position above the Reels bottom UI (y ≈ 1150–1250).
- Captions come from the **plain** (unvocalized) script; timings from the VO file.

## Language
- Decide the address form up front: at (את), ata (אתה), atem/aten, or neutral. Be consistent
  in every line: verbs, possessives (בשבילך vs בשבילךְ in niqqud), imperatives (שלחי / שלח / שלחו).
- **Job ads** must address all genders (see `/ad-creative` → `references/legal-il.md`).
- Prefer everyday Hebrew over formal register; read every line aloud.

## Voiceover (Gemini TTS)
- Text sent to Gemini **must be fully vocalized** — the engine rejects unpointed Hebrew.
  Full rules: `/media-use` → `audio/references/tts.md` → "Hebrew narration".
- Keep two versions of the script: `script.plain` (captions, on-screen) and vocalized `text` in
  `audio_request.json`. Change both together.
- Recommended young female voices: Leda (youthful), Aoede (breezy), Sulafat (warm). Male: Puck
  (upbeat), Achird (friendly). Put direction in `style`, not in text.

## Hebrew QA (add to the normal review)
- Look at a contact sheet (`video-studio/tools/contact-sheet.sh`) for: reversed punctuation,
  reversed numbers, missing final letters (ך ם ן ף ץ), broken niqqud rendering, cut-off lines.
- Listen for mispronounced words → fix niqqud on that word only and regenerate that line.
