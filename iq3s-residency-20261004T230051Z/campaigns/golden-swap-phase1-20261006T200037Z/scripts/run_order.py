from common import *
tasks=['code-archive','math-inventory','text-websocket','mixed-chinook'];arms=['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_LEARNED_VICTIM'];runs=[]
for block in range(1,4):
 for ti,task in enumerate(tasks):
  shift=(block-1+ti)%3;order=arms[shift:]+arms[:shift]
  for arm in order:runs.append({'task':task,'block':block,'arm':arm,'attempt':block,'label':f'{task}-block{block}-{arm}'})
save(C/'run-order.json',{'frozen_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'main':runs,'fallback':'Block rounds1/2/3, each fixed task order archive/inventory/websocket/chinook. Preserve complete adjacent three-arm blocks; no gain-based selection. Do not start block unless projected completion plus reserve fits cutoff.','optional':'text-tls128K actual81.7K calibration-source; only if main and analysis reserve fit.','attempt_limit':3});ledger('Counterbalanced main order and deadline fallback frozen before live timings',requests=len(runs))
