import numpy as np, re, vtracer, sys
from PIL import Image
from scipy import ndimage as ndi
def prep(img,scale,is_magenta_bg=True,white_bg=False):
    im=img.convert("RGB")
    im=im.resize((im.width*scale,im.height*scale),Image.LANCZOS)
    a=np.array(im).astype(np.int32)
    if white_bg:
        bg=(a.min(axis=2)>228)
    else:
        bg=(a[...,0]>170)&(a[...,2]>140)&(a[...,1]<140)&(a[...,0]-a[...,1]>70)&(a[...,2]-a[...,1]>50)
    bg=ndi.binary_opening(bg,iterations=1)
    near=ndi.binary_dilation(bg,iterations=scale*1+1)&~bg
    keep=~(bg|near)
    idx=ndi.distance_transform_edt(~keep,return_distances=False,return_indices=True)
    out=a[idx[0],idx[1]]
    out[bg]=(255,0,255)
    return Image.fromarray(out.astype(np.uint8))
def trace(img,out,**kw):
    img.save("_t.png")
    vtracer.convert_image_to_svg_py("_t.png",out,colormode="color",hierarchical="stacked",mode="spline",filter_speckle=kw.get("speck",6),color_precision=kw.get("cp",6),layer_difference=kw.get("ld",12),corner_threshold=60,length_threshold=4.0,max_iterations=10,splice_threshold=45,path_precision=2)
def paths(svg,drop_magenta=True):
    s=open(svg).read(); w=int(re.search(r'width="(\d+)"',s).group(1)); h=int(re.search(r'height="(\d+)"',s).group(1))
    ps=re.findall(r'<path[^>]*/>',s); keep=[]
    for p in ps:
        m=re.search(r'fill="#([0-9a-fA-F]{6})"',p)
        if drop_magenta and m:
            r,g,b=[int(m.group(1)[i:i+2],16) for i in (0,2,4)]
            if r>190 and b>190 and g<90: continue
        keep.append(p)
    return w,h,keep
if __name__=="__main__":
    art=Image.open("poster_art_0.png").convert("RGB")
    import numpy as _np
    arr=_np.array(art).astype(int); bgm=(arr[...,0]>170)&(arr[...,2]>140)&(arr[...,1]<140); ys,xs=_np.where(~bgm)
    bx=(max(0,xs.min()-12),max(0,ys.min()-12),min(art.width,xs.max()+12),min(art.height,ys.max()+12)); print("bbox",bx); art=art.crop(bx)
    a=prep(art,2); trace(a,"art_raw.svg",speck=10,cp=6,ld=14)
    w,h,ps=paths("art_raw.svg"); print("art",w,h,len(ps))
    open("art_paths.txt","w").write("\n".join(ps)); open("art_size.txt","w").write(f"{w} {h}")
