import os,sys,json,base64,wave,urllib.request,ssl
KEY=os.environ["GEMINI_API_KEY"]  # set in your environment, never commit it
ctx=ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
def tts(text,voice,style,model,out):
    prompt=f"{style}\n\n{text}"
    body={"contents":[{"parts":[{"text":prompt}]}],
          "generationConfig":{"responseModalities":["AUDIO"],
           "speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}",
        data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=120,context=ctx) as r: d=json.load(r)
    part=d["candidates"][0]["content"]["parts"][0]["inlineData"]
    pcm=base64.b64decode(part["data"]); mime=part.get("mimeType","")
    if "wav" in mime and pcm[:4]==b"RIFF":
        open(out,"wb").write(pcm)
        with wave.open(out) as w: return w.getnframes()/w.getframerate(),mime
    with wave.open(out,"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
    return len(pcm)/2/24000,mime
if __name__=="__main__":
    t="תִּכָּנְסוּ. שִׂימוּ לֵב לָאוֹר, שִׂימוּ לֵב לַשֶּׁטַח, שִׂימוּ לֵב לַקִּירוֹת: מְמוּחְזָרִים. אֶקוֹלוֹגִיִּים. בְּלִי רְטִיבוּת. חוּץ מִגֶּשֶׁם."
    st="Speak Hebrew. You are a slick, shady lawyer-pigeon selling a dubious apartment. Warm, smooth, oily baritone, overconfident, a smile in the voice, fast rolling delivery like a salesman, slight pause before the last joke. Read the following text:"
    for model,voice in (("gemini-2.5-flash-preview-tts","Algieba"),("gemini-3.8-flash-tts","Algieba")):
        try:
            print(model,voice,tts(t,voice,st,model,f"audio/test_{model}_{voice}.wav"))
        except Exception as e:
            print(model,"ERR",str(e)[:300])
