"""Contact sheets: grid of numbered thumbnails for fast visual review.

usage: python contact.py OUT_PREFIX PATH [PATH ...] [--flat] [--per N] [--cols C] [--size PX]
  PATH = folder (recursive unless --flat) or single image file.
Writes OUT_PREFIX_01.jpg, _02.jpg ... and OUT_PREFIX_index.tsv (sheet, num, path, WxH, KB).
"""
import os, sys, argparse
from PIL import Image, ImageDraw, ImageFont, ImageOps
sys.path.insert(0, os.path.dirname(__file__))
from common import lp, walk_files, IMG_EXT, utf8_stdout

Image.MAX_IMAGE_PIXELS = None


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--flat', action='store_true')
    ap.add_argument('--per', type=int, default=20)
    ap.add_argument('--cols', type=int, default=5)
    ap.add_argument('--size', type=int, default=300)
    ap.add_argument('--skipdups', action='store_true', help='skip files that are duplicates of a canonical copy elsewhere')
    a = ap.parse_args()
    files = []
    for p in a.paths:
        files += list(walk_files(p, IMG_EXT, recursive=not a.flat, skipdups=a.skipdups))
    if not files:
        print('no images'); return
    try:
        font = ImageFont.truetype('arial.ttf', 22)
    except Exception:
        font = ImageFont.load_default()
    S = a.size
    rows_out = []
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or '.', exist_ok=True)
    nsheets = (len(files) + a.per - 1) // a.per
    for si in range(nsheets):
        chunk = files[si * a.per:(si + 1) * a.per]
        rows = (len(chunk) + a.cols - 1) // a.cols
        sheet = Image.new('RGB', (a.cols * (S + 10) + 10, rows * (S + 40) + 10), 'white')
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            num = si * a.per + i + 1
            x = 10 + (i % a.cols) * (S + 10)
            y = 10 + (i // a.cols) * (S + 40)
            wh, kb = '?', 0
            try:
                kb = os.path.getsize(lp(f)) // 1024
                im = Image.open(lp(f))
                im = ImageOps.exif_transpose(im)
                wh = f'{im.width}x{im.height}'
                im = im.convert('RGB')
                im.thumbnail((S, S))
                sheet.paste(im, (x + (S - im.width) // 2, y + (S - im.height) // 2))
            except Exception as e:
                d.rectangle([x, y, x + S, y + S], outline='red')
                d.text((x + 5, y + S // 2), 'ERR', fill='red', font=font)
            d.rectangle([x, y + S + 2, x + 60, y + S + 30], fill='black')
            d.text((x + 4, y + S + 4), f'#{num}', fill='yellow', font=font)
            d.text((x + 66, y + S + 8), wh, fill='gray', font=ImageFont.load_default())
            rows_out.append((si + 1, num, f, wh, kb))
        sheet.save(f'{a.out}_{si + 1:02d}.jpg', quality=82)
    with open(a.out + '_index.tsv', 'w', encoding='utf-8') as fh:
        fh.write('sheet\tnum\tpath\twh\tkb\n')
        for r in rows_out:
            fh.write('\t'.join(map(str, r)) + '\n')
    print(f'{len(files)} images -> {nsheets} sheets: {a.out}_01..{nsheets:02d}.jpg ; index {a.out}_index.tsv')


if __name__ == '__main__':
    main()
