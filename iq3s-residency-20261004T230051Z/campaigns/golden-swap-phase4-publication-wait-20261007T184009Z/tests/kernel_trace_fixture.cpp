#include "strata/kernels/native_moe.hpp"
#include "strata/kernels/shared_expert.hpp"
#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <vector>
#include <random>
#include <cstring>
#include <iostream>
using namespace strata::kernels;
void ok(bool v){if(!v)throw std::runtime_error("kernel trace parity failed");}
void ck(cudaError_t e){if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));}
template<class T>T* alloc(size_t n){T* p;ck(cudaMalloc(&p,n*sizeof(T)));return p;}
int main(){std::mt19937 rng(730041);for(int dev=0;dev<2;++dev){ck(cudaSetDevice(dev));cudaStream_t stream;ck(cudaStreamCreateWithFlags(&stream,cudaStreamNonBlocking));
 for(int T:{1,2,4}){const int N=3072,K=10,F=640;std::vector<float> parts(T*K*N),weights(T*K),shared(T*N),x(T*N);for(auto& v:parts)v=(int(rng()%100)-50)*.01f;for(auto& v:weights)v=(rng()%100)*.001f;for(auto& v:shared)v=(int(rng()%100)-50)*.01f;for(auto& v:x)v=(int(rng()%100)-50)*.01f;
 auto *dp=alloc<float>(parts.size()),*dw=alloc<float>(weights.size()),*ds=alloc<float>(shared.size()),*dx=alloc<float>(x.size()),*out=alloc<float>(shared.size());ck(cudaMemcpy(dp,parts.data(),parts.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(dw,weights.data(),weights.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(ds,shared.data(),shared.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(dx,x.data(),x.size()*4,cudaMemcpyHostToDevice));auto *data=alloc<unsigned long long>(8),*count=alloc<unsigned long long>(1);auto *finished=alloc<unsigned int>(1);Q4KernelTrace trace{data,count,finished,2,7};ck(cudaMemset(count,0,8));ck(cudaMemset(finished,0,4));std::vector<float> before(T*N),after(T*N);
 native_moe_combine_multi(dp,dw,ds,out,N,K,T,stream);ck(cudaStreamSynchronize(stream));ck(cudaMemcpy(before.data(),out,T*N*4,cudaMemcpyDeviceToHost));native_moe_combine_multi(dp,dw,ds,out,N,K,T,stream,trace);ck(cudaStreamSynchronize(stream));ck(cudaMemcpy(after.data(),out,T*N*4,cudaMemcpyDeviceToHost));ok(!memcmp(before.data(),after.data(),T*N*4));unsigned long long n,r[4];ck(cudaMemcpy(&n,count,8,cudaMemcpyDeviceToHost));ck(cudaMemcpy(r,data,32,cudaMemcpyDeviceToHost));ok(n==1&&r[1]>=r[0]&&r[2]==7);
 std::vector<unsigned char> q(F*N/32*34);for(size_t b=0;b<q.size();b+=34){uint16_t scale=__half_as_ushort(__float2half(.03f));memcpy(q.data()+b,&scale,2);for(int j=0;j<32;++j)q[b+2+j]=(signed char)(int(rng()%25)-12);}auto *dgate=alloc<unsigned char>(q.size()),*dup=alloc<unsigned char>(q.size()),*ddown=alloc<unsigned char>(q.size());for(auto* p:{dgate,dup,ddown})ck(cudaMemcpy(p,q.data(),q.size(),cudaMemcpyHostToDevice));std::vector<uint16_t> gi(N,0x3b80);auto* dgi=alloc<uint16_t>(N);ck(cudaMemcpy(dgi,gi.data(),N*2,cudaMemcpyHostToDevice));auto *gate=alloc<float>(T*F),*up=alloc<float>(T*F),*g=alloc<float>(T);auto* q81=alloc<unsigned char>(T*N/32*36);NativeSharedWeights nw;nw.gate_type=nw.up_type=nw.down_type=8;nw.gate_data=dgate;nw.up_data=dup;nw.down_data=ddown;nw.q8_1=q81;shared_expert_set_native_bf16(true);
 shared_expert_multi(T,dx,nullptr,nw,dgi,gate,up,g,out,N,F,stream);ck(cudaStreamSynchronize(stream));ck(cudaMemcpy(before.data(),out,T*N*4,cudaMemcpyDeviceToHost));ck(cudaMemset(count,0,8));nw.trace=trace;
 cudaGraph_t graph;cudaGraphExec_t executable;ck(cudaStreamBeginCapture(stream,cudaStreamCaptureModeGlobal));shared_expert_multi(T,dx,nullptr,nw,dgi,gate,up,g,out,N,F,stream);ck(cudaStreamEndCapture(stream,&graph));ck(cudaGraphInstantiate(&executable,graph,0));ck(cudaGraphLaunch(executable,stream));ck(cudaGraphLaunch(executable,stream));ck(cudaStreamSynchronize(stream));ck(cudaMemcpy(after.data(),out,T*N*4,cudaMemcpyDeviceToHost));ok(!memcmp(before.data(),after.data(),T*N*4));ck(cudaMemcpy(&n,count,8,cudaMemcpyDeviceToHost));ok(n==2);ck(cudaMemcpy(r,data+4,32,cudaMemcpyDeviceToHost));ok(r[3]==1&&r[2]==7&&r[1]>=r[0]);
 cudaGraphExecDestroy(executable);cudaGraphDestroy(graph);for(void* p:{(void*)dp,(void*)dw,(void*)ds,(void*)dx,(void*)out,(void*)data,(void*)count,(void*)finished,(void*)dgate,(void*)dup,(void*)ddown,(void*)dgi,(void*)gate,(void*)up,(void*)g,(void*)q81})cudaFree(p);std::cout<<"PASS device="<<dev<<" T="<<T<<" combine/shared bitwise OFF/ON and graph indexing\n";
 }cudaStreamDestroy(stream);}}
