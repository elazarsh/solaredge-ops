import sys,asyncio,os,subprocess,time
from playwright.sync_api import sync_playwright
ts=[float(x) for x in sys.argv[1:]] if len(sys.argv)>1 else None
srv=subprocess.Popen(["python3","-m","http.server","8765","--directory","web"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=b.new_page(viewport={"width":1280,"height":720})
        msgs=[]
        pg.on("console",lambda m:msgs.append(m.text)); pg.on("pageerror",lambda e:msgs.append("ERR "+str(e)))
        pg.goto("http://localhost:8765/anim.html")
        pg.wait_for_function("window.READY===true",timeout=60000)
        os.makedirs("frames",exist_ok=True)
        if ts:
            for t in ts:
                pg.evaluate(f"window.renderFrame({t})"); pg.locator("#c").screenshot(path=f"frames/t_{t:05.2f}.png")
        else:
            n=int(35*25)
            for i in range(n):
                pg.evaluate(f"window.renderFrame({i/25})"); pg.locator("#c").screenshot(path=f"frames/f{i:04d}.png")
                if i%100==0: print(i,flush=True)
        print("\n".join(msgs[:10]))
        b.close()
finally:
    srv.terminate()
