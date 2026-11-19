"""Synthetic-only unit and optional local FFmpeg smoke tests."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contf.shot_pipeline import compile_plan, render_preview, validate, main  # noqa: E402


def fixture():
    return {
        "schema_version": "0.2.0", "project_id": "synthetic-001",
        "rights": "owned-original", "approval_status": "draft",
        "shots": [
            {
                "shot_id": "S01", "beat": "hook", "duration_s": 0.6,
                "title": "The challenge", "action": "Maya holds a microphone",
                "dialogue": "Three minutes of quiet", "source_media": None,
                "review_status": "pending",
            },
            {
                "shot_id": "S02", "beat": "payoff", "duration_s": 0.6,
                "title": "The response", "action": "Ethan grins",
                "dialogue": "Not a sound", "source_media": None,
                "review_status": "pending",
            },
        ],
    }


class ShotPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="contf-unit-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = fixture()

    def test_timeline_and_provenance(self):
        self.assertEqual(validate(self.project, self.root), [])
        p = compile_plan(self.project, self.root)
        self.assertEqual(p["duration_s"], 1.2)
        self.assertEqual([s["start_s"] for s in p["shots"]], [0.0, 0.6])
        self.assertEqual(p["output_type"], "silent-storyboard-preview")
        self.assertFalse(p["is_final_video"])
        self.assertEqual(p["unapproved_shot_count"], 2)

    def test_stable_cache_and_single_shot_invalidation(self):
        old = compile_plan(self.project, self.root)
        same = compile_plan(copy.deepcopy(self.project), self.root)
        self.assertEqual(old["shots"], same["shots"])
        revised = copy.deepcopy(self.project)
        revised["shots"][1]["dialogue"] = "A new original punchline"
        new = compile_plan(revised, self.root)
        self.assertEqual(old["shots"][0]["cache_key"], new["shots"][0]["cache_key"])
        self.assertNotEqual(old["shots"][1]["cache_key"], new["shots"][1]["cache_key"])

    def test_rejects_unlicensed_project(self):
        self.project["rights"] = "unknown"
        self.assertTrue(validate(self.project, self.root))

    def test_rejects_duplicate_shot_id(self):
        self.project["shots"][1]["shot_id"] = "S01"
        self.assertIn("shots[1].shot_id duplicate", validate(self.project, self.root))

    def test_rejects_path_traversal_and_missing_media(self):
        shot = self.project["shots"][0]
        shot["source_rights"] = "owned"
        for filename in ("../elsewhere.mp4", "/tmp/other.mp4", "missing.mp4"):
            shot["source_media"] = filename
            self.assertTrue(validate(self.project, self.root), filename)

    def test_source_content_changes_cache_key(self):
        media = self.root / "my-owned-clip.mp4"
        media.write_bytes(b"synthetic-content-a")
        shot = self.project["shots"][0]
        shot["source_media"] = media.name
        shot["source_rights"] = "owned"
        key_a = compile_plan(self.project, self.root)["shots"][0]["cache_key"]
        media.write_bytes(b"synthetic-content-b")
        key_b = compile_plan(self.project, self.root)["shots"][0]["cache_key"]
        self.assertNotEqual(key_a, key_b)

    def test_nonfinite_duration_is_rejected(self):
        for value in (float("nan"), float("inf"), True, -1, 91):
            self.project["shots"][0]["duration_s"] = value
            self.assertTrue(validate(self.project, self.root), repr(value))

    def test_cli_validate_and_plan(self):
        project_file = self.root / "project.json"
        project_file.write_text(json.dumps(self.project), encoding="utf-8")
        self.assertEqual(main(["validate", str(project_file), "--root", str(self.root)]), 0)
        self.assertEqual(main(["plan", str(project_file), "--root", str(self.root)]), 0)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not installed")
    def test_single_shot_change_rerenders_only_changed_segment_and_preserves_other_bytes(self):
        """SYNTHETIC: verify actual cached MP4 hashes, not only planned cache keys."""
        import hashlib
        out = self.root / "preview.mp4"
        cache = self.root / "cache"
        first = render_preview(self.project, self.root, out, cache,
                               width=320, height=180, fps=8)
        self.assertEqual(first["rendered_count"], 2)
        old_clips = {
            item["shot_id"]: cache / (item["cache_key"] + ".mp4")
            for item in first["shots"]
        }
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        unchanged_before = digest(old_clips["S01"])
        revised = copy.deepcopy(self.project)
        revised["shots"][1]["dialogue"] = "An original revised line"
        second = render_preview(revised, self.root, out, cache,
                                width=320, height=180, fps=8)
        self.assertEqual(second["rendered_count"], 1, second["shot_actions"])
        self.assertEqual(second["reused_count"], 1, second["shot_actions"])
        self.assertEqual(
            {x["shot_id"]: x["action"] for x in second["shot_actions"]},
            {"S01": "reused", "S02": "rendered"},
        )
        self.assertEqual(digest(old_clips["S01"]), unchanged_before)
        self.assertTrue(old_clips["S02"].exists())
        self.assertNotEqual(first["shots"][1]["cache_key"],
                            second["shots"][1]["cache_key"])
        manifest = json.loads(out.with_suffix(".manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["shot_actions"], second["shot_actions"])
        self.assertFalse(manifest["is_final_video"])
        self.assertEqual(manifest["output_type"], "silent-storyboard-preview")

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not installed")
    def test_real_render_and_local_cache(self):
        out = self.root / "out.mp4"
        cache = self.root / "cache"
        result1 = render_preview(self.project, self.root, out, cache,
                                 width=320, height=180, fps=8)
        self.assertEqual(result1["rendered_count"], 2)
        self.assertTrue(out.stat().st_size > 0)
        self.assertTrue(out.with_suffix(".manifest.json").is_file())
        result2 = render_preview(self.project, self.root, out, cache,
                                 width=320, height=180, fps=8)
        self.assertEqual(result2["reused_count"], 2)
        revised = copy.deepcopy(self.project)
        revised["shots"][0]["title"] = "The revised challenge"
        result3 = render_preview(revised, self.root, out, cache,
                                 width=320, height=180, fps=8)
        self.assertEqual(result3["reused_count"], 1)
        self.assertEqual(result3["rendered_count"], 1)


if __name__ == "__main__":
    unittest.main()
