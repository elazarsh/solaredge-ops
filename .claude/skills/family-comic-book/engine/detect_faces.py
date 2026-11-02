"""Find faces in the generated art (YuNet), so lettering avoids them and crops keep heads.
    python revisions/book1-v08/detect_faces.py /path/face_detection_yunet_2023mar.onnx
Writes faces.json: {panel_id: [[x, y, w, h], ...]} in percent of the image."""
import json
import sys
from pathlib import Path

import cv2

V = Path(__file__).resolve().parent
model = sys.argv[1]
CFG = json.loads((V / 'book.json').read_text(encoding='utf-8'))
B = (V / CFG.get('book_root', '..')).resolve()
progress = json.loads((B / CFG['progress']).read_text(encoding='utf-8'))
out = {}
for a in progress['assets']:
    img = cv2.imread(str(B / a['file']))
    if img is None:
        continue
    H, W = img.shape[:2]
    found = []
    for scale in (1.0, 0.6):
        im = cv2.resize(img, (int(W * scale), int(H * scale)))
        det = cv2.FaceDetectorYN.create(model, '', (im.shape[1], im.shape[0]), 0.6, 0.3, 5000)
        _, faces = det.detect(im)
        for f in (faces if faces is not None else []):
            (x, y, w, h), score = (float(f[k]) / scale for k in range(4)), float(f[-1])
            small = w / W < 0.08
            if score < (0.62 if small else 0.8):
                continue
            box = [round(x / W * 100, 1), round(y / H * 100, 1), round(w / W * 100, 1), round(h / H * 100, 1)]
            if not any(abs(box[0] - b[0]) < 4 and abs(box[1] - b[1]) < 4 for b in found):
                found.append(box)
    out[a['id']] = found
(V / 'faces.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(len(out), 'images,', sum(len(v) for v in out.values()), 'faces')
