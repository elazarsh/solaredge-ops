#!/usr/bin/env bash
# One-command build: vendor setup (once) -> deterministic render with motion blur -> procedural audio -> loudness normalise -> mux to MP4.
# Usage: build.sh <project_dir> [composition=index.html] [out=video.mp4]
# Config via env: FPS=30 DURATION=30 W=1080 H=1920 SUB=4 SHUTTER=0.5 WORKERS=4 BPM=120 ENERGY="0:0.3,4:0.8" KEY=A
# Loudness via env: LUFS=-14 (final integrated) TRUE_PEAK=-2.5 (dBTP before AAC; AAC 160-256k adds up to ~0.6 dB, delivery limit -1.5) LRA=11
#   PRE_LUFS=-15 (sfx.py --lufs) SFX_CEILING=TRUE_PEAK-(LUFS-PRE_LUFS) (sfx.py --ceiling, so the loudnorm gain stays linear)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; P="$(cd "$1" && pwd)"; COMP="${2:-index.html}"; OUT="${3:-video.mp4}"
FPS="${FPS:-30}"; DURATION="${DURATION:-30}"; W="${W:-1080}"; H="${H:-1920}"; SUB="${SUB:-4}"; SHUTTER="${SHUTTER:-0.5}"; WORKERS="${WORKERS:-4}"
BPM="${BPM:-120}"; ENERGY="${ENERGY:-0:0.3,4:0.8}"; KEY="${KEY:-A}"
LUFS="${LUFS:--14}"; TRUE_PEAK="${TRUE_PEAK:--2.5}"; LRA="${LRA:-11}"; PRE_LUFS="${PRE_LUFS:--15}"
SFX_CEILING="${SFX_CEILING:-$(awk -v tp="$TRUE_PEAK" -v i="$LUFS" -v p="$PRE_LUFS" 'BEGIN { print tp - (i - p) }')}"

# Two-pass ffmpeg loudnorm, linear gain only: pass 1 measures (print_format=json), pass 2 applies the measured_* values with
# linear=true. The I target is lowered if needed (I <= measured_I + TRUE_PEAK - measured_TP) and the LRA target raised to the
# measured LRA, so loudnorm never falls back to its dynamic (AGC) mode. Writes a 48 kHz 24-bit wav for the AAC encode.
loudnorm_wav() {
  local in="$1" out="$2" m af
  m="$(ffmpeg -hide_banner -nostats -i "$in" -af "loudnorm=I=${LUFS}:TP=${TRUE_PEAK}:LRA=${LRA}:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')"
  af="$(python3 -c '
import json, math, sys
m = json.loads(sys.argv[1]); I, TP, LRA = map(float, sys.argv[2:5])
mi, mtp, mlra, mth, off = (float(m[k]) for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"))
if not math.isfinite(mi) or mi < -60: print("anull"); sys.exit()
i_eff = max(-70.0, min(I, math.floor((mi + TP - mtp) * 10) / 10)); lra_eff = min(50.0, max(LRA, math.ceil(mlra * 10) / 10 + 0.1))
if i_eff < I: print(f"loudnorm: true peak limits the linear gain, target lowered to {i_eff} LUFS", file=sys.stderr)
print(f"loudnorm=I={i_eff}:TP={TP}:LRA={lra_eff}:measured_I={mi}:measured_TP={mtp}:measured_LRA={mlra}:measured_thresh={mth}"
      f":offset={off}:linear=true:print_format=summary,aresample=48000")
' "$m" "$LUFS" "$TRUE_PEAK" "$LRA")"
  ffmpeg -hide_banner -nostats -y -i "$in" -af "$af" -c:a pcm_s24le "$out" 2>&1 | grep -E "Normalization Type|Output Integrated|Output True Peak" || true
}

[ -f "$P/vendor/gsap.min.js" ] || "$HERE/setup.sh" "$P"
cp "$HERE/engine.js" "$P/vendor/engine.js"
export PLAYWRIGHT_MODULE="$P/.deps/node_modules/playwright"
FR="$P/.frames"; rm -rf "$FR"; mkdir -p "$FR"
node "$HERE/render.js" "$P/$COMP" "$FR" --fps "$FPS" --duration "$DURATION" --w "$W" --h "$H" --sub "$SUB" --shutter "$SHUTTER" --workers "$WORKERS"
python3 "$HERE/sfx.py" "$FR/cues.json" "$FR/audio.wav" --duration "$DURATION" --bpm "$BPM" --energy "$ENERGY" --key "$KEY" \
  --lufs "$PRE_LUFS" --ceiling "$SFX_CEILING"
loudnorm_wav "$FR/audio.wav" "$FR/audio_norm.wav"
# average the SUB sub-frames of every frame (temporal supersampling = real motion blur), keep one output frame per group
if [ "$SUB" -gt 1 ]; then
  VF="tmix=frames=${SUB},select='eq(mod(n\,${SUB})\,$((SUB-1)))',setpts=N/${FPS}/TB"; IN_FPS=$((FPS*SUB))
else VF="setpts=N/${FPS}/TB"; IN_FPS=$FPS; fi
ffmpeg -loglevel error -y -framerate "$IN_FPS" -i "$FR/s_%06d.png" -i "$FR/audio_norm.wav" -vf "$VF,format=yuv420p" \
  -r "$FPS" -c:v libx264 -preset slow -crf 16 -tune animation -c:a aac -b:a 256k -shortest -movflags +faststart "$P/$OUT"
echo "built $P/$OUT"
# final loudness check on the encoded file (target ~ -14 LUFS, true peak <= -1.5 dBTP)
ffmpeg -hide_banner -nostats -i "$P/$OUT" -vn -af ebur128=peak=true -f null - 2>&1 | grep -E '^ +(I|LRA|Peak):' | tr -s ' ' | paste -sd' ' || true
