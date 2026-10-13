#!/usr/bin/env python3
"""PixVerse Platform API client (standard library only).

Implements the flow from https://docs.platform.pixverse.ai :
  submit job -> receive video_id -> poll status (1 = done, 5 = generating) -> download Resp.url

Auth: environment variable PIXVERSE_API_KEY (create one at https://platform.pixverse.ai, "API Keys").
The key is never printed. Every request gets a fresh UUID in the Ai-trace-id header, because the API
returns the PREVIOUS result when that header repeats.

    pixverse.py balance
    pixverse.py estimate --model v6 --quality 720p --duration 5 --audio
    pixverse.py text  --prompt "..." --aspect 9:16 --duration 5 --quality 720p --out clip.mp4
    pixverse.py image --image start.png --prompt "..." --out clip.mp4
    pixverse.py transition --first a.png --last b.png --prompt "..." --out clip.mp4
    pixverse.py extend --source-video-id 123 --prompt "..." --out longer.mp4
    pixverse.py status 123
    pixverse.py wait 123 --out clip.mp4

Every generation command prints a credit estimate first and refuses to run above --max-credits
(default 300). Use --dry-run to see the payload and estimate without spending anything.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any, Optional, Sequence

BASE_URL = os.environ.get("PIXVERSE_BASE_URL", "https://app-api.pixverse.ai").rstrip("/")

# Credits per second, from https://docs.platform.pixverse.ai/pricing-796039m0 (checked 2026-10-13).
# (no audio, with audio). Re-check the pricing page before relying on it: prices change.
CREDITS_PER_SECOND = {
    "c1": {"360p": (6, 8), "540p": (8, 10), "720p": (10, 13), "1080p": (19, 24)},
    "v6": {"360p": (5, 7), "540p": (7, 9), "720p": (9, 12), "1080p": (18, 23)},
}
# Docs: "$1 = 5 videos (v6, 720p, 5s, no audio)" = 5 * 45 credits = 225 credits per dollar.
CREDITS_PER_USD = 225.0

STATUS_TEXT = {1: "done", 5: "generating", 6: "deleted", 7: "blocked by content moderation", 8: "generation failed"}

ERROR_HINTS = {
    400017: "Invalid parameter (check model/quality/duration/aspect combination).",
    400018: "Prompt too long for this endpoint.",
    400032: "Invalid image ID: upload the image first.",
    500044: "Concurrent generation limit reached (Free plan: 3 at a time). Wait and retry.",
    500054: "Image blocked by content moderation. Use a different image.",
    500063: "Blocked by content moderation (video, image or text). Rephrase or replace the input.",
    500069: "PixVerse is under high load. Retry later.",
    500071: "This effect does not support 720p/1080p.",
    500090: "Insufficient credits. Top up at https://platform.pixverse.ai/billing (API credits are separate from the web app).",
}


class PixVerseError(RuntimeError):
    pass


def estimate_credits(model: str, quality: str, duration: int, audio: bool) -> Optional[float]:
    table = CREDITS_PER_SECOND.get(model.lower())
    if not table or quality not in table:
        return None
    return float(table[quality][1 if audio else 0] * duration)


def _key() -> str:
    key = os.environ.get("PIXVERSE_API_KEY", "").strip()
    if not key:
        raise PixVerseError(
            "PIXVERSE_API_KEY is not set. Create a key at https://platform.pixverse.ai (API Keys) and "
            "store it as an environment variable or secret. Never paste it into a chat."
        )
    return key


def _headers(extra: Optional[dict] = None) -> dict:
    h = {"API-KEY": _key(), "Ai-trace-id": str(uuid.uuid4()), "User-Agent": "video-studio/0.1"}
    if extra:
        h.update(extra)
    return h


def _request(method: str, path: str, body: Optional[bytes] = None, headers: Optional[dict] = None) -> Any:
    url = path if path.startswith("http") else f"{BASE_URL}{path}"
    req = urllib.request.Request(url, data=body, method=method, headers=_headers(headers))
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        if not raw:
            raise PixVerseError(f"HTTP {exc.code} from {path}") from None
    except urllib.error.URLError as exc:
        raise PixVerseError(f"Cannot reach {BASE_URL}: {exc.reason}. If this runs in a sandbox, allow the host "
                            "app-api.pixverse.ai in the network settings.") from None
    try:
        data = json.loads(raw)
    except ValueError:
        raise PixVerseError(f"Non-JSON response from {path}: {raw[:200]!r}") from None
    if isinstance(data, dict) and data.get("ErrCode", 0) != 0:
        code = data["ErrCode"]
        hint = ERROR_HINTS.get(code, "")
        raise PixVerseError(f"PixVerse error {code}: {data.get('ErrMsg', '')} {hint}".strip())
    return data


def _post_json(path: str, payload: dict) -> Any:
    return _request("POST", path, json.dumps(payload).encode(), {"Content-Type": "application/json"})


def _multipart(field: str, filename: str, content: bytes, mime: str) -> tuple[bytes, str]:
    boundary = "----videostudio" + uuid.uuid4().hex
    head = (f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n").encode()
    return head + content + f"\r\n--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


def upload_image(source: str) -> int:
    """Upload a local file or an https URL; returns img_id for the generation calls."""
    if source.startswith(("http://", "https://")):
        boundary = "----videostudio" + uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image_url"\r\n\r\n{source}\r\n'
                f"--{boundary}--\r\n").encode()
        ctype = f"multipart/form-data; boundary={boundary}"
    else:
        with open(source, "rb") as fh:
            content = fh.read()
        mime = mimetypes.guess_type(source)[0] or "application/octet-stream"
        if mime not in ("image/jpeg", "image/png", "image/webp"):
            raise PixVerseError(f"{source}: PixVerse accepts JPG, PNG or WebP only (got {mime}).")
        if len(content) > 20 * 1024 * 1024:
            raise PixVerseError(f"{source}: image is over the 20 MB limit.")
        body, ctype = _multipart("image", os.path.basename(source), content, mime)
    data = _request("POST", "/openapi/v2/image/upload", body, {"Content-Type": ctype})
    return int(data["Resp"]["img_id"])


def get_status(video_id: int) -> dict:
    return _request("GET", f"/openapi/v2/video/result/{video_id}")["Resp"]


def wait_for(video_id: int, timeout: float, poll: float) -> dict:
    deadline = time.monotonic() + timeout
    while True:
        resp = get_status(video_id)
        status = resp.get("status")
        if status == 1:
            return resp
        if status in (6, 7, 8):
            raise PixVerseError(f"video {video_id}: {STATUS_TEXT.get(status)} (status {status})")
        if time.monotonic() > deadline:
            raise PixVerseError(f"video {video_id}: still generating after {timeout:.0f}s; "
                                f"resume with: pixverse.py wait {video_id}")
        print(f"  video {video_id}: {STATUS_TEXT.get(status, status)}...", file=sys.stderr)
        time.sleep(poll)


def download(url: str, out: str) -> None:
    # The media CDN URL is public; do not send the API key to it.
    req = urllib.request.Request(url, headers={"User-Agent": "video-studio/0.1"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(out, "wb") as fh:
        while chunk := resp.read(1 << 20):
            fh.write(chunk)


def _gate(args: argparse.Namespace, label: str, payload: dict) -> None:
    model = payload.get("model", "v6")
    est = estimate_credits(model, payload.get("quality", "720p"), int(payload.get("duration", 5)),
                           bool(payload.get("generate_audio_switch")))
    if est is None:
        print(f"[{label}] cost: unknown for model {model} (see the pricing page)", file=sys.stderr)
    else:
        print(f"[{label}] estimated cost: {est:.0f} credits (~${est / CREDITS_PER_USD:.2f})", file=sys.stderr)
        if est > args.max_credits:
            raise PixVerseError(f"estimate {est:.0f} credits is above --max-credits {args.max_credits:.0f}; "
                                "raise the limit only after the user approved the spend")
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        raise SystemExit(0)


def _submit_and_collect(args: argparse.Namespace, path: str, payload: dict) -> int:
    if getattr(args, "extra", None):
        payload.update(json.loads(args.extra))
    _gate(args, args.cmd, payload)
    video_id = int(_post_json(path, payload)["Resp"]["video_id"])
    print(f"submitted: video_id={video_id}", file=sys.stderr)
    if args.no_wait:
        print(json.dumps({"video_id": video_id}))
        return 0
    resp = wait_for(video_id, args.timeout, args.poll)
    result = {"video_id": video_id, "url": resp.get("url"), "width": resp.get("outputWidth"),
              "height": resp.get("outputHeight"), "seed": resp.get("seed")}
    if args.out:
        download(resp["url"], args.out)
        result["file"] = args.out
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _common_payload(args: argparse.Namespace) -> dict:
    p: dict = {"model": args.model, "prompt": args.prompt, "duration": args.duration, "quality": args.quality}
    if args.seed is not None:
        p["seed"] = args.seed
    if args.audio:
        p["generate_audio_switch"] = True
    if args.multi_clip:
        p["generate_multi_clip_switch"] = True
    if getattr(args, "negative", None):
        p["negative_prompt"] = args.negative
    return p


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def gen(name: str, help_: str) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--prompt", required=True)
        sp.add_argument("--model", default="v6", help="v6 (general, extend) or c1 (cinematic, references)")
        sp.add_argument("--duration", type=int, default=5, help="seconds, 1-15 for v6/c1")
        sp.add_argument("--quality", default="720p", choices=["360p", "540p", "720p", "1080p"])
        sp.add_argument("--seed", type=int, default=None)
        sp.add_argument("--audio", action="store_true", help="generate audio (v5.5+/v6/c1)")
        sp.add_argument("--multi-clip", action="store_true", help="multi-clip output (v6)")
        sp.add_argument("--negative", default=None, help="negative prompt")
        sp.add_argument("--extra", default=None, help="JSON object merged into the payload for fields not covered here")
        sp.add_argument("--out", default=None, help="download the finished video to this path")
        sp.add_argument("--no-wait", action="store_true")
        sp.add_argument("--dry-run", action="store_true", help="print payload and cost, spend nothing")
        sp.add_argument("--max-credits", type=float, default=300.0)
        sp.add_argument("--timeout", type=float, default=600.0)
        sp.add_argument("--poll", type=float, default=float(os.environ.get("PIXVERSE_POLL_SECONDS", "4")))
        return sp

    t = gen("text", "text-to-video")
    t.add_argument("--aspect", default="9:16", help="16:9 9:16 1:1 4:3 3:4 (v6/c1 also 2:3 3:2 21:9)")
    i = gen("image", "image-to-video (local file, https URL, or --img-id)")
    i.add_argument("--image", default=None)
    i.add_argument("--img-id", type=int, default=None)
    tr = gen("transition", "first-frame to last-frame video")
    tr.add_argument("--first", required=True)
    tr.add_argument("--last", required=True)
    ex = gen("extend", "extend a PixVerse video (v6 only)")
    ex.add_argument("--source-video-id", type=int, required=True)

    es = sub.add_parser("estimate", help="credit estimate only; needs no API key")
    es.add_argument("--model", default="v6")
    es.add_argument("--quality", default="720p")
    es.add_argument("--duration", type=int, default=5)
    es.add_argument("--audio", action="store_true")

    sub.add_parser("balance", help="show credit balance")
    up = sub.add_parser("upload-image", help="upload an image, print img_id")
    up.add_argument("source")
    st = sub.add_parser("status", help="show status of a video_id")
    st.add_argument("video_id", type=int)
    wt = sub.add_parser("wait", help="wait for a video_id and optionally download it")
    wt.add_argument("video_id", type=int)
    wt.add_argument("--out", default=None)
    wt.add_argument("--timeout", type=float, default=600.0)
    wt.add_argument("--poll", type=float, default=float(os.environ.get("PIXVERSE_POLL_SECONDS", "4")))
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "estimate":
            est = estimate_credits(args.model, args.quality, args.duration, args.audio)
            if est is None:
                print("unknown for this model/quality; see https://docs.platform.pixverse.ai/pricing-796039m0")
            else:
                print(f"{est:.0f} credits (~${est / CREDITS_PER_USD:.2f}); approximate, re-check the pricing page")
            return 0
        if args.cmd == "balance":
            r = _request("GET", "/openapi/v2/account/balance")["Resp"]
            print(json.dumps({"credit_monthly": r.get("credit_monthly"), "credit_package": r.get("credit_package")}))
            return 0
        if args.cmd == "upload-image":
            print(upload_image(args.source))
            return 0
        if args.cmd == "status":
            r = get_status(args.video_id)
            print(json.dumps({"status": r.get("status"), "meaning": STATUS_TEXT.get(r.get("status")), "url": r.get("url")}))
            return 0
        if args.cmd == "wait":
            r = wait_for(args.video_id, args.timeout, args.poll)
            if args.out:
                download(r["url"], args.out)
            print(json.dumps({"video_id": args.video_id, "url": r.get("url"), "file": args.out}))
            return 0
        if args.cmd == "text":
            payload = _common_payload(args)
            payload["aspect_ratio"] = args.aspect
            return _submit_and_collect(args, "/openapi/v2/video/text/generate", payload)
        if args.cmd == "image":
            if args.img_id is None:
                if not args.image:
                    raise PixVerseError("give --image (file or URL) or --img-id")
                if args.dry_run:
                    img_id = 0
                else:
                    img_id = upload_image(args.image)
                    print(f"uploaded: img_id={img_id}", file=sys.stderr)
            else:
                img_id = args.img_id
            payload = _common_payload(args)
            payload["img_id"] = img_id
            return _submit_and_collect(args, "/openapi/v2/video/img/generate", payload)
        if args.cmd == "transition":
            first = 0 if args.dry_run else upload_image(args.first)
            last = 0 if args.dry_run else upload_image(args.last)
            payload = _common_payload(args)
            payload.update({"first_frame_img": first, "last_frame_img": last})
            return _submit_and_collect(args, "/openapi/v2/video/transition/generate", payload)
        if args.cmd == "extend":
            payload = _common_payload(args)
            payload["source_video_id"] = args.source_video_id
            return _submit_and_collect(args, "/openapi/v2/video/extend/generate", payload)
    except PixVerseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
