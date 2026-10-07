"""Apply narrow query memoization and gated dependency-wait instrumentation to Phase 2."""
from common import *
p=SOURCE/'include/strata/research/q4_oracle.hpp';s=p.read_text()
s=s.replace('#include <limits>','#include <limits>\n#include <ctime>')
s=s.replace(' int current=-1;',''' struct DemandMemo {int from=-1,until=-1,target=-1,uses=0,boundary_reason=0;};
 std::array<DemandMemo,48*512> demand_memo{};
 bool planner_opt=false,decision_audit=false,cache_timing=false;
 uint64_t memo_lookups=0,memo_hits=0,memo_misses=0,memo_lower=0,memo_upper=0,memo_rewind=0,memo_reset=0,memo_time_ns=0,host_cpu_ns=0;
 uint64_t decision_hash=1469598103934665603ull,decision_records=0;
 void decision(int d,int c,int key,int reason,int target=-1,int uses=-1,int victim=-1){if(!decision_audit)return;for(int v:{current,d,c,key,reason,target,uses,victim}){decision_hash^=uint32_t(v);decision_hash*=1099511628211ull;}++decision_records;}
 static uint64_t thread_cpu(){timespec t{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000ull+t.tv_nsec;}
 std::pair<int,int> demand(int l,int expert,int at,int until){
  if(!planner_opt||!causal_policy||incoming_horizon)return {next(l,expert,at+1),count(l,expert,at+1,until)};
  uint64_t started=cache_timing?ns():0;++memo_lookups;auto& m=demand_memo[l*512+expert];
  if(m.from>=0&&at>=m.from&&at<m.until){++memo_hits;if(cache_timing)memo_time_ns+=ns()-started;return {m.target,m.uses};}
  ++memo_misses;if(m.from>=0){if(at<m.from)++memo_rewind;else if(m.boundary_reason==1)++memo_lower;else ++memo_upper;}
  int target=next(l,expert,at+1),uses=count(l,expert,at+1,until);
  // Cache only immutable incoming facts. A lower occurrence leaves when at==target;
  // an upper occurrence enters when at==next_after_upper-768. Inclusive upper bound.
  const auto& v=future[l*512+expert];auto hi=std::upper_bound(v.begin(),v.end(),std::make_pair(until,INT_MAX));
  int lower=target<0?INT_MAX:target,upper=hi==v.end()?INT_MAX:hi->first-768;
  int stop=std::min(lower,upper);require(stop>at,"invalid memo boundary");
  m={at,stop,target,uses,lower<=upper?1:2};if(cache_timing)memo_time_ns+=ns()-started;return {target,uses};
 }
 int current=-1;''')
s=s.replace('Q4Oracle(){leases.fill(-1);','Q4Oracle(){const char* opt=std::getenv("STRATA_Q4_PLANNER_OPT");planner_opt=opt&&opt[0]==\'1\';const char* da=std::getenv("STRATA_Q4_DECISION_AUDIT");decision_audit=da&&da[0]==\'1\';const char* ct=std::getenv("STRATA_Q4_CACHE_TIMING");cache_timing=ct&&ct[0]==\'1\';leases.fill(-1);')
s=s.replace('void prepare(){if(!configured','void prepare(){for(auto& m:demand_memo)m={};++memo_reset;if(!configured')
s=s.replace('void begin(){if(!configured||!q4_tape.active)return;','void begin(){if(!configured||!q4_tape.active)return;for(auto& m:demand_memo)m={};memo_lookups=memo_hits=memo_misses=memo_lower=memo_upper=memo_rewind=memo_time_ns=host_cpu_ns=0;memo_reset=1;decision_hash=1469598103934665603ull;decision_records=0;')
old='int target=next(l,expert,current+1);if(target<0)continue;int utility_end=std::min((int)q4_tape.windows.size()*48-1,current+768);int uses=causal_policy?count(l,expert,current+1,utility_end):0;'
new='int utility_end=std::min((int)q4_tape.windows.size()*48-1,current+768);int target,uses=0;if(causal_policy){auto value=demand(l,expert,current,utility_end);target=value.first;uses=value.second;}else target=next(l,expert,current+1);if(target<0){decision(w.dev,w.cls,key,1);continue;}'
assert old in s;s=s.replace(old,new)
s=s.replace('++cost_veto;++scorer.rejections;continue;','++cost_veto;++scorer.rejections;decision(w.dev,w.cls,key,2,target,uses);continue;')
s=s.replace('int v=victim(l,expert,current);if(v<0)continue;','int v=victim(l,expert,current);if(v<0){decision(w.dev,w.cls,key,3,target,uses);continue;}')
s=s.replace('++risk_veto;continue;','++risk_veto;decision(w.dev,w.cls,key,4,target,uses,v);continue;')
s=s.replace('++victim_cost_veto;++scorer.rejections;continue;','++victim_cost_veto;++scorer.rejections;decision(w.dev,w.cls,key,5,target,uses,v);continue;')
s=s.replace('double utility=strategy?', 'decision(w.dev,w.cls,key,6,target,uses,v);double utility=strategy?')
s=s.replace('if(bestl>=0)issue(w,bestl,beste,besttarget);','decision(w.dev,w.cls,bestl<0?-1:bestl*512+beste,bestl<0?7:8,besttarget);if(bestl>=0)issue(w,bestl,beste,besttarget);')
s=s.replace('void plan(Worker& w){if(w.state.load()!=0)return;','void plan(Worker& w){if(w.state.load()!=0){decision(w.dev,w.cls,-1,9);return;}')
s=s.replace('protected_count(w.dev,w.cls)>=protection_cap){++capacity_veto;return;}int lead','protected_count(w.dev,w.cls)>=protection_cap){++capacity_veto;decision(w.dev,w.cls,-1,10);return;}int lead')
s=s.replace('current=(int)q4_tape.index*48+l;uint64_t t=ns();','current=(int)q4_tape.index*48+l;uint64_t cpu=thread_cpu();uint64_t t=ns();')
s=s.replace('planner_ns+=ns()-t;}\n void observe_plan','planner_ns+=ns()-t;host_cpu_ns+=thread_cpu()-cpu;}\n void observe_plan')
s=s.replace('  active=false;tracked=false;','''  std::fprintf(stderr,"Q4_PLANNER_END optimized=%d lookups=%llu hits=%llu misses=%llu invalid_lower=%llu invalid_upper=%llu invalid_rewind=%llu reset=%llu avoided_queries=%llu retained_evaluations=%llu memo_bytes=%zu maintenance_ms=%.3f maintenance_timed=%d host_cpu_ms=%.3f decision_audit=%d decision_records=%llu decision_hash=%016llx opportunities=%llu\\n",planner_opt,(unsigned long long)memo_lookups,(unsigned long long)memo_hits,(unsigned long long)memo_misses,(unsigned long long)memo_lower,(unsigned long long)memo_upper,(unsigned long long)memo_rewind,(unsigned long long)memo_reset,(unsigned long long)(2*memo_hits),(unsigned long long)(planner_opt?memo_misses:opportunities),sizeof(demand_memo),memo_time_ns/1e6,cache_timing,host_cpu_ns/1e6,decision_audit,(unsigned long long)decision_records,(unsigned long long)decision_hash,(unsigned long long)opportunities);
  active=false;tracked=false;''')
p.write_text(s)
# Gated one-thread wait kernel uses GPU globaltimer; same launch, no per-event disk I/O.
p=SOURCE/'include/strata/kernels/verify_kernels.hpp';s=p.read_text();s=s.replace('void wait_flag_ge(const uint32_t* flag, uint32_t value, void* stream);','void wait_flag_ge(const uint32_t* flag, uint32_t value, void* stream);\nvoid wait_flag_ge_timed(const uint32_t* flag, uint32_t value, unsigned long long* stats, void* stream);');p.write_text(s)
p=SOURCE/'src/kernels/cuda/verify_kernels.cu';s=p.read_text();anchor='void wait_flag_ge(const uint32_t* flag, uint32_t value, void* stream) {'
addition='''namespace {
__device__ unsigned long long wait_clock(){unsigned long long v;asm volatile("mov.u64 %0, %%globaltimer;":"=l"(v));return v;}
__global__ void wait_flag_ge_timed_kernel(const volatile uint32_t* flag,uint32_t value,unsigned long long* stats){
    unsigned long long begin=wait_clock();while(*flag<value)strata_spin_pause();unsigned long long end=wait_clock();
    __threadfence_system();stats[0]+=end-begin;stats[1]+=1;
}
}
void wait_flag_ge_timed(const uint32_t* flag,uint32_t value,unsigned long long* stats,void* stream){
    wait_flag_ge_timed_kernel<<<1,1,0,(cudaStream_t)stream>>>(flag,value,stats);check("wait_flag_ge_timed");
}
'''
assert anchor in s;s=s.replace(anchor,addition+anchor);p.write_text(s)
p=SOURCE/'include/strata/core/verify.hpp';s=p.read_text().replace('std::string profile_report();','std::string profile_report();\n    void wait_report();');s=s.replace('bool prof_on_ = false;','unsigned long long* wait_stats_ = nullptr; // Six counters, request-scoped, opt-in.\n    bool prof_on_ = false;');p.write_text(s)
p=SOURCE/'src/core/verify.cpp';s=p.read_text().replace('if (arena_) cudaFree(arena_);','if (wait_stats_) cudaFree(wait_stats_);\n    if (arena_) cudaFree(arena_);');s=s.replace('    prof_on_ = std::getenv("STRATA_VERIFY_PROFILE") != nullptr;','''    const char* wp=std::getenv("STRATA_Q4_WAIT_PROFILE");
    if(wp&&wp[0]=='1') {if(cudaMalloc((void**)&wait_stats_,6*sizeof(unsigned long long))!=cudaSuccess){err="wait stats allocation";return false;}cudaMemset(wait_stats_,0,6*sizeof(unsigned long long));}
    prof_on_ = std::getenv("STRATA_VERIFY_PROFILE") != nullptr;''')
for flag,offset in [('m_flagA_',0),('m_flagB_',2),('m_flag_',4)]:
 old=f'wait_flag_ge({flag}, ring, cs);';new=f'if(wait_stats_)wait_flag_ge_timed({flag},ring,wait_stats_+{offset},cs);else wait_flag_ge({flag}, ring, cs);';assert old in s;s=s.replace(old,new)
s=s.replace('std::string Verifier::profile_report() {','''void Verifier::wait_report(){
    if(!wait_stats_)return;const OnDevice on_device(device_);unsigned long long s[6]{};
    // Request completion has already waited for final commit; no routed-event sync.
    cudaMemcpy(s,wait_stats_,sizeof(s),cudaMemcpyDeviceToHost);
    std::fprintf(stderr,"Q4_WAIT_END device=%d plan_ns=%llu plan_count=%llu mapped_ns=%llu mapped_count=%llu cpu_ns=%llu cpu_count=%llu metadata_bytes=48\\n",device_,s[0],s[1],s[2],s[3],s[4],s[5]);
    cudaMemsetAsync(wait_stats_,0,sizeof(s),cs_);
}
std::string Verifier::profile_report() {''');p.write_text(s)
p=SOURCE/'src/program/generate.cpp';s=p.read_text().replace('strata::research::q4_tape.finish(produced_n,cancelled);','strata::research::q4_tape.finish(produced_n,cancelled);\n            ver.wait_report();for(auto& stage:stages)stage->ver.wait_report();');p.write_text(s)
ledger('Implementation applied',hypothesis='Immutable incoming query reuse until exact sliding-window change; dependent flag wait measured separately',files=6)
