# -*- coding: utf-8 -*-
"""מכין נכסים לרינדור: python3 toldot-video/build/key_sprites.py ואז python3 toldot-video/build/prep_assets.py (מריצים מתיקיית toldot-video)."""
import glob,os,json,shutil
from PIL import Image
os.makedirs('build/web/assets/plates',exist_ok=True); os.makedirs('build/web/assets/sprites',exist_ok=True)
for f in glob.glob('art/plates/P*.jpg'): shutil.copy(f,'build/web/assets/plates/')
meta={}
for f in sorted(glob.glob('build/sprites_rgba/S*.png')):
    im=Image.open(f); bb=im.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox(); im=im.crop(bb)
    s=900/max(im.size); im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS)
    n=os.path.basename(f)[:3]; im.save(f'build/web/assets/sprites/{n}.png',optimize=True); meta[n]=im.size
json.dump(meta,open('build/web/assets/sprites.json','w'))
