#!/usr/bin/env python3
"""Independent rational review of the frozen paid balanced composition.

Apache-2.0. Prepared with OpenAI GPT-6.1 Sol assistance for RaD.
No producer, candidate checker, upstream module or saved verdict is imported.
The reviewed equations inherit the PR23/29, RaD, James Chang PR34,
Rohan Arun PR100/103, icekylinx/eumemic PR104/144/152/161 and chafreaky
PR141/163 contribution lineage. See ../NOTICE and the source inventory.

This review consumes explicitly pinned finite inputs. It reconstructs the
complex child distribution from its component counts and checks all binary
counts and exact moments. The independent binary finite word/annihilator
proof and complemented complex signed geometry remain separate prerequisites.
Paid all-size layout, routing, restoration and analytic contracts are stated
dependencies; rational arithmetic is not a proof of those contracts.
"""

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

GRID = 1 << 224
COARSE = F(594996721, 10**12)
ATOM = F(1, 1000)
OLD = F(384599, 10**10)
BAD = F(1, 10**16)
BIT = (1-ATOM)*COARSE + ATOM*OLD
COMPLEX = F(74320127, 125000000000)
BETA = F(1, 10**9)
ETA = F(1, 10**8)
WEAKENING = F(1, 10**10)
KAPPA = F(594087017, 10**12)
PUBLIC = F(148492550769873, 250000000000000000)
INPUTS = {"bit", "bit_frames", "complex_frames", "complex_graph",
          "complex_selection", "physical", "scalar"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, name, minimum=0):
    need(type(value) is int and value >= minimum, "Invalid integer: " + name)
    return value


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def exact_match(observed, expected, where):
    """Type-sensitive comparison also rejects bools masquerading as integers."""
    expected = encode(expected)
    need(type(observed) is type(expected), "Wrong type: " + where)
    if isinstance(expected, dict):
        need(set(observed) == set(expected), "Wrong fields: " + where)
        for name, value in expected.items():
            exact_match(observed[name], value, where + "." + name)
    elif isinstance(expected, list):
        need(len(observed) == len(expected), "Wrong length: " + where)
        for i, value in enumerate(expected):
            exact_match(observed[i], value, where + "." + str(i))
    else:
        need(observed == expected, "Independent recomputation differs: " + where)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def pinned_bytes(root, pin):
    name = pin["path"]
    relative = Path(name)
    need(isinstance(name, str) and not relative.is_absolute()
         and ".." not in relative.parts, "Unsafe pinned path")
    data = (root/relative).read_bytes()
    need(sha256(data).hexdigest() == pin["sha256"], "Pinned input/source mismatch: " + name)
    return data


def down(x):
    z = x*GRID
    return F(z.numerator//z.denominator, GRID)


def up(x):
    z = x*GRID
    return F(-(-z.numerator//z.denominator), GRID)


def log_interval(x):
    """80 positive atanh terms; omitted tail is bounded geometrically."""
    need(x >= 1, "Logarithm domain")
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def unit(y):
        z = (y-1)/(y+1)
        zz, power, total = z*z, z, F(0)
        for j in range(80):
            total += 2*power/(2*j+1)
            power *= zz
        return total, total+2*power/(161*(1-zz))

    a, b = unit(x)
    a2, b2 = unit(F(2))
    return down(a+k*a2), up(b+k*b2)


def exp_interval(lo, hi):
    """Degree fourteen; the first omitted term has ratio at most hi/16."""
    need(0 <= lo <= hi < F(1, 2), "Exponential domain")
    low_term = high_term = low = high = F(1)
    for j in range(1, 15):
        low_term *= lo/j
        high_term *= hi/j
        low += low_term
        high += high_term
    tail = (high_term*hi/15)/(1-hi/16)
    return down(low), up(high+tail)


def moment(row, saving, fallback=False):
    low = high = F(0)
    for r, n in row["hist"].items():
        lo, hi = log_interval(F(row["m"], r))
        lo, hi = exp_interval(saving*lo, saving*hi)
        weight = F(r*n, row["m"]*row["W"])
        low += weight*lo
        high += weight*hi
    ideal_low, ideal_high = down(low), up(high)
    added_low = added_high = F(0)
    if fallback:
        lo, hi = log_interval(F(row["m"]))
        lo, hi = exp_interval(saving*lo, saving*hi)
        weight = BAD*F(32*row["m"]**2*row["edges"], row["m"]*row["W"])
        added_low, added_high = down(weight*lo), up(weight*hi)
    return dict(saving=saving, exponent=1-saving, lower=down(ideal_low+added_low),
                upper=up(ideal_high+added_high), gap_lower=down(1-ideal_high-added_high),
                ideal_lower=ideal_low, ideal_upper=ideal_high,
                fallback_lower=added_low, fallback_upper=added_high,
                grid_denominator=GRID, atanh_terms=80, exponential_degree=14)


def histogram(raw, name):
    need(isinstance(raw, dict), "Histogram object: " + name)
    out = Counter()
    for key, count in raw.items():
        need(isinstance(key, str) and key.isascii() and key.isdecimal(), "Rank key: " + name)
        rank = int(key)
        need(str(rank) == key, "Noncanonical rank key: " + name)
        integer(count, name)
        out[rank] += count
    return out


def complete_profile(raw, expected, component=False):
    m, w = integer(raw["m"], "m", 1), integer(raw["W_per_vertex"], "W", 1)
    h = histogram(raw["child_histogram"], "complete children")
    need(0 not in h and all(0 < r < m and n > 0 for r, n in h.items()), "Proper positive children")
    mass = sum(r*n for r, n in h.items())
    need(mass == integer(raw["rank_per_vertex"], "rank mass"), "Rank mass differs")
    need(m*w-mass == integer(raw["deficit_per_vertex"], "deficit", 1), "Deficit differs")
    need((m, w, mass, max(h)) == expected, "Frozen dimensions or maximum child changed")
    if component:
        fresh = Counter()
        for field in ("local_histogram", "source_data_histogram", "target_data_histogram"):
            for r, n in histogram(raw[field], field).items():
                fresh[r] += 3*n
        for r, n in histogram(raw["physical_gauge_histogram"], "physical gauges").items():
            fresh[3*r] += n
        fresh[2] += 2*raw["v"]
        fresh.pop(0, None)
        need(fresh == h, "Complex component reconstruction differs")
    return dict(m=m, W=w, hist=dict(sorted(h.items())), mass=mass,
                maxchild=max(h), edges=sum(h.values()))


def bridge(physical, scalar, cp):
    h, v, roles, centres, roots, mixers = (integer(scalar[k], k, 1)
        for k in ("h", "v", "R", "c", "q", "total_M_operations"))
    need((h, v, roles, centres, roots, mixers) == (22, 1320, 16011, 17735, 4477, 32426),
         "Unfused complex scalar input changed")
    need(roles == centres+roots-integer(scalar["matched"], "matching"), "Virtual role inventory")
    need((physical["h"], physical["v"], physical["R"], physical["loss"])
         == (h, v, roles, 440), "Physical scalar inventory")
    need((physical["physical_R"], physical["pairs"], physical["late_pairs"])
         == (13041, 2970, 2970), "Reuse and compensation inventory")
    need(physical["physical_R"] == roles-physical["pairs"] and
         cp["W"] == 2*v+physical["physical_R"] and cp["m"] == 3*h,
         "Persistent complex stock")
    need(cp["m"]*cp["W"]-cp["mass"] == 2*v-3*scalar["loss"] == 1320,
         "Shared-core telescoping")
    need(3*roots < 1 << 15, "Expanded readout numerator bound")
    m = cp["m"]
    n = m//2
    V = (1 << (m-1+(n-1)**2))*prod((1 << (2*i))-1 for i in range(1, n))
    W, s, N = V*cp["W"], V*cp["mass"], V*v
    setup = 4*(centres+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    readout, involution = 8*roles*v*(mixers+16), 32*v
    local = setup+readout+involution
    logical = 3*V*local+8*W+4*N+8*m*roles*V
    router = 64*(m+1)**3*(logical+1)*(W+1)**2
    E = 64*(W+m+router+1)**3
    literal = 2*router*W*W+8*s+4*W+4+32*m
    B, C0 = s+E, 32*m*(s+E)**2
    degree = 1
    while m**degree <= 2*cp["maxchild"]**degree:
        degree += 1
    row_coefficient = degree*W.bit_length()+9909+252
    out = dict(V=V, W=W, s=s, N=N, m=m, maxchild=cp["maxchild"],
        physical_roles=physical["physical_R"], scalar_roles=roles, reuse_pairs=physical["pairs"],
        local_scalar=local, logical_scalar=logical, router=router, E=E, literal=literal,
        B=B, C0=C0, C1=1, strict_literal_gap=E-literal,
        induction_gap=2*B*(m-cp["maxchild"])-s-E, guard_gap=C0-2*B-18,
        halving_degree=degree, wire_bits=W.bit_length(), complex_coefficient=degree*W.bit_length(),
        old_coarse_reserve=9909, old_leaf_reserve=252, row_coefficient=row_coefficient,
        row_degree=70000, row_gap=F(70000)-F(51*row_coefficient, 25), suffix_slope=280000,
        ordinary_saving=BIT, atom=ATOM, coarse=COARSE, old=OLD,
        adapter_gap=ATOM-BIT, internal_row_gap=1-BIT-ATOM, fixed_odd_divisor=3)
    need(all(out[k] > 0 for k in ("strict_literal_gap", "induction_gap", "guard_gap",
                                  "row_gap", "adapter_gap", "internal_row_gap")),
         "Finite guard, row or adapter bill failed")
    details = dict(setup_scalar=setup, expanded_readout_scalar=readout,
        involution_scalar=involution, decoder_denominator_divides=6,
        scalar_coefficient_bound=h+4, readout_numerator_binary_digits=mixers+16,
        common_odd_grid="One common dyadic grid times 3^(-K_grid); incoming odd exponent retained; no child rounding",
        internal_selector_stock="Borrowed and restored radix-q rows under the completed ordinary wrapper",
        full_group_bits=V.bit_length())
    return out, details


def assemble(bill, *, kappa=KAPPA, old_prefix=False, old_exposures=False, old_guard=False):
    a = min(BIT, (1-BETA)*COMPLEX-WEAKENING)
    need(a == BIT, "Supplier minimum unexpectedly weakened the binary interface")
    q = a*(1-2*ETA)
    c, epsilon = q+ETA/4, (1-ETA)/(1+q)
    tau, sigma = 1-a, 1-COMPLEX
    lp, lam = 1-q, (tau+1-q)/2
    g, delta = epsilon*q, ETA/8
    r = (g+1-epsilon)/2
    internal = tau+(1-BETA)*max(sigma-tau, F(0))
    leaf = sigma+BETA*(1-sigma)
    margins = dict(prefix=1-epsilon, movement=a, compact=g, bulk=a,
        Gaussian=min(1-epsilon-delta, r-delta), scalar=1-epsilon-delta, dimension=epsilon)
    if old_prefix:
        margins["prefix"] = 1-epsilon*(1+c)
    if old_exposures:
        margins["movement"] = epsilon*a*c
        margins["bulk"] = a*(1-epsilon)
    slacks = dict(a_positive=a, a_below_b=COMPLEX-a, b_below_one_over32=F(1,32)-COMPLEX,
        beta_positive=BETA, beta_below_one=1-BETA, phase_leaf_above_bit=(1-BETA)*COMPLEX-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma, lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=lp-lam, compact_leaf=lp-leaf, compact_reservations=lp-(1-c),
        lambda_prime_below_one=q, epsilon_positive=epsilon, epsilon_below_one=1-epsilon,
        guard_width=1-epsilon*(F(19991,10000) if old_guard else 1),
        K_geometry=1-epsilon*(1+c), K_dominates_log=epsilon*c, record_suffix=1-epsilon,
        phase_local=1-epsilon-delta, phase_boundary=r-delta, gamma_sublinear=1-epsilon-r,
        cell_above_band=epsilon-(1-r)/2, prime_interval_packing=1-epsilon,
        alpha_positive=r, alpha_below_one=1-r, alpha_below_one_fourth=F(1,4)-r,
        delta_positive=delta, delta_below_one_eighth=F(1,8)-delta,
        short_record_fallback=epsilon-a, small_field_exposure=1-epsilon-g,
        artificial_boundary=8-epsilon+r-delta-g,
        literal_scalar_guard=bill["strict_literal_gap"], row_product_gap=bill["row_gap"])
    slacks.update({name+"_above_kappa": value-kappa for name, value in margins.items()})
    need(len(slacks) == 47 and len(margins) == 7, "Incomplete 47+7")
    need(all(value > 0 for value in slacks.values()), "Nonpositive assembly constraint")
    need(min(margins.values()) == g and 1-epsilon-g == ETA
         and 1-epsilon-r == ETA/2 and c-q == ETA/4
         and 1-epsilon*(1+c) == ETA-epsilon*ETA/4, "Balanced algebra identity")
    return dict(a=a, b=COMPLEX, beta=BETA, eta=ETA, weakening=WEAKENING,
        q=q, c=c, epsilon=epsilon, lambda_=lam, lambda_prime=lp, g=g, r=r, delta=delta,
        kappa=kappa, tau=tau, sigma=sigma, internal=internal, leaf=leaf,
        margins=margins, slacks=slacks, absorption_gap=g-kappa, strict_ceiling=a/(1+a))


def ceil(x):
    return -(-x.numerator//x.denominator)


def thresholds(bill, assembly):
    e, c, r = (assembly[k] for k in ("epsilon", "c", "r"))
    ka, km, kb, ks = (ceil(1/x) for x in (r, e*c, 1-e, e*BETA))
    arity = 575
    cuts = dict(guard=ceil(F((2*bill["C0"]).bit_length())/(1-e)),
        normalization=ceil(7/(1-e-r)), alpha=16*ka*ka+1, compact=64*km*km+1,
        geometry=ceil(3/(1-e*(1+c))), phase_cell=ceil(9/(e-(1-r)/2)),
        period=128*kb*kb+1, stopped_leaf=ks*(4*arity).bit_length(), log_p=25, reservoir=14)
    common = max(cuts.values())
    checkpoints = []
    for j in range(6):
        z = common*(1 << j)
        pairs = dict(alpha=(z//ka, 8*(z+ka)+64), compact=(z//km, 32*(z+km)+192),
            period=(z//kb, 16*(z+kb)+56), rows=(z//kb, bill["suffix_slope"]*(z+kb+8)),
            leaf=(z//ks, 4*arity))
        need(all(lhs >= rhs.bit_length() for lhs, rhs in pairs.values()), "Threshold inequality")
        checkpoints.append(dict(log2_input=z, checks={name: dict(exponent=lhs, rhs=rhs,
            rhs_bits=rhs.bit_length()) for name, (lhs, rhs) in pairs.items()}))
    return dict(cuts=cuts, common=common, checkpoints=checkpoints, largest_arity=arity,
        scope="Sufficient arithmetic thresholds only; setup, prime, catalogue, logarithm and recovery thresholds remain inherited eventual conditions.")


def compare(candidate, expected):
    for name, value in expected.items():
        need(name in candidate, "Missing certificate field: " + name)
        exact_match(candidate[name], value, name)


def verify_intervals(candidate, intervals):
    for name, independent in intervals.items():
        reported = candidate[name]
        need(set(reported) == {"lower", "upper", "gap_lower"}, "Reported interval fields")
        need(all(isinstance(value, str) for value in reported.values()), "Reported rational interval types")
        lo, hi, gap = (F(reported[k]) for k in ("lower", "upper", "gap_lower"))
        need(0 < lo <= independent["lower"] <= independent["upper"] <= hi,
             "Author interval does not contain the independent tighter enclosure: " + name)
        need(gap == 1-hi, "Reported interval gap differs: " + name)


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "Output must have a fresh identity")
    started = time.monotonic()
    config = json.loads(args.config.read_text())
    need(set(config["inputs"]) == INPUTS and len(config["sources"]) == 75, "Frozen source/input inventory")
    chosen = dict(coarse=COARSE, atom=ATOM, complex_saving=COMPLEX, phase_stop=BETA,
                  backoff=ETA, strict_weakening=WEAKENING, kappa=KAPPA)
    for name, value in chosen.items():
        exact_match(config[name], value, "config."+name)
    values = {name: json.loads(pinned_bytes(args.sprint, pin))
              for name, pin in config["inputs"].items()}
    for pin in config["sources"].values():
        pinned_bytes(args.sprint, pin)
    candidate = json.loads(args.certificate.read_text())
    exact_match(candidate["source_pins"], config, "certificate.source_pins")
    need(candidate["config_sha256"] == digest(args.config), "Config identity differs")
    physical, scalar, bit = (values[name] for name in ("physical", "scalar", "bit"))
    need((bit["h"], bit["v"], bit["R"], bit["loss"], bit["virtual_R"])
         == (24, 1760, 23368, 528, 23368), "Binary word dimensions")
    need(bit["selected_rank_histogram"] == {"20": 5720} and bit["reused_registers"] == 0
         and bit["zero_rank_handoffs"] == 0, "Binary retained gauges or role reuse")
    bp = complete_profile(bit, (72, 26888, 1934000, 60))
    cp = complete_profile(physical, (66, 15681, 1033626, 20), component=True)
    need(bp["m"]*bp["W"]-bp["mass"] == 2*1760-3*528 == 1936, "Binary telescoping")
    bm, bn = moment(bp, COARSE, True), moment(bp, COARSE+F(1,10**12), True)
    cm, cn = moment(cp, COMPLEX), moment(cp, COMPLEX+F(1,10**12))
    need(bm["upper"] < 1 < bn["lower"] and cm["upper"] < 1 < cn["lower"], "Full supplier separation")
    rank = F(bp["mass"])+BAD*32*bp["m"]**2*bp["edges"]
    prime_gap = BAD-F(2*bp["m"]**3, 1 << 80)
    need(prime_gap > 0 and rank < bp["m"]*bp["W"], "Complete bad-class rank/prime bill")
    bill, details = bridge(physical, scalar, cp)
    assembly = assemble(bill)
    cutoff = thresholds(bill, assembly)
    improvement = KAPPA-PUBLIC
    need(improvement > 0, "Pinned frontier improvement failed")
    expected = dict(candidate_id=config["candidate_id"], coarse_bit_saving=COARSE, atom=ATOM,
        ordinary_bit_saving=BIT, complex_saving=COMPLEX, kappa=KAPPA,
        bit_profile=bp, complex_profile=cp, contaminated_bit_rank=rank,
        bridge=bill, assembly=assembly, cutoffs=cutoff)
    compare(candidate, expected)
    intervals = dict(bit_moment=bm, bit_next_grid=bn, complex_moment=cm, complex_next_grid=cn)
    verify_intervals(candidate, intervals)
    need(all(F(candidate[name]["upper"]) < 1 for name in ("bit_moment", "complex_moment"))
         and all(F(candidate[name]["lower"]) > 1 for name in ("bit_next_grid", "complex_next_grid")),
         "Author interval does not have the independently checked strict separation")
    rejected = []

    def reject(name, call):
        try:
            call()
        except (ValueError, KeyError, ZeroDivisionError):
            rejected.append(name)
        else:
            raise ValueError("Negative control accepted: " + name)

    for name, field, replacement in (
        ("local stock substituted for full W", "W", cp["W"]),
        ("virtual scalar roles collapsed to physical", "scalar_roles", physical["physical_R"]),
        ("scalar charge omitted", "local_scalar", 0),
        ("router charge omitted", "router", 0),
        ("ordinary leaf reserve omitted", "old_leaf_reserve", 0),
        ("old coarse reserve omitted", "old_coarse_reserve", 0),
        ("row coefficient understated", "row_coefficient", 1),
        ("insufficient row degree", "row_degree", 1),
        ("stale semantic guard", "C0", 1),
        ("ordinary supplier overstated", "ordinary_saving", str(BIT+F(1,10**24))),
    ):
        mutated = copy.deepcopy(candidate)
        mutated["bridge"][field] = replacement
        reject(name, lambda value=mutated: compare(value, expected))
    mutated = copy.deepcopy(candidate)
    mutated["bit_profile"]["hist"]["1"] += 2
    mutated["bit_profile"]["hist"]["2"] -= 1
    reject("mass-preserving child histogram mutation", lambda: compare(mutated, expected))
    fake_interval = copy.deepcopy(candidate)
    fake_interval["bit_moment"]["upper"] = "9/10"
    fake_interval["bit_moment"]["gap_lower"] = "1/10"
    reject("fabricated saved supplier enclosure", lambda: verify_intervals(fake_interval, intervals))
    reject("old prefix at balanced parameters", lambda: assemble(bill, old_prefix=True))
    reject("old separated movement/exposure charges", lambda: assemble(bill, old_exposures=True))
    reject("old nonlinear semantic guard", lambda: assemble(bill, old_guard=True))
    reject("kappa at the strict margin", lambda: assemble(bill, kappa=assembly["g"]))
    reject("kappa above the strict margin", lambda: assemble(bill, kappa=assembly["g"]+F(1,10**18)))
    badpin = dict(config["inputs"]["bit_frames"], sha256="0"*64)
    reject("corrupted source/input identity", lambda: pinned_bytes(args.sprint, badpin))
    reject("unsafe source path", lambda: pinned_bytes(args.sprint, dict(path="../escape", sha256="0"*64)))
    probe = subprocess.run([sys.executable, "-O", str(Path(__file__).resolve()), "--help"],
                           capture_output=True, text=True)
    need(probe.returncode != 0 and "Assertion-disabled Python" in probe.stderr, "Optimized execution was accepted")
    rejected.append("assertion-disabled execution")
    result = dict(status="PASS independent conditional balanced arithmetic", **expected,
        certificate_sha256=digest(args.certificate), configuration_sha256=digest(args.config),
        own_checker_sha256=digest(Path(__file__)), source_pins=config["sources"], input_pins=config["inputs"],
        checked_source_count=len(config["sources"]), checked_input_count=len(values),
        independent_intervals=dict(bit=bm, bit_next_grid=bn, complex=cm, complex_next_grid=cn),
        prime_bad_fraction_gap=prime_gap, scalar_bill_details=details,
        rejected_controls=rejected, public_comparison=dict(public_kappa=PUBLIC, improvement=improvement,
        scope="Pinned mathematical PR163 comparison; live public refresh belongs to coordinator"),
        proof_boundary=dict(binary="Supplied pinned complete histogram; independent finite bit/F2/dual-Gram reconstruction is a separate prerequisite",
            complex="Component histogram reconstructed here; source/destination reflection and signed inverse checked by independent geometry lane",
            transfer="Balanced named-coordinate layout, paid arbitrary-coordinate router and full bulk gathers depend on retained reviewed all-size interfaces",
            formal="No unconditional all-size theorem, practical threshold, hosted CI or unrelated Lean coverage is asserted"),
        elapsed_seconds=time.monotonic()-started, observation_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(encode(result), indent=2, sort_keys=True)+"\n")
    print("PASS: kappa="+str(KAPPA)+"; 75 source pins, 7 input pins; all 47+7; "
          +str(len(rejected))+" negative controls; certificate="+digest(args.certificate))
    print("Strict absorption gap="+str(assembly["absorption_gap"])
          +"; pinned public improvement="+str(improvement))


if __name__ == "__main__":
    main()
