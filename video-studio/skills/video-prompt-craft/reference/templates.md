# Prompt templates

All templates are model-agnostic. Replace `[...]`. Keep in English when sending to a model.

## 1. General clip (seven parts)

```
[SHOT TYPE] of [SUBJECT in detail]. [ACTION as an ordered sequence; use "before" for order].
Setting: [PLACE, TIME OF DAY, WEATHER, props]. Style: [LOOK], [LIGHT], [COLOUR WORLD].
Camera: [ONE move, e.g. slow push-in]. Audio: [AMBIENCE / EFFECTS / MUSIC / SPEECH].
Avoid: text, logos, watermark, extra people, morphing, camera shake.
```

## 2. Mascot ad, step 1: concepts

```
I want a 10-second animated ad for [PRODUCT/BUSINESS]. Give me 5 possible directions.
```
Or:
```
Write one direction built on a cute recurring mascot who embodies the solution to [PROBLEM].
Break it into 5 short scenes: 1) frustrated customer with the problem, 2) product/mascot activated,
3) mascot handles the problem, 4) customer relieved and smiling, 5) clean end card with a call to action.
Describe each scene briefly and very visually.
```

## 3. Mascot ad, step 2: character, then scenes

```
Based on the chosen concept, write a detailed English prompt to create the base mascot: appearance,
visual style (e.g. 3D Pixar-like / 2D animation), facial expression, key colours.
```
```
Attached is the base mascot. Write an image prompt for each of the 5 scenes with this exact mascot.
Keep the character identical across scenes. Scenes: [PASTE].
```
Save images in order 1..5. Then:
```
Write one precise video prompt that animates these images in order as a single 10-second ad:
[PASTE CONCEPT]. Keep the character identical; smooth transitions between scenes.
```

## 4. Orbit-to-street descent (one take, 12 s, 9:16)

Needs one still photo of the place, shot from across the street, head-on, ground to roofline visible
with context (pavement, kerb, parked car, neighbouring facades), natural late-afternoon light.

```
One continuous unbroken shot, vertical 9:16, 12 seconds, photorealistic, no cuts.
[0-3s] Low Earth orbit. The curved blue limb of the planet fills the lower frame, hard side light, thin
white cloud bands, black space and stars above. The camera begins to accelerate straight down.
[3-6s] The descent speeds up. The horizon flattens and leaves the frame. The camera punches through the
upper atmosphere and a layer of broken white cloud, wisps streaking past the lens.
[6-9s] Below the cloud the ground resolves: coastline, a city grid, main roads, then one street. The camera
keeps falling and tilts from top-down to eye level, motion blur at the frame edges.
[9-12s] The fall decelerates smoothly and settles on an eye-level shot of the exact place in the attached
image, head-on, matching its light, time of day and weather. It holds with a faint handheld drift.
Camera: one single accelerating-then-decelerating dolly-in. Do NOT cut, do NOT cross-dissolve, do NOT fade,
do NOT jump to a stock shot of Earth, do NOT change scene.
Audio: silence and a low space drone, rising wind and a deep swell during the descent, then quiet street ambience.
Avoid: text, labels, borders, map graphics, HUD, watermarks, lens flares over the subject, people entering at the end.
```
Reverse (street to orbit): same structure, start on the attached image, lift and tilt to top-down, the
subject shrinks to a dot, city, coastline, clouds, atmosphere, settle on the whole planet in stars; same bans
plus "do NOT return to the subject".

Adapting to a region: let the model look at the photo first and rewrite each altitude layer to match the
architecture, vegetation and vehicles, while keeping the timestamps, the single take, the speed profile and
the ban on text and map graphics.

## 5. Motion-transfer character swap, step 1: the new first frame

```
The attached image is the first frame of a video of me talking to the camera. Recreate this exact frame and
change only the person.
Keep 100% identical: camera position, framing and crop, lens and perspective, the room, every background
object, the chair, light sources and direction, shadows, colour grading, white balance.
Keep the exact pose: head tilt, shoulder line, both arms and hands, finger positions, mouth shape, eye
direction. The new character occupies the same space as I do.
Replace me with: [CHARACTER: age, face, hair, clothes]  (the user themself, a changed version of the user, or a
fully invented original character - never a real person who is not the user).
Photorealistic, natural skin texture, correct contact shadows on the chair. Same resolution and aspect ratio.
No added text, logos or extra people. Change nothing that is not the person.
```
Variants: **age change** (keep face identity, add realistic ageing, keep clothes), **outfit change** (keep
face and hair, hands bare and fully visible), **3D animated original character** with five-fingered hands
while the room stays photoreal. Step 2: feed that frame plus the source video into a motion-transfer tool
(for PixVerse: Motion Control / Mimic) so the new character performs the user's own movement.

## 6. Edit-by-conversation requests (one change per turn)

- "Change only the shirt to a tailored black suit; it should move naturally with my arms."
- "Switch to a close-up on the face; keep the lighting and the background."
- "Make the whole clip look like stop-motion clay animation; keep the motion."
- Remove an object / swap a prop / change the time of day - always add "keep everything else identical".

## 7. Negative-prompt starter

`text, subtitles, logo, watermark, extra fingers, extra people, warped face, morphing, flicker, camera shake, blur`
