// usage: node render.js out_dir [fps] [t0] [t1] | node render.js out_dir --times 1,2,3
const { chromium } = require('playwright'); const fs=require('fs'), path=require('path');
const out=process.argv[2]; const a=process.argv.slice(3);
const times = a[0]==='--times' ? a[1].split(',').map(Number) : null;
const fps = times?24:(Number(a[0])||24), t0=Number(a[1]||0), t1=Number(a[2]||64.4);
(async()=>{
  const meta=fs.readFileSync(path.join(__dirname,'web/assets/sprites.json'),'utf8');
  const html=fs.readFileSync(path.join(__dirname,'web/index.html'),'utf8').replace('%META%',meta);
  fs.writeFileSync(path.join(__dirname,'web/_built.html'),html);
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:720,height:1280}});
  p.on('pageerror',e=>console.error('PAGEERR',e.message)); p.on('console',m=>{if(m.type()==='error')console.error('CONSOLE',m.text())});
  await p.goto('file://'+path.join(__dirname,'web/_built.html')); await p.waitForFunction(()=>window.READY,{timeout:60000});
  const list = times || Array.from({length:Math.round((t1-t0)*fps)},(_,i)=>t0+i/fps);
  let n=0; for(const t of list){ await p.evaluate(x=>window.setT(x),t); const name=times?('t'+String(t).replace('.','_')+'.jpg'):String(n).padStart(5,'0')+'.jpg';
    await p.screenshot({path:path.join(out,name),type:'jpeg',quality:88}); n++; }
  await b.close(); console.log('frames',n);
})();
