import os,sys,json,base64,urllib.request,re
KEY=os.environ["GEMINI_API_KEY"]
def asr(path):
    b=base64.b64encode(open(path,'rb').read()).decode()
    prompt=("תמלל את ההקלטה בעברית בדיוק כפי שנאמרה, בלי ניקוד. החזר JSON בלבד: רשימה של אובייקטים {\"w\":\"מילה\",\"s\":שניות_התחלה,\"e\":שניות_סיום} לכל מילה, בסדר שנאמרו. "
            "אם נאמרה מילה לא ברורה או שגויה, תמלל כפי ששמעת.")
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"audio/wav","data":b}},{"text":prompt}]}],"generationConfig":{"temperature":0,"responseMimeType":"application/json"}}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=180))
    return json.loads(d['candidates'][0]['content']['parts'][0]['text'])
if __name__=='__main__':
    voice=sys.argv[1]
    allw={}
    for i in (1,2,3):
        w=asr(f'vo/p{i}_{voice}.wav');allw[i]=w
        print(i,' '.join(x['w'] for x in w)); print('   t:',w[0]['s'],'->',w[-1]['e'])
    json.dump(allw,open(f'vo/words_{voice}.json','w'),ensure_ascii=False)
