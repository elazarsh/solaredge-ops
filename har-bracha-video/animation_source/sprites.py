import numpy as np, json
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from collections import deque
A="assets/"; IN="in/"
SET={
 "pigeon":{"base":IN+"pigeon_in.png","open":A+"pigeon_A_open.png","tired":A+"pigeon_B_tired.png","tired_open":A+"pigeon_C_tired_open.png"},
 "yossi":{"base":IN+"yossi_in.png","open":A+"yossi_A_open.png","groan_open":A+"yossi_B_groan.png","groan":A+"yossi_C_groan_closed.png"},
 "liat":{"base":A+"liat_base_closed.png","open":A+"liat_A_open.png","pout":A+"liat_B_pout.png","pout_open":A+"liat_C_pout_open.png"},
}
def cut(path):
    im=Image.open(path).convert("RGB"); a=np.array(im).astype(int); h,w,_=a.shape
    bg=np.median(np.concatenate([a[:6,:6].reshape(-1,3),a[:6,-6:].reshape(-1,3),a[-6:,:6].reshape(-1,3)]),axis=0)
    cand=np.abs(a-bg).sum(axis=2)<70
    lab,n=ndi.label(cand)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bgmask=np.isin(lab,list(border))
    fg=~bgmask
    # keep largest component of fg
    l2,n2=ndi.label(ndi.binary_dilation(fg,iterations=2))
    sizes=ndi.sum(fg,l2,range(1,n2+1)); keep=1+int(np.argmax(sizes))
    fg=fg&(l2==keep)
    alpha=(fg*255).astype(np.uint8)
    alpha=np.array(Image.fromarray(alpha).filter(__import__("PIL.ImageFilter",fromlist=["x"]).GaussianBlur(0.8)))
    rgba=np.dstack([a.astype(np.uint8),alpha]); img=Image.fromarray(rgba,"RGBA")
    return img.crop(img.getbbox())
def blink_version(img):
    a=np.array(img); rgb=a[...,:3].astype(int); al=a[...,3]>128
    h,w=al.shape
    white=(rgb.min(axis=2)>185)&(rgb[...,0]-rgb[...,2]<75)&al
    white[int(h*0.46):]=False   # eyes only in the upper half
    lab,n=ndi.label(white)
    blobs=[]
    for i in range(1,n+1):
        m=lab==i; ar=m.sum()
        if ar>0.0025*h*w and ar<0.08*h*w: blobs.append((ar,i))
    blobs=sorted(blobs,reverse=True)[:2]
    out=img.copy(); d=ImageDraw.Draw(out); op=np.array(out)
    for ar,i in blobs:
        m=ndi.binary_fill_holes(lab==i); m=ndi.binary_dilation(m,iterations=3)
        ring=ndi.binary_dilation(m,iterations=9)&~m&al
        cols=rgb[ring]; cols=cols[cols.sum(axis=1)>240]
        skin=np.median(cols,axis=0).astype(np.uint8) if len(cols) else np.array([170,130,80],np.uint8)
        op[m&al,:3]=skin
        ys,xs=np.where(m); cx0,cx1=xs.min(),xs.max(); cy=int(ys.mean())
        out=Image.fromarray(op,"RGBA"); d=ImageDraw.Draw(out)
        d.arc((cx0,cy-int((cx1-cx0)*0.18),cx1,cy+int((cx1-cx0)*0.18)),20,160,fill=(25,15,8,255),width=max(4,int(w*0.012)))
        op=np.array(out)
    return Image.fromarray(op,"RGBA"),len(blobs)
meta={}
H=900
for ch,vs in SET.items():
    base=cut(vs["base"]); bh=base.height
    meta[ch]={}
    for name,p in vs.items():
        img=cut(p)
        s=H/img.height if name!="base" else H/bh
        img=img.resize((int(img.width*s),H),Image.LANCZOS)
        img.save(f"sprites/{ch}_{name}.png")
        bl,nb=blink_version(img); bl.save(f"sprites/{ch}_{name}_blink.png")
        meta[ch][name]=[img.width,img.height,nb]
        print(ch,name,img.size,"eyes",nb)
json.dump(meta,open("sprites/meta.json","w"))
