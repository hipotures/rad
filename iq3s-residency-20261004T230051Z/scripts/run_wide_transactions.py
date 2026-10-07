"""Evaluate only the development-frozen horizon, never combine two targets at one origin."""
import subprocess, time
from lab import ROOT, load, save
base = ROOT/'experiments/E020-wide-gate-lookahead/v1'
out = base/'transactions'
assert not out.exists(); out.mkdir()
selection = load(base/'selection.json'); assert selection['state'] == 'FROZEN_DEVELOPMENT_ONLY'
horizon = selection['horizon']
save(out/'protocol.json', {
    'horizon': horizon, 'selection': str(base/'selection.json'),
    'policy': ['rank-first', 'causal EMA minimum2 gain1.5'],
    'rate_GB_s': [1.8, 12.6], 'admissions': 'At most one per origin/window; distinct physical slots',
    'victims': 'Completed earlier layers on the same GPU; exact byte-size fit',
    'queue': 'Full promotion, baseline traffic and restoration in one serialized transfer queue',
    'labels': 'True future routed IDs used only for evaluation, never selection',
    'limits': 'Fixed observed trajectory/host deadlines; temporary restore scheme, no live TG prediction.'})
commands = []
py = str(ROOT/'src/control/.venv/bin/python')
for name in ['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math','32k','128k']:
    a = load(base/'analysis'/f'{name}.json'); assert a['state'] == 'PASS'
    a['records'] = [r for r in a['records'] if r['horizon'] == horizon]
    assert a['records']
    assert len({(r['window'], r['current_layer'], r['row']) for r in a['records']}) == len(a['records'])
    a['frozen_filter'] = {'horizon': horizon, 'source': str(base/'analysis'/f'{name}.json')}
    saved = out/'inputs'/f'{name}.json'; save(saved, a)
    cmd = [py, 'scripts/router_transactions.py', str(saved), '--output', str(out/'results'/f'{name}.json')]
    started = time.time()
    with (out/f'{name}.log').open('w') as f:
        r = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=150)
    commands.append({'command': cmd, 'returncode': r.returncode, 'elapsed_s': time.time()-started})
    save(out/'commands.json', commands); print(name, r.returncode, flush=True)
    if r.returncode: raise SystemExit(r.returncode)
