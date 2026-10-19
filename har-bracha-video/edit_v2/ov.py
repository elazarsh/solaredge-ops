import json,os
from playwright.sync_api import sync_playwright
CAPS={
 "k1a":"תיכנסו. שימו לב לאור, שימו לב לקירות: ממוחזרים, בלי רטיבות.",
 "l1":"וואו!","k1b":"חוץ מגשם.","y1":"ומה עם הארנונה?","k2":"אין ארנונה.","l2":"אין?","k3":"המועצה לא אוספת כאן כלום.",
 "k4a":"אז תושבים, בקצרה:","k4b":"קרטונים – לקרטוניה","k4c":"גזם – לפינת הגזם","k4d":"שקיות – לתוך הפח",
 "y2":"אוף, זה הבית שלנו.","l3":"ואני כבר קניתי וילונות.","n1a":"ושלחו ילד בגיל המתאים לזרוק את הפח","n1b":"מחוץ לפח – לא נאסף"}
html="""<style>@font-face{font-family:H;src:url(fonts/Heebo-Bold.ttf);font-weight:700}
html,body{margin:0;background:transparent}
.cap{width:1620px;height:200px;display:flex;align-items:center;justify-content:center;font:700 64px H;direction:rtl;color:#fff;
-webkit-text-stroke:0;text-shadow:0 0 0 #000;paint-order:stroke fill}
.cap span{-webkit-text-stroke:14px rgba(0,0,0,.92);paint-order:stroke fill;padding:0 40px;text-align:center;line-height:1.15}
.sign{width:1300px;height:150px;display:flex;align-items:center;justify-content:center;background:#0f9648;border-radius:36px;color:#fff;font:700 70px H;direction:rtl;
box-shadow:0 10px 30px rgba(0,0,0,.35)}
</style><div id=r></div>"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox","--allow-file-access-from-files"])
    pg=b.new_page(viewport={"width":1620,"height":400}); 
    open("ov/_t.html","w").write(html); pg.goto("file://"+os.path.abspath("ov/_t.html"))
    for k,t in CAPS.items():
        pg.evaluate("t=>{document.getElementById('r').innerHTML='<div class=cap id=e><span>'+t+'</span></div>'}",t)
        pg.wait_for_timeout(150); pg.locator("#e").screenshot(path=f"ov/cap_{k}.png",omit_background=True)
    pg.evaluate("()=>{document.getElementById('r').innerHTML='<div class=sign id=e>מחוץ לפח – המועצה לא אוספת.</div>'}")
    pg.wait_for_timeout(150); pg.locator("#e").screenshot(path="ov/sign.png",omit_background=True)
    b.close()
print(os.listdir("ov"))
