#!/usr/bin/env python3
"""Independent Python prerequisite controls; no real Git/GitHub commands.

Version tuples are deliberately simulated under the installed interpreter.
No actual Python 3.8, 3.10 or 3.11 interpreter compatibility is claimed.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PUBLICATION_CODE = Path(__file__).resolve().parents[2] / 'publication' / 'code'
sys.path.insert(0, str(PUBLICATION_CODE))
import build_publication as builder
import publication_runtime as runtime
from test_publication import Fixture


class MinimumTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='python-minimum-audit-',
                                               dir=os.environ.get('PUBLICATION_REVIEW_WORK'))
        self.fixture = Fixture(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_rejected_versions_make_no_runtime_commands_or_builder_output(self):
        for version in ((3, 8, 99), (3, 10, 99)):
            publisher, runner = self.fixture.publisher()
            output = self.fixture.directory / ('blocked-' + str(version[1]) + '.sh')
            with mock.patch.object(runtime.sys, 'version_info', version):
                for mode in ('--check', '--self-test', '--dry-run', 'publish'):
                    with self.assertRaisesRegex(runtime.Stop, 'Python 3.11 or newer'):
                        publisher.execute(mode)
                with self.assertRaisesRegex(runtime.Stop, 'Python 3.11 or newer'):
                    builder.build(self.fixture.spec, self.fixture.payload, output)
                with mock.patch.object(runtime.shutil, 'which', side_effect=AssertionError('Prerequisite lookup must not run')):
                    with self.assertRaisesRegex(runtime.Stop, 'Python 3.11 or newer'):
                        runtime.main()
            self.assertEqual(runner.calls, [])
            self.assertEqual(runner.writes, [])
            self.assertFalse(output.exists())

    def test_boundary_and_newer_tuple_allow_only_local_fixture_modes(self):
        for version in ((3, 11, 0), (3, 14, 4)):
            publisher, runner = self.fixture.publisher()
            with mock.patch.object(runtime.sys, 'version_info', version):
                for mode in ('--check', '--self-test'):
                    self.assertEqual(publisher.execute(mode)['mode'], mode)
            self.assertEqual(runner.calls, [])
            self.assertEqual(runner.writes, [])

    def test_generated_help_discloses_same_minimum_as_guard(self):
        script = self.fixture.directory / 'synthetic-help.sh'
        builder.build(self.fixture.spec, self.fixture.payload, script)
        result = subprocess.run(['/usr/bin/bash', str(script), '--help'], cwd='/',
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn(b'Python 3.11+', result.stdout)
        self.assertNotIn(b'Python 3.8+', result.stdout)

    def test_bootstrap_low_version_precedes_even_corrupt_payload(self):
        script = self.fixture.directory / 'synthetic-version-corruption.sh'
        receipt = builder.build(self.fixture.spec, self.fixture.payload, script)
        text = script.read_text()
        self.assertEqual(text.count('mode = sys.argv[1]'), 1)
        text = text.replace('mode = sys.argv[1]', 'sys.version_info = (3, 10, 99)\nmode = sys.argv[1]')
        text = text.replace(receipt['compressed_payload_sha256'], '0' * 64)
        script.write_text(text)
        env = dict(os.environ, TMPDIR=str(self.fixture.directory))
        result = subprocess.run(['/usr/bin/bash', str(script), '--check'], cwd='/',
                                env=env, capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'Python 3.11 or newer is required', result.stdout)
        self.assertIn(b'Workspace/logs retained after failure', result.stdout)
        self.assertNotIn(b'Compressed payload SHA-256 mismatch', result.stdout)
        self.assertNotIn(b'all hashes verified before packaged code', result.stdout)
        logs = list(self.fixture.directory.glob('publication-*/bootstrap.log'))
        self.assertEqual(len(logs), 1)
        self.assertIn('Python 3.11', logs[0].read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
