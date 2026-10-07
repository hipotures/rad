"""Single bounded post-smoke repair: replace per-layer stamp launches by existing-kernel observations."""
from common import *
import shutil
v=C/'versions/trace-v1';v.mkdir(parents=True,exist_ok=False)
for name in ['configs/runtime-identity.json','configs/trace-schema.json','patches/phase4.diff','patches/cumulative-from-original.diff']:
 p=v/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/name,p)
shutil.copyfile(BUILD/'strata',W/'builds/trace-v1-strata')
save(v/'repair-decision.json',{'hypothesis':'Six extra stamp kernels per invocation perturb scheduling; first pair decode +18.84%, completion wall +12.41%. CPU scheduling variation may also contribute, so launch overhead is a testable mechanism, not exclusive attribution.','change':'Replace per-layer marker launches with opt-in stores and all-block completion observations inside existing shared-scale and combine kernels. Keep two window stamps and existing timed wait kernels.','budget':'One substantive instrumentation repair, under unchanged clock; at most six new counted v2 requests, no old/new mixed pair.','old_pair_retained':str(R/'results'),'quantitative_v1':'Failed gross symmetric gate; structural diagnostic only'})

def edit(rel,old,new,count=1):
 p=SOURCE/rel;s=p.read_text();assert s.count(old)==count,(rel,old[:65],s.count(old));p.write_text(s.replace(old,new))
h=SOURCE/'include/strata/kernels/q4_trace.hpp';h.write_text('''// Optional recorder inside existing kernels; no new launch or global barrier.
#pragma once
#include <cstdint>
#include <cstddef>
namespace strata::kernels {
struct Q4KernelTrace {unsigned long long *data=nullptr,*count=nullptr;unsigned int* finished=nullptr;size_t cap=0;uint32_t value=0;};
#ifdef __CUDACC__
__device__ inline unsigned long long q4_clock(){unsigned long long t;asm volatile("mov.u64 %0, %%globaltimer;":"=l"(t));return t;}
__device__ inline void q4_kernel_begin(Q4KernelTrace t){if(t.data&&blockIdx.x==0&&blockIdx.y==0&&threadIdx.x==0){auto i=*t.count;if(i<t.cap)t.data[4*i]=q4_clock();}}
__device__ inline void q4_kernel_end(Q4KernelTrace t){if(!t.data)return;__syncthreads();if(threadIdx.x==0){__threadfence();auto n=atomicAdd(t.finished,1u);if(n+1==gridDim.x*gridDim.y){auto i=*t.count;if(i<t.cap){auto* r=t.data+4*i;r[1]=q4_clock();r[2]=t.value;r[3]=i;}*t.count=i+1;*t.finished=0;}}}
#endif
}
''')
sh='include/strata/kernels/shared_expert.hpp';sc='src/kernels/cuda/shared_expert.cu';mh='include/strata/kernels/native_moe.hpp';mc='src/kernels/cuda/native_moe.cu';lh='include/strata/core/layer.hpp';lc='src/core/layer.cpp';vh='include/strata/core/verify.hpp';vc='src/core/verify.cpp'
edit(sh,'#include <cstdint>', '#include <cstdint>\n#include "strata/kernels/q4_trace.hpp"')
edit(sh,'struct NativeSharedWeights {','struct NativeSharedWeights {\n    Q4KernelTrace trace{};')
for kernel in ['scale_rows_kernel','sigmoid_scale_rows_kernel']:
 edit(sc,'__global__ void '+kernel+'(float* __restrict__ out, const float* __restrict__ g, int n) {', '__global__ void '+kernel+'(float* __restrict__ out, const float* __restrict__ g, int n, Q4KernelTrace trace={}) {\n    q4_kernel_begin(trace);')
edit(sc,'    if (i < n) out[(size_t) t * n + i] *= g[t];', '    if (i < n) out[(size_t) t * n + i] *= g[t];\n    q4_kernel_end(trace);')
edit(sc,'        out[(size_t) t * n + i] *= gt;\n    }', '        out[(size_t) t * n + i] *= gt;\n    }\n    q4_kernel_end(trace);')
p=SOURCE/sc;s=p.read_text();a=s.index('void shared_expert_multi(');b=s.index('uint64_t shared_expert_scratch_bytes',a);chunk=s[a:b];assert chunk.count('out, g, (int) n_embd);')==3;p.write_text(s[:a]+chunk.replace('out, g, (int) n_embd);','out, g, (int) n_embd,nw.trace);')+s[b:])
edit(mh,'#include <cstdint>', '#include <cstdint>\n#include "strata/kernels/q4_trace.hpp"')
edit(mh,'int64_t k, void* stream);','int64_t k, void* stream,Q4KernelTrace trace={});')
edit(mh,'int n_tok, void* stream);','int n_tok, void* stream,Q4KernelTrace trace={});')
edit(mc,'int64_t n_embd, int k) {','int64_t n_embd, int k,Q4KernelTrace trace) {\n    q4_kernel_begin(trace);')
edit(mc,'    if (col >= n_embd) return;','    if (col < n_embd) {')
edit(mc,'    output[col] = sum;','    output[col] = sum;\n    }\n    q4_kernel_end(trace);')
edit(mc,'int64_t k, void* stream) {','int64_t k, void* stream,Q4KernelTrace trace) {')
edit(mc,'int n_tok, void* stream) {','int n_tok, void* stream,Q4KernelTrace trace) {')
edit(mc,'n_embd, int(k));','n_embd, int(k),trace);',2)
edit(lh,'#pragma once','#pragma once\n#include "strata/kernels/q4_trace.hpp"')
# Actual function declaration/definition span is narrow; no other MoE call path is changed.
p=SOURCE/lh;s=p.read_text();start=s.index('bool moe_combine_parts(');end=s.index(';',start);chunk=s[start:end];assert 'std::string& err)' in chunk;s=s[:start]+chunk.replace('std::string& err)','std::string& err,strata::kernels::Q4KernelTrace trace={})')+s[end:];p.write_text(s)
p=SOURCE/lc;s=p.read_text();start=s.index('bool moe_combine_parts(');end=s.index('{',start);chunk=s[start:end];assert 'std::string& err)' in chunk;s=s[:start]+chunk.replace('std::string& err)','std::string& err,strata::kernels::Q4KernelTrace trace)')+s[end:];p.write_text(s)
edit(lc,'native_moe_combine(parts, b.weights, b.shared, out, g.n_embd, k, stream);','native_moe_combine(parts, b.weights, b.shared, out, g.n_embd, k, stream,trace);')
# Remove only the six per-layer convenience launches, retaining window/calibration markers.
p=SOURCE/vc;s=p.read_text();lines=s.splitlines(True);removed=[x for x in lines if 'publication_mark(' in x and any(f'publication_mark({i},' in x for i in [3,4,5,6,7])];assert len(removed)==5,removed;s=''.join(x for x in lines if x not in removed);p.write_text(s)
edit(vh,'bool publication_detail_=false,publication_measured_=false;', 'bool publication_detail_=false,publication_measured_=false;\n    strata::kernels::Q4KernelTrace publication_kernel(int kind,uint32_t value);')
edit(vh,'#pragma once','#pragma once\n#include "strata/kernels/q4_trace.hpp"')
edit(vc,'publication_kinds_*8)!=cudaSuccess','(publication_kinds_+2)*8)!=cudaSuccess')
edit(vc,'cudaMemset(publication_counts_,0,publication_kinds_*8);','cudaMemset(publication_counts_,0,(publication_kinds_+2)*8);',2)
edit(vc,'void Verifier::publication_mark(','''strata::kernels::Q4KernelTrace Verifier::publication_kernel(int kind,uint32_t value){if(!publication_detail_)return {};return {publication_data_+kind*publication_cap_*4,publication_counts_+kind,(unsigned int*)(publication_counts_+publication_kinds_+(kind==7)),publication_cap_,value};}
void Verifier::publication_mark(''')
edit(vc,'            NativeSharedWeights nsw;', '            NativeSharedWeights nsw;nsw.trace=publication_kernel(4,(uint32_t)((l-lb_)*G+grp+1));')
edit(vc,'shared_ + tb * N, bo_ + tb * N, N, K, n, cs);','shared_ + tb * N, bo_ + tb * N, N, K, n, cs,publication_kernel(7,ring));')
edit(vc,'bo_ + t * N, cs, err))', 'bo_ + t * N, cs, err,publication_kernel(7,ring)))')
print('REPAIR_APPLIED; retained two window markers, all wait records, shared math readiness and combine kernel bracket',flush=True)
