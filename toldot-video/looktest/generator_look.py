# -*- coding: utf-8 -*-
import math
CX,CY=1280,540
FONTS="""
@font-face{font-family:Heebo;font-weight:900;src:url(node_modules/@fontsource/heebo/files/heebo-hebrew-900-normal.woff2)}
@font-face{font-family:Heebo;font-weight:700;src:url(node_modules/@fontsource/heebo/files/heebo-hebrew-700-normal.woff2)}
@font-face{font-family:Heebo;font-weight:400;src:url(node_modules/@fontsource/heebo/files/heebo-hebrew-400-normal.woff2)}
@font-face{font-family:Frank;font-weight:700;src:url(node_modules/@fontsource/frank-ruhl-libre/files/frank-ruhl-libre-hebrew-700-normal.woff2)}
@font-face{font-family:Frank;font-weight:400;src:url(node_modules/@fontsource/frank-ruhl-libre/files/frank-ruhl-libre-hebrew-400-normal.woff2)}
"""
def pos(theta,R,cx=CX,cy=CY,sy=1.0):
    t=math.radians(theta); return cx+R*math.sin(t), cy-R*math.cos(t)*sy

# who sits where: (angle, key)
SEATS=[(0,'isaac'),(60,'esau'),(120,'anon1'),(180,'rebecca'),(240,'anon2'),(300,'jacob')]
R=330
def figure(theta,key,col,seatcol,extra=''):
    x,y=pos(theta,R)
    return f'''<g transform="translate({x:.1f},{y:.1f}) rotate({theta})">
<rect x="-78" y="-70" width="156" height="92" rx="34" fill="{seatcol}"/>
<ellipse cx="0" cy="-6" rx="66" ry="34" fill="{col}"/>
<circle cx="0" cy="8" r="27" fill="{col}" stroke="rgba(0,0,0,.18)" stroke-width="3"/>
{extra}</g>'''
def extras(key,c):
    if key=='isaac':  return f'<line x1="86" y1="-40" x2="86" y2="40" stroke="{c}" stroke-width="7" stroke-linecap="round"/>'
    if key=='rebecca':return f'<path d="M-60,-20 Q0,60 60,-20 L50,-70 Q0,-40 -50,-70Z" fill="{c}" opacity=".85"/>'
    if key=='esau':   return f'<path d="M-90,-38 Q-120,0 -90,40" fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round"/><line x1="-90" y1="-38" x2="-90" y2="40" stroke="{c}" stroke-width="2"/>'
    if key=='jacob':  return f'<path d="M80,-44 Q96,-60 108,-46 M94,-52 L94,44" fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round"/>'
    return ''
def stray_chair(col,out):
    x,y=pos(36,640,sy=0.9)
    return f'<g id="stray" transform="translate({x:.1f},{y:.1f}) rotate(205)"><rect x="-78" y="-70" width="156" height="92" rx="34" fill="{col}" opacity="{out}"/></g>'
def hands_note(c): return ''

SCRIPT=r'''
const CX=1280,CY=540,R=330;
const ease=x=>x<=0?0:x>=1?1:1-Math.pow(1-x,3), seg=(t,a,b)=>ease((t-a)/(b-a));
const P=(th,r,sy=1)=>[CX+r*Math.sin(th*Math.PI/180),CY-r*Math.cos(th*Math.PI/180)*sy];
const q=s=>[...document.querySelectorAll(s)];
const voices=q('.voice'); voices.forEach(v=>{v._len=v.getTotalLength(); v._dotted=v.hasAttribute('stroke-dasharray');});
window.setT=function(t){
  q('.t1').forEach(e=>{const p=seg(t,0.3,1.2); e.style.opacity=p; e.style.translate='0px '+((1-p)*46)+'px';});
  q('.t2').forEach(e=>{const p=seg(t,1.0,1.9); e.style.opacity=p; e.style.translate='0px '+((1-p)*46)+'px';});
  q('.lamp').forEach(e=>{e.style.transformBox='fill-box';e.style.transformOrigin='center';e.style.transform='scale('+(1+0.12*Math.sin(t*3.1))+')';});
  voices.forEach(v=>{const p=seg(t,1.8,3.2);
    if(v._dotted){v.style.opacity=p; v.style.strokeDashoffset=(-t*60)+'px';}
    else{v.style.strokeDasharray=v._len; v.style.strokeDashoffset=v._len*(1-p);}});
  const s=document.getElementById('stray'), p=seg(t,3.5,5.4);
  const a=P(36,640,0.9), b=P(30,R,1), x=a[0]+(b[0]-a[0])*p, y=a[1]+(b[1]-a[1])*p, r=205+(30-205)*p;
  s.setAttribute('transform','translate('+x+','+y+') rotate('+r+')');
  s.style.opacity=(0.55+0.45*p);
};
'''
def page(css,body,defs=''):
    return f'''<!doctype html><html lang="he" dir="rtl"><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:1920px;height:1080px;overflow:hidden}}{css}</style><body>
<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{body}</svg><script>{SCRIPT}</script></html>'''

# ---------- A: poster, flat, loud ----------
def A():
    pal={'isaac':'#F3E6C4','rebecca':'#E58AA0','esau':'#E8571F','jacob':'#1D4ED8','anon1':'#2B2420','anon2':'#2B2420'}
    seat={k:'#2B2420' for k in pal}; seat['anon1']=seat['anon2']='#3A302A'
    figs=''.join(figure(t,k,pal[k],seat[k],extras(k,'#2B2420' if k in('isaac','esau','jacob') else '#B84A63')) for t,k in SEATS)
    body=f'''
<rect width="1920" height="1080" fill="#F7F0E3"/>
<rect x="0" y="0" width="1920" height="1080" fill="#FFC21A" opacity="0"/>
<circle cx="{CX}" cy="{CY}" r="470" fill="#FFC21A"/>
<circle cx="{CX}" cy="{CY}" r="250" fill="#FFF3C9"/>
<circle cx="{CX}" cy="{CY}" r="250" fill="none" stroke="#2B2420" stroke-width="6"/>
{figs}
<circle class="lamp" cx="{CX}" cy="{CY}" r="30" fill="#E8571F"/><circle cx="{CX}" cy="{CY}" r="12" fill="#FFF3C9"/>
{stray_chair('#2B2420',1)}
<path class="voice" d="M{pos(300,R)[0]+30:.0f},{pos(300,R)[1]+20:.0f} C {CX-250},{CY+120} {CX-150},{CY+20} {CX-26},{CY-6}" fill="none" stroke="#1D4ED8" stroke-width="9" stroke-linecap="round" stroke-dasharray="2 18"/>
<text class="t1" x="860" y="360" font-family="Heebo" font-weight="900" font-size="175" fill="#2B2420" text-anchor="start" transform="rotate(-3 860 360)">מי יישא</text>
<text class="t2" x="860" y="500" font-family="Heebo" font-weight="900" font-size="112" fill="#E8571F" text-anchor="start" transform="rotate(-3 860 500)">את ההבטחה?</text>
<rect x="0" y="1060" width="1280" height="20" fill="#E8571F"/>
<text x="70" y="1010" font-family="Heebo" font-weight="700" font-size="34" fill="#2B2420" text-anchor="end">A · פוסטר־תנועה: צבע שטוח, טיפוגרפיה ענקית, גוף יחיד לכל דמות</text>
'''
    return page('',body)

# ---------- B: cinematic dark, lamp-lit ----------
def B():
    pal={'isaac':'#CDBFA3','rebecca':'#B98493','esau':'#B5532C','jacob':'#4F73C9','anon1':'#1B1815','anon2':'#1B1815'}
    seat={k:'#16130F' for k in pal}
    figs=''.join(figure(t,k,pal[k],seat[k],extras(k,'#0E0C0A' if k!='rebecca' else '#7A4E5D')) for t,k in SEATS)
    defs=f'''
<radialGradient id="pool" cx="{CX}" cy="{CY}" r="760" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FFC768" stop-opacity=".95"/><stop offset=".22" stop-color="#E0902F" stop-opacity=".55"/><stop offset=".55" stop-color="#4a2a0f" stop-opacity=".25"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="dark" cx="{CX}" cy="{CY}" r="1100" gradientUnits="userSpaceOnUse"><stop offset=".25" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".92"/></radialGradient>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .5 0"/></filter>
<filter id="blur"><feGaussianBlur stdDeviation="9"/></filter>'''
    body=f'''
<rect width="1920" height="1080" fill="#0A0908"/>
<circle cx="{CX}" cy="{CY}" r="250" fill="#2A1C10"/>
<circle cx="{CX}" cy="{CY}" r="250" fill="none" stroke="#FFC768" stroke-opacity=".5" stroke-width="3"/>
{figs}
<rect width="1920" height="1080" fill="url(#pool)" style="mix-blend-mode:screen"/>
<rect width="1920" height="1080" fill="url(#dark)"/>
{stray_chair('#14110D',0.95)}
<circle class="lamp" cx="{CX}" cy="{CY}" r="20" fill="#FFE2A3" filter="url(#blur)"/><circle class="lamp" cx="{CX}" cy="{CY}" r="9" fill="#FFF6DA"/>
<path class="voice" d="M{pos(300,R)[0]+30:.0f},{pos(300,R)[1]+20:.0f} C {CX-250},{CY+120} {CX-150},{CY+20} {CX-26},{CY-6}" fill="none" stroke="#FFC768" stroke-width="4" stroke-linecap="round" opacity=".9" filter="url(#blur)"/>
<path class="voice" d="M{pos(300,R)[0]+30:.0f},{pos(300,R)[1]+20:.0f} C {CX-250},{CY+120} {CX-150},{CY+20} {CX-26},{CY-6}" fill="none" stroke="#FFF1CC" stroke-width="2" stroke-linecap="round"/>
<rect width="1920" height="1080" filter="url(#grain)" opacity=".12"/>
<text class="t1" x="860" y="520" font-family="Frank" font-weight="700" font-size="92" fill="#F4E6C8" text-anchor="start">מי יישא</text>
<text class="t2" x="860" y="630" font-family="Frank" font-weight="700" font-size="92" fill="#F4E6C8" text-anchor="start">את ההבטחה?</text>
<line class="t2" x1="860" y1="668" x2="360" y2="668" stroke="#FFC768" stroke-width="3"/>
<text x="70" y="1040" font-family="Heebo" font-weight="700" font-size="30" fill="#bba98a" text-anchor="end">B · קולנועי כהה: אור יחיד, צללית, גרגר פילם</text>
'''
    return page('',body,defs)

# ---------- C: riso paper-cut collage ----------
def C():
    pal={'isaac':'#F6E7B4','rebecca':'#FF6F91','esau':'#FF5A1F','jacob':'#2748E8','anon1':'#1E2A78','anon2':'#1E2A78'}
    seatc='#1E2A78'
    def off(s,dx,dy,col,op=1):
        return f'<g transform="translate({dx},{dy})" style="mix-blend-mode:multiply" opacity="{op}">{s}</g>'
    figs_main=''.join(figure(t,k,pal[k],'#F2C84B' if k not in('anon1','anon2') else '#F2C84B',extras(k,'#1E2A78' if k!='rebecca' else '#C23B63')) for t,k in SEATS)
    defs=f'''
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(25)"><circle cx="11" cy="11" r="5.2" fill="#FF5A1F"/></pattern>
<radialGradient id="m" cx="{CX}" cy="{CY}" r="520" gradientUnits="userSpaceOnUse"><stop offset=".25" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="halftone"><rect width="1920" height="1080" fill="url(#m)"/></mask>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="3" seed="9"/><feColorMatrix values="0 0 0 0 .25  0 0 0 0 .2  0 0 0 0 .1  0 0 0 .55 0"/></filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="3" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="9"/></filter>'''
    body=f'''
<rect width="1920" height="1080" fill="#EFE5CE"/>
<g filter="url(#rough)">
<rect width="1920" height="1080" fill="url(#dots)" mask="url(#halftone)" opacity=".85"/>
{off(f'<circle cx="{CX}" cy="{CY}" r="250" fill="#F2C84B"/>',6,5,'')}
{off(figs_main,-7,6,'')}
{figs_main}
{stray_chair('#1E2A78',1)}
<circle class="lamp" cx="{CX}" cy="{CY}" r="28" fill="#FF5A1F"/>
<path class="voice" d="M{pos(300,R)[0]+30:.0f},{pos(300,R)[1]+20:.0f} C {CX-250},{CY+120} {CX-150},{CY+20} {CX-26},{CY-6}" fill="none" stroke="#2748E8" stroke-width="10" stroke-linecap="round" stroke-dasharray="1 22"/>
</g>
<g filter="url(#rough)">
<rect class="t1" x="90" y="200" width="760" height="200" fill="#2748E8" transform="rotate(-2 90 200)"/>
<text class="t1" x="810" y="355" font-family="Frank" font-weight="700" font-size="150" fill="#EFE5CE" text-anchor="start" transform="rotate(-2 90 200)">מי יישא</text>
<rect class="t2" x="60" y="440" width="800" height="180" fill="#FF5A1F" transform="rotate(1.5 60 440)"/>
<text class="t2" x="830" y="575" font-family="Frank" font-weight="700" font-size="120" fill="#1E2A78" text-anchor="start" transform="rotate(1.5 60 440)">את ההבטחה?</text>
</g>
<rect width="1920" height="1080" filter="url(#grain)" opacity=".35" style="mix-blend-mode:multiply"/>
<text x="70" y="1030" font-family="Heebo" font-weight="700" font-size="34" fill="#1E2A78" text-anchor="end">C · קולאז' נייר/ריזוגרף: מרקם, חיתוך, מראה אנושי וחם</text>
'''
    return page('',body,defs)

for n,f in (('A',A),('B',B),('C',C)):
    open(f'look_{n}.html','w',encoding='utf-8').write(f())
print('ok')
