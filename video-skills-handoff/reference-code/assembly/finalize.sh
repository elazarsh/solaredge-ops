#!/bin/bash
# usage: finalize.sh TAG   (renders current state: real Veo clips where present, fallback elsewhere)
cd "$(dirname "$0")"
TAG=${1:-interim}
python3 render2.py || exit 1
../tts/v/bin/python mix_full.py || exit 1
ffmpeg -v error -y -i tmp/video_final.mp4 -i out/mix_full.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out/film_$TAG.mp4 || exit 1
ls -la out/film_$TAG.mp4
python3 -c "import json;t=json.load(open('tmp/timeline.json'));print('fallbacks:',len(t['fallbacks']),'of',len(t['segs']))"
