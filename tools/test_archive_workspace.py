"""Exercise publication policy in disposable local Git repositories."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import import_external_workspaces as importer


REPOSITORY = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("archive_workspace", REPOSITORY / "tools/archive_workspace.py")
ARCHIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARCHIVE)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rad-publication-test-")
        self.root = Path(self.temp.name)
        self.previous_root = ARCHIVE.ROOT
        ARCHIVE.ROOT = self.root
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(setattr, ARCHIVE, "ROOT", self.previous_root)
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "user.name", "Publication Test")
        self.git("config", "user.email", "publication-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", "/dev/null")
        self.write(".gitignore", (REPOSITORY / ".gitignore").read_text())
        self.write("README.md", "Baseline repository.\n")
        self.git("add", "--", ".gitignore", "README.md")
        self.git("commit", "--quiet", "-m", "Create isolated policy fixture")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content)
        return path

    def audit(self, staged_only=True):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = ARCHIVE.audit(staged_only=staged_only)
        report = json.loads((self.root / "storage/publication-audit.json").read_text())
        return status, report, output.getvalue()

    def assertFinding(self, report, category, path=None):
        self.assertTrue(any(f["reason"] == category and (path is None or f.get("path") == path)
                            for f in report["failures"]), report["failures"])

    def test_authored_source_allowed_and_execution_directories_ignored(self):
        for name in ["main.py", "main.rs", "main.go", "main.ts", "requirements.lock", "Dockerfile"]:
            relative = "research/fresh/code/" + name
            self.write(relative, "# Small authored source/configuration.\n")
            result = subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=self.root)
            self.assertEqual(result.returncode, 1, relative)
            self.assertIsNone(ARCHIVE.reason(self.root / relative))
        for directory in ["work", "downloads", "repos", "builds", "envs", "raw", "logs",
                          "tmp", "derived", "dist", "target", "inputs", "src"]:
            relative = "research/fresh/" + directory + "/payload.py"
            self.write(relative, "Execution payload.\n")
            result = subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=self.root)
            self.assertEqual(result.returncode, 0, relative)
            self.assertIsNotNone(ARCHIVE.reason(self.root / relative))
        self.git("add", "--", "research/fresh/code/")
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)
        self.assertEqual(report["files"], 6)

    def test_staged_only_preserves_unrelated_unstaged_edits(self):
        self.write("research/fresh/code/main.py", "print('durable work')\n")
        self.git("add", "--", "research/fresh/code/main.py")
        unrelated = "Unrelated work remains unstaged.\n"
        self.write("README.md", unrelated)
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)
        self.assertEqual(report["selection"], "staged-changes")
        self.assertEqual(report["files"], 1)
        self.assertEqual((self.root / "README.md").read_text(), unrelated)
        self.assertEqual(self.git("diff", "--cached", "--name-only").strip(), "research/fresh/code/main.py")
        status, report, _ = self.audit(staged_only=False)
        self.assertEqual(status, 1)
        self.assertFinding(report, "worktree changed after staging", "README.md")

    def test_new_formats_do_not_change_legacy_import_selection(self):
        for name in ["reference.html", "query.sql", ".gitattributes"]:
            relative = ARCHIVE.STUDY + "/sources/" + name
            path = self.write(relative, "Previously local-only legacy material.\n")
            result = subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=self.root)
            self.assertEqual(result.returncode, 0, relative)
            self.assertEqual(ARCHIVE.reason(path), "non-durable-format")

    def test_benchmark_source_and_user_launchers_are_durable(self):
        for relative in ["benchmarks/qwen-hardware-characterization/src/hwbench.cu",
                         "benchmarks/qwen-hardware-characterization/run-example/code-final/src/operations.cu",
                         "benchmarks/campaign/report.md", "benchmarks/campaign/raw/reference.md",
                         "launchers/user/start-128k.sh", "launchers/user/configs/128k.json"]:
            path = self.write(relative, "Small durable source or reference.\n")
            result = subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=self.root)
            self.assertEqual(result.returncode, 1, relative)
            self.assertIsNone(ARCHIVE.reason(path))
            self.git("add", "--", relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)
        for relative in ["launchers/user/logs/engine.log", "benchmarks/campaign/samples/telemetry.jsonl",
                         "benchmarks/campaign/raw/dump.json", "benchmarks/campaign/repos/checkout.py"]:
            path = self.write(relative, "Disposable execution payload.\n")
            result = subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=self.root)
            self.assertEqual(result.returncode, 0, relative)
            self.assertIsNotNone(ARCHIVE.reason(path))

    def test_portable_root_report_shortcuts_are_tracked(self):
        for name in sorted(n for n in ARCHIVE.ROOT_FILES if n.startswith("QWEN38_")):
            path = self.write(name, "[Preserved report](benchmarks/study/REPORT.md)\n")
            result = subprocess.run(["git", "check-ignore", "--quiet", name], cwd=self.root)
            self.assertEqual(result.returncode, 1, name)
            self.assertIsNone(ARCHIVE.reason(path))

    def test_external_import_preserves_originals_and_refuses_overwrite(self):
        source = self.root / "source-fixtures"
        bench = source / "benchmarks"
        launchers = source / "launchers"
        bench.mkdir(parents=True)
        launchers.mkdir()
        report = self.write("source-fixtures/benchmarks/study/report.md", "Historical evidence.\n")
        payload = self.write("source-fixtures/benchmarks/study/oversized.txt", "x" * (ARCHIVE.MAX_BYTES + 1))
        self.write("source-fixtures/benchmarks/study/raw/dump.json", '{"raw": true}\n')
        starter = self.write("source-fixtures/launchers/user/start-128k.sh", "#!/usr/bin/env bash\nexit 0\n")
        starter.chmod(0o755)
        with patch.multiple(importer, ROOT=self.root, CATALOG=self.root / "docs/external-workspaces.json",
                            SOURCES={"benchmarks": bench, "launchers": launchers}), \
             patch.object(importer.archive, "ROOT", self.root), patch.object(importer, "aliases", return_value=[]):
            selected, excluded, exports = importer.plan()
            self.assertEqual(len(selected), 2)
            self.assertTrue(any(r["reason"] == "large-artifact" for r in excluded))
            importer.copy(selected, excluded, exports)
            self.assertEqual((self.root / "benchmarks/study/report.md").read_bytes(), report.read_bytes())
            self.assertTrue((self.root / "launchers/user/start-128k.sh").stat().st_mode & 0o111)
            self.assertFalse((self.root / "benchmarks/study/oversized.txt").exists())
            self.assertTrue(payload.is_file())
            with contextlib.redirect_stdout(io.StringIO()):
                importer.verify()
            self.write("benchmarks/study/report.md", "Unrelated edit to preserve.\n")
            with self.assertRaisesRegex(RuntimeError, "Preserve different existing destination"):
                importer.copy(selected, excluded, exports)
            self.assertEqual((self.root / "benchmarks/study/report.md").read_text(), "Unrelated edit to preserve.\n")
            self.assertEqual(report.read_text(), "Historical evidence.\n")

    def test_force_added_work_payload_fails(self):
        relative = "research/fresh/work/checkout.py"
        self.write(relative, "Small but disposable downloaded source.\n")
        self.git("add", "-f", "--", relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, "local-directory:work", relative)

    def test_indexed_credential_is_found_even_if_worktree_is_cleaned(self):
        relative = "research/fresh/configs/example.txt"
        token = "gh" + "p_" + "a" * 36
        self.write(relative, token + "\n")
        self.git("add", "--", relative)
        self.write(relative, "No credential in the current worktree.\n")
        status, report, output = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, "github-token", relative)
        self.assertFinding(report, "worktree changed after staging", relative)
        self.assertNotIn(token, output)

    def test_binary_disguised_as_text_fails(self):
        relative = "research/fresh/runs/test/results/output.txt"
        self.write(relative, b"binary\0payload")
        self.git("add", "--", relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, "binary-content", relative)

    def test_oversized_indexed_blob_cannot_be_hidden_by_smaller_worktree(self):
        relative = "research/fresh/code/dependency.patch"
        size = 4 * ARCHIVE.MAX_BYTES + 1
        self.write(relative, "x" * size)
        self.git("add", "--", relative)
        self.write(relative, "Small replacement.\n")
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, "large-artifact", relative)
        self.assertEqual(report["staged_content_bytes"], size)

    def test_many_individually_small_files_exceed_commit_budget(self):
        content = "x" * (ARCHIVE.MAX_BYTES - 1) + "\n"
        for number in range(21):
            self.write(f"research/fresh/runs/test/results/part-{number}.txt", content)
        self.git("add", "--", "research/fresh/runs/test/results/")
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertEqual(report["staged_content_bytes"], 21 * ARCHIVE.MAX_BYTES)
        self.assertEqual([f["reason"] for f in report["failures"]], ["staged-content-budget"])

    def test_symlink_and_nested_gitlink_fail(self):
        target = self.write("external-data.txt", "Local payload.\n")
        link = self.root / "research/fresh/code/link.py"
        link.parent.mkdir(parents=True)
        link.symlink_to(target)
        self.git("add", "--", "research/fresh/code/link.py")
        head = self.git("rev-parse", "HEAD").strip()
        self.git("update-index", "--add", "--cacheinfo", f"160000,{head},research/fresh/checkout")
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        for relative in ["research/fresh/code/link.py", "research/fresh/checkout"]:
            self.assertFinding(report, "symlink, nested repository or unmerged index", relative)

    def test_notebook_outputs_must_be_cleared(self):
        relative = "research/fresh/code/analysis.ipynb"
        cell = {"cell_type": "code", "source": ["print(1)"], "outputs": [{"text": ["1"]}], "execution_count": 1}
        self.write(relative, json.dumps({"cells": [cell]}))
        self.git("add", "--", relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, "notebook-execution-payload", relative)
        cell.update(outputs=[], execution_count=None)
        self.write(relative, json.dumps({"cells": [cell]}))
        self.git("add", "--", relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)

    def test_deleted_worktree_file_is_reported_without_crashing(self):
        relative = "research/fresh/code/main.py"
        path = self.write(relative, "print('staged')\n")
        self.git("add", "--", relative)
        path.unlink()
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, "worktree changed after staging", relative)

    def test_staged_deletion_and_empty_index_change_are_supported(self):
        self.git("rm", "--quiet", "--", "README.md")
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)
        self.assertEqual(report["files"], 0)
        self.assertEqual(report["staged_content_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
