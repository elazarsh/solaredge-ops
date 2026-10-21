#!/usr/bin/env bash
# Pre-flight: one snapshot per beat (from beat-grid.py JSON) before the full render.
# Look for anything off the grid, cramped or hard to read, then fix before rendering.
# Usage (inside a HyperFrames project dir): bash video-studio/tools/beat-frames.sh grid.json [offset_s=0] [max_beats=40]
set -euo pipefail
grid="${1:?usage: beat-frames.sh grid.json [offset] [max]}"; off="${2:-0}"; max="${3:-40}"
at=$(python3 -c "import json,sys;g=json.load(open('$grid'));b=g['beats'];t0=b[0]
print(','.join(f'{t-t0+$off+0.001:.3f}' for t in b[:$max]))")
npx --yes hyperframes@0.8.96 snapshot --no-end --at "$at" -o snapshots/beats
echo "Read snapshots/beats/contact-sheet.jpg (one frame per beat)."
