#!/usr/bin/env python3
"""Independent high-precision Gaussian-to-source-transform composition.

This is a bounded full one-dimensional algebra discriminator before assembling
the multidimensional integer recovery prototype. All normalizations and both
frequency permutations are included, with direct DFT references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from random import Random
from time import perf_counter

import mpmath as mp


def run_case(config):
    start = perf_counter()
    mp.mp.dps = config["digits"]
    s, t, alpha = config["s"], config["t"], config["alpha"]
    rho = mp.mpf(t) / s
    u = alpha * alpha
    image_radius = int(mp.ceil(alpha * mp.sqrt((config["digits"] + 20) * mp.log(10) / mp.pi) / s)) + 2
    images = range(-image_radius, image_radius + 1)
    selector = [int(mp.floor(rho * j + mp.mpf("0.5"))) for j in range(s)]
    beta = [rho * j - selector[j] for j in range(s)]
    diagonal = [mp.exp(mp.pi * u * b * b) for b in beta]
    gaussian_s = mp.matrix(t, s)
    gaussian_t = mp.matrix(t, s)
    for k in range(t):
        for j in range(s):
            gaussian_s[k, j] = sum(mp.exp(-mp.pi * (j + period * s - mp.mpf(s) * k / t) ** 2 / u)
                                   for period in images) / alpha
            gaussian_t[k, j] = sum(mp.exp(-mp.pi * u * (rho * j + period * t - k) ** 2)
                                   for period in images)
    n = mp.matrix(s, s)
    for j in range(s):
        for h in range(s):
            n[j, h] = gaussian_t[selector[j], h] * diagonal[h]
    inverse = n ** -1
    inverse_residual = max(abs(v) for v in inverse * n - mp.eye(s))
    source_direct = mp.matrix(s, s)
    target_middle = mp.matrix(t, t)
    target_wrong = mp.matrix(t, t)
    for k in range(s):
        for j in range(s):
            source_direct[k, j] = mp.exp(-2j * mp.pi * t * j * k / s) / s
    for k in range(t):
        for j in range(t):
            target_middle[k, j] = mp.exp(2j * mp.pi * s * j * k / t) / t
            target_wrong[k, j] = mp.exp(-2j * mp.pi * j * k / t) / t
    rng = Random(config["seed"])
    probes = []
    for j in (0, 1, s - 1, s // 2):
        vector = mp.matrix(s, 1)
        vector[j] = mp.mpf(1) / 8
        probes.append(vector)
    for _ in range(4):
        probes.append(mp.matrix([mp.mpc(rng.randrange(-8, 9), rng.randrange(-8, 9)) / 64 for _ in range(s)]))
    maximum = mp.mpf(0)
    wrong_permutation = mp.mpf(0)
    normalizations = []
    for vector in probes:
        expanded = gaussian_s * vector / 2
        middle = target_middle * expanded
        selected = mp.matrix([middle[q] for q in selector])
        compressed = inverse * selected / 2
        result = mp.matrix([diagonal[j] * compressed[j] / mp.mpf(2) ** (2 * u - 2) for j in range(s)])
        result *= mp.mpf(2) ** (2 * u)
        expected = source_direct * vector
        maximum = max(maximum, max(abs(a - b) for a, b in zip(result, expected)))
        wrong_middle = target_wrong * expanded
        wrong_selected = mp.matrix([wrong_middle[q] for q in selector])
        wrong = inverse * wrong_selected
        wrong = mp.matrix([diagonal[j] * wrong[j] * 2 for j in range(s)])
        wrong_permutation = max(wrong_permutation, max(abs(a - b) for a, b in zip(wrong, expected)))
        normalizations.append({"expanded_norm": str(max(abs(x) for x in expanded)),
                               "middle_norm": str(max(abs(x) for x in middle)),
                               "compressed_before_scale_norm": str(max(abs(x) for x in result) / mp.mpf(2) ** (2 * u)),
                               "source_after_scale_norm": str(max(abs(x) for x in result))})
    assert maximum < mp.mpf("1e-60"), (config, maximum)
    assert inverse_residual < mp.mpf("1e-70")
    permutation_is_identity = (-s) % t == 1
    if not permutation_is_identity:
        assert wrong_permutation > mp.mpf("1e-4"), (config, wrong_permutation)
    # Period images are indispensable near the original source cut.
    cut_periodic = gaussian_s[0, s - 1]
    cut_unwrapped = mp.exp(-mp.pi * (s - 1) ** 2 / u) / alpha
    assert cut_periodic > cut_unwrapped + mp.mpf("1e-3")
    result = {"config": config, "period_image_radius": image_radius, "probes": len(probes), "maximum_source_transform_error": str(maximum),
            "inverse_residual": str(inverse_residual), "negative_missing_target_permutation_error": str(wrong_permutation),
            "negative_permutation_control_applicable": not permutation_is_identity,
            "negative_period_cut": {"periodic": str(cut_periodic), "unwrapped": str(cut_unwrapped)},
            "normalization_rows": normalizations, "seconds": perf_counter() - start}
    if config.get("row_output"):
        Path(config["row_output"]).write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config")
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("one to four allocated workers")
    os.environ["OMP_NUM_THREADS"] = "1"
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    configs = [{"s": s, "t": t, "alpha": alpha, "digits": 110, "seed": 202610090000 + s}
               for s, t, alpha in ((7, 8, 2), (13, 16, 3), (29, 32, 4), (61, 64, 5))]
    if args.config:
        configs = json.loads(Path(args.config).read_text())
    for config in configs:
        config["row_output"] = str(output / f"row-s{config['s']}-t{config['t']}.json")
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(run_case, configs))
    result = {"status": "complete Gaussian source-transform normalization passed", "workers": args.workers,
              "dependency": {"mpmath": mp.__version__}, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "seconds": perf_counter() - start, "rows": rows,
              "limitations": ["bounded finite matrix reference, not a fast fixed-tape Gaussian producer",
                              "no ordinary multiplier recovery is claimed by this preliminary composition check",
                              "parameters do not certify an all-size campaign cutoff"]}
    (output / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "seconds": result["seconds"],
                      "errors": [r["maximum_source_transform_error"] for r in rows]}))


if __name__ == "__main__":
    main()
