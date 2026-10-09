#!/usr/bin/env bash
# QA for a rendered video: probe, loudness, contact sheet, motion strips, black/freeze detection.
# Usage: qa.sh video.mp4 [outDir=./qa] [times="1,3,6,10,15,20,25,29"]
set -euo pipefail
V="$1"; O="${2:-./qa}"; TIMES="${3:-1,3,6,10,15,20,25,29}"; mkdir -p "$O"
echo "== probe"; ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,duration,channels -of compact "$V"
echo "== loudness (target about -14 LUFS integrated, true peak <= -1 dBTP for social)"
ffmpeg -hide_banner -nostats -i "$V" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|LRA|Peak):|I:|Peak:" | tail -4 || true
echo "== black frames / frozen frames (should be none except intentional fade at the end)"
ffmpeg -hide_banner -nostats -i "$V" -vf "blackdetect=d=0.15:pic_th=0.98" -an -f null - 2>&1 | grep -E "black_start" | head -5 || true
ffmpeg -hide_banner -nostats -i "$V" -vf "freezedetect=n=-60dB:d=0.7" -an -f null - 2>&1 | grep -E "freeze_(start|duration)" | head -10 || true
echo "== contact sheet"
IFS=',' read -ra T <<< "$TIMES"; ARGS=(); FILT=""; i=0
for t in "${T[@]}"; do ffmpeg -loglevel error -y -ss "$t" -i "$V" -frames:v 1 "$O/f_$t.png"; ARGS+=(-i "$O/f_$t.png"); FILT+="[$i]"; i=$((i+1)); done
ffmpeg -loglevel error -y "${ARGS[@]}" -filter_complex "${FILT}hstack=inputs=$i,scale=2000:-1" "$O/contact.png"
echo "wrote $O/contact.png"
echo "== motion strip (12 consecutive frames at t=${T[1]} - checks easing/overlap/blur)"
ffmpeg -loglevel error -y -ss "${T[1]}" -i "$V" -vf "select='not(mod(n\,2))',scale=270:-1,tile=12x1" -frames:v 1 "$O/strip.png" && echo "wrote $O/strip.png"
echo "== audio waveform/energy over time (peaks should line up with visual hits)"
ffmpeg -loglevel error -y -i "$V" -filter_complex "showwavespic=s=2000x300:colors=#ff7a1a" -frames:v 1 "$O/wave.png" && echo "wrote $O/wave.png"
