#!/usr/bin/env python3
"""Recompute changed-native CPU expenses without promoting arithmetic to proof.

Public finite inputs: Rohan Gupta (Claude), eumemic (Codex), Chafik
Boukhalfa (Codex), and the pinned predecessor notices in ../CREDITS.md.
The 38-row CPU framework is independently authored campaign research.
"""
import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', required=True, type=Path)
    parser.add_argument('--literal-ledger', required=True, type=Path)
    parser.add_argument('--public-assembly', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert __debug__ and not args.output.exists()
    campaign = Path(__file__).resolve().parents[2]
    native = json.loads(args.native.read_text())
    literal = json.loads(args.literal_ledger.read_text())
    controller = native['controller']
    assert native['moment']['strict_gap'] and F(native['moment']['strict_gap']) > 0
    for key, other in [('W', 'W'), ('total_rank', 'rank_mass'),
                       ('deficit', 'deficit'), ('maxchild', 'maxchild'),
                       ('wrapped_scalar_xors', 'replicated_wrapped_XORs')]:
        assert controller[key] == literal[other]
    assert literal['product_row_coefficient'] == native['finite_role_product_stock'] == 852
    assert literal['owned_copy_stream_groups_upper'] == 4*(2300*23+1771*25)
    assert F(literal['row_degree_gap']) > 0
    a, b = F(native['saving']), F(717, 10000000)
    epsilon = F(999999, 1000000)
    q = epsilon*a
    kappa = F(99999, 100000)*a
    cpu_source = campaign/'code/packed_assembly.py'
    cpu = module(cpu_source, 'changed_native_cpu38')
    changed = cpu.assembly(a, b, epsilon, q, kappa, guarded_crt=True)
    old = cpu.assembly(a, b, epsilon, q, kappa, guarded_crt=False)
    assert len(changed['strict_slacks']) == 38 and changed['arithmetic_pass']
    assert not old['arithmetic_pass']
    assert set(old['failed_slacks']) == {'triangular_controlled_crt_below_target'}
    assert changed['gain_over_old_supremum'] > 0
    public = module(args.public_assembly, 'changed_native_public47_control')
    finite_bridge = native['assembly']['finite_bridge']
    try:
        public_control = public.assembly(finite_bridge, a, kappa)
    except public.InvalidAssembly as error:
        # Retain the public checker's actual rejection; never disable require().
        failures = {name: F(value) for name, value in ast.literal_eval(str(error)).items()}
        margin_failures = {}
        public_parameters = dict(native['assembly']['parameters'], kappa=kappa)
        assert len(native['assembly']['constraints']) == 47
        assert failures and all(value <= 0 for value in failures.values())
    else:
        failures = {name: value for name, value in public_control['constraints'].items()
                    if value <= 0}
        margin_failures = {name: value-kappa for name, value in public_control['margins'].items()
                           if value <= kappa}
        public_parameters = public_control['parameters']
        assert len(public_control['constraints']) == 47
    assert failures or margin_failures
    paths = [args.native, args.literal_ledger, cpu_source, args.public_assembly,
             Path(__file__)]
    result = dict(
        recorded_utc=datetime.now(timezone.utc).isoformat(),
        status='CHANGED CPU38 ARITHMETIC PASS; FULL TRANSFER REVIEW OPEN',
        conditional_transfer_accepted=False,
        inputs={str(p): dict(bytes=p.stat().st_size,
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths},
        native_saving=a, candidate_kappa=kappa,
        changed_cpu_assembly=changed,
        rejected_unbatched_crt=old,
        rejected_unchanged_public47=dict(constraints=failures, margins=margin_failures,
                                         parameters=public_parameters),
        fixed_native_expenses=dict(
            bit_roles=controller['W'],
            bit_rank_mass=controller['total_rank'],
            complete_wrapped_local_xors=controller['wrapped_scalar_xors'],
            center_port_extra_linear_stream_groups=literal['owned_copy_stream_groups_upper'],
            product_row_coefficient=literal['product_row_coefficient'],
            product_row_degree=2000, row_degree_gap=literal['row_degree_gap'],
            complete_payload=True,
            interpretation='Paid fixed finite coefficients. The independently reviewed native recurrence absorbs their linear-volume work; they do not vanish from runtime accounting.'),
        proof_requirements=[
            'Explicit mapping of all 47 inherited assembly obligations to retained or changed CPU statements.',
            'Actual changed native role/frame/dirty/copy charges and semantic guard, including both orientations.',
            'Independent guarded CRT full-bank/full-payload, joint gather, deferred FFT and restore contracts.',
            'Packed forward/inverse Gaussian error, phase/free-axis repair, precision and recovery margins.',
            'Acyclic strong induction, eligible-prime/catalogue/setup and eventual constant absorption.',
        ],
        scope='Exact updated costs and negative controls; passing 38 inequalities alone does not establish the changed all-size transfer.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(encode(result), indent=2)+'\n')
    print(json.dumps(encode(dict(status=result['status'], kappa=kappa,
                                smallest_slack=changed['smallest_slack'],
                                public47_failed_constraints=failures,
                                public47_failed_margins=margin_failures))))


if __name__ == '__main__':
    main()
