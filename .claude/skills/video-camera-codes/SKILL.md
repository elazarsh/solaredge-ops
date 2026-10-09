---
name: video-camera-codes
description: Direct AI video generation (image-to-video) with named camera-movement codes - dolly, pan, tilt, tracking, orbit, zoom, whip pan, FPV, handheld, snorricam, bullet time, speed ramp. Use when creating a short video clip from an image, planning shots for a product/brand video, writing video prompts for Higgsfield, Gemini/Veo, Kling, Seedance, Runway, or fixing a bad camera move (סרטון, תנועת מצלמה, קוד וידאו).
---

# Video camera codes

100 named movements in 10 families. A code like `/Slow Dolly In` is a natural-language request, not a guaranteed command; results vary per attempt and per model.

## Core rules

1. **One subject action + one camera move per shot.** Complex = several tries or external editing.
2. **Start with a clear start image** (sharp, full subject, uncluttered).
3. **Describe the physical motion**, say what stays still ("the product remains stationary, the camera moves around it").
4. **Say "no zoom"** when you mean a dolly (camera physically moves).
5. **Specify start framing and end framing.**
6. **Lock identity & geometry:** "keep subject identity and geometry consistent, one continuous shot".
7. **Generate shots, time them in the editor.** Speed ramps, transitions and cuts belong to editing; do not expect the generator to time them.
8. Start simple (Slow Dolly In) before exotic moves (Dolly Zoom, Double Dolly).

## Expanded prompt template

```
Subject: ...            Setting: ...
Camera movement: [one code]
Direction and speed: ...
Subject action: ... (or "remains still")
Start framing: ...      End framing: ...
Constraints: keep subject identity and geometry consistent; one continuous shot; lighting unchanged.
```

## Pick by goal

| Goal | Move |
|---|---|
| Emphasise a product | Slow Dolly In / Slow Product Orbit |
| Reveal a shop/room/landscape | Dolly-Out Reveal / Pan to Reveal / Rising Reveal |
| Follow a person working | Side Tracking / Subtle Handheld |
| Join two shots | Whip Pan Transition (match rotation direction in both shots; join in editor) |
| Peak moment | Fast-Slow-Fast Ramp (timed in editor) |
| Unusual feeling | Dolly Zoom / Double Dolly (only after a simple move works) |
| Energy / sport | FPV Chase, Handheld Run, Whip Pan |

## Troubleshooting phrases

- Product spins instead of camera -> "product stationary, camera moves around it".
- Zoom instead of dolly -> "camera physically moves forward, no zoom".
- Slides sideways instead of pan -> "camera rotates from a fixed position".
- Character morphs -> simplify path, reduce orbit angle, use a clearer opening image.
- Too many moves -> one subject action, one camera move.
- Timing wrong -> generate a clean shot, retime in an editor.

## Practice / test protocol

One product, one image, three versions: Slow Dolly In, Quarter Orbit, Dolly-Out Reveal. Keep light, setting, description identical. Judge: identity consistent? instruction followed? does the move help understand the product?

## Cost discipline (when using paid generators)

Ask for model, credit cost and length before generating; test ONE shot first; do not resubmit while a job may still be running; keep text out of generated video (add titles as a graphics layer); save the approved reference image under a versioned name.

## Workflows by tool (high-level)

- **Higgsfield via ChatGPT plugin:** select the plugin, attach photo, send `/Movement Name`; confirm credit cost; watch the final output (progress messages are not results).
- **Gemini video:** pick video creation, attach the reference image, paste the code; if you get text back, rephrase as a full sentence ("create a video from the attached image with an Infinite Zoom effect").
- **Motion transfer (Higgsfield Genjutsu):** motion comes from a 4-30 s clean reference clip, look/identity from images + prompt. Give each image an explicit role; hero appears once; keep camera movement and original framing; ban text/logos/extra limbs.

Full list of 100 codes: `references/catalog.md`.
