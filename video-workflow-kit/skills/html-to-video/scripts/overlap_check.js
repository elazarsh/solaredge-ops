// בדיקת חפיפות אוטומטית בדף ה-HTML של הסרטון: עוברת על כל הסרטון בצעדים (ברירת מחדל 0.5 ש'),
// אוספת מלבני טקסט אמיתיים (Range), מתעלמת מאלמנטים שקופים (opacity<0.3), ומדווחת:
//   OVERLAP (טקסט על טקסט), SPILL (טקסט יוצא מהקונטיינר), OFFSCREEN (יוצא מהמסך).
// יש תוצאות שווא (טקסט באותו אלמנט, חיתוך מכוון, מספרים עולים) -> תמיד לבדוק גם בעין (snap.js + contact_sheet.py).
// דרישות מהדף: <div id="scenes"> עם אלמנטים .scene, window.OFF (מערך זמני תחילת סצנה), window.TOTAL, seek(t), preload().
// שימוש: node overlap_check.js <dir> [--page page.html] [--step 0.5] [--containers ".cc,.mc,.ec,.panel,.bub,.chip"]
const path = require('path');
const { launch, serve } = require('./lib');
const args = process.argv.slice(2), opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
const flagVals = new Set(['--page', '--step', '--containers']);
const dir = path.resolve(args.filter((a, i) => !a.startsWith('--') && !flagVals.has(args[i - 1]))[0] || '.');
const step = +opt('step', 0.5), PORT = 8797, CONT = opt('containers', '.cc,.mc,.ec,.panel,.bub,.chip');
function collect(CONT){
  const out=[];const w=document.createTreeWalker(document.getElementById('scenes'),NodeFilter.SHOW_TEXT);let n;
  while(n=w.nextNode()){
    const s=n.nodeValue.trim();if(!s)continue;const el=n.parentElement;if(!el)continue;
    let op=1,vis=true,e=el,scene=null;
    while(e&&e.id!=='scenes'){const cs=getComputedStyle(e);op*=parseFloat(cs.opacity);if(cs.visibility==='hidden'||cs.display==='none'){vis=false;break}if(e.classList&&e.classList.contains('scene'))scene=e;e=e.parentElement}
    if(!vis||op<0.3)continue;
    const r=document.createRange();r.selectNodeContents(n);let rs=[...r.getClientRects()].filter(q=>q.width>3&&q.height>3);
    if(!rs.length){const b=el.getBoundingClientRect();if(b.width>3)rs=[b]}
    if(!rs.length)continue;
    let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const q of rs){x0=Math.min(x0,q.left);y0=Math.min(y0,q.top);x1=Math.max(x1,q.right);y1=Math.max(y1,q.bottom)}
    const cont=el.closest(CONT);let cb=null;if(cont){const b=cont.getBoundingClientRect();cb=[b.left,b.top,b.right,b.bottom]}
    out.push({s:s.slice(0,40),r:rs.map(q=>[q.left,q.top,q.right,q.bottom]),box:[x0,y0,x1,y1],cb,op});
  }
  return out;
}
(async()=>{
 const srv=await serve(dir,PORT);const b=await launch();
 const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.log('PAGEERR',e.message));
 await p.goto(`http://localhost:${PORT}/${opt('page','page.html')}`);await p.evaluate(()=>window.preload());
 const total=await p.evaluate(()=>window.TOTAL),OFF=await p.evaluate(()=>window.OFF);
 const issues={};
 const sceneOf=t=>{let k=0;OFF.forEach((o,i)=>{if(t>=o)k=i});return k};
 for(let t=0.3;t<total;t+=step){
   const si=sceneOf(t);if(t-OFF[si]<0.9)continue; // skip reveal clip phase
   await p.evaluate(t=>window.seek(t),t);
   const items=await p.evaluate(collect,CONT);
   const rect=(a,b)=>{const w=Math.min(a[2],b[2])-Math.max(a[0],b[0]),h=Math.min(a[3],b[3])-Math.max(a[1],b[1]);return w>0&&h>0?w*h:0};
   const area=a=>(a[2]-a[0])*(a[3]-a[1]);
   for(let i=0;i<items.length;i++){
     const a=items[i];
     if(a.box[0]<-4||a.box[2]>1924||a.box[1]<-4||a.box[3]>1084)(issues['OFFSCREEN|'+si+'|'+a.s]??={t:[]}).t.push(t);
     if(a.cb){const c=a.cb;if(a.box[0]<c[0]-6||a.box[2]>c[2]+6||a.box[1]<c[1]-6||a.box[3]>c[3]+6)(issues['SPILL|'+si+'|'+a.s]??={t:[]}).t.push(t)}
     for(let j=i+1;j<items.length;j++){const c=items[j];let best=0;
       for(const ra of a.r)for(const rb of c.r){const ov=rect(ra,rb);if(ov>best)best=ov}
       const m=Math.min(area(a.box),area(c.box));
       if(best>0&&best/Math.min(...[a.r,c.r].map(rr=>Math.min(...rr.map(q=>(q[2]-q[0])*(q[3]-q[1])))))>0.15&&best>300)(issues['OVERLAP|'+si+'|'+a.s+' ⟂ '+c.s]??={t:[]}).t.push(t);
     }
   }
 }
 const keys=Object.keys(issues).sort();
 for(const k of keys){const t=issues[k].t;console.log(k,'@',t[0].toFixed(1),'-',t[t.length-1].toFixed(1),`(${t.length})`)}
 console.log('issues:',keys.length);
 await b.close();srv.close();
})();
