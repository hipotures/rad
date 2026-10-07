// Targeted parking transitions against the unchanged frozen CPU library.
#include "strata/kernels/cpu/pool.hpp"
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>
namespace cpu=strata::kernels::cpu;
int main() {
 if(!cpu::cpu_features().usable()) return 77;
 constexpr int NJ=32;
 std::vector<unsigned char> blob(cpu::BLOB,0);
 std::vector<float>x(cpu::H,.25f),out(NJ*cpu::H);
 cpu::ActQ act;cpu::act_quant_q8_1(x.data(),cpu::H,act);
 std::vector<cpu::ExpertJob>jobs(NJ);
 for(int i=0;i<NJ;++i){jobs[i].blob=blob.data();jobs[i].act=&act;jobs[i].out=out.data()+i*cpu::H;jobs[i].slot=i;}
 std::atomic<unsigned>beat{0};std::atomic<bool>done{false};
 std::thread dog([&]{unsigned last=0;auto t=std::chrono::steady_clock::now();while(!done){std::this_thread::sleep_for(std::chrono::milliseconds(100));if(beat!=last){last=beat;t=std::chrono::steady_clock::now();}if(std::chrono::steady_clock::now()-t>std::chrono::seconds(10)){std::fprintf(stderr,"HANG at%u\n",last);std::_Exit(3);}}});
 unsigned batches=0,jobs_done=0,gaps=0;
 for(int cycle=0;cycle<8;++cycle){
  cpu::ExpertPool pool(15);
  for(int i=0;i<500;++i){
   // No expert jobs after a long local period; many sleep/wakeup transitions.
   if(i%50==0){for(int k=0;k<64;++k)pool.run(nullptr,0);std::this_thread::sleep_for(std::chrono::milliseconds(25));++gaps;}
   else if(i%3==0){std::this_thread::sleep_for(std::chrono::microseconds((i%2)?120:800));++gaps;}
   int n=(i%5==0)?32:1+(i%4);
   for(int j=0;j<n*cpu::H;++j)out[j]=1234567.f;
   if(i%2)pool.run(jobs.data(),n);else pool.run_split(jobs.data(),n);
   // Immutable zero weights must write every element exactly once to zero.
   for(int j=0;j<n*cpu::H;++j)if(!std::isfinite(out[j])||out[j]!=0){std::fprintf(stderr,"FAILED cycle%d batch%d row%d value%g\n",cycle,i,j,out[j]);std::_Exit(2);}
   ++batches;jobs_done+=n;++beat;
  }
  std::this_thread::sleep_for(std::chrono::milliseconds(25)); // sleeping destructor
 }
 done=true;dog.join();std::printf("PASS batches%u jobs%u gaps%u cycles8 workers15\n",batches,jobs_done,gaps);
}
