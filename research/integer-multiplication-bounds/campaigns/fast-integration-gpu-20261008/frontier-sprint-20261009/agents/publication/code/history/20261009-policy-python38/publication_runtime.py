#!/usr/bin/env python3
"""Publication driver packaged by build_publication.py. Standard library only.

Only a frozen, independently accepted package may enter the real write path.
Tests inject an in-memory command backend; the CLI has no mock bypass switch.
"""
import base64
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid
from fractions import Fraction
from pathlib import Path, PurePosixPath
from urllib.parse import quote

UPSTREAM = "CrocSwap/integer-mult-bounds"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MAX_API_BYTES = 32 * 1024 * 1024
MINIMUM_RELATIVE_IMPROVEMENT = "1/100"


class Stop(RuntimeError):
    """A guard or command failed. The workspace remains available."""


class CommandFailure(Stop):
    def __init__(self, command, code, message):
        self.command, self.code, self.message = command, code, message
        super().__init__(f"Command failed ({code}): {shlex.join(command)}\n{message}")


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    if (not isinstance(value, str) or not value or "\\" in value or
            any(ord(character) < 32 for character in value)):
        raise Stop(f"Unsafe path: {value!r}")
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in {"", ".", "..", ".git"} for x in value.split("/")):
        raise Stop(f"Unsafe path: {value!r}")
    return value


def fraction(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:/[1-9][0-9]*)?", value):
        raise Stop(f"An exact nonnegative integer/rational is required: {value!r}")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise Stop("Invalid exact rational") from exc


def pointer(data, path):
    if not isinstance(path, str) or not path.startswith("/"):
        raise Stop("Certificate JSON pointer is missing")
    for item in path[1:].split("/"):
        item = item.replace("~1", "/").replace("~0", "~")
        data = data[int(item)] if isinstance(data, list) else data[item]
    return data


def local_file(root, name):
    """Reject existing symlinks in every component before reading/writing."""
    safe_path(name)
    at = root
    for part in name.split("/"):
        at = at / part
        if at.is_symlink():
            raise Stop(f"Symlink is forbidden in publication path: {name}")
    return at


class Runner:
    def __init__(self, workspace):
        self.workspace = workspace
        self.log = workspace / "publication.log"

    def note(self, message):
        line = f"[{utc()}] {message}"
        print(line, flush=True)
        with self.log.open("a", encoding="utf-8") as out:
            out.write(line + "\n")

    def run(self, args, *, cwd=None, network=False, write=False, timeout=45):
        # Reads may be retried; writes are not blindly repeated after a timeout.
        attempts = 1 if write or not network or args[:2] == ["git", "clone"] else 3
        if network and args[0] == "git":
            # Use the existing gh account without printing a token, installing
            # credentials or changing the user's Git configuration.
            args = ["git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "-c",
                    "credential.https://github.com.helper=!gh auth git-credential", *args[1:]]
        for attempt in range(attempts):
            self.note("Running " + shlex.join(args))
            process = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True)
            try:
                out, err = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
                failure = CommandFailure(args, "timeout", f"Timeout after {timeout}s")
            else:
                if len(out) > MAX_API_BYTES or len(err) > MAX_API_BYTES:
                    raise Stop("Command output exceeds the bounded receipt size")
                if process.returncode == 0:
                    # Authentication diagnostics may contain account metadata;
                    # never echo auth output or environment variables into logs.
                    return out
                message = ("Authentication check failed; inspect gh auth status locally" if
                           args[:3] == ["gh", "auth", "status"] else
                           err.decode("utf-8", "replace")[-4000:])
                failure = CommandFailure(args, process.returncode, message)
            if attempt + 1 == attempts:
                raise failure
            self.note(f"Read failed; retry {attempt + 2}/{attempts}")
            time.sleep(attempt + 1)


class Publisher:
    def __init__(self, package, workspace, runner=None):
        self.package, self.workspace = Path(package), Path(workspace)
        self.runner = runner or Runner(self.workspace)
        self.manifest = json.loads((self.package / "manifest.json").read_text())
        self.spec = self.manifest["release"]
        self.repo = self.workspace / "upstream"
        self.login = None
        self.marker = (f"<!-- frozen-candidate: {self.spec['candidate_id']} "
                       f"sha256:{self.spec['candidate_digest']} -->")

    def api(self, endpoint):
        raw = self.runner.run(["gh", "api", endpoint], network=True)
        try:
            return json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise Stop(f"Invalid API JSON: {endpoint}") from exc

    def pages(self, state):
        result, seen = [], set()
        for page in range(1, 101):
            batch = self.api(f"repos/{UPSTREAM}/pulls?state={state}&sort=updated&direction=desc"
                             f"&per_page=100&page={page}")
            if not isinstance(batch, list) or len(batch) > 100:
                raise Stop("Malformed/incomplete paginated PR response")
            for pr in batch:
                if pr.get("number") in seen:
                    raise Stop("PR pagination changed during collection; reassess before retrying")
                seen.add(pr.get("number"))
                result.append(pr)
            if len(batch) < 100:
                return result
        raise Stop("Pagination bound reached; publication comparison is unresolved")

    def content(self, source):
        repo, ref, path = source["repository"], source["ref"], safe_path(source["path"])
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not HEX40.fullmatch(ref):
            raise Stop("Unsafe certificate repository/ref")
        endpoint = f"repos/{repo}/contents/{quote(path, safe='/')}?ref={ref}"
        result = self.api(endpoint)
        if result.get("type", "file") != "file":
            raise Stop(f"Missing bounded certificate file: {repo}:{path}")
        if result.get("encoding") == "none":
            # GitHub omits base64 for larger declared source files. The pinned
            # raw response still comes through authenticated gh and is hashed.
            data = self.runner.run(["gh", "api", endpoint, "-H",
                                    "Accept: application/vnd.github.raw+json"], network=True)
        elif result.get("encoding") == "base64":
            try:
                data = base64.b64decode("".join(result["content"].split()), validate=True)
            except (KeyError, ValueError) as exc:
                raise Stop("Invalid certificate base64") from exc
        else:
            raise Stop("Missing supported bounded certificate content encoding")
        if len(data) > MAX_API_BYTES or digest(data) != source["decoded_sha256"]:
            raise Stop(f"Certificate fingerprint changed: {repo}:{path}")
        if source.get("bytes") is not None and len(data) != source["bytes"]:
            raise Stop("Declared downloaded source byte count changed")
        return data

    def verify_certificate(self, source, value):
        data = self.content(source)
        if source.get("value_pointer"):
            try:
                actual = fraction(pointer(json.loads(data), source["value_pointer"]))
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                raise Stop("Cannot extract exact certificate kappa") from exc
            if actual != value:
                raise Stop("Certificate exact kappa disagrees with reviewed comparison")
        # A source-only exact assertion is never executed. Its whole-file hash
        # binds the coordinator's explicit, frozen mathematical assessment.
        elif not source.get("manual_exact_assessment"):
            raise Stop("Source-only certificate lacks an explicit frozen exact assessment")

    def authenticate(self):
        self.runner.run(["gh", "auth", "status", "--hostname", "github.com"], network=True)
        user = self.api("user")
        self.login = user.get("login", "")
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", self.login):
            raise Stop("Cannot establish the authenticated GitHub account")

    def base(self):
        info = self.api(f"repos/{UPSTREAM}")
        expected = self.spec["default_branch"]
        if info.get("full_name") != UPSTREAM or info.get("default_branch") != expected:
            raise Stop("Upstream/default branch changed; revalidation is required")
        actual = self.api(f"repos/{UPSTREAM}/commits/{quote(expected, safe='')}").get("sha")
        if actual != self.spec["base_sha"]:
            raise Stop("Upstream base changed; revalidation is required (no automatic rebase)")

    def remote_modes(self, repository, commit):
        if not HEX40.fullmatch(commit):
            raise Stop("Remote candidate has no exact commit SHA")
        tree_sha = self.api(f"repos/{repository}/git/commits/{commit}").get("tree", {}).get("sha", "")
        if not HEX40.fullmatch(tree_sha):
            raise Stop("Cannot establish submission commit tree")
        tree = self.api(f"repos/{repository}/git/trees/{tree_sha}?recursive=1")
        if tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
            raise Stop("Remote file-mode tree is truncated or unresolved")
        entries = {item["path"]: item for item in tree["tree"]}
        if len(entries) != len(tree["tree"]):
            raise Stop("Remote tree contains duplicate paths")
        for item in self.spec["changes"]:
            current = entries.get(item["path"], {})
            if current.get("type") != "blob" or current.get("mode") != ("100755" if item["mode"] == 0o755 else "100644"):
                raise Stop("Remote candidate file mode/type differs from frozen package")

    def duplicate(self, prs):
        for pr in prs:
            if self.marker not in (pr.get("body") or ""):
                continue
            if pr.get("user", {}).get("login") != self.login:
                continue
            if pr.get("base", {}).get("repo", {}).get("full_name") != UPSTREAM:
                raise Stop("Candidate marker appears on an unexpected target repository")
            if pr.get("base", {}).get("ref") != self.spec["default_branch"]:
                raise Stop("Candidate marker appears on an unexpected target branch")
            head = pr.get("head", {})
            head_repo = (head.get("repo") or {}).get("full_name")
            if head_repo != f"{self.login}/integer-mult-bounds":
                raise Stop("Candidate marker appears on an unexpected submission fork")
            self.remote_modes(head_repo, head.get("sha", ""))
            for item in self.spec["changes"]:
                self.content({"repository": head_repo, "ref": head.get("sha", ""),
                              "path": item["path"], "decoded_sha256": item["sha256"]})
            for name, expected in {**self.spec["source_fingerprints"],
                                   **self.spec["protected_base_paths"]}.items():
                self.content({"repository": head_repo, "ref": head.get("sha", ""),
                              "path": name, "decoded_sha256": expected})
            changed = []
            for page in range(1, 101):
                items = self.api(f"repos/{UPSTREAM}/pulls/{pr['number']}/files?per_page=100&page={page}")
                if not isinstance(items, list) or len(items) > 100:
                    raise Stop("Existing candidate file collection is unresolved")
                changed.extend(items)
                if len(items) < 100:
                    break
            else:
                raise Stop("Existing candidate file pagination bound reached")
            if ({item["filename"] for item in changed} != {item["path"] for item in self.spec["changes"]} or
                    any(item["status"] not in {"added", "modified"} for item in changed)):
                raise Stop("Existing candidate has a different publication allowlist")
            current = self.api(f"repos/{UPSTREAM}/pulls/{pr['number']}")
            if current.get("head", {}).get("sha") != head["sha"] or self.marker not in (current.get("body") or ""):
                raise Stop("Existing candidate changed while being checked")
            url = pr.get("html_url", "")
            if not re.fullmatch(r"https://github\.com/CrocSwap/integer-mult-bounds/pull/[0-9]+", url):
                raise Stop("Existing candidate has no valid actual PR URL")
            self.runner.note(f"Exact frozen candidate already submitted: {url}")
            self.runner.note(f"Existing submission commit: {head['sha']}")
            return {"url": url, "commit": head["sha"], "duplicate": True}
        return None

    def frontier(self, prs):
        rules = self.spec["frontier_rules"]
        frozen = {int(r["pr"]): r for r in rules["claims"]}
        observed = {int(pr["number"]): pr for pr in prs}
        if len(observed) != len(prs) or set(observed) != set(frozen):
            raise Stop("New or closed PRs require frontier reassessment; comparison unresolved")
        values = []
        for number, pr in observed.items():
            rule = frozen[number]
            if pr.get("state") != "open" or pr.get("merged_at") is not None:
                raise Stop("Active PR collection contains inconsistent state")
            if pr.get("head", {}).get("sha") != rule["head_sha"]:
                raise Stop(f"PR #{number} head changed; comparison unresolved")
            for key in ("body", "title"):
                if digest((pr.get(key) or "").encode()) != rule[f"{key}_sha256"]:
                    raise Stop(f"PR #{number} {key} changed; comparison unresolved")
            if rule.get("unresolved") or rule.get("new_assumptions"):
                raise Stop(f"PR #{number} has unresolved scope/assumptions")
            if rule.get("excluded"):
                if not rule.get("assessment_scope"):
                    raise Stop("An excluded claim lacks explicit pinned evidence")
                continue
            exact, upper = rule.get("exact_kappa"), rule.get("certified_upper_bound")
            if bool(exact) == bool(upper):
                raise Stop(f"PR #{number} has no unique exact value/reviewed conservative bound")
            value = fraction(exact or upper)
            source = rule.get("certificate_source")
            if exact:
                if not source or source["ref"] != rule["head_sha"]:
                    raise Stop(f"PR #{number} lacks a certificate pinned to its actual head")
                self.verify_certificate(source, value)
            elif not rule.get("assessment_scope"):
                raise Stop("A conservative bound lacks its explicit reviewed scope")
            values.append((value, f"PR #{number}", "exact" if exact else "reviewed upper bound"))
        retained = rules["retained_main"]
        retained_value = fraction(retained["exact_kappa"])
        for source in retained["certificate_sources"]:
            if source["ref"] != self.spec["base_sha"]:
                raise Stop("Retained result certificate is not pinned to the verified base")
            self.verify_certificate(source, retained_value)
        if not retained["certificate_sources"]:
            raise Stop("Retained reviewed result has no certificate")
        values.append((retained_value, "retained main", "exact"))
        highest = max(values)
        if self.spec.get("minimum_relative_improvement") != MINIMUM_RELATIVE_IMPROVEMENT:
            raise Stop("Frozen publication policy must require at least 1% relative improvement")
        required = highest[0] * (1 + fraction(MINIMUM_RELATIVE_IMPROVEMENT))
        candidate = fraction(self.spec["exact_kappa"])
        if candidate <= highest[0]:
            raise Stop(f"Candidate does not strictly beat current comparable frontier {highest[0]}")
        if candidate < required:
            raise Stop(f"Candidate is below the exact 1% publication threshold {required}; "
                       f"current comparable frontier is {highest[0]}")
        report = {"observed_utc": utc(), "open_count": len(prs), "includes_drafts": True,
                  "maximum": str(highest[0]), "maximum_source": highest[1],
                  "maximum_kind": highest[2], "candidate": self.spec["exact_kappa"],
                  "minimum_relative_improvement": MINIMUM_RELATIVE_IMPROVEMENT,
                  "minimum_required_kappa": str(required),
                  "achieved_relative_improvement": str((candidate - highest[0]) / highest[0]) if highest[0] else None,
                  "comparison_resolved": True, "base_sha": self.spec["base_sha"]}
        path = self.workspace / f"frontier-{uuid.uuid4().hex[:12]}.json"
        path.write_text(json.dumps(report, indent=2) + "\n")
        self.runner.note(f"Current exact 1% publication gate passed at {report['observed_utc']}: "
                         f"{report['candidate']} >= {report['minimum_required_kappa']}")
        return report

    def fingerprints(self):
        for name, expected in {**self.spec["source_fingerprints"],
                               **self.spec["protected_base_paths"]}.items():
            path = local_file(self.repo, name)
            if not path.is_file() or digest(path.read_bytes()) != expected:
                raise Stop(f"Mathematical/protected dependency changed: {name}")

    def change_set(self, diff_options):
        paths = {item["path"] for item in self.spec["changes"]}
        names = self.runner.run(["git", "diff", *diff_options, "--no-renames", "--name-only", "-z"], cwd=self.repo)
        actual = [name.decode() for name in names.split(b"\x00") if name]
        if len(actual) != len(paths) or set(actual) != paths:
            raise Stop("Staged/committed changes do not exactly match the frozen allowlist")
        status = self.runner.run(["git", "diff", *diff_options, "--no-renames", "--name-status", "-z"], cwd=self.repo)
        fields = status.split(b"\x00")
        if fields[-1] == b"":
            fields.pop()
        if len(fields) != 2 * len(paths):
            raise Stop("Cannot validate publication change statuses")
        for index in range(0, len(fields), 2):
            if fields[index] not in {b"A", b"M"} or fields[index + 1].decode() not in paths:
                raise Stop("Deletion, rename or non-allowlisted publication change is forbidden")

    def staged(self):
        self.change_set(["--cached"])
        for item in self.spec["changes"]:
            entry = self.runner.run(["git", "ls-files", "--stage", "-z", "--", item["path"]], cwd=self.repo)
            expected_mode = b"100755" if item["mode"] == 0o755 else b"100644"
            try:
                metadata, name = entry.rstrip(b"\x00").split(b"\t")
                mode, blob, stage = metadata.split()
            except ValueError as exc:
                raise Stop("Publication index entry is missing or ambiguous") from exc
            if mode != expected_mode or stage != b"0" or name.decode() != item["path"]:
                raise Stop("Publication index mode/stage/path disagrees with frozen package")
            data = self.runner.run(["git", "show", ":" + item["path"]], cwd=self.repo)
            if digest(data) != item["sha256"]:
                raise Stop("Staged publication bytes disagree with the frozen payload")
        self.runner.run(["git", "diff", "--cached", "--check"], cwd=self.repo)

    def working(self):
        self.fingerprints()
        for item in self.spec["changes"]:
            path = local_file(self.repo, item["path"])
            if not path.is_file() or digest(path.read_bytes()) != item["sha256"]:
                raise Stop("A local command modified the frozen publication bytes")
        if self.runner.run(["git", "diff", "--name-only"], cwd=self.repo).strip():
            raise Stop("Unexpected unstaged changes after local checks")
        if self.runner.run(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=self.repo).strip():
            raise Stop("Unexpected untracked publication files after local checks")

    def committed(self):
        self.change_set([self.spec["base_sha"], "HEAD"])
        for item in self.spec["changes"]:
            entry = self.runner.run(["git", "ls-tree", "-z", "HEAD", "--", item["path"]], cwd=self.repo)
            expected_mode = b"100755" if item["mode"] == 0o755 else b"100644"
            try:
                metadata, name = entry.rstrip(b"\x00").split(b"\t")
                mode, kind, blob = metadata.split()
            except ValueError as exc:
                raise Stop("Committed publication tree entry is missing or ambiguous") from exc
            if mode != expected_mode or kind != b"blob" or name.decode() != item["path"]:
                raise Stop("Committed publication mode/type/path disagrees with frozen package")
            if digest(self.runner.run(["git", "show", "HEAD:" + item["path"]], cwd=self.repo)) != item["sha256"]:
                raise Stop("Committed publication bytes disagree with the frozen payload")
        self.working()

    def prepare(self):
        self.runner.run(["git", "clone", "--depth", "1", "--no-tags", "--single-branch",
                         "--branch", self.spec["default_branch"],
                         f"https://github.com/{UPSTREAM}.git", str(self.repo)], network=True)
        head = self.runner.run(["git", "rev-parse", "HEAD"], cwd=self.repo).decode().strip()
        if head != self.spec["base_sha"]:
            raise Stop("Clone base changed during download; revalidation is required")
        self.fingerprints()
        for item in self.spec["changes"]:
            path = local_file(self.repo, item["path"])
            before = item.get("before_sha256")
            if before is None:
                if path.exists():
                    raise Stop(f"Allowlisted addition unexpectedly exists: {item['path']}")
            elif not path.is_file() or digest(path.read_bytes()) != before:
                raise Stop(f"Allowlisted replacement base disagrees: {item['path']}")
            data = (self.content(item["acquire"]) if item.get("acquire") else
                    local_file(self.package, "files/" + item["path"]).read_bytes())
            if digest(data) != item["sha256"]:
                raise Stop("Publication bytes changed after extraction")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(item["mode"])
        self.fingerprints()
        paths = [item["path"] for item in self.spec["changes"]]
        self.runner.run(["git", "add", "--", *paths], cwd=self.repo)
        for item in self.spec["changes"]:
            self.runner.run(["git", "update-index", "--chmod=" +
                             ("+x" if item["mode"] == 0o755 else "-x"), "--", item["path"]],
                            cwd=self.repo)
        self.staged()
        for check in self.spec["local_checks"]:
            self.runner.run(check["command"], cwd=self.repo, timeout=check["timeout_seconds"])
        # A checker must not rewrite files or stage a different candidate.
        self.staged()
        self.working()
        self.runner.note(f"Allowlisted package prepared for inspection: {self.repo}")

    def own_fork(self):
        name = f"{self.login}/integer-mult-bounds"
        try:
            info = self.api(f"repos/{name}")
        except CommandFailure as exc:
            if "HTTP 404" not in exc.message:
                raise
            self.runner.run(["gh", "repo", "fork", UPSTREAM, "--clone=false", "--remote=false"],
                            network=True, write=True, timeout=60)
            info = self.api(f"repos/{name}")
        if (info.get("full_name") != name or not info.get("fork") or
                info.get("owner", {}).get("login") != self.login or
                info.get("parent", {}).get("full_name") != UPSTREAM):
            raise Stop("Authenticated user's repository is not their own upstream fork")
        return name

    def submit(self, fork, first):
        branch = (f"submission/{self.spec['candidate_id']}-"
                  f"{self.spec['candidate_digest'][:12]}-{uuid.uuid4().hex[:12]}")
        self.runner.run(["git", "checkout", "-b", branch], cwd=self.repo)
        self.runner.run(["git", "config", "user.name", self.login], cwd=self.repo)
        self.runner.run(["git", "config", "user.email", f"{self.login}@users.noreply.github.com"],
                        cwd=self.repo)
        self.staged()
        self.working()
        self.runner.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                         "commit", "-m", self.spec["commit_message"]], cwd=self.repo)
        commit = self.runner.run(["git", "rev-parse", "HEAD"], cwd=self.repo).decode().strip()
        if not HEX40.fullmatch(commit):
            raise Stop("Git did not return a valid submission commit")
        self.committed()
        url = f"https://github.com/{fork}.git"
        existing = self.runner.run(["git", "ls-remote", "--heads", url,
                                    "refs/heads/" + branch], network=True)
        if existing.strip():
            raise Stop("Unique submission branch unexpectedly exists; never replace history")
        self.runner.run(["git", "remote", "add", "submission", url], cwd=self.repo)
        resolved = self.runner.run(["git", "remote", "get-url", "--push", "submission"], cwd=self.repo).decode().strip()
        if resolved != url:
            raise Stop("Git configuration rewrites submission destination; no remote writes permitted")
        self.runner.run(["git", "push", "--porcelain", "submission",
                         f"HEAD:refs/heads/{branch}"], cwd=self.repo,
                        network=True, write=True, timeout=60)
        remote = self.runner.run(["git", "ls-remote", "--heads", url,
                                  "refs/heads/" + branch], network=True).decode().split()
        if remote != [commit, "refs/heads/" + branch]:
            raise Stop("Remote submission commit was not verified; no PR will be opened")
        self.remote_modes(fork, commit)
        for item in self.spec["changes"]:
            self.content({"repository": fork, "ref": commit, "path": item["path"],
                          "decoded_sha256": item["sha256"]})
        for name, expected in {**self.spec["source_fingerprints"], **self.spec["protected_base_paths"]}.items():
            self.content({"repository": fork, "ref": commit, "path": name, "decoded_sha256": expected})
        # All source/base and frontier guards run again immediately before PR creation.
        self.base()
        prs = self.pages("open")
        duplicate = self.duplicate(prs + self.pages("closed"))
        if duplicate:
            return duplicate
        final = self.frontier(prs)
        self.committed()
        last_remote = self.runner.run(["git", "ls-remote", "--heads", url,
                                       "refs/heads/" + branch], network=True).decode().split()
        if last_remote != [commit, "refs/heads/" + branch]:
            raise Stop("Remote branch changed before PR creation; no PR will be opened")
        body = self.spec["prepared_body"].replace("{{FRONTIER_OBSERVED_UTC}}", final["observed_utc"])
        body = body.replace("{{FRONTIER_MAXIMUM}}", final["maximum"])
        body = body.replace("{{MINIMUM_REQUIRED_KAPPA}}", final["minimum_required_kappa"])
        body += "\n\n" + self.marker + "\n"
        body_path = self.workspace / "pull-request-body.md"
        body_path.write_text(body)
        self.runner.note("Frontier race after this check cannot be eliminated; the PR states its timestamp")
        actual = self.runner.run(["gh", "pr", "create", "--repo", UPSTREAM,
                                  "--base", self.spec["default_branch"],
                                  "--head", f"{self.login}:{branch}",
                                  "--title", self.spec["title"], "--body-file", str(body_path)],
                                 network=True, write=True, timeout=60).decode().strip()
        if not re.fullmatch(r"https://github\.com/CrocSwap/integer-mult-bounds/pull/[0-9]+", actual):
            raise Stop("PR creation returned no unambiguous actual URL; inspect logs before retrying")
        self.runner.note(f"Created pull request: {actual}")
        self.runner.note(f"Submission commit: {commit}")
        self.runner.note("Hosted checks have not been claimed to pass; GitHub will run its configured checks")
        return {"url": actual, "commit": commit, "duplicate": False,
                "frontier_observed_utc": final["observed_utc"]}

    def execute(self, mode):
        if self.spec.get("minimum_relative_improvement") != MINIMUM_RELATIVE_IMPROVEMENT:
            raise Stop("Frozen publication policy must require at least 1% relative improvement")
        if mode in {"--check", "--self-test"}:
            if self.spec["upstream"] != UPSTREAM:
                raise Stop("Unexpected upstream repository")
            fraction(self.spec["exact_kappa"])
            safe_path("certificates/example.json")
            if mode == "--self-test":
                for bad in ("../escape", "/absolute", "a/.git/config", "a\\b", "a//b"):
                    try:
                        safe_path(bad)
                    except Stop:
                        continue
                    raise Stop("Local path self-test failed")
                if fraction("2/3") <= fraction("1/2"):
                    raise Stop("Local exact arithmetic self-test failed")
            self.runner.note("Payload integrity/local checks passed; no GitHub requests or writes made")
            return {"mode": mode, "candidate": self.spec["candidate_id"]}
        if self.spec.get("synthetic_test_only"):
            raise Stop("Synthetic fixture cannot use the CLI publication or network path")
        if not self.spec.get("freeze_approved") or self.spec.get("status") not in {
                "ACCEPTED_CONDITIONAL", "PUBLICATION_READY"}:
            raise Stop("Candidate is not frozen and conditionally accepted")
        self.authenticate()
        prs = self.pages("open")
        duplicate = self.duplicate(prs + self.pages("closed"))
        if duplicate:
            return duplicate
        self.base()
        first = self.frontier(prs)
        self.prepare()
        if mode == "--dry-run":
            self.runner.note("Dry run complete; no fork, remote push or PR creation was attempted")
            return {"mode": mode, "workspace": str(self.workspace), "frontier": first}
        if mode != "publish":
            raise Stop("Unknown execution mode")
        # Check again before the first GitHub mutation (fork creation if necessary).
        self.base()
        return self.submit(self.own_fork(), first)


def main():
    if len(sys.argv) != 4:
        raise Stop("Internal invocation requires mode, extracted package and workspace")
    mode, package, workspace = sys.argv[1:]
    for command in ("bash", "git", "python3", "gh"):
        if not shutil.which(command):
            raise Stop(f"Missing prerequisite: {command}; install it yourself before retrying")
    publisher = Publisher(package, workspace)
    try:
        result = publisher.execute(mode)
        (Path(workspace) / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    except Exception as exc:
        publisher.runner.note(f"STOPPED: {type(exc).__name__}: {exc}")
        publisher.runner.note(f"Workspace and logs retained for inspection: {workspace}")
        return 1
    publisher.runner.note(f"Workspace and logs retained: {workspace}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as exc:
        print(f"[{utc()}] STOPPED: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
