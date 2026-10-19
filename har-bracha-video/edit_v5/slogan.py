import json,os,sys
from playwright.sync_api import sync_playwright
cfg=json.load(open("timing.json")); D=cfg["slogan"][1]-cfg["slogan"][0]; FPS=30; N=int(D*FPS)
html="""<style>
@font-face{font-family:DS;src:url(fonts/DoodleShadow.ttf)}
html,body{margin:0;background:transparent;overflow:hidden}
#w{position:absolute;left:20px;top:0;width:1040px;height:1080px;direction:rtl}
.row{position:absolute;left:0;width:1040px;text-align:center;white-space:nowrap}
.ch{display:inline-block;white-space:pre;transform-origin:50% 70%}
#a{top:200px;font:400 200px/1 DS;color:#0f9648;-webkit-text-stroke:34px #fff;paint-order:stroke fill;filter:drop-shadow(10px 14px 0 rgba(6,74,33,.6)) drop-shadow(0 0 24px rgba(255,255,255,.35))}
#b{top:410px;font:400 205px/1 DS;color:#e8531f;-webkit-text-stroke:34px #fff;paint-order:stroke fill;filter:drop-shadow(12px 16px 0 #7a1c4d) drop-shadow(0 0 34px rgba(255,110,40,.5))}
#burst{position:absolute;left:60px;top:330px;width:960px;height:560px;opacity:0}
.dot{position:absolute;border-radius:50%}
</style>
<div id=w>
<svg id=burst viewBox="-480 -280 960 560"></svg>
<div id=a class=row></div><div id=b class=row></div>
<div class=dot id=d1 style="left:10px;top:150px;width:50px;height:50px;background:#1075bd"></div>
<div class=dot id=d2 style="left:960px;top:690px;width:42px;height:42px;background:#b72f77"></div>
<div class=dot id=d3 style="left:900px;top:170px;width:30px;height:30px;background:#ffa21f"></div>
<div class=dot id=d4 style="left:40px;top:730px;width:34px;height:34px;background:#0f9648"></div>
</div>
<script>
const E=t=>t<0?0:t>1?1:t, back=t=>{t=E(t);const s=2.2;t-=1;return t*t*((s+1)*t+s)+1}, out=t=>1-Math.pow(1-E(t),3);
function mk(id,txt){const el=document.getElementById(id);for(const c of txt){const s=document.createElement('span');s.className='ch';s.textContent=(c==" "?"\u00a0\u00a0":c);el.appendChild(s);}return [...el.children];}
const A=mk('a','מחוץ לפח?'), B=mk('b','לא נאסף!');
// starburst polygon
(function(){const n=22,pts=[];for(let i=0;i<n*2;i++){const r=(i%2?250:420)*(i%4==0?1.08:1),a=i/(n*2)*Math.PI*2;pts.push((Math.cos(a)*r*1.08).toFixed(1)+','+(Math.sin(a)*r*0.64).toFixed(1));}
document.getElementById('burst').innerHTML='<polygon points="'+pts.join(' ')+'" fill="#ffd21f" fill-opacity=".38" stroke="#b72f77" stroke-opacity=".55" stroke-width="10"/>';})();
function R(t,D){
 A.forEach((c,i)=>{const p=back((t-0.0-i*0.045)/0.4);const rot=(i%2?1:-1)*(5+3*((i*7)%3))*(1-p)+((i%3)-1)*2.5;c.style.opacity=E((t-i*0.045)/0.1);c.style.transform=`translateY(${(1-p)*-120+Math.sin(t*3+i)*3}px) scale(${0.3+0.7*p}) rotate(${rot}deg)`;});
 B.forEach((c,i)=>{const p=back((t-0.6-i*0.05)/0.35);const rot=((i%2)?1:-1)*(8*(1-p))+((i%3)-1)*3;c.style.opacity=E((t-0.6-i*0.05)/0.08);c.style.transform=`translateY(${(1-p)*140+Math.sin(t*3.4+i)*4}px) scale(${2.3-1.3*p}) rotate(${rot}deg)`;});
 const bb=document.getElementById('burst'); const kb=E((t-0.95)/0.2); bb.style.opacity=kb*0.95; bb.style.transform=`scale(${0.5+0.5*back((t-0.95)/0.35)}) rotate(${Math.sin(t*1.5)*2}deg)`;
 const ti=t-1.05, sh=(ti>0&&ti<0.4)?Math.sin(ti*80)*12*(1-ti/0.4):0; const w=document.getElementById('w'); w.style.transform=`translate(${sh}px,${sh*0.6}px)`;
 for(const [i,ph] of [[1,0],[2,1.3],[3,2.1],[4,3.2]]){const d=document.getElementById('d'+i);const k=E((t-1.0-ph*0.05)/0.3);d.style.opacity=k;d.style.transform=`scale(${k*(1+0.25*Math.sin(t*6+ph))})`;}
 document.body.style.opacity=0.95*E((D-t)/0.5);
}
</script>"""
open("slogan.html","w").write(html)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox","--allow-file-access-from-files"])
    pg=b.new_page(viewport={"width":1620,"height":1080}); pg.goto("file://"+os.path.abspath("slogan.html")); pg.wait_for_timeout(1000)
    for i in range(N):
        pg.evaluate(f"R({i/FPS},{D})"); pg.screenshot(path=f"slogan_frames/f{i:03d}.png",omit_background=True)
    b.close()
print(N,"frames",D)
