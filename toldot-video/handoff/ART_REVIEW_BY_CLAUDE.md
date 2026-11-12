# Independent review of the art (Claude) — after PR #21 (`gpt/art`)

Reviewed with my own eyes: all 6 contact sheets, plus full-size P14, P21, P27, and keyed sprites over a dark background. Strict validator passes (54 images).

## Verdict: usable. Style is consistent and strong.
- **Hard rules:** no faces, no text/numerals, no weapons seen in the approved set (spade/broom/staff/reed are tools, not weapons).
- **Motifs:** ring (S04/S13/S18), crown-shadow fist (S14) → open hand (S15), two different chairs (orange S05 outside the ring, green S11 inside; blue S25 for Jacob) are all present and consistent (see P14, P27).
- **Variety:** top-down, close hands, wide landscapes, symbolic scenes: it will not read as a slideshow.

## Weak or to watch (honest list)
1. **P02, P26** weak (GPT marked them). Not used; replaced by layered sprites per `assembly_map.csv`.
2. **S16 (Isaac overhead), S17 (Rebecca overhead)**: abstract soft shapes (a cream "pile" with a staff, a pink hood). Readable by color but odd as figures. Consider regenerating or using P09/P10/S10/S12 instead.
3. **P03**: the fist is a paper object with a crown above it, not a shadow. Use S14 as the projected shadow (GPT notes this too).
4. **P14**: heads are black circles (other plates use body-colored heads). Minor inconsistency.
5. **P20**: tiny house in a large empty field (subject small). Usable with a zoom/crop.
6. **P01 / beat 67**: the "same direction" pose was not generated; requires masking/staging.
7. **Beat 19** (long dining table) and the final parental handoff are multi-layer code compositions, not single plates.
8. **Not generated:** the 6 test images T1–T6 (deferred by the handoff), so the old test kit has no committed output.
9. **Repo size:** the art folder is ~139 MB (many originals in `refs/`). Consider moving originals out of git later.

## Keying (green removal): works
`toldot-video/build/key_sprites.py` converts every sprite to a transparent PNG (`build/sprites_rgba/`, gitignored, regenerate with the script). Checked over a dark background: crown, hands, fists, chairs (including the dark-green S11), the broken ring (S13) and the veil are clean; no green fringe visible at normal size.

## Next (Claude)
Build the first minute from `assembly_map.csv` + `beats.csv` (HTML/WebGL, free tools): intro (3 s) + chapter 1, render a 9:16 preview, then ask the user before continuing.
