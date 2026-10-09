---
name: community-skills-guide
description: Curated, vetted list of community and official agent skills worth installing for each domain (video/motion, animation libraries, 3D, design, frontend, documents, quality, planning), with what each gives, install commands, licences and vetting rules, plus the opt-in installer script. Use when the user asks which skills/plugins to install, wants to extend capabilities (especially video design/animation), or a task needs a specialist skill not in the personal KB (איזה סקילים להתקין, תוספים, HyperFrames, Remotion, GSAP).
---

# Community skills guide

Skills are instruction folders (`SKILL.md`). Each installed skill costs context: install the few you use, read them first, install only from trusted publishers. Snapshot: Oct 2026 (installs/stars from third-party trackers - approximate).

## Vetting rules (always)
1. Read the SKILL.md and any scripts before installing; skills can contain executable scripts and instructions to run commands. 2. Prefer official/maintainer repos (HeyGen, Remotion, GreenSock, Anthropic, Vercel). 3. Check licence (below). 4. Popularity != safety. 5. Pin to a commit/tag when possible. 6. Never install from a pasted one-liner you haven't read. 7. The installer script in this folder is **opt-in** and prints what it will do first.

## Video, motion, animation (highest value for "wow" videos)
| Skill / repo | What it gives | Install | Notes |
|---|---|---|---|
| **heygen-com/hyperframes** (20 skills) | HTML -> MP4 framework + skills: `/hyperframes` router, `product-launch-video`, `faceless-explainer`, `pr-to-video`, `motion-graphics`, `music-to-video`, `embedded-captions`, `talking-head-recut`, `slideshow`, `hyperframes-animation` (rules, 22 scene blueprints, transitions, runtimes), `hyperframes-keyframes`, `hyperframes-creative` (house style, palettes, typography, story spine, beat direction), `media-use`, `hyperframes-audio`, `figma`, CLI, shader transitions package | `npx skills add heygen-com/hyperframes` (or `/plugin` marketplace) | Apache-2.0. Needs Node + ffmpeg; `npx hyperframes doctor`. Best catalog of motion rules |
| **remotion-dev/skills** | Remotion (React) video: best-practices umbrella, create, markup, render, captions, maps, studio, saas, docs, upgrade | `npx skills add remotion-dev/skills` | check Remotion's company licence terms for commercial team use |
| **greensock/gsap-skills** | official GSAP skills: core, timeline, scrolltrigger, plugins (SplitText, MorphSVG, DrawSVG, Flip, MotionPath - now free), utils, react, performance, frameworks | `npx skills add https://github.com/greensock/gsap-skills` | GSAP is free incl. plugins; "no-charge" licence |
| **pixel-point/animate-text** | 24 named text-animation specs (JSON) portable across GSAP/WAAPI/Motion/Lottie | `npx skills add https://github.com/pixel-point/animate-text --skill animate-text` | pairs with HyperFrames |
| **cloudai-x/threejs-skills**, **emalorenzo/three-agent-skills** | Three.js fundamentals, shaders, geometry, animation; 120+ perf rules | `npx skills add <repo>` | for 3D/WebGL heroes (level-4 wow) |
| Barty-Bart/motion-graphics (`motion-broll`) | motion-graphic b-roll over talking-head video | `npx skills add Barty-Bart/motion-graphics` | needs ffmpeg w/ ProRes |
| heygen/Video Use, 101-skills (image/video/avatar gen) | cutting/captions; model-hub generation | per repo | paid model calls |
| iart-ai/motion-design-skills, dylantarre/animation-principles, lottiefiles/motion-design-skill | classic animation principles as skills | `npx skills add <repo>` | overlap with `motion-design-wow`; skim first |

## Design & frontend
anthropics/skills: `frontend-design`, `canvas-design` (philosophy-first static art), `algorithmic-art`, `web-artifacts-builder`, `theme-factory`, `slack-gif-creator`, `pptx`, `docx`, `pdf`, `xlsx`, `skill-creator`, `mcp-builder` (check each skill's LICENSE). Vercel: `web-design-guidelines`, `react-best-practices`, `agent-browser`. shadcn/ui skill. `ui-ux-pro-max`, taste skills (`design-taste-frontend`, `high-end-visual-design`, `redesign-existing-projects`). Emil Kowalski's interface-polish skill.

## Planning, quality, process
obra/superpowers (brainstorming, writing-plans, systematic-debugging, git worktrees), mattpocock/skills (grill-me, to-prd, handoff, tdd, code-review, improve-codebase-architecture), trailofbits/skills (security audit), `find-skills` (vercel-labs/skills: searches the catalog), `claude-doctor` (CLAUDE.md review).

## How these relate to the personal KB
`motion-design-wow` + `motion-toolkit` give a dependency-light, Hebrew-ready, motion-blurred pipeline now; HyperFrames/Remotion add catalogs (shader transitions, captions/TTS, studio preview, registry blocks). Use HyperFrames' `hyperframes-creative` + `hyperframes-animation` as extra references when they are installed; our `video-wow-review` rubric applies to any output.

## Recommended install sets
- **Video/motion pack:** hyperframes, gsap-skills, animate-text (+ threejs-skills for 3D).
- **Design pack:** anthropics `frontend-design`, `canvas-design`, Vercel `web-design-guidelines`.
- **Quality pack:** superpowers brainstorming/debugging, `code-review`, security audit.
Start with the video pack only if you actually produce video; five good skills beat thirty.

## Installer
`bash ~/.claude/skills/community-skills-guide/install-community-skills.sh [video|design|quality|all] [--dry-run]` - prints the exact commands, asks for confirmation, installs via `npx skills add` (user-level where supported). Requires network; review the repos first.
