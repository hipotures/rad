"""Separate analysis of the previously observed substantive archive task."""
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

from analyze import row, stat

C = Path(__file__).resolve().parents[1]


def main():
    rows = []
    for path in sorted((C / 'raw').glob('v2-32k-*-attemptindependent*/results.json')):
        label = path.parent.name
        match = re.fullmatch(r'v2-32k-(current|FF|F256)-attemptindependent([1-3])', label)
        if not match:
            continue
        value = row(label)
        value.update(arm=match[1], attempt=int(match[2]))
        cfg = json.loads(path.read_text())['runs'][0]['full_config']
        assert cfg['env']['STRATA_Q4_ORACLE_CHECK'] == '1'
        assert value['recorded_output'] == 1024
        rows.append(value)

    by = {(x['attempt'], x['arm']): x for x in rows}
    groups = defaultdict(list)
    pairs = []
    for value in rows:
        groups[value['arm']].append(value)
        current = by.get((value['attempt'], 'current'))
        full = by.get((value['attempt'], 'FF'))
        if current is None or full is None:
            continue
        saved = current['decode_s'] - full['decode_s']
        retention = ((current['decode_s'] - value['decode_s']) / saved
                     if saved > max(.1, .003 * current['decode_s']) else None)
        pairs.append({
            'attempt': value['attempt'], 'arm': value['arm'],
            'TG_ratio_vs_current': current['decode_s'] / value['decode_s'],
            'wall_ratio_vs_current': value['wall_s'] / current['wall_s'],
            'gain_retention': retention,
        })
    cells = []
    for arm, values in groups.items():
        paired = [p for p in pairs if p['arm'] == arm]
        ratios = [p['TG_ratio_vs_current'] for p in paired]
        retentions = [p['gain_retention'] for p in paired if p['gain_retention'] is not None]
        cells.append({
            'arm': arm, 'attempts': len(values),
            'valid': sum(v['state'] == 'VALID' and v['fidelity'] == 'PASS'
                         and v['ownership'] == 'PASS' for v in values),
            'TG_median': statistics.median(v['replay_equivalent_tok_s'] for v in values),
            'TG_min_median_max': stat([v['replay_equivalent_tok_s'] for v in values]),
            'wall_median': statistics.median(v['wall_s'] for v in values),
            'paired_TG_pct': (statistics.median(ratios) - 1) * 100 if ratios else None,
            'gain_retention': statistics.median(retentions) if retentions else None,
            'copy_GB': stat([v['copy_GB'] for v in values]),
            'victim_absent': stat([v['victim_absent_entries'] for v in values]),
        })
    result = {
        'description': 'Previously observed independent Python zipfile/archive task, '
                       '6991 input and 1024 recorded output tokens, total context 32768. '
                       'This is task transfer, not a new untouched holdout. Every arm '
                       'enables the same sampled copied-weight readback setting; '
                       'readbacks occur only where oracle copies are actually issued. '
                       'Their cost remains in request/decode timing. Fixed forced output '
                       'does not evaluate task quality.',
        'state': 'PASS' if rows and all(v['valid'] == 3 for v in cells) else 'INCOMPLETE',
        'rows': rows, 'cells': cells, 'pairs': pairs,
    }
    (C / 'phase-c/independent-summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'state': result['state'], 'cells': cells}, indent=2), flush=True)


if __name__ == '__main__':
    main()
