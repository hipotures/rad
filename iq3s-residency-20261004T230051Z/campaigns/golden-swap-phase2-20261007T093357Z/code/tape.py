"""Validate fixed-work binary tape without interpreting elapsed seconds as event identity."""
from pathlib import Path
import argparse,json,hashlib,numpy as np,ctypes
C=Path(__file__).resolve().parents[1]
HEADER=np.dtype([('magic','<u8'),('version','<u4'),('window_bytes','<u4'),('windows','<u8'),('prompt_count','<u8'),('output_budget','<u8'),('output_count','<u8'),('work_hash','<u8')])
ROUTES=np.dtype([('ids','<i4',(48,40)),('weights','<f4',(48,40)),('mtp_ids','<i4',(3,10)),('mtp_weights','<f4',(3,10)),('drafts','<i4',(3,)),('probs','<f4',(3,))])
WINDOW=np.dtype([('position','<i8'),('T','<i4'),('accepted','<i4'),('draft_count','<i4'),('emitted_before','<i4'),('inputs','<i4',(4,)),('outputs','<i4',(4,)),('routes',ROUTES)])
OBS=np.dtype([('begin_ns','<u8'),('end_ns','<u8'),('seen','<i4',(51,)),('disagreements','<i4',(51,)),('native_outputs','<i4',(4,)),('activation','<f4',(51,8))])
assert (HEADER.itemsize,WINDOW.itemsize,OBS.itemsize)==(56,15680,2072)
HEADER2=np.dtype(HEADER.descr+[("initial_rounds","<i8")])
ROUTES2=np.dtype(ROUTES.descr+[("qsa","<i4",(12,8204))])
WINDOW2=np.dtype([("position","<i8"),("T","<i4"),("accepted","<i4"),("draft_count","<i4"),("emitted_before","<i4"),("inputs","<i4",(4,)),("outputs","<i4",(4,)),("routes",ROUTES2)])
OBS2=np.dtype([("begin_ns","<u8"),("end_ns","<u8"),("seen","<i4",(51,)),("disagreements","<i4",(51,)),("native_outputs","<i4",(4,)),("qsa_seen","<i4",(12,)),("qsa_disagreements","<i4",(12,)),("activation","<f4",(51,8))])
class Tape:
 def __init__(self,path):
  self.path=Path(path);self.data=self.path.read_bytes();self.h=np.frombuffer(self.data,HEADER,1)[0];assert self.h['magic']==0x3150455441343451 and self.h['version'] in [1,2];self.version=int(self.h['version']);self.header_dtype=HEADER2 if self.version==2 else HEADER;self.window_dtype=WINDOW2 if self.version==2 else WINDOW;self.obs_dtype=OBS2 if self.version==2 else OBS;self.h=np.frombuffer(self.data,self.header_dtype,1)[0];assert self.h['window_bytes']==self.window_dtype.itemsize
  n=int(self.h['prompt_count']);off=self.header_dtype.itemsize;self.prompt=np.frombuffer(self.data,'<i4',n,off);off+=4*n;self.initial=np.frombuffer(self.data,'<i4',48*512,off).reshape(48,512);off+=4*48*512;self.heat=np.frombuffer(self.data,'<f4',48*512,off).reshape(48,512);off+=4*48*512;self.ws=np.frombuffer(self.data,self.window_dtype,int(self.h['windows']),off);assert off+self.ws.nbytes==len(self.data),'truncation/trailing';self.work_bytes=self.prompt.tobytes()+np.array([self.h['output_budget']],'<u8').tobytes()+self.ws.tobytes()
 def validate(self):
  errors=[];out=[];main=mtp=0;prevp=None;prevout=None
  lib=ctypes.CDLL(str(__import__('common').W/'builds/libfnv64.so'));f=lib.q4_fnv;f.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint64];f.restype=ctypes.c_uint64
  raw=np.frombuffer(self.work_bytes,np.uint8);computed_fnv=int(f(raw.ctypes.data,raw.nbytes,1469598103934665603))
  if computed_fnv!=int(self.h['work_hash']):errors.append('native FNV work checksum')
  for wi,w in enumerate(self.ws):
   T,a,nd=map(int,[w['T'],w['accepted'],w['draft_count']]);p=int(w['position']);r=w['routes'];e=int(w['emitted_before'])
   if not(1<=T<=4 and 0<=a<T and 0<=nd<=3):errors.append('shape');continue
   if prevp is not None and p!=prevp:errors.append('position dependency')
   if prevout is not None and w['inputs'][0]!=prevout:errors.append('main token dependency')
   if wi==0 and (T!=1 or p!=len(self.prompt)-1 or w['inputs'][0]!=self.prompt[-1]):errors.append('first window')
   if a<T-1 and w['inputs'][a+1]==w['outputs'][a]:errors.append('acceptance maximal prefix')
   if a>0 and not np.array_equal(w['inputs'][1:a+1],w['outputs'][:a]):errors.append('accepted equality')
   if e!=len(out):errors.append('emitted count')
   take=min(a+1,int(self.h['output_budget'])-e,int(self.h['output_count'])-e);out.extend(w['outputs'][:take].tolist());prevp=p+a+1;prevout=w['outputs'][a]
   if np.any(r['ids'][:,:10*T]<0) or np.any(r['ids'][:,:10*T]>=512):errors.append('route IDs')
   if not np.isfinite(r['weights'][:,:10*T]).all() or not np.isfinite(r['mtp_weights'][:nd]).all():errors.append('coefficient nonfinite')
   if self.version==2:
    q=r['qsa'].reshape(12,4,2051)[:,:T]
    # Native qsa_selection_width=min(n_kv,2051). Capacity tail is unused.
    for lane in range(T):
     width=min(p+lane+1,2051);active=q[:,lane,:width]
     if np.any(active<0) or np.any(active>p+lane):errors.append('QSA active selection IDs')
     if np.any(np.diff(active,axis=1)<=0):errors.append('QSA active selection ordering/uniqueness')
   if nd and wi+1<len(self.ws):
    nxt=self.ws[wi+1];nT=int(nxt['T']);expected=1
    while expected<4 and r['probs'][expected-1]>=.5:expected+=1
    if nT!=expected or not np.array_equal(nxt['inputs'][1:nT],r['drafts'][:nT-1]):errors.append('MTP dependency/early stopping')
   main+=T*48*10;mtp+=nd*10
  if len(out)!=self.h['output_count']:errors.append('final output count')
  if not 0<int(self.h['output_count'])<=int(self.h['output_budget']):errors.append('output header bounds')
  if int(np.sum(self.ws['accepted']+1))-len(out)>int(self.ws[-1]['accepted']):errors.append('unemitted suffix exceeds final window')
  result={'state':'PASS' if not errors else 'FAIL','errors':list(dict.fromkeys(errors)),'path':str(self.path),'schema':self.version,'initial_rounds':int(self.h['initial_rounds']) if self.version==2 else None,'sparse_attention_frozen':self.version==2,'native_FNV_work_verified':computed_fnv==int(self.h['work_hash']),'tape_sha256':hashlib.sha256(self.data).hexdigest(),'work_sha256':hashlib.sha256(self.work_bytes).hexdigest(),'native_FNV64':f"{int(self.h['work_hash']):016x}",'prompt_count':len(self.prompt),'prompt_ids_sha256_binary':hashlib.sha256(self.prompt.tobytes()).hexdigest(),'committed_emitted_output':len(out),'committed_in_state_prefix':int(np.sum(self.ws['accepted']+1)),'output_ids_sha256_binary':hashlib.sha256(np.asarray(out,'<i4').tobytes()).hexdigest(),'windows':len(self.ws),'main_routed_events':len(self.ws)*48,'MTP_full_routed_events':int(np.sum(self.ws['draft_count'])),'MTP_KV_only_catchup_invocations':int(np.count_nonzero(self.ws['draft_count'])),'MTP_KV_only_catchup_rows':int(self.ws['T'][self.ws['draft_count']>0].sum()),'MTP_full_routed_shape':'one row per actual draft step; catchup is native T-row KV-only prefix with no router/expert kernel','main_routed_entries':main,'MTP_routed_entries':mtp,'verifier_T_sum':int(self.ws['T'].sum()),'MTP_proposed_to_verifier':int(np.sum(self.ws['T']-1)),'MTP_accepted_to_commit':int(np.sum(self.ws['accepted'])),'RAM_tape_MB':len(self.data)/1e6,'initial_residents':int(np.count_nonzero(self.initial>=0)),'initial_resident_sha256':hashlib.sha256(self.initial.tobytes()).hexdigest(),'initial_heat_sha256':hashlib.sha256(self.heat.tobytes()).hexdigest(),'scope':'all48main decode layers plus real MTP routed steps; normal prefill from exactIDs, not route-overridden'}
  return result
 def events(self):
  for i,w in enumerate(self.ws):
   for l in range(48):yield i*48+l,l,w['routes']['ids'][l,:int(w['T'])*10],w['routes']['weights'][l,:int(w['T'])*10]
def main():
 a=argparse.ArgumentParser();a.add_argument('path');a.add_argument('--out');v=a.parse_args();t=Tape(v.path);r=t.validate();print(json.dumps(r,indent=2));p=Path(v.out) if v.out else C/'tapes'/f'{t.path.stem}-manifest.json';p.write_text(json.dumps(r,indent=2)+'\n');assert r['state']=='PASS',r
if __name__=='__main__':main()
