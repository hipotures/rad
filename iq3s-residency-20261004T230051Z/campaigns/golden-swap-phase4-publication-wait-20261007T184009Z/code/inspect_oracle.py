"""Conservation and logical ownership audit; monotonic host timeline, not GPU hardware clock."""
import numpy as np,json,re,argparse
from pathlib import Path
from tape import Tape
C=Path(__file__).resolve().parents[1]
L=np.dtype([('event','<u8'),('begin','<u8'),('plan_end','<u8'),('cpu_end','<u8'),('layer','<i4'),('n','<i4'),('ids','<i4',(40,)),('slots','<i4',(40,)),('path','<i4',(40,))])
E=np.dtype([(k,'<u8') for k in ['issue_ns','stage_begin','stage_end','copy_begin','copy_end','publish_ns']]+[(k,'<i4') for k in ['trigger','target','published_at','layer','incoming','victim','slot','oldslot','status']]+[('pad','<u4')]+[(k,'<u8') for k in ['bytes','uses','victim_uses']])
N=np.dtype([('issue_ns','<u8'),('publish_ns','<u8'),('bytes','<u8')]+[(k,'<i4') for k in ['window','layer','incoming','victim','slot']]+[('pad','<u4')])
assert (L.itemsize,E.itemsize,N.itemsize)==(520,112,48)
def audit(label,tape):
 p=Path(label) if Path(label).is_absolute() else C/'raw'/label;prefix=p/'raw/oracle';t=Tape(tape);layers=np.fromfile(str(prefix)+'-layers.bin',L);events=np.fromfile(str(prefix)+'-admissions.bin',E);native=np.fromfile(str(prefix)+'-native.bin',N);log=(p/'raw/run-engine.log').read_text();reserve_rows=re.findall(r'Q4_ORACLE_RESERVE device=(\d+) class=(\d+) bytes=(\d+) slot=(\d+) layer=(\d+) expert=(\d+)',log);initial_donor_absent=0
 for row in layers:
  for d,c,size,slot,l,e in reserve_rows:
   if int(row['layer'])==int(l):initial_donor_absent+=int(np.count_nonzero((row['ids'][:int(row['n'])]==int(e))&(row['slots'][:int(row['n'])]<0)))
 errors=[];counts={'local':0,'cpu':0,'mapped':0,'other':0};bylayer=[]
 if len(layers)!=len(t.ws)*48:errors.append('main event conservation')
 for i,a in enumerate(layers):
  wi,l=divmod(i,48);n=int(a['n']);expected=t.ws[wi]['routes']['ids'][l,:int(t.ws[wi]['T'])*10]
  if int(a['event'])!=i or l!=a['layer'] or n!=len(expected) or not np.array_equal(a['ids'][:n],expected):errors.append('event/route shape mismatch')
  paths=a['path'][:n];slots=a['slots'][:n];local=int(np.count_nonzero(slots>=0));cpu=int(np.count_nonzero(paths==-1));mapped=int(np.count_nonzero(paths==1));counts['local']+=local;counts['cpu']+=cpu;counts['mapped']+=mapped;counts['other']+=n-local-cpu-mapped
 if len(events):
  pub=events[events['publish_ns']>0]
  if np.any(pub['publish_ns']<pub['copy_end']) or np.any(events['copy_end']<events['copy_begin']):errors.append('publication before completion')
  if np.any(pub['layer']<0) or np.any(pub['victim']<0):errors.append('invalid publication')
  # Spares swap identity: a published copy consumes current class spare and releases oldslot.
  seen={};active={};slots={};spares={};res=t.initial.copy()
  log=(p/'raw/run-engine.log').read_text()
  for d,c,size,s,l,e in re.findall(r'Q4_ORACLE_RESERVE device=(\d+) class=(\d+) bytes=(\d+) slot=(\d+) layer=(\d+) expert=(\d+)',log):
   spares[(int(d),int(c))]=int(s);res[int(l),int(e)]=-1
  pending=[]
  for e in np.sort(pub,order='publish_ns'):
   l=int(e['layer']);cls={3072000:0,3584000:1,3993600:2}[int(e['bytes'])];key=(l//24,cls)
   if spares.get(key)!=int(e['slot']):errors.append('spare ownership mismatch')
   if res[l,int(e['incoming'])]>=0 or res[l,int(e['victim'])]!=int(e['oldslot']):errors.append('publication stale identity')
   res[l,int(e['victim'])]=-1;res[l,int(e['incoming'])]=int(e['slot']);spares[key]=int(e['oldslot'])
  # Validate every observed demand against the publication timeline, not only final ownership.
  state=t.initial.copy();class_spares={}
  for d,c,size,slot,l,e in re.findall(r'Q4_ORACLE_RESERVE device=(\d+) class=(\d+) bytes=(\d+) slot=(\d+) layer=(\d+) expert=(\d+)',log):state[int(l),int(e)]=-1
  ordered=np.sort(pub,order='publish_ns');k=0
  for row in layers:
   while k<len(ordered) and int(ordered[k]['publish_ns'])<=int(row['plan_end']):
    event=ordered[k];l=int(event['layer']);state[l,int(event['victim'])]=-1;state[l,int(event['incoming'])]=int(event['slot']);k+=1
   l=int(row['layer']);n=int(row['n']);ids=row['ids'][:n]
   if not np.array_equal(state[l,ids],row['slots'][:n]):errors.append('per-demand stale slot identity')
  for event in pub:
   wi=int(event['published_at'])//48;l=int(event['layer'])
   if int(event['victim']) in t.ws[wi]['routes']['ids'][l,:int(t.ws[wi]['T'])*10]:errors.append('evicted current-window protected victim')
   target=int(event['target']);wi,l=divmod(target,48)
   if int(event['incoming']) not in t.ws[wi]['routes']['ids'][l,:int(t.ws[wi]['T'])*10]:errors.append('target lacks predicted actual demand')
  total=int(np.count_nonzero(res>=0))
  if total!=int(np.count_nonzero(t.initial>=0))-5:errors.append('active capacity')
  for d in range(2):
   values=res[d*24:(d+1)*24];values=values[values>=0]
   if len(np.unique(values))!=len(values):errors.append('duplicate active slot')
 else:pub=events
 def quantile(v):return dict(zip(['min','median','p95','max'],map(float,np.quantile(v,[0,.5,.95,1])))) if len(v) else None
 r={'label':label,'state':'PASS' if not errors else 'FAIL','errors':sorted(set(errors)),'main_events':len(layers),'demand':counts,'copies':{'initial_spares':len(reserve_rows),'initial_spare_bytes':sum(int(x[2]) for x in reserve_rows),'restoration_bytes':sum(int(x[2]) for x in reserve_rows),'initial_donor_absent_entries':initial_donor_absent,'metadata_H2D_bytes_oracle':len(reserve_rows)*8+len(pub)*8,'issued':len(events),'bytes_issued':int(events['bytes'].sum()),'completed':int(np.count_nonzero(events['copy_end'])),'completed_bytes':int(events['bytes'][events['copy_end']>0].sum()),'staged_bytes':int(events['bytes'][events['stage_end']>0].sum()),'unpublished_bytes':int(events['bytes'][events['publish_ns']==0].sum()),'pending_at_end':int(np.count_nonzero((events['status']==4)|(events['status']==0))),'duplicate_suppressed':int(np.count_nonzero(events['status']==2)),'published':len(pub),'published_bytes':int(pub['bytes'].sum()),'ready_publications':int(np.count_nonzero(pub['status']==1)),'late_publications':int(np.count_nonzero(pub['status']==3)),'uses':int(events['uses'].sum()),'victim_absent':int(events['victim_uses'].sum()),'unused_bytes':int(events['bytes'][events['uses']==0].sum()),'native_issued':len(native),'native_bytes':int(native['bytes'].sum()),'native_published':int(np.count_nonzero(native['publish_ns'])),'native_published_bytes':int(native['bytes'][native['publish_ns']>0].sum()),'native_pending_bytes':int(native['bytes'][native['publish_ns']==0].sum())},'ms':{'staging':quantile((events['stage_end']-events['stage_begin'])/1e6),'copy_with_host_wait':quantile((events['copy_end']-events['copy_begin'])/1e6),'publication_delay_after_copy':quantile((pub['publish_ns']-pub['copy_end'])/1e6)},'scope_coverage':{'layers':sorted(set(map(int,layers['layer']))),'classes_bytes':sorted(set(map(int,events['bytes']))) if len(events) else sorted(set(map(int,native['bytes']))),'main_demand_entries':sum(counts.values()),'main_scope_fraction':1.0,'MTP_residency':'unchanged'},'scope':'48main layers, all3physical classes, MTP routes computed/frozen but residency unchanged','clock':'CPU monotonic timestamps include scheduling, cudaEventSynchronize wait; not exact DMA-only GPU duration'}
 (p/'ownership-audit.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('label');a.add_argument('tape');v=a.parse_args();r=audit(v.label,v.tape);print(json.dumps(r,indent=2));assert r['state']=='PASS',r
