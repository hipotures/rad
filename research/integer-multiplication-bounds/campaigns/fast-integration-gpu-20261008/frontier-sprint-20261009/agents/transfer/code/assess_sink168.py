#!/usr/bin/env python3
"""Paid source-bound PR168 terminal-sink arithmetic and fixed-profile limits.

This checker imports no upstream producer or finite-word implementation.
Literal signed identity and complemented geometry are separate prerequisites.
Apache-2.0; prepared with OpenAI GPT-6.1 Sol assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import prod
from pathlib import Path
import argparse
import copy
import json
import sys

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from check_balanced_composition import (BAD, OLD, balanced, ceil, cutoffs,
    halving, js, moment, profile, require)
from certify_lifetime_fused import pinned, reconstruct
from assess_frontier import exact_root_bracket


def sink_profile(row):
    hist = Counter()
    for field in ('local_histogram', 'source_data_histogram', 'target_data_histogram'):
        for rank, count in row[field].items():
            hist[int(rank)] += 3 * int(count)
    for rank, count in row['physical_gauge_histogram'].items():
        hist[3 * int(rank)] += int(count)
    hist[2] += 2 * row['v']
    hist.pop(0, None)
    require(dict(hist) == {int(r): n for r, n in row['child_histogram'].items() if n},
            'Complete sink component histogram does not reconstruct')
    p = profile(row['m'], row['W_per_vertex'], hist)
    require(p['m'] == 3 * row['h'] and p['W'] == 2 * row['v'] + row['physical_R'],
            'Sink dimension and physical stock')
    require(row['physical_R'] == row['R'] - row['pairs'] - row['sinks'],
            'Aliases and sinks are distinct paid role reductions')
    require(p['mass'] == row['rank_per_vertex'] and
            p['m'] * p['W'] - p['mass'] == row['deficit_per_vertex'] ==
            2 * row['v'] - 3 * row['loss'], 'Sink telescoping rank')
    return p


def sink_bridge(physical, scalar, coarse, atom, *, widened=True):
    """Retain all base charges, with an explicit optional sink overpayment.

    D bounds every extra target shear and every possible substituted half-write.
    Two additional cleared-numerator bits per event cover additive half-shears.
    This bound does not assume cancellation to obtain cheaper readout digits.
    """
    h, v, R, c, M = (int(scalar[k]) for k in ('h', 'v', 'R', 'c', 'total_M_operations'))
    require(R == scalar['c'] + scalar['q'] - scalar['matched'] == physical['R'],
            'Virtual scalar inventory')
    require(3 * (scalar['q'] - physical['sinks'] + M) < 2**18,
            'Conservative effective-root envelope')
    p = sink_profile(physical)
    half = p['m'] // 2
    V = 2**(p['m'] - 1 + (half - 1)**2) * prod(2**(2*i) - 1 for i in range(1, half))
    W, s, N = V * p['W'], V * p['mass'], V * v
    base = 4*(c+v) + 10*v + 4*h*v + 4*h*h + 8*h + 8 + 2*h + 8*R*v*(M+16) + 32*v
    target_shears = 2 * physical['sinks'] * (8 - 1)
    D = target_shears + M
    # With all M possible half-writes, the root envelope needs 18 rather than
    # 15 signed bits. Actual fresh event count independently restores 15 below.
    extra_digits = 2 * D + 3 if widened else 0
    extra_primitives = 4 * D if widened else 0
    local = base + 8 * R * v * extra_digits + extra_primitives
    logical = 3*V*local + 8*W + 4*N + 8*p['m']*R*V
    router = 64*(p['m']+1)**3*(logical+1)*(W+1)**2
    E = 64*(W+p['m']+router+1)**3
    charge = 2*router*W**2 + 8*s + 4*W + 4 + 32*p['m']
    B = s + E
    C0 = 32*p['m']*B**2
    degree = halving(p['m'], p['maxchild'])
    coefficient = degree*W.bit_length() + 9909 + 252
    actual = (1-atom)*coarse + atom*OLD
    require(actual < atom < 1-actual, 'Paid atom adapters or internal rows fail')
    result = dict(V=V, W=W, s=s, N=N, m=p['m'], maxchild=p['maxchild'],
        physical_roles=physical['physical_R'], scalar_roles=R, reuse_pairs=physical['pairs'],
        sinks=physical['sinks'], base_local_scalar=base, additional_event_bound=D,
        additional_target_shears=target_shears, additional_readout_digits=extra_digits,
        additional_primitive_bill=extra_primitives, readout_digit_bound=M+16+extra_digits,
        local_scalar=local, logical_scalar=logical, router=router, E=E, literal=charge,
        B=B, C0=C0, C1=1, strict_literal_gap=E-charge,
        induction_gap=2*B*(p['m']-p['maxchild'])-s-E, guard_gap=C0-2*B-18,
        halving_degree=degree, wire_bits=W.bit_length(), complex_coefficient=degree*W.bit_length(),
        old_coarse_reserve=9909, old_leaf_reserve=252, row_coefficient=coefficient,
        row_degree=70000, row_gap=Q(70000)-Q(51*coefficient,25), suffix_slope=280000,
        ordinary_saving=actual, atom=atom, coarse=coarse, old=OLD,
        adapter_gap=atom-actual, internal_row_gap=1-actual-atom, fixed_odd_divisor=3)
    require(min(result[k] for k in ('strict_literal_gap', 'induction_gap', 'guard_gap', 'row_gap')) > 0,
            'Complete sink scalar/precision/row bill fails')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Optimized execution unsupported')
    require(not args.output.exists(), 'Output must be fresh')
    config = json.loads(args.config.read_bytes())
    raw = {key: pinned(args.sprint, item) for key, item in config['inputs'].items()}
    for item in config['sources'].values():
        pinned(args.sprint, item)
    data = {key: json.loads(value) for key, value in raw.items()}
    certificate = data['public_certificate']
    all_pins = list(config['inputs'].values()) + list(config['sources'].values())
    for name, digest in certificate['source_sha256'].items():
        require(any(p['path'].endswith('/'+name) and p['sha256'] == digest for p in all_pins),
                'Public declared source omitted: '+name)
    for key in ('native_protocol', 'body_protocol'):
        record = data[key]
        for name, digest in record['source_pins'].items():
            require(any(p['path'].endswith('/'+name) and p['sha256'] == digest for p in all_pins),
                    'Regenerated protocol source omitted: '+name)
        for name, item in record['input_pins'].items():
            require(any(p['path'].endswith('/'+name) and p['sha256'] == item['sha256'] for p in all_pins),
                    'Regenerated protocol input omitted: '+name)
    bit, physical, scalar = (data[key] for key in ('bit', 'physical', 'scalar'))
    require(data['native_profile'] == physical, 'Producer-regenerated sink profile differs')
    bp, cp = reconstruct(bit, True), sink_profile(physical)
    require((bp['m'], bp['W'], bp['mass'], bit['R'], bit['physical_R'], bit['pairs']) ==
            (72, 21812, 1568528, 20052, 18292, 1760), 'Changed binary inventory')
    require((cp['m'], cp['W'], cp['mass'], scalar['R'], physical['physical_R'], physical['pairs'], physical['sinks']) ==
            (66, 13894, 915684, 13606, 11254, 2310, 42), 'Changed sink inventory')
    require((scalar['c'], scalar['q'], scalar['matched'], scalar['total_M_operations']) ==
            (20686, 3157, 10237, 32972), 'Changed source signed scalar inventory')
    inventory = dict(Counter(e[0] for e in data['forward_events']))
    require(inventory == dict(Counter(e[0] for e in data['reflected_events'])) ==
            data['native_reconstruction']['forward_inventory'], 'Raw literal event inventory')
    require(inventory['ysh'] == 588 and inventory['yw'] == 115 and inventory['op'] == 65714,
            'Fresh substituted literal operation counts')
    effective_q = scalar['q'] - physical['sinks'] + inventory['yw']
    require(3*effective_q < 2**15, 'Actual half-read numerator reserve')
    primitive = inventory['op'] + inventory['inj'] + inventory['ysh'] + 2*inventory['yw']
    require(primitive <= 4*(scalar['c']+scalar['v']), 'Actual extra primitives exceed retained allowance')
    P = (1 << 61)-1
    for event in data['forward_events'] + data['reflected_events']:
        if event[0] == 'ysh':
            require(event[3] in (-1, 1), 'Nonunit target shear')
        elif event[0] == 'yw':
            require(event[3] in ((P+1)//2, P-(P+1)//2), 'Nonhalf pivot write')
    require(len(data['sink_map']) == 42 and all(len(z['T']) == 8 for z in data['sink_map']),
            'Terminal target groups')
    groups = [t for z in data['sink_map'] for t in z['T']]
    require(len(groups) == len(set(groups)), 'Overlapping sink target groups')
    coarse, atom, b, beta, eta, zeta, public = (Q(config[key]) for key in
        ('coarse', 'atom', 'complex_saving', 'phase_stop', 'backoff', 'strict_weakening', 'public_kappa'))
    require(Q(certificate['kappa']) == public == Q(40557,62500000), 'Pinned frontier score')
    bb, cb = exact_root_bracket(bp, BAD), exact_root_bracket(cp, Q(0))
    require(moment(bp, coarse, BAD)['upper'] < 1 and moment(cp,b)['upper'] < 1,
            'Advertised full supplier moments fail')
    source_bridge = sink_bridge(physical, scalar, coarse, atom, widened=False)
    paid_bridge = sink_bridge(physical, scalar, coarse, atom)
    source_assembly = balanced(source_bridge,b,beta,eta,zeta,kappa=public)
    paid_assembly = balanced(paid_bridge,b,beta,eta,zeta,kappa=public)
    require(sorted(Q(x) for x in certificate['assembly']['strict_constraints'].values()) ==
            sorted(source_assembly['slacks'].values()), 'Public 47 inequalities differ')
    require(sorted(Q(x) for x in certificate['assembly']['margins'].values()) ==
            sorted(source_assembly['margins'].values()), 'Public seven margins differ')
    for field, section, name in [('W','complex','W'),('s','complex','s'),('N','complex','N'),
        ('local_scalar','complex','local_group_upper'),('logical_scalar','complex','logical_group_upper'),
        ('router','complex','scalar_group_upper'),('E','semantic','E'),('B','semantic','B'),
        ('C0','semantic','C0'),('literal','semantic','literal_charge'),
        ('row_coefficient','rows','coefficient'),('row_gap','rows','degree_gap')]:
        actual = certificate['finite_bridge'][section][name]
        if isinstance(source_bridge[field],Q):
            actual = Q(actual)
        require(actual == source_bridge[field], 'Full sink source bill differs: '+field)
    target = Q(config['required_ratio'])*public
    require(target == Q(4096257,6250000000), 'Latest exact one-percent floor')
    need = target/((1-2*eta)*(1-eta-target))
    requirements = dict(ideal_ordinary_complex=target/(1-target), ordinary=need,
        complex=(need+zeta)/(1-beta), optimized_coarse=need*(1-OLD)/(1-need))
    ordinary_upper = bb['upper']/(1+bb['upper']-OLD)
    native_upper = min(ordinary_upper,cb['upper'])
    ceiling = native_upper/(1+native_upper)
    require(ceiling < target, 'Fixed-profile obstruction fails')
    controls = []
    def reject(name, call):
        try:
            call()
        except (KeyError,ValueError,ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError('Negative control accepted: '+name)
    reject('current one-percent floor on fixed suppliers', lambda: balanced(paid_bridge,b,beta,eta,zeta,kappa=target))
    reject('preceding unpaid atom grid', lambda: sink_bridge(physical,scalar,coarse,atom-Q(1,10**12)))
    reject('sink charged as alias-only stock', lambda: sink_profile(dict(physical,sinks=0)))
    reject('deleted physical sinks returned to W', lambda: sink_profile(dict(physical,W_per_vertex=13936)))
    reject('virtual scalar roles collapsed', lambda: sink_bridge(physical,dict(scalar,R=11254),coarse,atom))
    reject('literal bill omitted', lambda: balanced(dict(paid_bridge,strict_literal_gap=0),b,beta,eta,zeta,kappa=public))
    reject('old separate prefix', lambda: balanced(paid_bridge,b,beta,eta,zeta,kappa=public,old_prefix=True))
    reject('source pin damaged', lambda: pinned(args.sprint,dict(config['inputs']['physical'],sha256='0'*64)))
    result = dict(status='PASS conditional sink arithmetic, paid conservative bridge and fixed-profile obstruction',
        source_pins=config, config_sha256=sha256(args.config.read_bytes()).hexdigest(),
        bit_profile=bp, complex_profile=cp, bit_root=bb, complex_root=cb,
        actual_event_inventory=inventory, effective_half_reads=effective_q, actual_primitive_bill=primitive,
        source_bridge=source_bridge, paid_bridge=paid_bridge, source_assembly=source_assembly,
        paid_assembly=paid_assembly, numeric_cutoffs=cutoffs(paid_bridge,paid_assembly),
        target=dict(kappa=target,required_ratio=Q(config['required_ratio']),requirements=requirements,
            sufficient_1e12_points={key:Q(ceil(value*10**12),10**12) for key,value in requirements.items()}),
        fixed_profile_obstruction=dict(ordinary_upper=ordinary_upper,complex_upper=cb['upper'],
            controlling_upper=native_upper,balanced_upper=ceiling,shortfall=target-ceiling,
            scope='Every reserve/paid-atom choice in this retained transfer family on these fixed complete profiles.'),
        rejected_controls=controls,
        scope='No upstream code imported. Native source/profile/event reconstruction and exact signed receipt are hash-bound, not re-executed here. Independent all-column identity, local-ring primes and literal complemented geometry remain separate gates. Completed tensors, ordinary restoration, router/layout, common-grid analytic recovery and tape hypotheses remain conditional.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS latest sink κ='+str(public)+'; conservative L='+str(paid_bridge['local_scalar'])+
          '; fixed-profile ceiling '+str(ceiling)+' below one-percent floor '+str(target))


if __name__ == '__main__':
    main()
