import sys,os,json,subprocess,time
from playwright.sync_api import sync_playwright
mode=sys.argv[1]  # preview or full or final
srv=subprocess.Popen(["python3","-m","http.server","8771","--directory","/tmp/claude-0/-home-user-solaredge-ops/b739defe-bfc9-5521-91fd-2d6f235476f6/scratchpad"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=b.new_page(viewport={"width":1920,"height":1080}); msgs=[]
        pg.on("console",lambda m:msgs.append(m.text)); pg.on("pageerror",lambda e:msgs.append("ERR "+str(e)))
        pg.goto("http://localhost:8771/tech/tech.html"); pg.wait_for_function("window.READY===true",timeout=60000); pg.wait_for_timeout(500)
        if os.path.exists("env.json"): pg.evaluate("e=>{ENV=e}",json.load(open("env.json")))
        os.makedirs("frames",exist_ok=True)
        if mode=="preview":
            for t in [float(x) for x in sys.argv[2:]]:
                pg.evaluate(f"R({t})"); pg.screenshot(path=f"frames/p_{t:05.2f}.jpg",type="jpeg",quality=90)
        elif mode=="full":
            T=float(sys.argv[2]); n=int(T*25)
            for i in range(n):
                pg.evaluate(f"R({i/25})"); pg.screenshot(path=f"frames/f{i:04d}.jpg",type="jpeg",quality=93)
                if i%100==0: print(i,flush=True)
        elif mode=="final":
            n=int(float(sys.argv[2])*25)
            for i in range(n):
                pg.evaluate(f"F({i/25})"); pg.screenshot(path=f"frames/g{i:04d}.jpg",type="jpeg",quality=93)
        print("\n".join(m for m in msgs if "404" not in m)[:1500]); b.close()
finally: srv.terminate()
