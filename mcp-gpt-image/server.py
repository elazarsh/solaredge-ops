#!/usr/bin/env python3
"""MCP server: generate/edit images with OpenAI's GPT image models.

Backends
  api    OpenAI Images API (official; needs OPENAI_API_KEY).
  codex  `codex exec` using the Codex CLI's ChatGPT login (~/.codex/auth.json).
         EXPERIMENTAL: relies on Codex's image-generation tool, which is not
         officially documented; may break without notice.
  auto   (default) api if OPENAI_API_KEY is set, otherwise codex.
"""
import base64
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Image

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
OUT_DIR = Path(os.environ.get("GPT_IMAGE_OUTPUT_DIR", "generated-images")).expanduser()
TIMEOUT = int(os.environ.get("GPT_IMAGE_TIMEOUT", "300"))
CODEX_BIN = os.environ.get("CODEX_BIN", "codex")
MAX_INLINE_BYTES = 4 * 1024 * 1024  # larger images are saved but not returned inline

mcp = FastMCP("gpt-image")


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


def _post(path: str, body: bytes, content_type: str) -> dict:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    req = urllib.request.Request(
        BASE_URL + path, data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": content_type},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"OpenAI API error {e.code}: {detail}") from None


def _multipart(fields: dict, files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, path in files:
        ctype = "image/png" if path.suffix.lower() == ".png" else "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/webp"
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{path.name}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n".encode() + path.read_bytes() + b"\r\n"
        )
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
    instruction = (
        "Use your image generation tool to create one image for the prompt below, "
        f"then save the final PNG to exactly this absolute path: {out}\n"
        f"Size/aspect: {size}\nDo nothing else.\n\nPrompt: {prompt}"
    )
    cmd = [exe, "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", "-C", str(out.parent), instruction]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, stdin=subprocess.DEVNULL)
    if out.exists():
        return
    # Fallback: Codex may have stored the image under ~/.codex instead.
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    recent = [p for p in codex_home.rglob("*") if p.suffix.lower() in (".png", ".jpg", ".webp") and p.stat().st_mtime >= started]
    if recent:
        shutil.copyfile(max(recent, key=lambda p: p.stat().st_mtime), out)
        return
    tail = (proc.stdout + proc.stderr)[-500:]
    raise RuntimeError(f"codex did not produce an image (exit {proc.returncode}): {tail}")


def _result(out: Path, backend: str):
    size = out.stat().st_size
    info = f"Saved {out} ({size // 1024} KiB) via {backend}"
    return [info, Image(path=str(out))] if size <= MAX_INLINE_BYTES else info


@mcp.tool()
def generate_image(prompt: str, size: str = "auto", quality: str = "auto",
                   output_path: str = "", backend: str = "auto"):
    """Generate an image from a text prompt with OpenAI's GPT image model.

    Args:
      prompt: Detailed description of the image.
      size: "auto", "1024x1024", "1536x1024" (landscape) or "1024x1536" (portrait).
      quality: "auto", "low", "medium" or "high".
      output_path: Where to save the PNG. Defaults to generated-images/ in the server's cwd.
      backend: "auto" (API key if set, else Codex login), "api" or "codex" (experimental).
    Returns the saved file path and the image itself.
    """
    b = _pick_backend(backend)
    out = _out_path(output_path or None)
    if b == "api":
        body = json.dumps({"model": MODEL, "prompt": prompt, "size": size, "quality": quality, "n": 1}).encode()
        _save_b64(_post("/images/generations", body, "application/json"), out)
    else:
        _codex_generate(prompt, size, out)
    return _result(out, b)


@mcp.tool()
def edit_image(prompt: str, image_paths: list[str], mask_path: str = "",
               size: str = "auto", quality: str = "auto", output_path: str = ""):
    """Edit or combine existing images using a text instruction (API backend only).

    Args:
      prompt: What to change or create using the input image(s).
      image_paths: One or more local PNG/JPEG/WEBP files.
      mask_path: Optional PNG mask; transparent areas are the parts to edit.
      size, quality, output_path: as in generate_image.
    """
    imgs = [Path(p).expanduser() for p in image_paths]
    for p in imgs + ([Path(mask_path).expanduser()] if mask_path else []):
        if not p.is_file():
            raise FileNotFoundError(str(p))
    files = [("image[]", p) for p in imgs]
    if mask_path:
        files.append(("mask", Path(mask_path).expanduser()))
    body, ctype = _multipart({"model": MODEL, "prompt": prompt, "size": size, "quality": quality}, files)
    out = _out_path(output_path or None)
    _save_b64(_post("/images/edits", body, ctype), out)
    return _result(out, "api")


if __name__ == "__main__":
    mcp.run()
