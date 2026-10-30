import os,sys,subprocess,time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(["python3","-m","http.server","8791","--directory","."],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=b.new_page(viewport={"width":1080,"height":1440}); pg.goto("http://localhost:8791/logo34.html"); pg.wait_for_function("window.READY===true"); 
        os.makedirs("fr",exist_ok=True)
        times=[float(x) for x in sys.argv[2:]] if sys.argv[1]=="prev" else [i/30 for i in range(int(float(sys.argv[2])*30))]
        for i,t in enumerate(times):
            pg.evaluate(f"A({t})"); pg.screenshot(path=("prev_%04.2f.png"%t) if sys.argv[1]=="prev" else f"fr/f{i:04d}.png")
        b.close()
finally: srv.terminate()
