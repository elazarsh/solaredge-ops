import os,sys,json,base64,urllib.request,re,io
import numpy as np
from PIL import Image
KEY=os.environ["GEMINI_API_KEY"]
def segment(img_path,label):
    im=Image.open(img_path).convert('RGB');W,H=im.size
    t=im.copy();t.thumbnail((1024,1024));buf=io.BytesIO();t.save(buf,'JPEG',quality=90)
    prompt=f"Give the segmentation mask for: {label}. Output a JSON list; each entry has \"box_2d\" as [ymin,xmin,ymax,xmax] normalized to 0-1000, \"mask\" as the base64 PNG probability map (cropped to the box), and \"label\". Only the single best matching object."
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"image/jpeg","data":base64.b64encode(buf.getvalue()).decode()}},{"text":prompt}]}],"generationConfig":{"temperature":0,"responseMimeType":"application/json"}}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=180));txt=d['candidates'][0]['content']['parts'][0]['text']
    items=json.loads(txt);it=items[0] if isinstance(items,list) else items
    y0,x0,y1,x1=it['box_2d'];full=np.zeros((H,W),np.float32)
    ys0,xs0,ys1,xs1=int(y0/1000*H),int(x0/1000*W),int(y1/1000*H),int(x1/1000*W)
    m=it.get('mask','')
    if m:
        m=re.sub(r'^data:image/\w+;base64,','',m);mk=Image.open(io.BytesIO(base64.b64decode(m))).convert('L').resize((max(1,xs1-xs0),max(1,ys1-ys0)))
        full[ys0:ys1,xs0:xs1]=np.asarray(mk,np.float32)/255.0
    else:full[ys0:ys1,xs0:xs1]=1.0
    return full,(x0/1000,y0/1000,x1/1000,y1/1000)
if __name__=='__main__':
    m,box=segment(sys.argv[1],sys.argv[2]);print(box,m.mean());Image.fromarray((m*255).astype(np.uint8)).resize((960,540)).save('seg_test.png')
