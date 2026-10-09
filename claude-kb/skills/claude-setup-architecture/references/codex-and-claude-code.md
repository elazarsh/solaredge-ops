# Claude Code & Codex operations reference

## Claude Code onboarding (for non-developers; ~20 min)
Prereqs: paid plan, regular Mac/Windows, desktop app (includes Code tab), Node.js, separate folder per project, one real time-wasting task. Windows: Git later. Hebrew works; mixed English may confuse RTL in terminals, fine in the desktop app.
First session: new folder -> permission mode that asks -> balanced model for routine, strongest for complex -> small checkable task, no sensitive data -> read proposed actions -> verify in the folder, not the "done" message.
Intro prompt: explain what you can do in this folder in a few lines; create one small test file but show the plan and wait for approval; tell me where it is saved and how to verify; touch nothing else.
Permission modes: Manual (asks), Accept edits, Auto, Bypass (skip checks - not for beginners/no backup). Plan mode first for anything new.
**CLAUDE.md interview prompt:** ask 7 questions one at a time (identity, goals, common tasks, communication style, technical level, things to avoid, technical preferences), draft, show, save after approval.
Three starter tasks (all in Plan mode): (1) organise a cluttered folder (table -> <=6 folders -> approval -> move without delete/rename -> log + file counts match); (2) one document -> LinkedIn post + customer message + 5 FAQs (ask 3 questions first; only document facts; `[להשלים]` for gaps; separate files); (3) local landing page (interview -> outline approval -> mobile-friendly, RTL -> no invented proof -> don't publish).
7-day path: install+intro -> CLAUDE.md -> folder task -> content task -> one read-only connector -> landing page -> first skill + HANDOFF.md.
Pitfalls: whole-desktop scope, giant tasks, skipping plan, bypass-all too early, trusting "done", pasting secrets, no backup, endless single chat.
Safety: no bank/credit/irreversible access; instructions are not enforcement; backups + permissions are. (A cited case: an agent update without backup destroyed months of work.)
Connectors: Customize -> Connectors -> Add -> Browse -> connect -> authenticate; start with one, read-only; "Account Mismatch" = sign in with the right account. MCP: distinguish server URLs from install commands.
Skills install: via directory, or copy install snippet from a skills repo; `npx skills add <repo> --skill <name>` style commands; vet source.

## Codex surfaces
Desktop app (threads, terminal, file tree, Review panel with diffs, browser, annotate UI, images, dictation); Cloud (remote container on GitHub repo; Ask = questions, Code = changes; results -> PR; computer can be off; harder auth/secrets debugging - start local); CLI (npm/brew; `/status` `/model` `/approvals` `/compact`, `codex resume`); IDE extension (VS Code/Cursor/Windsurf; delegate to cloud then Apply - check branch first); GitHub review (`@codex review`, `@codex address this feedback`, `@codex fix this CI failure`).
Modes: Read-only / Auto / Full access; reasoning effort low..extra-high (don't max out on 2-minute tasks).
Workflow: small scoped task with done-criteria; Plan mode for multi-file; generate variants and pick; `/init` drafts AGENTS.md; turn a successful session into a skill (description = trigger); subagents for independent tasks only (cheaper model for simple; never two on the same file); automations: perfect the skill first, then schedule, keep a ledger file to avoid double-processing, check which model the automation uses, close spreadsheets before writes; large projects: GitHub Issues -> worktree+branch each -> merge PRs in dependency order (worktrees lack node_modules/.env -> setup script); Context7 for current library docs; Computer Use for apps without APIs and for clicking through your own UI.
Safety: ask-for-approval mode, git revert path, review diffs, guardrail against destructive commands in full-access, keys in env files only, official plugins/MCP only (external text can try to steer the agent), Ask mode for read-only in cloud.

## Division of labour
One primary tool for 2 weeks; the other reviews ("make no changes; summarise recent changes; look for bugs/leftover placeholders; rank must-fix/should-fix/low; propose fixes"). Shared rules in AGENTS.md; CLAUDE.md points to it. Shared SKILL.md format. Long independent tasks -> cloud agent; interactive -> local. HANDOFF.md lets either tool resume.
