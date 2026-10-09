#!/usr/bin/env python3
"""Build one portable script from an explicitly frozen allowlisted release.

No network access, shell commands or Git writes are performed by this builder.
Synthetic fixtures may exercise extraction/check mode but cannot publish.
"""
import argparse
import base64
import gzip
import hashlib
import io
import json
import re
import tarfile
from decimal import Decimal, localcontext
from pathlib import Path

from publication_runtime import (HEX40, HEX64, MINIMUM_RELATIVE_IMPROVEMENT,
                                 UPSTREAM, Stop, fraction, require_python, safe_path)

MAX_PAYLOAD = 32 * 1024 * 1024
REQUIRED_GATES = ("exact_finite", "conditional_exponent", "independent_reproduction",
                  "negative_controls", "inherited_required_checks", "frontier_review",
                  "source_and_license_inventory")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decimal(value):
    with localcontext() as context:
        context.prec = 30
        return format(Decimal(value.numerator) / Decimal(value.denominator), ".18g")


def prepared_body(spec):
    text = spec["public_text"]
    candidate, predecessor = fraction(spec["exact_kappa"]), fraction(text["predecessor_kappa"])
    if candidate <= predecessor:
        raise Stop("Candidate does not improve its stated predecessor")
    required = ("construction_change", "predecessor", "verification_scope", "reproduction",
                "conditional_assumptions", "exclusions", "attribution", "license_notes",
                "source_inventory", "ai_assistance")
    if any(not isinstance(text.get(key), str) or not text[key].strip() for key in required):
        raise Stop("Public title/body lacks required scope, assumptions, attribution or reproduction")
    delta = candidate - predecessor
    ratio = delta / predecessor
    return (f"This frozen construction gives a **conditional** exponent saving "
            f"`kappa = {candidate}` (approximately `{decimal(candidate)}`).\n\n"
            f"## Construction and predecessor\n\n{text['construction_change']}\n\n"
            f"{text['predecessor']} The predecessor has `kappa = {predecessor}`. "
            f"The exact improvement is `{delta}` (approximately `{decimal(delta)}`), "
            f"or approximately `{decimal(100 * ratio)}%`.\n\n"
            f"## Verification coverage\n\n{text['verification_scope']}\n\n"
            "This package records completed local reproduction. Hosted CI is pending; "
            "no claim that hosted checks have passed is made.\n\n"
            f"## Reproduction\n\n{text['reproduction']}\n\n"
            f"## Conditional assumptions and exclusions\n\n{text['conditional_assumptions']}\n\n"
            f"{text['exclusions']}\n\n"
            f"## Attribution and source inventory\n\n{text['attribution']}\n\n"
            f"{text['source_inventory']}\n\n{text['license_notes']}\n\n"
            f"{text['ai_assistance']}\n\n"
            "## Publication-time comparison\n\n"
            "The current paginated comparison, including drafts and retained main, was "
            "completed at `{{FRONTIER_OBSERVED_UTC}}`. The maximum comparable exact claim "
            "or reviewed conservative upper bound was `{{FRONTIER_MAXIMUM}}`. "
            "The frozen publication policy requires at least `1/100` relative improvement; "
            "the exact required saving was `{{MINIMUM_REQUIRED_KAPPA}}`. "
            "A contributor may publish after that check; this timestamp is not a promise "
            "of permanent record status.\n")


def normalize_frontier_rules(rules):
    """Adapt the scout's source-pinned schema without making new assessments.

    Source-only exact claims still need manual_exact_assessment=True supplied by
    the frozen release owner. No rounded title is parsed or promoted to fact.
    """
    rules = json.loads(json.dumps(rules))
    retained = rules["retained_main"]
    if "certificate_sources" not in retained:
        retained["certificate_sources"] = [
            {"repository": UPSTREAM, "ref": rules["base_sha"],
             "path": retained["certificate_path"],
             "decoded_sha256": retained["certificate_decoded_sha256"],
             "value_pointer": retained["certificate_value_pointer"]},
            {"repository": UPSTREAM, "ref": rules["base_sha"],
             "path": retained["selected_record_path"],
             "decoded_sha256": retained["selected_record_decoded_sha256"],
             "value_pointer": retained["selected_value_pointer"]}]
    # Only the runtime's public-source allowlist enters the standalone script.
    # Historical receipts and internal execution paths stay in the research record.
    source_keys = ("repository", "ref", "path", "decoded_sha256", "bytes", "value_pointer",
                   "value_kind", "manual_exact_assessment")
    def public_source(source):
        return {key: source[key] for key in source_keys if key in source}
    retained = {"exact_kappa": retained["exact_kappa"], "certificate_sources": [
        public_source(source) for source in retained["certificate_sources"]]}
    claim_keys = ("pr", "head_sha", "body_sha256", "title_sha256", "exact_kappa",
                  "certified_upper_bound", "excluded", "assessment_scope", "comparability",
                  "conditional_assumptions", "unresolved", "new_assumptions")
    claims = []
    for rule in rules["claims"]:
        item = {key: rule[key] for key in claim_keys if key in rule}
        item["certificate_source"] = public_source(rule["certificate_source"]) if rule.get("certificate_source") else None
        claims.append(item)
    result = {key: rules[key] for key in ("schema_version", "observed_utc", "upstream", "base_sha",
                                         "default_branch", "open_count") if key in rules}
    result.update(claims=claims, retained_main=retained)
    return result


def validate_spec(spec, payload_root):
    require_python()
    if spec.get("upstream") != UPSTREAM or spec.get("default_branch") != "main":
        raise Stop("This builder targets only CrocSwap/integer-mult-bounds, verified main")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,70}", spec.get("candidate_id", "")):
        raise Stop("Candidate ID must be portable lower-case kebab text")
    if not HEX40.fullmatch(spec.get("base_sha", "")):
        raise Stop("An exact verified base commit is required")
    if not HEX64.fullmatch(spec.get("candidate_digest", "")):
        raise Stop("An immutable scientific candidate SHA-256 is required")
    if not spec.get("synthetic_test_only"):
        if spec.get("status") not in {"ACCEPTED_CONDITIONAL", "PUBLICATION_READY"} or not spec.get("freeze_approved"):
            raise Stop("The coordinator must explicitly freeze an accepted conditional candidate")
        if any(spec.get("gates", {}).get(gate) is not True for gate in REQUIRED_GATES):
            raise Stop("A publication/reproduction gate is incomplete; no release script will be created")
    fraction(spec["exact_kappa"])
    if spec.get("minimum_relative_improvement") != MINIMUM_RELATIVE_IMPROVEMENT:
        raise Stop("Release must immutably require at least 1% relative improvement")
    improvement_factor = 1 + fraction(MINIMUM_RELATIVE_IMPROVEMENT)
    if not spec.get("source_fingerprints") or not spec.get("protected_base_paths"):
        raise Stop("Mathematical dependencies and inherited tests/licenses must be pinned")
    for inventory in (spec["source_fingerprints"], spec["protected_base_paths"]):
        for name, value in inventory.items():
            safe_path(name)
            if not HEX64.fullmatch(value):
                raise Stop("Invalid source/protected fingerprint")
    if not spec.get("changes"):
        raise Stop("No allowlisted publication changes")
    seen, files = set(), {}
    for item in spec["changes"]:
        name = safe_path(item["path"])
        if name in seen or name in spec["protected_base_paths"]:
            raise Stop("Duplicate/protected publication change")
        seen.add(name)
        if item["mode"] not in {0o644, 0o755} or not HEX64.fullmatch(item["sha256"]):
            raise Stop("Invalid publication mode/hash")
        before = item.get("before_sha256")
        if before is not None and (not HEX64.fullmatch(before) or before == item["sha256"]):
            raise Stop("Invalid/redundant replacement hash")
        if item.get("acquire"):
            acquisition = item["acquire"]
            if (not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", acquisition.get("repository", "")) or
                    not HEX40.fullmatch(acquisition.get("ref", "")) or
                    acquisition.get("decoded_sha256") != item["sha256"]):
                raise Stop("Downloaded source must have a declared immutable repository/ref/hash")
            safe_path(acquisition["path"])
            continue
        source = payload_root / name
        if source.is_symlink() or not source.is_file():
            raise Stop("Missing/linked payload file: " + name)
        if any(parent.is_symlink() for parent in source.parents if parent != payload_root.parent):
            raise Stop("Payload parents must not be symlinks")
        data = source.read_bytes()
        if len(data) > 1024 * 1024 or digest(data) != item["sha256"]:
            raise Stop("Allowlisted payload file size/hash disagrees: " + name)
        # The coordinator still reviews source/license/privacy scope. This catches
        # recognizable credentials and accidental machine-local publication text.
        if re.search(rb"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", data):
            raise Stop("Recognizable credential/private key in publication payload")
        if b"/srv/ai/" in data or b"/home/user/" in data:
            raise Stop("Machine-local/internal campaign path in publication payload")
        files["files/" + name] = (data, item["mode"])
    for check in spec.get("local_checks", []):
        command = check.get("command")
        if (not isinstance(command, list) or not command or
                any(not isinstance(arg, str) or "\x00" in arg for arg in command) or
                command[0] != "python3" or len(command) < 2):
            raise Stop("Local checks must be explicit Python 3 argv, never shell commands")
        safe_path(command[1])
        known_paths = seen | set(spec["source_fingerprints"]) | set(spec["protected_base_paths"])
        if command[1].startswith("-") or command[1] not in known_paths or not command[1].endswith(".py"):
            raise Stop("Local check script must be a declared, hashed Python file")
        if not 1 <= check.get("timeout_seconds", 0) <= 120:
            raise Stop("Publication-time checks must have a bounded lightweight timeout")
    rules = spec["frontier_rules"]
    if (rules.get("upstream") != UPSTREAM or rules.get("base_sha") != spec["base_sha"] or
            rules.get("default_branch") != spec["default_branch"]):
        raise Stop("Frontier rules are not pinned to this exact inspected base")
    claims = rules.get("claims", [])
    if len({r["pr"] for r in claims}) != len(claims) or not claims:
        raise Stop("Incomplete/duplicate frozen frontier inventory")
    if rules.get("open_count") != len(claims):
        raise Stop("Frozen frontier inventory count disagrees")
    for rule in claims:
        for key in ("head_sha", "body_sha256", "title_sha256"):
            if not (HEX40 if key == "head_sha" else HEX64).fullmatch(rule.get(key, "")):
                raise Stop("Frontier rule lacks pinned head/body/title")
        if rule.get("unresolved") or rule.get("new_assumptions"):
            raise Stop("Unresolved frontier assumptions close the publication gate")
        if not rule.get("assessment_scope"):
            raise Stop("Frontier assessment scope is missing")
        if not rule.get("excluded"):
            exact, upper = rule.get("exact_kappa"), rule.get("certified_upper_bound")
            if bool(exact) == bool(upper):
                raise Stop("Claim needs one exact value or explicitly reviewed conservative upper bound")
            if improvement_factor * fraction(exact or upper) > fraction(spec["exact_kappa"]):
                raise Stop("Frozen candidate is below the exact 1% publication threshold for a public claim/bound")
            if exact:
                source = rule.get("certificate_source")
                if not source or source.get("ref") != rule["head_sha"]:
                    raise Stop("Exact public claim must have a pinned certificate/source")
                if not source.get("value_pointer") and not source.get("manual_exact_assessment"):
                    raise Stop("Source-only claim needs explicit manual_exact_assessment")
    retained = rules["retained_main"]
    if improvement_factor * fraction(retained["exact_kappa"]) > fraction(spec["exact_kappa"]):
        raise Stop("Candidate is below the exact 1% publication threshold for retained main")
    if not retained.get("certificate_sources"):
        raise Stop("Retained main certificate inventory is missing")
    for source in retained["certificate_sources"]:
        if source.get("ref") != spec["base_sha"]:
            raise Stop("Retained main certificate ref disagrees with verified base")
    if not spec.get("title") or not spec.get("commit_message"):
        raise Stop("English public title and commit message are required")
    spec["prepared_body"] = prepared_body(spec)
    if any(marker in (spec["title"] + spec["prepared_body"]) for marker in
           ("/srv/", "/home/", "frontier-sprint-", "fast-integration-gpu-")):
        raise Stop("Internal campaign/machine terms in public title/body")
    return files


# This bootstrap is part of the plain script and runs before packaged code.
# It validates the complete compressed archive and every member, then performs
# manual extraction; tarfile.extract/extractall are intentionally never used.
BOOTSTRAP = r'''
import base64, hashlib, io, json, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path, PurePosixPath
mode = sys.argv[1]
workspace = Path(tempfile.mkdtemp(prefix="publication-__CANDIDATE__-"))
log = workspace / "bootstrap.log"
def note(message):
    import datetime
    line = "[" + datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds") + "] " + message
    print(line, flush=True)
    with log.open("a") as out: out.write(line + "\n")
def fail(message): raise RuntimeError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
try:
    note("Fresh workspace: " + str(workspace))
    if sys.version_info[:2] < (3, 11):
        fail("Python 3.11 or newer is required; finite package tested with Python 3.14.4")
    for dependency in ("bash", "git", "python3", "gh"):
        if not shutil.which(dependency): fail("Missing prerequisite: " + dependency + "; install it yourself before retrying")
    encoded = """__PAYLOAD__"""
    compressed = base64.b64decode("".join(encoded.split()), validate=True)
    if sha(compressed) != "__COMPRESSED_SHA__": fail("Compressed payload SHA-256 mismatch")
    entries = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(compressed), mode="r:gz") as archive:
        for entry in archive:
            name = entry.name
            if (not entry.isfile() or entry.size > 1048576 or not name or "\\" in name or
                    any(ord(character) < 32 for character in name) or
                    PurePosixPath(name).is_absolute() or
                    any(part in {"", ".", "..", ".git"} for part in name.split("/"))):
                fail("Unsafe archive member: " + repr(name))
            if name in entries: fail("Duplicate archive member")
            total += entry.size
            if total > 33554432: fail("Payload expansion exceeds size bound")
            entries[name] = archive.extractfile(entry).read()
    if sha(entries.get("manifest.json", b"")) != "__MANIFEST_SHA__": fail("Manifest SHA-256 mismatch")
    manifest = json.loads(entries["manifest.json"])
    expected = manifest["members"]
    if set(entries) != set(expected) | {"manifest.json"}: fail("Archive member allowlist mismatch")
    for name, item in expected.items():
        if sha(entries[name]) != item["sha256"] or len(entries[name]) != item["bytes"]:
            fail("Member SHA-256/size mismatch: " + name)
        if item["mode"] not in (420, 493): fail("Unexpected member permissions")
    if sha(entries.get("publication_runtime.py", b"")) != "__RUNTIME_SHA__": fail("Driver SHA-256 mismatch")
    package = workspace / "package"
    package.mkdir(mode=0o700)
    for name, data in entries.items():
        target = package / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o600 if name == "manifest.json" else expected[name]["mode"])
    note("Archive paths, allowlist and all hashes verified before packaged code")
    result = subprocess.run([sys.executable, str(package / "publication_runtime.py"),
                             mode, str(package), str(workspace)])
    if result.returncode: fail("Packaged driver exited " + str(result.returncode))
    note("Completed; workspace/logs retained: " + str(workspace))
except Exception as exc:
    note("STOPPED: " + type(exc).__name__ + ": " + str(exc))
    note("Workspace/logs retained after failure: " + str(workspace))
    sys.exit(1)
'''


def build(spec, payload_root, output):
    if output.exists():
        raise Stop("Delivered/generated scripts are immutable; choose a fresh output identity")
    # Avoid mutating the caller's in-memory fixture/specification.
    spec = json.loads(json.dumps(spec))
    spec["frontier_rules"] = normalize_frontier_rules(spec["frontier_rules"])
    files = validate_spec(spec, payload_root)
    runtime = Path(__file__).with_name("publication_runtime.py").read_bytes()
    files["publication_runtime.py"] = (runtime, 0o644)
    members = {name: {"sha256": digest(data), "bytes": len(data), "mode": mode}
               for name, (data, mode) in sorted(files.items())}
    manifest = json.dumps({"schema_version": 1, "release": spec, "members": members},
                          sort_keys=True, separators=(",", ":")).encode()
    if len(manifest) > 1024 * 1024:
        raise Stop("Manifest exceeds the bootstrap member limit")
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for name, (data, mode) in {"manifest.json": (manifest, 0o600), **files}.items():
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime, info.uid, info.gid = len(data), mode, 0, 0, 0
            tar.addfile(info, io.BytesIO(data))
    compressed = gzip.compress(archive.getvalue(), mtime=0)
    if len(compressed) > MAX_PAYLOAD:
        raise Stop("Compressed payload exceeds the standalone-script budget")
    encoded = base64.b64encode(compressed).decode()
    encoded = "\n".join(encoded[i:i + 100] for i in range(0, len(encoded), 100))
    bootstrap = (BOOTSTRAP.replace("__CANDIDATE__", spec["candidate_id"])
                 .replace("__PAYLOAD__", encoded).replace("__COMPRESSED_SHA__", digest(compressed))
                 .replace("__MANIFEST_SHA__", digest(manifest)).replace("__RUNTIME_SHA__", digest(runtime)))
    shell = ("#!/usr/bin/env bash\nset -euo pipefail\n"
             "if ! command -v python3 >/dev/null 2>&1; then printf 'Missing prerequisite: python3; install it yourself before retrying.\\n' >&2; exit 1; fi\n"
             "python3 -c 'import datetime; print(\"[\" + datetime.datetime.now(datetime.timezone.utc).isoformat(timespec=\"seconds\") + \"] Starting frozen publication package\", flush=True)'\n"
             "mode=publish\nif (( $# > 1 )); then printf 'Use no argument, --check, --dry-run or --self-test\\n' >&2; exit 2; fi\n"
             "if (( $# == 1 )); then\n  case \"$1\" in\n"
             "    --check|--dry-run|--self-test) mode=\"$1\" ;;\n"
             "    --help) printf 'Default: publish after guards. --check: local integrity. --dry-run: read-only GitHub + prepared clone. --self-test: local integrity/path/arithmetic. Requires Bash, Git, Python 3.11+, authenticated gh; finite package tested with Python 3.14.4.\\n'; exit 0 ;;\n"
             "    *) printf 'Unknown argument: %s\\n' \"$1\" >&2; exit 2 ;;\n  esac\nfi\n"
             "python3 - \"$mode\" <<'PUBLICATION_BOOTSTRAP'\n" + bootstrap + "PUBLICATION_BOOTSTRAP\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as file:
        file.write(shell)
    output.chmod(0o755)
    return {"script": str(output), "sha256": digest(shell.encode()),
            "compressed_payload_sha256": digest(compressed), "manifest_sha256": digest(manifest),
            "runtime_sha256": digest(runtime), "bytes": len(shell.encode()),
            "synthetic_test_only": bool(spec.get("synthetic_test_only"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--payload-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(json.loads(args.spec.read_text()), args.payload_root.resolve(), args.output), indent=2))


if __name__ == "__main__":
    main()
