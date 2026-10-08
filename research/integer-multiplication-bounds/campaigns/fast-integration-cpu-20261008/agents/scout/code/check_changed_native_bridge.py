#!/usr/bin/env python3
"""Independent native-bridge and packed exponent checks for a changed controller.

Read an independently checked complete-controller receipt and the eligible
PR40 certificate. Reuse the unchanged complex witness; recompute all native
bit/row/semantic arithmetic. The public balanced checker is used only for an
auxiliary old-assembly witness, not to erase any changed machine cost.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, list):
        return [encode(v) for v in x]
    return x


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', required=True, type=Path)
    ap.add_argument('--controller-receipt', required=True, type=Path)
    ap.add_argument('--saving', required=True, type=F)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    assert __debug__, 'Run without Python -O'
    cert = args.source_root/'research/copied-both-reversed/certificate.json'
    source = args.source_root/'research/copied-fixed-reversed/balanced_assembly.py'
    original = json.loads(cert.read_text())
    independent = json.loads(args.controller_receipt.read_text())
    assert independent['moment']['strictly_passes']
    assert F(independent['moment']['saving']) == args.saving
    c, f = independent['controller'], original['finite_bridge']
    old_W = f['bit']['W']
    assert f['bit']['m'] == c['m'] and f['bit']['maxchild'] == c['maxchild']
    degree = 1
    while c['m']**degree <= 2*c['maxchild']**degree:
        degree += 1
    f['bit'] = dict(m=c['m'], W=c['W'], maxchild=c['maxchild'],
                    halving_degree=degree, wire_bits=c['W'].bit_length())
    phase, sem = f['complex'], f['semantic']
    E = 64*(phase['W']+phase['m']+phase['scalar_group_upper']+1)**3
    B = phase['s']+E
    literal = (2*phase['scalar_group_upper']*phase['W']**2+8*phase['s']
               +4*phase['W']+4+32*phase['m'])
    assert sem['E'] == E and sem['B'] == B and sem['C1'] == 1
    assert sem['C0'] == 32*phase['m']*B*B
    assert sem['literal_charge'] == literal
    assert sem['strict_literal_gap'] == E-literal > 0
    assert sem['induction_gap'] == 2*B*(phase['m']-phase['maxchild'])-phase['s']-E > 0
    coefficient = sum(f[name]['halving_degree']*f[name]['wire_bits']
                      for name in ('bit', 'complex'))
    row_degree = 1000*((coefficient*51)//25000+1)
    f['rows'] = dict(coefficient=coefficient, degree=row_degree,
                     degree_gap=row_degree-F(51,25)*coefficient,
                     suffix_slope=4*row_degree,
                     contract=original['finite_bridge']['rows']['contract'])
    spec = importlib.util.spec_from_file_location('eligible_balanced', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    a, b = args.saving, F(717, 10**7)
    old_kappa = a/(1+a)*F(99999999, 10**8)
    auxiliary = module.assembly(f, a, old_kappa)
    assert len(auxiliary['constraints']) == 47 and min(auxiliary['constraints'].values()) > 0
    backoff, beta, zeta = F(1, 10**6), F(1,20), F(1,1000)
    eps, q, kappa = 1-backoff, a*(1-backoff), a*(1-10*backoff)
    tau, sigma, target = 1-a, 1-b, 1-kappa
    internal = tau+(1-beta)*max(sigma-tau,F())
    leaf, lp = sigma+beta*(1-sigma), 1-q
    lam = (max(tau,sigma,internal,leaf)+lp)/2
    # Named physical cost rows, rather than deleting inherited constraints.
    costs = dict(completed_fft=1-eps*q, coordinate_routing=tau,
                 guarded_crt=tau, suffix_ring_product=1-eps,
                 packed_recursive_children=eps*(1-kappa),
                 sparse_repair_sorting=1-2*eps,
                 phase_band_lu=-eps+18*eps*zeta,
                 regular_free_axis_band_lu=-2*eps+18*eps*zeta,
                 source_elementary_phase=18*eps*zeta,
                 scalar_polynomial_windows=F(), linear_scans=F())
    strict = dict(a_positive=a, a_below_complex=b-a,
                  complex_below_one_over32=F(1,32)-b,
                  beta_positive=beta, beta_below_one=1-beta,
                  zeta_positive=zeta, zeta_below_one_eighth=F(1,8)-zeta,
                  epsilon_above_half=eps-F(1,2), epsilon_below_one=1-eps,
                  q_positive=q, q_below_bit=a-q,
                  q_below_stopped_complex=(1-beta)*b-q,
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  lambda_above_internal=lam-internal,
                  lambda_above_leaf=lam-leaf,
                  lambda_prime_above_lambda=lp-lam,
                  lambda_prime_below_one=q,
                  positive_kappa=kappa, kappa_below_one=1-kappa,
                  metadata_guard=16*eps-2,
                  crt_inverse_metadata=18*eps-4,
                  catalogue_cell_growth=2*eps-1,
                  bank_suffix_growth=1-eps,
                  inverse_phase_window_gap=F(12)-F(17,2),
                  forward_tensor_chirp_gap=F(18)-F(9),
                  tensor_prefix_depth=17*eps)
    strict.update({name+'_below_target': target-exponent for name, exponent in costs.items()})
    assert all(value > 0 for value in strict.values())
    assert eps*q-kappa == a*(8*backoff+backoff**2)
    assert lam-tau == a*backoff/2
    result = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                  status='exact_changed_native_bridge_and_packed_inequality_review',
                  source_pin='43f59ff533598762cbc43a5e14af2bbbc76fabbd',
                  native_bit_before_W=old_W, finite_bridge=f,
                  auxiliary_inherited47=dict(a=a,kappa=old_kappa,all47_positive=True,
                                             minimum_slack=min(auxiliary['constraints'].values())),
                  packed_parameters=dict(a=a,b=b,epsilon=eps,q=q,kappa=kappa,beta=beta,zeta=zeta),
                  costs=costs, independent_strict_slacks=strict,
                  gain_over_old_CRT_cap=kappa-a/(1+a),
                  inputs=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                          for p in (cert,source,args.controller_receipt)],
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Exact arithmetic; source-bound full matrices, general physical compiler, guarded CRT and all-size precision remain named proof premises')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(dict(native_bit=f['bit'],row_coefficient=coefficient,
                                 row_degree=row_degree,row_gap=f['rows']['degree_gap'],
                                 kappa=kappa,minimum_slack=min(strict.values()))),indent=2))


if __name__ == '__main__':
    main()
