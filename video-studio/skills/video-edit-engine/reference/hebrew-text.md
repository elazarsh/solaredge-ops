# Hebrew (and other RTL) text in video

## Why it breaks

- OpenCV `cv2.putText` has no shaping or bidi support: Hebrew appears mirrored or as boxes.
- Pillow's basic layout engine does not reorder mixed Hebrew/English; the default engine can render the
  whole string left-to-right, which reverses Hebrew words.
- Video models (PixVerse, Veo, Kling...) cannot be trusted to spell Hebrew inside a generated frame.

## What works

1. Pillow with the **RAQM** layout engine (libraqm + fribidi + harfbuzz).
   `python3 -c "from PIL import features; print(features.check('raqm'))"` must print `True`.
2. A **font file that contains Hebrew**, passed explicitly (Heebo, Rubik, Assistant, Noto Sans Hebrew,
   Frank Ruhl Libre, David Libre). Without a Hebrew font the glyphs fall back to boxes.
3. `ImageDraw.text(..., direction="rtl", language="he")` for Hebrew lines; `scripts/hebrew_text.py`
   wraps this and fails loudly if RAQM is missing.
4. Word wrap in **logical** order (first word first), then draw each line with `direction="rtl"`.
5. Captions: build an RGBA image per caption or per word-state, composite onto the frame with
   `alpha_composite`. For word-by-word highlight, render the line once, then re-render only the
   highlighted word in the accent colour at the same x-position (measure with `font.getlength`).

## English inside Hebrew

- RAQM keeps a Latin run as one left-to-right unit inside an RTL line. Check on a frame: brand names,
  URLs and product names must read correctly.
- If a name is split across a line break it will look wrong; keep it together (use a no-break space
  U+00A0 between its words and wrap again).
- Trailing punctuation: a final period or question mark can jump to the wrong end when the line ends
  in Latin text. Add a right-to-left mark (U+200F) after the Latin run if it does.

## Numbers, times, prices, phone numbers

- `19:00-08:00`, `₪149`, `054-123-4567` are the usual victims. Check each on a frame. Put
  U+200E (LRM) around ranges and phone numbers if the order is wrong.
- Currency: write the symbol the way the audience reads it (₪ before or after the number: be
  consistent with the user's usual copy).

## Transcription

- Hebrew speech: use an ivrit.ai Whisper model; it is much more accurate in Hebrew than the general
  model. Keep word-level timestamps.
- Always show the transcript for approval before rendering. Names and English terms need hand fixes.

## Checks (put these in every QA pass)

- No mirrored letters; English sequences intact; numbers in order.
- Caption does not cover the mouth; two lines maximum; safe zone respected on 9:16.
- Final-form letters (ם ן ץ ף ך) render correctly; nikud is off unless requested.
