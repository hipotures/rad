#!/usr/bin/env python3
"""Reconstruct a distinct paid lifetime/fused balanced transfer certificate.

All arithmetic is standard-library rational interval arithmetic. Source and
physical-word bytes are bound here; their finite identities, reflected
geometry and eligible-prime implementations remain independent prerequisites.
Apache-2.0; prepared with OpenAI GPT-6.1 Sol assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import gzip
import json
import sys

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from check_balanced_composition import (BAD, OLD, balanced, cutoffs,
    floor_strict, full_bridge, js, moment, profile, require)


def pinned(root, pin):
    raw = (root / pin['path']).read_bytes()
    require(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
            'Source/input corruption: ' + pin['path'])
    if pin.get('encoding') == 'gzip':
        raw = gzip.decompress(raw)
        require(sha256(raw).hexdigest() == pin['decoded_sha256'],
                'Decoded fixture corruption: ' + pin['path'])
    return raw


def reconstruct(row, binary=False):
    hist = Counter()
    for field in ('local_histogram', 'source_data_histogram', 'target_data_histogram'):
        for rank, count in row[field].items():
            hist[int(rank)] += 3 * int(count)
    for rank, count in row['physical_gauge_histogram'].items():
        hist[3 * int(rank)] += int(count)
    hist[2] += 2 * row['v']
    hist.pop(0, None)
    require(dict(hist) == {int(r): n for r, n in row['child_histogram'].items() if n},
            'Complete component histogram does not reconstruct')
    result = profile(row['m'], row['W_per_vertex'], hist)
    require(result['m'] == 3 * row['h'] and
            result['W'] == 2 * row['v'] + row['physical_R'], 'Physical role stock')
    require(row['physical_R'] == row['R'] - row['pairs'], 'Alias role stock')
    require(result['mass'] == row['rank_per_vertex'] and
            result['m'] * result['W'] - result['mass'] ==
            row['deficit_per_vertex'] == 2 * row['v'] - 3 * row['loss'], 'Telescoping rank')
    if binary:
        require(Q(2 * result['m']**3, 2**80) < BAD, 'Bad-class prime envelope')
        require(result['mass'] + BAD * 32 * result['m']**2 * result['edges'] <
                result['m'] * result['W'], 'Complete fallback rank fails')
    return result


def verify(root, config):
    require(not sys.flags.optimize, 'Optimized execution is unsupported')
    data = {name: json.loads(pinned(root, pin)) for name, pin in config['inputs'].items()}
    for pin in config['sources'].values():
        pinned(root, pin)
    # Every named frozen physical input and every explicitly declared recovery
    # dependency must be present. This prevents the earlier 74-source-only
    # arithmetic export from being mistaken for a closed signed-word export.
    for record in config['closure_requirements']:
        pin = config[record['section']][record['key']]
        require(pin['sha256'] == record['sha256'], 'Declared recovery closure mismatch')
    for name, item in data['complex_protocol']['input_pins'].items():
        require(any(pin['path'].endswith('/' + name) and pin['sha256'] == item['sha256']
                    for pin in config['inputs'].values()), 'Frozen physical protocol input omitted: ' + name)
    for origin, block in data['bit_source_manifest'].items():
        if not isinstance(block, dict) or 'files' not in block:
            continue
        for relative, item in block['files'].items():
            require(any(pin['path'].endswith('/' + relative) and pin['sha256'] == item['sha256']
                        for pin in config['sources'].values()), 'Binary imported source omitted: ' + relative)
    for relative, digest in data['complex_base_protocol']['discovery_protocol']['dependency_pins'].items():
        require(any(pin['path'] == relative and pin['sha256'] == digest
                    for pin in config['sources'].values()), 'Fusion driver dependency omitted: ' + relative)
    for relative, digest in data['complex_protocol']['search_sha256'].items():
        require(any(pin['path'].endswith('/' + relative) and pin['sha256'] == digest
                    for pin in config['sources'].values()), 'Physical frame dependency omitted: ' + relative)
    for name, digest in data['bit']['source_sha256'].items():
        require(any(pin['path'].endswith('/' + name) and pin['sha256'] == digest
                    for pin in config['inputs'].values()), 'Binary source export omitted: ' + name)
    require(data['bit_frames']['source_sha256'] == data['bit']['source_sha256'],
            'Binary plan and paid profile are from different compiled words')
    physical, scalar, bit = (data[key] for key in ('physical', 'scalar', 'bit'))
    bp, cp = reconstruct(bit, True), reconstruct(physical)
    require((bp['m'], bp['W'], bp['mass'], bp['maxchild']) ==
            tuple(config['expected_bit_inventory']), 'Frozen binary inventory changed')
    require((cp['m'], cp['W'], cp['mass'], cp['maxchild']) ==
            tuple(config['expected_complex_inventory']), 'Frozen complex inventory changed')
    require((bit['R'], bit['physical_R'], bit['pairs'], bit['v'], bit['loss']) ==
            tuple(config['expected_bit_roles']), 'Frozen binary role inventory changed')
    graph, word, logical = (data[key] for key in ('complex_graph', 'complex_word', 'complex_logical_frames'))
    require((graph['h'], graph['v'], len(graph['args']) - graph['v'], len(graph['roots']),
             len(logical['matching_arcs']), len(word['ops']), len(word['opcoeff'])) ==
            (scalar['h'], scalar['v'], scalar['c'], scalar['q'], scalar['matched'],
             scalar['total_M_operations'], scalar['total_M_operations']), 'Actual signed scalar inventory')
    require(len(word['selected']) == len(data['complex_pairs']) == physical['pairs'] and
            len(data['complex_frames']) == physical['changed_operation_frames'], 'Actual complex selected plan')
    bit_graph, bit_word = data['bit_graph'], data['bit_word']
    require((len(bit_graph['args']) - bit['v'], len(bit_graph['roots']), len(bit_word['arcs']),
             len(bit_word['ops'])) == tuple(config['expected_bit_scalar_inventory']), 'Actual binary scalar inventory')
    require(len(data['bit_frames']['pairs']) == bit['pairs'] and
            len(data['bit_frames']['frames']) == bit['changed_operation_frames'], 'Actual binary selected plan')
    coarse, atom, b, beta, eta, weakening, kappa = (Q(config[key]) for key in
        ('coarse', 'atom', 'complex_saving', 'phase_stop', 'backoff', 'strict_weakening', 'kappa'))
    bm, cm = moment(bp, coarse, BAD), moment(cp, b)
    bn = moment(bp, coarse + Q(config['bit_next_grid_step']), BAD)
    cn = moment(cp, b + Q(config['complex_next_grid_step']))
    require(bm['upper'] < 1 < bn['lower'] and cm['upper'] < 1 < cn['lower'],
            'Complete paid supplier moment/grid inequality failed')
    rank = bp['mass'] + BAD * 32 * bp['m']**2 * bp['edges']
    bill = full_bridge(physical, scalar, coarse, atom)
    result = balanced(bill, b, beta, eta, weakening, kappa=kappa)
    require(result['a'] == min(bill['ordinary_saving'], (1-beta)*b-weakening),
            'Paid common exponent does not use both actual suppliers')
    require(kappa == floor_strict(result['g'], 10**12), 'Frozen final grid is not conservative and complete')
    public = Q(config['comparison_public_kappa'])
    require(Q(data['frontier_claim']['kappa']) == public, 'Pinned frontier certificate claim changed')
    target = Q(config['required_publication_ratio']) * public
    require(kappa >= target, 'Candidate fails the source-confirmed one-percent gate')
    controls = []
    def reject(name, call):
        try:
            call()
        except (KeyError, ValueError, ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError('Negative control accepted: ' + name)
    reject('previous unpaid atom grid', lambda: full_bridge(physical, scalar, coarse, atom-Q(1,10**12)))
    reject('next final twelve-digit grid', lambda: balanced(bill,b,beta,eta,weakening,kappa=kappa+Q(1,10**12)))
    reject('old separate prefix', lambda: balanced(bill,b,beta,eta,weakening,kappa=kappa,old_prefix=True))
    reject('old nonlinear guard', lambda: balanced(bill,b,beta,eta,weakening,kappa=kappa,old_guard=True))
    reject('old separate movement bills', lambda: balanced(bill,b,beta,eta,weakening,kappa=kappa,old_exposures=True))
    reject('zero complex stop', lambda: balanced(bill,b,Q(0),eta,weakening,kappa=kappa))
    reject('zero geometry reserve', lambda: balanced(bill,b,beta,Q(0),weakening,kappa=kappa))
    reject('virtual scalar roles collapsed', lambda: full_bridge(physical,dict(scalar,R=physical['physical_R']),coarse,atom))
    reject('persistent width shortened', lambda: full_bridge(dict(physical,W_per_vertex=physical['W_per_vertex']-1),scalar,coarse,atom))
    reject('literal scalar bill omitted', lambda: balanced(dict(bill,strict_literal_gap=0),b,beta,eta,weakening,kappa=kappa))
    reject('external rows omitted', lambda: balanced(dict(bill,row_gap=Q(-1)),b,beta,eta,weakening,kappa=kappa))
    damaged = copy.deepcopy(bit); damaged['child_histogram']['1'] += 1
    reject('unregenerated binary histogram', lambda: reconstruct(damaged,True))
    damaged = copy.deepcopy(physical); damaged['child_histogram']['1'] += 1
    reject('unregenerated complex histogram', lambda: reconstruct(damaged))
    reject('source hash corruption', lambda: pinned(root,dict(config['inputs']['bit'],sha256='0'*64)))
    return js(dict(status='PASS conditional source-bound lifetime/fused paid balanced arithmetic',
        candidate_id=config['candidate_id'], source_pins=config, kappa=kappa,
        coarse_bit_saving=coarse, atom=atom, ordinary_bit_saving=bill['ordinary_saving'], complex_saving=b,
        bit_profile=bp, complex_profile=cp, bit_moment=bm, bit_next_grid=bn,
        complex_moment=cm, complex_next_grid=cn, contaminated_bit_rank=rank,
        bridge=bill, assembly=result, cutoffs=cutoffs(bill,result), rejected_controls=controls,
        public_comparison=dict(pinned_head=config['comparison_public_head'],public_kappa=public,
            ratio=kappa/public, exact_improvement=kappa-public, required_ratio=Q(config['required_publication_ratio']),
            publication_floor=target, surplus=kappa-target,
            scope='Pinned scientific comparison; live refresh is a separate coordinator gate.'),
        finite_prerequisites=config['finite_prerequisites'], inherited_hypotheses=config['inherited_hypotheses'],
        exclusions=['Hash binding does not prove the finite word, all projectors or reflected physical geometry.',
                    'No unconditional theorem, practical threshold or hosted-CI result is asserted.']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Output must be fresh')
    config = json.loads(args.config.read_bytes())
    result = verify(args.sprint, config)
    result['config_sha256'] = sha256(args.config.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print('PASS '+result['candidate_id']+' kappa='+result['kappa']+'; complete moments/full finite bills/47+7; '+
          str(len(result['rejected_controls']))+' rejected controls')


if __name__ == '__main__':
    main()
