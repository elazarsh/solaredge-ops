"""Local (free) tooling for layered / rigged 2D assets: split a parts sheet into
separate PNGs, describe a skeleton in rig.json, and render poses for QA.

rig.json conventions
  canvas   [w, h] of the assembled picture
  parts[]  name, file, size [w,h], parent (name|null), z (draw order),
           pivot  [x,y]  rotation point, in the part's own pixels
           anchor [x,y]  where the pivot sits: in the PARENT's pixels, or on the
                         canvas for root parts
  rotation: degrees, positive = clockwise on screen (same as CSS rotate()).
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi


def _load_rgba(path):
    a = np.array(Image.open(path).convert("RGBA"))
    keyed = False
    if a[..., 3].min() >= 250:  # no transparency: key out a flat background (corner colour)
        corners = np.array([a[0, 0, :3], a[0, -1, :3], a[-1, 0, :3], a[-1, -1, :3]], dtype=int)
        bg = np.median(corners, axis=0)
        d = np.abs(a[..., :3].astype(int) - bg).sum(-1)
        a[..., 3] = np.clip((d - 24) * 8, 0, 255).astype(np.uint8)
        keyed = True
    return a, keyed


def split_parts(sheet_path, out_dir, min_area_frac=0.002, merge_gap=4, pad=3):
    """Cut a parts sheet into one PNG per connected piece. Returns the manifest dict."""
    a, keyed = _load_rgba(sheet_path)
    H, W = a.shape[:2]
    mask = a[..., 3] > 24
    grown = ndi.binary_dilation(mask, structure=np.ones((3, 3), bool), iterations=merge_gap) if merge_gap > 0 else mask
    lab, _ = ndi.label(grown)
    lab = lab * mask
    areas = np.bincount(lab.ravel())
    areas[0] = 0
    if areas.max() == 0:
        raise ValueError("no visible pixels found in the sheet")
    thr = areas.max() * min_area_frac
    objs = ndi.find_objects(lab)
    found, discarded = [], 0
    for k in range(1, len(areas)):
        if areas[k] == 0:
            continue
        if areas[k] < thr:
            discarded += 1
            continue
        sl = objs[k - 1]
        ys, xs = np.nonzero(lab[sl] == k)
        found.append((k, int(ys.mean() + sl[0].start), int(xs.mean() + sl[1].start)))
    band = max(1, H // 8)
    found.sort(key=lambda t: (t[1] // band, t[2]))

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, (k, cy, cx) in enumerate(found, 1):
        sl = objs[k - 1]
        y0, y1 = max(0, sl[0].start - pad), min(H, sl[0].stop + pad)
        x0, x1 = max(0, sl[1].start - pad), min(W, sl[1].stop + pad)
        crop = a[y0:y1, x0:x1].copy()
        crop[..., 3] = np.where(lab[y0:y1, x0:x1] == k, crop[..., 3], 0)
        pid = f"p{i:02d}"
        Image.fromarray(crop, "RGBA").save(out / f"{pid}.png")
        w, h = x1 - x0, y1 - y0
        parts.append({
            "id": pid, "file": f"{pid}.png", "size": [w, h], "bbox_in_sheet": [x0, y0, x1, y1],
            "centroid_in_sheet": [cx, cy], "area_px": int(areas[k]),
            "pivot_hints": {"center": [w // 2, h // 2], "top_center": [w // 2, 0], "bottom_center": [w // 2, h],
                            "left_center": [0, h // 2], "right_center": [w, h // 2]},
        })
    manifest = {"sheet": str(sheet_path), "sheet_size": [W, H], "background_keyed_locally": keyed,
                "discarded_specks": discarded, "parts": parts}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    _labeled_preview(a, parts, out / "labeled.png")
    return manifest


def _labeled_preview(a, parts, path):
    base = Image.new("RGBA", (a.shape[1], a.shape[0]), (225, 225, 225, 255))
    base.alpha_composite(Image.fromarray(a, "RGBA"))
    d = ImageDraw.Draw(base)
    try:
        font = ImageFont.load_default(size=max(14, a.shape[0] // 45))
    except TypeError:
        font = ImageFont.load_default()
    for p in parts:
        x0, y0, x1, y1 = p["bbox_in_sheet"]
        d.rectangle([x0, y0, x1, y1], outline=(255, 0, 80, 255), width=2)
        d.text((x0 + 3, y0 + 2), p["id"], fill=(200, 0, 60, 255), font=font)
    base.convert("RGB").save(path)


def save_rig(parts_dir, specs, canvas):
    """Validate a skeleton description and write rig.json next to the part images."""
    d = Path(parts_dir)
    manifest = json.loads((d / "manifest.json").read_text())
    by_id = {p["id"]: p for p in manifest["parts"]}
    names = [s["name"] for s in specs]
    if len(set(names)) != len(names):
        raise ValueError("part names must be unique")
    rig_parts = []
    for s in specs:
        if s["id"] not in by_id:
            raise ValueError(f"unknown part id {s['id']}")
        src = by_id[s["id"]]
        parent = s.get("parent") or None
        if parent and parent not in names:
            raise ValueError(f"{s['name']}: parent '{parent}' is not a part")
        if not s.get("anchor"):
            raise ValueError(f"{s['name']}: anchor is required")
        w, h = src["size"]
        rig_parts.append({"name": s["name"], "id": s["id"], "file": src["file"], "size": [w, h], "parent": parent,
                          "pivot": list(s.get("pivot") or [w // 2, h // 2]), "anchor": list(s["anchor"]),
                          "z": int(s.get("z", 0))})
    pmap = {p["name"]: p for p in rig_parts}
    for p in rig_parts:  # cycle check
        seen, cur = set(), p
        while cur["parent"]:
            if cur["name"] in seen:
                raise ValueError(f"cycle in hierarchy at {cur['name']}")
            seen.add(cur["name"])
            cur = pmap[cur["parent"]]
    rig = {"canvas": list(canvas), "parts": rig_parts}
    (d / "rig.json").write_text(json.dumps(rig, indent=1))
    unused = sorted(set(by_id) - {s["id"] for s in specs})
    return str(d / "rig.json"), unused


def render_rig(rig_path, rotations, out_path, bg="#ffffff"):
    """Render the skeleton, optionally rotating named parts (degrees, clockwise +)."""
    rig = json.loads(Path(rig_path).read_text())
    base = Path(rig_path).parent
    parts = {p["name"]: p for p in rig["parts"]}
    unknown = set(rotations) - set(parts)
    if unknown:
        raise ValueError(f"unknown parts in rotations: {sorted(unknown)}")
    world = {}

    def solve(name):
        if name in world:
            return world[name]
        p, rot = parts[name], float(rotations.get(name, 0))
        if p["parent"] is None:
            res = ((float(p["anchor"][0]), float(p["anchor"][1])), rot)
        else:
            (px, py), pang = solve(p["parent"])
            par = parts[p["parent"]]
            dx, dy = p["anchor"][0] - par["pivot"][0], p["anchor"][1] - par["pivot"][1]
            r = math.radians(pang)
            res = ((px + dx * math.cos(r) - dy * math.sin(r), py + dx * math.sin(r) + dy * math.cos(r)), pang + rot)
        world[name] = res
        return res

    canvas = Image.new("RGBA", tuple(rig["canvas"]), (0, 0, 0, 0) if bg == "transparent" else bg)
    for p in sorted(rig["parts"], key=lambda q: q["z"]):
        (wx, wy), ang = solve(p["name"])
        img = Image.open(base / p["file"]).convert("RGBA")
        px, py = p["pivot"]
        W, H = img.size
        R = int(math.ceil(math.hypot(max(px, W - px), max(py, H - py)))) + 2
        sq = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
        sq.paste(img, (R - int(round(px)), R - int(round(py))))
        sq = sq.rotate(-ang, resample=Image.BICUBIC, center=(R, R))
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(sq, (int(round(wx)) - R, int(round(wy)) - R))
        canvas = Image.alpha_composite(canvas, layer)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path
