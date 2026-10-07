"""Read the versioned numeric trace and validate its full demand/publication accounting."""
import hashlib,json,pathlib,sys
import numpy as np
ENTRY=np.dtype([('expert','<i2'),('token','i1'),('path','i1'),('slot','<i4')])
LAYER=np.dtype([(x,'<u8') for x in ['window','t0','t1','t2','t3','t4','offset']]+[('layer','<u4'),('tokens','<u2'),('k','<u2')])
WINDOW=np.dtype([(x,'<u8') for x in ['number','position','begin','verify_end','end','pending_begin','pending_end']]+[(x,'<u4') for x in ['T','accepted','produced','reserved']]+[('tokens','<i4',(8,))])
PROMOTION=np.dtype([(x,'<u8') for x in ['window','issue','observed_ready','bytes']]+[(x,'<i4') for x in ['layer','incoming','outgoing','slot']])
PROMOTION_V2=np.dtype([(x,'<u8') for x in ['window','issue','observed_ready','bytes']]+[(x,'<i4') for x in ['layer','incoming','outgoing','slot','outgoing_layer','reserved']])
REACH=np.dtype([(x,'<u8') for x in ['window','begin','reached','released']]+[('layer','<i4'),('reserved','<i4')])
assert [x.itemsize for x in [ENTRY,LAYER,WINDOW,PROMOTION,REACH]]==[8,64,104,48,40]
class Trace:
 def __init__(self,prefix):
  self.prefix=str(prefix)
  def read(name,dtype):return np.fromfile(self.prefix+'-'+name+'.bin',dtype=dtype)
  metadata=pathlib.Path(self.prefix+'-schema.json')
  self.schema=json.loads(metadata.read_text()) if metadata.exists() else {'version':1,'promotion_record_bytes':48}
  if self.schema not in ({'version':1,'promotion_record_bytes':48},{'version':2,'promotion_record_bytes':56,'cross_layer_victim':True}):raise ValueError('Unknown trace schema; refuse guessing layout')
  self.entries=read('entries',ENTRY);self.layers=read('layers',LAYER);self.windows=read('windows',WINDOW);self.promotions=read('promotions',PROMOTION_V2 if self.schema['version']==2 else PROMOTION);self.reach=read('reach',REACH)
  self.blob_bytes=read('blob-bytes','<u8');self.nl=len(self.blob_bytes);self.initial=read('initial','<i4').reshape(self.nl,-1);self.final=read('final','<i4').reshape(self.initial.shape);self.ne=self.initial.shape[1]
  self.initial_usage=read('initial-usage','<f4').reshape(self.initial.shape);self.final_usage=read('final-usage','<f4').reshape(self.initial.shape)
  self.slot_bytes=[read('slot-bytes-gpu0','<u8'),read('slot-bytes-gpu1','<u8')];self.output_ids=read('output-ids','<i4')
  # Runtime rounds include prefill and need not start at zero for this request.
  self.window_index={int(w['number']):i for i,w in enumerate(self.windows)}
  if len(self.window_index)!=len(self.windows):raise ValueError('Duplicate runtime window IDs')
 def grouped(self):
  for layer in self.layers:
   at=int(layer['offset']);yield layer,self.entries[at:at+int(layer['tokens'])*int(layer['k'])]
 def counts(self):
  a=np.zeros((len(self.windows),self.nl,self.ne),dtype=np.float32)
  for r,es in self.grouped():
   np.add.at(a[self.window_index[int(r['window'])],int(r['layer'])],es['expert'],1)
  return a
 def validate(self):
  errors=[];counts={int(p):int(np.count_nonzero(self.entries['path']==p)) for p in [-1,0,1,2]}
  if sum(counts.values())!=len(self.entries):errors.append('Unknown path enum')
  if self.ne!=512 or self.nl!=48:errors.append('Unexpected model geometry')
  if np.any(self.entries['expert']<0) or np.any(self.entries['expert']>=self.ne):errors.append('Invalid expert ID')
  expected=int(np.sum(self.windows['T']))*self.nl*10
  if expected!=len(self.entries):errors.append(f'Entry total mismatch: expected {expected}, got {len(self.entries)}')
  if self.windows.size and int(self.windows[-1]['produced'])!=len(self.output_ids):errors.append('Output count mismatch')
  if np.any(self.windows['accepted']>=self.windows['T']):errors.append('Invalid acceptance range')
  events=[]
  for p in self.promotions:
   events.append((int(p['issue']),0,p))
   if p['observed_ready']:events.append((int(p['observed_ready']),1,p))
  events.sort(key=lambda e:(e[0],e[1]));state=self.initial.copy();idx=0;bad_resident=0;bad_kind=0
  for layer,es in self.grouped():
   now=int(layer['t0']);l=int(layer['layer']);w=int(layer['window'])
   if not all(int(layer[a])<=int(layer[b]) for a,b in zip(['t0','t1','t2','t3'],['t1','t2','t3','t4'])):errors.append('Unordered host dispatch timestamps')
   while idx<len(events) and events[idx][0]<=now:
    _,kind,p=events[idx];pl=int(p['layer'])
    if kind==0:state[int(p['outgoing_layer']) if 'outgoing_layer' in p.dtype.names else pl,int(p['outgoing'])]=-1
    else:state[pl,int(p['incoming'])]=int(p['slot'])
    idx+=1
   current=state[l,es['expert']]
   bad_resident+=int(np.count_nonzero(current!=es['slot']))
   bad_kind+=int(np.count_nonzero((es['path']==0)!=(current>=0)))
   if np.any(es['token']<0) or np.any(es['token']>=self.windows[self.window_index[w]]['T']):errors.append('Invalid global branch ordinal')
  while idx<len(events):
   _,kind,p=events[idx];pl=int(p['layer'])
   if kind==0:state[int(p['outgoing_layer']) if 'outgoing_layer' in p.dtype.names else pl,int(p['outgoing'])]=-1
   else:state[pl,int(p['incoming'])]=int(p['slot'])
   idx+=1
  if bad_resident:errors.append(f'{bad_resident} residency mismatches in recorded policy replay')
  if bad_kind:errors.append(f'{bad_kind} path/local-hit mismatches')
  if not np.array_equal(state,self.final):errors.append('Recorded promotion replay final residency mismatch')
  for p in self.promotions:
   gpu=0 if p['layer']<25 else 1
   if 'outgoing_layer' in p.dtype.names and (0 if p['outgoing_layer']<25 else 1)!=gpu:errors.append('Cross-device victim in same-device policy trace')
   if p['slot']<0 or p['slot']>=len(self.slot_bytes[gpu]):errors.append('Invalid promotion slot')
   elif p['bytes']>self.slot_bytes[gpu][p['slot']]:errors.append('Promotion exceeds physical slot class')
   if p['observed_ready'] and p['observed_ready']<p['issue']:errors.append('Published before copy issue')
  return {'prefix':self.prefix,'state':'PASS' if not errors else 'FAIL','errors':list(dict.fromkeys(errors)),'windows':len(self.windows),'layers':len(self.layers),'output_tokens':len(self.output_ids),'output_ids_sha256':hashlib.sha256(self.output_ids.tobytes()).hexdigest(),'demand_entries':len(self.entries),'path_counts':counts,'all_demand_local_hit_pct':100*counts[0]/len(self.entries) if len(self.entries) else None,'reported_hit_pct_denominator':100*counts[0]/(counts[0]+counts[-1]) if counts[0]+counts[-1] else None,'promotions':len(self.promotions),'promotion_bytes':int(self.promotions['bytes'].sum()),'unpublished_promotions_at_request_end':int(np.count_nonzero(self.promotions['observed_ready']==0)),'gpu_budgets':[{'slots':len(x),'bytes':int(x.sum()),'size_classes':{str(int(n)):int(c) for n,c in zip(*np.unique(x,return_counts=True))}} for x in self.slot_bytes]}
if __name__=='__main__':
 t=Trace(sys.argv[1]);r=t.validate();print(json.dumps(r,indent=2));sys.exit(0 if r['state']=='PASS' else 1)
