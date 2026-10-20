import numpy as np, glob, json
from PIL import Image
from scipy import ndimage as ndi
files=sorted(glob.glob('fr/f*.png'))
S=0.64  # scale
info=[]
for i,f in enumerate(files):
    a=np.array(Image.open(f).convert('RGB')).astype(np.float32)
    border=np.concatenate([a[:8].reshape(-1,3),a[-8:].reshape(-1,3),a[:,:8].reshape(-1,3),a[:,-8:].reshape(-1,3)])
    bg=np.median(border,0)
    d=np.sqrt(((a-bg)**2).sum(2))
    cand=d<34
    lab,n=ndi.label(cand)
    sizes=ndi.sum(cand,lab,range(1,n+1))
    keep=np.zeros(n+1,bool)
    # border-connected components or large components -> background
    bl=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    for k in range(1,n+1):
        if k in bl or sizes[k-1]>1500: keep[k]=True
    bgm=keep[lab]
    fg=~bgm
    fg=ndi.binary_opening(fg,iterations=1)
    lab2,n2=ndi.label(fg); 
    if n2>1:
        sz=ndi.sum(fg,lab2,range(1,n2+1)); fg=lab2==(1+int(np.argmax(sz)))
    fg=ndi.binary_fill_holes(fg) if False else fg
    fg=ndi.binary_erosion(fg,iterations=1)
    al=ndi.gaussian_filter(fg.astype(np.float32),0.8)
    al=np.clip((al-0.2)/0.6,0,1)
    out=np.dstack([a,al*255]).astype(np.uint8)
    im=Image.fromarray(out,'RGBA')
    ys,xs=np.where(fg)
    info.append((int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())))
    im.save(f'rgba/r{i+1:03d}.png')
    if i%30==0: print(i,bg,info[-1],flush=True)
json.dump(info,open('bbox.json','w'))
