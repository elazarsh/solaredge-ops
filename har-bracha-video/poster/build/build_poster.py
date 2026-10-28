import re,math,random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
W,H=2480,3508
FONT="DoodleFull.ttf"
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
def read(n): 
    w,h=map(int,open(f"{n}_size.txt").read().split()); return w,h,open(f"{n}_paths.txt").read()
aw,ah,art=read("art"); hw,hh,hb=read("hb"); cw,ch_,cc=read("cc")
random.seed(5)
svg=[]
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append('<defs><radialGradient id="bgr" cx="50%" cy="58%" r="75%"><stop offset="0" stop-color="#FFFBEA"/><stop offset="1" stop-color="#FFE7A3"/></radialGradient></defs>')
svg.append(f'<rect id="background" width="{W}" height="{H}" fill="url(#bgr)"/>')
# sunburst
cx0,cy0=1240,2250; rays=[]
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
# art
svg.append('<ellipse id="ground-shadow" cx="1230" cy="3068" rx="360" ry="34" fill="#0A3C1E" opacity="0.28"/>')
s=min(2300/aw,1860/ah); ax=1240-aw*s/2; ay=3075-ah*s; print('art scale',s,aw*s,ah*s)
svg.append(f'<g id="characters" transform="translate({ax:.1f},{ay:.1f}) scale({s:.5f})">'+art+'</g>')
# ground shadow
# title
_,u1=text_path("ליד הפח",1000,1240,0); _,u2=text_path("לא נאסף!",1000,1240,0)
S_=min(2260/u1,2260/u2)*1000; print("title size",S_)
l1,w1=text_path("ליד הפח",S_,1240,40); l2,w2=text_path("לא נאסף!",S_,1240,40+S_*0.98)
sh=lambda p,c,dx,dy,sw: f'<g fill="{c}" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" transform="translate({dx},{dy})">{p}</g>'
svg.append('<g id="title">')
svg.append(sh(l1,"#0A3C1E",16,22,90)); svg.append(sh(l1,"#0F9648",0,0,70)); svg.append(f'<g fill="#FFF3C4" stroke="#0A3C1E" stroke-width="6" stroke-linejoin="round">{l1}</g>')
svg.append(sh(l2,"#3D0824",16,22,90)); svg.append(sh(l2,"#b72f77",0,0,70)); svg.append(f'<g fill="#FFC21F" stroke="#3D0824" stroke-width="6" stroke-linejoin="round">{l2}</g>')
svg.append('</g>')
# footer strip with logos
svg.append(f'<g id="footer"><rect x="0" y="3110" width="{W}" height="398" fill="#ffffff"/><rect x="0" y="3094" width="{W}" height="22" fill="#0F9648"/>')
hs=340/hh; cs=300/ch_*1.0
hx=1240+30; 
svg.append(f'<g id="logo-har-bracha" transform="translate({1240-80-hw*hs:.1f},{3110+28:.1f}) scale({hs:.5f})">{hb}</g>')
svg.append(f'<rect x="1237" y="3150" width="6" height="320" fill="#cfd8c8" rx="3"/>')
svg.append(f'<g id="logo-shomron-council" transform="translate({1240+80:.1f},{3110+50:.1f}) scale({cs*1.0:.5f})">{cc}</g></g>')
svg.append('</svg>')
open("poster.svg","w").write("\n".join(svg)); print("size KB",len("\n".join(svg))//1024)
