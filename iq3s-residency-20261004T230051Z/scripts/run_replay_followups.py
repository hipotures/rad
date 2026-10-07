"""Finite, independently recorded causal-signal and transfer-sensitivity follow-ups."""
import argparse, hashlib, pathlib, shutil, subprocess
from lab import ROOT, save
py=str(ROOT/'src/control/.venv/bin/python')
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='v1');ap.add_argument('--sensitivity-attempt',default='v4-sensitivity');a=ap.parse_args()
traces={'32k':ROOT/'experiments/E003-diagnostics/v5/32k/traces/runtime-request2',
        '128k':ROOT/'experiments/E003-diagnostics/v5-portfix/128k/traces/runtime-request2'}
steps=[]
for profile,prefix in traces.items():
    steps.append((ROOT/'experiments/E007-causal-signals'/a.attempt/profile,
                  ROOT/'experiments/E007-causal-signals'/a.attempt/f'{profile}-rate12p6',
                  str(prefix),12.6,['markov-scaled','token-bigram-hybrid']))
for rate in (1.8,.5):
    for profile,prefix in traces.items():
        tag=str(rate).replace('.','p')
        steps.append((ROOT/'experiments/E004-replay'/a.sensitivity_attempt/f'{profile}-rate{tag}',
                      ROOT/'experiments/E004-replay'/a.sensitivity_attempt/f'{profile}-rate{tag}',
                      str(prefix),rate,['current','frequency','future-nextuse']))
plan=ROOT/'experiments/E007-causal-signals'/a.attempt/'followup-plan.json'
if plan.exists():raise RuntimeError('Follow-up plan already exists')
save(plan,{'steps':[{'command':[py,str(ROOT/'scripts/replay.py'),prefix,'--output',str(output),'--policies',*policies,'--rate',str(rate)],'logpath':str(path/'logs/replay')} for path,output,prefix,rate,policies in steps],
           'source_sha256':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['replay.py','token_history.py']},
           'timing_scope':'Offline CPU diagnostics only; must finish before clean headline speed measurements. One execution per deterministic point.'})
for path,output,prefix,rate,policies in steps:
    command=[py,str(ROOT/'scripts/replay.py'),prefix,'--output',str(output),'--policies',*policies,'--rate',str(rate)]
    wrapped=[py,str(ROOT/'scripts/run_logged.py'),'--path',str(path/'logs/replay'),'--timeout','120','--',*command]
    rc=subprocess.run(wrapped,cwd=ROOT,timeout=140).returncode
    if rc:raise SystemExit(rc)
