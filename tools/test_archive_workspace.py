"""Exercise publication policy in disposable local Git repositories."""
import contextlib
import importlib.util
import io
import gzip
import hashlib
import json
import os
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

    def audit(self, staged_only=True, budget_policy=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = ARCHIVE.audit(staged_only=staged_only, budget_policy=budget_policy)
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

    def test_large_ci_registry_is_configuration_only_at_exact_valid_path(self):
        checks = [dict(id=f"check-{i}", group="smoke", command=["{python}", "check.py"],
                       inputs=["check.py"], paths=["tools/**"], timeout_seconds=10,
                       scope="Explicit check scope. " * 60) for i in range(140)]
        content = json.dumps(dict(version=1, checks=checks))
        self.assertGreater(len(content.encode()), 128 * 1024)
        registry = self.write("tools/ci_checks.json", content)
        self.assertIsNone(ARCHIVE.reason(registry))
        for relative in ["tools/other_checks.json", "research/fresh/code/ci_checks.json"]:
            self.assertEqual(ARCHIVE.reason(self.write(relative, content)), "row-level-result-dump")
        malformed = dict(version=1, checks=[dict(value="Execution row. " * 100)] * 140)
        self.assertEqual(ARCHIVE.reason(self.write("tools/ci_checks.json", json.dumps(malformed))),
                         "row-level-result-dump")
        self.write("tools/ci_checks.json", content)
        self.git("add", "--", "tools/ci_checks.json")
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)

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

    def test_static_review_formats_keep_payload_and_size_guards(self):
        for name in ['index.html', 'app.js', 'styles.css', 'data/catalog.json']:
            path = self.write(ARCHIVE.STUDY + '/reviews/atlas/site/' + name, '{}\n')
            self.assertIsNone(ARCHIVE.reason(path))
        payload = self.write(ARCHIVE.STUDY + '/reviews/atlas/site/data/dump.json', '{}\n')
        self.assertEqual(ARCHIVE.reason(payload), 'local-payload-directory')
        oversized = self.write(ARCHIVE.STUDY + '/reviews/atlas/site/app.js', b'x' * (ARCHIVE.MAX_BYTES + 1))
        self.assertEqual(ARCHIVE.reason(oversized), 'large-artifact')
        binary = self.write(ARCHIVE.STUDY + '/reviews/atlas/site/index.html', b'html\x00payload')
        self.assertEqual(ARCHIVE.reason(binary), 'binary-content')

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

    def test_legacy_campaign_patch_attributes_are_durable(self):
        relative = ARCHIVE.STUDY + "/campaigns/golden-swap-phase3-20261007T150955Z/.gitattributes"
        path = self.write(relative, "patches/*.diff -whitespace\n")
        self.assertEqual(subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=self.root).returncode, 1)
        self.assertIsNone(ARCHIVE.reason(path))
        self.git("add", "--", relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)

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

    def test_gzip_raw_text_is_not_ignored_and_expanded_size_is_not_plain_file_limit(self):
        relative = 'research/fresh/evidence/run/raw/rows.json.gz'
        original = json.dumps({'entries': ['measured service'] * 200000}).encode()
        self.assertGreater(len(original), ARCHIVE.MAX_BYTES)
        path = self.write(relative, gzip.compress(original, mtime=0))
        self.assertEqual(subprocess.run(['git', 'check-ignore', '--quiet', relative], cwd=self.root).returncode, 1)
        self.assertIsNone(ARCHIVE.reason(path))
        self.git('add', '--', relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 0, report)
        self.assertEqual(report['staged_content_bytes'], path.stat().st_size)

    def test_gzip_limit_is_exclusive_and_role_is_explicit(self):
        relative = 'research/fresh/evidence/run/large.log.gz'
        size = ARCHIVE.text_evidence.MAX_COMPRESSED_BYTES
        path = self.write(relative, b'x' * size)
        self.assertEqual(ARCHIVE.file_limit(path), size - 1)
        self.git('add', '--', relative)
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, 'large-artifact', relative)
        for other in ['research/fresh/code/log.txt.gz', 'research/fresh/work/evidence/log.txt.gz',
                      'research/fresh/evidence/weights.bin.gz', 'research/fresh/evidence/repos/file.txt.gz']:
            self.assertIsNotNone(ARCHIVE.reason(self.write(other, gzip.compress(b'content', mtime=0))))

    def test_compressed_indexed_credential_crosses_stream_boundary_and_cannot_be_hidden(self):
        relative = 'research/fresh/evidence/run/engine.log.gz'
        token = 'gh' + 'p_' + 'b' * 36
        original = b' ' * (ARCHIVE.text_evidence.CHUNK_BYTES - 2) + token.encode() + b'\n'
        self.write(relative, gzip.compress(original, mtime=0))
        self.git('add', '--', relative)
        self.write(relative, gzip.compress(b'Cleaned worktree.\n', mtime=0))
        status, report, output = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, 'github-token', relative)
        self.assertFinding(report, 'worktree changed after staging', relative)
        self.assertNotIn(token, output)

    def test_gzip_binary_invalid_utf8_corruption_and_truncation_fail(self):
        samples = [(gzip.compress(b'payload\0bytes', mtime=0), 'binary-content'),
                   (gzip.compress(b'bad\xff', mtime=0), 'non-utf8-content'),
                   (gzip.compress(b'utf8 tail\xc3', mtime=0), 'non-utf8-content'),
                   (gzip.compress(b'measurement', mtime=0)[:-3], 'invalid-gzip'),
                   (b'plain text', 'invalid-gzip')]
        damaged = bytearray(gzip.compress(b'measurement', mtime=0));damaged[-8] ^= 1
        samples.append((bytes(damaged), 'invalid-gzip'))
        malformed = bytearray(gzip.compress(b'measurement', mtime=0));malformed[10:14] = b'\xff\xff\xff\xff'
        samples.append((bytes(malformed), 'invalid-gzip'))
        for number, (data, expected) in enumerate(samples):
            path = self.write(f'research/fresh/evidence/run/case{number}.log.gz', data)
            self.assertEqual(ARCHIVE.reason(path), expected)

    def test_gzip_staging_budget_counts_full_compressed_blobs(self):
        # Random bytes represented as valid text provide realistic incompressible logs.
        import random
        rng = random.Random(20261007)
        original = rng.randbytes(7500000).hex().encode()
        data = gzip.compress(original, mtime=0)
        self.assertLess(len(data), ARCHIVE.text_evidence.MAX_COMPRESSED_BYTES)
        self.assertGreater(3 * len(data), ARCHIVE.MAX_STAGED_BYTES)
        for number in range(3):
            self.write(f'research/fresh/evidence/run/log{number}.txt.gz', data)
        self.git('add', '--', 'research/fresh/evidence/')
        status, report, _ = self.audit()
        self.assertEqual(status, 1)
        self.assertFinding(report, 'staged-content-budget')
        self.assertEqual(report['staged_content_bytes'], 3 * len(data))
        policy = self.write('docs/backfill-policy.json', json.dumps({
            'decision': 'Explicit fixture for independent complete evidence files.',
            'max_staged_content_bytes': 64 * ARCHIVE.MAX_BYTES,
            'gzip_evidence_prefixes': ['research/fresh/evidence/run']}))
        self.git('add', '--', 'docs/backfill-policy.json')
        status, report, _ = self.audit(budget_policy=policy)
        self.assertEqual(status, 0, report)
        self.assertEqual(report['staged_content_limit_bytes'], 64 * ARCHIVE.MAX_BYTES)
        self.assertEqual(report['ordinary_staged_content_bytes'], policy.stat().st_size)
        value = json.loads(policy.read_text());value['gzip_evidence_prefixes'] = ['research/other/evidence/run']
        policy.write_text(json.dumps(value));self.git('add', '--', 'docs/backfill-policy.json')
        status, report, _ = self.audit(budget_policy=policy)
        self.assertEqual(status, 1)
        self.assertFinding(report, 'ordinary-staged-content-budget')
        policy.write_text('Unstaged replacement cannot authorize the exception.')
        with self.assertRaisesRegex(ValueError, 'indexed bytes'):
            self.audit(budget_policy=policy)

    def test_pack_is_deterministic_preserves_sources_and_reports_rejections(self):
        source = self.root / 'originals'
        source.mkdir()
        good = self.write('originals/run/output.jsonl', '{"value": 1}\n' * 500)
        bad = self.write('originals/run/nontext.txt', b'bin\0ary')
        self.write('originals/run/tape.bin', b'physical payload')
        self.write('originals/run/.env.txt', 'Private configuration.\n')
        self.write('originals/run/repos/dependency.txt', 'Downloaded dependency.\n')
        (source/'run/link.log').symlink_to(good)
        before = good.read_bytes(), good.stat().st_mtime_ns, bad.read_bytes()
        outputs = [self.root/'research/fresh/evidence/a', self.root/'research/fresh/evidence/b']
        with contextlib.redirect_stdout(io.StringIO()):
            first = ARCHIVE.text_evidence.pack(source, outputs[0], ARCHIVE.SECRETS)
            ARCHIVE.text_evidence.pack(source, outputs[1], ARCHIVE.SECRETS)
        self.assertEqual(first['files_archived'], 1)
        a, b = outputs
        self.assertEqual((a/'run/output.jsonl.gz').read_bytes(), (b/'run/output.jsonl.gz').read_bytes())
        self.assertEqual((a/'archive-manifest.jsonl.gz').read_bytes(), (b/'archive-manifest.jsonl.gz').read_bytes())
        self.assertEqual(gzip.decompress((a/'run/output.jsonl.gz').read_bytes()), before[0])
        self.assertEqual((good.read_bytes(), good.stat().st_mtime_ns, bad.read_bytes()), before)
        records = [json.loads(line) for line in gzip.decompress((a/'archive-manifest.jsonl.gz').read_bytes()).splitlines()]
        archived = next(r for r in records[1:] if r['status'] == 'archived')
        self.assertEqual(archived['original_sha256'], hashlib.sha256(before[0]).hexdigest())
        self.assertTrue({'binary-content', 'non-text-format', 'private-configuration', 'local-symlink',
                         'source-or-environment-directory'} <= set(first['skipped']))
        with self.assertRaises(FileExistsError):
            ARCHIVE.text_evidence.pack(source, a, ARCHIVE.SECRETS)

    def test_pack_never_publishes_partial_or_oversized_compressed_files(self):
        source = self.root/'originals';source.mkdir()
        self.write('originals/large.log', ''.join(chr(33 + n % 80) for n in range(100000)))
        destination = self.root/'research/fresh/evidence/small-cap'
        with patch.object(ARCHIVE.text_evidence, 'MAX_COMPRESSED_BYTES', 80), contextlib.redirect_stdout(io.StringIO()):
            # The manifest also exceeds this artificial cap, so the entire namespace aborts.
            with self.assertRaises(ARCHIVE.text_evidence.TextRejected):
                ARCHIVE.text_evidence.pack(source, destination, ARCHIVE.SECRETS)
        self.assertFalse(destination.exists())
        self.assertTrue((source/'large.log').exists())

    def test_ignored_selection_skips_tracked_data_and_environment_trees(self):
        good = self.write('research/fresh/raw/results.json', '{"value":42}\n')
        owner = self.write('research/fresh/raw/owned-process.json', '{"pid":123,"historical":true}\n')
        tracked = self.write('research/fresh/configs/seed.json', '{"seed":42}\n')
        self.git('add', '--', str(tracked.relative_to(self.root)))
        self.write('research/fresh/repos/dependency.json', '{"upstream":true}\n')
        self.write('research/fresh/envs/cache.json', '{"environment":true}\n')
        selected = ARCHIVE.ignored_text_paths()
        self.assertEqual(set(selected), {str(good.relative_to(self.root)), str(owner.relative_to(self.root))})
        destination = self.root/'docs/evidence/backfill'
        with contextlib.redirect_stdout(io.StringIO()):
            result = ARCHIVE.text_evidence.pack(self.root, destination, ARCHIVE.SECRETS, paths=selected)
        self.assertEqual(result['files_archived'], 2)
        self.assertIsNone(ARCHIVE.reason(destination/'research/fresh/raw/owned-process.json.gz'))
        self.assertTrue(good.exists())

    def test_nonregular_source_is_rejected_without_blocking(self):
        fifo = self.root / 'pipe.log'
        os.mkfifo(fifo)
        with self.assertRaisesRegex(ARCHIVE.text_evidence.TextRejected, 'non-regular-source'):
            ARCHIVE.text_evidence.compress_file(fifo, self.root/'pipe.log.gz', ARCHIVE.SECRETS, lambda: None)
        self.assertFalse((self.root/'pipe.log.gz').exists())

    def test_verify_detects_changed_original_archive_and_unlisted_content(self):
        self.write('originals/run.log', 'Complete text evidence.\n' * 50)
        destination = self.root/'docs/evidence/verified'
        with contextlib.redirect_stdout(io.StringIO()):
            ARCHIVE.text_evidence.pack(self.root/'originals', destination, ARCHIVE.SECRETS)
        self.assertEqual(ARCHIVE.text_evidence.verify(destination, ARCHIVE.SECRETS, True)['files'], 1)
        self.write('originals/run.log', 'Changed original.\n')
        with self.assertRaisesRegex(ValueError, 'Current original differs'):
            ARCHIVE.text_evidence.verify(destination, ARCHIVE.SECRETS, True)
        self.assertEqual(ARCHIVE.text_evidence.verify(destination, ARCHIVE.SECRETS)['state'], 'PASS')
        self.write('docs/evidence/verified/extra.log.gz', gzip.compress(b'Unlisted.\n', mtime=0))
        with self.assertRaisesRegex(ValueError, 'unlisted files'):
            ARCHIVE.text_evidence.verify(destination, ARCHIVE.SECRETS)
        (destination/'extra.log.gz').unlink()
        self.write('docs/evidence/verified/run.log.gz', gzip.compress(b'Replaced.\n', mtime=0))
        with self.assertRaisesRegex(ValueError, 'Compressed identity mismatch'):
            ARCHIVE.text_evidence.verify(destination, ARCHIVE.SECRETS)


if __name__ == "__main__":
    unittest.main()
