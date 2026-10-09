#!/usr/bin/env python3
"""Reconstruct one current physical frame plan and check exact prime units.

Frame fixtures encode every difference from the named node frames. Therefore
the replay resets to those frames before applying the complete fixture, even
when the starting public physical word already had operation-frame changes.
Prepared for RaD with OpenAI assistance; inherited source licenses persist.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
from bit_current_control import need, sha, read, modules, HEAD
from bit_current_discriminators import physical_experiment
from audit_bit_projectors import audit


def main():
    need(not sys.flags.optimize, 'assertions enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--source170', type=Path, required=True)
    ap.add_argument('--control', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = time.monotonic()
    need(not args.output.exists(), 'fresh exact audit directory')
    args.output.mkdir(parents=True)
    _, physical, lifetime, _ = modules(args.source.resolve(), args.source170.resolve())
    e = physical_experiment(lifetime, physical, args.control.resolve())
    plan = args.candidate / 'selected/frames.json'
    expected = read(args.candidate / 'selected/profile.json')
    e.frames = list(e.base_frames)
    e.load(plan, require_pins=True)
    recomputed = e.verified_profile(replay=True)
    need(recomputed == expected, 'complete plan replay, full F2 and histogram match the saved candidate')
    result = audit(e)
    result.update(source_head=HEAD, verified_utc=datetime.now(timezone.utc).isoformat(),
                  candidate_plan_sha256=sha(plan), candidate_profile_sha256=sha(args.candidate / 'selected/profile.json'),
                  code_sha256={p.name: sha(p) for p in [Path(__file__), Path(__file__).with_name('audit_bit_projectors.py'),
                            Path(__file__).with_name('bit_current_discriminators.py'), Path(__file__).with_name('bit_current_control.py')]},
                  baseline_file_sha256=e.source_hashes(), full_plan_and_histogram_reconstructed=True,
                  wall_seconds=time.monotonic()-started)
    (args.output / 'prime-witnesses.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    compact = {k: v for k, v in result.items() if k != 'frame_witnesses'}
    (args.output / 'receipt.json').write_text(json.dumps(compact, indent=2, sort_keys=True) + '\n')
    print(json.dumps(compact), flush=True)


if __name__ == '__main__':
    main()
