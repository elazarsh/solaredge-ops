import sys,cv2,numpy as np,glob,os
sys.argv=[sys.argv[0]]+sys.argv[1:]
from engine import *
ts=[float(x) for x in sys.argv[1:]]
tiles=[]
for tt in ts:
    fr=frame_at(int(round(tt*FPS))); small=cv2.resize(fr,(640,360),interpolation=cv2.INTER_AREA)
    cv2.putText(small,f"{tt:.1f}",(8,24),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2); tiles.append(small)
while len(tiles)%3: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)]
cv2.imwrite(f"{SCR}/contact.jpg",np.vstack(rows))
