# -*- coding: utf-8 -*-
import json,os,sys
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from PIL import Image,ImageOps
from catalog_data import C,X,VID
from scenes import S,timeline,BEAT
SCR="/tmp/claude-0/-home-user-solaredge-ops/73fe8d55-5833-5852-9694-53b5adaa6cc2/scratchpad"
files_rel=json.load(open(f"{SCR}/order.json")); files=[f"{SCR}/{p}" for p in files_rel]; titles=json.load(open(f"{SCR}/files.json"))
san=lambda t:t.replace(' ','_').replace('(','').replace(')','')
orig={}
for folder,v in titles.items():
    for fid,t in v: orig[f"src/{folder}/{san(t)}"]=t
used={}
for s in S:
    for i in s[3]:
        if isinstance(i,int): used.setdefault(i,[]).append(s[0])
HDR=PatternFill("solid",fgColor="1F4E79");HF=Font(bold=True,color="FFFFFF",name="Arial",size=11)
thin=Side(style="thin",color="BBBBBB");B=Border(left=thin,right=thin,top=thin,bottom=thin)
AFILL={"A":"C6EFCE","B":"FFEB9C","C":"EDEDED","X":"FFC7CE"}
def sheet(wb,name,headers,widths):
    ws=wb.create_sheet(name); ws.sheet_view.rightToLeft=True
    ws.append(headers)
    for c,w in enumerate(widths,1):
        ws.column_dimensions[get_column_letter(c)].width=w
        cell=ws.cell(1,c); cell.fill=HDR;cell.font=HF;cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True);cell.border=B
    ws.row_dimensions[1].height=32; ws.freeze_panes="B2"; return ws
def fmt(ws,start=2):
    for r in ws.iter_rows(min_row=start):
        for c in r:
            c.alignment=Alignment(vertical="top",wrap_text=True,horizontal="right");c.border=B;c.font=Font(name="Arial",size=10)
wb=Workbook();wb.remove(wb.active)
# ---------- 1 קטלוג
ws=sheet(wb,"1 קטלוג תמונות",["תצוגה","שם קובץ","קטגוריה מזוהה","תת-נושא","ציון רגשי (1-10)","ציון איכות חזותית (1-10)","משך מומלץ (שנ')","עדיפות","בשימוש בסצנות","סוג צילום","כיוון","רזולוציה","הערות","אישור פרסום (הורים) – למילוי"],[16,34,16,22,10,10,10,9,14,18,8,12,40,16])
os.makedirs("thumbs_tmp",exist_ok=True)
rows=[]
for i,f in enumerate(files):
    f_rel=files_rel[i]; im=ImageOps.exif_transpose(Image.open(f)); w,h=im.size
    ori="אנכית" if h>w*1.05 else ("מרובעת" if abs(h-w)<=w*.05 else "אופקית")
    name=orig.get(f_rel,os.path.basename(f))
    if i in C:
        cat,sub,shot,e,q,d,p,note=C[i]
        folder=f_rel.split("/")[1]
        rows.append((i,[None,name,folder if cat==folder else f"{folder} ({cat})",sub,e,q,d if d else "—",p,", ".join(used.get(i,[])) or ("—"),shot,ori,f"{w}x{h}",note,""],p,im))
    else:
        cat,note=X[i]
        rows.append((i,[None,name,f_rel.split("/")[1],cat,"—","—","—","לא לשימוש","—","—",ori,f"{w}x{h}",note,""],"X",im))
for v,(t,e,q,d,p,note) in VID.items():
    rows.append((None,[None,os.path.basename(v),v.split('/')[0],t,e,q,d if d else "—",p,"S34" if p=="A" else "—","וידאו","אופקית","848x480",note,""],p,None))
for n,(i,vals,p,im) in enumerate(rows,2):
    ws.append(vals)
    if im is not None:
        im2=im.copy(); im2.thumbnail((110,85)); tp=f"thumbs_tmp/{i}.jpg"; im2.convert("RGB").save(tp,quality=70)
        xi=XLImage(tp); ws.add_image(xi,f"A{n}")
    ws.row_dimensions[n].height=68
    ws.cell(n,8).fill=PatternFill("solid",fgColor=AFILL.get(p,"FFFFFF"))
fmt(ws)
ws.auto_filter.ref=f"A1:N{ws.max_row}"
# ---------- 2 סטוריבורד
ws=sheet(wb,"2 סטוריבורד",["ציר זמן","מס' סצנה","משך (שנ')","תמונות בשימוש","סוג מעבר","תנועת מצלמה","טקסט על המסך","קריינות","סימן מוזיקלי","מערך","סוג צילום","פרק בסיפור"],[14,9,9,22,24,22,32,12,40,14,22,14])
tl,total=timeline()
CAM={"push":"Push-in איטי (100%→112%)","pull":"Pull-out / זום החוצה (114%→100%)","panR":"Ken Burns – פאן ימינה (זום 108%)","panL":"Ken Burns – פאן שמאלה (זום 108%)","hold":"החזקה עם דריפט כמעט בלתי-מורגש (100%→103%)","punch":"Punch-in מהיר (100%→106%) על הפעימה","video":"וידאו חי + push עדין (100%→104%)","dim":"רקע איטי, בהירות 30%","logo":"אנימציית לוגו (ראו גיליון 5)","tiltUp":"Tilt-up"}
def tc(x):return f"{int(x//60)}:{x%60:05.2f}"
for s,(sid,a,b) in zip(S,tl):
    imgs=[]
    for i in s[3]:
        if isinstance(i,int): imgs.append(os.path.basename(files[i]).replace("WhatsApp_Image_","IMG ")+f" [#{i}]")
        else: imgs.append({"V1":"וידאו: ילד מנגן פסנתר","BG":"רקע גרדיינט (גרפי)","LOGO_HB":"לוגו הר ברכה (מקור 2.png)","LOGO_MATNAS":"לוגו מתנ\"ס (מקור 1.jpg, ללא שומרון)","LOGO_BOTH":"שני הלוגואים"}[i])
    ws.append([f"{tc(a)}–{tc(b)}",s[0],s[2],"\n".join(imgs),s[4],CAM[s[5]],s[7],"—",s[8],"דיפטיך (2 תמונות)" if len(s[3])==2 else "יחיד",s[6],s[1]])
fmt(ws)
r=ws.max_row+2
ws.cell(r,1,f"סה\"כ אורך: {total:.0f} שנ' | {len(S)} סצנות | 30fps | 1920x1080 | BPM 100 (פעימה=0.6 שנ'; כל חיתוך על פעימה)").font=Font(bold=True)
# ---------- 3 עריכה
ws=sheet(wb,"3 הוראות עריכה",["סצנה","זום","פאן","חיתוך (Crop)","מהירות","פייד","אפקטים חזותיים","נקודת מיקוד"],[8,24,26,34,12,22,38,28])
ZOOM={"push":("100% → 112%","מרכז, איטי"),"pull":("114% → 100%","מרכז, איטי"),"panR":("108% קבוע","שמאל → ימין, 6% מרוחב הפריים"),"panL":("108% קבוע","ימין → שמאל, 6% מרוחב הפריים"),"hold":("100% → 103%","ללא פאן / דריפט אלכסוני 1%"),"punch":("100% → 106% ב-0.6 שנ'","קפיצה קצרה על הפעימה"),"video":("100% → 104%","ללא"),"dim":("100% → 105%, איטי מאד","ללא"),"logo":("ראו גיליון 5","ראו גיליון 5")}
for s in S:
    z,p=ZOOM[s[5]]
    n=len(s[3]); sid=s[0]
    if s[5]=="logo": crop="לוגו על רקע בהיר/לבן, מרווח ביטחון 8%"
    elif sid=="C03": crop="גרדיינט כחול-כהה (#0B2545 → #13315C)"
    elif n==2: crop="דיפטיך: שני פאנלים 944x1080 עם מרווח 8px; חיתוך אנכי-לפנים, שערים נוגדי-פאן (אחד עולה, אחד יורד)"
    elif s[2]<=1.2: crop="16:9 ממורכז סביב נקודת המיקוד; לא לחתוך ראשים"
    else: crop="16:9 + מרווח זום 12%; חיתוך חותמות תאריך (אם יש)"
    spd="100%" if s[5]!="video" else "100% (קול מקורי)"
    fade="פייד שחור 0.8 שנ'" if sid=="S01" else ("עמעום תוך 1.2 שנ' לשחור בסוף" if sid=="L03" else ("הצלבה 0.6 שנ'" if "הצלבה" in s[4] else "חיתוך ישיר"))
    fx="גריידינג חם (+8 חמימות, +5 ניגודיות), ויניטה עדינה"
    if s[5]=="punch": fx+="; רעידה קצרה 2px על ההיט"
    if s[4].startswith("Whip"): fx+="; טשטוש תנועה אופקי 6 פריימים"
    if s[4].startswith("זום"): fx+="; זום-דרך עם טשטוש רדיאלי קל"
    if s[5]=="dim": fx="בהירות 30%, טשטוש רקע 2px, חלקיקי אור (bokeh) איטיים"
    if s[5]=="logo": fx="ראו גיליון 5"
    ws.append([sid,z,p,crop,spd,fade,fx,s[9]])
fmt(ws)
# ---------- 4 ציר זמן
ws=sheet(wb,"4 ציר זמן הפקה",["שנייה","סצנה","פרק","תמונה/אלמנט פעיל","תנועה","טקסט על המסך","הערת מוזיקה","פעימות (0.6 שנ')"],[8,8,14,34,26,34,40,16])
beat_notes={0:"פסנתר בודד",12:"נוספת גיטרה",20.4:"ריזר 2 תיבות",20.4:"דרופ: תופים + בס",54:"האטה: מיתרים",82.8:"שקט בין משפטים",94.8:"היט לוגו",104.4:"אקורד אחרון"}
sec_music=[(0,"קטע א' – סקרנות: פסנתר/גיטרה, 90→100 BPM, חמים, דליל"),(18,"ריזר – בניית מתח"),(20.4,"קטע ב' – אנרגיה: תופים, בס, מחיאות; 100 BPM"),(52,"האטה – מיתרים נכנסים"),(54,"קטע ג' – צמיחה: פסנתר + מיתרים, רגשי"),(72,"קרשנדו – קהילה"),(82.8,"סיום: דליל, קטעי שקט בין המשפטים"),(94.8,"לוגו: היט + 'שוש' + אקורד אחרון")]
def msec(t):
    m=""
    for a,b in sec_music:
        if t>=a: m=b
    return m
for sec in range(int(total)):
    t0,t1=sec,sec+1
    act=[(s,a,b) for s,(sid,a,b) in zip(S,tl) if a<t1-1e-9 and b>t0+1e-9]
    ids=" / ".join(s[0] for s,_,_ in act)
    el=[]
    for s,_,_ in act:
        el.append(", ".join(f"#{i}" if isinstance(i,int) else str(i) for i in s[3]))
    txt=" | ".join(s[7] for s,a,b in act if s[7] and a<t1 and b>t0 and (a>=t0 or t0<a+4))
    ws.append([f"{tc(sec)}",ids,act[0][0][1],"; ".join(el),"; ".join(CAM[s[5]].split(" (")[0] for s,_,_ in act),txt,msec(sec),f"{sec/BEAT:.1f}–{(sec+1)/BEAT:.1f}"])
fmt(ws)
# ---------- 5 לוגו
ws=sheet(wb,"5 רצף לוגואים",["שלב","זמן (בתוך הרצף)","מה קורה","פירוט טכני"],[8,16,48,70])
LOGO=[
("L01-a","94.8–95.4","רקע לבן נקי; פתאום 'נשמעים' פעימות (היט)","הפרדת לוגו הר ברכה לשכבות לפי צבע (בניינים כחול/כתום, עץ ורוד, עצים ירוקים, בית ירוק, דמויות מחוברות בידיים, גבעה, טקסט 'הר ברכה', כיתוב 'עיר העתיד של השומרון')"),
("L01-b","95.4–98.4","החלקים 'עפים' פנימה מהצדדים ומתיישבים: גבעה → בניינים → עצים → בית → 3 הדמויות המחוברות (קפיצה קטנה) → טקסט","כל שכבה: תנועת כניסה 12–18 פריימים, ease-out-back, סטגר 5 פריימים בין שכבות; הדמויות מקבלות 'בום' קטן (scale 1.15→1.0)"),
("L01-c","98.4–98.4","הלוגו שלם – החזקה על פעימה, מתחיל להתכווץ ולזוז לצד","הלוגו מתכווץ ל-45% ונע ל-1/3 הימני של המסך (בסוף: lockup)"),
("L02-a","98.4–100.2","לוגו מתנ\"ס – פתיחה בזום חזק על 3 הדמויות (כתום, ורוד, כחול) – הן קופצות משמחה","שכבות הדמויות מופרדות; זום 320% על מרכז הדמויות; לופ קפיצה: כל דמות עולה/יורדת 4–6% בגובה, בפאזה שונה (כל 0.6 שנ'), הילד הוורוד מוחזק בידיים – תנועת 'ריבאונד'"),
("L02-b","100.2–103.4","זום החוצה לאורך 3.2 שנ'; בזמן הזום מתלבשים בשלבים: גבעה ירוקה → העצים → הספר הסגול → השמש הכתומה → קו מקווקו מצויר (draw-on) → הלב הירוק → כיתוב 'מתנ\"ס' → 'הר-ברכה'","כל שכבה נכנסת לפי הסדר עם 0.4 שנ' הפרש; הקו המקווקו – מסכה אנימטיבית לאורך הנתיב; הזום עם ease-in-out, מסתיים ב-100%"),
("L02-c","103.4–104.4","הלוגו שלם – החזקה קצרה והתיישבות לצד שמאל","הלוגו מתכווץ ל-45% ונע לשליש השמאלי"),
("L03-a","104.4–106.8","'חיבוק': שני הלוגואים מתקרבים זה לזה ופסי אור/חלקיקים ירוקים-כתומים נמשכים ביניהם","הלוגואים נעים 6% זה לקראת זה ('חיבוק'), חלקיקי אור צבעוניים נצמדים לקו המפגש, קו אנכי דק מופיע במרכז"),
("L03-b","106.8–108.0","החזקה סופית ופייד לשחור","כיתוב קטן מתחת: 'מתנ\"ס הר ברכה · הר ברכה – עיר העתיד של השומרון'; פייד אל לבן/שחור 0.8 שנ'"),
]
for r in LOGO: ws.append(list(r))
ws.append([]);ws.append(["הערות","","",""])
for n in ["מקור לוגו מתנ\"ס: 1.jpg – חותכים רק את החלק השמאלי (מסירים לוגו 'מועצה אזורית שומרון').","מקור לוגו הר ברכה: 2.png (רקע שקוף).","הפרדה לשכבות נעשית בקוד לפי צבע + רכיבים מחוברים (לא נדרש קובץ מקור וקטורי), נבדק ויזואלית לפני הפקה."]:
    ws.append(["•",n,"",""])
fmt(ws)
# ---------- 6 מוזיקה ופתוחים
ws=sheet(wb,"6 מוזיקה והחלטות",["נושא","המלצה / שאלה","סטטוס"],[24,100,20])
for r in [
("מוזיקה – סגנון","אקוסטית-פופ אופטימית: פסנתר, גיטרה פריטה, מחיאות, בס חם; תופים מאמצע הסרט; מיתרים לסיום. ללא שירה.","המלצה"),
("מוזיקה – BPM","100 BPM קבוע (פעימה = 0.6 שנ') – כל החיתוכים מסונכרנים. תקציב: 108 שנ' = 180 פעימות = 45 תיבות.","המלצה"),
("מוזיקה – התקדמות","0:00–0:20 סקרנות (דליל) · 0:20–0:54 אנרגיה (דרופ) · 0:54–1:12 צמיחה (רגשי) · 1:12–1:22 קהילה (קרשנדו) · 1:22–1:35 דליל + שקטים · 1:35–1:48 לוגו","המלצה"),
("מוזיקה – רישיון","צריך רצועה ברישיון לשימוש פומבי (Artlist/Epidemic/Pixabay Music/YouTube Audio Library). לציין BPM 100 בחיפוש. אפשר גם אני אייצר רצועה טכנית-זמנית (מטרונום+אקורדים) להדגמה בלבד.","נדרשת החלטה"),
("קריינות","המלצה: ללא קריינות (כתוביות עבריות בלבד) – תמיד ניתן לצפות בלי קול בקבוצות ווטסאפ. אופציונלי: הקלטת קול אנושי לשלושת משפטי הסיום.","נדרשת החלטה"),
("מספרים שיופיעו","600+ משתתפים בחוגים · 500 ילדים בקייטנות הקיץ · 70 תלמידי מוזיקה. (חוץ מזה אין מספרים.)","לאישור"),
("משחקייה","תיקיית 'משחקיה' ריקה – אין תמונות. נתונים (5,000 ביקורים, 25 משפחות) לא מופיעים בסרט. אם יש תמונות – אשלב.","חסר חומר"),
("בית ספר למוזיקה","תמונות הבניין החדש הן מתקופת בנייה (#28, #29) ולכן לא בשימוש; חדר התופים החדש (#33) לא נכנס. אפשר להוסיף תמונת בניין גמור.","חסר חומר"),
("מתחברים ביחד","יש 3 תמונות רלוונטיות (#34, #35, #36) – משולבות. מתאים להוסיף עוד תמונה של חונך+ילד.","הצעה"),
("פנים ילדים","זיהוי פנים ביומטרי לא בוצע (שיקולי פרטיות); דירוג ובחירה בוצעו ידנית. נדרש אישור הורים/המתנ\"ס לפרסום – עמודה בקטלוג.","נדרש אישור"),
("שפה","כל הטקסטים בעברית (RTL), פונט Heebo/Assistant בהתאם למותג (כחול #1275BC, כתום #E97F2D, ירוק #0F9549, סגול #B5306F).","החלטה בוצעה"),
("תאריך הרשמה","הסרט מסתיים ב'נפתחת בקרוב'. אם יש תאריך/קישור/טלפון – אפשר להוסיף שורה אחרי הלוגו (3.6 שנ').","פתוח"),
("גרסאות נוספות","אחרי אישור: גרסת 9:16 לווטסאפ/סטורי וגרסה קצרה 45 שנ'.","הצעה"),
("מועצה אזורית שומרון","הוסר מהסרט לפי בקשה (לוגו חתוך).","בוצע"),
]: ws.append(list(r))
fmt(ws)
wb.save("storyboard_har_bracha.xlsx"); print("saved",total)
