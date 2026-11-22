# Real satellite base for story maps (Sentinel-2 cloudless 2016 by EOX, CC BY 4.0), web-mercator. Usage in map_labels.py.
import math, io, urllib.request, sys
from PIL import Image
Z=9; T=256; N=2**Z*T
def mx(lon): return (lon+180)/360*N
def my(lat):
    r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*N
lon0,lon1=float(sys.argv[1]),float(sys.argv[2])
cx_lat=float(sys.argv[3]); OW,OH=int(sys.argv[4]),int(sys.argv[5]); OUT=sys.argv[6]
x0,x1=mx(lon0),mx(lon1); w=x1-x0; h=w*OH/OW
yc=my(cx_lat); y0,y1=yc-h/2,yc+h/2
tiles={}
mos=Image.new('RGB',(int(x1//T-x0//T+1)*T,int(y1//T-y0//T+1)*T))
for tx in range(int(x0//T),int(x1//T)+1):
    for ty in range(int(y0//T),int(y1//T)+1):
        url=f'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{Z}/{ty}/{tx}.jpg'
        data=urllib.request.urlopen(url,timeout=30).read()
        mos.paste(Image.open(io.BytesIO(data)).convert('RGB'),((tx-int(x0//T))*T,(ty-int(y0//T))*T))
ox,oy=int(x0//T)*T,int(y0//T)*T
crop=mos.crop((int(x0-ox),int(y0-oy),int(x1-ox),int(y1-oy))).resize((OW,OH),Image.LANCZOS)
crop.save(OUT+'.jpg',quality=92)
open(OUT+'_geo.txt','w').write(f'{x0} {y0} {w} {h} {Z}')
print(crop.size)
