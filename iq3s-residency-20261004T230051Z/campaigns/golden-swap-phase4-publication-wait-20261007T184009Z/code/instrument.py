#!/usr/bin/env python3
"""Apply the bounded, buffered Phase 4 recorder to the verified parent source."""
from common import *

def edit(rel, old, new, count=1):
 p=SOURCE/rel;s=p.read_text();assert s.count(old)==count,(rel,old[:90],s.count(old));p.write_text(s.replace(old,new))
o='include/strata/research/q4_oracle.hpp'
edit(o,'struct Q4Oracle {','''// All producer/worker observations use one CLOCK_MONOTONIC domain.
struct PublicationTrace {uint64_t generation,event,device,cls,validation_begin,command_available,wait_begin,wait_end,cpu_begin,cpu_end,commit_end,worker_observed,metadata_submit,cuda_observed,ack_state,notify_unlock_return;};
struct ProducerTrace {uint64_t event,hook_begin,publications_end,hook_end,flag_before,flag_after,plan_end,cpu_end;};
struct Q4Oracle {
 static constexpr size_t pub_trace_cap=65536,host_trace_cap=65536;
 bool publication_trace=[](){const char* p=std::getenv("STRATA_Q4_PUBLICATION_TRACE");return p&&p[0]=='1';}();
 std::vector<PublicationTrace> publication_records;
 std::vector<ProducerTrace> producer_records;
 uint64_t publication_trace_overflow=0;
 PublicationTrace* pt(int index){if(!publication_trace)return nullptr;if(index<0||size_t(index)>=pub_trace_cap){++publication_trace_overflow;return nullptr;}return &publication_records[index];}
 ProducerTrace* ht(){if(!publication_trace||!tracked||!q4_tape.active)return nullptr;if(current<0||size_t(current)>=host_trace_cap){++publication_trace_overflow;return nullptr;}return &producer_records[current];}
 void flag_a(bool after){auto* h=ht();if(h){if(after)h->flag_after=ns();else h->flag_before=ns();}}
''')
edit(o,'static void publish_state(Worker& w,int s){std::lock_guard<std::mutex> lk(w.mu);w.state.store(s,std::memory_order_release);w.cv.notify_all();}', '''static void publish_state(Worker& w,int s,PublicationTrace* p=nullptr){{std::lock_guard<std::mutex> lk(w.mu);w.state.store(s,std::memory_order_release);if(p)p->ack_state=ns();w.cv.notify_all();}if(p)p->notify_unlock_return=ns();}''')
edit(o,'else if(command==4){w.metadata[0]=-1;', 'else if(command==4){int generation=w.index;auto* p=pt(generation);if(p)p->worker_observed=ns();w.metadata[0]=-1;')
edit(o,'w.metadata[1]=w.destination;ck(cudaMemcpyAsync(dres[d]', 'w.metadata[1]=w.destination;if(p)p->metadata_submit=ns();ck(cudaMemcpyAsync(dres[d]')
edit(o,'ck(cudaEventSynchronize(w.done));publish_state(w,5);', 'ck(cudaEventSynchronize(w.done));if(p)p->cuda_observed=ns();publish_state(w,5,p);')
edit(o,'events.clear();lifetimes.clear();', 'publication_records.assign(pub_trace_cap,{});producer_records.assign(host_trace_cap,{});publication_trace_overflow=0;events.clear();lifetimes.clear();')
edit(o,'auto& e=events[w.index];if(transaction_control', 'auto& e=events[w.index];auto* trace=pt(w.index);if(trace){trace->generation=w.index;trace->event=current;trace->device=w.dev;trace->cls=w.cls;trace->validation_begin=ns();}if(transaction_control')
edit(o,'uint64_t t=ns();{std::unique_lock<std::mutex> lk(w.mu);w.victim=v;', 'uint64_t t=ns();if(trace){trace->wait_begin=ns();trace->cpu_begin=thread_cpu();}{std::unique_lock<std::mutex> lk(w.mu);w.victim=v;if(trace)trace->command_available=ns();')
edit(o,'}publication_ns+=ns()-t;res[w.layer', '}if(trace){trace->cpu_end=thread_cpu();trace->wait_end=ns();}publication_ns+=ns()-t;res[w.layer')
edit(o,'w.state.store(0,std::memory_order_release);}\n void issue', 'w.state.store(0,std::memory_order_release);if(trace)trace->commit_end=ns();}\n void issue')
edit(o,'uint64_t t=ns();if(active){advance_lifetimes(current);', 'uint64_t t=ns();auto* host_trace=ht();if(host_trace){host_trace->event=current;host_trace->hook_begin=t;}if(active){advance_lifetimes(current);')
edit(o,'publish(w);}for(int j=0;j<n;++j)', 'publish(w);}if(host_trace)host_trace->publications_end=ns();for(int j=0;j<n;++j)')
edit(o,'host_cpu_ns+=thread_cpu()-cpu;}', 'host_cpu_ns+=thread_cpu()-cpu;if(host_trace)host_trace->hook_end=ns();}')
edit(o,'layers.push_back(a);if(active)', 'layers.push_back(a);if(auto* h=ht())h->plan_end=a.plan_end;if(active)')
edit(o,'layers.back().cpu_end=ns();if(causal_policy)', 'layers.back().cpu_end=ns();if(auto* h=ht())h->cpu_end=layers.back().cpu_end;if(causal_policy)')
edit(o,'write("-lifecycle.bin",lifetimes);}', '''write("-lifecycle.bin",lifetimes);if(publication_trace){publication_records.resize(std::min(events.size(),pub_trace_cap));producer_records.resize(std::min(layers.size(),host_trace_cap));write("-publication-trace.bin",publication_records);write("-producer-trace.bin",producer_records);}}
  std::fprintf(stderr,"Q4_PUBLICATION_TRACE enabled=%d overflow=%llu host_alloc_bytes=%zu pub_cap=%zu producer_cap=%zu\\n",publication_trace,(unsigned long long)publication_trace_overflow,pub_trace_cap*sizeof(PublicationTrace)+host_trace_cap*sizeof(ProducerTrace),pub_trace_cap,host_trace_cap);''')
vh='include/strata/core/verify.hpp';vk='include/strata/kernels/verify_kernels.hpp';cu='src/kernels/cuda/verify_kernels.cu';vc='src/core/verify.cpp'
edit(vh,'    void wait_report();', '    void wait_report();\n    void publication_trace_begin();\n    void publication_trace_calibrate(int boundary);')
edit(vh,'    unsigned long long* wait_stats_ = nullptr;', '''    static constexpr size_t publication_cap_=20000,publication_kinds_=9;
    unsigned long long *publication_data_=nullptr,*publication_counts_=nullptr;
    bool publication_detail_=false;
    uint64_t publication_cal_host_[4]{};
    void publication_mark(int kind,uint32_t value,void* stream);
    unsigned long long* wait_stats_ = nullptr;''')
edit(vk,'unsigned long long* stats, void* stream);', 'unsigned long long* stats, void* stream, unsigned long long* records=nullptr, unsigned long long* count=nullptr, size_t cap=0);\nvoid q4_trace_mark(unsigned long long* records, unsigned long long* count, size_t cap, uint32_t value, void* stream);')
edit(cu,'uint32_t value,unsigned long long* stats){', 'uint32_t value,unsigned long long* stats,unsigned long long* records,unsigned long long* count,size_t cap){')
edit(cu,'__threadfence_system();stats[0]+=end-begin;stats[1]+=1;', '''__threadfence_system();stats[0]+=end-begin;stats[1]+=1;
    if(records){unsigned long long i=(*count)++;if(i<cap){auto* r=records+4*i;r[0]=begin;r[1]=end;r[2]=value;r[3]=i;}}''')
edit(cu,'void wait_flag_ge_timed(const uint32_t* flag,uint32_t value,unsigned long long* stats,void* stream){\n    wait_flag_ge_timed_kernel<<<1,1,0,(cudaStream_t)stream>>>(flag,value,stats);check("wait_flag_ge_timed");\n}', '''void wait_flag_ge_timed(const uint32_t* flag,uint32_t value,unsigned long long* stats,void* stream,unsigned long long* records,unsigned long long* count,size_t cap){
    wait_flag_ge_timed_kernel<<<1,1,0,(cudaStream_t)stream>>>(flag,value,stats,records,count,cap);check("wait_flag_ge_timed");
}
namespace {
__global__ void q4_trace_mark_kernel(unsigned long long* records,unsigned long long* count,size_t cap,uint32_t value){auto t=wait_clock();auto i=(*count)++;if(i<cap){auto* r=records+4*i;r[0]=t;r[1]=t;r[2]=value;r[3]=i;}}
}
void q4_trace_mark(unsigned long long* records,unsigned long long* count,size_t cap,uint32_t value,void* stream){q4_trace_mark_kernel<<<1,1,0,(cudaStream_t)stream>>>(records,count,cap,value);check("q4_trace_mark");}
''')
edit(vc,'    if (wait_stats_) cudaFree(wait_stats_);', '    if (wait_stats_) cudaFree(wait_stats_);\n    if(publication_data_)cudaFree(publication_data_);if(publication_counts_)cudaFree(publication_counts_);')
edit(vc,'    prof_on_ = std::getenv("STRATA_VERIFY_PROFILE") != nullptr;', '''    const char* publication_switch=std::getenv("STRATA_Q4_PUBLICATION_TRACE");
    if(publication_switch){publication_detail_=publication_switch[0]=='1';if(cudaMalloc((void**)&publication_data_,publication_kinds_*publication_cap_*4*8)!=cudaSuccess||cudaMalloc((void**)&publication_counts_,publication_kinds_*8)!=cudaSuccess){err="publication trace allocation";return false;}cudaMemset(publication_counts_,0,publication_kinds_*8);}
    prof_on_ = std::getenv("STRATA_VERIFY_PROFILE") != nullptr;''')
edit(vc,'wait_flag_ge_timed(m_flagA_,ring,wait_stats_+0,cs)', 'wait_flag_ge_timed(m_flagA_,ring,wait_stats_+0,cs,publication_detail_?publication_data_:nullptr,publication_counts_,publication_cap_)')
edit(vc,'wait_flag_ge_timed(m_flagB_,ring,wait_stats_+2,cs)', 'wait_flag_ge_timed(m_flagB_,ring,wait_stats_+2,cs,publication_detail_?publication_data_+publication_cap_*4:nullptr,publication_counts_?publication_counts_+1:nullptr,publication_cap_)')
edit(vc,'wait_flag_ge_timed(m_flag_,ring,wait_stats_+4,cs)', 'wait_flag_ge_timed(m_flag_,ring,wait_stats_+4,cs,publication_detail_?publication_data_+publication_cap_*8:nullptr,publication_counts_?publication_counts_+2:nullptr,publication_cap_)')
edit(vc,'        // the window\'s rows routed in 2 launches', '        if(publication_detail_)publication_mark(3,(uint32_t)((l-lb_)*G+grp+1),sh_stream);\n        // the window\'s rows routed in 2 launches')
edit(vc,'            if (sh_fork) cudaEventRecord(ev_join_, sh_cs_);', '            if(publication_detail_)publication_mark(4,(uint32_t)((l-lb_)*G+grp+1),sh_stream);\n            if (sh_fork) cudaEventRecord(ev_join_, sh_cs_);')
edit(vc,'        if (!prof_on_ && sh_cs_ != nullptr && ev_fork_ != nullptr && ev_join_ != nullptr) {\n            cudaStreamWaitEvent(cs, ev_join_, 0);\n        }', '''        if(publication_detail_)publication_mark(5,ring,cs);
        if (!prof_on_ && sh_cs_ != nullptr && ev_fork_ != nullptr && ev_join_ != nullptr) {
            cudaStreamWaitEvent(cs, ev_join_, 0);
        }
        if(publication_detail_)publication_mark(6,ring,cs);''')
edit(vc,'        stamp(l, 24, grp);', '        stamp(l, 24, grp);\n        if(publication_detail_)publication_mark(7,ring,cs);')
edit(vc,'void Verifier::wait_report(){', '''void Verifier::publication_mark(int kind,uint32_t value,void* stream){if(!publication_data_)return;q4_trace_mark(publication_data_+kind*publication_cap_*4,publication_counts_+kind,publication_cap_,value,stream);}
void Verifier::publication_trace_calibrate(int boundary){
 if(!publication_data_)return;const OnDevice on_device(device_);
 publication_cal_host_[2*boundary]=strata::research::Q4Tape::ns();
 publication_mark(8,uint32_t(boundary),cs_);
 unsigned long long sample[4]{};cudaMemcpy(sample,publication_data_+8*publication_cap_*4+boundary*4,sizeof(sample),cudaMemcpyDeviceToHost);
 publication_cal_host_[2*boundary+1]=strata::research::Q4Tape::ns();
}
void Verifier::publication_trace_begin(){if(!publication_data_)return;const OnDevice on_device(device_);cudaMemset(publication_counts_,0,publication_kinds_*8);publication_trace_calibrate(0);}
void Verifier::wait_report(){''')
edit(vc,'    cudaMemsetAsync(wait_stats_,0,sizeof(s),cs_);', '''    if(publication_data_){
      publication_trace_calibrate(1);unsigned long long counts[publication_kinds_]{};cudaMemcpy(counts,publication_counts_,sizeof(counts),cudaMemcpyDeviceToHost);
      const char* prefix=std::getenv("STRATA_Q4_ORACLE_LOG");
      if(prefix&&strata::research::q4_tape.replaying){std::string path=std::string(prefix)+"-gpu"+std::to_string(device_)+"-trace.bin";FILE* f=std::fopen(path.c_str(),"wbx");strata::research::Q4Tape::require(f,"GPU trace exists");
       uint64_t header[18]={1,uint64_t(device_),publication_cap_,publication_kinds_,publication_detail_};for(int i=0;i<9;++i)header[5+i]=counts[i];for(int i=0;i<4;++i)header[14+i]=publication_cal_host_[i];strata::research::Q4Tape::io(f,header,18,true);
       std::vector<unsigned long long> buffer(publication_cap_*4);for(int i=0;i<9;++i){size_t n=std::min<size_t>(counts[i],publication_cap_);if(n)cudaMemcpy(buffer.data(),publication_data_+i*publication_cap_*4,n*32,cudaMemcpyDeviceToHost);strata::research::Q4Tape::io(f,buffer.data(),n*4,true);}std::fclose(f);
      }
      std::fprintf(stderr,"Q4_GPU_TRACE device=%d detail=%d alloc_bytes=%zu A=%llu B=%llu CPU=%llu shared_begin=%llu shared_end=%llu prejoin=%llu postjoin=%llu layer_end=%llu calibration=%llu overflow=%d\\n",device_,publication_detail_,publication_kinds_*publication_cap_*32+publication_kinds_*8,counts[0],counts[1],counts[2],counts[3],counts[4],counts[5],counts[6],counts[7],counts[8],std::any_of(counts,counts+9,[](auto v){return v>publication_cap_;}));
    }
    cudaMemsetAsync(wait_stats_,0,sizeof(s),cs_);''')
edit(vc,'    _mm_sfence();\n    *(volatile uint32_t*) v->h_flagA_ = v->cur_layer_ + 1;', '    strata::research::q4_oracle.flag_a(false);\n    _mm_sfence();\n    *(volatile uint32_t*) v->h_flagA_ = v->cur_layer_ + 1;\n    strata::research::q4_oracle.flag_a(true);')
edit('src/program/generate.cpp','            const Clock::time_point d0 = Clock::now();\n            strata::research::q4_oracle.begin();', '            ver.publication_trace_begin();for(auto& stage:stages)stage->ver.publication_trace_begin();\n            const Clock::time_point d0 = Clock::now();\n            strata::research::q4_oracle.begin();')
print('INSTRUMENT_PATCH_APPLIED',flush=True)
edit(vc,'#include "strata/research/q4_tape.hpp"', '#include "strata/research/q4_tape.hpp"\n#include "strata/research/q4_oracle.hpp"')
edit(vh,'bool publication_detail_=false;', 'bool publication_detail_=false,publication_measured_=false;')
edit(vc,'if(!publication_data_)return;const OnDevice on_device(device_);cudaMemset(publication_counts_', 'if(!publication_data_)return;publication_measured_=strata::research::q4_tape.active;const OnDevice on_device(device_);cudaMemset(publication_counts_')
edit(vc,'cudaMemcpy(sample,publication_data_+8*publication_cap_*4+boundary*4,sizeof(sample),cudaMemcpyDeviceToHost);', 'cudaMemcpyAsync(sample,publication_data_+8*publication_cap_*4+boundary*4,sizeof(sample),cudaMemcpyDeviceToHost,cs_);cudaStreamSynchronize(cs_);')
edit(vc,'if(prefix&&strata::research::q4_tape.replaying)', 'if(prefix&&publication_measured_)')

edit(vc,'return;q4_trace_mark(', 'return;strata::kernels::q4_trace_mark(')

edit(vk,'#include <cstdint>', '#include <cstdint>\n#include <cstddef>')

edit(o,'plan_end,cpu_end;};\nstruct Q4Oracle', 'plan_end,cpu_end,flag_b_before,flag_b_after,flag_cpu_before,flag_cpu_after;};\nstruct Q4Oracle')
edit(o,' void flag_a(bool after)', ' void other_flag(int kind,bool after){auto* h=ht();if(h){auto& t=kind==1?(after?h->flag_b_after:h->flag_b_before):(after?h->flag_cpu_after:h->flag_cpu_before);t=ns();}}\n void flag_a(bool after)')
edit(vh,'publication_kinds_=9;', 'publication_kinds_=11;')
edit(vc,'    if (n <= 0) { raise_flag(v->h_flagB_, want); return; }', '    if (n <= 0) { strata::research::q4_oracle.other_flag(1,false);raise_flag(v->h_flagB_, want);strata::research::q4_oracle.other_flag(1,true); return; }')
edit(vc,'        if (!(test_stall && k + 1 == steps)) *flag = want;', '        if (!(test_stall && k + 1 == steps)) {strata::research::q4_oracle.other_flag(2,false);*flag = want;strata::research::q4_oracle.other_flag(2,true);}')
edit(vc,'    copy_i32_from_mapped(step_, m_step_, (int64_t) T * kStepCount, cs);', '    if(publication_detail_)publication_mark(9,0,cs);\n    copy_i32_from_mapped(step_, m_step_, (int64_t) T * kStepCount, cs);')
edit(vc,'        copy_from_mapped(hout + (size_t) T * (HC + 1) * N, inj2_, (int64_t) T * HC, cs);\n        return true;', '        copy_from_mapped(hout + (size_t) T * (HC + 1) * N, inj2_, (int64_t) T * HC, cs);\n        if(publication_detail_)publication_mark(10,0,cs);\n        return true;')
edit(vc,'    stamp(g.n_layers, 1, 0);\n    return true;', '    stamp(g.n_layers, 1, 0);\n    if(publication_detail_)publication_mark(10,0,cs);\n    return true;')
edit(vc,'uint64_t header[18]={1,uint64_t(device_),publication_cap_,publication_kinds_,publication_detail_};for(int i=0;i<9;++i)header[5+i]=counts[i];for(int i=0;i<4;++i)header[14+i]=publication_cal_host_[i];strata::research::Q4Tape::io(f,header,18,true);', 'uint64_t header[20]={1,uint64_t(device_),publication_cap_,publication_kinds_,publication_detail_};for(int i=0;i<11;++i)header[5+i]=counts[i];for(int i=0;i<4;++i)header[16+i]=publication_cal_host_[i];strata::research::Q4Tape::io(f,header,20,true);')
edit(vc,'for(int i=0;i<9;++i){size_t n=', 'for(int i=0;i<11;++i){size_t n=')
edit(vc,'std::any_of(counts,counts+9,', 'std::any_of(counts,counts+11,')
