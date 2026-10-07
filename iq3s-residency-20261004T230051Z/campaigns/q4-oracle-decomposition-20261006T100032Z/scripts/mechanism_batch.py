"""Post-run mechanism analysis. Never run concurrently with headline GPU requests."""
import json
import re
from pathlib import Path

from owned import C
from persistent_lifetimes import analyze as lifetimes
from recurrent_exchanges import analyze as recurrence
from residual_misses import analyze as residual
from target_readiness import analyze as targets
from victim_accounting import analyze as victims


def main():
    values = []
    pattern = r'v2-(32k|128k|256k)-(current|FF|64F|F64|6464|F256)-attempt(?:[1-3]|independent[1-3])'
    for path in sorted((C / 'raw').glob('v2-*/results.json')):
        label = path.parent.name
        if not re.fullmatch(pattern, label):
            continue
        print('MECHANISM_PROGRESS', label, flush=True)
        result = {'label': label}
        result['target_readiness'] = targets(label)
        result['victim_accounting'] = victims(label)
        result['persistent_lifetimes'] = lifetimes(label)
        result['recurrent_exchanges'] = recurrence(label)
        result['residual_misses'] = residual(label)
        values.append(result)
    (C / 'analysis/mechanism-summary.json').write_text(json.dumps(values, indent=2) + '\n')
    print('MECHANISM_COMPLETE', len(values), flush=True)


if __name__ == '__main__':
    main()
