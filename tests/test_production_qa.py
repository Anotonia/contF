"""Synthetic media preflight contract tests; no external network or private footage."""
import sys
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_qa import inspect, _video_duration


class CandidatePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.media = Path(self.tmp.name) / "synthetic.mp4"
        self.media.write_bytes(b"SYNTHETIC: mocked ffprobe metadata")

    def test_rejects_missing_audio(self):
        with patch("contf.production_qa.probe", return_value={
            "format": {"duration": "20.0"},
            "streams": [{"codec_type": "video", "width": 1280, "height": 720, "duration": "20"}],
        }):
            result = inspect(self.media)
        self.assertFalse(result["passed"])
        self.assertIn("audio stream missing", result["errors"])

    def test_rejects_out_of_window(self):
        with patch("contf.production_qa.probe", return_value={
            "format": {"duration": "192.0"},
            "streams": [{"codec_type": "video", "width": 1280, "height": 720, "duration": "192"},
                        {"codec_type": "audio"}],
        }):
            result = inspect(self.media)
        self.assertFalse(result["passed"])
        self.assertIn("duration outside candidate window", result["errors"])

    def test_stream_pass_never_claims_final_visual_qa(self):
        with patch("contf.production_qa.probe", return_value={
            "format": {"duration": "20.0"},
            "streams": [{"codec_type": "video", "width": 1280, "height": 720, "duration": "20"},
                        {"codec_type": "audio"}],
        }):
            result = inspect(self.media)
        self.assertTrue(result["passed"])
        self.assertFalse(result["is_final_video"])
        self.assertTrue(all(x == "pending" for x in result["manual_gates"].values()))

    def test_missing_media_fails_closed(self):
        result = inspect(self.media.parent / "missing.mp4")
        self.assertFalse(result["passed"])
        self.assertTrue(result["errors"])

    def test_attached_picture_is_not_video_and_unknown_duration_fails_closed(self):
        info = {"format": {"duration": "20"}, "streams": [
            {"codec_type": "video", "duration": "20", "width": 1280, "height": 720,
             "disposition": {"attached_pic": 1}},
            {"codec_type": "video", "width": 1280, "height": 720}, {"codec_type": "audio"}]}
        with patch("contf.production_qa.probe", return_value=info):
            result = inspect(self.media)
        self.assertFalse(result["passed"])
        self.assertEqual(result["video_stream_count"], 1)
        self.assertIsNone(result["duration_s"])
        self.assertIn("video duration cannot be established", result["errors"])
        info["streams"].pop(1)
        with patch("contf.production_qa.probe", return_value=info):
            self.assertIn("video stream missing", inspect(self.media)["errors"])

    def test_packet_duration_fallback_and_missing_timestamps(self):
        packets = {"packets": [{"pts_time": "5", "duration_time": "1"},
                               {"pts_time": "6", "duration_time": "1"}]}
        completed = subprocess.CompletedProcess([], 0, json.dumps(packets), "")
        with patch("contf.production_qa.subprocess.run", return_value=completed) as run:
            self.assertEqual(_video_duration(self.media, {"index": 2}), 2)
            self.assertIn("2", run.call_args.args[0])
        completed.stdout = '{"packets": []}'
        with patch("contf.production_qa.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "cannot be established"):
                _video_duration(self.media, {"index": 2})

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg not installed")
    def test_short_video_long_audio_rejected(self):
        for suffix in (".mp4", ".mkv"):
            media = self.media.with_suffix(suffix)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            "testsrc=size=640x360:rate=12:duration=2", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=12", "-c:v", "libx264", "-preset", "ultrafast",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", str(media)], check=True)
            result = inspect(media, min_seconds=11.5, max_seconds=12.5)
            self.assertFalse(result["passed"])
            self.assertAlmostEqual(result["duration_s"], 2, delta=0.2)
            self.assertIn("duration outside candidate window", result["errors"])


if __name__ == "__main__":
    unittest.main()
