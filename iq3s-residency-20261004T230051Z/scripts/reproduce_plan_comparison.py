"""Replay the retained unsafe/fenced arithmetic diagnostic, never a speed test."""
import argparse
import time
from lab import ROOT, Session, deadline, save

ap = argparse.ArgumentParser()
ap.add_argument('--attempt', required=True)
ap.add_argument('--port', type=int, default=18132)
ap.add_argument('--reproduction', action='store_true')
a = ap.parse_args()
if a.reproduction and time.time() <= deadline():
    raise RuntimeError('Later explicit replay only; the active deadline remains binding')
out = ROOT / 'experiments/E016-device-plan-ids' / a.attempt
if out.exists():
    raise RuntimeError('Existing attempt; refuse overwrite')
out.mkdir(parents=True)
save(out / 'protocol.json', {'headline': False, 'variant': 'diagnostic-plan-compare-v1',
     'scope': 'Warmup-only arithmetic race diagnostic; the ON mode is intentionally unsafe.',
     'modes': ['off', 'on', 'on-ple-fence'], 'output': 64,
     'repair': 'Create all trace parents before first-head/per-layer capture; no build or source change.'})
for mode in ['off', 'on', 'on-ple-fence']:
    path = out / mode
    (path / 'traces').mkdir(parents=True)
    extra = {'STRATA_LAB_PLAN_COMPARE': '1'}
    if mode != 'off':
        extra.update(STRATA_VERIFY_DEVICE_PLAN='1', STRATA_LAB_PLAN_IDS='1')
    if mode == 'on-ple-fence':
        extra['STRATA_LAB_PLAN_PLE_FENCE'] = '1'
    with Session('diagnostic-plan-compare-v1', '32k', path, port=a.port,
                 budgeted=not a.reproduction, diagnostic_env=extra) as s:
        r = s.request('warmup', 'warmup', 'warmup')
        save(path / 'results.json', {'headline': False, 'request': r, 'mode': mode,
             'warning': 'No unsafe ON throughput enters headline summaries.'})
