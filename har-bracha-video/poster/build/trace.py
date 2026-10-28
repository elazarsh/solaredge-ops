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
    art=Image.open("poster_art_0.png"); a=prep(art,2); trace(a,"art_raw.svg",speck=10,cp=6,ld=14)
    w,h,ps=paths("art_raw.svg"); print("art",w,h,len(ps))
    open("art_paths.txt","w").write("\n".join(ps)); open("art_size.txt","w").write(f"{w} {h}")
    # logos
    L="/tmp/claude-0/-home-user-solaredge-ops/b739defe-bfc9-5521-91fd-2d6f235476f6/images/"
    hb=Image.open(L+"1.png").convert("RGBA"); bg=Image.new("RGBA",hb.size,(255,0,255,255)); 
    # hard alpha to avoid pink fringe: composite onto white first then white->bg
    wbg=Image.new("RGBA",hb.size,(255,255,255,255)); wbg.alpha_composite(hb)
    t1=prep(wbg,2,white_bg=True); trace(t1,"hb_raw.svg",speck=6,cp=7,ld=10); w,h,ps=paths("hb_raw.svg"); print("hb",w,h,len(ps)); open("hb_paths.txt","w").write("\n".join(ps)); open("hb_size.txt","w").write(f"{w} {h}")
    cc=Image.open(L+"3.jpg"); t2=prep(cc,4,white_bg=True); trace(t2,"cc_raw.svg",speck=8,cp=7,ld=10); w,h,ps=paths("cc_raw.svg"); print("cc",w,h,len(ps)); open("cc_paths.txt","w").write("\n".join(ps)); open("cc_size.txt","w").write(f"{w} {h}")
