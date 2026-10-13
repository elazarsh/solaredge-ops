"""Tests for the video-studio scripts. Run:  python3 -m unittest discover -s video-studio/tests -v"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "skills"
for sub in ("video-edit-engine/scripts", "video-qa/scripts", "pixverse-generate/scripts"):
    sys.path.insert(0, str(ROOT / sub))

import timemap  # noqa: E402
import hebrew_text  # noqa: E402
import contact_sheet  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # has Hebrew glyphs


class TimeMapTests(unittest.TestCase):
    def test_cut_mapping(self):
        tm = timemap.TimeMap([(0, 2), (4, 6)])
        self.assertAlmostEqual(tm.final_duration, 4.0)
        self.assertAlmostEqual(tm.to_final(1.0), 1.0)
        self.assertAlmostEqual(tm.to_final(5.0), 3.0)
        self.assertIsNone(tm.to_final(3.0))
        self.assertEqual(tm.to_orig(3.0), (5.0, False))

    def test_hold(self):
        tm = timemap.TimeMap([(0, 2), (4, 6)], holds=[(1.0, 0.5)])
        self.assertAlmostEqual(tm.final_duration, 4.5)
        self.assertAlmostEqual(tm.to_final(1.0), 1.0)
        self.assertAlmostEqual(tm.to_final(1.0, after_hold=True), 1.5)
        self.assertAlmostEqual(tm.to_final(5.0), 3.5)
        self.assertEqual(tm.to_orig(1.2), (1.0, True))
        self.assertEqual(tm.to_orig(1.7)[1], False)

    def test_hold_in_cut_region_rejected(self):
        with self.assertRaises(ValueError):
            timemap.TimeMap([(0, 2), (4, 6)], holds=[(3.0, 0.5)])

    def test_overlap_rejected(self):
        with self.assertRaises(ValueError):
            timemap.TimeMap([(0, 3), (2, 5)])

    def test_segments_from_words(self):
        words = [{"word": "a", "start": 0.0, "end": 0.4}, {"word": "b", "start": 0.5, "end": 0.9},
                 {"word": "c", "start": 3.0, "end": 3.5}, {"word": "tick", "start": 8.0, "end": 8.05}]
        segs = timemap.segments_from_words(words, duration=10, max_gap=0.45, pad=0.1, min_len=0.3)
        self.assertEqual(len(segs), 2)  # the 0.05 s noise is dropped
        self.assertAlmostEqual(segs[0][0], 0.0)
        self.assertAlmostEqual(segs[0][1], 1.0)
        self.assertAlmostEqual(segs[1][0], 2.9)

    def test_audio_graph_has_one_piece_per_segment_and_concat(self):
        g = timemap.TimeMap([(0, 2), (4, 6)], holds=[(1.0, 0.5)]).audio_filtergraph()
        self.assertIn("concat=n=4:v=0:a=1[aout]", g)  # play, hold, play, play
        self.assertIn("anullsrc", g)

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg missing")
    def test_audio_graph_runs_in_ffmpeg_and_matches_duration(self):
        tm = timemap.TimeMap([(0, 1), (2, 3)], holds=[(0.5, 0.25)])
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=f=440:d=4", "-ar", "48000",
                            "-ac", "2", src], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", tm.audio_filtergraph(),
                            "-map", "[aout]", out], check=True)
            self.assertAlmostEqual(contact_sheet.probe_duration(out), tm.final_duration, delta=0.1)


@unittest.skipUnless(hebrew_text.features.check("raqm") and os.path.exists(FONT), "RAQM or font missing")
class HebrewTextTests(unittest.TestCase):
    def test_renders_non_empty(self):
        img = hebrew_text.render_text("שלום עולם", FONT, 64)
        self.assertGreater(img.width, 50)
        self.assertIsNotNone(img.getbbox())

    def test_rtl_differs_from_ltr(self):
        a = hebrew_text.render_text("שלום Falafel", FONT, 64, direction="rtl", padding=0)
        b = hebrew_text.render_text("שלום Falafel", FONT, 64, direction="ltr", padding=0)
        self.assertNotEqual(a.tobytes(), b.tobytes() if a.size == b.size else a.tobytes() + b"x")

    def test_wrap_respects_max_width(self):
        font = hebrew_text.load_font(FONT, 48)
        lines = hebrew_text.wrap_lines("זה משפט ארוך מאוד שצריך לרדת שורה כמה פעמים", font, 300, "rtl")
        self.assertGreater(len(lines), 1)
        for ln in lines:
            self.assertLessEqual(font.getlength(ln, direction="rtl", language="he"), 300 + 1)

    def test_missing_raqm_fails_loudly(self):
        original = hebrew_text.features.check
        hebrew_text.features.check = lambda name: False
        try:
            with self.assertRaises(RuntimeError):
                hebrew_text.render_text("שלום", FONT, 40)
        finally:
            hebrew_text.features.check = original


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg missing")
class ContactSheetTests(unittest.TestCase):
    def test_sheet_and_moments(self):
        with tempfile.TemporaryDirectory() as d:
            vid = os.path.join(d, "t.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=24:duration=3",
                            "-pix_fmt", "yuv420p", vid], check=True)
            out = os.path.join(d, "qa")
            files = contact_sheet.build_sheets(vid, out, fps=6, cols=6, thumb_w=160, start=0, end=None, per_sheet=36)
            self.assertEqual(len(files), 1)
            from PIL import Image
            with Image.open(files[0]) as im:
                w, h = im.size
            self.assertEqual(w, 6 * 160)
            self.assertEqual(h, 3 * 120)  # 18 frames / 6 cols = 3 rows of 160x120
            moments = contact_sheet.grab_moments(vid, out, [1.0, 2.5])
            self.assertTrue(all(os.path.exists(m) for m in moments))
            self.assertEqual(contact_sheet.timecode(75.5), "01:15.50")


class _Mock(BaseHTTPRequestHandler):
    calls = []
    polls = 0

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        _Mock.calls.append((self.path, dict(self.headers), body))
        if self.path == "/openapi/v2/image/upload":
            return self._send({"ErrCode": 0, "ErrMsg": "success", "Resp": {"img_id": 9, "img_url": "x"}})
        if self.path == "/openapi/v2/video/text/generate" and b"BOOM" in body:
            return self._send({"ErrCode": 500090, "ErrMsg": "Insufficient balance"})
        return self._send({"ErrCode": 0, "ErrMsg": "success", "Resp": {"video_id": 123}})

    def do_GET(self):
        _Mock.calls.append((self.path, dict(self.headers), b""))
        if self.path == "/openapi/v2/video/result/123":
            _Mock.polls += 1
            if _Mock.polls < 2:
                return self._send({"ErrCode": 0, "Resp": {"status": 5}})
            host = self.headers["Host"]
            return self._send({"ErrCode": 0, "Resp": {"status": 1, "url": f"http://{host}/file.mp4",
                                                       "outputWidth": 720, "outputHeight": 1280, "seed": 7}})
        if self.path == "/file.mp4":
            self.send_response(200)
            self.send_header("Content-Length", "5")
            self.end_headers()
            self.wfile.write(b"VIDEO")
            return
        if self.path == "/openapi/v2/account/balance":
            return self._send({"ErrCode": 0, "Resp": {"account_id": 1, "credit_monthly": 100, "credit_package": 50}})
        self._send({"ErrCode": 1, "ErrMsg": "nope"})


class PixVerseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Mock)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        os.environ["PIXVERSE_BASE_URL"] = f"http://127.0.0.1:{cls.server.server_port}"
        os.environ["PIXVERSE_API_KEY"] = "test-key-123"
        os.environ["PIXVERSE_POLL_SECONDS"] = "0.01"
        os.environ["NO_PROXY"] = "127.0.0.1"
        sys.path.insert(0, str(ROOT / "pixverse-generate/scripts"))
        import importlib
        import pixverse
        cls.px = importlib.reload(pixverse)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        _Mock.calls.clear()
        _Mock.polls = 0

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = self.px.main(list(argv))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_estimate_matches_docs_example(self):
        # Docs: $1 = 5 videos of v6/720p/5s/no audio  =>  45 credits each
        self.assertEqual(self.px.estimate_credits("v6", "720p", 5, False), 45.0)
        self.assertEqual(self.px.estimate_credits("c1", "1080p", 10, True), 240.0)
        self.assertIsNone(self.px.estimate_credits("v5", "720p", 5, False))

    def test_text_flow_downloads_and_never_leaks_key(self):
        with tempfile.TemporaryDirectory() as d:
            out_file = os.path.join(d, "c.mp4")
            code, out, err = self.run_cli("text", "--prompt", "a fox", "--out", out_file, "--audio")
            self.assertEqual(code, 0, err)
            self.assertEqual(Path(out_file).read_bytes(), b"VIDEO")
            self.assertEqual(json.loads(out)["video_id"], 123)
            self.assertNotIn("test-key-123", out + err)
        post = next(c for c in _Mock.calls if c[0].endswith("/video/text/generate"))
        payload = json.loads(post[2])
        self.assertEqual(payload["aspect_ratio"], "9:16")
        self.assertTrue(payload["generate_audio_switch"])
        hdr = {k.lower(): v for k, v in post[1].items()}  # urllib capitalises names; HTTP is case-insensitive
        self.assertEqual(hdr["api-key"], "test-key-123")
        # status polled twice (5 then 1) with distinct trace ids on every request
        ids = [{k.lower(): v for k, v in c[1].items()}["ai-trace-id"] for c in _Mock.calls if c[0].startswith("/openapi")]
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            uuid.UUID(i)

    def test_dry_run_spends_nothing(self):
        code, out, err = self.run_cli("text", "--prompt", "x", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(_Mock.calls, [])
        self.assertIn("estimated cost: 45 credits", err)

    def test_spend_guard_blocks_expensive_job(self):
        code, _, err = self.run_cli("text", "--prompt", "x", "--model", "c1", "--quality", "1080p", "--duration", "15", "--audio")  # 360 credits
        self.assertEqual(code, 2)
        self.assertIn("above --max-credits", err)
        self.assertEqual(_Mock.calls, [])

    def test_image_uploads_then_generates(self):
        with tempfile.TemporaryDirectory() as d:
            img = os.path.join(d, "a.png")
            Path(img).write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 20)
            code, out, err = self.run_cli("image", "--image", img, "--prompt", "move", "--no-wait")
        self.assertEqual(code, 0, err)
        paths = [c[0] for c in _Mock.calls]
        self.assertEqual(paths[0], "/openapi/v2/image/upload")
        self.assertEqual(json.loads(_Mock.calls[1][2])["img_id"], 9)

    def test_api_error_is_readable(self):
        code, _, err = self.run_cli("text", "--prompt", "BOOM", "--no-wait")
        self.assertEqual(code, 2)
        self.assertIn("500090", err)
        self.assertIn("Top up", err)

    def test_balance(self):
        code, out, _ = self.run_cli("balance")
        self.assertEqual(json.loads(out), {"credit_monthly": 100, "credit_package": 50})

    def test_missing_key_message(self):
        saved = os.environ.pop("PIXVERSE_API_KEY")
        try:
            code, _, err = self.run_cli("balance")
        finally:
            os.environ["PIXVERSE_API_KEY"] = saved
        self.assertEqual(code, 2)
        self.assertIn("PIXVERSE_API_KEY", err)


class PluginStructureTests(unittest.TestCase):
    """Skills and agents must be loadable: valid front matter, names match folders, references resolve."""
    PLUGIN = Path(__file__).resolve().parents[1]

    @staticmethod
    def front_matter(path):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{path}: missing front matter"
        head = text.split("\n---\n", 1)[0][4:]
        fields = {}
        for line in head.splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fields[k.strip()] = v.strip()
        return fields

    def test_manifest(self):
        data = json.loads((self.PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(data["name"], "video-studio")

    def test_every_skill_is_valid(self):
        skills = sorted((self.PLUGIN / "skills").iterdir())
        self.assertGreaterEqual(len(skills), 8)
        for d in skills:
            fm = self.front_matter(d / "SKILL.md")
            self.assertEqual(fm["name"], d.name)
            self.assertTrue(20 < len(fm["description"]) <= 1024, d.name)

    def test_every_agent_is_valid(self):
        agents = sorted((self.PLUGIN / "agents").glob("*.md"))
        self.assertEqual(len(agents), 5)
        for a in agents:
            fm = self.front_matter(a)
            self.assertEqual(fm["name"], a.stem)
            self.assertIn("description", fm)
            self.assertIn("tools", fm)

    def test_script_and_reference_paths_mentioned_in_skills_exist(self):
        import re
        for skill in (self.PLUGIN / "skills").iterdir():
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            for rel in re.findall(r"`((?:scripts|reference)/[\w./-]+)`", text):
                self.assertTrue((skill / rel).exists(), f"{skill.name}: {rel} is referenced but missing")

    @unittest.skipUnless(shutil.which("bash"), "bash missing")
    def test_install_script_copies_and_respects_existing(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, CLAUDE_HOME=home)
            r = subprocess.run(["bash", str(self.PLUGIN / "install.sh")], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(home) / "skills" / "video-studio" / "SKILL.md").exists())
            self.assertTrue((Path(home) / "agents" / "video-director.md").exists())
            self.assertFalse(list(Path(home).rglob("__pycache__")))
            # a user-edited skill is not overwritten without --force
            edited = Path(home) / "skills" / "video-qa" / "SKILL.md"
            edited.write_text("mine")
            r = subprocess.run(["bash", str(self.PLUGIN / "install.sh")], env=env, capture_output=True, text=True)
            self.assertIn("SKIP  skills/video-qa", r.stdout)
            self.assertEqual(edited.read_text(), "mine")
            subprocess.run(["bash", str(self.PLUGIN / "install.sh"), "--force"], env=env, check=True, capture_output=True)
            self.assertNotEqual(edited.read_text(), "mine")


if __name__ == "__main__":
    unittest.main()
