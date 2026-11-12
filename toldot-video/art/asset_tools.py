"""Local production utilities. Preserve raw generations before centered 9:16 crops.

Usage: python3 toldot-video/art/asset_tools.py format P16 P18 P20
       python3 toldot-video/art/asset_tools.py audit
       python3 toldot-video/art/asset_tools.py sheets
Formatting never approves an image: inspect the cropped output separately.
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ART = Path(__file__).resolve().parent

def main():
    manifest = ART / 'manifest.json'
    data = json.loads(manifest.read_text())
    command = sys.argv[1]
    if command == 'format':
        for item in data['images']:
            if item['id'] not in sys.argv[2:]:
                continue
            path = ART / item['file']
            with Image.open(path) as source:
                image = source.convert('RGB')
            original = ART / 'refs' / (path.stem + '_generated.png')
            if original.exists():
                raise SystemExit(f'Refusing to overwrite preserved raw image: {original}')
            image.save(original)
            width, height = image.size
            crop_width = min(width, round(height * 9 / 16))
            crop_height = min(height, round(width * 16 / 9))
            left, top = (width - crop_width) // 2, (height - crop_height) // 2
            box = [left, top, left + crop_width, top + crop_height]
            image = image.crop(box)
            image.save(path, format='JPEG', quality=95, subsampling=0)
            item['processing'] = {'original': str(original.relative_to(ART)),
                                  'crop': box, 'encoding': 'JPEG quality95, chroma 4:4:4'}
            item['dimensions'] = list(image.size)
            item['aspect'] = f'{image.width}:{image.height}'
            print(item['id'], image.size, 'visual crop review required')
        manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    elif command == 'audit':
        approved = [i for i in data['images'] if i['status'] == 'approved' and i['type'] in ('plate', 'sprite')]
        covered = {b for i in approved for b in i['beats']}
        missing = sorted(set(range(76)) - covered)
        print(f'{len(approved)} approved assets; approved coverage missing: {missing}')
        print('Coverage labels require visual review against beats.csv; this check cannot prove content.')
        raise SystemExit(bool(missing))
    elif command == 'sheets':
        (ART / 'sheets').mkdir(exist_ok=True)
        for kind in ('plate', 'sprite'):
            items = sorted((i for i in data['images'] if i['type'] == kind), key=lambda i: i['id'])
            for start in range(0, len(items), 12):
                batch = items[start:start+12]
                sheet = Image.new('RGB', (1000, ((len(batch)+3)//4)*480), '#eeeeee')
                draw = ImageDraw.Draw(sheet)
                for n, item in enumerate(batch):
                    with Image.open(ART / item['file']) as source:
                        thumb = ImageOps.contain(source.convert('RGB'), (240, 440))
                    x, y = n % 4 * 250, n // 4 * 480
                    sheet.paste(thumb, (x+(240-thumb.width)//2, y))
                    draw.text((x+5, y+445), item['id']+' '+item['status'], fill='black')
                sheet.save(ART / 'sheets' / f'{kind}s_{start//12+1:02}.jpg', quality=95)
    else:
        raise SystemExit('Expected format, audit or sheets')

if __name__ == '__main__':
    main()
