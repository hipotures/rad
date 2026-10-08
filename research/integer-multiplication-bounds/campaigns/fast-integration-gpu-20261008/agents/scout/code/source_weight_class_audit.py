#!/usr/bin/env python3
"""Recover exact recorded catalogues and classify source-weight conjugates."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def initial_catalogue(device, base):
    lambdas = sorted({F(n, d) for d in range(1, 25)
                      for n in range(-8*d, 12*d+1) if n})
    if device == 0:
        pairs = [(F(2, 39), x/84) for x in lambdas] + [(F(2, 39), F(-1))]
    else:
        pairs = [(x/78, x/84) for x in lambdas]
        grid = [F(x, 4) for x in range(-16, 49) if x]
        pairs += [(x/78, y/84) for x in grid for y in grid]
        pairs += [(F(-1), F(1, 21)), (F(2, 39), F(-1)), (F(-1), F(-1))]
    return sorted({pair for pair in pairs if all(
        pair[k] not in base.forbidden(h) for k, h in enumerate((23, 25)))})


def key(pair, base):
    return tuple(base.rational_weights(h, beta)[1]
                 for h, beta in zip((23, 25), pair))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    own = Path(__file__).parent
    paths = [own/'gpu_basis_parameter_discovery.py',
             own/'gpu_basis_parameter_vectorized.py',
             own/'gpu_basis_parameter_gamma.py']
    modules = [load_module(f'basis_catalogue_{i}', p) for i, p in enumerate(paths)]
    hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    base = modules[0]
    root = args.work_root/'derived/scout'
    protocols = sorted(root.glob('gpu-basis-*/protocol.json'),
                       key=lambda p: json.loads(p.read_text())['start_utc'])
    seen_classes = set()
    seen_pairs = set()
    records = []
    candidates = []
    for path in protocols:
        protocol = json.loads(path.read_text())
        version = hashes.index(protocol['source_sha256'])
        raw = initial_catalogue(protocol['device'], base) if version == 0 else modules[version].candidates(protocol['device'])
        primes = protocol.get('primes', [protocol.get('prime')])
        pairs = []
        for pair in raw:
            weights = [w for h, beta in zip((23, 25), pair)
                       for w in base.rational_weights(h, beta)]
            if all(w.numerator % p and w.denominator % p for p in primes for w in weights):
                pairs.append(pair)
        assert len(pairs) == protocol['parameter_pairs'], (path, len(pairs))
        classes = [key(pair, base) for pair in pairs]
        unique = set(classes)
        local_index = {value: i for i, value in enumerate(sorted(unique))}
        lookup = {'protocol_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                  'source_sha256': protocol['source_sha256'],
                  'canonical_beta_pairs': len(pairs),
                  'source_weight_classes': len(unique),
                  'pair_index_to_weight_class': [local_index[x] for x in classes],
                  'scope': 'Same exact source weights for both actual fixture triples; local projectors can transpose.'}
        lookup_path = path.parent/'source-weight-class-index.json'
        encoded = (json.dumps(lookup, separators=(',', ':'))+'\n').encode()
        if lookup_path.exists():
            assert lookup_path.read_bytes() == encoded
        else:
            lookup_path.write_bytes(encoded)
        records.append({'run_id': path.parent.name,
                        'protocol_path': str(path),
                        'canonical_beta_pairs': len(pairs),
                        'source_weight_classes': len(unique),
                        'new_beta_pairs_vs_previous_catalogues': len(set(pairs)-seen_pairs),
                        'new_source_weight_classes_vs_previous_catalogues': len(unique-seen_classes),
                        'lookup_path': str(lookup_path),
                        'lookup_sha256': hashlib.sha256(encoded).hexdigest(),
                        'lookup_bytes': len(encoded)})
        seen_pairs.update(pairs)
        seen_classes.update(unique)
        for candidate_path in sorted(path.parent.glob('candidate-*.json')):
            value = json.loads(candidate_path.read_text())
            pair = tuple(F(value[f'beta{h}']['numerator'], value[f'beta{h}']['denominator'])
                         for h in (23, 25))
            weight_class = key(pair, base)
            candidates.append({'path': str(candidate_path),
                               'source_weight_class': [{'numerator': z.numerator,
                                                        'denominator': z.denominator} for z in weight_class],
                               'source_id': value['source_id'],
                               'sample_rational_check': value.get('sample_rational_check'),
                               'entropy': value['entropy']})
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Exact source catalogue recovery and rational conjugacy deduplication; no matrix/profile replay.',
              'method': 'Recover sorted beta-pair list from pinned discovery source; apply exact original modular-availability filters; require recorded catalogue length; classify by exact outside source weights.',
              'source_files': [{'path': str(p), 'sha256': h} for p, h in zip(paths, hashes)],
              'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'unique_beta_pairs_across_catalogues': len(seen_pairs),
              'unique_source_weight_classes_across_catalogues': len(seen_classes),
              'catalogues': records,
              'sample_candidates': candidates}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('source_files', 'sample_candidates')}))


if __name__ == '__main__':
    main()
