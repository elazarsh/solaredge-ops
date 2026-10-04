#!/usr/bin/env bash
cd "$(dirname "$0")/.."
KEEP="Realistic handheld documentary video, very subtle natural camera movement, no cuts, no zoom. Only a man's hands and forearms in an olive-green polo sleeve are visible, no face ever. Bright warm window daylight. Sound: running tap water, soft dish clinks, quiet kitchen."
run(){ out=$1; shift; for m in veo-3.1-generate-preview veo-3.1-fast-generate-preview; do python3 gen/veo.py "$out" "$@" $m > gen/v-$(basename $out .mp4).log 2>&1 && [ -f "$out" ] && return 0; done; }
[ -f clips/sink-close.mp4 ] || run clips/sink-close.mp4 frames/sink1.jpg "$KEEP He scrubs the white plate under the running water for about three seconds. Then his right hand lifts off the plate, reaches to the chrome side lever of the tap at the left and pushes it down, and the running water stops completely. The tap is dry and still. Both hands then rest calmly on the edge of the sink. The camera stays steady."
