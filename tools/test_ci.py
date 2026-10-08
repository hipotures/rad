"""Negative controls for the bounded CI runner; no third-party packages."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import run_ci as ci
from ci_archive_audit import is_workflow


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/"tools").mkdir()
        (self.root/"input.txt").write_text("source\n")
        self.check = dict(id="fixture", group="smoke", command=["{python}", "-c", "print('ok')"],
                          inputs=["input.txt"], paths=["input.txt"], timeout_seconds=5, scope="Runner fixture, not a mathematical theorem")
        self.write()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def write(self, checks=None):
        (self.root/"tools/ci_checks.json").write_text(json.dumps({"version":1,"checks":checks if checks is not None else [self.check]}))

    def invalid(self):
        self.write()
        with self.assertRaises(ValueError):
            ci.load_registry(self.root)

    def test_valid_registry(self):
        self.assertEqual(len(ci.load_registry(self.root)), 1)

    def test_duplicate_ids(self):
        self.write([self.check, self.check])
        with self.assertRaises(ValueError):
            ci.load_registry(self.root)

    def test_duplicate_json_keys(self):
        (self.root/"tools/ci_checks.json").write_text('{"version":1,"version":1,"checks":[]}')
        with self.assertRaises(ValueError):
            ci.load_registry(self.root)

    def test_unknown_fields(self):
        self.check["typo"] = True
        self.invalid()

    def test_unknown_group(self):
        self.check["group"] = "fomal"
        self.invalid()

    def test_empty_command(self):
        self.check["command"] = []
        self.invalid()

    def test_missing_input(self):
        self.check["inputs"] = ["missing.py"]
        self.invalid()

    def test_path_traversal(self):
        self.check["inputs"] = ["../outside.py"]
        self.invalid()

    def test_absolute_path(self):
        self.check["inputs"] = [str(self.root/"input.txt")]
        self.invalid()

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as other:
            path = Path(other)/"outside.txt"
            path.write_text("outside")
            (self.root/"escape").symlink_to(path)
            self.check["inputs"] = ["escape"]
            self.invalid()

    def test_boolean_timeout_rejected(self):
        self.check["timeout_seconds"] = True
        self.invalid()

    def test_excessive_timeout_rejected(self):
        self.check["timeout_seconds"] = 100000
        self.invalid()

    def test_sha_pin(self):
        self.check["sha256"] = {"input.txt": hashlib.sha256(b"source\n").hexdigest()}
        self.write()
        ci.load_registry(self.root)
        (self.root/"input.txt").write_text("tampered")
        with self.assertRaises(ValueError):
            ci.load_registry(self.root)

    def test_affected_paths(self):
        self.assertTrue(ci.selected(self.check, ["input.txt"]))
        self.assertFalse(ci.selected(self.check, ["README.md"]))
        self.assertTrue(ci.selected(self.check, ["README.md"], True))
        self.assertTrue(ci.selected(self.check, None))
        self.assertTrue(ci.selected(self.check, ["tools/ci_checks.json"]))

    def test_no_history_runs_all(self):
        self.assertIsNone(ci.changed_paths(self.root, "0"*40))

    def test_option_injection_rejected(self):
        with self.assertRaises(ValueError):
            ci.changed_paths(self.root, "--output=/tmp/file")

    def test_command_pass(self):
        status, code = ci.run_command(self.check["command"], self.root, 5, self.root/"log")
        self.assertEqual((status, code), ("pass", 0))

    def test_command_fail(self):
        status, code = ci.run_command(["{python}", "-c", "raise SystemExit(7)"], self.root, 5, self.root/"log")
        self.assertEqual((status, code), ("fail", 7))

    def test_timeout(self):
        status, code = ci.run_command(["{python}", "-c", "import time; time.sleep(20)"], self.root, 1, self.root/"log")
        self.assertEqual((status, code), ("timeout", None))

    def test_empty_group_not_verified(self):
        with self.assertRaises(ValueError):
            ci.execute("formal", self.root, self.root/"out", None, True)

    def test_evidence_overwrite_rejected(self):
        (self.root/"out").mkdir()
        with self.assertRaises(ValueError):
            ci.execute("smoke", self.root, self.root/"out", None, True)

    def test_failed_check_produces_failed_report(self):
        self.check["command"] = ["{python}", "-c", "raise SystemExit(2)"]
        self.write()
        code = ci.execute("smoke", self.root, self.root/"out", None, True)
        report = json.loads((self.root/"out/report.json").read_text())
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["checks"][0]["exit_code"], 2)

    def test_unaffected_check_is_not_a_pass(self):
        code = ci.execute("smoke", self.root, self.root/"out", ["README.md"], False)
        report = json.loads((self.root/"out/report.json").read_text())
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "skipped-unaffected")

    def test_successful_report_records_input_hash(self):
        code = ci.execute("smoke", self.root, self.root/"out", None, True)
        report = json.loads((self.root/"out/report.json").read_text())
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["checks"][0]["inputs_sha256"]["input.txt"], hashlib.sha256(b"source\n").hexdigest())

    def test_workflow_exception_is_narrow(self):
        self.assertTrue(is_workflow(Path(".github/workflows/verify.yml")))
        self.assertFalse(is_workflow(Path(".github/actions/local.py")))
        self.assertFalse(is_workflow(Path(".github/workflows/private.key")))
        self.assertFalse(is_workflow(Path(".github/workflows/nested/x.yml")))


if __name__ == "__main__":
    unittest.main()
