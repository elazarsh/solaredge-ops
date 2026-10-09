#!/usr/bin/env bash
# Installs the personal knowledge base into the USER-level Claude config so it applies to every project.
#   ./install.sh            install / update
#   ./install.sh --dry-run  show what would change
#   ./install.sh --uninstall remove skills/hooks/block installed by this script
# Idempotent. Never deletes files it did not install. Backs up settings.json and CLAUDE.md before editing.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
MODE="install"
for a in "$@"; do
  case "$a" in
    --dry-run) MODE="dry" ;;
    --uninstall) MODE="uninstall" ;;
    -h|--help) sed -n '2,7p' "${BASH_SOURCE[0]}"; exit 0 ;;
  esac
done
BEGIN="<!-- BEGIN claude-kb (managed) -->"
END="<!-- END claude-kb (managed) -->"
MANIFEST="$DEST/.claude-kb-manifest"

say() { echo "[claude-kb] $*"; }
run() { if [ "$MODE" = "dry" ]; then say "(dry) $*"; else eval "$@"; fi; }

command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }

if [ "$MODE" = "uninstall" ]; then
  [ -f "$MANIFEST" ] || { say "nothing installed (no manifest)"; exit 0; }
  while IFS= read -r p; do [ -n "$p" ] && rm -rf -- "$DEST/$p" && say "removed $p"; done < "$MANIFEST"
  python3 - "$DEST" "$BEGIN" "$END" <<'PY'
import sys, re, os, json
dest, begin, end = sys.argv[1:4]
p = os.path.join(dest, "CLAUDE.md")
if os.path.exists(p):
    t = open(p, encoding="utf-8").read()
    t = re.sub(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", "", t, flags=re.S)
    open(p, "w", encoding="utf-8").write(t)
s = os.path.join(dest, "settings.json")
if os.path.exists(s):
    cfg = json.load(open(s, encoding="utf-8"))
    hooks = cfg.get("hooks", {})
    for ev in list(hooks):
        new = []
        for grp in hooks[ev]:
            grp["hooks"] = [h for h in grp.get("hooks", []) if "/.claude/hooks/" not in h.get("command", "") or not any(n in h["command"] for n in ("guard-destructive","guard-files-secrets","session-context","skill-router","post-edit-check"))]
            if grp["hooks"]:
                new.append(grp)
        if new: hooks[ev] = new
        else: del hooks[ev]
    if not hooks: cfg.pop("hooks", None)
    json.dump(cfg, open(s, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
  rm -f "$MANIFEST"; say "uninstalled"; exit 0
fi

run "mkdir -p '$DEST/skills' '$DEST/hooks'"
: > /tmp/.claude-kb-manifest.$$

# 1) skills
for d in "$SRC"/skills/*/; do
  n="$(basename "$d")"
  say "skill: $n"
  run "rm -rf '$DEST/skills/$n' && cp -R '$d' '$DEST/skills/$n'"
  echo "skills/$n" >> /tmp/.claude-kb-manifest.$$
done

# 2) hooks
for f in "$SRC"/hooks/*; do
  n="$(basename "$f")"
  say "hook file: $n"
  run "cp '$f' '$DEST/hooks/$n' && chmod +x '$DEST/hooks/$n'"
  echo "hooks/$n" >> /tmp/.claude-kb-manifest.$$
done

# 3) settings.json hook merge (dedupe by command string; preserves existing settings)
if [ "$MODE" = "dry" ]; then
  say "(dry) would merge hooks from settings.hooks.json into $DEST/settings.json"
else
  [ -f "$DEST/settings.json" ] && cp "$DEST/settings.json" "$DEST/settings.json.bak.$(date +%s)"
  python3 - "$SRC/settings.hooks.json" "$DEST/settings.json" <<'PY'
import sys, json, os
src, dst = sys.argv[1:3]
new = json.load(open(src, encoding="utf-8"))
cfg = json.load(open(dst, encoding="utf-8")) if os.path.exists(dst) else {}
hooks = cfg.setdefault("hooks", {})
added = 0
for ev, groups in new["hooks"].items():
    cur = hooks.setdefault(ev, [])
    existing = {h.get("command") for g in cur for h in g.get("hooks", [])}
    for g in groups:
        fresh = [h for h in g["hooks"] if h["command"] not in existing]
        if not fresh:
            continue
        # merge into an existing group with the same matcher when present
        tgt = next((c for c in cur if c.get("matcher") == g.get("matcher")), None)
        if tgt: tgt["hooks"].extend(fresh)
        else:
            ng = {k: v for k, v in g.items() if k != "hooks"}; ng["hooks"] = fresh; cur.append(ng)
        added += len(fresh)
json.dump(cfg, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"[claude-kb] settings.json: {added} hook command(s) added")
PY
fi

# 4) global CLAUDE.md managed block
if [ "$MODE" = "dry" ]; then
  say "(dry) would update managed block in $DEST/CLAUDE.md"
else
  [ -f "$DEST/CLAUDE.md" ] && cp "$DEST/CLAUDE.md" "$DEST/CLAUDE.md.bak.$(date +%s)"
  python3 - "$SRC/global-CLAUDE.md" "$DEST/CLAUDE.md" "$BEGIN" "$END" <<'PY'
import sys, re, os
src, dst, begin, end = sys.argv[1:5]
block = begin + "\n" + open(src, encoding="utf-8").read().rstrip() + "\n" + end + "\n"
t = open(dst, encoding="utf-8").read() if os.path.exists(dst) else ""
pat = re.escape(begin) + r".*?" + re.escape(end) + r"\n?"
t = re.sub(pat, block, t, flags=re.S) if re.search(pat, t, flags=re.S) else (t.rstrip() + "\n\n" if t.strip() else "") + block
open(dst, "w", encoding="utf-8").write(t)
PY
fi

[ "$MODE" = "install" ] && mv /tmp/.claude-kb-manifest.$$ "$MANIFEST" || rm -f /tmp/.claude-kb-manifest.$$
say "done ($MODE). Restart Claude Code sessions to load skills and hooks."
