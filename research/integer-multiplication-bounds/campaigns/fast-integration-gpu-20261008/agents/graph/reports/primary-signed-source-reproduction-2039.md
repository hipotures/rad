# Reproduce the signed joint-word source certificate

The immutable configuration is [joint-signed-primary-reproduction-2039.json](../fixtures/joint-signed-primary-reproduction-2039.json). It reconstructs the actual signed-frame word directly from the pinned public PR #62 source, including its inherited PR #57 compiler, without requiring a previous discovery transition binary. Source-only certificates do not by themselves certify an exponent.

Set `CAMPAIGN` to the campaign directory, `PUBLIC_SOURCE` to an immutable checkout of public commit `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`, and `REPRODUCTION_ROOT` to a fresh external directory. The following commands reconstruct both dimensions and assert the literal word, roles and actual transition digest. No previous discovery payload is read.

```bash
python3 - "$CAMPAIGN" "$PUBLIC_SOURCE" "$REPRODUCTION_ROOT" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
campaign, source, run = map(Path, sys.argv[1:])
assert not run.exists()
run.mkdir(parents=True)
config = json.loads((campaign / 'agents/graph/fixtures/joint-signed-primary-reproduction-2039.json').read_text())
constructor = campaign / config['constructor']
for axis in config['axes']:
    h = axis['h']
    receipt = run / f'h{h}-source.json'
    argv = [sys.executable, str(constructor), '--source', str(source),
            '--work', str(run / f'h{h}-work'), '--output', str(receipt)]
    for name in ['h', 'budget', 'mode', 'value', 'expected_parent_sha256', 'expected_word_sha256']:
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

When a separately produced transition binary is available, append `--profile-transitions PATH` to the axis command. Exact equality is then mandatory and the receipt records `profile_bytes_independently_compared=true`. The existing accepted intermediate signed receipts used this stricter gate. Their exact constructor version is preserved as `source_only_selective_signed_joint_v1.py`; the current constructor adds only optional comparison and explicit scope reporting.

The clean h23 reproduction was exercised on 2026-10-08 at 20:32 UTC: 27,719 roles, all 31,261 dirty basis vectors in both orientations, word digest `b8e3e030e49585145aee0b8fbb50ef99f9dda27af091324717ac0ca0fab55e19`, and actual transition digest `4dd20f628b863c6b273eed914da5fffb51a1838f003235d04ff78266fb26637e`. See [the fresh receipt](../results/joint-signed-clean-bootstrap-2021-h23.json). The h25 accepted receipt already reconstructs its complete 40,953 dirty basis with exact supplied transition equality; the optional omission is a separately tested h23 regeneration path.

Attribution: Avi Eisenberg's PR #62 provides the interval scalar graph and core-aware assembly; eumemic's PR #57 provides joint invertible binary synthesis and paid reclamation; Alejandro Zarzuelo Urdiales's PR #61 provides the parameter-only public predecessor. Preserve all directly inherited source-partition, cloning, geometry, analytic, routing and fixed-tape credits and AI-assistance disclosures from the campaign publication.
