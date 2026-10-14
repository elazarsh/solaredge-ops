#!/usr/bin/env python3
"""Two 30 s music clips from Google Lyria 3 Clip (USD 0.04 each, Gemini API Interactions endpoint)."""
import base64, json, os, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
PROMPTS = {
    "epic": ("Instrumental only, no vocals. Hollywood blockbuster action-movie trailer music, huge cinematic orchestra: "
             "pounding taiko and war drums from the very first second, low brass stabs, soaring urgent strings, "
             "rapidly rising tension and accelerating energy, dark heroic minor key, 150 bpm, begins immediately at full intensity."),
    "nursery": ("Instrumental only, no vocals. Silly cheerful children's kindergarten music: bouncy xylophone, glockenspiel, "
                "toy bells and a squeaky recorder flute, simple catchy major-key melody, 120 bpm, light pizzicato bass, "
                "playful and slightly ridiculous, begins immediately."),
}


def generate(name, prompt):
    body = {"model": "lyria-3-clip-preview", "input": prompt}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=json.dumps(body).encode(),
                                 method="POST", headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    for step in data.get("steps", []):
        if step.get("type") == "model_output":
            for c in step.get("content", []):
                if c.get("type") == "audio":
                    mp3 = HERE / "music" / f"{name}.mp3"
                    mp3.write_bytes(base64.b64decode(c["data"]))
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "2", str(mp3.with_suffix(".wav"))], check=True)
                    return mp3
    raise RuntimeError(f"no audio in response: {json.dumps(data)[:300]}")


if __name__ == "__main__":
    for name, prompt in PROMPTS.items():
        if (HERE / "music" / f"{name}.wav").exists():
            print(name, "cached"); continue
        for attempt in range(5):
            try:
                print(name, generate(name, prompt)); break
            except Exception as exc:
                wait = 30 * (attempt + 1) if "429" in str(exc) else 8
                print(name, "failed:", str(exc)[:80], f"waiting {wait}s", file=sys.stderr, flush=True); time.sleep(wait)
        time.sleep(5)
