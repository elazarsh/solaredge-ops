# -*- coding: utf-8 -*-
"""פירוק לוגו מתנ"ס ולוגו הר ברכה לשכבות (לפי צבע+מיקום) לצורך אנימציה."""
import numpy as np, cv2, os, sys
from scipy import ndimage as ndi
from PIL import Image
SCR="/tmp/claude-0/-home-user-solaredge-ops/73fe8d55-5833-5852-9694-53b5adaa6cc2/scratchpad"
PAL={'blue':(15,117,186),'orange':(232,125,47),'magenta':(179,49,118),'green':(12,146,67),'lgreen':(138,195,65),'dgreen':(2,70,33)}
NAMES=list(PAL); P=np.array([PAL[n] for n in NAMES],np.float32)
def classify(rgb,fg):
    d=((rgb[...,None,:].astype(np.float32)-P)**2).sum(-1); cls=d.argmin(-1); cls[~fg]=-1; return cls
def assign(rgb,fg,rule):
    cls=classify(rgb,fg); H,W=cls.shape
    layer=np.full((H,W),-1,np.int32); names=[]
    def lid(n):
        if n not in names: names.append(n)
        return names.index(n)
    yy,xx=np.mgrid[0:H,0:W]
    inherit=np.zeros((H,W),bool)
    for k,n in enumerate(NAMES):
        lab,m=ndi.label(cls==k)
        if m==0: continue
        objs=ndi.find_objects(lab); sizes=ndi.sum(cls==k,lab,range(1,m+1))
        for i in range(m):
            sl=objs[i]; bb=(sl[1].start,sl[0].start,sl[1].stop,sl[0].stop); mask=lab==i+1
            if sizes[i]<60: inherit|=mask; continue
            r=rule(n,int(sizes[i]),bb,mask,xx,yy)
            if r=="inherit": inherit|=mask
            elif r is not None: layer[mask]=lid(r)
    # whitish/unassigned fg pixels -> nearest assigned layer
    miss=fg&(layer<0)|inherit
    if miss.any():
        _,(iy,ix)=ndi.distance_transform_edt(layer<0 if False else ~((layer>=0)&~inherit),return_indices=True)
        layer[miss]=layer[iy,ix][miss]
    return names,layer
def mrule(n,s,bb,mask,xx,yy):
    x0,y0,x1,y1=bb
    if s<1500 and not (n=='orange' and x0>=1060 and y1<=760): return 'inherit'
    if n=='blue': return 'text_matnas' if y0>=700 else 'person_blue'
    if n=='orange':
        if y0>=1000: return 'text_harbracha'
        if x0>=1200 and y1<=200 and s>20000: return 'sun'
        if s>=6000: return 'person_orange'
        return 'arc'
    if n=='magenta': return ('book' if x1<=700 else 'child') if s>1500 else 'inherit'
    if n=='lgreen': return ('heart' if (x0>=950 and x1<=1100 and y0>=180 and y1<=300) else 'inherit') if s<10000 else 'hill'
    if n=='green': return 'tree_big' if (x1<=450 or (x0>=316 and x1<=349)) and y0<=620 and s<30000 else 'hill'
    if n=='dgreen':
        return 'tree_dark' if True else None
def mrule2(n,s,bb,mask,xx,yy):
    r=mrule(n,s,bb,mask,xx,yy)
    if n=='dgreen':
        out=np.where((xx<420)&(yy<=610),1,0)
        # per-pixel split handled by caller via sub-mask
        return ('SPLIT',)
    return r
def build_matnas():
    rgb=np.array(Image.open(f"{SCR}/src/root/WhatsApp_Image_2026-01-13_at_20.48.02.jpeg").convert('RGB'))
    fg=np.abs(rgb.astype(int)-247).sum(2)>60
    names,layer=assign(rgb,fg,lambda n,s,bb,m,xx,yy: ('dsplit' if n=='dgreen' else mrule(n,s,bb,m,xx,yy)))
    # split dsplit by position
    H,W=layer.shape; yy,xx=np.mgrid[0:H,0:W]
    if 'dsplit' in names:
        d=names.index('dsplit'); names+=['tree_dark','hill_dark']
        td=names.index('tree_dark'); hd=names.index('hill_dark')
        m=layer==d; layer[m&(xx<420)&(yy<=610)]=td; layer[m&~((xx<420)&(yy<=610))]=hd
    return rgb,fg,names,layer
def hrule(img):
    def rule(n,s,bb,mask,xx,yy):
        x0,y0,x1,y1=bb
        if n=='blue': return 'tower' if s>10000 else 'tree_right'
        if n=='orange': return 'bldg_orange' if s>10000 else 'bldg_back'
        if n=='magenta': return 'tree_pink' if y0>=160 and x1<=380 else 'book'
        if n=='green':
            if y0>=640: return 'text_name'
            if s>15000: return 'house'
            if 380<=x0<=830 and 380<=y0<=480 and s<4000: return 'kids'
            return 'hill'
        if n=='lgreen':
            if s>40000: return 'hill'
            if x1<=210: return 'tree_left'
            return 'inherit'
        if n=='dgreen':
            if y0>=830: return 'text_sub'
            if x1<=300 and y0<400: return 'tree_left'
            if x0>=780 and y1<=540: return 'tree_right'
            if s>10000: return 'kids'
            return 'inherit'
    return rule
def build_hb():
    a=np.array(Image.open("/tmp/claude-0/-home-user-solaredge-ops/73fe8d55-5833-5852-9694-53b5adaa6cc2/images/2.png"))
    rgb=a[...,:3]; fg=a[...,3]>40
    names,layer=assign(rgb,fg,hrule(rgb))
    return a,fg,names,layer
def export(src_rgb,alpha_src,fg,names,layer,outdir,bgcol=None):
    os.makedirs(outdir,exist_ok=True)
    H,W=layer.shape
    # soft alpha: use fg coverage (blur) for smooth edges
    if alpha_src is None:
        dist=np.abs(src_rgb.astype(np.float32)-np.array(bgcol,np.float32)).sum(2)
        cov=np.clip((dist-30)/140,0,1)
    else: cov=alpha_src.astype(np.float32)/255
    res={}
    for i,n in enumerate(names):
        m=(layer==i)
        if not m.any(): continue
        md=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8))>0
        al=cov*md  # slight overlap to hide seams
        rgba=np.dstack([src_rgb,(al*255).astype(np.uint8)])
        ys,xs=np.where(al>0.02)
        if len(ys)==0: continue
        bb=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
        Image.fromarray(rgba).save(f"{outdir}/{n}.png"); res[n]=bb
    return res
if __name__=="__main__":
    rgb,fg,names,layer=build_matnas()
    r1=export(rgb,None,fg,names,layer,f"{SCR}/logo_m",bgcol=(247,247,247)); print(r1)
    a,fg,names,layer=build_hb()
    r2=export(a[...,:3],a[...,3],fg,names,layer,f"{SCR}/logo_h"); print(r2)
