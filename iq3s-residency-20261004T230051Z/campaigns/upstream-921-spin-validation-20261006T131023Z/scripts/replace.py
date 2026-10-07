"""Objective invalidation and bounded replacement; original pair always preserved.

Only use after investigating a concrete protocol/system failure, never a timing
result or token trajectory difference. Two replacement slots per cell maximum.
"""
import argparse,copy,json,os,pathlib,time
import run
C=run.C
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cell',required=True,choices=list(run.load(C/'orders/all.json')));ap.add_argument('--pair',type=int,required=True);ap.add_argument('--reason',required=True);ap.add_argument('--evidence',type=pathlib.Path,required=True);ap.add_argument('--measure',action='store_true');a=ap.parse_args()
 path=C/'raw'/a.cell/f'pair{a.pair:02d}';assert path.exists(),'Original attempt missing'
 assert not (path/'pair.json').exists(),'Refuse replacing protocol-valid pair'
 assert a.evidence.is_file(),'Objective evidence missing'
 orders=run.load(C/'orders/all.json');original=orders[a.cell]['pairs'][a.pair-1]
 ledger=run.load(C/'invalid-pair-ledger.json');entry=next((x for x in ledger if x['path']==str(path)),None)
 if entry is None:
  used=[x for x in ledger if x['cell']==a.cell];assert len(used)<2,'Replacement limit'
  slot=len(used)+1
  entry={'cell':a.cell,'original_pair':a.pair,'path':str(path),'state':'INVALID_ENTIRE_PAIR','reason':a.reason,'evidence':str(a.evidence.resolve()),'evidence_sha256':run.filehash(a.evidence),'audit_utc':run.utc(),'replacement_slot':slot,'replacement_path':str(C/'raw'/a.cell/f'replacement{slot:02d}')}
  ledger.append(entry);run.save(C/'invalid-pair-ledger.json',ledger);run.save(path/'invalid.json',entry)
 if not a.measure:print(json.dumps(entry,indent=2));return
 env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')}
 assert run.load(C/'provenance/parent-environment-hashes.json')=={k:run.hashlib.sha256(v.encode()).hexdigest() for k,v in env.items()},'Parent environment drift'
 point=copy.deepcopy(original);slot=entry['replacement_slot'];point.update(order=orders[a.cell]['replacement_slots'][slot-1]['order'],replacement=True,replacement_slot=slot,replaces_pair=a.pair)
 assert time.monotonic()<run.load(C/'timing.json')['measurement_cutoff_monotonic'],'Measurement cutoff'
 run.runpair(a.cell,point,env,run.load(C/'configs-base.json'),run.load(C/'workloads/manifest.json'),run.load(C/'timing.json'),directory=f'replacement{slot:02d}')
if __name__=='__main__':main()
