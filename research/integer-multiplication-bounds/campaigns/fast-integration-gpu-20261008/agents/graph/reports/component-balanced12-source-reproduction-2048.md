# Reproduce componentwise balanced signed frames

The fresh configuration is [joint-component-balanced12-reproduction-2048.json](../fixtures/joint-component-balanced12-reproduction-2048.json). The constructor independently rebuilds the scalar graph and literal joint word from pinned public PR #62, then adds only the selected balanced signed components and their required forward closure. No prior word, transition binary or discovered profile is required as an input.

Set `CAMPAIGN` to the campaign directory, `PUBLIC_SOURCE` to an immutable public checkout at `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`, and `REPRODUCTION_ROOT` to a fresh external directory. Then run:

```bash
python3 - "$CAMPAIGN" "$PUBLIC_SOURCE" "$REPRODUCTION_ROOT" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
campaign, source, run = map(Path, sys.argv[1:])
assert not run.exists()
run.mkdir(parents=True)
config = json.loads((campaign / 'agents/graph/fixtures/joint-component-balanced12-reproduction-2048.json').read_text())
for axis in config['axes']:
    h = axis['h']
    receipt = run / f'h{h}-source.json'
    argv = [sys.executable, str(campaign / config['constructor']),
            '--source', str(source), '--work', str(run / f'h{h}-work'),
            '--output', str(receipt)]
    for name in ['h', 'budget', 'mode', 'threshold', 'scope', 'expected_parent_sha256', 'expected_word_sha256']:
        argv += ['--' + name.replace('_', '-'), str(axis[name])]
    argv += ['--order'] + list(map(str, axis['order']))
    subprocess.run(argv, check=True)
    result = json.loads(receipt.read_text())
    assert result['R'] == axis['expected_roles']
    assert result['word_sha256'] == axis['expected_word_sha256']
    assert result['profile_transition_sha256'] == axis['expected_transition_sha256']
    assert result['profile_bytes_independently_compared'] is False
PY
```

The recovered `signed-transitions.bin` files can then be profiled in their selected rational bases by the campaign's exact native signed-frame verifier. That second step certifies actual ordered ranks, bounded-minor CRT and contiguous child widths; its outputs must be bound to the same word and transition hashes before assembling an exponent. Supplying a separately generated binary with `--profile-transitions PATH` enforces exact byte equality instead of omitting that comparison.

Both selected axes were independently recovered from pinned scalar source with exact discovery-byte equality: [h23 receipt](../results/joint-component-balanced12-Q-source-only-23.json), [h25 receipt](../results/joint-component-balanced12-Q-source-only-25.json). The constructor already supported clean omission of this optional comparison in the original version; it remains frozen at SHA256 `ca0ffffd8b34f71915de0dec00dfd9ba18866358294c28897ee949b7377c7db7`, also preserved in `source_only_componentwise_signed_joint_v1.py`.

Finite dirty receipts check F2 role basis vectors. Arbitrary address-array restoration follows from the [common-gauge transfer](common-frame-dirty-address-transfer-2048.md), conditional on the retained all-size realization and charged endpoint interpretation. Preserve the complete contributor and AI-assistance attribution recorded in the manifest and main construction certificate.
