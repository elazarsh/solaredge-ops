import os,sys,base64,requests,json
H={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"]}
MODEL="gpt-image-2"
def gen(name,prompt,refs,size="1536x1024",quality="high"):
    files=[("image[]",(os.path.basename(r),open(r,"rb"),"image/png")) for r in refs]
    r=requests.post("https://api.openai.com/v1/images/edits",headers=H,data={"model":MODEL,"prompt":prompt,"size":size,"quality":quality,"n":"1"},files=files,timeout=600)
    if r.status_code!=200: print(name,r.status_code,r.text[:400]); return False
    open(name+".png","wb").write(base64.b64decode(r.json()["data"][0]["b64_json"])); print("ok",name); return True
