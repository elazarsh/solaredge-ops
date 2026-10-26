import sys,os,json,subprocess,time
from playwright.sync_api import sync_playwright
cfg=json.load(open("cfg.json")); n=int(float(sys.argv[1])*25)
srv=subprocess.Popen(["python3","-m","http.server","8782","--directory","/tmp/claude-0/-home-user-solaredge-ops/b739defe-bfc9-5521-91fd-2d6f235476f6/scratchpad"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=b.new_page(viewport={"width":1920,"height":1080}); msgs=[]
        pg.on("pageerror",lambda e:msgs.append("ERR "+str(e)))
        pg.goto("http://localhost:8782/ind/ind.html"); pg.wait_for_function("window.READY===true",timeout=60000); pg.wait_for_timeout(500)
        pg.evaluate("e=>{ENV=e}",json.load(open("env.json"))); pg.evaluate("c=>{CFG=c}",cfg)
        pg.add_style_tag(content="html,body,#root,.scene{background:transparent!important}#s6>img,#s6>div:not(.row):not(#s6t),#wipe,#fade,#s6t{display:none!important}")
        os.makedirs("slogan",exist_ok=True)
        for i in range(n):
            pg.evaluate(f"R({21.3+i/25})"); pg.screenshot(path=f"slogan/s{i:04d}.png",omit_background=True)
        print("\n".join(msgs[:6])); b.close()
finally: srv.terminate()
