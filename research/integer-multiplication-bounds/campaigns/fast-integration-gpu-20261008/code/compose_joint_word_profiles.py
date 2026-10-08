#!/usr/bin/env python3
"""Compose actual, already center-corrected joint-word width profiles.

Credits: Avi Eisenberg's interval graph, eumemic's joint binary compiler,
Alejandro Zarzuelo Urdiales's refined comparison, and inherited contributors.
This arithmetic gate does not replace source, word, geometry or proof gates.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path
from exact_composition import choose, reconstruct, moment, js
from bind_source_profile_certificate import moment_bounds


def exact(x):
    if isinstance(x, dict):
        return {k: exact(v) for k, v in x.items()}
    if isinstance(x, list):
        return [exact(v) for v in x]
    if isinstance(x, str) and '/' in x:
        try:
            return Q(x)
        except ValueError:
            return x
    return x


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--axes', type=Path, required=True)
    p.add_argument('--phase', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--assembly', type=Path, required=True)
    p.add_argument('--geometry', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists()
    axes = json.loads(a.axes.read_text())
    if isinstance(axes, dict):
        axes = [axes['axes'][str(h)] for h in [23,25]]
    profiles = [x.get('profile', x) for x in axes]
    assert [x['h'] for x in profiles] == [23, 25]
    m, N = 575, comb(23, 3)*comb(25, 3)
    banks = [N//x['v']*x['R'] for x in profiles]
    W = 2*N+sum(banks)
    L = sum(N//x['v']*x['loss'] for x in profiles)
    parts = {'data': Counter({1:18*N, 21:2*N, 17:2*N, 481:2*N}), 'paid_endpoint': Counter({1:N})}
    for x, bank in zip(profiles, banks):
        h, rep = x['h'], N//x['v']
        assert x['v'] == comb(h, 3) and x['loss'] == h*(h-1)
        assert x.get('different_modular_profiles', x.get('crt_disagreements')) == 0
        assert sum(t*n for t, n in enumerate(x['blocks'])) == h*x['R']+x['loss'] == x['rank_sum']
        # prepare(word) has already charged copied centers; no second correction.
        parts[f'local_{h}'] = Counter({t:rep*n for t, n in enumerate(x['blocks']) if t and n})
        parts[f'exterior_{h}'] = Counter({h:bank, m-2*h:bank})
        parts[f'growth_{h}'] = Counter({1:2*N, h-2:2*N})
    hist = sum(parts.values(), Counter())
    rank = sum(t*n for t, n in hist.items())
    assert rank == m*W-N+L
    bit = dict(m=m, N=N, W=W, L=L, banks=banks, total_rank=rank, deficit=N-L,
        maxchild=max(hist), parts=parts, child_multiplicities=dict(sorted(hist.items())), axes=profiles)
    bm = choose(bit)
    saving = bm['saving']
    independent_lo, independent_hi = moment_bounds(hist, m, W, saving)
    assert independent_hi < 1
    phase_row = json.loads(a.phase.read_text())
    phase = reconstruct([phase_row, phase_row], True)
    phase_moment = moment(phase, Q(717, 10**7))
    assert phase_moment['strict_gap'] > 0
    baseline = exact(json.loads(a.baseline.read_text()))
    bridge = baseline['finite_bridge']
    assert all(phase[k] == bridge['complex'][k] for k in ['m', 'W'])
    assert phase['total_rank'] == bridge['complex']['s']
    bridge['bit']['W'] = W
    bridge['bit']['wire_bits'] = W.bit_length()
    spec = importlib.util.spec_from_file_location('pinned_joint_balanced_assembly', a.assembly)
    assembly_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembly_module)
    backoff = Q(1, 10**12)
    q = saving*(1-2*backoff)
    upper_k = (1-backoff)*q/(1+q)
    scaled = upper_k*10**14
    kappa = Q(scaled.numerator//scaled.denominator, 10**14)
    assert kappa < upper_k
    assembled = assembly_module.assembly(bridge, saving, kappa, a_complex=Q(717, 10**7))
    assert len(assembled['constraints']) == 47 and len(assembled['margins']) == 7
    assert all(x > 0 for x in assembled['constraints'].values())
    assert all(x > 0 for x in assembled['margins'].values())
    floor = (1-independent_hi)*10**40
    gap = Q(floor.numerator//floor.denominator, 10**40)
    assert gap > 0
    paths = [a.axes, a.phase, a.baseline, a.assembly, a.geometry]
    result = dict(status='EXACT CANDIDATE; source/word/frame/data/finite-charge/proof acceptance recorded separately',
        kappa=kappa, bit=bit, phase=phase, bit_moment=bm, phase_moment=phase_moment,
        independent_bit_gap_lower_bound=gap, finite_bridge=bridge, assembly=assembled,
        eventual=assembly_module.cutoffs(bridge, assembled),
        geometry_receipt=json.loads(a.geometry.read_text()),
        input_sha256={str(x):sha256(x.read_bytes()).hexdigest() for x in paths},
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(js(result), indent=2)+'\n')
    print(json.dumps(dict(kappa=str(kappa), bit_saving=str(saving), W=W, rank=rank,
        exceeds_PR61=kappa>Q(25508460085039,500000000000000000), constraints=47)))


if __name__ == '__main__':
    main()
