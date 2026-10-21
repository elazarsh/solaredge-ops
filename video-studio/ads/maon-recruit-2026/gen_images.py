import os, sys, json, base64, urllib.request, concurrent.futures as cf
KEY=os.environ["GEMINI_API_KEY"]; OUT=os.path.join(os.path.dirname(__file__),"hf/assets/gen/raw")
MODEL=os.environ.get("IMG_MODEL","gemini-3-pro-image")
ISO=("Overhead flat-lay product photograph, camera pointing straight down at 90 degrees, "
     "soft diffuse daylight, photorealistic, high detail, the object is fully visible and centered with generous margin, "
     "isolated on a pure seamless white background, no text, no logos, no hands, no people. Subject: ")
JOBS={
 "table": ("9:16","Seamless texture photograph: a light natural oak wooden table top shot straight down, the wood surface fills 100 percent of the frame edge to edge with no table edges, no floor, no window, no borders, "
           "subtle realistic wood grain running vertically, soft even natural window light, calm and clean, no objects, no text, photorealistic."),
 "bag": ("1:1",ISO+"a large dark navy leather work tote bag lying on its side, visibly overstuffed and bulging, the corner of a paper folder and a cable peeking out of its open top edge which faces the bottom of the frame, handles resting on top."),
 "bag_light": ("1:1",ISO+"a large dark navy leather work tote bag lying flat on its side, almost empty and slack, soft and relaxed shape, top opening facing the bottom of the frame, handles resting on top, nothing sticking out."),
 "laptop": ("1:1",ISO+"a closed thin silver laptop, plain lid, no brand logo."),
 "chargers": ("1:1",ISO+"two white phone and laptop chargers with long white cables hopelessly tangled together with a pair of black wireless over-ear headphones."),
 "sticky": ("1:1",ISO+"a single blank square bright yellow sticky note, slightly curled corner, nothing written on it."),
 "sandwich": ("1:1",ISO+"half of a sad cheese sandwich on crumpled wax paper, with one bite taken out, slightly dry, from yesterday."),
 "drawing": ("3:4",ISO+"a toddler's joyful crayon drawing on a sheet of white paper with fold creases: messy colorful scribbles, a big yellow sun, a flower, and a smiling stick figure woman with long hair and very big arms, lots of pink and orange, the top quarter of the paper is left empty."),
 "sock": ("1:1",ISO+"one tiny toddler sock, mint green with small cartoon dinosaur pattern, slightly crumpled."),
 "keys": ("1:1",ISO+"a small bunch of three house keys on a ring with a little felt heart keychain."),
}
def gen(name):
    ar,prompt=JOBS[name]
    body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":ar,"imageSize":"2K"}}}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=300))
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            ext="png" if "png" in p["inlineData"]["mimeType"] else "jpg"
            fn=f"{OUT}/{name}.{ext}"; open(fn,"wb").write(base64.b64decode(p["inlineData"]["data"])); return fn
    return f"{name}: no image {json.dumps(d)[:300]}"
names=sys.argv[1:] or list(JOBS)
with cf.ThreadPoolExecutor(5) as ex:
    for r in ex.map(lambda n: (lambda: gen(n))() if True else None, names): print(r)
