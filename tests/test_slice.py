"""SYNTHETIC offline slice integration, including real generated media."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from contf.cli import main
from contf.production_adapter import REQUIRED_REVIEW
from contf.production_jobs import build_jobs
from contf.slice import run_slice
from test_production_jobs import project


class SliceTests(unittest.TestCase):
    def test_invalid_cli_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'SYNTHETIC.json'
            path.write_text('{}')
            with patch.object(sys, 'argv', ['contf', 'slice', str(path), '--out', str(root)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(), 2)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg not installed')
    def test_real_slice_acceptance_reuse_stale_and_null_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = project()
            spec['shots'][0]['duration_s'] = 12
            spec['shots'][1]['duration_s'] = 0.6
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                            'testsrc=size=640x360:rate=12', '-f', 'lavfi', '-i',
                            'sine=frequency=440:sample_rate=44100', '-t', '12',
                            '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt',
                            'yuv420p', '-c:a', 'aac', str(root / 'SYNTHETIC.mp4')], check=True)
            receipt = {'receipt_version': '0.1.0', 'shot_id': 'S01',
                       'fingerprint': build_jobs(spec, root)['jobs'][0]['fingerprint'],
                       'producer': 'SYNTHETIC', 'model_version': 'ffmpeg-testsrc',
                       'media_path': 'SYNTHETIC.mp4', 'source_rights': 'owned',
                       'reviewer': 'SYNTHETIC reviewer',
                       'manual_review': {k: 'pass' for k in REQUIRED_REVIEW},
                       'cost': {'amount': 3, 'currency': 'USD', 'source': 'SYNTHETIC billing'}}
            path = root / 'receipt.json'
            path.write_text(json.dumps(receipt))
            spec_path = root / 'project.json'
            spec_path.write_text(json.dumps(spec))
            argv = ['contf', 'slice', str(spec_path), '--root', str(root),
                    '--out', str(root / 'out'), '--receipt', str(path)]
            with patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(main(), 0)
            first = json.loads(stream.getvalue())
            totals = first['audit']['totals']
            self.assertEqual(totals['counts_by_state'], {'accepted': 1, 'awaiting-human-approval': 1})
            self.assertEqual(totals['known_cost_sum'], 3)
            self.assertEqual(totals['unknown_cost_count'], 1)
            self.assertIsNone(totals['cost_per_accepted_minute'])
            self.assertEqual(first['render']['rendered_count'], 2)
            self.assertGreater((root / 'out' / 'preview.mp4').stat().st_size, 0)
            second = run_slice(spec, root, root / 'out')
            self.assertEqual(second['render']['reused_count'], 2)
            self.assertEqual(second['audit'], first['audit'])
            media = root / 'SYNTHETIC.mp4'
            original = media.read_bytes()
            media.write_bytes(b'SYNTHETIC invalid changed media')
            changed = run_slice(spec, root, root / 'out', no_render=True)
            self.assertEqual(changed['audit']['shots'][0]['state'], 'blocked')
            media.write_bytes(original)
            receipt.pop('cost')
            path.write_text(json.dumps(receipt))
            missing = run_slice(spec, root, root / 'out', receipts=[path], no_render=True)
            self.assertIsNone(missing['audit']['shots'][0]['cost'])
            self.assertEqual(missing['audit']['totals']['unknown_cost_count'], 2)
            receipt['fingerprint'] = 'stale'
            path.write_text(json.dumps(receipt))
            stale = run_slice(spec, root, root / 'out', receipts=[path], no_render=True)
            self.assertTrue(stale['errors'])
            self.assertEqual(stale['audit']['shots'][0]['state'], 'blocked-stale-receipt')
