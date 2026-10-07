# usage: veo.py out.mp4 first_frame.jpg "prompt" [model]
import os,sys,json,base64,urllib.request,time
KEY=os.environ["GEMINI_API_KEY"]; out,img,prompt=sys.argv[1:4]; model=sys.argv[4] if len(sys.argv)>4 else "veo-3.1-generate-preview"
B="https://generativelanguage.googleapis.com/v1beta/"
inst={"prompt":prompt,"image":{"bytesBase64Encoded":base64.b64encode(open(img,"rb").read()).decode(),"mimeType":"image/jpeg"}}
body={"instances":[inst],"parameters":{"aspectRatio":"9:16","durationSeconds":8,"resolution":"1080p","personGeneration":"allow_adult"}}
def call(url,data=None):
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    return json.load(urllib.request.urlopen(r,timeout=300))
op=call(B+f"models/{model}:predictLongRunning",body); name=op["name"]
while not op.get("done"):
    time.sleep(10); op=call(B+name)
if "error" in op: print("ERR",op["error"]); sys.exit(1)
s=op["response"]["generateVideoResponse"]
if "generatedSamples" not in s: print("NOSAMPLE",json.dumps(s)[:400]); sys.exit(1)
uri=s["generatedSamples"][0]["video"]["uri"]
r=urllib.request.Request(uri,headers={"x-goog-api-key":KEY})
open(out,"wb").write(urllib.request.urlopen(r,timeout=300).read()); print(out)
