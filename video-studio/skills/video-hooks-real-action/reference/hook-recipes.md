# Hook recipes

Adapted from Brain's "5 crazy hooks" guide (brainai.co.il/guides/crazy-ai-hooks), rewritten as reusable templates.

Each recipe is a prompt skeleton to give the build step (you, or a subagent). Replace
`[...]`. Keep the structure: **filename -> what was filmed -> numbered build steps -> output ->
"show me N key frames before finishing".** Output is always 1080x1920 unless told otherwise.

## Common rules

- The element is drawn by us, in the user's language, in an app-like style (rounded white card, small
  profile circle, grey input field) - not a real screenshot and not a real logo.
- Width about 60-65% of the frame, centred on the empty point, with a strip of wall between head and element.
- Track frame by frame; save the track to disk so reruns are consistent.
- Depth order: hand/prop in front of the element, element in front of the wall and of any bright object
  on the wall (lamp, window) that must not be covered wrongly.
- Slow and partial beats instant and total.

## 1. Burn (lighter)

Filmed: `burn.mp4`, creator lights a lighter under an empty point above the head.
1. Question-sticker card: profile circle on top, title `[TITLE]`, grey field `[PLACEHOLDER]`; bottom edge just above the flame tip, not covering it.
2. Track the lighter; find the frame where the flame touches the card's bottom.
3. From contact: slow, partial burn bottom-to-top - real flame tongues, a jagged charred edge that advances, sparks, thin smoke. Burn about half the card by the cut, never all of it.
4. Hand and lighter always in front of the card; card in front of the wall; warm flickering light on the face while it burns.
5. Output `burn_fx.mp4`. Show 4 frames: before ignition, contact, mid-burn, end.

## 2. Crumple (paper card)

Filmed: `crumple.mp4`, creator holds a blank white card overhead with both hands, crumples it into a ball, throws it.
1. Reply-bubble: profile circle, small username, `[TEXT]`.
2. Find the card's four corners in every frame and print the bubble with perspective so it moves with the paper.
3. While crumpling, **do not fake wrinkles**: reuse the real paper's shading and folds so they run across the text too; fingers stay above the print.
4. When it becomes a ball, the print is swallowed by its shadow; the throw stays as filmed.
5. Output `crumple_fx.mp4`. Show 4 frames: flat, start of crumple, ball, throw.

## 3. Wipe (spray and cloth)

Filmed: `wipe.mp4`, spray twice at an empty point, then wipe there with a cloth.
1. Notification banner dropping from the top: icon, app name, `[TEXT]`; sharp, centred, about 65% width; must not touch bright background objects.
2. Detect spray frames from the bottle's motion. At each spray: a thin mist cloud that disperses, droplets that stay on the banner and slide a little.
3. Track the cloth. Erase the banner and droplets **only where the cloth has passed**, in strokes. If a corner was never reached it stays. No fade; that is what makes it believable.
4. Hand, bottle and cloth in front of the banner; banner in front of the wall.
5. Output `wipe_fx.mp4`. Show 4 frames: after spray 1, after spray 2, mid-wipe, clean.

## 4. Pop (pin) - bonus

Filmed: `pop.mp4`, creator slowly brings a pin to an empty point and flinches.
1. AI-assistant chat bubble: white, black dot and small name at the top, `[TEXT]`.
2. Track the pin tip; find the exact frame it touches the bubble edge.
3. Two frames before contact the bubble trembles; at contact it shatters like thin plastic: shards fly out from the contact point, spin, fall with gravity, vanish.
4. Hand and pin in front of the bubble and shards.
5. Output `pop_fx.mp4`. Show 4 frames: approach, contact, burst, after.

## 5. Follow press (finger) - bonus

Filmed: `follow.mp4`, creator raises a finger and presses an empty point as if pressing a lift button.
1. Blue "Follow" button in the app's shape and font, about 35% width, exactly where the fingertip will press.
2. Track the fingertip; the **press frame** is when it stops and starts to return.
3. On press: button sinks, shrinks slightly, inner shadow; next frame it becomes a grey "Following" button and springs back with a small bounce.
4. Finger in front of the button; button in front of the wall.
5. Output `follow_fx.mp4`. Show 3 frames: before, press, "Following".

## 6. Ending: code word in the air (marker)

Filmed: `cta.mp4`, creator moves a closed marker as if writing on invisible glass, right to left; code word `[CODE WORD]`.
1. Track the marker tip in every frame and keep its path.
2. Write the word in thick marker handwriting in `[COLOUR]` at marker height, about 70% of frame width.
3. Reveal letter by letter exactly as the tip passes each letter's position - never ahead of or behind the hand.
4. After the word completes, a soft fade-in of `[SECOND LINE]` below in white.
5. Hand and marker in front of the writing; keep the word on screen a full extra second.
6. Output `cta_fx.mp4`. Show 4 frames: start, middle of word 1, middle of word 2, end.

## 7. Sound

For each clip: a dry, tight sound that fits the material, on the exact frame of each event; motion
sounds start only when the motion happens (late beats early). See `video-edit-engine/reference/sound-design.md`.
Show a table "sound, time" and 3 frames with the sound marked before mixing.

## 8. Assembly (one reel)

Order: burn, crumple, wipe, ending (code word), then bonuses (pop, follow). Each hook 2.5-3.5 s; enter
just before the prop touches the element and leave right after the effect ends; the ending stays at least
2 s after the word is written. Corner counter 1/5...5/5 on the right middle edge, inside the safe zone.
2-3 frame white flash and whoosh+thud at each cut; light music under everything, ducking under effects.
Show one frame per clip and the cut times; render the final only after approval.
