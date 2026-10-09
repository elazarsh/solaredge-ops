## Personal knowledge base (managed block - edit in claude-kb/global-CLAUDE.md, then re-run install.sh)

**About the user:** Hebrew speaker. Reply in Hebrew unless asked otherwise (code, identifiers and commit messages in English). Interests: visual design, video/film, documents and presentations, deep research, building apps and automations. Prefers practical, verified results over explanations.

**How to work (all projects):**
1. For any non-trivial task, check the skill list and load the matching skill(s) first (a router hook may suggest them). Index: `kb-router` skill.
2. Plan before building; smallest working version first; one change at a time.
3. Never invent facts, prices, citations, testimonials, contact details - mark `[להשלים]` / "needs verification".
4. Verify the real output (open the file/run it/watch the video) and report: verified / not verified / missing. Definition of done is in `verify-and-safety-gates`.
5. Ask before outward-facing or irreversible actions (send, publish, pay, delete, force-push). Back up first. Secrets only via env vars.
6. Hebrew deliverables: RTL everywhere, Hebrew-capable fonts, check mixed Hebrew/English/numbers (`hebrew-rtl-output`).
7. Write like a person: specific, plain, no AI cliches (`human-writing-hebrew`).
8. Long sessions: write/read `HANDOFF.md` (goal, decisions, key files, tested, open, next step).

**Skill families:** visual/design (`visual-codes`, `image-generation-playbook`, `design-system-first`), video (`video-camera-codes`, `code-driven-video`, `ai-influencer-ugc-video`), docs/research (`deck-and-doc-craft`, `grounded-research`, `human-writing-hebrew`, `prompt-modifiers`, `content-engine`), apps/automation (`web-build-harden`, `agentic-build-discipline`, `automation-scoping`, `automation-recipes`, `blender-unity-pipeline`), business/marketing (`ad-creative-workflow`, `marketing-analytics-workflow`, `seo-geo-playbook`, `ai-adoption-playbook`), setup (`claude-setup-architecture`, `claude-hooks-playbook`, `custom-assistant-builder`, `ai-tools-landscape`), cross-cutting (`verify-and-safety-gates`, `hebrew-rtl-output`).
