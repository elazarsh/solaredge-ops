const {chromium}=require('../anim/pw/node_modules/playwright-core');
const http=require('http'),fs=require('fs'),path=require('path');
const times=process.argv.slice(2).map(Number);
const srv=http.createServer((q,r)=>{let p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));if(!fs.existsSync(p)){r.writeHead(404);r.end();return}const ext=path.extname(p);r.writeHead(200,{'Content-Type':{'.html':'text/html;charset=utf-8','.js':'text/javascript','.woff2':'font/woff2','.jpg':'image/jpeg','.png':'image/png'}[ext]||'application/octet-stream'});fs.createReadStream(p).pipe(r)}).listen(8796);
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--force-color-profile=srgb']});
 const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.log('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
 await p.goto('http://localhost:8796/page3.html');await p.evaluate(()=>window.preload());
 fs.mkdirSync('tmp/q',{recursive:true});
 for(const t of times){await p.evaluate(t=>window.seek(t),t);await p.waitForTimeout(40);await p.screenshot({path:`tmp/q/${t.toFixed(1)}.jpg`,type:'jpeg',quality:82})}
 await b.close();srv.close();
})();
