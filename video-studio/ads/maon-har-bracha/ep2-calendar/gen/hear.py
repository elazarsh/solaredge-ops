# Transcribe an audio file with Gemini (for checking TTS takes).  usage: hear.py file.wav
import os, sys, json, base64, urllib.request
KEY = os.environ["GEMINI_API_KEY"]
d = base64.b64encode(open(sys.argv[1], "rb").read()).decode()
body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/wav", "data": d}}, {"text": "Transcribe exactly in Hebrew with timestamps per phrase. Describe the voice briefly."}]}]}
r = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent", json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
print(json.load(urllib.request.urlopen(r, timeout=200))["candidates"][0]["content"]["parts"][-1]["text"])
