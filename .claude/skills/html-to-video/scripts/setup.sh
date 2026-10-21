#!/bin/bash
# מתקין תלויות מקומיות לעבודה עם HTML->וידאו: playwright-core (בלי הורדת דפדפן), gsap ופונט Heebo (מקומי, לא CDN).
# שימוש: bash setup.sh [תיקיית עבודה=.]   -> יוצר <dir>/node_modules, <dir>/gsap.min.js, <dir>/fonts/heebo-*.woff2
set -e
D=${1:-.}; mkdir -p "$D/fonts"; cd "$D"
[ -f package.json ] || npm init -y >/dev/null
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --no-audit --no-fund playwright-core gsap @fontsource/heebo >/dev/null
cp node_modules/gsap/dist/gsap.min.js ./gsap.min.js
for w in 400 700 900; do for s in hebrew latin; do cp node_modules/@fontsource/heebo/files/heebo-$s-$w-normal.woff2 fonts/; done; done
echo "ok: $(ls fonts | wc -l) fonts, gsap $(wc -c < gsap.min.js) bytes"
ls /opt/pw-browsers 2>/dev/null | grep -q chromium && echo "Chromium: $(ls -d /opt/pw-browsers/chromium-* | head -1)" || echo "אזהרה: אין Chromium ב-/opt/pw-browsers (הגדר PLAYWRIGHT_BROWSERS_PATH או CHROMIUM_PATH)"
