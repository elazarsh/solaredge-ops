---
name: hebrew-rtl-output
description: Rules and QA for producing Hebrew (right-to-left) output in any medium - web pages, slides, documents, charts, images, video captions, narration/TTS and emails - including mixed Hebrew/English/numbers, fonts, mirrored layouts and Israeli context. Use whenever the deliverable is in Hebrew or bilingual (עברית, RTL, כתוביות, גופן, מיושר לימין).
---

# Hebrew / RTL output

## Web
- `<html lang="he" dir="rtl">`; use logical CSS properties (`margin-inline-start`, `text-align: start`, `padding-inline`). Mirror icons with direction (arrows, chevrons, progress bars), not logos or media controls.
- Hebrew-capable font loaded explicitly (web-font), weights bundled; test fallbacks.
- Mixed content: wrap English/numbers/URLs/emails in `<bdi>` or `dir="ltr"` spans where punctuation gets scrambled. Test phone numbers, prices (₪), percentages, dates, parentheses, quotes.
- Forms: labels right, inputs `dir` appropriate (email/phone LTR), validation text in Hebrew.
- Check at 360/390/768/1440 widths, long names/addresses, enlarged text.
- Real accessibility testing (keyboard, focus, contrast) - not overlays.

## Slides & documents
- Set presentation/document language and RTL paragraph direction on every text box/table cell; right-align bullets and numbering; reverse table column order logic; charts: axis labels, legend, data-label order checked.
- Page numbers and headers mirrored. Exports (PDF/PPTX) re-checked after conversion.
- Avoid fonts that lack Hebrew glyphs (falls back to ugly substitute).

## Images (AI-generated)
- Put the exact Hebrew string in quotes in the prompt; specify font style (bold sans-serif) and position; consider English prompt wording but verbatim Hebrew text; request "RTL, not mirrored".
- Expect garbled Hebrew: verify letter by letter; prefer adding text as a separate design layer (Canva/Figma/HTML) over baking into the image. Tools differ in Hebrew text quality - test.
- Add exclusions: "no extra text, no logos, no captions, no watermarks".

## Video
- Hebrew-capable font bundled in the render; set RTL on text containers; test mixed Hebrew/English/numbers.
- Narration: TTS with good Hebrew; fix mispronunciations with niqqud/spelling or shorter sentences; transcribe the *final* audio for word timestamps and check names/numbers/English terms.
- Captions synced to speech; avatar tools may mishandle Hebrew text - test first.
- Vertical (9:16): bigger text, stack elements.

## Writing quality
Plain modern Hebrew; avoid translated-from-English constructions and buzzwords (see `human-writing-hebrew`); consistent gender forms and terminology; Hebrew and Latin punctuation not mixed carelessly.

## Israel-specific
Currency ₪ placement, date format DD/MM/YYYY, week starts Sunday, time zone `Asia/Jerusalem` for scheduled tasks, accessibility and privacy obligations for sites - verify with official sources/professional.

## QA checklist
- Every text container RTL? Numbers/English readable and in correct order?
- Fonts present for every glyph in every exported format?
- No mirrored logos/images; no cut-off text; no overlapping when text grows.
- Spell-check the Hebrew inside images/video frames visually.
