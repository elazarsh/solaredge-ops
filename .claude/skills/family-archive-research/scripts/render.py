"""Render PDF pages / downscale big images to PNG/JPG so they can be viewed (Read tool).

usage: python render.py OUTDIR PATH [PATH ...] [--dpi 150] [--pages 1-5] [--max 1800]
  PDF -> OUTDIR/<stem>_p<N>.png ; image -> OUTDIR/<stem>.jpg (max side --max px, EXIF-rotated)
  --crop x0,y0,x1,y1 (fractions 0-1) crops images (for zooming into a detail).
"""
import os, sys, argparse, re
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(__file__))
from common import lp, walk_files, IMG_EXT, utf8_stdout

Image.MAX_IMAGE_PIXELS = None


def safe(s):
    return re.sub(r'[<>:"/\\|?*]', '_', s)[:80]


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--pages', default=None)
    ap.add_argument('--max', type=int, default=1800)
    ap.add_argument('--crop', default=None)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for root in a.paths:
        for f in walk_files(root, IMG_EXT | {'.pdf'}):
            stem = safe(os.path.splitext(os.path.basename(f))[0])
            if f.lower().endswith('.pdf'):
                import fitz
                doc = fitz.open(lp(f))
                rng = range(len(doc))
                if a.pages:
                    s, _, e = a.pages.partition('-')
                    rng = range(int(s) - 1, min(len(doc), int(e or s)))
                for i in rng:
                    pix = doc[i].get_pixmap(dpi=a.dpi)
                    out = os.path.join(a.outdir, f'{stem}_p{i + 1}.png')
                    pix.save(out)
                    print(out)
            else:
                im = ImageOps.exif_transpose(Image.open(lp(f))).convert('RGB')
                if a.crop:
                    x0, y0, x1, y1 = map(float, a.crop.split(','))
                    im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
                    stem += '_crop'
                im.thumbnail((a.max, a.max))
                out = os.path.join(a.outdir, f'{stem}.jpg')
                im.save(out, quality=88)
                print(out, f'{im.width}x{im.height}')


if __name__ == '__main__':
    main()
