#!/usr/bin/env python3
"""PreToolUse(Write|Edit|MultiEdit): protect sensitive files and stop secrets being written into files.
Exit 2 = block with message to Claude."""
import sys, json, re, os
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input", {}) or {}
path = ti.get("file_path", "") or ""
text = " ".join(str(ti.get(k, "")) for k in ("content", "new_string")) + " " + " ".join(
    str(e.get("new_string", "")) for e in (ti.get("edits") or []) if isinstance(e, dict))

base = os.path.basename(path)
protected = [r"^\.env(\..+)?$", r".*\.pem$", r"^id_(rsa|ed25519|ecdsa)(\.pub)?$", r"^\.npmrc$", r"^\.pypirc$", r"^credentials(\.json)?$"]
if re.search(r"(^|/)\.git/", path) or any(re.match(p, base) for p in protected):
    if base not in (".env.example", ".env.sample", ".env.template"):
        print(f"BLOCKED: '{path}' is a protected/secrets file. Ask the user before touching it; use .env.example for variable names only.", file=sys.stderr)
        sys.exit(2)

patterns = {
    "AWS access key": r"AKIA[0-9A-Z]{16}",
    "GitHub token": r"gh[pousr]_[A-Za-z0-9]{30,}",
    "Slack token": r"xox[abprs]-[A-Za-z0-9-]{10,}",
    "OpenAI/Anthropic-style key": r"\bsk-(ant-)?[A-Za-z0-9_\-]{32,}",
    "Google API key": r"AIza[0-9A-Za-z_\-]{35}",
    "Private key block": r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "Stripe live key": r"\b[sr]k_live_[0-9A-Za-z]{20,}",
}
for name, pat in patterns.items():
    if re.search(pat, text):
        print(f"BLOCKED: content looks like it contains a secret ({name}). Keep secrets in environment variables / a secrets manager, reference them by name, and tell the user to rotate the key if it was pasted in chat.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
