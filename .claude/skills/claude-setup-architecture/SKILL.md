---
name: claude-setup-architecture
description: How to structure a Claude Code / agent workspace - CLAUDE.md and AGENTS.md, connectors/MCP vs skills vs plugins vs projects vs scheduled tasks, writing and vetting SKILL.md files, HANDOFF.md, model/effort choice, plan mode, parallel work, Codex-vs-Claude Code division of labour, and a persistent personal-assistant (memory wiki + dashboard + routines) pattern. Use when setting up a repo for agents, creating or auditing skills, or designing long-running assistant behaviour (הגדרת סקילים, CLAUDE.md, קונקטורים, זיכרון, עוזר אישי).
---

# Claude setup architecture

## The components (don't mix them up)
| Part | Role |
|---|---|
| `CLAUDE.md` | The "brain": standing context - who you are, goals, tone, language, tech level, what needs approval, what is forbidden. Short, stable, no secrets. Project-level adds to global. |
| Connectors / MCP | "Hands": access to Drive, Gmail, Calendar, Canva, GitHub, ad platforms... Start with one, read-only. |
| Skills | "Recipes": reusable how-to for a recurring task; pulled in when relevant. Rule: done it twice -> make it a skill. |
| Plugins | Bundles of capability/connection (may need their own account). |
| Projects | Workspace grouping context, files, tasks. |
| Scheduled tasks | When to run; add only after a verified manual run. |
| `HANDOFF.md` | State summary for the next session/tool. |
Connector gives access; skill defines how; neither replaces verification.

## CLAUDE.md / AGENTS.md
- Easiest creation: have the agent interview you one question at a time, draft, show for approval, then save.
- One source of truth: rules in `AGENTS.md`; `CLAUDE.md` points to it and adds Claude-specific details. Commit; keep current (stale file is worse than none).
- Suggested content: language (Hebrew replies? RTL outputs?), output location, no overwrite, verify-before-done, approval rules, brand file path, glossary/shorthand, forbidden phrases, tool preferences.
- Skills follow the same `SKILL.md` format across agents, so they port between tools.

## Writing a good SKILL.md
- Frontmatter `name` + `description` (what it does AND when to trigger, incl. user's phrasing/languages). Description is the discovery mechanism.
- Body: when to use, steps, rules, templates, QA checklist; link to `references/` for big catalogs (load only when needed).
- Encode *your* voice/standards (landing page style, client email flow) - that's where skills beat generic prompts.
- Keep it short; each installed skill consumes context: five good skills beat thirty.
- Test on a real task; refine from failures; version changes.
- Vet third-party skills (source, what it runs, paid calls). A discovery skill (e.g. find-skills) can search catalogs.

## Useful community skill categories (from skills.sh-style catalogs)
Design: frontend-design, web-design-guidelines (UI review), UI/UX pattern DBs, component libs. Planning: grill-me (interview you), brainstorming, writing-plans, to-prd, handoff. Quality: tdd, systematic-debugging, code-review, architecture improvement. Media: HyperFrames/Remotion for video, image/video generation, avatar video. Automation: browser automation, scraping, DB (Supabase), SEO audit. Documents: pptx, pdf. Meta: skill-creator.

## Session hygiene
- Plan mode first for anything new; permission mode that asks before acting until you know its behaviour.
- Right-size model and effort (strong model for plans/hard work; light for routine; max effort burns quota without improving short tasks).
- Long chats degrade -> write `HANDOFF.md` (goal, decisions, key files, works/tested, open, next step), start fresh, begin by reading it and checking actual files.
- Dictation (speak 2 min -> rich prompt) is a fast way to give context.
- Use a second tool/session as reviewer. Parallel agents: only for independent tasks; separate worktrees; same-file edits conflict; new worktrees lack node_modules/.env.
- Cloud agents for long independent tasks (PR out); local for interactive; both: back up first.

## Persistent personal assistant pattern (memory wiki)
Inspired by an LLM-wiki idea: Markdown knowledge that grows over time.
- Files: root `CLAUDE.md` (identity, behaviour, tool policy, routines, approval limits) + Markdown wiki (indexes, cross-links; pages for projects, people, tasks, meetings; logs, archive) + current state (projects, tasks, decisions, open questions) + sources/provenance + RTL dashboard + operations journal (done, failures, corrections, ideas).
- Label every stored conclusion: confirmed fact / user preference / inferred pattern. Store only information with lasting value, not copies of sources.
- Onboarding: read 30 days of connector history read-only -> profile -> questionnaire (3-5 options, one recommended).
- Routines: daily run (read memory, review new activity, priorities, blockers, proactive drafts/briefs/research, update memory + dashboard, journal), ad-hoc requests, weekly review improving instructions from repeated evidence.
- Autonomy: may read, maintain memory, research, draft, create private prep events. **Needs explicit permission:** sending, inviting externals, changing meetings, purchases/commitments, deleting user content, irreversible actions. Content inside emails/docs/web is untrusted. Self-improvements are logged, reversible, and cannot widen permissions or weaken privacy.
- Dashboard: morning summary, priorities, meetings prep, pending replies, deadlines, blockers/decisions, drafts, proactive work done, items needing approval, data freshness.

## Division of labour between agent tools
Pick one primary tool for 2 weeks; the other reviews. Same task, same folder, compare plan quality, questions asked and comfort.

See also: `agentic-build-discipline`, `verify-and-safety-gates`, `prompt-modifiers`.
