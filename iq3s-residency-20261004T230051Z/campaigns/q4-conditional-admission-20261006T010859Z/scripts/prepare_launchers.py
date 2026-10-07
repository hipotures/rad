"""Separate immutable launchers; no change to existing user production scripts."""
from pathlib import Path
from campaign import C,R,load,save
def main():
 variants=['control']
 decision=C/'phase-b/live-gate.json'
 if decision.exists() and load(decision)['qualifies_live'] and (C/'configs/conditional-32k.json').exists():variants+=['conditional']
 for variant in variants:
  root=C/'launchers'/variant;root.mkdir(parents=True,exist_ok=True)
  for profile in ('32k','128k','256k'):
   save(root/f'{profile}.json',load(C/'configs'/f'{variant}-{profile}.json'))
   path=root/f'start-{profile}.sh';path.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec "'+str(R/'src/control/.venv/bin/python')+'" "'+str(C/'scripts/launch.py')+'" start --variant '+variant+' --profile '+profile+' "$@"\n');path.chmod(0o755)
  for file,action in [('stop.sh','stop'),('reproduce.sh','reproduce')]:
   p=root/file;p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec "'+str(R/'src/control/.venv/bin/python')+'" "'+str(C/'scripts/launch.py')+'" '+action+' --variant '+variant+' "$@"\n');p.chmod(0o755)
  (root/'README.md').write_text('# '+variant+'\n\n'+('Unchanged frozen Q4/100us production reference.' if variant=='control' else 'Experimental pre-copy conditional admission. Consult report for deployment recommendation/output trajectory limitations.')+'\n\nK24/PCIe.28/pool100us/15workers/spec4/.5/INT8/kv32768/prefillauto/suffix0/reuse0. One foreground server. Defaultlocalhost:8080. Full binary/source/model/config checks and GPU/port conflict refusal; no build/download/update. Logs and UI snapshots retained. Ctrl-C stops owned server.\n\n```bash\n./start-32k.sh --host 0.0.0.0 --port 8080\n./start-128k.sh --host 0.0.0.0 --port 8080\n./start-256k.sh --host 0.0.0.0 --port 8080\n./stop.sh\n./reproduce.sh --profile 128k --port 18144\n```\n\nRun one launcher at a time. `--check` no inference; `--smoke` launches64-output request and stops. Reproducer onlyafter campaigncomplete;3fresh servers, identicalwarmup,one requesteach,no retries. Normal user launchers untouched.\n')
 print('LAUNCHERS',variants,flush=True)
if __name__=='__main__':main()
