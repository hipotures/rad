"""Logical future-index payload accounting; allocator RSS is not fabricated."""
import json
import numpy as np
from pathlib import Path
from tape import Tape

C = Path(__file__).resolve().parents[1]


def main():
    rows = []
    for profile in ['32k', '128k', '256k']:
        tape = Tape(C / 'tapes' / f'capture-{profile}-v3.bin')
        pairs = 0
        for _, _, ids, _ in tape.events():
            pairs += len(np.unique(ids))
        rows.append({
            'profile': profile, 'tape_bytes': len(tape.data),
            'future_index_event_count_pairs': pairs,
            'future_index_pair_payload_bytes': pairs * 8,
            'future_index_expert_vectors': 48 * 512,
            'pair_fields': 'Two int32 values: routed invocation and multiplicity',
            'scope': 'Logical pair payload only. Vector capacity slack, allocator '
                     'metadata and additional tape copies are not measured RSS.',
        })
        print('FUTURE_MEMORY_PROGRESS', profile, pairs, flush=True)
    (C / 'analysis/future-index-memory.json').write_text(
        json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    main()
