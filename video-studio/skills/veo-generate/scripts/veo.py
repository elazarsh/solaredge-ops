#!/usr/bin/env python3
"""Google Veo 3.1 client for the Gemini API (standard library only).

Flow (docs: https://ai.google.dev/gemini-api/docs/veo):
  POST models/<model>:predictLongRunning  -> operation name
  GET  <operation name> until done        -> response.generateVideoResponse.generatedSamples[0].video.uri
  GET  <uri> with the key header          -> mp4   (videos are deleted by Google after 2 days)

Auth: environment variable GEMINI_API_KEY (never printed). Veo is NOT on the free tier: every second is billed.
Audio is always generated natively and included in the price.

    veo.py models
    veo.py estimate --model fast --resolution 720p --duration 4
    veo.py text  --prompt "..." --aspect 9:16 --duration 4 --out clip.mp4
    veo.py image --image start.png --prompt "..." --out clip.mp4
    veo.py transition --first a.png --last b.png --prompt "..." --out clip.mp4
    veo.py wait operations/abc123 --out clip.mp4

Every generation prints a USD estimate first and refuses to run above --max-usd (default 2.00). --dry-run
prints the request and the estimate and spends nothing.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Optional, Sequence

BASE_URL = os.environ.get("VEO_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")

MODELS = {
    "fast": "veo-3.1-fast-generate-preview",
    "standard": "veo-3.1-generate-preview",
    "lite": "veo-3.1-lite-generate-preview",
}
# USD per second of output, with audio. Source: https://ai.google.dev/gemini-api/docs/pricing (checked 2026-10-13).
USD_PER_SECOND = {
    "fast": {"720p": 0.10, "1080p": 0.12, "4k": 0.30},
    "standard": {"720p": 0.40, "1080p": 0.40, "4k": 0.60},
    "lite": {"720p": 0.05, "1080p": 0.08},
}


class VeoError(RuntimeError):
    pass


def resolve_model(name: str) -> str:
    return MODELS.get(name, name)  # allow a full model id


def estimate_usd(model: str, resolution: str, duration: int) -> Optional[float]:
    tier = next((k for k, v in MODELS.items() if v == resolve_model(model) or k == model), None)
    price = USD_PER_SECOND.get(tier or "", {}).get(resolution)
    return None if price is None else round(price * duration, 2)


def _key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise VeoError("GEMINI_API_KEY is not set (store it as an environment variable/secret; never paste it in chat).")
    return key


def _request(method: str, url: str, body: Optional[dict] = None, auth: bool = True, timeout: int = 120) -> Any:
    headers = {"User-Agent": "video-studio/0.1"}
    if auth:
        headers["x-goog-api-key"] = _key()
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url if url.startswith("http") else f"{BASE_URL}/{url.lstrip('/')}", data=data,
                                 method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            err = json.loads(raw)["error"]
            raise VeoError(f"HTTP {exc.code} {err.get('status', '')}: {err.get('message', '')[:400]}") from None
        except (ValueError, KeyError):
            raise VeoError(f"HTTP {exc.code}: {raw[:200]!r}") from None
    except urllib.error.URLError as exc:
        raise VeoError(f"Cannot reach {BASE_URL}: {exc.reason}. Allow generativelanguage.googleapis.com in the "
                       "environment's network policy.") from None
    try:
        return json.loads(raw)
    except ValueError:
        raise VeoError(f"Non-JSON response: {raw[:200]!r}") from None


def _inline_image(path: str) -> dict:
    mime = mimetypes.guess_type(path)[0] or "image/png"
    if mime not in ("image/png", "image/jpeg", "image/webp"):
        raise VeoError(f"{path}: use PNG, JPEG or WebP (got {mime}).")
    with open(path, "rb") as fh:
        return {"inlineData": {"mimeType": mime, "data": base64.b64encode(fh.read()).decode()}}


def submit(model: str, instance: dict, params: dict) -> str:
    body = {"instances": [instance], "parameters": params}
    try:
        data = _request("POST", f"models/{resolve_model(model)}:predictLongRunning", body)
    except VeoError as exc:
        # The docs list durationSeconds as strings ("4","6","8"); the SDKs send integers. Try the other form once.
        if "duration" in str(exc).lower() and "durationSeconds" in params:
            alt = dict(params)
            alt["durationSeconds"] = str(params["durationSeconds"]) if isinstance(params["durationSeconds"], int) else int(params["durationSeconds"])
            data = _request("POST", f"models/{resolve_model(model)}:predictLongRunning", {"instances": [instance], "parameters": alt})
        else:
            raise
    name = data.get("name")
    if not name:
        raise VeoError(f"no operation name in response: {json.dumps(data)[:300]}")
    return name


def wait_for(operation: str, timeout: float, poll: float) -> dict:
    deadline = time.monotonic() + timeout
    while True:
        op = _request("GET", operation)
        if op.get("done"):
            if "error" in op:
                raise VeoError(f"generation failed: {op['error'].get('message', op['error'])}")
            resp = op.get("response", {}).get("generateVideoResponse", {})
            samples = resp.get("generatedSamples") or []
            if not samples:
                reasons = resp.get("raiMediaFilteredReasons") or ["no video returned"]
                raise VeoError("blocked or empty result (safety filter?): " + "; ".join(map(str, reasons)))
            return samples[0]["video"]
        if time.monotonic() > deadline:
            raise VeoError(f"still running after {timeout:.0f}s; resume with: veo.py wait {operation}")
        print("  generating...", file=sys.stderr)
        time.sleep(poll)


def download(uri: str, out: str) -> None:
    req = urllib.request.Request(uri, headers={"x-goog-api-key": _key(), "User-Agent": "video-studio/0.1"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(out, "wb") as fh:
        while chunk := resp.read(1 << 20):
            fh.write(chunk)


def _run(args: argparse.Namespace, instance: dict) -> int:
    params: dict = {"aspectRatio": args.aspect, "durationSeconds": args.duration, "resolution": args.resolution}
    if args.negative:
        params["negativePrompt"] = args.negative
    if args.seed is not None:
        params["seed"] = args.seed
    if args.resolution in ("1080p", "4k") and args.duration != 8:
        raise VeoError("1080p and 4k only support 8-second clips.")
    est = estimate_usd(args.model, args.resolution, args.duration)
    if est is None:
        raise VeoError(f"no price known for {args.model} at {args.resolution}")
    print(f"[{args.cmd}] model={resolve_model(args.model)} {args.resolution} {args.duration}s: estimated cost ${est:.2f}", file=sys.stderr)
    if est > args.max_usd:
        raise VeoError(f"estimate ${est:.2f} is above --max-usd {args.max_usd:.2f}; raise only with the user's approval")
    if args.dry_run:
        shown = json.loads(json.dumps(instance))
        for k in ("image", "lastFrame"):
            if k in shown:
                shown[k] = "<inline image>"
        print(json.dumps({"instances": [shown], "parameters": params}, ensure_ascii=False, indent=2))
        return 0
    op = submit(args.model, instance, params)
    print(f"submitted: {op}", file=sys.stderr)
    if args.no_wait:
        print(json.dumps({"operation": op}))
        return 0
    video = wait_for(op, args.timeout, args.poll)
    result: dict = {"operation": op, "uri": video.get("uri"), "usd_estimate": est}
    if args.out:
        download(video["uri"], args.out)
        result["file"] = args.out
    print(json.dumps(result, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def gen(name: str, help_: str) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--prompt", required=True)
        sp.add_argument("--model", default="fast", help="fast | standard | lite | full model id")
        sp.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
        sp.add_argument("--duration", type=int, default=4, choices=[4, 6, 8])
        sp.add_argument("--resolution", default="720p", choices=["720p", "1080p", "4k"])
        sp.add_argument("--negative", default=None)
        sp.add_argument("--seed", type=int, default=None)
        sp.add_argument("--out", default=None)
        sp.add_argument("--no-wait", action="store_true")
        sp.add_argument("--dry-run", action="store_true")
        sp.add_argument("--max-usd", type=float, default=2.0)
        sp.add_argument("--timeout", type=float, default=900.0)
        sp.add_argument("--poll", type=float, default=float(os.environ.get("VEO_POLL_SECONDS", "10")))
        return sp

    gen("text", "text-to-video")
    gen("image", "image-to-video").add_argument("--image", required=True)
    tr = gen("transition", "first frame -> last frame")
    tr.add_argument("--first", required=True)
    tr.add_argument("--last", required=True)

    es = sub.add_parser("estimate")
    es.add_argument("--model", default="fast")
    es.add_argument("--resolution", default="720p")
    es.add_argument("--duration", type=int, default=4)
    sub.add_parser("models", help="list Veo models this key can use (free call)")
    wt = sub.add_parser("wait")
    wt.add_argument("operation")
    wt.add_argument("--out", default=None)
    wt.add_argument("--timeout", type=float, default=900.0)
    wt.add_argument("--poll", type=float, default=float(os.environ.get("VEO_POLL_SECONDS", "10")))
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "estimate":
            est = estimate_usd(args.model, args.resolution, args.duration)
            print("unknown" if est is None else f"${est:.2f} (with audio; re-check the pricing page)")
            return 0
        if args.cmd == "models":
            data = _request("GET", "models?pageSize=200")
            for m in data.get("models", []):
                if "veo" in m["name"].lower():
                    print(m["name"], "|", m.get("displayName"))
            return 0
        if args.cmd == "wait":
            video = wait_for(args.operation, args.timeout, args.poll)
            if args.out:
                download(video["uri"], args.out)
            print(json.dumps({"uri": video.get("uri"), "file": args.out}))
            return 0
        if args.cmd == "text":
            return _run(args, {"prompt": args.prompt})
        if args.cmd == "image":
            return _run(args, {"prompt": args.prompt, "image": _inline_image(args.image)})
        if args.cmd == "transition":
            return _run(args, {"prompt": args.prompt, "image": _inline_image(args.first),
                               "lastFrame": _inline_image(args.last)})
    except VeoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
