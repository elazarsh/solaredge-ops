---
name: ai-tools-landscape
description: Decision knowledge base for choosing AI tools and models by task - coding agents, general assistants, image/video/voice/music, presentations, research, automation platforms, Google/OpenAI/Anthropic ecosystems, agent infrastructure - with selection principles, cost-saving habits, Hebrew-quality gaps and availability warnings. Use when the user asks "which tool should I use", wants alternatives, price/credit planning, or when picking a generator for video/image/voice/app building (איזה כלי, השוואת כלים, עלויות, קרדיטים).
---

# AI tools landscape (snapshot: Aug-Oct 2026, from amichai-ai.co.il)

**Prices, limits and availability change every few weeks - verify on the vendor page before recommending or promising anything.** Descriptions below are the source's, not independently verified.

## Selection principles
1. Start from the task, then the tool; check whether a tool the user already pays for can do it.
2. Concepts transfer between tools (context, skills, connectors, permissions); don't chase hype.
3. Prefer provider-agnostic standards (MCP, SKILL.md, AGENTS.md).
4. Free/low-cost first; draft cheap (low-res, short clips, small models), finalize expensive.
5. Hebrew voice/speech/text quality varies a lot - test before committing.
6. Keep instruction files short; use heavy reasoning only for complex planning; split long chats.
7. Back up (git) before loosening permissions; prefer "Auto"/ask modes over "bypass".
8. Verify before shipping: security audit + browser test.

## Quick chooser
| Need | First choices | Notes |
|---|---|---|
| Build apps/sites with an agent | Claude Code, Codex, Cursor, Antigravity, Lovable/Base44 (no-code), Google AI Studio | Codex = cloud tasks/PR review; Claude Code = plan mode, connectors |
| Deploy / data / backup | Vercel, Supabase, GitHub | free tiers usually enough |
| Presentations | Gamma, NotebookLM slides, Claude Design, Genspark Slides | brand via design system |
| Design / UI | Claude Design, Canva AI, Figma (+MCP), Aura, Neuform, Paper | see `design-system-first` |
| Diagrams from text | Napkin AI, Excalidraw | |
| Research | NotebookLM (sources+citations), Perplexity (web+Deep Research), Claude/GPT research modes | see `grounded-research` |
| Images | Nano Banana Pro (Gemini), GPT Image, Ideogram (text), Midjourney, Astria (custom subjects), Lummi (stock) | see `image-generation-playbook` |
| 3D | Meshy, Tripo, Blender | `blender-unity-pipeline` |
| Video from scratch | Veo, Kling, Seedance 2, Sora, MiniMax | Seedance cinematic but bad Hebrew; Veo decent Hebrew; Kling cheap |
| Edit real video | Omni (Flow), HyperFrames/Video Use (code), CapCut | `code-driven-video`, `ai-influencer-ugc-video` |
| Avatars/talking head | HeyGen, MakeUGC | HeyGen Hebrew text weak |
| Voice / TTS / dubbing | ElevenLabs (V3 best Hebrew; use nikud), MiniMax | |
| Hebrew transcription | ivrit.ai (free), Whisper | |
| Music | Suno | |
| Dictation | Wispr Flow, Speakly | long detailed prompts by voice |
| Automation | Make, n8n, Zapier, Apps Script | `automation-recipes` |
| Agents/memory/integrations | OpenClaw, Hermes Agent, Composio, Supermemory, Vapi (voice), Kapso/Green API (WhatsApp), Periskope | `agentic-build-discipline` |
| Media APIs | fal.ai, KIE.ai, Google AI Studio | cheaper than premium wrappers |
| SEO | RankGrow, Semrush, Search Console | `seo-geo-playbook` |
| App store ops | Stora | |
| All-in-one agent | Genspark, Manus | sensitive data -> enterprise suites |

## Ecosystem notes
- **Google:** Gemini (+Gems), NotebookLM (free), Workspace Studio automations (Workspace plans), Flow + Veo + Omni (video), Nano Banana, Gemini Spark (background personal agent; region/plan-gated; 50 schedules/15 parallel tasks; keep approval for sends), Antigravity (agent control room, free), Project Genie (research prototype).
- **OpenAI:** ChatGPT (Work/Sites/Projects/Skills/plugins), Codex (desktop app, cloud, CLI, IDE, GitHub review), model families picked by task not release date; reasoning level by task complexity.
- **Anthropic:** Claude (chat, Cowork, Design, in Chrome), Claude Code, connectors/MCP, skills.
- **Higgsfield:** wrapper for many image/video/audio models + MCP/CLI + agent ("Super Computer"); convenient not cheap; direct APIs cheaper.
- **Perplexity:** use operators (`site:`, `after:`, `file:`), academic mode, Spaces for project context, Pages -> HTML; click every cited source.
- **Genspark:** multi-model, slides, site builder, "Call for me"; credit-based; download code and host elsewhere; avoid for complex integrations/sensitive data.

## Cost habits
4-s clips before 8-s; 720p tests; cheap model for Hebrew narration; write scripts/prompts in an external LLM first; one test unit before batches; cap budgets; confirm cost before generation; watch usage meters; separate planning (LLM) cost from generation cost; cancel unused subscriptions.

## Extra agent-environment tools (context feeders)
Voice dictation (Speakly/Wispr), launcher + clipboard history (Raycast), screenshot/recording (CleanShot/Shottr), design via MCP (Paper), reading highlights with API (Readwise), diagram (Excalidraw).

## Community-popular skills (verify before installing)
Planning: brainstorming, writing-plans, grill-me, to-prd, handoff. Quality: tdd, systematic-debugging, code-review, security audit (static scan), react best-practices, web-design-guidelines. Design: frontend-design, UI/UX pattern DBs. Media: hyperframes, remotion, image/video generation. Browser: agent-browser. Meta: skill-creator, find-skills, a CLAUDE.md "doctor". Repos: skills.sh, agentskills.co.il (Hebrew/Israel compliance skills - treat claims about legal compliance as unverified).

More: `references/misc-workflows.md` (job search with a scraping connector, memory transfer, vacation planning ideas).
