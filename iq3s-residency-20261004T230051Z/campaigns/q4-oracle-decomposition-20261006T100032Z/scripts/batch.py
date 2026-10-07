"""Frozen fresh-start blocks. Each completed/failed attempt immutable; never favorable retries."""
import argparse,json,sys,time
from pathlib import Path
from owned import C,run
from fidelity import audit as fidelity
from inspect_oracle import audit as ownership
PY=C.parents[1]/'src/control/.venv/bin/python'
def point(profile,arm,attempt,payload=None,tape=None,check=False,unknown='legacy'):
 label=f'v2-{profile}-{arm}-attempt{attempt}'
 args=[PY,C/'scripts/runner.py','replay','--profile',profile,'--label',label,'--payload',payload or profile+'-run1','--variant','oracle-decomposition-v2','--tape',tape or C/'tapes'/f'capture-{profile}-v3.bin']
 budgets={'current':('full','full'),'FF':('full','full'),'64F':('64','full'),'F64':('full','64'),'F256':('full','256'),'6464':('64','64'),'repair64':('64','64')}
 i,v=budgets[arm];args+=['--oracle','off' if arm=='current' else 'full','--incoming',i,'--victim',v,'--unknown','ema-tail' if arm=='repair64' else unknown]
 if check:args+=['--check']
 out=run(label,args,timeout=1200)
 tape=Path(tape or C/'tapes'/f'capture-{profile}-v3.bin');f=fidelity(label,tape);o=ownership(label,tape)
 assert f['state']=='PASS' and o['state']=='PASS',(f['errors'],o['errors'])
 (C/'ledger.jsonl').open('a').write(json.dumps({'phase':'C','label':label,'state':'VALID','profile':profile,'arm':arm,'attempt':attempt,'fidelity':'PASS','ownership':'PASS'})+'\n')
 return label
def main():
 a=argparse.ArgumentParser();a.add_argument('phase',choices=['overhead','32k','transfer','independent']);v=a.parse_args()
 if v.phase=='overhead':
  args=[PY,C/'scripts/runner.py','natural','--profile','32k','--label','development-v2-natural','--payload','development','--variant','oracle-decomposition-v2']
  run('development-v2-natural',args,timeout=1200)
  point('32k','current','development',payload='development',tape=C/'tapes/development-capture-v3.bin')
 elif v.phase=='32k':
  protocol=json.loads((C/'phase-a/protocol.json').read_text())
  for attempt,arms in enumerate(protocol['32k_blocks'],1):
   for arm in arms:point('32k',arm,attempt)
 elif v.phase=='transfer':
  protocol=json.loads((C/'phase-c/transfer-protocol.json').read_text())
  for profile,blocks in protocol['blocks'].items():
   for attempt,arms in enumerate(blocks,1):
    for arm in arms:point(profile,arm,attempt)
 else:
  protocol=json.loads((C/'phase-c/independent-protocol.json').read_text())
  for attempt,arms in enumerate(protocol['blocks'],1):
   for arm in arms:point('32k',arm,'independent'+str(attempt),payload='independent-code4',tape=C/'tapes/independent-code4-capture-v3.bin',check=True)
 print('BATCH_COMPLETE',v.phase,flush=True)
if __name__=='__main__':main()
