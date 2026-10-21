import random,os,sys,json,time,base64,urllib.request,urllib.error,threading,concurrent.futures as cf
from PIL import Image
from plan import P
KEY=os.environ["GEMINI_API_KEY"];B="https://generativelanguage.googleapis.com/v1beta/"
ids=['K6']+[p[0] for p in P];D={p[0]:p for p in P}
TR=[(ids[i],ids[i+1]) for i in range(len(ids)-1)]
G=("Hand-drawn charcoal animation on warm beige paper, shot on twos with a slightly boiling hand-drawn line. The first drawing transforms into the last drawing in one continuous organic transition: charcoal smoke and ink sweep across the paper, hiding some parts and revealing the new drawing, while figures and objects move naturally with life (breathing, walking, swaying). ")
END=" Do not add any other writing or letters beyond those that exist in the final drawing. No cuts, no photographic look. Silent."
def call(url,data=None):
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    return json.load(urllib.request.urlopen(r,timeout=300))
def enc(n):
    im=Image.open(f'img/{n}.png').convert('RGB');im.thumbnail((1920,1080));im.save(f'img/{n}_in.jpg',quality=92)
    return {"bytesBase64Encoded":base64.b64encode(open(f'img/{n}_in.jpg','rb').read()).decode(),"mimeType":"image/jpeg"}
MODELS=["veo-3.1-lite-generate-preview","veo-3.1-lite-generate-preview"]
def run(a,b):
    out=f'veo/{a}_{b}.mp4'
    if os.path.exists(out):return 'exists'
    while not(os.path.exists(f'img/{a}.png') and os.path.exists(f'img/{b}.png')):time.sleep(20)
    cam=D[b][5]
    prompt=G+"Camera: "+cam+". Final drawing: "+D[b][3][:230]+END
    body={"instances":[{"prompt":prompt,"image":enc(a),"lastFrame":enc(b)}],"parameters":{"aspectRatio":"16:9","durationSeconds":8,"resolution":"720p"}}
    mi=0;fails=0
    attempt=-1
    while True:
        attempt+=1
        m=MODELS[mi%2]
        try:op=call(B+f"models/{m}:predictLongRunning",body)
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:150].replace('\n',' ')
            print(a,b,m,'HTTP',e.code,msg[:80],flush=True)
            if e.code==429:mi+=1;time.sleep(75+random.random()*30);continue
            fails+=1;time.sleep(20);mi+=1;continue
        except Exception as e:print(a,b,'EXC',str(e)[:80],flush=True);time.sleep(20);continue
        name=op["name"]
        try:
            while not op.get("done"):time.sleep(10);op=call(B+name)
        except Exception as e:print(a,b,'poll EXC',str(e)[:80],flush=True);time.sleep(20);continue
        if "error" in op or "generatedSamples" not in op.get("response",{}).get("generateVideoResponse",{}):
            print(a,b,m,'ERR',json.dumps(op)[:200],flush=True);mi+=1;time.sleep(10);continue
        uri=op["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
        r=urllib.request.Request(uri,headers={"x-goog-api-key":KEY});open(out,'wb').write(urllib.request.urlopen(r,timeout=300).read())
        return 'ok '+m

if __name__=='__main__':
    n=int(sys.argv[1]) if len(sys.argv)>1 else 4
    with cf.ThreadPoolExecutor(n) as ex:
        futs=[(t,ex.submit(run,*t)) for t in TR]
        for t,f in futs:print('RESULT',t,f.result(),flush=True)
