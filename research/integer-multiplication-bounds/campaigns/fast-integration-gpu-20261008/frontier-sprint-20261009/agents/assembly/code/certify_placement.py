#!/usr/bin/env python3
"""Fresh finite reconstruction and strict assembly for a pinned frame placement.

Apache-2.0. Prepared for RaD with OpenAI GPT-6.1 Sol assistance.
The finite bridge and assembly expressions below adapt icekylinx's PR161
scripts/paired_cube_network.py and scripts/structured_bulk_assembly.py.
Their Apache-2.0 copyright and contribution notices remain applicable.
PR23's assembly credits Zhihao Chen and the RaD project; completed-core
sharing credits an664 PR128. The actual scalar/frame compiler credits
icekylinx, eumemic, jamesyc, Zhihao Chen and Swapnil Jain in the retained
source notices. This file changes certification and reconstruction only;
the placement search is a separate contribution.

No saved candidate verdict or histogram is used as an input. The signed
complex producer and the unchanged bit producer are regenerated from pinned
immutable module inputs. Both finite checkers run on the new outputs. The
selected physical frames then determine a freshly recounted full histogram.
All-size transfer remains conditional on the named inherited contracts.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import prod
from pathlib import Path
import json
import resource
import sys
import time

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
sys.dont_write_bytecode = True

GRID = 1 << 180
COARSE = Q(5936323, 10**10)
ATOM = Q(1, 1000)
OLD = Q(384599, 10**10)
AB = (1 - ATOM) * COARSE + ATOM * OLD
BAD = Q(1, 10**16)
AC = Q(594561016, 10**12)
BETA = Q(1, 10**9)
ETA = Q(1, 10**8)
KAPPA = Q(592374462, 10**12)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def js(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): js(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [js(v) for v in value]
    return value


def write(path, value):
    require(not path.exists(), "Refusing to replace an existing evidence file: " + str(path))
    path.write_text(json.dumps(js(value), indent=2, sort_keys=True) + "\n")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def down(value):
    return Q((value.numerator * GRID) // value.denominator, GRID)


def up(value):
    return Q((value.numerator * GRID + value.denominator - 1) // value.denominator, GRID)


def log_bounds(value):
    """40 positive atanh terms after power-of-two range reduction.

    For z=(x-1)/(x+1), the omitted tail after j=39 is between zero
    and 2*z^81/(81*(1-z^2)). All inputs here are at least one.
    """
    require(value >= 1, "Logarithm domain")
    power = 0
    while value >= 2:
        value /= 2
        power += 1

    def small(x):
        z = (x - 1) / (x + 1)
        lower = 2 * sum((z**(2*j + 1) / (2*j + 1) for j in range(40)), Q(0))
        return lower, lower + 2*z**81 / (81*(1 - z*z))

    lo2, hi2 = small(Q(2))
    lo, hi = small(value)
    return down(power*lo2 + lo), up(power*hi2 + hi)


def exp_bounds(lower, upper):
    """Degree-nine Taylor polynomial and an explicit positive tail.

    The tail begins at u^10/10! and its later-term ratios are at most
    u/11. Every arithmetic operation is rounded outwards on the grid.
    """
    require(0 <= lower <= upper < 1, "Exponential domain")
    lo_term = hi_term = Q(1)
    lo_sum = hi_sum = Q(1)
    for k in range(1, 10):
        lo_term = down(lo_term*lower/k)
        hi_term = up(hi_term*upper/k)
        lo_sum = down(lo_sum + lo_term)
        hi_sum = up(hi_sum + hi_term)
    tail = up(up(hi_term*upper/10) / (1 - upper/11))
    return lo_sum, up(hi_sum + tail)


def moment(profile, saving, fallback=False):
    m, W, hist = profile["m"], profile["W_per_vertex"], profile["child_multiplicities"]
    logs = {r: log_bounds(Q(m, r)) for r in hist}
    lo, hi = Q(0), Q(0)
    for r, count in hist.items():
        elo, ehi = exp_bounds(down(saving*logs[r][0]), up(saving*logs[r][1]))
        lo += Q(count*r, m*W)*elo
        hi += Q(count*r, m*W)*ehi
    ideal_lo, ideal_hi = down(lo), up(hi)
    extra_lo = extra_hi = Q(0)
    fallback_children = 32*m*m
    if fallback:
        llo, lhi = log_bounds(Q(m))
        elo, ehi = exp_bounds(down(saving*llo), up(saving*lhi))
        weight = BAD*Q(fallback_children*sum(hist.values()), m*W)
        extra_lo, extra_hi = down(weight*elo), up(weight*ehi)
    return dict(saving=saving, exponent=1-saving,
                ideal_moment_lower=ideal_lo, ideal_moment_upper=ideal_hi,
                added_bad_moment_lower=extra_lo, added_bad_moment_upper=extra_hi,
                moment_lower=down(ideal_lo+extra_lo), moment_upper=up(ideal_hi+extra_hi),
                strict_gap_lower=down(1-ideal_hi-extra_hi),
                logarithm_bounds=logs, rounding_denominator=GRID,
                method="40-term atanh with geometric tail; degree-nine exponential with geometric tail; outward rational rounding")


def bit_profile(row):
    h, v, R, loss = (row[k] for k in ("h", "v", "R", "loss"))
    require((h, v, R, loss) == (24, 1760, 23368, 528), "Retained bit dimensions")
    hist = Counter()
    selected = {int(r): n for r, n in row["selected_rank_histogram"].items()}
    require(selected == {20: 5720}, "Retained bit gauges")
    for r, n in selected.items():
        hist[3*r] += n
    for name in ("remaining_internal_histogram", "source_data_histogram", "target_data_histogram"):
        for r, n in row[name].items():
            if int(r):
                hist[int(r)] += 3*n
    hist[2] += 2*v
    return checked_profile(hist, 3*h, 2*v+R, 2*v-3*loss, row)


def complex_profile(physical, row):
    h, v, R, loss = (row[k] for k in ("h", "v", "R", "loss"))
    require((h, v, R, loss) == (22, 1320, 16011, 440), "Retained complex dimensions")
    require(physical["physical_R"] == R-physical["pairs"], "Physical stock")
    hist = Counter()
    for name in ("local_histogram", "source_data_histogram", "target_data_histogram"):
        for r, n in physical[name].items():
            if int(r):
                hist[int(r)] += 3*n
    for rank, n in physical["physical_gauge_histogram"].items():
        if int(rank):
            hist[3*int(rank)] += n
    hist[2] += 2*v
    result = checked_profile(hist, 3*h, 2*v+physical["physical_R"], 2*v-3*loss, physical)
    result.update(physical_roles=physical["physical_R"], reuse_pairs=physical["pairs"],
                  late_reads=physical["late_pairs"], moved_operation_frames=physical["changed_operation_frames"])
    return result


def checked_profile(hist, m, W, deficit, row):
    hist = dict(sorted((r, n) for r, n in hist.items() if r and n))
    require(all(isinstance(r, int) and isinstance(n, int) and 0 < r < m and n > 0
                for r, n in hist.items()), "Positive proper children")
    mass = sum(r*n for r, n in hist.items())
    require(hist == {int(r): n for r, n in row["child_histogram"].items()}, "Fresh component recount")
    require((m, W, mass, m*W-mass) == (row["m"], row["W_per_vertex"], row["rank_per_vertex"], row["deficit_per_vertex"]),
            "Fresh full profile dimensions")
    require(m*W-mass == deficit, "Telescoping deficit")
    return dict(m=m, W_per_vertex=W, rank_per_vertex=mass, deficit_per_vertex=deficit,
                child_multiplicities=hist, maxchild=max(hist), edge_count=sum(hist.values()))


def halving(m, r):
    require(0 < r < m, "Halving contraction")
    n = 1
    while m**n <= 2*r**n:
        n += 1
    return n


def finite_bridge(profile, row):
    """The full PR161 finite scalar, router, precision and row reserve.

    No numerical quantity is replaced by a normalized per-vertex count
    when charging full cover permutations or the semantic guard.
    """
    m, w = profile["m"], profile["W_per_vertex"]
    n = m//2
    V = 2**(m-1+(n-1)**2)*prod(2**(2*i)-1 for i in range(1, n))
    W, s, N = V*w, V*profile["rank_per_vertex"], V*row["v"]
    h, v, R, M = (row[k] for k in ("h", "v", "R", "total_M_operations"))
    require(M == 32426 and row["q"] == 4477, "Literal scalar inventory")
    original_X = 32*v
    local = 4*(row["c"]+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    dirty_reads = 8*R*v*(M+16)
    local += dirty_reads+original_X
    logical = 3*V*local+8*W+4*N+8*m*R*V
    G = 64*(m+1)**3*(logical+1)*(W+1)**2
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*s+4*W+4+32*m
    B, C0, r = s+E, 32*m*(s+E)**2, profile["maxchild"]
    require(charge < E and 2*B*(m-r) >= s+E and 2*B+18 < C0, "Finite semantic guard")
    dc, wc = halving(m, r), W.bit_length()
    coefficient, degree = dc*wc+9909+252, 70000
    require(Q(degree) > Q(51*coefficient, 25), "External row reserve")
    return dict(bit_uniform=dict(coarse_saving=COARSE, atom_beta=ATOM, old_atom_saving=OLD, ordinary_saving=AB,
                 selector_stock="O(w log e) internally borrowed radix-q digits; restored by retained ordinary wrapper"),
        conservative_old_coarse_row_reserve=9909, ordinary_leaf_row_degree=252,
        complex=dict(m=m, W=W, s=s, N=N, maxchild=r, invocations_per_stage=V, stages=3,
            auxiliary_banks_after_sharing=1, halving_degree=dc, wire_bits=wc,
            group_order_bits=V.bit_length(), local_group_upper=local,
            expanded_dirty_readout_group_upper=dirty_reads, original_X_involution_scalar_group_upper=original_X,
            logical_group_upper=logical, scalar_group_upper=G, finite_group_router_upper=G,
            routing_charge="64*(m+1)^3*(K+1)*(W+1)^2; complete W-role permutation overcharged per logical group",
            coefficient_bound=h+4, coefficient_denominator_divides=6,
            dirty_matrix_numerator_bits=M+16),
        semantic=dict(E=E, literal_charge=charge, strict_literal_gap=E-charge, B=B, C0=C0, C1=1,
            induction_gap=2*B*(m-r)-s-E, C0_gap=C0-2*B-18, fixed_odd_divisor=3,
            exact_grid="One common dyadic grid times 3^(-K_grid), K_grid=G*(D_complex+1); no child rounding"),
        rows=dict(coefficient=coefficient, complex_coefficient=dc*wc, degree=degree,
            suffix_slope=4*degree, degree_gap=Q(degree)-Q(51*coefficient, 25),
            contract="Full finite complex stock; conservative bit reserves; selectors internally borrowed/restored; one prefix and one padding; sequential reuse"))


def assembly(a, b, bridge, kappa):
    """PR23/PR161 retained parameter formulas, with explicit strict checks.

    Modified from scripts/structured_bulk_assembly.py: use require rather
    than assertions; report actual available bit saving separately.
    """
    tau, sigma = 1-a, 1-b
    q = a*(1-2*ETA)
    lp, lam = 1-q, (tau+1-q)/2
    c = q*(1+ETA)
    eps = (1-ETA)/(1+c+q)
    minimum = eps*q
    r, delta = (minimum+1-eps)/2, ETA/8
    internal = tau+(1-BETA)*max(sigma-tau, Q(0))
    leaf = sigma+BETA*(1-sigma)
    margins = dict(original_prefix=1-eps*(1+c), coordinate_movement=a,
        compact_phase_layer=minimum, bulk_exposure=a,
        Gaussian_arithmetic=min(1-eps-delta, r-delta), scalar_work=1-eps-delta, dimension=eps)
    slacks = dict(bit_positive=a, complex_above_bit=b-a,
        complex_below_one_over32=Q(1, 32)-b, beta_positive=BETA,
        beta_below_one=1-BETA, leaf_saving_above_bit=(1-BETA)*b-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf, compact_reservations=lp-(1-c),
        lambda_prime_below_one=q, epsilon_positive=eps, epsilon_below_one=1-eps,
        guard_width=1-eps, K_geometry=1-eps*(1+c), K_dominates_log=eps*c,
        record_suffix=1-eps, phase_local=1-eps-delta, phase_boundary=r-delta,
        gamma_sublinear=1-eps-r, cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1, 4)-r, delta_positive=delta,
        delta_below_one_eighth=Q(1, 8)-delta, short_record_fallback=eps-a,
        small_field_exposure=1-eps-minimum,
        artificial_boundary=8-eps+r-delta-minimum,
        literal_scalar_guard=Q(bridge["semantic"]["strict_literal_gap"]),
        row_product_gap=bridge["rows"]["degree_gap"])
    slacks.update({name+"_above_kappa": val-kappa for name, val in margins.items()})
    require(len(slacks) == 47 and len(margins) == 7, "Complete 47+7 assembly")
    require(all(v > 0 for v in slacks.values()), "Nonpositive assembly constraint: " +
            ", ".join(k for k, v in slacks.items() if v <= 0))
    require(min(margins.values()) == minimum and margins["original_prefix"]-minimum == ETA,
            "Assembly minimum identity")
    require(a <= AB, "Supported bit interface")
    return dict(parameters=dict(a_bit=a, actual_bit_saving=AB, a_complex=b, tau=tau, sigma=sigma,
        eta=ETA, beta=BETA, q=q, c=c, epsilon=eps, lambda_=lam, lambda_prime=lp,
        alpha_squared_power=r, delta=delta, C0=bridge["semantic"]["C0"], C1=1, kappa=kappa),
        strict_constraints=slacks, margins=margins, minimum_margin=minimum,
        absorption_gap=minimum-kappa,
        recurrence=dict(internal=internal, leaf=leaf, reservations=1-c))


def source_check(source, pin):
    hashes = pin["source_sha256"]
    for name, expected in hashes.items():
        p = Path(name)
        require(not p.is_absolute() and ".." not in p.parts, "Unsafe source path")
        require(digest(source/p) == expected, "Source hash mismatch: " + name)
    return hashes


def validated_frames(path, ops, h):
    payload = json.loads(path.read_text())
    require(isinstance(payload, list), "Frame payload must be a list")
    seen = set()
    for item in payload:
        require(isinstance(item, list) and len(item) == 2, "Frame entry shape")
        i, rows = item
        require(type(i) is int and 0 <= i < len(ops) and i not in seen, "Invalid/aliased operation index")
        require(isinstance(rows, list) and all(type(x) is int and 0 < x < 1 << h for x in rows), "Frame vector domain")
        seen.add(i)
    return payload


def main():
    require(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--frames", type=Path, required=True)
    ap.add_argument("--pin", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    require(not output.exists(), "Refusing to overwrite an attempt")
    pin = json.loads(args.pin.read_text())
    hashes = source_check(source, pin)
    require(digest(args.frames) == pin["candidate_frames_sha256"], "Candidate frame hash mismatch")
    output.mkdir(parents=True)
    start = time.monotonic()
    def stage(message):
        print(datetime.now(timezone.utc).isoformat(timespec="seconds"), message, flush=True)
    stage("Pinned inputs verified; reconstructing unchanged complex producer")
    sys.path.insert(0, str(source/"scripts"))
    from paired_cube_producer import regenerate
    from paired_cube_physical import physical
    row = json.loads((source/"certificates/paired-cube-complex-input.json").read_text())
    receipt = regenerate(row, output/"complex-export")
    write(output/"complex-regeneration.json", receipt)
    g, witness, word = [json.loads((output/"complex-export"/name).read_text())
                        for name in ("graph.json", "frames.json", "selection.json")]
    frames = validated_frames(args.frames, word["ops"], g["h"])
    pairs = json.loads((source/"references/paired-cube/physical/pairs.json").read_text())["pairs"]
    stage("Recounting selected physical frames and executing signed dirty replay")
    phys = physical(g, witness, word, row, frames, pairs)
    write(output/"physical-profile.json", phys)
    phase = complex_profile(phys, row)
    stage("Regenerating unchanged bit producer from frozen pair module and carrier arcs")
    folder = source/"research/paired-cube-bit"
    sys.path.insert(0, str(folder))
    from paired_cube_bit_word import build, dumps
    from check_paired_cube_bit import Checker
    arcs = json.loads((folder/"data/arcs_p12.json").read_text())
    _out, bitrow, regenerated_arcs, exports = build(12, arcs, log=stage)
    require(regenerated_arcs == arcs, "Regenerated bit carrier arcs differ")
    bitdir = output/"bit-export"
    bitdir.mkdir()
    for name, data in exports.items():
        (bitdir/(name+"_p12.json")).write_text(dumps(data))
    (bitdir/"profile_p12.json").write_text(dumps(bitrow))
    stage("Independently checking regenerated bit word and exact rational frame ranks")
    bitchecks = Checker(bitdir, 12).run()
    write(output/"bit-regeneration.json", dict(checks=bitchecks, fresh_profile=bitrow,
        export_sha256={p.name: digest(p) for p in sorted(bitdir.iterdir())}))
    bit = bit_profile(bitrow)
    stage("Enclosing full moments, including complete rare-class fallback")
    bmoment, cmoment = moment(bit, COARSE, True), moment(phase, AC)
    successor = moment(phase, AC+Q(1, 10**12))
    require(bmoment["strict_gap_lower"] > 0 and cmoment["strict_gap_lower"] > 0, "Strict supplier moments")
    require(successor["moment_lower"] > 1, "Complex successor grid point is not rigorously rejected")
    rank_upper = Q(bit["rank_per_vertex"])+BAD*(32*bit["m"]**2)*bit["edge_count"]
    require(rank_upper < bit["m"]*bit["W_per_vertex"], "Contaminated bit rank moment")
    require(Q(2*bit["m"]**3, 2**80) < BAD, "Fixed prime bad-class allowance")
    require(AB < ATOM < 1-AB, "Adapter and internally borrowed-row tolls")
    bridge = finite_bridge(phase, row)
    a = min(AB, (1-BETA)*AC-Q(1, 10**10))
    require(a == AB, "The selected placement did not free the available bit interface")
    result = assembly(a, AC, bridge, KAPPA)
    frozen_bit_hist = json.loads((folder/"out/profile_p12.json").read_text())["child_histogram"]
    require({int(r): n for r, n in frozen_bit_hist.items()} == bit["child_multiplicities"], "Unchanged binary supplier")
    elapsed = time.monotonic()-start
    certificate = dict(status="EXACT_FINITE", candidate_id=pin["candidate_id"],
        source_revision=pin["source_revision"], kappa=KAPPA,
        bit=dict(counts=bit, coarse=bmoment, coarse_saving=COARSE, effective_saving=AB,
            atom_exponent=ATOM, ordinary_leaf_saving=OLD, bad_fraction=BAD,
            fallback_children_per_edge=32*bit["m"]**2, rank_mass_upper_per_vertex=rank_upper,
            row_stock="Internal radix-q selector rows borrowed/restored; conservative old external row reserves retained"),
        complex=dict(counts=phase, **cmoment, successor_grid=successor),
        finite_bridge=bridge, assembly=result, source_sha256=hashes,
        candidate_frames_sha256=digest(args.frames), candidate_pin_sha256=digest(args.pin),
        fresh_complex_export_sha256={p.name: digest(p) for p in sorted((output/"complex-export").iterdir())},
        verification=dict(fresh_complex_producer=True, fresh_bit_producer=True,
            physical_forward_signed_dirty_replay=True, supplier_rational_enclosures=True,
            full_finite_scalar_precision_router_rows=True, strict_assembly_constraints=47, final_margins=7),
        inherited_hypotheses=["arbitrary-subspace Clifford implementation and fixed-tape routing",
            "completed-core sharing and three-stage source/target incidence cover",
            "uniform stopped local-ring recursion, rare-class fallback and ordinary wrapper",
            "exact common odd-grid precision, semantic induction and outer recovery",
            "retained analytic Gaussian/bulk-resampling and tape interfaces"],
        exclusions=["Independent reflected geometry review receipt required before ACCEPTED_CONDITIONAL",
            "Independent certificate review required before ACCEPTED_CONDITIONAL",
            "Full repository and relevant Lean coverage is separate",
            "Current public comparison and tested publication package required before PUBLICATION_READY",
            "No unconditional all-size multiplication theorem"],
        elapsed_seconds=elapsed, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    write(output/"certificate.json", certificate)
    write(output/"summary.json", dict(candidate_id=pin["candidate_id"], kappa=KAPPA,
        bit_saving=AB, complex_saving=AC, complex_strict_gap_lower=cmoment["strict_gap_lower"],
        complex_successor_excess_lower=successor["moment_lower"]-1,
        bit_contaminated_strict_gap_lower=bmoment["strict_gap_lower"],
        minimum_margin=result["minimum_margin"], absorption_gap=result["absorption_gap"],
        strict_constraints=47, margins=7, elapsed_seconds=elapsed,
        certificate_sha256=digest(output/"certificate.json")))
    stage("PASS finite suppliers and 47+7: kappa="+str(KAPPA)+" = "+format(float(KAPPA), ".12g"))


if __name__ == "__main__":
    main()
