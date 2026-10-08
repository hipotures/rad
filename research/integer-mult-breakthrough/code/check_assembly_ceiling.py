#!/usr/bin/env python3
"""Verify exact consequences of explicitly ASSUMED frozen assembly inequalities.

This is an arithmetic regression, not a certificate for an integer multiplier.
The inherited algorithm and all-size proof are not executed or proved here.
"""
from fractions import Fraction as Q
import argparse
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def rational(value):
    if not isinstance(value, str):
        raise ValueError("Exact rationals must be strings, not floating-point values")
    return Q(value)


def derive(b, beta, target):
    if not (0 < b < 1 and 0 < beta < 1 and 0 < target < 1):
        raise ValueError("Parameters must lie strictly between zero and one")
    limit_a = (1-beta)*b
    return {"a_strict_upper_bound": str(limit_a),
            "kappa_strict_upper_bound": str(limit_a/(1+limit_a)),
            "required_a_strict_lower_bound": str(target/(1-target)),
            "required_b_strict_lower_bound": str(target/((1-target)*(1-beta)))}


def verify(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("scope") != "arithmetic-under-assumed-inequalities":
        raise ValueError("Wrong certificate version or scientific scope")
    if data.get("assumptions") != ["a < (1-beta)*b", "kappa < a/(1+a)"]:
        raise ValueError("The frozen assumptions were changed")
    result = derive(*(rational(data[key]) for key in ("b", "beta", "target_kappa")))
    if data.get("derived") != result:
        raise ValueError("Recorded exact consequences do not match independent arithmetic")
    if rational(result["kappa_strict_upper_bound"]) >= rational(data["target_kappa"]):
        raise ValueError("This fixture does not establish the stated scoped obstruction")
    return {"status": "pass", "scope": data["scope"], "derived": result,
            "not_proved": "Underlying assembly, native constructions, all-size transfer, or a new kappa result"}


class ArithmeticTests(unittest.TestCase):
    def test_exact_bounds(self):
        row = derive(Q(717,10**7), Q(1,20), Q(1,10000))
        self.assertEqual(row["required_a_strict_lower_bound"], "1/9999")
        self.assertEqual(row["required_b_strict_lower_bound"], "20/189981")
        self.assertLess(Q(row["kappa_strict_upper_bound"]), Q(1,10000))

    def test_monotonicity(self):
        for a in (Q(1,100000), Q(1,10000), Q(1,10)):
            self.assertLess(a/(1+a), (2*a)/(1+2*a))

    def test_target_threshold_is_strict(self):
        target = Q(1,10000)
        boundary = target/(1-target)
        self.assertEqual(boundary/(1+boundary), target)
        self.assertLess((boundary/2)/(1+boundary/2), target)

    def test_float_rejected(self):
        with self.assertRaises(ValueError):
            rational(0.0001)

    def test_invalid_parameters(self):
        for args in ((0,Q(1,20),Q(1,10000)), (Q(1,10),1,Q(1,10000)), (Q(1,10),Q(1,20),1)):
            with self.assertRaises(ValueError):
                derive(*args)

    def test_fixture(self):
        self.assertEqual(verify(HERE.parent/"fixtures/frozen-assembly-ceiling.json")["status"], "pass")

    def test_corrupted_fixture_rejected(self):
        import tempfile
        source = HERE.parent/"fixtures/frozen-assembly-ceiling.json"
        row = json.loads(source.read_text())
        row["derived"]["required_a_strict_lower_bound"] = "1/10000"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bad.json"
            path.write_text(json.dumps(row))
            with self.assertRaises(ValueError):
                verify(path)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--certificate", type=Path, default=HERE.parent/"fixtures/frozen-assembly-ceiling.json")
        args = parser.parse_args()
        try:
            print(json.dumps(verify(args.certificate), indent=2))
        except (ValueError, OSError, KeyError) as error:
            parser.exit(1, f"FAIL: {error}\n")
