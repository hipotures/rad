#!/usr/bin/env python3
"""Bind pinned PR54 retained DATA proof to four I+J/conjugate basis choices.

Universal coordinate identities replace a repeated million-pair computation.
Only retained bounded geometry and ten exact bad-prime witnesses are checked.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def record(path):
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def serial(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr54-snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.pr54_snapshot
    assert root.name == 'pr54-84eb0b067741dc2690da837743fda06d133da865'
    manifest_path = root.parent / 'snapshot-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    source = next(item for item in manifest['sources'] if item['pr'] == 54)
    assert source['pinned_commit'] == source['current_pr_head'] == '84eb0b067741dc2690da837743fda06d133da865'
    allowed_hashes = {item['path']: item['sha256'] for item in source['files']}
    consumed = ['LICENSE', 'NOTICE', 'research/skip-clones/PROOF.md',
                'research/skip-clones/witness.py', 'research/copied-fixed/verify.py',
                'research/copied-fixed/data_recovery.py', 'research/copied-fixed/data_corners.cpp',
                'research/copied-fixed/data-corners.json', 'research/copied-fixed/reversed/geometry.py']
    identities = []
    for h in (23, 25):
        beta, star = F(-1), F(10, 9 * (h + 1))
        axis = []
        for value in (beta, star):
            gamma = (9 * value - 1) / (3 * (1 - h * value))
            p = (1 - 3 * value, -3 * value)
            dual = ((1 + gamma) / 2, gamma / 2)
            products = tuple(a * b for a, b in zip(p, dual))
            assert all(p) and all(dual) and 3 * products[0] + (h - 3) * products[1] == 1
            k = F(h - 9, 4)
            c = (2 - 3 * value * (h - 3)) / (h - 9)
            v = F(h - 9) * (1 - 3 * value) / (12 * (1 - h * value))
            center_p, center_dual = (1 + c, c), (v - k, v)
            assert all(center_p) and all(center_dual)
            assert center_p[0] * center_dual[0] + (h - 1) * center_p[1] * center_dual[1] == 1
            assert 1 - h * value
            axis.append({'beta': serial(value), 'gamma': serial(gamma),
                         'source_primal_inside_outside': [str(x) for x in p],
                         'source_dual_inside_outside': [str(x) for x in dual],
                         'source_products_inside_outside': [str(x) for x in products],
                         'center_primal_center_outside': [str(x) for x in center_p],
                         'center_dual_center_outside': [str(x) for x in center_dual]})
        assert axis[0]['source_products_inside_outside'] == axis[1]['source_products_inside_outside']
        inverses = [1 / F(x) for x in axis[0]['source_products_inside_outside']]
        assert inverses == [F(3 * (h + 1), 2 * (3 * (h + 1) - 10)), -F(h + 1, 5)]
        for a, b in zip(axis[1]['source_primal_inside_outside'], axis[0]['source_dual_inside_outside']):
            assert F(a) == 2 * F(b)
        for a, b in zip(axis[1]['center_primal_center_outside'], axis[0]['center_dual_center_outside']):
            assert F(a) == -F(b) / F(h - 9, 4)
        identities.append({'h': h, 'bases': axis, 'PR54_inverse_products': [str(x) for x in inverses],
                           'conjugate_source_and_center_products_identical': True})
    spec = importlib.util.spec_from_file_location('pr54_fixed_data_bounded', root / 'research/copied-fixed/verify.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    geometry = base.geometry()
    N = 4073300
    assert geometry['modular']['primary_good'] == N - 10
    assert geometry['modular']['primary_fallback'] == 10
    assert geometry['modular']['good'] == N and geometry['modular']['fallback'] == 0
    assert geometry['accepted_profile'] == {'singletons': 9, 'blocks': [21, 17, 481]}
    # Derive actual endpoint coordinates from the campaign's pinned physical map.
    own = Path(__file__).resolve().parent
    campaign = own.parents[2]
    helper_path = campaign / 'code/gpu_changed_basis_repair.py'
    spec = importlib.util.spec_from_file_location('pr54_physical_map', helper_path)
    physical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(physical)
    pi = physical.baseline()
    rows = [(int(pi[i % 25, i // 25]), i % 25) for i in range(47)]
    columns = [(int(pi[(528 + i) % 25, (528 + i) // 25]), (528 + i) % 25) for i in range(47)]
    assert rows == [tuple(x) for x in geometry['inherited']['rows']]
    assert columns == [tuple(x) for x in geometry['inherited']['columns']]
    for relative in consumed:
        assert record(root / relative)['sha256'] == allowed_hashes[relative]
    result = {'utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS UNIVERSAL PR54 DATA COMPATIBILITY FOR FOUR CONJUGATE CHOICES',
              'pinned_PR54': '84eb0b067741dc2690da837743fda06d133da865',
              'snapshot_manifest': record(manifest_path),
              'audit_source': record(Path(__file__)), 'physical_map_source': record(helper_path),
              'consumed_sources': [record(root / relative) for relative in consumed],
              'basis_identities': identities,
              'basis_combinations': [[str(x), str(y)] for x in (F(-1), F(5, 108))
                                     for y in (F(-1), F(5, 117))],
              'actual_permutation': pi.tolist(), 'rows': rows, 'columns': columns,
              'normalized_matrix': 'delta(r,c)/z23[r]+delta(b,d)/z25[b]-1; invertible source row/column diagonal scaling only.',
              'universal_identity': 'Conjugate source coordinate products agree inside/outside every triple; therefore all four complete normalized DATA families are entrywise identical under the actual same physical order.',
              'source_pairs': N, 'one_data_front_histogram': {'1': 9 * N, '17': N, '21': N, '481': N},
              'primary_good': N - 10, 'primary_failures_exactly_recovered': 10,
              'bounded_recovered_controls': geometry['modular']['exact_recovery'],
              'bounded_scope': 'Executed pinned geometry() exact rank-cut controls, retained complete primary coverage/schema, ten exact rational failed-prime witnesses, physical endpoint identity. No full million-pair sweep or binary pivot arrays regenerated.',
              'limitations': ['Retained full primary sweep remains attributed upstream evidence, not a new scout sweep.',
                              'Conjugate signed/source/center projectors transpose; actual local NE profiles on the new DAG need separate validation.',
                              'No new scalar/compiler/bridge/physical assembly or headline kappa is certified here.'],
              'attribution': 'PR54 Chafik Boukhalfa, PR53 Avi Eisenberg, Rohan Arun and retained predecessor notices; copied centers icekylinx, fixed bases Dominik Scholz, controlled reversed geometry James Chang, exact recovery Chafik Boukhalfa.'}
    assert not args.output.exists()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'source_pairs': N, 'exact_controls': 10, 'output': str(args.output)}))


if __name__ == '__main__':
    main()
