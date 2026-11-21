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
from contf.production_adapter import REQUIRED_REVIEW, ingest
from contf.production_jobs import build_jobs
from contf.shot_pipeline import render_preview
from test_production_jobs import project


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
    def test_multiple_video_tracks_rejected_and_preview_maps_first_real_video(self):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "color=red:size=640x360:rate=12:duration=12", "-f", "lavfi", "-i",
                        "color=blue:size=800x450:rate=12:duration=20", "-f", "lavfi", "-i",
                        "sine=frequency=440:duration=20", "-map", "0:v", "-map", "1:v",
                        "-map", "2:a", "-c:v", "libx264", "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-disposition:v:0", "0",
                        "-disposition:v:1", "default", str(self.media)], check=True)
        result = inspect(self.media, min_seconds=11.5, max_seconds=12.5)
        self.assertFalse(result["passed"])
        self.assertEqual(result["video_stream_count"], 2)
        self.assertAlmostEqual(result["duration_s"], 12, delta=0.2)
        self.assertIn("multiple video streams are not supported", result["errors"])
        spec = project()
        spec["shots"][0]["duration_s"] = 12
        root = self.media.parent
        receipt = {"receipt_version": "0.1.0", "shot_id": "S01",
                   "fingerprint": build_jobs(spec, root)["jobs"][0]["fingerprint"],
                   "producer": "SYNTHETIC", "model_version": "SYNTHETIC-multitrack",
                   "media_path": self.media.name, "source_rights": "owned",
                   "reviewer": "SYNTHETIC reviewer",
                   "manual_review": {gate: "pass" for gate in REQUIRED_REVIEW}}
        self.assertFalse(ingest(spec, receipt, root)["accepted"])
        spec["shots"] = spec["shots"][:1]
        spec["shots"][0].update(source_media=self.media.name, source_rights="owned", duration_s=0.5)
        output = root / "preview.mp4"
        render_preview(spec, root, output, root / "cache")
        pixel = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(output),
                                         "-frames:v", "1", "-vf", "crop=2:2:0:0",
                                         "-pix_fmt", "rgb24", "-f", "rawvideo", "-"])
        self.assertGreater(pixel[0], 200)
        self.assertLess(pixel[2], 30)

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
