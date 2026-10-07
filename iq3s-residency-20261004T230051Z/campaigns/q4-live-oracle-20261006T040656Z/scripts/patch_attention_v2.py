"""Versioned full-work repair: freeze QSA block selection and native adaptation phase."""
from pathlib import Path
import subprocess
C=Path(__file__).resolve().parents[1];s=C/'src/oracle-v2'
subprocess.run(['git','clone','--no-hardlinks',str(C/'src/oracle-v1'),str(s)],check=True,timeout=60)
(s/'.venv').symlink_to(C.parents[1]/'src/control/.venv',target_is_directory=True)
def edit(f,a,b,n=1):
 p=s/f;t=p.read_text();assert t.count(a)>=n,(f,a);p.write_text(t.replace(a,b,n))
f='include/strata/research/q4_tape_gpu.hpp'
edit(f,'float probs[3]; };','float probs[3]; int32_t qsa[12][4*2051]; };')
edit(f,'int32_t nonfinite;','int32_t nonfinite; int32_t qsa_seen[12],qsa_disagreements[12];')
edit(f,'void tape_route(','void tape_attention(TapePage* page,int qi,int row_offset,int n,int cap,int32_t* selection,const int32_t* steps,void* stream);\nvoid tape_route(')
f='include/strata/research/q4_tape.hpp'
edit(f,'native_outputs[4];','native_outputs[4],qsa_seen[12],qsa_disagreements[12];')
edit(f,'version=1,','version=2,')
edit(f,'work_hash=0; };','work_hash=0; int64_t initial_rounds=0; };')
edit(f,'header.version==1','header.version==2')
edit(f,'void graph_mtp(int','void graph_attention(int d,int qi,int off,int n,int cap,int32_t* sel,const int32_t* step,void* stream){require(qi>=0&&qi<12&&cap==2051,"QSA geometry differs");if(enabled)tape_attention(mapped[d],qi,off,n,cap,sel,step,stream);}\n void graph_mtp(int')
edit(f,'const float* heat){if(!enabled)','const float* heat,int64_t rounds){if(!enabled)')
edit(f,'if(replaying){require(ids.size()','if(replaying){require(rounds==header.initial_rounds,"native adaptation phase differs");require(ids.size()')
edit(f,'else{header.output_budget=budget;','else{header.initial_rounds=rounds;header.output_budget=budget;')
edit(f,'require(!nonfinite,"nonfinite route/activation");','for(int qi=0;qi<12;++qi){int d=qi<6?0:1;auto* p=host[d];obs.qsa_seen[qi]=p->qsa_seen[qi];obs.qsa_disagreements[qi]=p->qsa_disagreements[qi];require(p->qsa_seen[qi]==1,"QSA invocation differs");if(!replaying)std::memcpy(current.routes.qsa[qi],p->routes.qsa[qi],sizeof(current.routes.qsa[qi]));}require(!nonfinite,"nonfinite route/activation");')
f='src/core/verify.cpp'
edit(f,'                stamp(l, 11, grp);','                strata::research::q4_tape.graph_attention(device_,(int)qi,tb,n,(int)cap_,sel_+(size_t)tb*cap_,step_+tb*kStepCount,cs);\n                stamp(l, 11, grp);')
f='src/program/generate.cpp'
edit(f,'q4_tape.begin(ids,max_new,host_res.data(),drive.d.usage.data());','q4_tape.begin(ids,max_new,host_res.data(),drive.d.usage.data(),rounds);')
p=s/'src/kernels/cuda/elementwise.cu';p.write_text(p.read_text()+r'''
namespace strata::research {
__global__ void tape_attention_kernel(TapePage* p,int qi,int off,int n,int cap,int32_t* sel,const int32_t* steps){
 int mode=((volatile int32_t*)&p->mode)[0];if(!mode)return;
 if(threadIdx.x==0)atomicAdd(p->qsa_seen+qi,1);
 for(int j=threadIdx.x;j<n*cap;j+=blockDim.x){int row=j/cap,i=j%cap;int width=steps[row*4+3];int32_t* saved=p->routes.qsa[qi]+(off+row)*cap+i;
  if(i<width){if(mode==1)*saved=sel[j];else{if(sel[j]!=*saved)atomicAdd(p->qsa_disagreements+qi,1);sel[j]=*saved;}}
 }
 __threadfence_system();
}
void tape_attention(TapePage* p,int qi,int off,int n,int cap,int32_t* sel,const int32_t* steps,void* stream){tape_attention_kernel<<<1,256,0,(cudaStream_t)stream>>>(p,qi,off,n,cap,sel,steps);}
}
''')
print('PATCH_ATTENTION_V2',s)
