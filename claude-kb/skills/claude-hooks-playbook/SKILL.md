---
name: claude-hooks-playbook
description: How to design, write, install and debug Claude Code hooks (settings.json) - events, matchers, stdin JSON, exit codes, context injection, blocking guards, auto-checks, and the ready-made hooks in this knowledge base (guard-destructive, guard-files-secrets, skill-router, session-context, post-edit-check). Use when the user wants automatic behaviour "whenever/before/after X", safety guards, auto-formatting/tests, context injection, or to extend the KB router (הוק, hooks, אוטומציה בקלוד קוד, settings.json).
---

# Claude Code hooks playbook

A hook is a command the **harness** runs on an event - it is deterministic, unlike a memory or instruction. If the user says "from now on, whenever X do Y", use a hook (settings.json), not a note. Prefer the `update-config` skill for the actual settings edit if available.

## Events (the useful ones)
| Event | When | Typical use |
|---|---|---|
| `SessionStart` | session begins/resumes | print context (date, git state, handoff file); stdout becomes context |
| `UserPromptSubmit` | user sends a prompt | inject hints/context (skill router); can block |
| `PreToolUse` | before a tool runs (matcher = tool name regex: `Bash`, `Write|Edit`, `mcp__.*`) | guards; exit 2 blocks and returns stderr to Claude |
| `PostToolUse` | after a tool succeeds | syntax check, format, lint, run fast tests; exit 2 sends stderr back to Claude |
| `Stop` / `SubagentStop` | Claude finishes | final verification nudges (guard against loops: check `stop_hook_active`) |
| `PreCompact` | before context compaction | snapshot state |
| `Notification` | Claude needs attention | desktop/phone notify |
| `SessionEnd` | session ends | cleanup/logging |

## Contract
- Config (`~/.claude/settings.json` user-level, `.claude/settings.json` project, `.claude/settings.local.json` personal):
```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "$HOME/.claude/hooks/guard-destructive.sh"}]}]}}
```
- Input: JSON on **stdin** (`tool_name`, `tool_input`, `prompt`, `cwd`, `session_id`, `transcript_path`, `hook_event_name`...).
- Output/exit: `0` = ok (stdout is added as context for SessionStart/UserPromptSubmit); `2` = block, **stderr is fed to Claude**; other non-zero = non-blocking error shown to the user. JSON output on stdout can carry richer decisions.
- Hooks run with your shell permissions, in parallel with other matching hooks, with a timeout. Keep them fast (<1 s), idempotent, quiet when everything is fine.
- Test by piping sample JSON: `echo '{"tool_input":{"command":"rm -rf ~"}}' | ./guard-destructive.sh; echo $?`.

## Design rules
1. A guard blocks only what is clearly dangerous; message must tell Claude what to do instead.
2. Never block `Stop` unconditionally (infinite loops). Prefer nudges via context.
3. Don't print noise on success.
4. No secrets or network calls in hooks. Review third-party hooks like code you'd run as yourself.
5. Hooks complement - not replace - permissions and backups.
6. After editing settings, restart the session. Debug with `claude --debug` or `/hooks`.

## Shipped hooks (claude-kb/hooks)
- `guard-destructive.sh` (PreToolUse Bash): blocks `rm -rf /|~|.`, force-push to protected branches or without lease, `git reset --hard`, `git clean -f`, disk writes (`mkfs`, `dd of=/dev`), `chmod 777 /`, curl|sh, destructive SQL, staging `.env`/keys.
- `guard-files-secrets.py` (PreToolUse Write/Edit): blocks edits to `.env*`, keys, `.git/`, and any content that looks like an API key/token/private key.
- `skill-router.py` + `router-rules.json` (UserPromptSubmit): keyword -> "load skill X" hint (Hebrew + English). **Edit the JSON to teach it new topics.**
- `session-context.sh` (SessionStart): date, git branch/dirty count, HANDOFF.md reminder, KB pointer.
- `post-edit-check.sh` (PostToolUse Write/Edit): syntax check for py/sh/json/js/yaml, error returned to Claude.
Install: `claude-kb/install.sh` (merges into `~/.claude/settings.json` without clobbering). Uninstall: `--uninstall`.

## Ideas to add on request
Auto-format on save (prettier/ruff/black); run changed-file tests after edits; block edits on `main`; require plan approval before `git push`; log every Bash command to a file; notification when a long task finishes; verify-before-stop nudge that checks for an unreported test run; enforce commit message style; remind to update HANDOFF.md at PreCompact; per-project hooks for deploy safety (e.g. block `vercel --prod` without confirmation).

## Adding a rule to the router
Append to `rules` in `router-rules.json`: `{"skills": ["skill-a"], "keywords": ["hebrew word", "english phrase"]}` (case-insensitive substring match), re-run `install.sh`.
