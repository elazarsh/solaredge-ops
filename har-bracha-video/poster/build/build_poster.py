import re,math,random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
W,H=2480,3508
FONT="fonts/Rubik900.ttf"
FONT2="fonts/Rubik800.ttf"
f=TTFont(FONT); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f["head"].unitsPerEm; hmtx=f["hmtx"]
def text_path(txt,size,cx,top,track=0):
    vis=txt[::-1]; adv=[]; names=[]
    for ch in vis:
        n=cmap.get(ord(ch)); names.append(n); adv.append(hmtx[n][0] if n else upm*0.3)
    s=size/upm; total=sum(adv)*s+track*(len(vis)-1); x=cx-total/2; asc=f["hhea"].ascent*s
    out=[]
    for n,a in zip(names,adv):
        if n:
            pen=SVGPathPen(gs); gs[n].draw(pen); d=pen.getCommands()
            if d: out.append(f'<path transform="translate({x:.1f},{top+asc:.1f}) scale({s:.5f},{-s:.5f})" d="{d}"/>')
        x+=a*s+track
    return "\n".join(out),total
def text_path2(txt,size,cx,top,fontfile):
    ff=TTFont(fontfile); g2=ff.getGlyphSet(); cm=ff.getBestCmap(); u=ff["head"].unitsPerEm; hm=ff["hmtx"]
    vis=txt[::-1]; s=size/u; adv=[hm[cm[ord(c)]][0] if ord(c) in cm else u*0.3 for c in vis]; total=sum(adv)*s; x=cx-total/2; asc=ff["hhea"].ascent*s; out=[]
    for c,a in zip(vis,adv):
        n=cm.get(ord(c))
        if n:
            pen=SVGPathPen(g2); g2[n].draw(pen); d=pen.getCommands()
            if d: out.append(f'<path transform="translate({x:.1f},{top+asc:.1f}) scale({s:.5f},{-s:.5f})" d="{d}"/>')
        x+=a*s
    return "\n".join(out),total
def read(n): 
    w,h=map(int,open(f"{n}_size.txt").read().split()); return w,h,open(f"{n}_paths.txt").read()
aw,ah,art=read("art"); hw,hh,hb=read("hb2"); cw,ch_,cc=read("cc")
_,uu=text_path2('אגף שפ"ע',1000,0,0,FONT2)
_sz=1180/uu*1000
_tp,_=text_path2('אגף שפ"ע',_sz,hw/2,1648,FONT2)
hb=hb+'<g fill="#22693A">'+_tp+'</g>'
random.seed(5)
svg=[]
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append('<defs><radialGradient id="bgr" cx="50%" cy="58%" r="75%"><stop offset="0" stop-color="#FFFBEA"/><stop offset="1" stop-color="#FFE7A3"/></radialGradient></defs>')
svg.append(f'<rect id="background" width="{W}" height="{H}" fill="url(#bgr)"/>')
# sunburst
cx0,cy0=1240,2300; rays=[]
n=28
for i in range(n):
    if i%2: continue
    a0=2*math.pi*i/n; a1=2*math.pi*(i+1)/n; R=4200
    rays.append(f'<path d="M{cx0},{cy0} L{cx0+R*math.cos(a0):.0f},{cy0+R*math.sin(a0):.0f} L{cx0+R*math.cos(a1):.0f},{cy0+R*math.sin(a1):.0f}Z"/>')
svg.append('<g id="sunburst" fill="#FFF3C4" opacity="0.75">'+"".join(rays)+'</g>')
# hills
svg.append('<g id="hills"><path d="M0,2960 C500,2830 1000,2940 1500,2850 S2200,2830 2480,2900 V3300 H0Z" fill="#7DC13F"/><path d="M0,3040 C600,2930 1200,3020 1800,2960 S2300,2950 2480,2990 V3300 H0Z" fill="#0F9648"/></g>')
# confetti + sparkles
cols=["#1075bd","#b72f77","#f28a1f","#0f9648","#ffd23f"]
def spark(x,y,r,c): 
    return f'<path d="M{x},{y-r} Q{x+r*0.18},{y-r*0.18} {x+r},{y} Q{x+r*0.18},{y+r*0.18} {x},{y+r} Q{x-r*0.18},{y+r*0.18} {x-r},{y} Q{x-r*0.18},{y-r*0.18} {x},{y-r}Z" fill="{c}"/>'
dec=[]
zones=[(80,1500,420,3000),(2060,1500,2400,3000)]
for z in zones:
    for k in range(16):
        x=random.uniform(z[0],z[2]); y=random.uniform(z[1],z[3]); c=random.choice(cols); t=random.choice(["c","t","s"]); r=random.uniform(22,48)
        if t=="c": dec.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{c}"/>')
        elif t=="t": dec.append(f'<path d="M{x:.0f},{y-r:.0f} L{x+r:.0f},{y+r*0.8:.0f} L{x-r:.0f},{y+r*0.8:.0f}Z" fill="{c}" transform="rotate({random.uniform(0,360):.0f} {x:.0f} {y:.0f})"/>')
        else: dec.append(spark(round(x),round(y),r*1.6,c))
for (x,y,r,c) in [(620,1450,90,"#ffd23f"),(1900,1500,80,"#ffffff"),(560,2500,70,"#ffffff"),(1960,2450,100,"#ffd23f"),(700,2900,60,"#ffd23f")]: dec.append(spark(x,y,r,c))
svg.append('<g id="confetti-sparkles">'+"".join(dec)+'</g>')
# --- minimal call-to-action pills ---
def pill(x,y,w,h,col,dark,txt,icon):
    _,uu=text_path2(txt,1000,0,0,FONT2); sz=min(96,(w-300)/uu*1000)
    tp,tw=text_path2(txt,sz,x+(w-230)/2,y+(h-sz*1.0)/2-4,FONT2)
    return (f'<g id="pill">'
            f'<rect x="{x+10}" y="{y+14}" width="{w}" height="{h}" rx="{h/2}" fill="{dark}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{col}" stroke="#ffffff" stroke-width="8"/>'
            f'<g fill="#ffffff">{tp}</g>{icon}</g>')
bag_icon=lambda cx,cy,k: f'<g transform="translate({cx-50*k:.0f},{cy-55*k:.0f}) scale({k})"><path d="M50,8 C40,0 34,10 40,20 C14,34 4,62 8,86 C12,112 88,112 92,86 C96,62 86,34 60,20 C66,10 60,0 50,8Z" fill="#26292b" stroke="#ffffff" stroke-width="4"/><path d="M38,24 H62" stroke="#6b7176" stroke-width="5" stroke-linecap="round"/><path d="M26,56 C22,72 26,88 34,98" fill="none" stroke="#6b7176" stroke-width="5" stroke-linecap="round"/></g>'
box_icon=lambda cx,cy,k: f'<g transform="translate({cx-55*k:.0f},{cy-40*k:.0f}) scale({k})"><rect x="0" y="30" width="110" height="60" rx="5" fill="#b87a30" stroke="#ffffff" stroke-width="4"/><rect x="42" y="30" width="26" height="60" fill="#e8c27a"/><path d="M0,34 L22,4 H88 L110,34Z" fill="#c68a3c" stroke="#ffffff" stroke-width="4" stroke-linejoin="round"/><path d="M-10,52 L18,22" stroke="#ffffff" stroke-width="0"/></g>'
ph=150; py=1215
svg.append(pill(1290,py,1090,ph,"#0F9648","#064A21","שקיות – לתוך הפח",bag_icon(1290+1090-120,py+ph/2,1.1)))
svg.append(pill(100,py,1090,ph,"#1075BD","#0A4170","קרטונים – לקרטוניה",box_icon(100+1090-125,py+ph/2,1.15)))
# art
svg.append('<ellipse id="ground-shadow" cx="1230" cy="3068" rx="360" ry="34" fill="#0A3C1E" opacity="0.28"/>')
s=min(2300/aw,1690/ah); ax=1240-aw*s/2; ay=3075-ah*s; print('art scale',s,aw*s,ah*s)
svg.append(f'<g id="characters" transform="translate({ax:.1f},{ay:.1f}) scale({s:.5f})">'+art+'</g>')
# ground shadow
# title
_,u1=text_path("ליד הפח",1000,1240,0); _,u2=text_path("לא נאסף!",1000,1240,0)
S_=min(2180/u1,2180/u2)*1000; print("title size",S_)
l1,w1=text_path("ליד הפח",S_,1240,40); l2,w2=text_path("לא נאסף!",S_,1240,40+S_*0.98)
sh=lambda p,c,dx,dy,sw: f'<g fill="{c}" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" transform="translate({dx},{dy})">{p}</g>'
svg.append('<g id="title">')
svg.append(sh(l1,"#0A3C1E",14,20,64)); svg.append(sh(l1,"#0F9648",0,0,46)); svg.append(f'<g fill="#FFF8DC" stroke="none">{l1}</g>')
svg.append(sh(l2,"#3D0824",14,20,64)); svg.append(sh(l2,"#D6336C",0,0,46)); svg.append(f'<g fill="#FFD23F" stroke="none">{l2}</g>')
svg.append('</g>')
# footer strip with logos
svg.append(f'<g id="footer"><rect x="0" y="3110" width="{W}" height="398" fill="#ffffff"/><rect x="0" y="3094" width="{W}" height="22" fill="#0F9648"/>')
# --- footer: two logos side by side (Shefa Har Bracha + Shomron council) ---
tgt=330
sc2=tgt/hh; sc3=tgt/ch_*1.05
w2_=hw*sc2; w3_=cw*sc3
gap=220; total=w2_+w3_+gap; x0=(W-total)/2; y0=3110+(398-tgt)/2+4
x2=x0; x3=x2+w2_+gap
svg.append(f'<g id="logo-1-shefa-har-bracha" transform="translate({x2:.1f},{y0:.1f}) scale({sc2:.5f})">{hb}</g>')
svg.append(f'<rect id="divider" x="{x2+w2_+gap/2-3:.1f}" y="3170" width="6" height="280" fill="#cfd8c8" rx="3"/>')
svg.append(f'<g id="logo-2-shomron-council" transform="translate({x3:.1f},{y0-4:.1f}) scale({sc3:.5f})">{cc}</g></g>')
svg.append('</svg>')
open("poster.svg","w").write("\n".join(svg)); print("size KB",len("\n".join(svg))//1024)
