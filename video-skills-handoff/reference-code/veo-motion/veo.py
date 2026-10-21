import os,sys,json,base64,urllib.request,time,concurrent.futures as cf
from PIL import Image
KEY=os.environ["GEMINI_API_KEY"];B="https://generativelanguage.googleapis.com/v1beta/"
COMMON=" Shadow-puppet paper-cut animation, stop-motion hand-crafted feel with slight natural jitter, layered translucent paper with parallax depth, warm sepia backlight softly pulsing. One continuous take, no cuts, no text, no faces, silhouettes only. No speech, no singing, no music."
P={
"k1":"Very slow gentle camera push-in toward the mother and baby. The villagers' open hands slowly rise and reach toward the baby, their long shadows stretching across the ground; the paper layers drift with subtle parallax and the sun glow breathes. Sound: soft dawn ambience, distant birds, quiet room tone.",
"k2":"Slow camera push toward the small child. The tall stack of jars and bricks on his shoulders sways precariously, his small body trembles slightly under the weight, the looming villager silhouettes behind shift slowly. Sound: low creaking of clay jars, soft wind.",
"k3":"Slow lateral camera dolly to the right across the village with strong parallax between paper layers. Smoke wisps rise from the chimneys, children run across the hill, the woman walks with her jar, and in the far background a tiny figure hammers on the ark skeleton. Sound: morning village ambience, birds, faint distant hammering, far-away children's laughter without words.",
"k3b":"Slow gentle camera drift. The woman walks across with her jar, the two children run past, the man waves to his neighbor, smoke curls up from the oven. Subtle parallax between paper layers. Sound: morning village, footsteps on dust, murmur without words, soft baking crackle.",
"k4":"The old man's silhouette rhythmically swings the hammer, striking a plank about once a second; golden sparks fly with each strike. The camera slowly pushes in; the long line of watchers in the distance sways slightly; the backlight flickers like candlelight. Sound: rhythmic hammer blows on wood, wind slowly rising.",
"k4b":"The tiny old man keeps hammering without turning; the crowd of villagers at the left rock with laughter, shoulders shaking and arms pointing; the camera slowly pushes in across the hill with parallax; the backlight flickers like candlelight. Sound: distant mocking laughter without words, rhythmic hammering, wind.",
"k5":"The hand slowly drags the charcoal along the plank leaving a dark smudged charcoal line, camera slowly pushes in, dust motes drift in the backlight. Only abstract scratches, no letters. Sound: dry scratch of charcoal on wood, quiet room.",
"k6":"The black storm clouds slowly boil and creep higher over the hill while cold grey-blue light spreads across the sky; the tiny figure stands completely still; slow camera push forward; heavy stillness. Sound: low distant rumble, wind.",
}
def call(url,data=None):
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    return json.load(urllib.request.urlopen(r,timeout=300))
def run(k,model="veo-3.1-generate-preview"):
    im=Image.open(f'img/{k}.png').convert('RGB');im.thumbnail((1920,1080));im.save(f'img/{k}_in.jpg',quality=93)
    inst={"prompt":P[k]+COMMON,"image":{"bytesBase64Encoded":base64.b64encode(open(f'img/{k}_in.jpg','rb').read()).decode(),"mimeType":"image/jpeg"}}
    body={"instances":[inst],"parameters":{"aspectRatio":"16:9","durationSeconds":8,"resolution":"1080p","personGeneration":"allow_adult"}}
    for i in range(6):
        try: op=call(B+f"models/{model}:predictLongRunning",body);break
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:200]
            if e.code==429 and i<5: print(k,'429',msg,flush=True);time.sleep(45*(i+1));continue
            return k,f'HTTP {e.code} {msg}'
    name=op["name"]
    while not op.get("done"):
        time.sleep(10);op=call(B+name)
    if "error" in op: return k,'ERR '+json.dumps(op["error"])[:300]
    s=op["response"]["generateVideoResponse"]
    if "generatedSamples" not in s: return k,'NOSAMPLE '+json.dumps(s)[:300]
    uri=s["generatedSamples"][0]["video"]["uri"]
    r=urllib.request.Request(uri,headers={"x-goog-api-key":KEY});open(f'veo/{k}.mp4','wb').write(urllib.request.urlopen(r,timeout=300).read())
    return k,'ok'
if __name__=='__main__':
    ks=sys.argv[1:] or list(P)
    with cf.ThreadPoolExecutor(3) as ex:
        for r in ex.map(run,ks): print(r,flush=True)
