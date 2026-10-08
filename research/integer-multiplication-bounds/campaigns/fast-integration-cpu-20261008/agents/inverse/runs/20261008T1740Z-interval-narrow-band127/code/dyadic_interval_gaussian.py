#!/usr/bin/env python3
"""Exact dyadic enclosures of cyclic Gaussian coefficients and residuals.

Only Python integers certify the result. Decimal LU merely proposes a vector;
the frozen dyadic words can be replayed without that proposal computation.
Every omitted lifted image is charged by the retained Gaussian tail lemma.
"""
import argparse
from decimal import Decimal, localcontext
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import random
import time

STATS = {"pi_evaluations": 0, "exp_evaluations": 0,
         "max_taylor_terms": 0, "max_squarings": 0}


def ceildiv(a, b):
    assert b > 0
    return -((-a) // b)


@lru_cache(maxsize=None)
def pi_interval(bits):
    """Machin's identity and alternating rational arctangent bounds."""
    work = bits + (bits + 1).bit_length() + 16
    scale = 1 << work

    def arctan_inverse(m):
        power, j, lower, upper = m, 0, 0, 0
        while True:
            denominator = (2 * j + 1) * power
            lo, hi = scale // denominator, ceildiv(scale, denominator)
            if j % 2:
                lower -= hi
                upper -= lo
            else:
                lower += lo
                upper += hi
            j += 1
            power *= m * m
            remainder = ceildiv(scale, (2 * j + 1) * power)
            if remainder <= 1:
                return lower - remainder, upper + remainder

    a, b = arctan_inverse(5), arctan_inverse(239)
    lower, upper = 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]
    divisor = 1 << (work - bits)
    lower, upper = lower // divisor, ceildiv(upper, divisor)
    assert 3 * (1 << bits) < lower <= upper < 4 * (1 << bits)
    STATS["pi_evaluations"] += 1
    return lower, upper


@lru_cache(maxsize=None)
def exp_minus_pi_rational(numerator, denominator, bits):
    """Enclose exp(-pi*numerator/denominator) on a 2^-bits grid."""
    assert numerator >= 0 and denominator > 0 and bits >= 8
    if numerator == 0:
        return 1 << bits, 1 << bits
    common = math.gcd(numerator, denominator)
    numerator, denominator = numerator // common, denominator // common
    squarings = max(1, (4 * numerator // denominator).bit_length() + 1)
    work = bits + 32 + squarings + (bits + 1).bit_length()
    scale = 1 << work
    pi_lo, pi_hi = pi_interval(work)
    divisor = denominator << squarings
    t_lo = pi_lo * numerator // divisor
    t_hi = ceildiv(pi_hi * numerator, divisor)
    assert 0 <= t_lo <= t_hi <= scale // 2
    term_lo = term_hi = scale
    lower = upper = scale
    stop = 1 << (work - bits - squarings - 16)
    j = 0
    while True:
        j += 1
        term_lo = term_lo * t_lo // (scale * j)
        term_hi = ceildiv(term_hi * t_hi, scale * j)
        if j % 2:
            lower -= term_hi
            upper -= term_lo
        else:
            lower += term_lo
            upper += term_hi
        if term_hi <= stop:
            # Alternating remainder <= the next term <= this last term.
            lower -= term_hi
            upper += term_hi
            break
    lower, upper = max(0, lower), min(scale, upper)
    for _ in range(squarings):
        lower = lower * lower // scale
        upper = ceildiv(upper * upper, scale)
    down = 1 << (work - bits)
    lower, upper = lower // down, ceildiv(upper, down)
    assert 0 <= lower <= upper <= (1 << bits)
    assert upper - lower <= 3, "interval oracle exceeded its explicit grid width"
    STATS["exp_evaluations"] += 1
    STATS["max_taylor_terms"] = max(STATS["max_taylor_terms"], j)
    STATS["max_squarings"] = max(STATS["max_squarings"], squarings)
    return lower, upper


def selector(j, source, target):
    return (2 * target * j + source) // (2 * source)


def coefficient_interval(row, displacement, source, target, u, bits):
    column = row + displacement
    qi = selector(row, source, target)
    qj = selector(column, source, target)
    beta_numerator = target * column - source * qj
    n = qj - qi
    numerator = u * n * (n * source + 2 * beta_numerator)
    assert numerator >= 0, "lifted Gaussian coefficient is outside positive regime"
    return exp_minus_pi_rational(numerator, source, bits)


def gaussian_tail_upper(u, half_bandwidth, bits):
    scale = 1 << bits
    top = exp_minus_pi_rational(u * half_bandwidth * (half_bandwidth + 1), 1, bits)[1]
    ratio = exp_minus_pi_rational(2 * u * (half_bandwidth + 1), 1, bits)[1]
    assert ratio < scale
    return ceildiv(2 * top * scale, scale - ratio)


def propose(rows, rhs_words, bits, solution_bits, drop_wrap, source, half_bandwidth):
    """Untrusted Decimal proposal. The resulting integer words are the input."""
    with localcontext() as context:
        context.prec = (max(bits, solution_bits) * 30103 + 99999) // 100000 + 30
        scale = Decimal(1 << bits)
        matrix = [[Decimal(0) for _ in rows] for _ in rows]
        rhs = [Decimal(word) / Decimal(16) for word in rhs_words]
        for i, row in enumerate(rows):
            for h, interval in row.items():
                if drop_wrap and not 0 <= i + h < source:
                    continue
                matrix[i][(i + h) % source] += Decimal(interval[0] + interval[1]) / (2 * scale)
        for k in range(source):
            pivot = matrix[k][k]
            assert pivot != 0
            for i in range(k + 1, source):
                if matrix[i][k] == 0:
                    continue
                multiplier = matrix[i][k] / pivot
                matrix[i][k] = Decimal(0)
                for j in range(k + 1, source):
                    if matrix[k][j] != 0:
                        matrix[i][j] -= multiplier * matrix[k][j]
                rhs[i] -= multiplier * rhs[k]
        solution = [Decimal(0)] * source
        for i in range(source - 1, -1, -1):
            solution[i] = (rhs[i] - sum(matrix[i][j] * solution[j]
                                      for j in range(i + 1, source))) / matrix[i][i]
        return [int(value * Decimal(1 << solution_bits)) for value in solution]


def certify(source, target, alpha, target_bits, half_bandwidth, solution_bits,
            rhs_words, solution_words, rows, coefficient_bits):
    assert 0 < source < target and source > 4 * half_bandwidth
    assert len(rhs_words) == len(solution_words) == source
    scale = 1 << coefficient_bits
    solution_scale = 1 << solution_bits
    tail = gaussian_tail_upper(alpha * alpha, half_bandwidth, coefficient_bits)
    row_gap = scale
    residual = 0
    worst_residual_row = None
    max_coefficient_width = 0
    for i, row in enumerate(rows):
        off_diagonal = 0
        lower = upper = 0
        for h, (lo, hi) in row.items():
            max_coefficient_width = max(max_coefficient_width, hi - lo)
            if h != 0:
                off_diagonal += hi
            word = solution_words[(i + h) % source]
            if word < 0:
                product_lo, product_hi = hi * word, lo * word
            else:
                product_lo, product_hi = lo * word, hi * word
            lower += product_lo // solution_scale
            upper += ceildiv(product_hi, solution_scale)
        row_gap = min(row_gap, scale - off_diagonal - tail)
        exact_rhs = rhs_words[i] * (scale // 16)
        lower -= exact_rhs
        upper -= exact_rhs
        bound = max(abs(lower), abs(upper))
        if bound > residual:
            residual, worst_residual_row = bound, i
    norm = max(map(abs, solution_words))
    numerator = residual * solution_scale + tail * norm
    denominator = row_gap * solution_scale
    certified = row_gap > 0 and (numerator << target_bits) < denominator
    return {
        "status": "RIGOROUS_TARGET_CERTIFIED" if certified else "RIGOROUS_TARGET_NOT_CERTIFIED",
        "directed_integer_arithmetic_only": True,
        "strict_row_gap_proved": row_gap > 0,
        "row_gap_lower_word": str(row_gap),
        "row_gap_fraction_bits": coefficient_bits,
        "retained_residual_upper_word": str(residual),
        "retained_residual_fraction_bits": coefficient_bits,
        "omitted_all_lifted_aliases_row_upper_word": str(tail),
        "omitted_tail_fraction_bits": coefficient_bits,
        "solution_norm_word": str(norm),
        "solution_fraction_bits": solution_bits,
        "full_matrix_solution_error_upper_rational": {"numerator": str(numerator), "denominator": str(denominator)}
            if row_gap > 0 else None,
        "strict_error_below_2_to_minus_target": certified,
        "worst_retained_residual_row": worst_residual_row,
        "maximum_coefficient_interval_width_grid_units": max_coefficient_width,
        "scope": "A posteriori exact dyadic residual and all-alias tail enclosure of the true cyclic Gaussian matrix; no fixed-tape exponent claim",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=int, default=127)
    parser.add_argument("--target", type=int, default=128)
    parser.add_argument("--alpha", type=int, default=2)
    parser.add_argument("--target-bits", type=int, default=128)
    parser.add_argument("--half-bandwidth", type=int)
    parser.add_argument("--solution-bits", type=int)
    parser.add_argument("--mode", choices=("complete","drop-wrap","low-precision","narrow-band"), default="complete")
    parser.add_argument("--seed", type=int, default=202610081735)
    parser.add_argument("--verify-certificate", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "use a fresh immutable result path"
    started = time.time()
    if args.verify_certificate:
        prior = json.loads(args.verify_certificate.read_text())
        config = prior["config"]
        rhs_words = list(map(int,prior["rhs_sixteenth_words"]))
        solution_words = list(map(int,prior["proposed_dyadic_solution_words"]))
        replay_hash = hashlib.sha256(args.verify_certificate.read_bytes()).hexdigest()
    else:
        q = args.target_bits
        w = args.half_bandwidth
        if w is None:
            # This conservative selector is metadata, not a proof oracle.
            w = math.isqrt((q + 128) // (3 * args.alpha * args.alpha)) + 3
        if args.mode == "narrow-band":
            w = 1
        solution_bits = args.solution_bits or q + 64
        if args.mode == "low-precision":
            solution_bits = q - 16
        assert solution_bits >= 16
        config = {"source":args.source,"target":args.target,"alpha":args.alpha,
                  "target_bits":q,"half_bandwidth":w,"solution_bits":solution_bits,
                  "coefficient_bits":q+96,"seed":args.seed,"mode":args.mode}
        rng = random.Random(args.seed)
        rhs_words = [rng.randrange(-16,17) for _ in range(args.source)]
        solution_words = None
        replay_hash = None
    source, target, alpha = (config[k] for k in ("source","target","alpha"))
    w, bits = config["half_bandwidth"], config["coefficient_bits"]
    assert source > 4*w and 0 < source < target
    rows = [{h:coefficient_interval(i,h,source,target,alpha*alpha,bits)
             for h in range(-w,w+1)} for i in range(source)]
    if solution_words is None:
        solution_words = propose(rows,rhs_words,bits,config["solution_bits"],
                                 config["mode"]=="drop-wrap",source,w)
    result = certify(source,target,alpha,config["target_bits"],w,
                     config["solution_bits"],rhs_words,solution_words,rows,bits)
    result.update(config=config,rhs_sixteenth_words=rhs_words,
                  proposed_dyadic_solution_words=list(map(str,solution_words)),
                  proposal_trusted=False,
                  proposal="Frozen input words on replay" if replay_hash else "Decimal LU on interval-midpoint band; not trusted by certification",
                  replay_input_sha256=replay_hash,
                  interval_algorithm="Machin alternating arctangent, directed dyadic alternating exp Taylor, directed repeated squaring",
                  interval_statistics=STATS.copy(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  wall_seconds=time.time()-started,workers=1,native_threads=1)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({"status":result["status"],"config":config,
                      "interval_statistics":STATS,"wall_seconds":result["wall_seconds"]}))


if __name__ == "__main__":
    main()
