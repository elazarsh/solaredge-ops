import os,sys,json,base64,urllib.request,io,time
from PIL import Image
KEY=os.environ["GEMINI_API_KEY"]
def boxes(img_path,labels):
    im=Image.open(img_path).convert('RGB');im.thumbnail((1024,1024));buf=io.BytesIO();im.save(buf,'JPEG',quality=88)
    prompt=("Detect these objects in the drawing and return JSON: a list of {\"label\":..., \"box_2d\":[ymin,xmin,ymax,xmax]} normalized 0-1000, one entry per label, in the same order. Labels: "+"; ".join(labels))
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"image/jpeg","data":base64.b64encode(buf.getvalue()).decode()}},{"text":prompt}]}],"generationConfig":{"temperature":0,"responseMimeType":"application/json"}}
    for t in range(4):
        try:
            req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
            d=json.load(urllib.request.urlopen(req,timeout=90));return json.loads(d['candidates'][0]['content']['parts'][0]['text'])
        except Exception as e:print('retry',str(e)[:60],flush=True);time.sleep(8)
if __name__=='__main__':
    print(boxes(sys.argv[1],sys.argv[2:]))
