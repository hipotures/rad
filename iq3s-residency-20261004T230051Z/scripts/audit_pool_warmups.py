"""Read saved requests only; verify the warmup fairness condition at each fresh pair."""
import argparse,hashlib,pathlib
from lab import ROOT,load,save
ap=argparse.ArgumentParser();ap.add_argument('experiment');a=ap.parse_args();base=ROOT/'experiments'/a.experiment;s=load(base/'summary.json');rows=[]
for pair in s['paired']:
 family=pair['family'];profile=pair['profile'];n=pair['replicate'];data={}
 for role in ['default','sleep100us']:
  d=base/'v1'/family/profile/role/f'rep{n}'/'raw';w=load(d/'warmup.json');ids=load(d/'output-ids-request1.json');incoming=load(d/'output-ids-input-request1.json')
  assert w['state']=='VALID' and w['actual_output_tokens']==64 and len(ids)==64 and w['actual_input_tokens']==4096
  assert incoming['count']==4096 and incoming['sha256']==w['payload']['input_ids_sha256']
  data[role]={'input':incoming,'output_ids_sha256':hashlib.sha256((d/'output-ids-request1.json').read_bytes()).hexdigest(),'actual_output_tokens':w['actual_output_tokens'],'mtp_proposed':w['mtp_proposed'],'mtp_accepted':w['mtp_accepted'],'config_spec':w['full_config']['args'][w['full_config']['args'].index('--spec')+1],'reuse':w['reuse']}
 rows.append({'family':family,'profile':profile,'replicate':n,'same_warmup':data['default']==data['sleep100us'],'roles':data})
result={'state':'PASS' if all(r['same_warmup'] for r in rows) else 'INVESTIGATE','pairs':len(rows),'rows':rows,'scope':'Actual input/outputIDs, counts, MTP, spec and reuse; every measured run followed identical fixed64-token warmup'};save(base/'warmup-audit.json',result);print(result['state'],len(rows),flush=True)
assert result['state']=='PASS'
