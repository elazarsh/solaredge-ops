#!/usr/bin/env bash
# Technical QA for a rendered ad: format, duration, fps, loudness, black/silent gaps.
# Usage: bash video-studio/tools/ad-qa.sh <video.mp4> [min_s=6] [max_s=60]
# Exit code 1 if any FAIL.
set -uo pipefail
f="${1:?usage: ad-qa.sh <video> [min_s] [max_s]}"; min="${2:-6}"; max="${3:-60}"
[ -f "$f" ] || { echo "no such file: $f" >&2; exit 2; }
fail=0
ok()   { printf 'PASS  %s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*"; }
bad()  { printf 'FAIL  %s\n' "$*"; fail=1; }
probe() { ffprobe -v error "$@" -of default=nw=1:nk=1 "$f"; }

w=$(probe -select_streams v:0 -show_entries stream=width); h=$(probe -select_streams v:0 -show_entries stream=height)
fps=$(probe -select_streams v:0 -show_entries stream=avg_frame_rate); fpsn=$(awk -F/ '{printf "%.2f", ($2?$1/$2:$1)}' <<<"$fps")
codec=$(probe -select_streams v:0 -show_entries stream=codec_name); pix=$(probe -select_streams v:0 -show_entries stream=pix_fmt)
dur=$(probe -show_entries format=duration); size=$(stat -c %s "$f")
acodec=$(probe -select_streams a:0 -show_entries stream=codec_name)

case "${w}x${h}" in
  1080x1920|1440x2560|720x1280) ok "resolution ${w}x${h} (9:16)";;
  1080x1080) ok "resolution ${w}x${h} (1:1)";;
  1080x1350) ok "resolution ${w}x${h} (4:5)";;
  1920x1080|1280x720) ok "resolution ${w}x${h} (16:9)";;
  *) bad "resolution ${w}x${h} is not a standard ad size";;
esac
awk -v d="$dur" -v a="$min" -v b="$max" 'BEGIN{exit !(d>=a && d<=b)}' && ok "duration ${dur}s (target ${min}-${max}s)" || bad "duration ${dur}s outside ${min}-${max}s"
awk -v r="$fpsn" 'BEGIN{exit !(r>=23.9 && r<=60.1)}' && ok "fps $fpsn" || bad "fps $fpsn"
[ "$codec" = h264 ] && ok "video codec h264" || warn "video codec $codec (h264 is safest)"
[ "$pix" = yuv420p ] && ok "pixel format yuv420p" || bad "pixel format $pix (use yuv420p for phones)"
[ "$size" -lt 104857600 ] && ok "file size $((size/1024/1024)) MB" || warn "file size $((size/1024/1024)) MB > 100 MB"

if [ -z "$acodec" ]; then
  warn "no audio track (OK only for a deliberate silent ad)"
else
  ok "audio codec $acodec"
  ln=$(ffmpeg -hide_banner -nostats -i "$f" -af ebur128=peak=true -f null - 2>&1 | tail -n 14)
  I=$(awk '/I:/{print $2}' <<<"$ln" | tail -1); TP=$(awk '/Peak:/{print $2}' <<<"$ln" | tail -1)
  awk -v i="$I" 'BEGIN{exit !(i>=-16 && i<=-11)}' && ok "loudness ${I} LUFS (target -14)" || bad "loudness ${I} LUFS (target -14; fix with tools/loudnorm.sh)"
  awk -v p="$TP" 'BEGIN{exit !(p<=-0.9)}' && ok "true peak ${TP} dBTP" || bad "true peak ${TP} dBTP > -1 (fix with tools/loudnorm.sh)"
  sil=$(ffmpeg -hide_banner -nostats -i "$f" -af silencedetect=n=-50dB:d=2 -f null - 2>&1 | grep -c silence_start || true)
  [ "$sil" -eq 0 ] && ok "no silent gaps ≥2s" || warn "$sil silent gap(s) ≥2s"
fi

blk=$(ffmpeg -hide_banner -nostats -i "$f" -vf blackdetect=d=0.5:pix_th=0.10 -an -f null - 2>&1 | grep -o 'black_start:[0-9.]*' || true)
if [ -z "$blk" ]; then ok "no black segments ≥0.5s"; else
  grep -q 'black_start:0$\|black_start:0\.0*$' <<<"$blk" && bad "video opens on black (kills the hook)" || warn "black segments: $(tr '\n' ' ' <<<"$blk")"
fi
frz=$(ffmpeg -hide_banner -nostats -t 1.5 -i "$f" -vf freezedetect=n=0.003:d=0.9 -an -f null - 2>&1 | grep -o 'freeze_start: *[0-9.]*' | head -1 || true)
[ -z "$frz" ] && ok "motion in the first second" || warn "frozen/static opening ($frz) — weak hook"

[ $fail -eq 0 ] && echo "RESULT: PASS" || echo "RESULT: FAIL"
exit $fail
