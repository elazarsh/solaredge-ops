import sys,glob,os
from PIL import Image,ImageDraw
ts=[float(x) for x in sys.argv[2:]];out=sys.argv[1]
n=len(ts);cols=2;rows=(n+1)//2
W,H=960,540
sh=Image.new('RGB',(W*cols,H*rows))
for k,t in enumerate(ts):
    im=Image.open(f'tmp/q/{t:.1f}.jpg').resize((W,H));d=ImageDraw.Draw(im);d.rectangle([0,0,110,26],fill=(0,0,0));d.text((6,6),f't={t:.1f}',fill=(255,255,0))
    sh.paste(im,((k%cols)*W,(k//cols)*H))
sh.save(out,quality=85)
