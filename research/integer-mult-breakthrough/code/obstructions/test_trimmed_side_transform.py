#!/usr/bin/env python3
"""Complete small coefficient replay and actual DAG corruption controls."""
from copy import deepcopy
import unittest

from trimmed_side_transform import build_dag, evaluate


class TrimmedControls(unittest.TestCase):
    def setUp(self):
        self.dag = build_dag(8, 5)
        self.source = self.dag["top"][0]
        self.inputs = [8] + [0] * (len(self.dag["top"]) - 1)
        # Independently specified side coefficients, scaled by eight.
        self.expected = [(-3, 0, 1, 0, -3, 0)[(m & self.source).bit_count()]
                         for m in self.dag["top"]]

    def test_every_source_and_target(self):
        for j, source in enumerate(self.dag["top"]):
            xs = [0] * len(self.dag["top"])
            xs[j] = 8
            expected = [(-3, 0, 1, 0, -3, 0)[(m & source).bit_count()]
                        for m in self.dag["top"]]
            self.assertEqual(evaluate(self.dag, xs), expected)

    def test_corrupt_actual_scalar_gate(self):
        dag = deepcopy(self.dag)
        for i, node in enumerate(dag["nodes"]):
            if node[0] == "scale" and node[2:] == (-3, 8):
                dag["nodes"][i] = ("scale", node[1], -2, 8)
                break
        else:
            self.fail("Missing total-feature scale")
        self.assertNotEqual(evaluate(dag, self.inputs), self.expected)

    def test_omitted_identity_feature_is_rejected(self):
        dag = deepcopy(self.dag)
        old = dag["outputs"][0]
        dag["nodes"].append(("scale", 0, -1, 1))
        dag["nodes"].append(("add", old, len(dag["nodes"]) - 1))
        dag["outputs"][0] = len(dag["nodes"]) - 1
        wrong = evaluate(dag, self.inputs)
        self.assertNotEqual(wrong, self.expected)
        self.assertEqual(wrong[0], -8)

    def test_complete_event_accounting(self):
        counts = self.dag["counts"]
        for phase in ("superset", "subset"):
            self.assertEqual(sum(counts.get(phase + suffix, 0) for suffix in
                ("_additions", "_zero_source_skips", "_zero_destination_aliases")),
                self.dag["raw_edges_per_pass"])
        self.assertEqual(len(self.dag["nodes"]), len(self.dag["top"]) +
                         counts["superset_additions"] + counts["subset_additions"] +
                         counts["nonunit_scalar_gates"])


if __name__ == "__main__":
    unittest.main()
