#!/usr/bin/env python3
"""Deterministic media digest for a video/audio file: facts, frames, contact sheet, optional Hebrew/English transcript.

Usage: python3 media_extract.py <file> --out DIR [--fps 0.5] [--lang he] [--no-transcribe] [--model NAME]
Needs ffmpeg/ffprobe. Transcription needs `pip install faster-whisper numpy` (local, no API, no tokens).
Output: DIR/info.json, DIR/frames/f%03d.jpg, DIR/sheet.jpg (one image to look at instead of many), DIR/transcript.json + .txt
Reading the contact sheet costs one image instead of N frames.
"""
import argparse, json, os, subprocess, sys, wave

def run(cmd): return subprocess.run(cmd, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=float, default=0.5); ap.add_argument("--lang", default="he")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--model", default="ivrit-ai/whisper-large-v3-turbo-ct2")
    a = ap.parse_args(); os.makedirs(os.path.join(a.out, "frames"), exist_ok=True)
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height", "-of", "json", a.file])
    info = json.loads(p.stdout or "{}"); json.dump(info, open(os.path.join(a.out, "info.json"), "w"), indent=2)
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    has_video = any(s.get("codec_type") == "video" for s in info.get("streams", []))
    if has_video:
        run(["ffmpeg", "-v", "error", "-y", "-i", a.file, "-vf", f"fps={a.fps},scale=270:-1", os.path.join(a.out, "frames", "f%03d.jpg")])
        n = len([x for x in os.listdir(os.path.join(a.out, "frames")) if x.endswith(".jpg")])
        cols = 5; rows = max(1, -(-n // cols))
        run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", os.path.join(a.out, "frames", "f%03d.jpg"),
             "-vf", f"tile={cols}x{rows}", "-frames:v", "1", os.path.join(a.out, "sheet.jpg")])
    if has_audio and not a.no_transcribe:
        wav = os.path.join(a.out, "a.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", a.file, "-ac", "1", "-ar", "16000", wav])
        try:
            import numpy as np
            from faster_whisper import WhisperModel
            w = wave.open(wav); audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            segs, _ = WhisperModel(a.model, device="cpu", compute_type="int8").transcribe(audio, language=a.lang)
            rows = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
            json.dump(rows, open(os.path.join(a.out, "transcript.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(os.path.join(a.out, "transcript.txt"), "w", encoding="utf-8").write("\n".join(f"{r['start']:6.1f} {r['text']}" for r in rows))
        except Exception as e:  # report, never fake a transcript
            open(os.path.join(a.out, "transcript.error.txt"), "w").write(repr(e))
            print("transcription skipped:", repr(e), file=sys.stderr)
    print("done:", a.out)

if __name__ == "__main__":
    sys.exit(main())
