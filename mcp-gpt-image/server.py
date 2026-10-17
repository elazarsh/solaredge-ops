#!/usr/bin/env python3
"""MCP server: frugal image generation with OpenAI GPT image models, plus local
tooling that turns one generated "parts sheet" into a rigged, animatable asset.

Cost safety (the API is paid):
  * generate_image / edit_image are DRY-RUN by default: they show the exact prompt,
    model, size, quality and estimated price, and send nothing until confirm=true.
  * Identical requests are served from the local ledger at no charge.
  * A daily budget (GPT_IMAGE_DAILY_BUDGET_USD, default 2.00) is enforced.
  * Everything under "Local tools" below is free (no API call).

Backends: api (OpenAI Images API, needs OPENAI_API_KEY), codex (experimental,
`codex exec` with a ChatGPT login), auto (api if a key is set, else codex).
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Image

import parts as P

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
OUT_DIR = Path(os.environ.get("GPT_IMAGE_OUTPUT_DIR", "generated-images")).expanduser()
TIMEOUT = int(os.environ.get("GPT_IMAGE_TIMEOUT", "300"))
CODEX_BIN = os.environ.get("CODEX_BIN", "codex")
BUDGET = float(os.environ.get("GPT_IMAGE_DAILY_BUDGET_USD", "2.00"))
MAX_INLINE_BYTES = 4 * 1024 * 1024

# USD per image, gpt-image-1 list prices (developers.openai.com). Verify if you change OPENAI_IMAGE_MODEL.
PRICES = {
    ("low", "1024x1024"): 0.011, ("low", "1024x1536"): 0.016, ("low", "1536x1024"): 0.016,
    ("medium", "1024x1024"): 0.042, ("medium", "1024x1536"): 0.063, ("medium", "1536x1024"): 0.063,
    ("high", "1024x1024"): 0.167, ("high", "1024x1536"): 0.25, ("high", "1536x1024"): 0.25,
}

mcp = FastMCP("gpt-image")


# ---------------------------------------------------------------- cost guard
def _estimate(quality: str, size: str) -> float:
    if quality == "auto" or size == "auto":
        return 0.25  # unknown: assume worst case, so prefer explicit values
    return PRICES.get((quality, size), 0.25)


def _ledger_path() -> Path:
    return OUT_DIR / "ledger.jsonl"


def _rows() -> list[dict]:
    p = _ledger_path()
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _spent_today() -> float:
    today = date.today().isoformat()
    return sum(r.get("est_usd", 0) for r in _rows() if r["ts"].startswith(today))


def _record(row: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with _ledger_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _key(params: dict) -> str:
    return hashlib.sha1(json.dumps(params, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _pick_backend(backend: str) -> str:
    if backend in ("api", "codex"):
        return backend
    if backend != "auto":
        raise ValueError("backend must be one of: auto, api, codex")
    return "api" if os.environ.get("OPENAI_API_KEY") else "codex"


def _out_path(output_path: str | None) -> Path:
    p = Path(output_path).expanduser() if output_path else OUT_DIR / f"img-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def _gate(kind: str, params: dict, est: float, backend: str, confirm: bool, output_path: str | None):
    """Returns (early_result, key). early_result is set for cache hits and dry runs."""
    key = _key(params)
    for r in reversed(_rows()):
        if r["key"] == key and Path(r["path"]).exists():
            if output_path:
                dst = _out_path(output_path)
                if dst != Path(r["path"]).resolve():
                    shutil.copyfile(r["path"], dst)
                return _result(dst, f"{backend} (cached, no charge)"), key
            return _result(Path(r["path"]), f"{backend} (cached, no charge)"), key
    spent = _spent_today()
    if not confirm:
        note = "" if MODEL == "gpt-image-1" else f" (price table is for gpt-image-1; {MODEL} may differ)"
        return (f"DRY RUN - nothing was sent and nothing was charged.\n"
                f"{kind}: backend={backend} model={MODEL} size={params.get('size')} quality={params.get('quality')} "
                f"background={params.get('background')}\n"
                f"Estimated cost: ${est:.3f}{note}. Spent today: ${spent:.3f} of ${BUDGET:.2f}.\n"
                f"Prompt:\n{params['prompt']}\n\n"
                f"If this is exactly what the user approved, call again with confirm=true."), key
    if backend == "api" and spent + est > BUDGET:
        raise RuntimeError(f"Daily budget ${BUDGET:.2f} would be exceeded (spent ${spent:.3f} + ${est:.3f}). "
                           "Raise GPT_IMAGE_DAILY_BUDGET_USD only if the user asks.")
    return None, key


# ---------------------------------------------------------------- HTTP helpers
def _post(path: str, body: bytes, content_type: str) -> dict:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    req = urllib.request.Request(BASE_URL + path, data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI API error {e.code}: {e.read().decode('utf-8', 'replace')[:500]}") from None


def _multipart(fields: dict, files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in fields.items()]
    for k, path in files:
        sfx = path.suffix.lower()
        ctype = "image/png" if sfx == ".png" else "image/jpeg" if sfx in (".jpg", ".jpeg") else "image/webp"
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{path.name}"\r\n'
                     f"Content-Type: {ctype}\r\n\r\n".encode() + path.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _save_b64(resp: dict, out: Path) -> None:
    data = resp.get("data") or []
    if not data or not data[0].get("b64_json"):
        raise RuntimeError(f"No image in response: {str(resp)[:300]}")
    out.write_bytes(base64.b64decode(data[0]["b64_json"]))


def _codex_generate(prompt: str, size: str, out: Path) -> None:
    exe = shutil.which(CODEX_BIN)
    if not exe:
        raise RuntimeError("codex CLI not found (npm i -g @openai/codex, then `codex login`)")
    started = time.time()
    instruction = ("Use your image generation tool to create one image for the prompt below, "
                   f"then save the final PNG to exactly this absolute path: {out}\n"
                   f"Size/aspect: {size}\nDo nothing else.\n\nPrompt: {prompt}")
    cmd = [exe, "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", "-C", str(out.parent), instruction]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, stdin=subprocess.DEVNULL)
    if out.exists():
        return
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    recent = [p for p in codex_home.rglob("*") if p.suffix.lower() in (".png", ".jpg", ".webp") and p.stat().st_mtime >= started]
    if recent:
        shutil.copyfile(max(recent, key=lambda p: p.stat().st_mtime), out)
        return
    raise RuntimeError(f"codex did not produce an image (exit {proc.returncode}): {(proc.stdout + proc.stderr)[-500:]}")


def _result(out: Path, backend: str):
    size = out.stat().st_size
    info = f"Saved {out} ({size // 1024} KiB) via {backend}"
    return [info, Image(path=str(out))] if size <= MAX_INLINE_BYTES else info


# ---------------------------------------------------------------- paid tools
@mcp.tool()
def generate_image(prompt: str, size: str = "1024x1024", quality: str = "medium", background: str = "auto",
                   output_path: str = "", backend: str = "auto", confirm: bool = False):
    """Generate an image with OpenAI's GPT image model. PAID - dry-run unless confirm=true.

    Only set confirm=true after the user has approved the exact prompt, size and quality.
    Use quality "low" for drafts/tests; "high" only for final art.

    Args:
      prompt: Full image description.
      size: "1024x1024", "1536x1024" (landscape) or "1024x1536" (portrait).
      quality: "low" (~$0.01), "medium" (~$0.04-0.06), "high" (~$0.17-0.25).
      background: "auto", "transparent" (PNG with alpha) or "opaque".
      output_path: Where to save the PNG (default: generated-images/).
      backend: "auto", "api" or "codex" (experimental).
      confirm: false = show cost and prompt only; true = actually send and charge.
    """
    b = _pick_backend(backend)
    params = {"model": MODEL, "backend": b, "prompt": prompt, "size": size, "quality": quality, "background": background}
    est = 0.0 if b == "codex" else _estimate(quality, size)
    early, key = _gate("generate_image", params, est, b, confirm, output_path or None)
    if early is not None:
        return early
    out = _out_path(output_path or None)
    if b == "api":
        body = {"model": MODEL, "prompt": prompt, "size": size, "quality": quality, "n": 1}
        if background != "auto":
            body.update(background=background, output_format="png")
        _save_b64(_post("/images/generations", json.dumps(body).encode(), "application/json"), out)
    else:
        _codex_generate(prompt, size, out)
    _record({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "key": key, "est_usd": est, "backend": b, "model": MODEL,
             "path": str(out), "prompt": prompt, "size": size, "quality": quality})
    return _result(out, b)


@mcp.tool()
def edit_image(prompt: str, image_paths: list[str], mask_path: str = "", size: str = "1024x1024",
               quality: str = "medium", output_path: str = "", confirm: bool = False):
    """Edit/combine existing images with a text instruction (API backend only). PAID - dry-run unless confirm=true.

    Args:
      prompt: What to change or create using the input image(s).
      image_paths: One or more local PNG/JPEG/WEBP files.
      mask_path: Optional PNG mask; transparent areas are the parts to edit.
      size, quality, output_path, confirm: as in generate_image.
    """
    imgs = [Path(p).expanduser() for p in image_paths]
    for p in imgs + ([Path(mask_path).expanduser()] if mask_path else []):
        if not p.is_file():
            raise FileNotFoundError(str(p))
    digest = hashlib.sha1(b"".join(p.read_bytes() for p in imgs)).hexdigest()
    params = {"model": MODEL, "backend": "api", "prompt": prompt, "size": size, "quality": quality,
              "background": "auto", "inputs": digest, "mask": mask_path}
    est = _estimate(quality, size) + 0.01  # + input image tokens (approx.)
    early, key = _gate("edit_image", params, est, "api", confirm, output_path or None)
    if early is not None:
        return early
    files = [("image[]", p) for p in imgs] + ([("mask", Path(mask_path).expanduser())] if mask_path else [])
    body, ctype = _multipart({"model": MODEL, "prompt": prompt, "size": size, "quality": quality}, files)
    out = _out_path(output_path or None)
    _save_b64(_post("/images/edits", body, ctype), out)
    _record({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "key": key, "est_usd": est, "backend": "api", "model": MODEL,
             "path": str(out), "prompt": prompt, "size": size, "quality": quality})
    return _result(out, "api")


# ---------------------------------------------------------------- free tools
@mcp.tool()
def image_usage() -> str:
    """Show today's estimated spend, the daily budget and the most recent generations. Free."""
    rows = _rows()
    last = "\n".join(f"  {r['ts']}  ${r['est_usd']:.3f}  {r['quality']} {r['size']}  {r['path']}" for r in rows[-5:])
    return f"Spent today: ${_spent_today():.3f} of ${BUDGET:.2f}. Total generations on record: {len(rows)}.\n{last}"


@mcp.tool()
def plan_parts_sheet(subject: str, style: str, parts: list[dict], pose: str = "neutral standing pose, facing front",
                     notes: str = "", size: str = "1536x1024", quality: str = "medium") -> str:
    """Build the prompt for ONE image containing every animatable part of a character/object, separated. FREE (no API call).

    One generation returns the whole puppet sheet, which split_parts then cuts into layers, so a
    full character costs a single image instead of one per limb.

    Args:
      subject: e.g. "a friendly middle-aged chef".
      style: e.g. "flat vector illustration, bold outlines, warm palette".
      parts: [{"name": "head", "description": "..."}, ...]. For a person typically: head, torso, pelvis,
             upper/lower arm and hand (left & right), upper/lower leg and foot (left & right), optionally
             mouth/eye variants. Name only what the planned animation needs.
      pose: Rest pose; keep limbs slightly away from the torso.
      notes: Extra requirements (accessories, colours).
    Returns the prompt, estimated cost and the next step. Show it to the user before calling generate_image.
    """
    if not parts:
        raise ValueError("parts must not be empty")
    listing = "\n".join(f"- {p['name']}" + (f": {p['description']}" if p.get("description") else "") for p in parts)
    prompt = (
        f"2D cut-out puppet sheet for skeletal animation. Subject: {subject}. Style: {style}.\n"
        f"Draw every part below as its own SEPARATE, complete piece, arranged on one sheet in the {pose}, "
        "each piece in its natural orientation and relative scale, with clear empty space (at least 5% of the image width) "
        "between every piece so that no two pieces touch or overlap.\n"
        "Each piece must be fully drawn and unobstructed, including the hidden part at its joints (for example the top of an arm "
        "continues under the shoulder, the neck continues under the head), with rounded joint ends, so a piece can rotate without "
        "showing a gap. Same line weight, shading, lighting and colour palette on all pieces.\n"
        f"Pieces (exactly one of each):\n{listing}\n"
        + (f"Notes: {notes}\n" if notes else "")
        + "No text, labels, arrows, shadows, ground or scenery. Plain transparent background."
    )
    spec = {"subject": subject, "style": style, "parts": parts, "pose": pose, "notes": notes, "size": size,
            "quality": quality, "prompt": prompt}
    slug = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")[:40] or "sheet"
    specp = OUT_DIR / "specs" / f"{slug}.json"
    specp.parent.mkdir(parents=True, exist_ok=True)
    specp.write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    return (f"Spec saved: {specp}\nEstimated cost of the single generation: ${_estimate(quality, size):.3f} "
            f"({quality}, {size}).\n\nPROMPT:\n{prompt}\n\n"
            "Next: confirm the part list and prompt with the user -> generate_image(prompt, size, quality, "
            "background='transparent', confirm=true) -> split_parts -> save_rig -> render_rig to check.")


@mcp.tool()
def split_parts(sheet_path: str, out_dir: str = "", min_area_frac: float = 0.002, merge_gap: int = 4):
    """Cut a parts sheet into one transparent PNG per piece. FREE (local, no API call).

    Writes p01.png..., manifest.json (sizes, positions, pivot hints) and labeled.png (numbered boxes).
    Look at the returned labeled.png, then name each id and describe the hierarchy in save_rig.
    If pieces were merged, regenerate nothing: lower merge_gap; if a piece was split, raise it.

    Args:
      sheet_path: PNG from generate_image.
      out_dir: Output folder (default: next to the sheet, named <sheet>_parts).
      min_area_frac: Pieces smaller than this fraction of the largest piece are discarded as specks.
      merge_gap: Pixels; fragments closer than this are kept together (eyes, fingers, etc.).
    """
    sp = Path(sheet_path).expanduser()
    out = Path(out_dir).expanduser() if out_dir else sp.with_name(sp.stem + "_parts")
    m = P.split_parts(sp, out, min_area_frac, merge_gap)
    summary = ", ".join(f"{p['id']}={p['size'][0]}x{p['size'][1]}" for p in m["parts"])
    msg = (f"{len(m['parts'])} parts in {out} ({summary}); discarded specks: {m['discarded_specks']}; "
           f"background keyed locally: {m['background_keyed_locally']}.")
    return [msg, Image(path=str(out / "labeled.png"))]


@mcp.tool()
def save_rig(parts_dir: str, parts: list[dict], canvas: list[int]) -> str:
    """Describe the skeleton of a split sheet and write rig.json. FREE.

    Args:
      parts_dir: Folder created by split_parts.
      parts: One entry per used piece:
        {"id": "p03", "name": "head", "parent": "neck" or null, "pivot": [x, y], "anchor": [x, y], "z": 5}
        pivot  = rotation point in the piece's own pixels (see pivot_hints in manifest.json).
        anchor = where that pivot sits, in the PARENT piece's pixels (root: position on the canvas).
        z      = draw order (higher = in front).
      canvas: [width, height] of the assembled picture.
    """
    path, unused = P.save_rig(parts_dir, parts, canvas)
    return f"Wrote {path}. Unused piece ids: {unused or 'none'}. Verify with render_rig."


@mcp.tool()
def render_rig(rig_path: str, rotations: dict | None = None, output_path: str = "", background: str = "#ffffff"):
    """Render the assembled rig, optionally posed. FREE (local) - use it to check joints before animating.

    Args:
      rig_path: rig.json from save_rig.
      rotations: {"left_forearm": -40, "head": 8} degrees, positive = clockwise; children follow parents.
      output_path: Default: <rig folder>/preview.png.
      background: CSS colour or "transparent".
    """
    rp = Path(rig_path).expanduser()
    out = Path(output_path).expanduser() if output_path else rp.with_name("preview.png")
    P.render_rig(rp, rotations or {}, out, background)
    return [f"Rendered {out}", Image(path=str(out))]


if __name__ == "__main__":
    mcp.run()
