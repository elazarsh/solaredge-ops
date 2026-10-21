import os,sys,json,time,base64,urllib.request,urllib.error,random,concurrent.futures as cf
from PIL import Image
from shots import M
KEY=os.environ["GEMINI_API_KEY"];B="https://generativelanguage.googleapis.com/v1beta/"
G="Hand-drawn charcoal animation on warm beige paper, shot on twos with a slightly boiling line. "
END=" The camera stays still. The composition and every Hebrew letter or word in the drawing stay exactly as in the image and never change or morph; nothing new is added. Silent."
def call(url,data=None):
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={"Content-Type":"application/json","x-goog-api-key":KEY});return json.load(urllib.request.urlopen(r,timeout=300))
def enc(n):
    im=Image.open(f'img/{n}.png').convert('RGB');im.thumbnail((1920,1080));im.save(f'img/{n}_in.jpg',quality=92)
    return {"bytesBase64Encoded":base64.b64encode(open(f'img/{n}_in.jpg','rb').read()).decode(),"mimeType":"image/jpeg"}
MODELS=["veo-3.1-lite-generate-preview","veo-3.1-fast-generate-preview"]
def run(k):
    out=f'veo/shot_{k}.mp4'
    if os.path.exists(out):return 'exists'
    body={"instances":[{"prompt":G+M[k]+END,"image":enc(k)}],"parameters":{"aspectRatio":"16:9","durationSeconds":8,"resolution":"1080p"}}
    a=-1
    while True:
        a+=1;m=MODELS[0]
        try:op=call(B+f"models/{m}:predictLongRunning",body)
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:150].replace('\n',' ');print(k,m,'HTTP',e.code,msg[:70],flush=True)
            time.sleep(75+random.random()*30 if e.code==429 else 20);continue
        except Exception as e:print(k,'EXC',str(e)[:60],flush=True);time.sleep(20);continue
        try:
            while not op.get("done"):time.sleep(10);op=call(B+op["name"])
        except Exception as e:print(k,'poll',str(e)[:60],flush=True);time.sleep(20);continue
        g=op.get("response",{}).get("generateVideoResponse",{})
        if "error" in op or "generatedSamples" not in g:print(k,'ERR',json.dumps(op)[:160],flush=True);time.sleep(10);continue
        uri=g["generatedSamples"][0]["video"]["uri"];r=urllib.request.Request(uri,headers={"x-goog-api-key":KEY});open(out,'wb').write(urllib.request.urlopen(r,timeout=300).read());print(k,'ok',flush=True);return 'ok'
if __name__=='__main__':
    ks=[p for p in M];n=int(sys.argv[1]) if len(sys.argv)>1 else 2
    with cf.ThreadPoolExecutor(n) as ex:
        for k,r in zip(ks,ex.map(run,ks)):print('RESULT',k,r,flush=True)
