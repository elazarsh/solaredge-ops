import re,math,random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
FONT="fonts/Rubik900.ttf"; FONT2="fonts/Rubik800.ttf"
TW,TH=4000,2000; BL=20          # trim size (units = 0.5 mm) and bleed
def ink_text(txt,size,cx,cy,fontfile,mode="center"):
    ff=TTFont(fontfile); g2=ff.getGlyphSet(); cm=ff.getBestCmap(); u=ff["head"].unitsPerEm; hm=ff["hmtx"]
    vis=txt[::-1]; k=size/u; x=0; items=[]; xmin=1e9; xmax=-1e9; ymin=1e9; ymax=-1e9
    for c in vis:
        n=cm.get(ord(c)); a=hm[n][0] if n else u*0.3
        if n:
            bp=BoundsPen(g2); g2[n].draw(bp)
            if bp.bounds:
                x0,y0,x1,y1=bp.bounds; xmin=min(xmin,x+x0); xmax=max(xmax,x+x1); ymin=min(ymin,y0); ymax=max(ymax,y1)
            items.append((n,x))
        x+=a
    ox=cx-((xmin+xmax)/2)*k; oy=cy+((ymin+ymax)/2)*k
    out=[]
    for n,xx in items:
        pen=SVGPathPen(g2); g2[n].draw(pen); d=pen.getCommands()
        if d: out.append(f'<path transform="translate({ox+xx*k:.1f},{oy:.1f}) scale({k:.5f},{-k:.5f})" d="{d}"/>')
    return "\n".join(out),(xmax-xmin)*k,(ymax-ymin)*k
def read(n):
    w,h=map(int,open(f"{n}_size.txt").read().split()); return w,h,open(f"{n}_paths.txt").read()
aw,ah,art=read("hart"); hw,hh,hb=read("hb2"); cw,ch_,cc=read("cc")
# Shefa lockup: add department name under the settlement name
_,uw,_=ink_text('אגף שפ"ע',1000,0,0,FONT2); _sz=1180/uw*1000
_tp,_,_=ink_text('אגף שפ"ע',_sz,hw/2,1760,FONT2)
hb=hb+'<g fill="#22693A">'+_tp+'</g>'
random.seed(11)
X0,Y0,X1,Y1=-BL,-BL,TW+BL,TH+BL
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{(TW+2*BL)/2}mm" height="{(TH+2*BL)/2}mm" viewBox="{X0} {Y0} {TW+2*BL} {TH+2*BL}">']
svg.append(f'<rect id="background" x="{X0}" y="{Y0}" width="{TW+2*BL}" height="{TH+2*BL}" fill="#FFEFB8"/>')
# sunburst (flat colours, runs through bleed)
cx0,cy0=1150,1000; rays=[]; n=32
for i in range(0,n,2):
    a0=2*math.pi*i/n; a1=2*math.pi*(i+1)/n; R=6000
    rays.append(f'<path d="M{cx0},{cy0} L{cx0+R*math.cos(a0):.0f},{cy0+R*math.sin(a0):.0f} L{cx0+R*math.cos(a1):.0f},{cy0+R*math.sin(a1):.0f}Z"/>')
svg.append(f'<g id="sunburst" fill="#FFF8DC" clip-path="url(#bleedclip)">'+"".join(rays)+'</g>')
svg.insert(1,f'<defs><clipPath id="bleedclip"><rect x="{X0}" y="{Y0}" width="{TW+2*BL}" height="{TH+2*BL}"/></clipPath></defs>')
# hills (through bleed)
svg.append(f'<g id="hills"><path d="M{X0},1640 C500,1540 1000,1640 1600,1560 S2600,1520 3200,1580 S3800,1560 {X1},1600 V{Y1} H{X0}Z" fill="#7DC13F"/><path d="M{X0},1760 C600,1680 1200,1760 1900,1700 S3000,1690 3600,1730 S3900,1720 {X1},1740 V{Y1} H{X0}Z" fill="#0F9648"/></g>')
cols=["#1075bd","#b72f77","#f28a1f","#0f9648","#ffd23f"]
def spark(x,y,r,c): return f'<path d="M{x},{y-r} Q{x+r*0.18},{y-r*0.18} {x+r},{y} Q{x+r*0.18},{y+r*0.18} {x},{y+r} Q{x-r*0.18},{y+r*0.18} {x-r},{y} Q{x-r*0.18},{y-r*0.18} {x},{y-r}Z" fill="{c}"/>'
dec=[]
for (x0,y0,x1,y1,cnt) in [(120,160,2150,520,14),(120,1500,2150,1640,8),(60,520,330,1450,8),(1950,520,2200,1450,6)]:
    for k in range(cnt):
        x=random.uniform(x0,x1); y=random.uniform(y0,y1); c=random.choice(cols); t=random.choice("cts"); r=random.uniform(18,40)
        if t=="c": dec.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{c}"/>')
        elif t=="t": dec.append(f'<path d="M{x:.0f},{y-r:.0f} L{x+r:.0f},{y+r*0.8:.0f} L{x-r:.0f},{y+r*0.8:.0f}Z" fill="{c}" transform="rotate({random.uniform(0,360):.0f} {x:.0f} {y:.0f})"/>')
        else: dec.append(spark(round(x),round(y),r*1.7,c))
for (x,y,r,c) in [(300,300,80,"#ffd23f"),(2000,260,70,"#ffffff"),(250,1350,60,"#ffffff"),(2100,1300,80,"#ffd23f")]: dec.append(spark(x,y,r,c))
svg.append('<g id="confetti-sparkles">'+"".join(dec)+'</g>')
# characters (left, wide)
s=min(2100/aw,1230/ah); ax=1150-aw*s/2; ay=1640-ah*s
svg.append('<ellipse id="ground-shadow" cx="1150" cy="1650" rx="760" ry="36" fill="#0A3C1E" opacity="0.25"/>')
svg.append(f'<g id="characters" transform="translate({ax:.1f},{ay:.1f}) scale({s:.5f})">{art}</g>')
print("art scale",s,aw*s,ah*s,"y",ay)
# ---- right column: title, pills, logo card ----
CX=3065; COLW=1560
def title_line(txt,size,cx,cy,fill,mid,dark):
    p,w,h=ink_text(txt,size,cx,cy,FONT)
    sh=lambda c,dx,dy,sw: f'<g fill="{c}" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" transform="translate({dx},{dy})">{p}</g>'
    return sh(dark,12,16,48)+sh(mid,0,0,34)+f'<g fill="{fill}">{p}</g>',w,h
_,u1,_=ink_text("ליד הפח",1000,0,0,FONT); _,u2,_=ink_text("לא נאסף!",1000,0,0,FONT)
S=min(COLW/u1,COLW/u2)*1000
svg.append('<g id="title">')
t1,w1,h1=title_line("ליד הפח",S,CX,300,"#FFF8DC","#0F9648","#0A3C1E")
t2,w2,h2=title_line("לא נאסף!",S,CX,300+S*0.93,"#FFD23F","#D6336C","#3D0824")
svg.append(t1); svg.append(t2); svg.append('</g>')
print("title size",S,"w",w1,w2,"h",h1,h2)
bag_icon=lambda cx,cy,k: f'<g transform="translate({cx-50*k:.0f},{cy-55*k:.0f}) scale({k})"><path d="M50,8 C40,0 34,10 40,20 C14,34 4,62 8,86 C12,112 88,112 92,86 C96,62 86,34 60,20 C66,10 60,0 50,8Z" fill="#26292b" stroke="#ffffff" stroke-width="4"/><path d="M38,24 H62" stroke="#6b7176" stroke-width="5" stroke-linecap="round"/><path d="M26,56 C22,72 26,88 34,98" fill="none" stroke="#6b7176" stroke-width="5" stroke-linecap="round"/></g>'
box_icon=lambda cx,cy,k: f'<g transform="translate({cx-55*k:.0f},{cy-40*k:.0f}) scale({k})"><rect x="0" y="30" width="110" height="60" rx="5" fill="#b87a30" stroke="#ffffff" stroke-width="4"/><rect x="42" y="30" width="26" height="60" fill="#e8c27a"/><path d="M0,34 L22,4 H88 L110,34Z" fill="#c68a3c" stroke="#ffffff" stroke-width="4" stroke-linejoin="round"/></g>'
def pill(x,y,w,h,col,dark,txt,icon_fn,icon_w,k_icon,sz):
    _,tw,_=ink_text(txt,sz,0,0,FONT2); gap=50; group=icon_w+gap+tw; gx0=x+(w-group)/2
    icx=gx0+group-icon_w/2; tcx=gx0+tw/2; cy=y+h/2; tp,_,_=ink_text(txt,sz,tcx,cy,FONT2)
    return (f'<g id="pill"><rect x="{x+10}" y="{y+14}" width="{w}" height="{h}" rx="{h/2}" fill="{dark}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{col}" stroke="#ffffff" stroke-width="8"/><g fill="#ffffff">{tp}</g>{icon_fn(icx,cy,k_icon)}</g>')
px=CX-COLW/2; ph=150
svg.append(pill(px,985,COLW,ph,"#0F9648","#064A21","שקיות – לתוך הפח",bag_icon,110,1.1,92))
svg.append(pill(px,1175,COLW,ph,"#1075BD","#0A4170","קרטונים – לקרטוניה",box_icon,126,1.15,92))
# logo card
cardy=1400; cardh=420
svg.append(f'<g id="logos"><rect x="{px+10}" y="{cardy+14}" width="{COLW}" height="{cardh}" rx="70" fill="#0A3C1E" opacity="0.35"/><rect x="{px}" y="{cardy}" width="{COLW}" height="{cardh}" rx="70" fill="#ffffff"/>')
tgt=330; sc2=tgt/hh; sc3=tgt/ch_*1.05; w2_=hw*sc2; w3_=cw*sc3; gap=190; total=w2_+w3_+gap; x2=CX-total/2; x3=x2+w2_+gap; y0=cardy+(cardh-tgt)/2
svg.append(f'<g id="logo-1-shefa-har-bracha" transform="translate({x2:.1f},{y0:.1f}) scale({sc2:.5f})">{hb}</g>')
svg.append(f'<rect x="{x2+w2_+gap/2-3:.1f}" y="{cardy+60}" width="6" height="{cardh-120}" fill="#cfd8c8" rx="3"/>')
svg.append(f'<g id="logo-2-shomron-council" transform="translate({x3:.1f},{y0-4:.1f}) scale({sc3:.5f})">{cc}</g></g>')
open("ad_core.txt","w").write("\n".join(svg[1:]))
guides=(f'<g id="GUIDES-NOT-FOR-PRINT" fill="none" stroke-width="6"><rect x="0" y="0" width="{TW}" height="{TH}" stroke="#ff0000"/><rect x="150" y="150" width="{TW-300}" height="{TH-300}" stroke="#0066ff" stroke-dasharray="40 30"/>'
        +"".join(f'<circle cx="{x}" cy="{y}" r="38" stroke="#ff00ff"/>' for x in (150,TW-150) for y in (150,TH-150))+'</g>')
open("ad.svg","w").write(svg[0]+"\n"+"\n".join(svg[1:])+"\n</svg>")
open("ad_guides.svg","w").write(svg[0]+"\n"+"\n".join(svg[1:])+"\n"+guides+"\n</svg>")
print("ok",len(open("ad.svg").read())//1024,"KB")
