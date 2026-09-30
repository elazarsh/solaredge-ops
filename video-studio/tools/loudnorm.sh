#!/usr/bin/env bash
# Two-pass loudness normalization to -14 LUFS / -1 dBTP; video stream is copied.
# Usage: bash video-studio/tools/loudnorm.sh <in.mp4> [out.mp4] [target_lufs=-14]
set -euo pipefail
in="${1:?usage: loudnorm.sh <in> [out] [lufs]}"; out="${2:-${in%.*}.norm.mp4}"; I="${3:--14}"
m=$(ffmpeg -hide_banner -nostats -i "$in" -af "loudnorm=I=$I:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { python3 -c "import json,sys;print(json.loads(sys.stdin.read())['$1'])" <<<"$m"; }
ffmpeg -hide_banner -loglevel error -y -i "$in" -c:v copy \
  -af "loudnorm=I=$I:TP=-1.5:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true" \
  -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$out"
echo "$out"
