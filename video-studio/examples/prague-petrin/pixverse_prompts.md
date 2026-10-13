# PixVerse prompts: clips 1, 2, 5

Only the three clips that are fantasy or filler are generated. Scenes 3, 4, 6 use the real photo (done in
`build_animatic.py`) so the funicular's structure is never altered, as the brief demands.

Common settings: model `v6`, aspect `9:16`, **no audio** (we use our own sound so the music cut and
the record scratch land exactly), seed fixed for repeatability. Generate 5 s and trim to the scene length.
No Hebrew or any text inside generated frames: text is added afterwards in code.

## Cost (docs prices checked 2026-10-13, approximate; re-check the pricing page)

| Plan | Per clip | 3 clips |
|---|---|---|
| draft: V6, 540p, 5 s | 35 credits (~$0.16) | ~105 credits (~$0.47) |
| better: V6, 720p, 5 s | 45 credits (~$0.20) | ~135 credits (~$0.60) |
| final: V6, 1080p, 5 s | 90 credits (~$0.40) | ~270 credits (~$1.20) |

Expect 2-3 attempts per clip; budget about 3x. Free plan allows 3 generations at once.

## Clip 1: the big promise (scene 1, 0-4 s)

```
Epic cinematic aerial shot, fast sweeping drone fly-through between jagged snow-capped Alpine peaks and
enormous cloud-filled abysses. Thin steel cables with red cable cars hanging hundreds of metres above the
valley floor, swaying slightly in the wind. Cold blue-teal colour grade, hard low sun breaking through
dramatic clouds, high-contrast blockbuster trailer look. Rapid camera moves: a sharp bank, a push through a
gap between two peaks, a quick tilt down into the void. Sense of danger and enormous height.
Avoid: text, logos, watermark, close-up faces, warped geometry, slow motion.
```
Save the prompt above as `clip1.txt`, then (remove `--dry-run` only after approval):
`python3 ../../skills/pixverse-generate/scripts/pixverse.py text --model v6 --aspect 9:16 --duration 5 --quality 540p --seed 11 --prompt "$(cat clip1.txt)" --out clip1.mp4 --dry-run`

## Clip 2: tension peaks (scene 2, 4-8 s) - use `--multi-clip`

```
Rapid-fire blockbuster action montage in saturated orange-red tones: a roller coaster tipping over the first
steep drop, a row of passengers with arms raised screaming with excitement (generic fictional people, no
close-up identifiable faces), a red cable car swinging above a gorge, a whip-zoom toward the edge of a drop,
camera shake, white flashes between shots, motion blur streaks. Pure adrenaline, trailer energy.
Avoid: text, logos, watermark, gore, injury, real brands.
```

## Clip 5: the survivors (scene 5, 17-21 s)

```
A cheerful toddler amusement park. A small bright red toy train with two little wagons races along a tiny
circular track at a comically exaggerated speed, wobbling, puffing cartoon steam. In the front wagon sits a calm
toddler with a pacifier, completely relaxed, hair slightly blown back, looking at the camera with total
serenity. Pastel colours, sunny, playground background with balloons. Low static camera with one quick pan to
follow the train.
Avoid: text, logos, watermark, distress, anything unsafe, realistic faces in close-up.
```
Note: generated children and moderation. If PixVerse blocks the clip (status 7 / code 500063), rephrase
("a stuffed-toy passenger", or "a smiling toy bear in the wagon") rather than retry the same prompt.

## Order of work

1. Approve the cost line above (ask the user; the script refuses over 300 credits by default).
2. Generate the three drafts in parallel (background shells), review each with `video-qa`.
3. Replace the placeholder generators in `build_animatic.py` (`scene1`, `scene2`, `scene5`) with
   `ffmpeg`-trimmed clips; keep captions, subtitles, countdown and the BOOM flash in code.
4. Add the narrator, final mix at about -14 LUFS, final QA, export.
