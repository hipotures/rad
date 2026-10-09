#!/usr/bin/env python3
"""Copy the distinct historical 168/170 checkpoint into a prepared upstream clone.

Only local reads and explicit package-file copies are performed. The coordinator
creates the exact-base Git clone; this helper performs no Git mutations, network
access, scientific freeze or release-script generation. All inventory paths are
relative to the research sprint or the isolated upstream repository.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

from publication_runtime import safe_path

BASE = "d1d6c070f5a8c684727ee7ec35d930f9ebfa9758"
IDENTITY = "balanced-lifetime-fused-168-170-20261009"
PACKAGE = "research/lifetime-fused-frames"
COMMITS = {"pr168": "98c115b53742b6613ad630de4d493f37b0119da7",
           "pr170": "29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4"}
PRIVATE = (b"/srv/ai/", b"/home/user/", b"frontier-sprint-", b"fast-integration-gpu-",
           b"work/frontier/", b"agents/transfer/", b"agents/signed/", b"work/placement/")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    sprint = args.sprint.resolve()
    destination = sprint / "work/publication/qualifying168-provisional/repository"
    if not (destination / ".git").is_dir():
        raise ValueError("The coordinator must prepare the isolated exact-base clone")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination).decode().strip()
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=destination).decode().strip()
    if head != BASE or origin != "https://github.com/CrocSwap/integer-mult-bounds.git":
        raise ValueError("Unexpected upstream base or origin; no automatic rebase is allowed")
    roots = {}
    for label in COMMITS:
        source = json.loads((sprint / f"agents/frontier/{label}-archive-manifest.json").read_text())
        if source["head_sha"] != COMMITS[label]:
            raise ValueError("Immutable predecessor manifest moved: " + label)
        roots[label] = Path(source["extracted_root"])
    records, contents = {}, {}

    def put(name, source, provenance, expected=None):
        name = safe_path(PACKAGE + "/" + safe_path(name))
        if source.is_symlink() or not source.is_file():
            raise ValueError("Missing/linked source: " + str(source))
        data = source.read_bytes()
        if expected and digest(data) != expected:
            raise ValueError("Input fingerprint moved: " + str(source))
        inspected = gzip.decompress(data) if source.name.endswith(".gz") else data
        if any(marker in inspected for marker in PRIVATE):
            raise ValueError("Internal provenance must be normalized before export: " + str(source))
        if name in contents and contents[name] != data:
            raise ValueError("Conflicting source closure: " + name)
        mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
        records[name] = dict(path=name, sha256=digest(data), bytes=len(data), mode=mode,
                             source=source.relative_to(sprint).as_posix(), provenance=provenance)
        contents[name] = data

    bit = sprint / "agents/bit/candidates/binary-168-paired-lifetime-p12"
    inputs = json.loads((bit / "source-inputs.json").read_text())
    manifest = json.loads((bit / "fixture-manifest.json").read_text())
    for label, key in (("pr168", "source168"), ("pr170", "source170")):
        if inputs[key]["commit"] != COMMITS[label]:
            raise ValueError("Binary predecessor identity moved")
        for name, pin in inputs[key]["files"].items():
            put("sources/" + label + "/" + name, roots[label] / name,
                inputs[key]["repository"] + "@" + COMMITS[label], pin["sha256"])
    for name in manifest["code"]:
        put("binary/" + name, bit / name, "Binary constructor/replay", manifest["code"][name]["sha256"])
    for pin in manifest["fixtures"].values():
        put("binary/" + pin["path"], bit / pin["path"], "Complete frozen binary fixture", pin["gzip_sha256"])
        raw = gzip.decompress((bit / pin["path"]).read_bytes())
        if digest(raw) != pin["sha256"] or len(raw) != pin["bytes"]:
            raise ValueError("Decoded binary fixture changed")
    for name in ("source-inputs.json", "fixture-manifest.json", "proof.md", "NOTICE.md", "adapted-source-provenance.json"):
        put("binary/" + name, bit / name, "Binary source/proof/attribution metadata")

    complex_data = sprint / "agents/signed/fixtures/fused168-98c115b-raised"
    cm = json.loads((complex_data / "manifest.json").read_text())
    if cm["source_head"] != COMMITS["pr168"]:
        raise ValueError("Complex predecessor identity moved")
    for name, pin in cm["fixture_pins"].items():
        put("complex/data/" + name, complex_data / name, "Frozen coherent complex fixture", pin["sha256"])
    put("complex/data/manifest.json", complex_data / "manifest.json", "Normalized public complex provenance")
    for name, pin in cm["original_source_pins"].items():
        put("sources/pr168/" + name, roots["pr168"] / name, "eumemic/integer-mult-bounds@" + COMMITS["pr168"], pin)
    for name in ("reconstruct_complex.py", "screen_pr168_modules.py", "check_pr165_signed_control.py",
                 "audit_scalar_bounds.py", "interval_moments.py", "enclose_finite_export.py"):
        put("complex/code/" + name, sprint / "agents/signed/code" / name, "Complex author and exact scalar/moment checks")
    put("independent/code/exact_aliased_core.py", sprint / "agents/baseline/code/exact_aliased_core.py", "Independent exact arbitrary-dirty scalar kernel")

    gp = sprint / "agents/geometry/configs/fused168-portable-public-pins.json"
    geometry = json.loads(gp.read_text())
    # Source/proof paths are explicit in the original reviewed geometry map;
    # the normalized public map intentionally contains no workspace path list.
    original = json.loads((sprint / "agents/geometry/configs/fused168-joint-raise-winner-pins.json").read_text())
    for key, name in original["paths"].items():
        source = sprint / name
        if roots["pr168"] in source.parents:
            put("sources/pr168/" + source.relative_to(roots["pr168"]).as_posix(), source,
                "Original source/proof geometry dependency", geometry["sha256"][key])
    put("independent/complex-pins.json", gp, "Normalized independent geometry provenance")
    for name in ("reflected_paid_replay_fused168.py", "portable_complex_reflection.py"):
        put("independent/code/" + name, sprint / "agents/geometry/code" / name, "Independent literal and reflected finite replay")

    transfer = sprint / "agents/transfer/publication/lifetime-fused-frames/transfer"
    for source in sorted(transfer.rglob("*")):
        if source.is_file() and "__pycache__" not in source.parts:
            put("transfer/" + source.relative_to(transfer).as_posix(), source, "Coherent conditional transfer arithmetic/proof")

    # Preserve the original supplier provenance and PR117 source/license
    # closure used by the retained h20 module. This does not claim that the
    # full 141-source arithmetic acceptance was rerun by this compact export.
    science = json.loads((sprint / "agents/transfer/configs/lifetime-fused-168-170.json").read_text())
    for name, pin in science["sources"].items():
        if name.startswith("references/three-stage-cover/pr117/") or name == "references/partial-gauge/pr97/SOURCE.json":
            put("sources/pr168/" + name, roots["pr168"] / name,
                "Retained original supplier proof/source/license", pin["sha256"])
    for label in COMMITS:
        put("sources/" + label + "/NOTICE", roots[label] / "NOTICE",
            "Original upstream attribution retained")

    for name in ("review_public_fused.py", "review_fused_lifetime.py",
                 "review_balanced_unified.py", "review_rebuilt168_ceiling.py"):
        put("independent/code/" + name, sprint / "agents/assembly/code" / name,
            "Independent portable arithmetic; no author arithmetic imports")
    for name in ("NOTICE", "LICENSE"):
        put("independent/" + name, sprint / "agents/assembly" / name,
            "Independent arithmetic source/license attribution")
    metadata = sprint / "agents/publication/fixtures/lifetime-fused-package"
    for name in ("README.md", "NOTICE"):
        put(name, metadata / name, "Public checkpoint scope and attribution")
    put("LICENSE", roots["pr168"] / "LICENSE", "Inherited Apache-2.0 retained")

    # The public inventory deliberately omits the local recovery paths kept
    # in the research-only export receipt. It records its own generation
    # rule instead of recursively attempting to hash itself.
    public = dict(schema_version=1, candidate_id=IDENTITY, package_alias=PACKAGE,
                  status="HISTORICAL_CONDITIONAL_CHECKPOINT", exact_kappa="61728289/100000000000",
                  minimum_relative_improvement="1/100", publication_eligible=False,
                  predecessors={label: dict(repository=inputs[key]["repository"], commit=COMMITS[label])
                                for label, key in (("pr168", "source168"), ("pr170", "source170"))},
                  files=[{key: row[key] for key in ("path", "sha256", "bytes", "mode", "provenance")}
                         for row in sorted(records.values(), key=lambda item: item["path"])],
                  inventory_scope="Every exported file except SOURCE.json itself. Original full 141-source/24-input acceptance is separate; this compact package includes executable component closure and public arithmetic metadata.")
    source_name = PACKAGE + "/SOURCE.json"
    data = (json.dumps(public, indent=2, sort_keys=True) + "\n").encode()
    contents[source_name] = data
    records[source_name] = dict(path=source_name, sha256=digest(data), bytes=len(data), mode=0o644,
                               source="agents/publication/code/prepare_lifetime_fused_export.py",
                               provenance="Generated path-clean public package inventory")

    # Collect and validate the complete package before writing any byte.
    inherited = subprocess.check_output(["git", "ls-files", "--", PACKAGE], cwd=destination)
    if inherited:
        raise ValueError("The historical checkpoint must use a new upstream package path")
    for name in contents:
        target = destination / name
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
            raise ValueError("Symlink in export destination")
    for name, data in contents.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(records[name]["mode"])
    observed = dt.datetime.now(dt.timezone.utc)
    inventory = dict(schema_version=1, candidate_id=IDENTITY, package_alias=PACKAGE,
                     status="HISTORICAL_PROVISIONAL_EXPORT", freeze_approved=False,
                     base_sha=BASE, created_utc=observed.isoformat(), exact_kappa="61728289/100000000000",
                     minimum_relative_improvement="1/100", publication_eligible=False,
                     destination=destination.relative_to(sprint).as_posix(), entries=sorted(records.values(), key=lambda row: row["path"]))
    path = sprint / "work/publication" / ("lifetime-fused-export-" + observed.strftime("%Y%m%dT%H%M%SZ") + ".json")
    with path.open("x") as output:
        json.dump(inventory, output, indent=2); output.write("\n")
    print(json.dumps(dict(inventory=path.relative_to(sprint).as_posix(), files=len(records),
                          bytes=sum(row["bytes"] for row in records.values()), status=inventory["status"])))


if __name__ == "__main__":
    main()
