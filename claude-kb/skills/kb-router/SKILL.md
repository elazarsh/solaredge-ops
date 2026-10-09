---
name: kb-router
description: Index and routing guide for the personal knowledge base of skills - which skill to load for which kind of request (design, video, images, documents, research, writing, web/app building, automation, marketing, SEO, AI adoption, tool selection, Claude setup, hooks), plus combos for multi-step projects. Use at the start of any broad or multi-domain request, when unsure which skill applies, or when the user asks what the knowledge base contains (איזה סקיל, מה יש במאגר, תכנון פרויקט רב-שלבי).
---

# KB router

## Quick map
| Request type | Load |
|---|---|
| Infographic, diagram, concept visual, product visual | `visual-codes` + `image-generation-playbook` |
| Image editing/enhancement/consistency/Hebrew text in images | `image-generation-playbook`, `hebrew-rtl-output` |
| Brand look, design system, deck/landing visuals | `design-system-first` |
| AI video from image / camera moves | `video-camera-codes` |
| UGC / AI influencer / viral short, editing footage with AI | `ai-influencer-ugc-video` |
| **Stunning / wow / cinematic / premium video, ad, intro, reel, animated slide** | `motion-design-wow` -> `motion-toolkit` (+ `kinetic-typography-hebrew`, `sound-design-procedural`) -> `video-wow-review` |
| Review a rendered video / "not wow enough" | `video-wow-review` |
| Which community skills to install (HyperFrames, Remotion, GSAP, Three.js) | `community-skills-guide` |
| Explainer, motion graphics, captions, ad variants as code | `code-driven-video` |
| Ads, campaign creative | `ad-creative-workflow` |
| Campaign data analysis, reports | `marketing-analytics-workflow` |
| Content calendar, hooks, repurposing | `content-engine`, `prompt-modifiers` |
| Deck, report, minutes, SOP | `deck-and-doc-craft` (+ pptx/docx/pdf skills) |
| Research, comparison, source-based analysis | `grounded-research` |
| Writing/editing, de-AI-ify, Hebrew copy | `human-writing-hebrew` |
| Website / landing page / launch check | `web-build-harden` (+ `design-system-first`) |
| App, bot, pipeline, API integrations | `agentic-build-discipline` |
| 3D, Blender, Unity, game prototype | `blender-unity-pipeline` |
| What to automate / how | `automation-scoping`, then `automation-recipes` |
| Org-wide AI rollout, policy, ROI | `ai-adoption-playbook` |
| SEO / GEO | `seo-geo-playbook` |
| Which tool? costs? | `ai-tools-landscape` |
| Reusable assistant / Gem / system prompt | `custom-assistant-builder` |
| CLAUDE.md, skills, memory, Codex vs Claude Code | `claude-setup-architecture` |
| Hooks, guards, automatic behaviours | `claude-hooks-playbook` |
| Thinking/writing modifiers like /redteam | `prompt-modifiers` |
| ALWAYS before finishing / irreversible actions / sensitive data | `verify-and-safety-gates` |
| Any Hebrew deliverable | `hebrew-rtl-output` |

## Multi-step project combos
- **Product launch video:** `grounded-research` (facts) -> `design-system-first` -> `motion-design-wow` (concept, style, beats) -> `motion-toolkit` (+ `kinetic-typography-hebrew`, `sound-design-procedural`) -> `video-wow-review` -> `ad-creative-workflow` (variants) -> `verify-and-safety-gates`. For AI-generated footage instead: `image-generation-playbook` -> `video-camera-codes` / `ai-influencer-ugc-video` -> `code-driven-video` (captions/edit).
- **Website for a business:** `design-system-first` -> `web-build-harden` -> `seo-geo-playbook` -> `hebrew-rtl-output` -> `verify-and-safety-gates`.
- **Research report + deck:** `grounded-research` -> `deck-and-doc-craft` -> `visual-codes` -> `human-writing-hebrew`.
- **Back-office automation:** `automation-scoping` -> `automation-recipes` -> `agentic-build-discipline` -> `verify-and-safety-gates`.
- **Company AI rollout:** `ai-adoption-playbook` -> `automation-scoping` -> `custom-assistant-builder` -> `deck-and-doc-craft`.

## Rules for using the KB
1. Load only the skills that fit (each costs context); read `references/` files only when needed.
2. When a skill conflicts with explicit user instructions, the user wins.
3. Source material was a single author's blog; claims about prices, features, laws and availability are **unverified snapshots** - check current sources before relying on them.
4. When you learn something new that should persist (a correction, a better prompt, a new workflow), propose adding it to the right skill in `claude-kb/skills/` and re-running `install.sh`.
5. Don't recite skill text at the user; apply it.
