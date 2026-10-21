---
name: install-skill-from-url
description: >
  Turn a documentation URL (or a skills package/repo) into a project skill and take it end to end.
  Use when the user says "התקן סקיל", "install a skill", "add a skill from <link>", or just pastes a docs link
  and asks for it to become a skill.
---

# Install a skill from a link, end to end

1. **Source.** Package or repo of skills → `npx --yes skills add <owner/repo> -y` (installs to `.agents/skills`, symlinked into `.claude/skills`). Docs page → continue below.
2. **Fetch the real content.** If WebFetch/curl returns 404 or a "Redirecting" shell, the site is JS-driven: find the underlying page (look for `list.json`, an iframe `src`, or a `pages/` path in the page source) and fetch that.
3. **Write** `.claude/skills/<kebab-name>/SKILL.md`: frontmatter `name` + `description` (what it does and trigger phrases, Hebrew and English), then a concise body: source URL, working code, rules, and an explicit "not covered by the source" section. Never invent API details that are not in the source.
4. **Verify** the files exist, no secrets, valid frontmatter; run any package-specific check (e.g. `npx hyperframes doctor`).
5. **Ship:** branch `add-<name>-skill` from up-to-date `main` → commit → push → PR. **Ask the user before push and before merge** (standing rule: confirm each outward step). After merge, tell them to open a new session so the skill loads.
