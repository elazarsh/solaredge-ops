import os,sys,subprocess,time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(["python3","-m","http.server","8783","--directory","/tmp/claude-0/-home-user-solaredge-ops/b739defe-bfc9-5521-91fd-2d6f235476f6/scratchpad"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=b.new_page(viewport={"width":1920,"height":1080}); pg.goto("http://localhost:8783/pan/title.html"); pg.wait_for_function("window.READY===true"); pg.wait_for_timeout(400)
        os.makedirs("title",exist_ok=True)
        for i in range(int(4.3*25)): pg.evaluate(f"T({i/25})"); pg.screenshot(path=f"title/t{i:04d}.png",omit_background=True)
        b.close()
finally: srv.terminate()
