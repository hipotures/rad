"""C++/Python joint-selector parity, byte budgets and pointer/ID accounting; CPU-only."""
import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import ctypes,numpy as np,subprocess,time
from campaign import C,save
from q4_replay import SWAP
out=C/'analysis/history-selector-test';out.mkdir(exist_ok=False)
cpp=out/'wrapper.cpp';cpp.write_text('''#include "q4_history_policy.hpp"
extern "C" int select_q4(const float* heat,const float* fast,const int* resident,const unsigned long long* bytes,void* output){
 strata::research::Q4HistoryPolicy p;p.enabled=true;p.active=true;p.nl=48;p.ne=512;p.fast.assign(fast,fast+48*512);p.bytes.assign(bytes,bytes+48);std::vector<float> h(heat,heat+48*512);std::vector<int> r(resident,resident+48*512);struct S{float gain;int layer,in,out;};std::vector<S> result;p.select(h,r,result,96);std::copy(result.begin(),result.end(),(S*)output);return result.size();}
''')
cmd=['g++','-O2','-std=c++17','-fPIC','-shared','-I'+str(C/'scripts/templates'),str(cpp),'-o',str(out/'selector.so')]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(out/'build.log').write_text(r.stdout+r.stderr);assert not r.returncode
lib=ctypes.CDLL(str(out/'selector.so'));lib.select_q4.argtypes=[ctypes.c_void_p]*5
rng=np.random.default_rng(20261005);bb=np.full(48,3072000,np.uint64);bb[[4,30,46,47]]=3584000;bb[2]=3993600;records=[]
for case in range(30):
 heat=(rng.random((48,512))*12).astype(np.float32);fast=(rng.random((48,512))*4).astype(np.float32);resident=np.full((48,512),-1,np.int32)
 for l in range(48):ids=rng.choice(512,240,replace=False);resident[l,ids]=np.arange(240)
 score=heat*.2+fast*np.float32(2/3);choices=[]
 for l in range(48):
  ins=np.flatnonzero((resident[l]<0)&(score[l]>=1));outs=np.flatnonzero(resident[l]>=0)
  ins=sorted(ins,key=lambda e:(-float(score[l,e]),int(e)));outs=sorted(outs,key=lambda e:(float(score[l,e]),int(e)))
  for inc,victim in zip(ins,outs):
   benefit=float(score[l,inc]-score[l,victim])*.25-int(bb[l])/13.2e6-.0042
   if benefit<=.125:break
   choices.append((benefit/int(bb[l]),l,int(inc),int(victim)))
 choices.sort(key=lambda x:(-x[0],x[1],x[2],x[3]));expected=[];used=[0,0]
 for gain,l,inc,victim in choices:
  dev=l>=24
  if len(expected)>=96:break
  if used[dev]+int(bb[l])>160*1024*1024:continue
  used[dev]+=int(bb[l]);expected.append((l,inc,victim))
 actual=np.zeros(96,SWAP);n=lib.select_q4(heat.ctypes.data,fast.ctypes.data,resident.ctypes.data,bb.ctypes.data,actual.ctypes.data)
 found=[(int(x['layer']),int(x['incoming']),int(x['outgoing'])) for x in actual[:n]]
 assert found==expected,(case,found,expected)
 assert n<=96 and max(used)<=160*1024*1024
 assert len(set((l,e) for l,e,v in found))==n and len(set((l,v) for l,e,v in found))==n
 records.append({'case':case,'actions':n,'device_bytes':used,'parity':True})
save(out/'result.json',{'state':'PASS','cases':records,'scope':'30 independently seeded CPU-selector states; native variable blob classes, deterministic ordering, fixed-device byte bounds','command':cmd})
print('HISTORY_SELECTOR_PASS',len(records),flush=True)
