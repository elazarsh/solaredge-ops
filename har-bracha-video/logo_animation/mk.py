import json,random
P=json.load(open("paths.json"))
cols={"blue":0,"orange":1}
def cluster(items,gap=110):
    items=sorted(items,key=lambda o:(o["bb"][0]+o["bb"][2])/2); cl=[]; cur=[]; last=None; lastx1=None
    for o in items:
        x0,x1=o["bb"][0],o["bb"][2]
        if cur and x0-lastx1>gap: cl.append(cur); cur=[]; lastx1=None
        cur.append(o); lastx1=max(lastx1 or -1e9,x1)
    if cur: cl.append(cur)
    return cl
def pathel(o): return f'<path d="{o["d"]}" transform="translate({o["tx"]},{o["ty"]})" fill="rgb({o["col"][0]},{o["col"][1]},{o["col"][2]})"/>'
groups=[]   # (kind,t0,dur,[paths])
def add(kind,items,t0,dur,stag=0.0,gap=110):
    for k,c in enumerate(cluster(items,gap)):
        groups.append((kind,t0+k*stag,dur,c))
G={k:[o for o in P if o["g"]==k] for k in set(o["g"] for o in P)}
groups.append(("hill",0.20,0.65,G["hill"]))
add("rise",G["orange"],0.55,0.55,0.0,10000)
add("rise",G["blue"],0.68,0.55,0.18,160)
add("pop",G["magenta"],0.95,0.45)
add("pop",G["house"],0.80,0.5,0.0,10000)
add("pop",G["dark"],1.00,0.40,0.12,120)
add("flip",G["magenta_book"],1.15,0.5)
groups.append(("text",1.45,0.75,G["text"]+[o for o in P if o["g"]=="other"]))
groups.append(("tag",2.05,0.55,G["tag"]))
body=[]
for i,(kind,t0,dur,items) in enumerate(groups):
    body.append(f'<g class="el" data-k="{kind}" data-t0="{t0:.3f}" data-d="{dur:.3f}" id="e{i}">'+"".join(pathel(o) for o in items)+'</g>')
html=f'''<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;width:1080px;height:1440px;overflow:hidden;background:#fff}}
svg{{position:absolute;left:0;top:0}}
.el{{transform-box:fill-box}}
</style>
<svg id="stage" width="1080" height="1440" viewBox="0 0 1080 1440">
<defs>
<radialGradient id="bg" cx="50%" cy="46%" r="75%"><stop offset="0" stop-color="#FBFBF6"/><stop offset=".55" stop-color="#E9EDEE"/><stop offset="1" stop-color="#BFCDD8"/></radialGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter><filter id="blur20"><feGaussianBlur stdDeviation="22"/></filter>
<clipPath id="textclip"><rect id="tc" x="0" y="0" width="0" height="1866"/></clipPath>
</defs>
<rect width="1080" height="1440" fill="url(#bg)"/>
<ellipse id="halo" cx="540" cy="700" rx="520" ry="520" fill="url(#glow)" opacity="0"/>
<g id="parts"></g>
<ellipse id="shadow" cx="540" cy="1130" rx="300" ry="26" fill="#6a7a86" opacity="0" filter="url(#blur20)"/>
<g id="logo" transform="translate(140,300) scale(0.4292)">
{"".join(body)}
</g>
<g id="streak" opacity="0"><ellipse cx="0" cy="0" rx="330" ry="9" fill="#fff" filter="url(#blur8)"/><ellipse cx="0" cy="0" rx="70" ry="70" fill="url(#glow)"/></g>
<g id="sparks"></g>
</svg>
<script>
const E=t=>t<0?0:t>1?1:t, out3=t=>1-Math.pow(1-E(t),3), ease=t=>{{t=E(t);return t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2}};
const back=t=>{{t=E(t);const s=1.9;t-=1;return t*t*((s+1)*t+s)+1}};
const els=[...document.querySelectorAll('.el')];
// textual group gets clip-path wipe
const textEl=els.find(e=>e.dataset.k==='text'); textEl.setAttribute('clip-path','url(#textclip)');
// particles
let seed=7;const rnd=()=>{{seed=(seed*16807)%2147483647;return seed/2147483647}};
const NP=46,P=[];const ns='http://www.w3.org/2000/svg';
for(let i=0;i<NP;i++){{const g=document.createElementNS(ns,'path');g.setAttribute('d','M0,-1 L.35,-.35 L1,0 L.35,.35 L0,1 L-.35,.35 L-1,0 L-.35,-.35Z');g.setAttribute('fill','#ffffff');document.getElementById('parts').appendChild(g);P.push({{g,x:rnd()*1080,y:rnd()*1440,s:4+rnd()*10,v:6+rnd()*18,ph:rnd()*6.28,a:.25+rnd()*.5}});}}
// sparkles at fixed points
const SP=[[300,470,0.22],[780,420,0.2],[860,760,0.18],[230,820,0.16],[540,360,0.25],[650,1000,0.15]];
const spEl=SP.map(()=>{{const g=document.createElementNS(ns,'path');g.setAttribute('d','M0,-1 Q.12,-.12 1,0 Q.12,.12 0,1 Q-.12,.12 -1,0 Q-.12,-.12 0,-1Z');g.setAttribute('fill','#fffbe0');document.getElementById('sparks').appendChild(g);return g}});
function A(t){{
  const bg=E(t/0.5);
  document.getElementById('halo').setAttribute('opacity',(0.9*ease(t/0.8)*(1-0.4*E((t-2.6)/1))).toFixed(3));
  P.forEach(p=>{{const y=(p.y-p.v*t+1440*3)%1440, x=p.x+Math.sin(t*0.8+p.ph)*14; const tw=0.5+0.5*Math.sin(t*3+p.ph); p.g.setAttribute('transform',`translate(${{x}},${{y}}) scale(${{p.s*(0.6+0.4*tw)}})`); p.g.setAttribute('opacity',(p.a*bg*tw).toFixed(3));}});
  const breath=1+0.008*Math.sin(t*2)*E((t-2.3)/0.4);
  document.getElementById('logo').setAttribute('transform',`translate(${{140+(1864*0.4292)*(1-breath)/2}},${{300-(t>2.3?6*Math.sin((t-2.3)*1.6):0)}}) scale(${{0.4292*breath}})`);
  document.getElementById('shadow').setAttribute('opacity',(0.35*ease((t-0.9)/0.8)).toFixed(3));
  els.forEach(e=>{{const k=e.dataset.k,t0=+e.dataset.t0,d=+e.dataset.d,u=(t-t0)/d,B=back(u),o=E(u*3);
    if(k==='hill'){{const p=out3(u);e.style.opacity=E(u*4);e.style.transformOrigin='50% 100%';e.style.transform=`scale(${{0.15+0.85*p}},${{0.5+0.5*p}})`;}}
    else if(k==='rise'){{e.style.opacity=o;e.style.transformOrigin='50% 100%';e.style.transform=`scaleY(${{Math.max(0.001,B)}})`;}}
    else if(k==='pop'){{e.style.opacity=o;e.style.transformOrigin='50% 100%';e.style.transform=`scale(${{Math.max(0.001,B)}})`;}}
    else if(k==='flip'){{e.style.opacity=o;e.style.transformOrigin='50% 100%';e.style.transform=`scale(${{Math.max(0.001,B)}}) rotate(${{(1-E(u))*-25}}deg)`;}}
    else if(k==='text'){{e.style.opacity=1;}}
    else if(k==='tag'){{e.style.opacity=E(u);e.style.transform=`translateY(${{(1-out3(u))*40}}px)`;}}
  }});
  // text wipe from right to left (Hebrew direction) with streak
  const tu=E((t-1.45)/0.75), edge=1864*(1-ease(tu));
  document.getElementById('tc').setAttribute('x',edge);document.getElementById('tc').setAttribute('width',1864-edge+4);
  const sk=document.getElementById('streak'); const sx=140+edge*0.4292, sy=300+1455*0.4292;
  sk.setAttribute('transform',`translate(${{sx}},${{sy}})`); sk.setAttribute('opacity',(tu>0&&tu<1?1:0)*(0.9));
  // sparkle glints
  spEl.forEach((g,i)=>{{const [x,y,s]=SP[i]; const t0=1.3+i*0.28, u=(t-t0)/0.7; const a=u>0&&u<1?Math.sin(Math.PI*u):0; g.setAttribute('transform',`translate(${{x}},${{y}}) scale(${{s*120*a}}) rotate(${{u*40}})`); g.setAttribute('opacity',a.toFixed(3));}});
}}
window.READY=true;
</script>'''
open("logo34.html","w").write(html); print("groups",len(groups))
