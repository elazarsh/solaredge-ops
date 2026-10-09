#!/usr/bin/env bash
# PreToolUse(Bash): block catastrophic or hard-to-reverse shell commands.
# Reads hook JSON on stdin. Exit 2 = block (stderr is shown to Claude).
set -u
cmd=$(python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    pass' 2>/dev/null)
[ -z "$cmd" ] && exit 0

block() { echo "BLOCKED by guard-destructive hook: $1. Ask the user for explicit approval or use a safer alternative (back up first, scope the path)." >&2; exit 2; }

# rm -rf on root, home, or wildcard of root/home
if echo "$cmd" | grep -Eq '(^|[;&|[:space:]])rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*[[:space:]]+)+(/|~|\$HOME|/\*|~/\*|\.\.?)([[:space:]]|$)'; then
  block "recursive delete of /, ~, \$HOME, . or .."
fi
# force-push to protected branches or any --force without lease
if echo "$cmd" | grep -Eq 'git[[:space:]]+push([^;&|]*)[[:space:]](-f|--force)([[:space:]]|$)' && echo "$cmd" | grep -Eq '(main|master|trunk|develop|release)'; then
  block "force push to a protected branch"
fi
echo "$cmd" | grep -Eq 'git[[:space:]]+push[^;&|]*--force([[:space:]]|$)' && ! echo "$cmd" | grep -q 'force-with-lease' && block "git push --force (use --force-with-lease, and only on your own branch)"
# destructive git on the working tree
echo "$cmd" | grep -Eq 'git[[:space:]]+reset[[:space:]]+--hard' && block "git reset --hard discards uncommitted work"
echo "$cmd" | grep -Eq 'git[[:space:]]+clean[[:space:]]+-[a-zA-Z]*f[a-zA-Z]*d?' && block "git clean -f deletes untracked files"
# disk / permission / pipe-to-shell
echo "$cmd" | grep -Eq '(^|[;&|[:space:]])(mkfs(\.[a-z0-9]+)?|dd[[:space:]]+[^;&|]*of=/dev/)' && block "disk-level write"
echo "$cmd" | grep -Eq 'chmod[[:space:]]+(-R[[:space:]]+)?777[[:space:]]+(/|~)' && block "chmod 777 on root/home"
echo "$cmd" | grep -Eq '(curl|wget)[^|;&]*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z)?sh' && block "piping a download into a shell (download, read, then run)"
# destructive SQL without WHERE
echo "$cmd" | grep -Eiq '(drop[[:space:]]+(table|database)|truncate[[:space:]]+table)' && block "destructive SQL"
# committing secrets
echo "$cmd" | grep -Eq 'git[[:space:]]+add[^;&|]*(\.env($|[[:space:]])|\.pem|id_rsa)' && block "staging a secrets file"
exit 0
