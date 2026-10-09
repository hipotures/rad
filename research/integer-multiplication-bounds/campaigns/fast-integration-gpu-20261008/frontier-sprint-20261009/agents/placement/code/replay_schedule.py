#!/usr/bin/env python3
"""Regenerate the unchanged PR120 scalar DAG with an explicit new placement."""
import argparse
import json
import os
from pathlib import Path
from screen_placement import read_module, require


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--schedule", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), "attempt already exists")
    args.output.mkdir(parents=True)
    module = read_module(args.source)
    saved = json.loads(args.schedule.read_text())
    placed = {int(s): module.sat_basis(X) for s, X in saved["placed"].items()}

    def placement(cand, reach):
        for s, X in placed.items():
            require(s in cand and module.sat_contained(X, module.sat_basis(cand[s])), "ineligible saved frame")
        return placed

    module.saturated_placement = placement
    module.WRITE = True
    module.OUT = args.output / "complex-profile.json"
    os.environ["DEFER_DUMP"] = str(args.output / "word.json")
    module.main()


if __name__ == "__main__":
    main()
