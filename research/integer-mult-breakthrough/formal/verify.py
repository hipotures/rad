#!/usr/bin/env python3
"""Build actual Lean proofs, audit dependencies, and exercise rejection controls."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN = re.compile(r"\b(?:sorry|admit|native_decide|axiom|unsafe|implemented_by)\b")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def without_comments(text: str) -> str:
    """Remove nested Lean block comments and line comments for source linting."""
    output = []
    depth = 0
    index = 0
    while index < len(text):
        pair = text[index:index + 2]
        if pair == "/-":
            depth += 1
            output.append(" ")
            index += 2
        elif depth and pair == "-/":
            depth -= 1
            index += 2
        elif not depth and pair == "--":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
        else:
            if not depth or text[index] == "\n":
                output.append(text[index])
            index += 1
    require(depth == 0, "Unclosed Lean comment")
    return "".join(output)


def audit_axioms(text: str, expected: set[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    pattern = r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
    for match in re.finditer(pattern, text, flags=re.MULTILINE):
        name = match.group(1)
        require(name not in found, f"Duplicate axiom result: {name}")
        dependencies = [x.strip() for x in (match.group(2) or "").split(",") if x.strip()]
        unexpected = set(dependencies) - ALLOWED_AXIOMS
        require(not unexpected, f"Unapproved axioms for {name}: {sorted(unexpected)}")
        found[name] = dependencies
    require(set(found) == expected, f"Axiom coverage mismatch: expected {sorted(expected)}, found {sorted(found)}")
    return found


def source_checks() -> tuple[dict, set[str], dict[str, str]]:
    coverage = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    expected = set(coverage["theorems"])
    require(expected and len(expected) == len(coverage["theorems"]), "Empty or duplicate theorem registry")
    declared = set()
    fingerprints = {}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in {".lake", "__pycache__", ".git"} for part in relative.parts) or not path.is_file():
            continue
        require(not path.is_symlink(), f"Symlink is not a formal source: {relative}")
        fingerprints[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
        if path.suffix != ".lean":
            continue
        source = without_comments(path.read_text(encoding="utf-8"))
        require(not FORBIDDEN.search(source), f"Unapproved proof construct: {relative}")
        for name in re.findall(r"^(?:theorem|lemma)\s+([A-Za-z][A-Za-z0-9_]*)", source, flags=re.MULTILINE):
            qualified = coverage["namespace"] + "." + name
            require(qualified not in declared, f"Duplicate declaration: {qualified}")
            declared.add(qualified)
    require(declared == expected, "Every declared theorem must have a coverage entry")
    return coverage, expected, fingerprints


def command(argv: list[str], logfile: Path, timeout: int = 900) -> subprocess.CompletedProcess:
    result = subprocess.run(argv, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout)
    logfile.write_text(result.stdout, encoding="utf-8")
    print(result.stdout[-20000:], flush=True)
    return result


def verify(output: Path) -> int:
    require(not output.exists(), f"Refusing to overwrite evidence: {output}")
    output.mkdir(parents=True)
    report = {"status": "fail", "scope": "Listed general finite-matrix lemmas and exact boundary examples only"}
    started = time.monotonic()
    try:
        coverage, names, fingerprints = source_checks()
        report.update(coverage=coverage, inputs_sha256=fingerprints,
                      allowed_axioms=sorted(ALLOWED_AXIOMS))
        version = command(["lake", "env", "lean", "--version"], output / "lean-version.log")
        require(version.returncode == 0 and "version 4.31.0" in version.stdout, "Unexpected Lean toolchain")
        report["lean_version"] = version.stdout.strip()
        lock = json.loads((ROOT / "lake-manifest.json").read_text())
        for package in lock["packages"]:
            actual = subprocess.check_output(["git", "-C", str(ROOT / ".lake/packages" / package["name"]),
                                              "rev-parse", "HEAD"], text=True).strip()
            require(actual == package["rev"], f"Dependency revision mismatch: {package['name']}")
        built = command(["lake", "build"], output / "build.log")
        require(built.returncode == 0, "Lean proof build failed")
        with tempfile.TemporaryDirectory(prefix="rad-lean-audit-") as temp:
            audit = Path(temp) / "Audit.lean"
            audit.write_text("import RaD\n" + "\n".join(
                f"#check {name}\n#print axioms {name}" for name in sorted(names)) + "\n", encoding="utf-8")
            compiled = command(["lake", "env", "lean", "-DwarningAsError=true", str(audit)], output / "axioms.log")
            require(compiled.returncode == 0, "Lean theorem/axiom extraction failed")
            report["axioms"] = audit_axioms(compiled.stdout, names)
            bad = Path(temp) / "FalseEquality.lean"
            bad.write_text("import RaD\nexample : (1 : Nat) = 2 := by decide\n", encoding="utf-8")
            rejected = command(["lake", "env", "lean", str(bad)], output / "negative-false-equality.log")
            require(rejected.returncode != 0, "False equality was unexpectedly accepted")
            missing = Path(temp) / "MissingProof.lean"
            missing.write_text("import RaD\nexample : False := by sorry\n", encoding="utf-8")
            rejected = command(["lake", "env", "lean", "-DwarningAsError=true", str(missing)], output / "negative-missing-proof.log")
            require(rejected.returncode != 0, "Missing proof was unexpectedly accepted")
            injected = Path(temp) / "InjectedAxiom.lean"
            injected.write_text("import RaD\naxiom injectedAxiom : False\ntheorem injected : False := injectedAxiom\n#print axioms injected\n", encoding="utf-8")
            result = command(["lake", "env", "lean", str(injected)], output / "negative-injected-axiom.log")
            require(result.returncode == 0, "Custom-axiom rejection control did not reach the auditor")
            try:
                audit_axioms(result.stdout, {"injected"})
            except ValueError:
                pass
            else:
                raise ValueError("Injected axiom was not rejected by the axiom policy")
        _, _, after = source_checks()
        require(fingerprints == after, "Verification changed a source or dependency lock")
        report.update(status="pass", theorem_count=len(names),
                      negative_controls=["false-equality-rejected", "missing-proof-rejected", "injected-axiom-rejected"],
                      not_proved=coverage["not_proved"])
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        report["error"] = str(error)
        print(f"ERROR: {error}", file=sys.stderr)
    finally:
        report["seconds"] = round(time.monotonic() - started, 3)
        report["commit"] = os.environ.get("GITHUB_SHA", "local-run")
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        summary = (f"## Lean formal lemmas: {report['status']}\n\n"
                   f"Theorems audited: {report.get('theorem_count', 0)}.\n\n"
                   "Coverage: finite real nonnegative-matrix obstruction, arbitrary finite level words, "
                   "nonnegative added work, and exact boundary examples.\n\n"
                   "This does not formalize a multiplication exponent, log/exp enclosures, "
                   "physical frames, or the all-size machine theorem.\n")
        if "error" in report:
            summary += "\nError: " + report["error"] + "\n"
        (output / "summary.md").write_text(summary, encoding="utf-8")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
                handle.write(summary)
    return 0 if report["status"] == "pass" else 1


class AuditorTests(unittest.TestCase):
    def test_standard_dependencies(self):
        self.assertEqual(audit_axioms("'X.t' depends on axioms: [propext, Classical.choice, Quot.sound]", {"X.t"})["X.t"],
                         ["propext", "Classical.choice", "Quot.sound"])
    def test_axiom_free(self):
        self.assertEqual(audit_axioms("'X.t' does not depend on any axioms", {"X.t"}), {"X.t": []})
    def test_reject_extra_axioms(self):
        for axiom in ("sorryAx", "fake", "Lean.ofReduceBool", "X._native"):
            with self.subTest(axiom=axiom), self.assertRaises(ValueError):
                audit_axioms(f"'X.t' depends on axioms: [{axiom}]", {"X.t"})
    def test_require_all_theorems(self):
        with self.assertRaises(ValueError):
            audit_axioms("", {"X.t"})
    def test_reject_duplicates(self):
        with self.assertRaises(ValueError):
            audit_axioms("'X.t' does not depend on any axioms\n" * 2, {"X.t"})
    def test_nested_comments(self):
        self.assertFalse(FORBIDDEN.search(without_comments("/- no sorry /- axiom -/ here -/\n-- admit\ntheorem t : True := True.intro")))
        self.assertTrue(FORBIDDEN.search(without_comments("theorem t : False := by sorry")))
    def test_registry_and_sources(self):
        _, names, _ = source_checks()
        self.assertEqual(len(names), 11)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(AuditorTests)
        sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
    directory = args.output or Path(tempfile.mkdtemp(prefix="rad-lean-")) / "evidence"
    sys.exit(verify(directory))
