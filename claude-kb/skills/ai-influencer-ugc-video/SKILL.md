---
name: ai-influencer-ugc-video
description: Pipeline for AI influencer / UGC-style product videos and viral short-form content - idea test, layered writing ("documents" method), master shot, consistent character, emotional set, product-in-hand compositing, first/last-frame animation (Flow/Veo, Kling, Seedance, HeyGen), Hebrew speech workarounds, clip chaining, CapCut finish, and video-editing-by-prompt (Omni). Use for UGC ads, AI presenters, serialized brand characters, TikTok/Reels content, or editing real footage with AI (משפיען AI, UGC, סרטון ויראלי, דמות עקבית, רילס).
---

# AI influencer / UGC / viral video

Start from a **human situation that is recognised in 3 seconds**, not from a tool. Quality of the first image, product image and last frame decides the video quality.

## A. Idea & writing track (human-led)
1. Pick a situation with real friction (money, time, relationships, work, kids, food, status).
2. **Idea diagnosis** (no script yet): familiar concept in first 3 s? clear emotion? real-life friction? strong first punchline? reason to rewatch?
3. **Nested documents ("babushka"):** personal free-write -> ideas doc -> one-line premise (compass) -> punchlines/moments/exaggerations -> logline (what happens after what) -> script (last) -> production appendix (assets to create/animate/record/edit).
4. Use AI for raw material (e.g. 100 concepts/sayings/awkward moments/visual images in the niche), but **write the final jokes yourself**. Avoid forced humor and cheap wordplay; prefer embarrassment, conflict, exaggeration.
5. Record the dialogue yourself for intonation/rhythm when possible; the performance matters more than the final voice.

## B. Production track
1. **Master shot** (9:16, cinematic, readable characters, no text/logos/watermark) defines the world; derive everything from it.
2. **15-angle breakdown** from the master shot: 5 emotional cinematic angles, 5 main-character sizes, 5 secondary character/object. Same light, wardrobe, perspective.
3. **Character:** photorealistic UGC selfie (lived-in, slightly imperfect background, not too beautiful, not studio). Repeat invariant details (same woman, outfit, room, light, phone-camera style, 9:16) in EVERY prompt.
4. **Emotional set:** neutral, angry, worried, sad, excited, confused, suspicious, embarrassed, deeply moved - change only expression/body language.
5. **Product in hand:** character image = identity reference, clean product image = product reference; natural grip, realistic proportions, preserved packaging, no overlays. Product inputs must be stills (pause a video frame, remove background). Non-existent product -> mock it up first.
6. **Animate with first + last frame** (not text-only prompts): describe the motion between frames; realistic hands; consistent camera/light/identity.
7. **Speech:** Veo speaks Hebrew but glitches -> retry; for clean Hebrew use ElevenLabs (request nikud for tricky names) + lip-sync (HeyGen), or record yourself. Keep on-screen Hebrew very short. Seedance produces gibberish Hebrew; has no negative prompts - write positively.
8. **Beyond 8 s:** chain clips - last frame of clip N = first frame of clip N+1, same voice/outfit/setting, "no camera jumps or identity change". Never one long generation.
9. **Edit in CapCut** (or code, see `code-driven-video`): trim weak parts, pace, punchline timing, repetition, subtitles, music, sound; add subtle background motion so only the lips aren't alive.
10. One change per step (pose OR product OR action). If the image tool drifts after ~6-7 edits or refuses: new chat, re-upload latest image, confirm the Pro/image mode.

## C. Editing real footage with prompts (Omni-style)
- Takes an existing video and modifies it: style, background, clothing, effects, avatar. Run one change per pass.
- Prompt skeleton: *keep person, camera angle, lighting, movement, lip-sync unchanged; change ONLY [object/area] from [time]; must be physically realistic; change nothing else.*
- Triggers: use a gesture (finger snap) as trigger for sequential edits. Drone flyover from a map screenshot with a marked route.
- Limits: ~8-10 s clips, many people/small details are hard, Hebrew in-video text is poor, identity/voice are near but not 100% faithful (may invent speech), outputs may carry a watermark, celebrity likeness restricted. First attempts rarely succeed - budget retries.
- Cost: prefer the cheaper "flash" tier for tests; test short clips; use rights-free source footage.

## D. Business uses
UGC product ads, AI presenter for a service, staff training clips, character explaining an app feature, A/B testing characters and messages, serialized brand stories without a shoot.

## E. Pitfalls
Opening tools before having an idea; blank-page scripts; over-perfect characters; skipping the master shot; one image per character; "make a video" without start/end frames; long Hebrew text; skipping manual editing; assuming one model fits all (test same storyboard on several); judging only first views (rewatch is the signal).

## F. Responsible use
Disclose AI where required; do not imitate real people/celebrities or use a real person's likeness without consent; do not invent customer testimonials; review `verify-and-safety-gates` (copyright, likeness, platform rules).

Model/tool notes and costs: `ai-tools-landscape`. Camera moves: `video-camera-codes`. Image techniques: `image-generation-playbook`.
