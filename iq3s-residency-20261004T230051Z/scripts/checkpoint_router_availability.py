"""Persist the discovered stale-activation limitation and its repair plan."""
import json
from datetime import datetime, timezone
from lab import ROOT, save

status = json.loads((ROOT / 'STATUS.json').read_text())
path = str(ROOT / 'experiments/E008-router-boundary/v2/analysis-r2')
reason = ('Router-quality/readiness aggregates mix fresh and stale h_x when '
          'the current group is all-local: doorbell_publish_res skips x. '
          'Boundary/events and output accounting remain valid. E015 repairs '
          'diagnostic availability; the full-CPU negative verdict is restricted '
          'pending fresh-only analysis.')
if not any(x['path'] == path for x in status['excluded']):
    status['excluded'].append({'path': path, 'reason': reason})
status['running'] = 'E014'
status['next_exact_action'] = ('Both batteries passed. Run clean E014 same-binary '
    'OFF guard, then E013 exact-choice fast repair, three attempts per profile '
    'each. No background builds, training, or analysis. E015 build completed; '
    'its tests and collection follow headline measurements.')
status['updated_utc'] = datetime.now(timezone.utc).isoformat()
save(ROOT / 'STATUS.json', status)
(ROOT / 'STATUS.md').write_text('# Research status\n\n' +
    json.dumps(status, indent=2) + '\n')
