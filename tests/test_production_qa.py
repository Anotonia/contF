"""Synthetic media preflight contract tests; no external network or private footage."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_qa import inspect


class CandidatePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.media = Path(self.tmp.name) / "synthetic.mp4"
        self.media.write_bytes(b"SYNTHETIC: mocked ffprobe metadata")

    def test_rejects_missing_audio(self):
        with patch("contf.production_qa.probe", return_value={
            "format": {"duration": "20.0"},
            "streams": [{"codec_type": "video", "width": 1280, "height": 720}],
        }):
            result = inspect(self.media)
        self.assertFalse(result["passed"])
        self.assertIn("audio stream missing", result["errors"])

    def test_rejects_out_of_window(self):
        with patch("contf.production_qa.probe", return_value={
            "format": {"duration": "192.0"},
            "streams": [{"codec_type": "video", "width": 1280, "height": 720},
                        {"codec_type": "audio"}],
        }):
            result = inspect(self.media)
        self.assertFalse(result["passed"])
        self.assertIn("duration outside candidate window", result["errors"])

    def test_stream_pass_never_claims_final_visual_qa(self):
        with patch("contf.production_qa.probe", return_value={
            "format": {"duration": "20.0"},
            "streams": [{"codec_type": "video", "width": 1280, "height": 720},
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


if __name__ == "__main__":
    unittest.main()
