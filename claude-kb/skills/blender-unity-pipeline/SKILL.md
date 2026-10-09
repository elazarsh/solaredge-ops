---
name: blender-unity-pipeline
description: Agent-driven 3D and game workflows - photos or product image to approximate Blender model, named cameras, gray composition renders, design pass, animation, simple browser games, Blender-to-Unity games (mechanics, materials, sound) with verification at each stage and honest limits of accuracy. Use for 3D mockups, apartment/room visualisation, product turntables, prototype games or any Blender/Unity task with a computer-use or coding agent (בלנדר, יוניטי, מודל תלת מימד, משחק).
---

# Blender / Unity pipeline (with an agent)

## Principles
Define the result (e.g. `.blend` + PNG renders), separate chat from action, check each stage before the next, make focused corrections ("the handlebar hides the road"), start small (one can, one room, three objects), keep originals, version every save, limit app permissions (computer-use only for needed apps; written scope is no substitute for system permissions).

## Computer-use readiness
Enable the capability in the workspace, grant OS permissions (screen recording, accessibility on macOS), close unrelated windows/passwords, test with a trivial app first (calculator 125x8: must really open the app and show 1000 on screen).

## Pipeline A - photos to room/apartment mock-up
1. Source: overlapping photos of the same space, no people/personal info, real dimensions with units if available, named by angle.
2. Blender model: approximate, named objects (walls, floor, windows, kitchen, furniture), assumptions stated; save `.blend` + two check renders (overview + eye-level). **Dimensions from photos are not for ordering/construction.**
3. Named cameras for a sequence; gray renders first to validate composition; geometry fixed across shots.
4. Design pass: gray render (angle) + original photo (colours/materials); keep angle, add only verifiable features, no invented furniture/people; output separate from original.
5. Video: animate chosen images with a video tool; ask tool/terms/cost for one test clip first; inspect for distortion/shape change/jumps. Illustrative mock-up, not a faithful record; if accuracy matters animate the original photos.

## Pipeline B - product to 3D
Clear image with simple shape -> approximate model with separate editable parts (body, lid, details), simple camera + studio light -> `.blend` + PNG -> check silhouette (height, lid, proportion) before colour/details -> three cameras (front, three-quarter left, elevated), same model/lighting -> show raw renders then processed versions, labelled. Image post-processing changes pixels, not materials: for angle-independent materials edit materials/textures in the scene and re-render. Check logos/text/shape against the original for branded goods.

## Pipeline C - games
- First a simplest playable browser version (arrow keys, collect 3 items, counter, finish message, restart). Test: collect all, counter updates, finish shows, restart resets, nothing reachable outside play area.
- 3D upgrade: Blender creates assets; Unity assembles (install Unity Hub + required Editor; check licence eligibility). Order: **mechanics -> materials/textures -> sound**; verify in the running game, not only Blender.
- Racing-game lessons: cockpit steering wheel blocking road (fix camera), finished rival blocking finish line, engine sound tuning, reversing near start must not count as a lap; keep a working version before large changes; one fix at a time.
- Separate automatic checks (file exists) from manual play-through checks.

## Blender sanity prompts
Base scene: product + separate parts + camera + lighting, versioned saves, preview render, report tested/untested. Fix-up: one defined change set, new version, compare old/new image. Animation: 5-second single rotation, fixed camera/light, check framing and smooth start. Status/recovery: what exists, what failed, smallest fix.

## Costs
Blender is free/open source; subscriptions, video generation, API use are separate. Test one small task and check usage meter; ask the agent to stop for review before large batches. Local tasks need the computer on.

See also: `agentic-build-discipline`, `verify-and-safety-gates`.
