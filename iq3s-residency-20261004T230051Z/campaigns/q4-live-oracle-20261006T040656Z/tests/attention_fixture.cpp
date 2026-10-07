#include "strata/research/q4_tape_gpu.hpp"
#include <cuda_runtime.h>
#include <cstdio>
#include <vector>
#include <cstring>
#include <stdexcept>
using namespace strata::research;
void ck(cudaError_t s){if(s!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(s));}
int main(){for(int d=0;d<2;++d){ck(cudaSetDevice(d));TapePage *p,*dp;ck(cudaHostAlloc(&p,sizeof(TapePage),cudaHostAllocMapped));ck(cudaHostGetDevicePointer(&dp,p,0));int32_t *sel,*steps;ck(cudaMalloc(&sel,4*2051*4));ck(cudaMalloc(&steps,16*4));std::vector<int32_t>x(4*2051),st(16),y(x.size());for(int t=0;t<4;++t){st[t*4]=30000+t;st[t*4+1]=30001+t;st[t*4+2]=(30001+t)/4;st[t*4+3]=2051;for(int j=0;j<2051;++j)x[t*2051+j]=t*3000+j;}
ck(cudaMemcpy(steps,st.data(),64,cudaMemcpyHostToDevice));
for(int T=1;T<=4;++T)for(int qi=0;qi<12;++qi){std::memset(p,0,sizeof(*p));p->mode=1;ck(cudaMemcpy(sel,x.data(),x.size()*4,cudaMemcpyHostToDevice));tape_attention(dp,qi,0,T,2051,sel,steps,nullptr);ck(cudaDeviceSynchronize());if(p->qsa_seen[qi]!=1||std::memcmp(p->routes.qsa[qi],x.data(),T*2051*4))throw std::runtime_error("record selection differs");p->mode=2;p->qsa_seen[qi]=0;ck(cudaMemset(sel,0,x.size()*4));tape_attention(dp,qi,0,T,2051,sel,steps,nullptr);ck(cudaDeviceSynchronize());ck(cudaMemcpy(y.data(),sel,x.size()*4,cudaMemcpyDeviceToHost));if(p->qsa_seen[qi]!=1||std::memcmp(y.data(),x.data(),T*2051*4)||!p->qsa_disagreements[qi])throw std::runtime_error("replay selection differs");p->mode=0;ck(cudaMemset(sel,0,x.size()*4));tape_attention(dp,qi,0,T,2051,sel,steps,nullptr);ck(cudaDeviceSynchronize());ck(cudaMemcpy(y.data(),sel,x.size()*4,cudaMemcpyDeviceToHost));for(int j=0;j<T*2051;++j)if(y[j])throw std::runtime_error("OFF changes native selection");}
ck(cudaFree(steps));ck(cudaFree(sel));ck(cudaFreeHost(p));std::printf("PASS GPU%d: T1..4, all12QSA selections, record/replay/native OFF, mismatch observation\n",d);}return 0;}
