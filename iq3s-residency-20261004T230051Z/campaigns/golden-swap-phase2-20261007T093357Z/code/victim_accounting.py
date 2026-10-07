"""Comparable observed victim absence from native/oracle publication journals."""
import json
import collections
import re
from pathlib import Path

import numpy as np

from inspect_oracle import E, L, N
from tape import Tape

C = Path(__file__).resolve().parents[1]


def analyze(label):
    path = C / 'raw' / label
    cfg = json.loads((path / 'config.json').read_text())
    tape = Tape(cfg['env']['STRATA_Q4_TAPE'])
    layers = np.fromfile(path / 'raw/oracle-layers.bin', L)
    oracle = np.fromfile(path / 'raw/oracle-admissions.bin', E)
    native = np.fromfile(path / 'raw/oracle-native.bin', N)
    oracle_active = cfg['env']['STRATA_Q4_ORACLE_MODE'] != 'off'
    if oracle_active:
        assert len(native) == 0, 'Unexpected mixed admission authority'
        swaps = [(int(e['publish_ns']), 'exchange', int(e['layer']), int(e['incoming']),
                  int(e['victim']), int(e['slot'])) for e in oracle if e['publish_ns']]
    else:
        assert len(oracle) == 0
        # Native adaptation removes the victim at issue, before copy completion.
        # Its incoming expert becomes resident only at the publication marker.
        swaps = [(int(e['issue_ns']), 'evict', int(e['layer']), int(e['incoming']),
                  int(e['victim']), int(e['slot'])) for e in native]
        swaps += [(int(e['publish_ns']), 'admit', int(e['layer']), int(e['incoming']),
                   int(e['victim']), int(e['slot'])) for e in native if e['publish_ns']]
    swaps.sort()
    state = tape.initial.copy()
    log = (path / 'raw/run-engine.log').read_text()
    for layer, expert in re.findall(r'Q4_ORACLE_RESERVE device=\d+ class=\d+ bytes=\d+ slot=\d+ layer=(\d+) expert=(\d+)', log):
        state[int(layer), int(expert)] = -1
    absent = set()
    admissions = collections.Counter()
    reloads = collections.Counter()
    counts = {'CPU': 0, 'mapped': 0, 'other': 0}
    publication_index = 0
    for row in layers:
        boundary = int(row['plan_end'])
        while publication_index < len(swaps) and swaps[publication_index][0] <= boundary:
            _, action, layer, incoming, victim, slot = swaps[publication_index]
            if victim >= 0 and action in ['evict', 'exchange']:
                state[layer, victim] = -1
                absent.add((layer, victim))
            if action in ['admit', 'exchange']:
                key = (layer, incoming)
                admissions[key] += 1
                if key in absent:
                    reloads[key] += 1
                state[layer, incoming] = slot
                absent.discard((layer, incoming))
            publication_index += 1
        layer = int(row['layer'])
        n = int(row['n'])
        ids = row['ids'][:n]
        assert np.array_equal(state[layer, ids], row['slots'][:n]), (
            label, int(row['event']), 'Publication journal disagrees with actual service slots')
        for expert, slot, service in zip(ids, row['slots'][:n], row['path'][:n]):
            if int(slot) < 0 and (layer, int(expert)) in absent:
                counts['CPU' if int(service) == -1 else 'mapped' if int(service) == 1 else 'other'] += 1
    total = sum(counts.values())
    if oracle_active:
        assert total == int(oracle['victim_uses'].sum()), 'Victim journal/counter disagreement'
    result = {'state': 'PASS', 'label': label, 'authority': 'oracle' if oracle_active else 'native',
              'victim_absent_entries': total, 'paths': counts,
              'publication_count': int(np.count_nonzero(oracle['publish_ns'])) if oracle_active else int(np.count_nonzero(native['publish_ns'])),
              'eviction_boundary': 'Oracle publication; native copy issue, per unchanged runtime source',
              'chronological_victim_reloads': sum(reloads.values()),
              'victims_reloaded_repeatedly': sum(n >= 2 for n in reloads.values()),
              'repeat_admissions_beyond_first': sum(max(0, n - 1) for n in admissions.values()),
              'unique_admitted_experts': len(admissions),
              'scope': 'Observed routed entries demanded while an expert is absent following an '
                       'actual eviction in this policy journal. Initial spare donors are separate. '
                       'Readmission ends absence. This is not exclusive causal latency damage '
                       'and does not assume unchanged counterfactual placement.'}
    (C / 'analysis' / (label + '-victim-accounting.json')).write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('labels', nargs='+')
    for label in parser.parse_args().labels:
        print(json.dumps(analyze(label)), flush=True)
