#!/usr/bin/env python3
"""Independent changed-interface numerical checks for joint Gaussian cells.

The reference is the periodic normalized global Gaussian applied to a sum of
two separable signed inputs. The producer uses the actual fractional core,
chirped Toeplitz factors, zero padding, and signed integer Kronecker products.
No public producer/checker or campaign inverse code is imported.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, ROUND_FLOOR, localcontext
from pathlib import Path
from random import Random
from time import perf_counter

PI = Decimal("3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481")


def decimal_pi(digits):
    """Machin's formula with a precision-dependent convergent tail cutoff."""
    with localcontext() as context:
        context.prec = digits + 12
        cutoff = Decimal(10) ** (-digits - 8)

        def atan_inverse(q):
            x = Decimal(1) / q
            square = x * x
            power = x
            answer = Decimal(0)
            k = 0
            while True:
                term = power / (2 * k + 1)
                answer += term if k % 2 == 0 else -term
                if abs(term) < cutoff:
                    break
                power *= square
                k += 1
            return answer

        answer = 16 * atan_inverse(5) - 4 * atan_inverse(239)
    return +answer


def coordinates(shape):
    return itertools.product(*(range(s) for s in shape))


def encode(point, base):
    result = 0
    for x in point:
        result = result * base + x
    return result


def rounded_product(values, scale):
    """Stable prefix setup: every contracting multiplication returns to P bits."""
    result = scale
    for value in values:
        result = int((Decimal(result) * value).to_integral_value(rounding=ROUND_FLOOR))
    return result


def pack_sparse(rows, slot_bytes, degree):
    buffer = bytearray((degree + 1) * slot_bytes)
    for index, value in rows:
        assert value >= 0
        buffer[index * slot_bytes:(index + 1) * slot_bytes] = value.to_bytes(slot_bytes, "little")
    return int.from_bytes(buffer, "little")


def run_case(config):
    start = perf_counter()
    with localcontext() as context:
        context.prec = 160
        pi = PI
        shape = tuple(config["source_shape"])
        target = config["target_side"]
        dimension = len(shape)
        side = config["side"]
        radius = config["radius"]
        alpha = Decimal(config["alpha"])
        shift = config["shift"]
        target_origins = tuple(x * side + shift for x in config["cell_indices"])
        source_origins = tuple(s * k // target for s, k in zip(shape, target_origins))
        source_ends = tuple(s * (k + side) // target for s, k in zip(shape, target_origins))
        lengths = tuple(e - j for e, j in zip(source_ends, source_origins))
        assert all(0 <= j < e <= s for s, j, e in zip(shape, source_origins, source_ends))
        assert all(e + radius < s and j > radius for s, j, e in zip(shape, source_origins, source_ends))
        rho = tuple(Decimal(target) / Decimal(s) for s in shape)
        theta = tuple(r - 1 for r in rho)
        g = tuple(1 / (r * r * alpha * alpha) for r in rho)
        y = tuple(r * j - k for r, j, k in zip(rho, source_origins, target_origins))
        reserve_log = sum(pi * gi * th * Decimal((side - 1) ** 2) for gi, th in zip(g, theta))
        reserve_bits = math.ceil(reserve_log / Decimal(2).ln())
        target_bits = 128
        work_bits = target_bits + reserve_bits + math.ceil(math.log2(side ** dimension)) + math.ceil(math.log2(dimension)) + 48
        context.prec = max(160, math.ceil((work_bits + 64) / math.log2(10)))
        pi = decimal_pi(context.prec)
        # Rebuild rational geometry after raising the work precision.
        rho = tuple(Decimal(target) / Decimal(s) for s in shape)
        theta = tuple(r - 1 for r in rho)
        g = tuple(1 / (r * r * alpha * alpha) for r in rho)
        y = tuple(r * j - k for r, j, k in zip(rho, source_origins, target_origins))
        scale = 1 << work_bits
        base = side + 2 * radius
        slot_bits = 8 * math.ceil((2 * work_bits + math.ceil(math.log2(side ** dimension)) + 5) / 8)
        slot_bytes = slot_bits // 8
        rng = Random(config["seed"])
        components = [[tuple(Decimal(rng.randrange(-8, 9)) / 32 for _ in range(s)) for s in shape]
                      for _ in range(2)]

        def input_value(global_point):
            answer = Decimal(0)
            for component in components:
                product = Decimal(1)
                for axis, j in enumerate(global_point):
                    product *= component[axis][j % shape[axis]]
                answer += product
            return answer

        input_diagonals = []
        output_diagonals = []
        kernels = []
        for gi, r, th, yi in zip(g, rho, theta, y):
            input_diagonals.append(tuple((-pi * gi * r * th * (Decimal(a) + yi / r) ** 2).exp() for a in range(side)))
            output_diagonals.append(tuple((pi * gi * th * Decimal(b * b)).exp() for b in range(side)))
            # The packed polynomial displacement is b-a; the analytic
            # Toeplitz argument is a-b. This sign is deliberately explicit.
            kernels.append(tuple((-pi * gi * r * (Decimal(-h) + yi / r) ** 2).exp()
                                 for h in range(-radius, radius + 1)))
        positive = []
        negative = []
        occupied = 0
        for a in coordinates((side,) * dimension):
            if not all(ai < length for ai, length in zip(a, lengths)):
                continue
            diagonal = rounded_product((input_diagonals[i][ai] for i, ai in enumerate(a)), scale)
            value = input_value(tuple(j + ai for j, ai in zip(source_origins, a)))
            magnitude = int((Decimal(diagonal) * abs(value)).to_integral_value(rounding=ROUND_FLOOR))
            (positive if value >= 0 else negative).append((encode(a, base), magnitude))
            occupied += 1
        kernel_rows = []
        for hp in coordinates((2 * radius + 1,) * dimension):
            coefficient = rounded_product((kernels[i][h] for i, h in enumerate(hp)), scale)
            kernel_rows.append((encode(hp, base), coefficient))
        input_degree = encode((side - 1,) * dimension, base)
        kernel_degree = encode((2 * radius,) * dimension, base)
        assert input_degree + kernel_degree < base ** dimension
        packed_positive = pack_sparse(positive, slot_bytes, input_degree)
        packed_negative = pack_sparse(negative, slot_bytes, input_degree)
        packed_kernel = pack_sparse(kernel_rows, slot_bytes, kernel_degree)
        if config.get("integer_backend") == "gmpy2-2.3.0":
            import gmpy2
            assert gmpy2.__version__ == "2.3.0"
            product_positive = int(gmpy2.mpz(packed_positive) * gmpy2.mpz(packed_kernel))
            product_negative = int(gmpy2.mpz(packed_negative) * gmpy2.mpz(packed_kernel))
        else:
            product_positive = packed_positive * packed_kernel
            product_negative = packed_negative * packed_kernel
        mask = (1 << slot_bits) - 1
        normalization = (2 * alpha) ** (-dimension)

        multiplication_seconds = perf_counter() - start

        @lru_cache(maxsize=None)
        def global_axis_reference(i, k):
            # The two input components share coefficients, and sample outputs
            # share axis coordinates. Keep the independently evaluated global
            # periodic sum, but compute each coefficient only once.
            totals = [Decimal(0), Decimal(0)]
            for j in range(shape[i]):
                weight = sum((-pi * g[i] * (rho[i] * j - k + v * target) ** 2).exp()
                             for v in (-1, 0, 1)) / (2 * alpha)
                for c, component in enumerate(components):
                    totals[c] += component[i][j] * weight
            return tuple(totals)

        def global_reference(output_point):
            axis_values = [global_axis_reference(i, k) for i, k in enumerate(output_point)]
            return sum(math.prod(values[c] for values in axis_values) for c in range(2))

        @lru_cache(maxsize=None)
        def cell_axis_references(i, bi):
            totals = [[Decimal(0), Decimal(0)] for _ in range(3)]
            for ai in range(lengths[i]):
                direct_weight = (-pi * g[i] *
                    (rho[i] * (source_origins[i] + ai) - (target_origins[i] + bi)) ** 2).exp()
                factor_weight = (input_diagonals[i][ai] * output_diagonals[i][bi] *
                    (-pi * g[i] * rho[i] * (Decimal(ai - bi) + y[i] / rho[i]) ** 2).exp())
                wrong_weight = ((pi * g[i] * theta[i] * bi * bi).exp() *
                    (-pi * g[i] * rho[i] * theta[i] * ai * ai).exp() *
                    (-pi * g[i] * rho[i] * Decimal(ai - bi) ** 2).exp())
                for c, component in enumerate(components):
                    value = component[i][source_origins[i] + ai]
                    for kind, weight in enumerate((direct_weight, factor_weight, wrong_weight)):
                        totals[kind][c] += value * weight / (2 * alpha)
            return tuple(tuple(row) for row in totals)

        # Check selector composition as well as plain forward target samples:
        # q_j=nearest(target*j/source) is an exact global selector. Both grids
        # have separately derived source origins and y.
        samples = set()
        selector_samples = 0
        for b in coordinates((2,) * dimension):
            samples.add(tuple(radius + x for x in b))
        selector_source_points = []
        for a in coordinates((2,) * dimension):
            j = tuple(j0 + radius + x for j0, x in zip(source_origins, a))
            q = tuple((2 * target * ji + s) // (2 * s) for ji, s in zip(j, shape))
            b = tuple(qi - k0 for qi, k0 in zip(q, target_origins))
            if all(radius <= bi < side - radius for bi in b):
                samples.add(b)
                selector_source_points.append((j, q))
                selector_samples += 1
        max_packed_error = Decimal(0)
        max_factorization_error = Decimal(0)
        max_wrong_origin_error = Decimal(0)
        outputs = []
        for b in sorted(samples):
            assert all(radius <= bi < side - radius for bi in b)
            index = encode(tuple(bi + radius for bi in b), base)
            numerator = ((product_positive >> (slot_bits * index)) & mask) - ((product_negative >> (slot_bits * index)) & mask)
            output_diagonal = math.prod(output_diagonals[i][bi] for i, bi in enumerate(b))
            packed_value = Decimal(numerator) / Decimal(scale * scale) * output_diagonal * normalization
            point = tuple(k0 + bi for k0, bi in zip(target_origins, b))
            reference = global_reference(point)
            error = abs(packed_value - reference)
            max_packed_error = max(max_packed_error, error)
            # Separately sum the exact cell factors and the direct unwrapped
            # Gaussian. This distinguishes algebra/normalization from tails.
            # Distributivity is exact for the two-component input definition.
            # This evaluates the SAME direct/factored/wrong-origin cell sum
            # with rank*d*side terms instead of side**d high-precision exp calls.
            axis_cells = [cell_axis_references(i, bi) for i, bi in enumerate(b)]
            direct_cell, factor_cell, wrong_cell = (
                sum(math.prod(axis[kind][c] for axis in axis_cells) for c in range(2))
                for kind in range(3))
            max_factorization_error = max(max_factorization_error, abs(direct_cell - factor_cell))
            max_wrong_origin_error = max(max_wrong_origin_error, abs(wrong_cell - direct_cell))
            assert error < Decimal(2) ** -target_bits, (config, b, error)
            assert abs(direct_cell - factor_cell) < Decimal("1e-125")
            outputs.append({"local_target": b, "global_target": point, "reference": str(reference),
                            "packed": str(packed_value), "absolute_error": str(error)})
        assert max_wrong_origin_error > Decimal("1e-8")
        # The floor selector need not stay in the same source core at its
        # final target slot; retain an exact, independent small counterexample.
        plateau = {"s": 13, "t": 16, "side": 2, "k0": 4, "b": 1,
                   "source_origin": 13 * 4 // 16, "source_end": 13 * 6 // 16,
                   "selected_source": 13 * 5 // 16}
        assert plateau["selected_source"] == plateau["source_end"]
        # A source-period cut is not covariance of an unwrapped global shift.
        cut_j = shape[0] - 1
        cut_k = 0
        unwrapped_cut = (-pi * g[0] * (rho[0] * cut_j - cut_k) ** 2).exp()
        periodic_cut = sum((-pi * g[0] * (rho[0] * cut_j - cut_k + v * target) ** 2).exp()
                           for v in (-1, 0, 1))
        assert periodic_cut > unwrapped_cut + Decimal("1e-4")
        return {"name": config["name"], "config": config, "source_origins": source_origins,
                "target_origins": target_origins, "core_lengths": lengths, "true_y": [str(x) for x in y],
                "target_bits": target_bits, "work_bits": work_bits, "full_tensor_reserve_bits": reserve_bits,
                "decimal_digits": context.prec,
                "oracle_policy": "exact distributive rank-two sums; cached independent axis coefficients",
                "multiplication_setup_and_input_seconds": multiplication_seconds,
                "global_axis_reference_sums": global_axis_reference.cache_info().misses,
                "cell_axis_reference_sums": cell_axis_references.cache_info().misses,
                "kronecker_base": base, "slot_bits": slot_bits, "input_records": occupied,
                "kernel_records": len(kernel_rows), "padded_records": base ** dimension,
                "outputs_checked": len(outputs), "exact_global_selector_outputs": selector_samples,
                "maximum_packed_vs_periodic_reference_error": str(max_packed_error),
                "maximum_direct_vs_factorization_error": str(max_factorization_error),
                "negative_constant_origin_maximum_error": str(max_wrong_origin_error),
                "negative_floor_plateau": plateau,
                "negative_period_cut": {"source_j": cut_j, "target_k": cut_k,
                                        "unwrapped": str(unwrapped_cut), "periodic": str(periodic_cut)},
                "outputs": outputs, "seconds": perf_counter() - start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--config", help="JSON list of independently specified changed parameter cases")
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error("one to six changed-interface workers")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    configs = [
        {"name": "two-dimensional-unshifted-L16", "source_shape": [251, 249], "target_side": 256,
         "side": 16, "radius": 7, "alpha": "0.75", "shift": 0, "cell_indices": [2, 7], "seed": 202610086001},
        {"name": "two-dimensional-shifted-L32", "source_shape": [251, 253], "target_side": 256,
         "side": 32, "radius": 12, "alpha": "1.25", "shift": 16, "cell_indices": [2, 4], "seed": 202610086002},
        {"name": "three-dimensional-unshifted-L16", "source_shape": [251, 253, 249], "target_side": 256,
         "side": 16, "radius": 7, "alpha": "0.75", "shift": 0, "cell_indices": [2, 4, 7], "seed": 202610086003},
        {"name": "three-dimensional-shifted-L16", "source_shape": [251, 253, 249], "target_side": 256,
         "side": 16, "radius": 7, "alpha": "0.75", "shift": 8, "cell_indices": [2, 4, 7], "seed": 202610086004},
    ]
    if args.config:
        configs = json.loads(Path(args.config).read_text())
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(run_case, configs))
    result = {"status": "changed fractional Gaussian cell interface passed", "workers": args.workers,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "decimal_policy": "max(160,ceil((work_bits+64)/log2(10)))", "seconds": perf_counter() - start, "rows": rows,
              "limitations": ["bounded representative cells, not an all-size Gaussian tail proof",
                              "periodic reference retains images -1,0,+1; remote images are far below target precision",
                              "known-bit global gather is a separately paid routing premise",
                              "CRT movement is not implemented or granted by this check"]}
    (out / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "seconds": result["seconds"],
                      "rows": [{key: row[key] for key in ("name", "outputs_checked", "exact_global_selector_outputs",
                                                         "maximum_packed_vs_periodic_reference_error", "seconds")}
                               for row in rows]}))


if __name__ == "__main__":
    main()
