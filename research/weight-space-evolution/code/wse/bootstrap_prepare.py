"""Operator-only Phase D preparation. No provider calls, launches or held-out scoring.

Run from topic: PYTHONPATH=code work/envs/wse/bin/python -m wse.bootstrap_prepare
Missing salt or altered frozen inputs fail closed; this never invokes salt generation.
"""
import hashlib
import json
import os
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def verify_rows(rows, directory):
    """Check identities and actual payload hashes without exporting private rows."""
    seen = set()
    for row in rows:
        iid = row['id']
        if Path(iid).name != iid or iid in seen:
            raise ValueError('invalid or duplicate instance identity')
        seen.add(iid)
        for ext in ('json', 'npz'):
            if digest(directory / f'{iid}.{ext}') != row[f'{ext}_sha256']:
                raise ValueError('benchmark payload hash mismatch')
    return len(seen)


def verify(topic=TOPIC):
    cfg = topic / 'configs/phaseD_bootstrap'
    for name, expected in json.loads((cfg / 'frozen-lock.json').read_text())['files'].items():
        if digest(topic / name) != expected:
            raise ValueError(f'frozen file changed: {name}')
    frozen = json.loads((topic / 'configs/phaseD_v2/protocol_v2_frozen.json').read_text())
    bench = topic / 'work/benchmarks/phaseD-v2'
    secret = bench / 'secret_salt.txt'
    # Do not call pd2_bench.salt(): it silently creates a new salt when missing.
    if not secret.is_file() or secret.is_symlink():
        raise ValueError('original salt missing or symlinked; do not regenerate')
    if hashlib.sha256(secret.read_text().strip().encode()).hexdigest() != frozen['salt_sha256']:
        raise ValueError('salt commitment mismatch')
    splits = {}
    for split, identity in frozen['manifests'].items():
        public = json.loads((topic / f'configs/phaseD_v2/manifests/{split}.json').read_text())
        private = split in ('test', 'transfer')
        if private:
            path = bench / f'manifest-{split}.json'
            if digest(path) != identity['manifest_sha256']:
                raise ValueError('private manifest mismatch')
            rows = json.loads(path.read_text())
        else:
            rows = public['instances']
            canonical = json.dumps(rows, sort_keys=True).encode()
            if hashlib.sha256(canonical).hexdigest() != identity['manifest_sha256']:
                raise ValueError('public manifest mismatch')
        if len(rows) != identity['n']:
            raise ValueError('instance count mismatch')
        splits[split] = {'instances_verified': verify_rows(rows, bench / split), 'commitment_matches': True}
    return {'frozen_lock_matches': True, 'salt_commitment_matches': True, 'splits': splits}


def protect_private(topic=TOPIC):
    bench = topic / 'work/benchmarks/phaseD-v2'
    # Owner-only ACL baseline; actual parent isolation is a namespace with no host mounts.
    for split in ('test', 'transfer', 'select'):
        d = bench / split
        d.chmod(0o700)
        for p in d.iterdir():
            if p.is_symlink() or not p.is_file():
                raise ValueError('unexpected private payload type')
            p.chmod(0o400)
    (bench / 'secret_salt.txt').chmod(0o400)
    for split in ('test', 'transfer'):
        (bench / f'manifest-{split}.json').chmod(0o400)


def prepare_views(topic=TOPIC):
    """Export only rendered dev prompts/constraints, never answers, full instances or baselines."""
    cfg = topic / 'configs/phaseD_bootstrap'
    sessions = json.loads((cfg / 'sessions.json').read_text())['sessions']
    bench = topic / 'work/benchmarks/phaseD-v2'
    public = json.loads((topic / 'configs/phaseD_v2/manifests/dev.json').read_text())
    prompts = []
    for row in public['instances']:
        rec = json.loads((bench / 'dev' / (row['id'] + '.json')).read_text())
        tiers = {}
        for tier, value in rec['tiers'].items():
            if tier == 'T0':
                tiers[tier] = [{'prompt': rot['prompt']} for rot in value]
            else:
                tiers[tier] = {k: value[k] for k in ('prompt', 'regex', 'followup') if k in value}
        prompts.append({'id': row['id'], 'tiers': tiers})
    for session in sessions:
        root = topic / session['scratch']
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        view = root / 'view'
        view.mkdir(exist_ok=True, mode=0o700)
        # Existing views must remain identical; do not overwrite session work.
        for name, content in {'dev_prompts.json': json.dumps(prompts, indent=1),
                              'brief.md': (topic / session['brief']).read_text()}.items():
            p = view / name
            if p.exists():
                if p.read_text() != content:
                    raise ValueError('existing session view differs')
            else:
                p.write_text(content)
                p.chmod(0o400)
    return {'sessions_prepared': len(sessions), 'dev_instances_per_view': len(prompts)}


def main():
    for key in ('WSE_WORK_ROOT', 'WSE_BENCH_DIR'):
        if os.environ.get(key):
            raise ValueError('unset work/benchmark overrides for campaign preparation')
    result = verify()
    protect_private()
    result.update(prepare_views())
    from .registry import verify as verify_gold
    result['gold_verified'] = verify_gold('qwen3.5-0.8B@2fc0636')
    if not result['gold_verified']:
        raise ValueError('Gold integrity failed')
    result['paid_sessions_launched'] = 0
    result['salt_backup_status'] = 'private persistent backup not identified; recovery gap disclosed'
    out = TOPIC / 'runs/20261103T-phaseD-bootstrap-execution/results/preflight.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
