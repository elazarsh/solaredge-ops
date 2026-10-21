#!/usr/bin/env python3
"""Contact sheet of rendered snapshots. usage: sheet.py out.png cols w h file..."""
import subprocess, sys
out, cols, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
files = sys.argv[5:]
cmd = ['ffmpeg', '-v', 'error', '-y']
for f in files: cmd += ['-i', f]
n = len(files)
filt = ''.join(f'[{i}:v]scale={w}:{h}[v{i}];' for i in range(n)) + ''.join(f'[v{i}]' for i in range(n)) \
     + f'xstack=inputs={n}:layout=' + '|'.join(f'{(i % cols) * w}_{(i // cols) * h}' for i in range(n)) + '[o]'
subprocess.run(cmd + ['-filter_complex', filt, '-map', '[o]', out], check=True)
