#!/usr/bin/env python3
"""Synthetic local tests. GitHub and publication commands are never executed.

Only Bash syntax and generated --check/--self-test paths run as subprocesses.
Every publication-control-flow test injects FakeRunner before it starts.
"""
import base64
import copy
import contextlib
import gzip
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest import mock as unittest_mock
from pathlib import Path
from fractions import Fraction

import build_publication as builder
import publication_runtime as runtime


def data_digest(data):
    return runtime.digest(data)


def source(repo, ref, path, data, pointer="/kappa"):
    return {"repository": repo, "ref": ref, "path": path,
            "decoded_sha256": data_digest(data), "value_pointer": pointer}


class Fixture:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.base = self.directory / "base"
        self.payload = self.directory / "payload"
        self.package = self.directory / "package"
        self.workspace = self.directory / "workspace"
        for path in (self.base, self.payload, self.package, self.workspace):
            path.mkdir()
        (self.base / "tests").mkdir()
        (self.base / "tests/inherited.py").write_text("# synthetic inherited test\n")
        (self.base / "LICENSE").write_text("Synthetic test license only.\n")
        (self.base / "formula.py").write_text("# unchanged synthetic mathematics\n")
        name = "certificates/synthetic.json"
        (self.payload / "certificates").mkdir()
        candidate = b'{"kappa":"3/5000","synthetic":true}\n'
        (self.payload / name).write_bytes(candidate)
        self.base_sha, self.claim_sha, self.submit_sha = "1" * 40, "2" * 40, "9" * 40
        public = b'{"kappa":"1/2000"}\n'
        retained = b'{"kappa":"1/2500"}\n'
        self.certificates = {
            ("reviewer/integer-mult-bounds", self.claim_sha, "certificates/current.json"): public,
            (runtime.UPSTREAM, self.base_sha, "certificates/retained.json"): retained,
        }
        self.pr = {"number": 101, "title": "Synthetic conditional claim", "body": "Synthetic body",
                   "state": "open", "draft": True, "merged_at": None,
                   "head": {"sha": self.claim_sha, "repo": {"full_name": "reviewer/integer-mult-bounds"}},
                   "base": {"repo": {"full_name": runtime.UPSTREAM}, "ref": "main"},
                   "user": {"login": "reviewer"},
                   "html_url": f"https://github.com/{runtime.UPSTREAM}/pull/101"}
        rule = {"pr": 101, "head_sha": self.claim_sha,
                "body_sha256": data_digest(self.pr["body"].encode()),
                "title_sha256": data_digest(self.pr["title"].encode()),
                "exact_kappa": "1/2000", "certified_upper_bound": None, "excluded": False,
                "assessment_scope": "Synthetic exact certificate fixture",
                "certificate_source": source("reviewer/integer-mult-bounds", self.claim_sha,
                                             "certificates/current.json", public)}
        self.spec = {
            "upstream": runtime.UPSTREAM, "candidate_id": "synthetic-fixture",
            "candidate_digest": "7" * 64, "default_branch": "main", "base_sha": self.base_sha,
            "exact_kappa": "3/5000", "status": "ACCEPTED_CONDITIONAL", "freeze_approved": True,
            "minimum_relative_improvement": "1/100",
            "synthetic_test_only": True, "gates": {gate: True for gate in builder.REQUIRED_GATES},
            "source_fingerprints": {"formula.py": data_digest((self.base / "formula.py").read_bytes())},
            "protected_base_paths": {name: data_digest((self.base / name).read_bytes())
                                     for name in ("tests/inherited.py", "LICENSE")},
            "changes": [{"path": name, "sha256": data_digest(candidate),
                         "mode": 0o644, "before_sha256": None}],
            "local_checks": [{"command": ["python3", "tests/inherited.py"], "timeout_seconds": 5}],
            "frontier_rules": {"upstream": runtime.UPSTREAM, "base_sha": self.base_sha,
                               "default_branch": "main", "open_count": 1,
                               "claims": [rule], "retained_main": {
                                   "exact_kappa": "1/2500", "certificate_sources": [source(
                                       runtime.UPSTREAM, self.base_sha, "certificates/retained.json", retained)]}},
            "title": "Synthetic conditional fixture; never a real publication",
            "commit_message": "Record synthetic mock candidate",
            "public_text": {key: "Synthetic fixture; no scientific claim." for key in (
                "construction_change", "predecessor", "verification_scope", "reproduction",
                "conditional_assumptions", "exclusions", "attribution", "license_notes",
                "source_inventory", "ai_assistance")},
        }
        self.spec["public_text"]["predecessor_kappa"] = "1/2000"
        self.spec["prepared_body"] = builder.prepared_body(self.spec)
        self.persist()

    def persist(self):
        (self.package / "manifest.json").write_text(json.dumps({"release": self.spec}))
        target = self.package / "files"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(self.payload, target)

    def publisher(self):
        self.persist()
        checkout = self.workspace / "upstream"
        if checkout.exists():
            shutil.rmtree(checkout)  # Disposable synthetic fixture only.
        backend = FakeRunner(self)
        pub = runtime.Publisher(self.package, self.workspace, backend)
        # This isolated in-memory object cannot call subprocesses: FakeRunner
        # implements every command and rejects anything not explicitly mocked.
        pub.spec["synthetic_test_only"] = False
        backend.publisher = pub
        return pub, backend


class FakeRunner:
    """Fake Git/GitHub only. No subprocess invocation exists in this class."""
    def __init__(self, fixture):
        self.fixture = fixture
        self.publisher = None
        self.calls, self.messages, self.writes = [], [], []
        self.prs, self.closed = [copy.deepcopy(fixture.pr)], []
        self.certificates = copy.deepcopy(fixture.certificates)
        self.current_base = fixture.base_sha
        self.committed = False
        self.remote_commit = None
        self.fork_exists = True
        self.fail_prefix = None
        self.bad_remote = False
        self.frontier_reads = 0
        self.mutate_final = False
        self.large_files = set()
        self.foreign_fork = False
        self.extra_staged_path = None
        self.extra_prfile = None
        self.on_check_extra_staged = None
        self.index_blobs = {}
        self.index_modes = {}
        self.untracked = b""
        self.remote_mode_mutation = False
        self.rewrite_remote = False

    def note(self, message):
        self.messages.append(message)

    def run(self, args, *, cwd=None, network=False, write=False, timeout=45):
        self.calls.append(args)
        if write:
            self.writes.append(args)
        if self.fail_prefix and args[:len(self.fail_prefix)] == self.fail_prefix:
            raise runtime.CommandFailure(args, 42, "Synthetic command failure")
        if args[:5] == ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false"]:
            args = ["git", *args[5:]]
        if args[:3] == ["gh", "auth", "status"]:
            return b"Synthetic authentication; no real account queried\n"
        if args[:2] == ["gh", "api"]:
            endpoint = args[2]
            if endpoint == "user":
                value = {"login": "fixture-user"}
            elif endpoint == f"repos/{runtime.UPSTREAM}":
                value = {"full_name": runtime.UPSTREAM, "default_branch": "main"}
            elif endpoint == f"repos/{runtime.UPSTREAM}/commits/main":
                value = {"sha": self.current_base}
            elif endpoint.startswith(f"repos/{runtime.UPSTREAM}/pulls?"):
                state = "open" if "state=open" in endpoint else "closed"
                page = int(endpoint.rsplit("page=", 1)[1])
                if state == "open" and page == 1:
                    self.frontier_reads += 1
                    if self.mutate_final and self.frontier_reads == 2:
                        self.prs[0]["body"] = "Changed during synthetic final check"
                values = self.prs if state == "open" else self.closed
                value = values[(page - 1) * 100:page * 100]
            elif re.match(rf"repos/{runtime.UPSTREAM}/pulls/[0-9]+/files\?", endpoint):
                value = [{"filename": item["path"], "status": "added"}
                         for item in self.publisher.spec["changes"]]
                if self.extra_prfile:
                    value.append({"filename": self.extra_prfile, "status": "modified"})
            elif re.fullmatch(rf"repos/{runtime.UPSTREAM}/pulls/[0-9]+", endpoint):
                number = int(endpoint.rsplit("/", 1)[1])
                value = next(item for item in self.prs + self.closed if item["number"] == number)
            elif "/git/commits/" in endpoint:
                value = {"tree": {"sha": "6" * 40}}
            elif "/git/trees/" in endpoint:
                value = {"truncated": False, "tree": [
                    {"path": item["path"], "type": "blob", "mode": "100755" if
                     self.remote_mode_mutation or item["mode"] == 0o755 else "100644"}
                    for item in self.publisher.spec["changes"]]}
            elif "/contents/" in endpoint:
                repository, tail = endpoint[6:].split("/contents/", 1)
                path, ref = tail.rsplit("?ref=", 1)
                key = (repository, ref, path)
                if key not in self.certificates:
                    raise runtime.CommandFailure(args, 1, "HTTP 404 synthetic missing source")
                data = self.certificates[key]
                if "-H" in args:
                    return data
                value = ({"encoding": "none", "type": "file", "content": ""} if key in self.large_files
                         else {"encoding": "base64", "type": "file", "content": base64.b64encode(data).decode()})
            elif endpoint == "repos/fixture-user/integer-mult-bounds":
                if not self.fork_exists:
                    raise runtime.CommandFailure(args, 1, "HTTP 404 synthetic missing fork")
                value = {"full_name": "fixture-user/integer-mult-bounds", "fork": True,
                         "owner": {"login": "fixture-user"}, "parent": {
                             "full_name": "foreign/repository" if self.foreign_fork else runtime.UPSTREAM}}
            else:
                raise AssertionError("Unmocked GitHub endpoint: " + endpoint)
            return json.dumps(value).encode()
        if args[:3] == ["gh", "repo", "fork"]:
            self.fork_exists = True
            return b"Synthetic fork created only in memory\n"
        if args[:3] == ["gh", "pr", "create"]:
            assert "--draft" not in args
            return f"https://github.com/{runtime.UPSTREAM}/pull/999\n".encode()
        if args[:2] == ["git", "clone"]:
            shutil.copytree(self.fixture.base, self.publisher.repo)
            return b"Synthetic clone copied only local fixture files\n"
        if args[:3] == ["git", "rev-parse", "HEAD"]:
            return (self.fixture.submit_sha if self.committed else self.fixture.base_sha).encode() + b"\n"
        if args[:2] == ["git", "commit"]:
            self.committed = True
            return b"Synthetic local commit only in memory\n"
        if args[:2] == ["git", "ls-remote"]:
            if self.remote_commit:
                sha = "0" * 40 if self.bad_remote else self.remote_commit
                return f"{sha}\t{args[-1]}\n".encode()
            return b""
        if args[:2] == ["git", "push"]:
            self.remote_commit = self.fixture.submit_sha
            for item in self.publisher.spec["changes"]:
                self.certificates[("fixture-user/integer-mult-bounds", self.fixture.submit_sha,
                                   item["path"])] = (self.publisher.repo / item["path"]).read_bytes()
            for name in {**self.publisher.spec["source_fingerprints"], **self.publisher.spec["protected_base_paths"]}:
                self.certificates[("fixture-user/integer-mult-bounds", self.fixture.submit_sha,
                                   name)] = (self.publisher.repo / name).read_bytes()
            return b"Synthetic remote push only in memory\n"
        if args[:2] == ["git", "diff"]:
            changed = "--cached" in args or "HEAD" in args
            if changed and "--name-only" in args:
                names = [item["path"] for item in self.publisher.spec["changes"]]
                if self.extra_staged_path:
                    names.append(self.extra_staged_path)
                return b"\x00".join(name.encode() for name in names) + b"\x00"
            if changed and "--name-status" in args:
                return b"\x00".join(b"A\x00" + item["path"].encode()
                                      for item in self.publisher.spec["changes"]) + b"\x00"
            return b""
        if args[:2] == ["git", "ls-files"]:
            if "--others" in args:
                return self.untracked
            name = args[-1]
            item = next(item for item in self.publisher.spec["changes"] if item["path"] == name)
            mode = self.index_modes.get(name, "100755" if item["mode"] == 0o755 else "100644")
            return f"{mode} {'6' * 40} 0\t{name}\x00".encode()
        if args[:2] == ["git", "ls-tree"]:
            name = args[-1]
            item = next(item for item in self.publisher.spec["changes"] if item["path"] == name)
            mode = "100755" if item["mode"] == 0o755 else "100644"
            return f"{mode} blob {'6' * 40}\t{name}\x00".encode()
        if args[:2] == ["git", "show"]:
            name = args[-1].split(":", 1)[1]
            return self.index_blobs.get(name, (self.publisher.repo / name).read_bytes())
        if args[:3] == ["git", "remote", "get-url"]:
            return (f"https://github.com/{runtime.UPSTREAM}.git" if self.rewrite_remote else
                    "https://github.com/fixture-user/integer-mult-bounds.git").encode()
        if args[:2] in (["git", "add"], ["git", "update-index"], ["git", "config"],
                        ["git", "checkout"], ["git", "remote"]):
            return b""
        if args[0] == "python3":
            if self.on_check_extra_staged:
                self.extra_staged_path = self.on_check_extra_staged
            return b"Synthetic local check result only\n"
        raise AssertionError("Unmocked command (never executed): " + repr(args))


class PublicationTests(unittest.TestCase):
    def setUp(self):
        root = os.environ.get("PUBLICATION_TEST_WORK")
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-", dir=root)
        self.fixture = Fixture(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def script(self):
        output = self.fixture.directory / "synthetic_publish.sh"
        receipt = builder.build(self.fixture.spec, self.fixture.payload, output)
        return output, receipt

    def run_local(self, script, mode="--check", env=None):
        env = dict(os.environ if env is None else env, TMPDIR=str(self.fixture.directory))
        return subprocess.run(["/usr/bin/bash", str(script), mode], cwd="/", env=env,
                              capture_output=True, timeout=15)

    def mutated_archive(self, script, receipt, mutate):
        shell = script.read_text()
        encoded = re.search(r'encoded = """(.*?)"""', shell, re.S).group(1)
        raw = base64.b64decode("".join(encoded.split()))
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
            entries = [(entry.name, archive.extractfile(entry).read(), entry.mode) for entry in archive]
        entries = mutate(entries)
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode="w:gz") as archive:
            for member in entries:
                name, data, mode = member[:3]
                item = tarfile.TarInfo(name)
                item.size, item.mode = len(data), mode
                if len(member) == 4:
                    item.type, item.linkname = member[3], "../escape"
                archive.addfile(item, io.BytesIO(data))
        new = out.getvalue()
        shell = shell.replace(encoded, base64.b64encode(new).decode())
        shell = shell.replace(receipt["compressed_payload_sha256"], data_digest(new))
        script.write_text(shell)

    def test_shell_syntax_arbitrary_cwd_and_local_checks(self):
        script, _ = self.script()
        syntax = subprocess.run(["bash", "-n", str(script)], capture_output=True, timeout=10)
        self.assertEqual(syntax.returncode, 0, syntax.stderr)
        for mode in ("--check", "--self-test"):
            result = self.run_local(script, mode)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(b"all hashes verified before packaged code", result.stdout)
            self.assertIn(b"no GitHub requests or writes made", result.stdout)

    def test_synthetic_cli_publication_network_path_blocked(self):
        script, _ = self.script()
        result = self.run_local(script, "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Synthetic fixture cannot", result.stdout)

    def test_missing_dependency(self):
        script, _ = self.script()
        path = self.fixture.directory / "minimal-bin"
        path.mkdir()
        for name in ("bash", "git", "python3"):
            (path / name).symlink_to(shutil.which(name))
        env = dict(os.environ, PATH=str(path))
        result = self.run_local(script, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Missing prerequisite: gh", result.stdout + result.stderr)

    def test_compressed_hash_corruption(self):
        script, receipt = self.script()
        script.write_text(script.read_text().replace(receipt["compressed_payload_sha256"], "0" * 64))
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Compressed payload SHA-256 mismatch", result.stdout)

    def test_archive_traversal_is_rejected_before_execution(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries: entries + [("../escape", b"bad", 0o644)])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Unsafe archive member", result.stdout)

    def test_duplicate_archive_members_are_rejected(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries: entries + [entries[-1]])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Duplicate archive member", result.stdout)

    def test_archive_symbolic_link_is_rejected(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries:
                             entries + [("files/link", b"", 0o644, tarfile.SYMTYPE)])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Unsafe archive member", result.stdout)

    def test_archive_oversize_member_is_rejected(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries:
                             entries + [("files/large", b"x" * (1048576 + 1), 0o644)])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Unsafe archive member", result.stdout)

    def test_archive_unallowlisted_member_is_rejected(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries:
                             entries + [("files/unrelated.py", b"# unrelated", 0o644)])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Archive member allowlist mismatch", result.stdout)

    def test_manifest_hash_mismatch_is_rejected(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries: [
            (name, data + b" " if name == "manifest.json" else data, mode)
            for name, data, mode in entries])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Manifest SHA-256 mismatch", result.stdout)

    def test_member_hash_mismatch_is_rejected(self):
        script, receipt = self.script()
        self.mutated_archive(script, receipt, lambda entries: [
            (name, data + b"corruption" if name == "publication_runtime.py" else data, mode)
            for name, data, mode in entries])
        result = self.run_local(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Member SHA-256/size mismatch", result.stdout)

    def test_builder_refuses_unfrozen_or_incomplete_release(self):
        self.fixture.spec["synthetic_test_only"] = False
        for status in ("DISCOVERY", "EXACT_FINITE"):
            self.fixture.spec["status"] = status
            with self.assertRaises(runtime.Stop):
                self.script()
        self.fixture.spec["status"] = "ACCEPTED_CONDITIONAL"
        self.fixture.spec["gates"]["independent_reproduction"] = False
        with self.assertRaises(runtime.Stop):
            self.script()

    def test_builder_output_is_immutable(self):
        self.script()
        with self.assertRaises(runtime.Stop):
            self.script()

    def test_builder_protects_inherited_tests(self):
        item = copy.deepcopy(self.fixture.spec["changes"][0])
        item["path"] = "tests/inherited.py"
        self.fixture.spec["changes"] = [item]
        with self.assertRaises(runtime.Stop):
            self.script()

    def test_builder_rejects_inline_or_unpinned_check_code(self):
        for command in (["python3", "-c", "print('unhashed')"], ["python3", "unlisted.py"]):
            self.fixture.spec["local_checks"][0]["command"] = command
            with self.assertRaisesRegex(runtime.Stop, "declared, hashed Python file"):
                self.script()

    def test_mock_dry_run_has_no_github_mutations(self):
        pub, mock = self.fixture.publisher()
        result = pub.execute("--dry-run")
        self.assertEqual(result["mode"], "--dry-run")
        self.assertEqual(mock.writes, [])
        self.assertFalse(any(call[:3] == ["gh", "repo", "fork"] for call in mock.calls))

    def test_mock_publication_returns_actual_mock_url_and_commit(self):
        pub, mock = self.fixture.publisher()
        mock.fork_exists = False
        result = pub.execute("publish")
        self.assertEqual(result["url"], f"https://github.com/{runtime.UPSTREAM}/pull/999")
        self.assertEqual(result["commit"], self.fixture.submit_sha)
        self.assertEqual([call[:3] for call in mock.writes],
                         [["gh", "repo", "fork"], ["git", "push", "--porcelain"], ["gh", "pr", "create"]])
        self.assertEqual(mock.frontier_reads, 2)

    def test_wrong_upstream_base_stops_before_mutations(self):
        pub, mock = self.fixture.publisher()
        mock.current_base = "3" * 40
        with self.assertRaisesRegex(runtime.Stop, "base changed"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_api_failure_stops_before_mutations(self):
        pub, mock = self.fixture.publisher()
        mock.fail_prefix = ["gh", "api", f"repos/{runtime.UPSTREAM}"]
        with self.assertRaises(runtime.CommandFailure):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_stale_head_body_and_title_stop(self):
        for field in ("head", "body", "title"):
            pub, mock = self.fixture.publisher()
            if field == "head":
                mock.prs[0]["head"]["sha"] = "4" * 40
            else:
                mock.prs[0][field] += " changed"
            with self.assertRaisesRegex(runtime.Stop, "changed"):
                pub.execute("publish")
            self.assertEqual(mock.writes, [])

    def test_equal_and_better_public_scores_stop(self):
        for value in ("3/5000", "7/10000"):
            pub, mock = self.fixture.publisher()
            cert = (json.dumps({"kappa": value}) + "\n").encode()
            rule = pub.spec["frontier_rules"]["claims"][0]
            rule["exact_kappa"] = value
            rule["certificate_source"]["decoded_sha256"] = data_digest(cert)
            mock.certificates[("reviewer/integer-mult-bounds", self.fixture.claim_sha,
                               "certificates/current.json")] = cert
            with self.assertRaisesRegex(runtime.Stop, "does not strictly beat"):
                pub.execute("publish")
            self.assertEqual(mock.writes, [])

    def test_exact_one_percent_boundary_below_equal_above(self):
        required = Fraction(101, 100) * Fraction(1, 2000)
        for offset in (-Fraction(1, 10**12), Fraction(0), Fraction(1, 10**12)):
            pub, mock = self.fixture.publisher()
            pub.spec["exact_kappa"] = str(required + offset)
            if offset < 0:
                with self.assertRaisesRegex(runtime.Stop, "below the exact 1%"):
                    pub.frontier(mock.prs)
            else:
                result = pub.frontier(mock.prs)
                self.assertEqual(result["minimum_required_kappa"], str(required))
                self.assertEqual(result["minimum_relative_improvement"], "1/100")
            self.assertEqual(mock.writes, [])

    def test_builder_exact_one_percent_boundary(self):
        required = Fraction(101, 100) * Fraction(1, 2000)
        for offset in (-Fraction(1, 10**12), Fraction(0), Fraction(1, 10**12)):
            spec = copy.deepcopy(self.fixture.spec)
            spec["exact_kappa"] = str(required + offset)
            if offset < 0:
                with self.assertRaisesRegex(runtime.Stop, "below the exact 1%"):
                    builder.validate_spec(spec, self.fixture.payload)
            else:
                builder.validate_spec(spec, self.fixture.payload)

    def test_publication_policy_cannot_be_missing_or_weakened(self):
        for value in (None, "0", "1/1000", "2/200"):
            spec = copy.deepcopy(self.fixture.spec)
            spec["minimum_relative_improvement"] = value
            with self.assertRaisesRegex(runtime.Stop, "immutably require at least 1%"):
                builder.validate_spec(spec, self.fixture.payload)
            pub, mock = self.fixture.publisher()
            pub.spec["minimum_relative_improvement"] = value
            with self.assertRaisesRegex(runtime.Stop, "at least 1% relative"):
                pub.execute("publish")
            self.assertEqual(mock.writes, [])

    def test_unresolved_or_new_assumptions_stop(self):
        for field in ("unresolved", "new_assumptions"):
            pub, mock = self.fixture.publisher()
            pub.spec["frontier_rules"]["claims"][0][field] = True
            with self.assertRaisesRegex(runtime.Stop, "unresolved scope/assumptions"):
                pub.execute("publish")
            self.assertEqual(mock.writes, [])

    def test_unknown_or_closed_pr_stops(self):
        pub, mock = self.fixture.publisher()
        new = copy.deepcopy(mock.prs[0])
        new["number"] = 102
        mock.prs.append(new)
        with self.assertRaisesRegex(runtime.Stop, "frontier reassessment"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_certificate_corruption_and_disagreeing_value_stop(self):
        pub, mock = self.fixture.publisher()
        key = ("reviewer/integer-mult-bounds", self.fixture.claim_sha, "certificates/current.json")
        mock.certificates[key] = b"corrupt"
        with self.assertRaisesRegex(runtime.Stop, "fingerprint changed"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])
        pub, mock = self.fixture.publisher()
        rule = pub.spec["frontier_rules"]["claims"][0]
        rule["exact_kappa"] = "1/3000"
        with self.assertRaisesRegex(runtime.Stop, "disagrees"):
            pub.execute("publish")

    def test_duplicate_exact_candidate_prints_existing_url(self):
        pub, mock = self.fixture.publisher()
        duplicate = copy.deepcopy(mock.prs[0])
        duplicate.update(number=888, body=pub.marker, user={"login": "fixture-user"},
                         html_url=f"https://github.com/{runtime.UPSTREAM}/pull/888")
        duplicate["head"] = {"sha": self.fixture.submit_sha,
                             "repo": {"full_name": "fixture-user/integer-mult-bounds"}}
        mock.closed.append(duplicate)
        for item in pub.spec["changes"]:
            mock.certificates[("fixture-user/integer-mult-bounds", self.fixture.submit_sha,
                               item["path"])] = (self.fixture.payload / item["path"]).read_bytes()
        for name in {**pub.spec["source_fingerprints"], **pub.spec["protected_base_paths"]}:
            mock.certificates[("fixture-user/integer-mult-bounds", self.fixture.submit_sha,
                               name)] = (self.fixture.base / name).read_bytes()
        result = pub.execute("publish")
        self.assertTrue(result["duplicate"])
        self.assertTrue(result["url"].endswith("/888"))
        self.assertEqual(mock.writes, [])
        # A submitted exact candidate remains discoverable after upstream moves;
        # this returns an existing URL and never attempts a new publication.
        mock.current_base = "3" * 40
        self.assertTrue(pub.execute("publish")["duplicate"])
        mock.extra_prfile = "unrelated.py"
        with self.assertRaisesRegex(runtime.Stop, "different publication allowlist"):
            pub.execute("publish")

    def test_different_candidate_is_not_edited(self):
        pub, mock = self.fixture.publisher()
        old = copy.deepcopy(mock.prs[0])
        old["body"] = "<!-- frozen-candidate: previous sha256:" + "8" * 64 + " -->"
        old["user"] = {"login": "fixture-user"}
        mock.closed.append(old)
        result = pub.execute("publish")
        self.assertFalse(result["duplicate"])
        self.assertFalse(any("edit" in call for call in mock.calls))

    def test_final_frontier_change_blocks_pr_after_mock_push(self):
        pub, mock = self.fixture.publisher()
        mock.mutate_final = True
        with self.assertRaisesRegex(runtime.Stop, "body changed"):
            pub.execute("publish")
        self.assertTrue(any(call[:2] == ["git", "push"] for call in mock.calls))
        self.assertFalse(any(call[:3] == ["gh", "pr", "create"] for call in mock.calls))

    def test_remote_commit_mismatch_blocks_pr(self):
        pub, mock = self.fixture.publisher()
        mock.bad_remote = True
        with self.assertRaisesRegex(runtime.Stop, "not verified"):
            pub.execute("publish")
        self.assertFalse(any(call[:3] == ["gh", "pr", "create"] for call in mock.calls))

    def test_push_and_pr_failure_are_never_success(self):
        for prefix in (["git", "push"], ["gh", "pr", "create"]):
            pub, mock = self.fixture.publisher()
            mock.fail_prefix = prefix
            with self.assertRaises(runtime.CommandFailure):
                pub.execute("publish")
            if prefix == ["git", "push"]:
                self.assertFalse(any(call[:3] == ["gh", "pr", "create"] for call in mock.calls))

    def test_local_check_failure_blocks_github_mutations(self):
        pub, mock = self.fixture.publisher()
        mock.fail_prefix = ["python3", "tests/inherited.py"]
        with self.assertRaises(runtime.CommandFailure):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_foreign_fork_blocks_push_and_pr(self):
        pub, mock = self.fixture.publisher()
        mock.foreign_fork = True
        with self.assertRaisesRegex(runtime.Stop, "not their own upstream fork"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_staged_allowlist_mismatch_blocks_mutations(self):
        pub, mock = self.fixture.publisher()
        mock.extra_staged_path = "unrelated.py"
        with self.assertRaisesRegex(runtime.Stop, "frozen allowlist"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_checker_added_staged_path_blocks_mutations(self):
        pub, mock = self.fixture.publisher()
        mock.on_check_extra_staged = "unrelated.py"
        with self.assertRaisesRegex(runtime.Stop, "frozen allowlist"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_index_blob_or_mode_mutation_blocks_mutations(self):
        for mutation in ("blob", "mode"):
            pub, mock = self.fixture.publisher()
            name = pub.spec["changes"][0]["path"]
            if mutation == "blob":
                mock.index_blobs[name] = b"different staged bytes"
            else:
                mock.index_modes[name] = "100755"
            with self.assertRaises(runtime.Stop):
                pub.execute("publish")
            self.assertEqual(mock.writes, [])

    def test_untracked_unexpected_file_blocks_mutations(self):
        pub, mock = self.fixture.publisher()
        mock.untracked = b"unrelated.py\x00"
        with self.assertRaisesRegex(runtime.Stop, "Unexpected untracked"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_global_remote_rewrite_blocks_push_and_pr(self):
        pub, mock = self.fixture.publisher()
        mock.rewrite_remote = True
        with self.assertRaisesRegex(runtime.Stop, "rewrites submission destination"):
            pub.execute("publish")
        self.assertFalse(any(call[:2] == ["git", "push"] for call in mock.calls))
        self.assertFalse(any(call[:3] == ["gh", "pr", "create"] for call in mock.calls))

    def test_missing_required_dependency_fingerprint_stops(self):
        pub, mock = self.fixture.publisher()
        (self.fixture.base / "formula.py").write_text("# changed mathematics\n")
        with self.assertRaisesRegex(runtime.Stop, "dependency changed"):
            pub.execute("publish")
        self.assertEqual(mock.writes, [])

    def test_allowlisted_pinned_source_acquisition(self):
        acquired = b"# synthetic inherited source, never executed\n"
        item = {"path": "inherited/source.py", "sha256": data_digest(acquired), "mode": 0o644,
                "before_sha256": None, "acquire": source("predecessor/integer-mult-bounds", "5" * 40,
                                                          "inherited/source.py", acquired, pointer=None)}
        self.fixture.spec["changes"].append(item)
        pub, mock = self.fixture.publisher()
        mock.certificates[("predecessor/integer-mult-bounds", "5" * 40, "inherited/source.py")] = acquired
        mock.large_files.add(("predecessor/integer-mult-bounds", "5" * 40, "inherited/source.py"))
        result = pub.execute("--dry-run")
        self.assertEqual((pub.repo / "inherited/source.py").read_bytes(), acquired)
        self.assertEqual(mock.writes, [])
        self.assertEqual(result["mode"], "--dry-run")
        self.assertTrue(any("-H" in call for call in mock.calls))

    def test_paginated_open_collection_includes_drafts(self):
        pub, mock = self.fixture.publisher()
        for number in range(102, 203):
            item = copy.deepcopy(mock.prs[0])
            item["number"] = number
            mock.prs.append(item)
        collection = pub.pages("open")
        self.assertEqual(len(collection), 102)
        self.assertTrue(all(item["draft"] for item in collection))
        self.assertTrue(any("page=2" in call[-1] for call in mock.calls))

    def test_real_local_command_timeout_and_failure_propagate(self):
        # Actual subprocesses here are disposable Python children only, never
        # Git, gh, network operations or the script's default publishing mode.
        runner = runtime.Runner(self.fixture.workspace)
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(runtime.CommandFailure) as failed:
                runner.run(["python3", "-c", "import sys; sys.exit(7)"], timeout=2)
            self.assertEqual(failed.exception.code, 7)
            with self.assertRaises(runtime.CommandFailure) as timed:
                runner.run(["python3", "-c", "import time; time.sleep(5)"], timeout=0.05)
            self.assertEqual(timed.exception.code, "timeout")

    def test_read_retries_are_bounded_and_write_failures_not_retried(self):
        command = ["python3", "-c", "import sys; sys.exit(8)"]
        runner = runtime.Runner(self.fixture.workspace)
        with contextlib.redirect_stdout(io.StringIO()), unittest_mock.patch.object(runtime.time, "sleep"):
            with self.assertRaises(runtime.CommandFailure):
                runner.run(command, network=True, timeout=2)
        log = (self.fixture.workspace / "publication.log").read_text()
        self.assertEqual(log.count("Running "), 3)
        (self.fixture.workspace / "publication.log").write_text("")
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(runtime.CommandFailure):
                runner.run(command, network=True, write=True, timeout=2)
        log = (self.fixture.workspace / "publication.log").read_text()
        self.assertEqual(log.count("Running "), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
