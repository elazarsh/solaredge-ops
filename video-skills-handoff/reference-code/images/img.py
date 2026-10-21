import os,sys,json,base64,urllib.request,concurrent.futures as cf
KEY=os.environ["GEMINI_API_KEY"]
STYLE=("Shadow-puppet paper-cut animation still frame, in the visual language of Lotte Reiniger silhouette films and the 'Tale of the Three Brothers' animated sequence. "
"Warm sepia monochrome palette with subtle tonal variation, elegant high-contrast black ink silhouettes with intricately cut ornamental detail, "
"background made of layered translucent backlit paper sheets with visible paper fibers and grain, a soft warm glowing backlight behind the paper, "
"aged grainy paper texture over the entire frame, delicate haunting fairy-tale mood, cinematic composition with depth between paper layers. "
"Characters are pure silhouettes with no faces. Absolutely no text, no letters, no words anywhere. 16:9 widescreen.")
SHOTS={
"k1":"A mother silhouette at the center holds up a newborn baby wrapped in a cloth toward the glowing dawn sun. Around her a gentle ring of villager silhouettes, men, women and elders with graceful upright bodies, all reach their open palms upward and forward toward the infant with tender, hopeful, reverent gestures, and their long shadows stretch across the ground toward the baby. Ancient Near-Eastern flat-roofed village rooftops with ornamental cut-out windows and palm trees behind. Calm, tender, solemn mood, nothing menacing.",
"k2":"A very small child silhouette stands alone in the lower center, and on his tiny shoulders balances an impossibly tall, precarious stack of clay jars, stones and bricks that rises up toward the top of the frame. Enormous looming silhouettes of village figures stand far behind him, their long shadows falling over him. Warm amber backlight, vast empty paper sky.",
"k3":"A wide view of an ancient village on a hill at early morning: flat-roofed stone houses, palm trees, thin smoke rising from chimneys (bread baking), silhouettes of neighbors greeting each other, a woman carrying a jar on her head, children running. In the far right background the huge wooden skeleton of an ark under construction rises behind the houses. Soft golden sun glowing through paper layers.",
"k3b":"A medium shot inside the village lane at dawn: a woman silhouette carrying a clay jar, two children silhouettes running past, a man silhouette greeting a neighbor over a low wall, a baker's oven with rising smoke, ornate cut-paper details on the doorways and arches. Warm glowing backlight, layered paper depth.",
"k4":"Noah, an elderly bearded man in a long robe seen as a pure silhouette, hammering wooden planks on the gigantic hull of an ark under construction at dusk; the ribs of the hull and scaffolding are visible, sparks flying from the hammer. In the far distance a long line of village silhouettes watches him. Amber backlight turning darker, ornate paper-cut details.",
"k4b":"A wide shot of the gigantic wooden ark under construction on a hill at dusk, its ribs and scaffolding rising; a small silhouette of the old bearded man works high on the scaffold hammering. At the left a small crowd of ancient Near-Eastern villager silhouettes wearing long robes, head cloths and sashes (no wigs, no European clothing) stands pointing and laughing, hands on bellies, leaning on each other, mocking him. Long shadows, amber backlight, ornate paper-cut detail.",
"k5":"Extreme close-up of an old weathered hand silhouette holding a stick of charcoal pressed against a rough wooden plank, the plank fills the lower half of the frame with visible wood grain and nail holes, warm sepia backlight, paper-cut aesthetic. The plank surface is completely blank with no marks.",
"k6":"A wide dusk landscape: a massive, dark, heavy bank of storm clouds rising along the whole horizon behind a distant hill, rendered as dense black layered paper clouds against the sepia sky, with a cold grey-blue glow bleeding in from the horizon. In the foreground, small silhouettes of the village rooftops and palm trees, and a single tiny figure standing at the edge of the hill looking toward the clouds. Ominous quiet.",
}
def gen(k):
    body={"contents":[{"parts":[{"text":STYLE+"\n\nScene: "+SHOTS[k]}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"16:9","imageSize":"2K"}}}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    try: d=json.load(urllib.request.urlopen(req,timeout=400))
    except Exception as e: return k,'ERR '+str(e)[:200]
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            open(f'img/{k}.png','wb').write(base64.b64decode(p["inlineData"]["data"]));return k,'ok'
    return k,'noimg '+str(d)[:300]
ks=sys.argv[1:] or list(SHOTS)
with cf.ThreadPoolExecutor(4) as ex:
    for r in ex.map(gen,ks): print(r,flush=True)
