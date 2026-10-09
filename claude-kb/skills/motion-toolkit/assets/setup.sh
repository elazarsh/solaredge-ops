#!/usr/bin/env bash
# Prepares ./vendor for a composition: gsap + bundled Hebrew/Latin fonts (offline, deterministic renders).
# Usage: ./setup.sh [target_dir=.]   (run from anywhere; installs deps into <target>/.deps)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="${1:-.}"; mkdir -p "$T/vendor" "$T/.deps"
cp "$HERE/package.json" "$T/.deps/package.json"
(cd "$T/.deps" && npm install --no-audit --no-fund --silent)
cp "$T/.deps/node_modules/gsap/dist/gsap.min.js" "$T/vendor/gsap.min.js"
python3 - "$T" <<'PY'
import sys, os, re, shutil
T = sys.argv[1]; nm = os.path.join(T, ".deps/node_modules/@fontsource")
out = os.path.join(T, "vendor/fonts"); os.makedirs(out, exist_ok=True)
HEB = "U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F"
LAT = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
spec = {  # family-dir: (css family name, weights, subsets)
  "heebo": ("Heebo", [400,700,900], ["hebrew","latin"]),
  "rubik": ("Rubik", [400,500,800,900], ["hebrew","latin"]),
  "secular-one": ("Secular One", [400], ["hebrew","latin"]),
  "frank-ruhl-libre": ("Frank Ruhl Libre", [400,900], ["hebrew","latin"]),
  "assistant": ("Assistant", [300,400,700,800], ["hebrew","latin"]),
  "karantina": ("Karantina", [300,400,700], ["hebrew","latin"]),
  "space-grotesk": ("Space Grotesk", [500,700], ["latin"]),
  "jetbrains-mono": ("JetBrains Mono", [400,700], ["latin"]),
}
css = []
for d, (fam, weights, subs) in spec.items():
    src = os.path.join(nm, d, "files")
    if not os.path.isdir(src): continue
    dst = os.path.join(out, d); os.makedirs(dst, exist_ok=True)
    for w in weights:
        for s in subs:
            f = f"{d}-{s}-{w}-normal.woff2"
            if not os.path.exists(os.path.join(src, f)): continue
            shutil.copy(os.path.join(src, f), os.path.join(dst, f))
            rng = HEB if s == "hebrew" else LAT
            css.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:block;"
                       f"src:url(fonts/{d}/{f}) format('woff2');unicode-range:{rng};}}")
open(os.path.join(T, "vendor/fonts.css"), "w").write("\n".join(css) + "\n")
print(f"fonts.css: {len(css)} faces")
PY
cp "$HERE/engine.js" "$T/vendor/engine.js"
echo "vendor ready in $T/vendor (gsap.min.js, fonts.css, engine.js). Playwright module: $T/.deps/node_modules/playwright"
