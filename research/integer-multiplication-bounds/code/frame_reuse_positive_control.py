#!/usr/bin/env python3
"""Small positive control showing one valid retained-controller link."""
import json

from frame_reuse import labels, optimize_chains, compile_reuse, check, independent_spaces


class Control:
    n = 9
    inputs = [(0, 1), (2, 3), (4, 5)]
    variables = {pair: index+1 for index, pair in enumerate(inputs)}
    args = [None, None, None, None, (1, 2), (1, 3), (2, 5)]
    active = set(range(1, 7))
    additions = 3
    outputs = {(4, 5): 4, (6, 7): 6}


if __name__ == "__main__":
    circuit = Control()
    frames, _ = labels(circuit)
    compiled = compile_reuse(circuit, frames, optimize_chains(circuit, frames, "id"))
    result = {"original_roles": 5, "roles": compiled["roles"],
              "chains": compiled["chain_summary"], "check": check(circuit, frames, compiled),
              "independent": independent_spaces(circuit, frames)}
    assert compiled["roles"] == 4 and compiled["chain_summary"]["selected_links"] == 1
    print(json.dumps(result, indent=2))
