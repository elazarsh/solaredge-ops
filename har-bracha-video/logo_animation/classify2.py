import re,json
from svgpathtools import parse_path
s=open("hbc_paths.txt").read(); ps=re.findall(r'<path[^>]*/>',s)
out=[]
for i,p in enumerate(ps):
    d=re.search(r' d="([^"]+)"',p).group(1); f=re.search(r'fill="#([0-9a-fA-F]{6})"',p)
    t=re.search(r'translate\(([-\d.]+),\s*([-\d.]+)\)',p); tx,ty=(float(t.group(1)),float(t.group(2))) if t else (0,0)
    col=tuple(int(f.group(1)[k:k+2],16) for k in (0,2,4)) if f else (0,0,0)
    try: x0,x1,y0,y1=parse_path(d).bbox()
    except Exception: continue
    out.append(dict(i=i,d=d,tx=tx,ty=ty,col=col,bb=(x0+tx,y0+ty,x1+tx,y1+ty),area=(x1-x0)*(y1-y0)))
json.dump(out,open("../logo34/paths.json","w"))
print(len(out))
def grp(o):
    r,g,b=o["col"]; x0,y0,x1,y1=o["bb"]; cy=(y0+y1)/2; cx=(x0+x1)/2
    if cy>1620: return "tag"
    if cy>1300 and g>r+60 and r<80: return "text"
    if cy>1280: return "other"
    if b>r+40 and b>g: return "blue"
    if r>200 and 90<g<170 and b<90: return "orange"
    if r>140 and g<100 and b>80: return "magenta_book" if cx>1100 and cy<420 else "magenta"
    if g>165 and r>90: return "hill"
    if g<110: return "dark"
    if g>=110: return "house"
    return "other"
from collections import Counter
for o in out: o["g"]=grp(o)
print(Counter(o["g"] for o in out))
json.dump(out,open("../logo34/paths.json","w"))
# debug render
cols={"blue":"#1075bd","orange":"#f28a1f","magenta":"#b72f77","magenta_book":"#ff00ff","hill":"#8dc63f","dark":"#003d1c","house":"#0f9648","text":"#00aa44","tag":"#444","other":"#ff0000"}
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1864 1866" width="600" height="600"><rect width="1864" height="1866" fill="#fff"/>'+"".join(f'<path d="{o["d"]}" transform="translate({o["tx"]},{o["ty"]})" fill="{cols[o["g"]]}"/>' for o in out)+'</svg>'
open("../logo34/debug.svg","w").write(svg)
import cairosvg; cairosvg.svg2png(bytestring=svg.encode(),write_to="../logo34/debug.png")
