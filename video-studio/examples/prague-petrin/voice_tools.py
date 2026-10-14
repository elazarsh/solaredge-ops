#!/usr/bin/env python3
"""Narration tools: Gemini TTS -> 48 kHz wav, and transcription check (stdlib + ffmpeg).
Key from GEMINI_API_KEY (never printed). Used for the Prague funicular meme narrator."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path

BASE = "https://generativelanguage.googleapis.com/v1beta"
TTS_MODEL = os.environ.get("TTS_MODEL", "gemini-2.5-flash-preview-tts")
STT_MODEL = os.environ.get("STT_MODEL", "gemini-flash-latest")


def _post(path: str, body: dict, timeout=180) -> dict:
    req = urllib.request.Request(f"{BASE}/{path}", data=json.dumps(body).encode(), method="POST",
                                 headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def tts(text: str, out_wav: Path, voice: str = "Charon", style: str = "") -> float:
    prompt = f"{style}\n\n{text}" if style else text
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    data = _post(f"models/{TTS_MODEL}:generateContent", body)
    cand = data.get("candidates", [{}])[0]
    if "content" not in cand:
        raise RuntimeError(f"TTS returned no audio (finishReason={cand.get('finishReason')})")
    part = cand["content"]["parts"][0]["inlineData"]
    pcm = base64.b64decode(part["data"])
    raw = out_wav.with_suffix(".raw.wav")
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ar", "48000", "-ac", "1", str(out_wav)], check=True)
    raw.unlink()
    return duration(out_wav)


def duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def transcribe(wav: Path) -> str:
    b64 = base64.b64encode(wav.read_bytes()).decode()
    body = {"contents": [{"parts": [{"text": "Transcribe this Hebrew audio exactly, word by word, without niqqud and without any comment. Output only the transcript."},
                                    {"inlineData": {"mimeType": "audio/wav", "data": b64}}]}]}
    data = _post(f"models/{STT_MODEL}:generateContent", body)
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


if __name__ == "__main__":
    text, out = sys.argv[1], Path(sys.argv[2])
    voice = sys.argv[3] if len(sys.argv) > 3 else "Charon"
    style = sys.argv[4] if len(sys.argv) > 4 else ""
    print(round(tts(text, out, voice, style), 2), "s")
