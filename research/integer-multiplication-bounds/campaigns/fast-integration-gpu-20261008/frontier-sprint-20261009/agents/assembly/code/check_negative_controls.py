#!/usr/bin/env python3
"""Cheap adversarial controls for the candidate certificate entry point.

Apache-2.0. Prepared for RaD with OpenAI GPT-6.1 Sol assistance.
These are entry-point/arithmetic guards, separate from the independent
finite word, signed reflection and paid-incidence mutation controls.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import certify_placement as c


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    c.require(not args.output.exists(), "Refusing to replace a receipt")
    controls = {}

    def rejects(name, function):
        try:
            function()
        except (ValueError, FileNotFoundError):
            controls[name] = "REJECTED"
        else:
            raise ValueError("Negative control accepted: "+name)

    with tempfile.TemporaryDirectory(prefix="placement-negative-") as d:
        root = Path(d)
        for name, payload in (
            ("negative_operation_index", [[-1, [1]]]),
            ("outside_operation_index", [[2, [1]]]),
            ("boolean_operation_index", [[True, [1]]]),
            ("duplicate_operation_index", [[0, [1]], [0, [2]]]),
            ("negative_frame_vector", [[0, [-1]]]),
            ("outside_frame_vector", [[0, [4]]]),
        ):
            p = root/(name+".json")
            p.write_text(json.dumps(payload))
            rejects(name, lambda p=p: c.validated_frames(p, [0, 1], 2))
        (root/"source.py").write_text("changed source\n")
        rejects("source_corruption", lambda: c.source_check(root, {"source_sha256": {"source.py": "0"*64}}))
        rejects("unsafe_source_path", lambda: c.source_check(root, {"source_sha256": {"../source.py": "0"*64}}))

    bridge = {"semantic": {"strict_literal_gap": 1, "C0": 1}, "rows": {"degree_gap": 1}}
    rejects("predecessor_unweakened_bit_claim", lambda: c.assembly(c.AB, Q(5885669, 10**10), bridge, Q(0)))
    valid = c.assembly(c.AB, c.AC, bridge, c.KAPPA)
    rejects("kappa_at_minimum", lambda: c.assembly(c.AB, c.AC, bridge, valid["minimum_margin"]))
    rejects("kappa_above_minimum", lambda: c.assembly(c.AB, c.AC, bridge, valid["minimum_margin"]+Q(1, 10**12)))
    rejects("nonpositive_literal_guard", lambda: c.assembly(c.AB, c.AC,
        {"semantic": {"strict_literal_gap": 0, "C0": 1}, "rows": {"degree_gap": 1}}, c.KAPPA))
    optimized = subprocess.run([sys.executable, "-O", str(Path(c.__file__).resolve()), "--help"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    c.require(optimized.returncode != 0 and b"Assertion-disabled" in optimized.stderr, "Optimized Python accepted")
    controls["assertion_disabled_execution"] = "REJECTED"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status="PASS", controls=controls,
        scope="Certificate input and strict assembly guards; independent word/reflection controls are separate"),
        indent=2, sort_keys=True)+"\n")
    print("PASS "+str(len(controls))+" adversarial entry-point/assembly controls")


if __name__ == "__main__":
    main()
