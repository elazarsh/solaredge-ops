// usage: node render.js OUT --info                    -> prints TEND and writes OUT/sfx.json
//        node render.js OUT --frames i0 i1 [fps=24]   -> renders frames i0..i1-1 as OUT/%05d.jpg
//        node render.js OUT --times 1,2,3             -> test frames
const { chromium } = require('playwright'); const fs=require('fs'), path=require('path');
const out=process.argv[2]; const a=process.argv.slice(3);
(async()=>{
  const meta=fs.readFileSync(path.join(__dirname,'web/assets/sprites.json'),'utf8');
  const tl=fs.readFileSync(path.join(__dirname,'timeline.json'),'utf8');
  const html=fs.readFileSync(path.join(__dirname,'web/index.html'),'utf8').replace('%META%',meta).replace('%TL%',tl);
  const built=path.join(__dirname,`web/_built_${process.pid}.html`); fs.writeFileSync(built,html);
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:720,height:1280}});
  p.on('pageerror',e=>console.error('PAGEERR',e.message)); p.on('console',m=>{if(m.type()==='error')console.error('CONSOLE',m.text())});
  await p.goto('file://'+built); await p.waitForFunction(()=>window.READY,{timeout:120000});
  if(a[0]==='--info'){ const info=await p.evaluate(()=>({TEND,AUDIO_END,SFX})); fs.writeFileSync(path.join(out,'sfx.json'),JSON.stringify(info)); console.log('TEND',info.TEND,'sfx',info.SFX.length); }
  else {
    let list; const fps=Number(a[3]||24);
    if(a[0]==='--times') list=a[1].split(',').map(Number).map(t=>({t,name:'t'+String(t).replace('.','_')+'.jpg'}));
    else { const i0=Number(a[1]),i1=Number(a[2]); list=[]; for(let i=i0;i<i1;i++) list.push({t:i/fps,name:String(i).padStart(5,'0')+'.jpg'}); }
    for(const f of list){ await p.evaluate(x=>window.setT(x),f.t); await p.screenshot({path:path.join(out,f.name),type:'jpeg',quality:88}); }
    console.log('frames',list.length);
  }
  await b.close(); fs.unlinkSync(built);
})();
