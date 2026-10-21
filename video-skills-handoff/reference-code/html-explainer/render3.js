const {chromium}=require('../anim/pw/node_modules/playwright-core');
const http=require('http'),fs=require('fs'),path=require('path');
const [w,nw,port]=process.argv.slice(2).map(Number);const FPS=24;
const srv=http.createServer((q,r)=>{let p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));if(!fs.existsSync(p)){r.writeHead(404);r.end();return}const ext=path.extname(p);r.writeHead(200,{'Content-Type':{'.html':'text/html;charset=utf-8','.js':'text/javascript','.woff2':'font/woff2','.jpg':'image/jpeg','.png':'image/png'}[ext]||'application/octet-stream'});fs.createReadStream(p).pipe(r)}).listen(port);
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--force-color-profile=srgb']});
 const p=await b.newPage({viewport:{width:1920,height:1080}});
 await p.goto(`http://localhost:${port}/page3.html`);await p.evaluate(()=>window.preload());
 const total=await p.evaluate(()=>window.TOTAL);const N=Math.ceil(total*FPS);
 const MAXF=process.env.MAXF?+process.env.MAXF:N;for(let f=w;f<Math.min(N,MAXF);f+=nw){
   const out=`tmp/g3/${String(f).padStart(5,'0')}.jpg`;if(fs.existsSync(out)&&!process.env.FORCE)continue;
   await p.evaluate(t=>window.seek(t),f/FPS);
   await p.screenshot({path:out,type:'jpeg',quality:90});
 }
 console.log('worker',w,'done');await b.close();srv.close();
})();
