#!/usr/bin/env python3
"""Clean the matte fringe from the gold title PNG. usage: defringe.py in.webp out.png"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
im = Image.open(sys.argv[1]).convert('RGBA')
a = np.array(im).astype(np.float32)
rgb, al = a[..., :3], a[..., 3] / 255.0
print('size', im.size, 'alpha min %.2f max %.2f' % (al.min(), al.max()),
      'opaque %.1f%% partial %.1f%% clear %.1f%%' % (100*(al > .98).mean(), 100*((al > .02) & (al <= .98)).mean(), 100*(al <= .02).mean()))
ys, xs = np.where(al > 0.05); print('bbox', xs.min(), ys.min(), xs.max(), ys.max())
solid = ndi.binary_erosion(al > 0.97, iterations=3)
idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
filled = rgb[idx[0], idx[1]]
al2 = ndi.gaussian_filter(np.clip((al - 0.18) / (0.97 - 0.18), 0, 1), 0.6)
out = np.dstack([filled, al2 * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(sys.argv[2])
for name, bg in (('dark', (10, 18, 24)), ('warm', (60, 40, 20))):
    for tag, src in (('', Image.fromarray(out, 'RGBA')), ('-orig', im)):
        base = Image.new('RGBA', im.size, bg + (255,)); base.alpha_composite(src)
        base.convert('RGB').save(f'build/snaps/title-{name}{tag}.jpg', quality=92)
