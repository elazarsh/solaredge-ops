import sys
from PIL import Image,ImageDraw
ids=sys.argv[2:];out=sys.argv[1]
w,h=480,270;cols=4;rows=(len(ids)+cols-1)//cols
W=Image.new('RGB',(cols*w,rows*h),'white');d=ImageDraw.Draw(W)
for i,k in enumerate(ids):
    im=Image.open(f'img/{k}.png').convert('RGB').resize((w,h));W.paste(im,((i%cols)*w,(i//cols)*h));d.text(((i%cols)*w+6,(i//cols)*h+4),k,fill=(255,0,0))
W.save(out,quality=80)
