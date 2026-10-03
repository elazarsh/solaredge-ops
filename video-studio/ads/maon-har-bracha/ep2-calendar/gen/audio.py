# Music (Lyria) and the VO line (Gemini TTS, voice Leda) for ep2.  usage: audio.py music|vo
import os, sys, json, base64, urllib.request, subprocess
KEY = os.environ["GEMINI_API_KEY"]; B = "https://generativelanguage.googleapis.com/v1beta/models/"
def call(model, body):
    r = urllib.request.Request(B + model + ":generateContent", json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
    return json.load(urllib.request.urlopen(r, timeout=600))
if sys.argv[1] == "music":
    P = ("Instrumental, no vocals, 84 BPM, key of G major, 64 seconds long. Warm, tender, hopeful early-morning mood for a heartfelt "
         "commercial about the people who raise our children: soft felt piano melody with fingerpicked nylon acoustic guitar, light "
         "brushed percussion and a gentle music-box sparkle. Quiet and intimate for the first 34 seconds with a steady calm groove, then "
         "a soft emotional lift with warm strings from 34 to 52 seconds, then it settles and ends cleanly on a soft G major chord at about 62 seconds. "
         "No drops, no sudden hits, no drones.")
    for i in (1, 2):
        d = call("lyria-3-pro-preview", {"contents": [{"parts": [{"text": P}]}]})
        for p in d["candidates"][0]["content"]["parts"]:
            if "inlineData" in p: open(f"assets/bgm/take{i}.mp3", "wb").write(base64.b64decode(p["inlineData"]["data"])); print("take", i)
else:
    lines = {"vo-end-1": "הַכִּנּוּי לֹא הִתְעַדְכֵּן. הַתַּפְקִיד כֵּן."}
    style = "Say warmly and confidently, smiling: "
    for k, txt in lines.items():
        for take in (1, 2):
            d = call("gemini-3.8-flash-tts", {"contents": [{"parts": [{"text": style + txt}]}],
                  "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Leda"}}}}})
            p = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            pcm = base64.b64decode(p["data"]); rate = int(p["mimeType"].split("rate=")[1].split(";")[0]) if "rate=" in p["mimeType"] else 24000
            out = f"assets/voice/{k}-t{take}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "-", "-af",
                            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                            "-ar", "48000", out], input=pcm, check=True); print(out)
