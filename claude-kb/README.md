# claude-kb - personal Claude knowledge base

Portable bundle of **27 skills + 5 hooks + a managed global CLAUDE.md block**, built from a research pass over amichai-ai.co.il plus Claude Code best practice. It installs into the **user-level** Claude config (`~/.claude`), so it applies to every project - not just the repo it lives in.

```
claude-kb/
  skills/            27 skill folders (SKILL.md + references/) + README index
  hooks/             guard-destructive.sh, guard-files-secrets.py, session-context.sh,
                     skill-router.py (+ router-rules.json), post-edit-check.sh
  settings.hooks.json  hook wiring merged into ~/.claude/settings.json
  global-CLAUDE.md   managed block appended to ~/.claude/CLAUDE.md
  install.sh         idempotent installer (--dry-run, --uninstall)
```

## Install (on each machine / new container)
```bash
git clone <this repo> && cd <repo>/claude-kb
./install.sh --dry-run   # preview
./install.sh             # install
```
Installer: copies skills and hooks, merges hook entries into `~/.claude/settings.json` (backup `.bak.<ts>` first, no duplicates), inserts a marked block into `~/.claude/CLAUDE.md`, records what it installed so `--uninstall` removes only that. Set `CLAUDE_HOME` to install elsewhere. Restart Claude Code afterwards.

Cloud sessions are ephemeral: either run `install.sh` from a SessionStart step in your environment's setup script, or keep this folder in a repo you attach to sessions.

## Maintain
- Edit a skill -> re-run `install.sh`.
- Teach the router new topics -> `hooks/router-rules.json`.
- New knowledge from sessions (corrections, better prompts) -> add to the matching skill, commit.
- Sources are one author's blog snapshot (Aug-Oct 2026): prices/availability/laws drift; skills tell Claude to re-verify.

## Hooks summary
| Hook | Event | Effect |
|---|---|---|
| guard-destructive | PreToolUse Bash | blocks rm -rf /~, force-push, reset --hard, clean -f, disk writes, curl\|sh, destructive SQL, staging .env |
| guard-files-secrets | PreToolUse Write/Edit | blocks editing .env/keys/.git and writing API keys/tokens |
| skill-router | UserPromptSubmit | hints which skills to load (Hebrew + English keywords) |
| session-context | SessionStart | date, git state, HANDOFF.md reminder |
| post-edit-check | PostToolUse Write/Edit | syntax check py/sh/json/js/yaml, feeds errors back |

Skill index: `skills/README.md`.
