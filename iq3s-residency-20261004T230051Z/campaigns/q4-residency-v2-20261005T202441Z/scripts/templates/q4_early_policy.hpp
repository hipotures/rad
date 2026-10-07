// Experimental same-device persistent Q4 admission. Default OFF.
// The planner invokes no CUDA API while an active graph waits for its plan.
#pragma once
#include "strata/core/weights.hpp"
#include "strata/core/layout.hpp"
#include "strata/kernels/bf16_gemv.hpp"
#include "strata/kernels/native_router.hpp"
#include "strata/kernels/elementwise.hpp"
#include "strata/research/q4_linear_constants.hpp"
#include <cuda_runtime.h>
#include <array>
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <string>
#include <vector>
namespace strata::research {
struct Q4EarlyPolicy {
    static constexpr std::array<int,5> origins{5,12,25,32,38};
    static constexpr std::array<int,5> targets{9,16,29,36,42};
    static constexpr int ne=512,nl=48,maxT=4,k=10;
    bool enabled=false,active=false,reactive=false,diagnostic=false;int forced_expert=-1,request_index=0;
    struct Event{int window,layer,incoming,victim=-1,slot=-1;uint64_t issue=0,copy_begin=0,copy_end=0,published=0,uses=0,victim_entries=0;const char* status="pending";};
    std::vector<Event> events;std::vector<int> by_in,by_victim;std::vector<int> readbacks;uint64_t readback_checks=0;
    int32_t* host_res=nullptr;const float* native_heat=nullptr;
    std::array<const uint16_t*,5> gates{};
    std::array<bool,2> configured{};
    std::array<int32_t*,2> pred_ids{},mapped_ids{};
    std::array<float*,2> pred_weights{},mapped_weights{};
    std::array<unsigned*,2> seq{},mapped_seq{};
    std::array<int32_t*,2> device_res{};
    std::array<int,2> spare{-1,-1},reserve_layer{-1,-1},reserve_expert{-1,-1};
    std::vector<uint64_t> bytes;
    std::function<const uint8_t*(int,int)> blob;
    std::function<void*(int,int)> device_slot;
    std::vector<float> heat,fast,slow,freq,last_counts,initial_heat,score;
    std::vector<int32_t> last,initial;
    std::array<std::vector<float>,4> recent;
    int window_index=0;
    uint64_t issued=0,ready_admits=0,late=0,wrong=0,busy=0,traffic=0,target_entries=0;
    uint64_t features_ns=0,publish_wait_ns=0,copy_ns=0,staging_ns=0,drain_ns=0;
    struct Worker {
        std::mutex mutex;std::condition_variable cv;std::thread thread;
        // state:0idle,1copy queued,2copying,3ready,4publish queued,5published,6retire,7failed.
        std::atomic<int> state{0};bool quit=false;
        int target=-1,incoming=-1,victim=-1,destination=-1,new_spare=-1,event_index=-1;
        const uint8_t* source=nullptr;size_t n=0;
        uint8_t* staging=nullptr;int32_t* metadata=nullptr;
        cudaStream_t stream=nullptr;cudaEvent_t done=nullptr;
        uint64_t issue_ns=0,copy_begin_ns=0,copy_end_ns=0,staging_cost_ns=0;
    };
    std::array<Worker,2> workers;
    static uint64_t ns(){return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
    static void check(cudaError_t e){if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));}
    static void fatal(const char* message){std::fprintf(stderr,"Q4_EARLY_FATAL %s\n",message);std::fflush(stderr);std::_Exit(1);}
    Q4EarlyPolicy(){const char* p=std::getenv("STRATA_Q4_EARLY");enabled=p&&p[0]=='1';p=std::getenv("STRATA_Q4_EARLY_REACTIVE");reactive=p&&p[0]=='1';p=std::getenv("STRATA_Q4_EARLY_DIAGNOSTIC");diagnostic=p&&p[0]=='1';p=std::getenv("STRATA_Q4_EARLY_FORCE_EXPERT");if(p)forced_expert=std::atoi(p);}
    int origin_index(int l)const {auto i=std::find(origins.begin(),origins.end(),l);return i==origins.end()?-1:int(i-origins.begin());}
    bool target_layer(int l)const{return std::find(targets.begin(),targets.end(),l)!=targets.end();}
    bool configure_gate(const strata::core::WeightTable& wt,const strata::core::ModelGeometry& g,int dev,int first,int end,std::string& err){
        if(!enabled)return true;
        if(dev<0||dev>1||g.n_embd!=2560||g.n_expert!=512||g.n_layers!=48||first!=dev*24||end!=(dev+1)*24){err="Q4 early frozen K24 geometry required";return false;}
        if(configured[dev])return true;
        try{
            check(cudaHostAlloc(&pred_ids[dev],5*maxT*k*sizeof(int32_t),cudaHostAllocMapped));check(cudaHostGetDevicePointer(&mapped_ids[dev],pred_ids[dev],0));
            check(cudaHostAlloc(&pred_weights[dev],5*maxT*k*sizeof(float),cudaHostAllocMapped));check(cudaHostGetDevicePointer(&mapped_weights[dev],pred_weights[dev],0));
            check(cudaHostAlloc(&seq[dev],64,cudaHostAllocMapped));check(cudaHostGetDevicePointer(&mapped_seq[dev],seq[dev],0));*seq[dev]=0;
            auto& w=workers[dev];check(cudaHostAlloc(&w.staging,3993600,cudaHostAllocDefault));check(cudaHostAlloc(&w.metadata,2*sizeof(int32_t),cudaHostAllocDefault));check(cudaStreamCreateWithFlags(&w.stream,cudaStreamNonBlocking));check(cudaEventCreateWithFlags(&w.done,cudaEventDisableTiming));
            for(int i=0;i<5;++i)if(origins[i]>=first&&targets[i]<end){auto* gate=wt.find("blk."+std::to_string(targets[i])+".ffn_gate_inp.weight");if(!gate||gate->kind!=strata::core::WeightKind::Bf16InF32||gate->bytes!=uint64_t(2560)*512*2)throw std::runtime_error("Q4 early native BF16 gate missing");gates[i]=(const uint16_t*)gate->data;}
            configured[dev]=true;w.thread=std::thread([this,dev]{worker_loop(dev);});
        }catch(const std::exception& e){err=std::string("Q4 early configure: ")+e.what();return false;}
        return true;
    }
    static void publish_state(Worker& w,int value){std::lock_guard<std::mutex> lock(w.mutex);w.state.store(value,std::memory_order_release);w.cv.notify_all();}
    void worker_loop(int dev){
        auto& w=workers[dev];try{
            check(cudaSetDevice(dev));
            while(true){int command;
                {std::unique_lock<std::mutex> lock(w.mutex);w.cv.wait(lock,[&]{return w.quit||w.state.load()==1||w.state.load()==4||w.state.load()==6;});if(w.quit)break;command=w.state.load();if(command==1)w.state.store(2,std::memory_order_release);}
                if(command==1){
                    const char* delay=std::getenv("STRATA_Q4_EARLY_DELAY_US");if(delay)std::this_thread::sleep_for(std::chrono::microseconds(std::atoi(delay)));
                    uint64_t t=ns();std::memcpy(w.staging,w.source,w.n);w.staging_cost_ns+=ns()-t;w.copy_begin_ns=ns();
                    check(cudaMemcpyAsync(device_slot(dev,w.destination),w.staging,w.n,cudaMemcpyHostToDevice,w.stream));check(cudaEventRecord(w.done,w.stream));check(cudaEventSynchronize(w.done));w.copy_end_ns=ns();
                    publish_state(w,3);
                }else if(command==4){
                    w.metadata[0]=-1;w.metadata[1]=w.destination;
                    check(cudaMemcpyAsync(device_res[dev]+w.target*ne+w.victim,w.metadata,sizeof(int32_t),cudaMemcpyHostToDevice,w.stream));
                    check(cudaMemcpyAsync(device_res[dev]+w.target*ne+w.incoming,w.metadata+1,sizeof(int32_t),cudaMemcpyHostToDevice,w.stream));check(cudaEventRecord(w.done,w.stream));check(cudaEventSynchronize(w.done));
                    publish_state(w,5);
                }else if(command==6){publish_state(w,0);}
            }
        }catch(const std::exception& e){std::fprintf(stderr,"Q4_EARLY_WORKER_FAIL device%d %s\n",dev,e.what());publish_state(w,7);}
    }
    void runtime(int32_t* r,const float* u,std::vector<uint64_t> sizes,std::array<int32_t*,2> dr,
                 std::function<const uint8_t*(int,int)> source,std::function<void*(int,int)> slot){
        if(!enabled)return;host_res=r;native_heat=u;bytes=std::move(sizes);device_res=dr;blob=std::move(source);device_slot=std::move(slot);
        const size_t n=48*512;heat.resize(n);fast.resize(n);slow.resize(n);freq.resize(n);last_counts.resize(n);initial_heat.resize(n);score.resize(n);last.resize(n);initial.resize(n);for(auto& x:recent)x.resize(n);
    }
    // Existing verifier scratch is reused BEFORE the real router overwrites it.
    // No extra GPU expert/scratch allocation is added by the predictor.
    void gpu_score(int l,int T,const float* activation,float* logits,int32_t* ids,float* weights,cudaStream_t stream){
        if(!enabled||reactive||T>4)return;int i=origin_index(l);if(i<0||!gates[i])return;int dev=l>=24;
        strata::kernels::bf16_gemv_fp32_mmvf_multi(activation,2560,gates[i],logits,512,2560,512,T,stream);
        strata::kernels::native_router_top10_multi(logits,ids,weights,T,stream);
        strata::kernels::doorbell_publish(nullptr,ids,weights,0,T*10,nullptr,mapped_ids[dev]+i*40,mapped_weights[dev]+i*40,mapped_seq[dev],stream);
    }
    void begin_request(){
        if(!enabled)return;if(!host_res||!configured[0]||!configured[1])throw std::runtime_error("Q4 early runtime not configured");active=true;window_index=0;issued=ready_admits=late=wrong=busy=traffic=target_entries=0;features_ns=publish_wait_ns=copy_ns=staging_ns=drain_ns=0;
        std::copy(native_heat,native_heat+48*512,heat.begin());initial_heat=heat;std::copy(host_res,host_res+48*512,initial.begin());
        for(auto* x:{&fast,&slow,&freq,&last_counts})std::fill(x->begin(),x->end(),0);std::fill(last.begin(),last.end(),-10000);for(auto& x:recent)std::fill(x.begin(),x.end(),0);for(size_t j=0;j<score.size();++j)score[j]=heat[j]*.3f;
        if(diagnostic){events.clear();readbacks.clear();by_in.assign(48*512,-1);by_victim.assign(48*512,-1);readback_checks=0;}++request_index;
        for(auto& w:workers)w.staging_cost_ns=0;
        for(int dev=0;dev<2;++dev){int best=-1;float cold=INFINITY;for(int l=dev*24;l<(dev+1)*24;++l)if(bytes[l]==3072000)for(int e=0;e<512;++e){int j=l*512+e;if(host_res[j]>=0&&heat[j]<cold){cold=heat[j];best=j;}}
            if(best<0)throw std::runtime_error("Q4 early no correctly sized reserve");spare[dev]=host_res[best];reserve_layer[dev]=best/512;reserve_expert[dev]=best%512;host_res[best]=-1;
            std::fprintf(stderr,"Q4_EARLY_RESERVE device%d slot%d layer%d expert%d bytes3072000 active_capacity_minus1\n",dev,spare[dev],best/512,best%512);}
    }
    void begin_window(){if(enabled&&active)std::fill(last_counts.begin(),last_counts.end(),0);}
    void enqueue(int dev,int target,int e){auto& w=workers[dev];if(w.state.load(std::memory_order_acquire)!=0){++busy;return;}const uint8_t* ptr=blob(target,e);if(!ptr)fatal("canonical Q4 blob unavailable");
        {std::lock_guard<std::mutex> lock(w.mutex);w.target=target;w.incoming=e;w.destination=spare[dev];w.source=ptr;w.n=bytes[target];w.issue_ns=ns();if(diagnostic){w.event_index=(int)events.size();events.push_back({window_index,target,e,-1,w.destination,w.issue_ns});}w.state.store(1,std::memory_order_release);}++issued;traffic+=w.n;w.cv.notify_all();}
    void retire(int dev){auto& w=workers[dev];uint64_t begin=ns();std::unique_lock<std::mutex> lock(w.mutex);if(!w.cv.wait_for(lock,std::chrono::seconds(5),[&]{return w.state.load()==0||w.state.load()==3||w.state.load()==7;}))fatal("copy retirement timeout");if(w.state.load()==7)fatal("copy worker failure");if(w.state.load()==3){if(diagnostic&&w.event_index>=0){auto& e=events[w.event_index];e.copy_begin=w.copy_begin_ns;e.copy_end=w.copy_end_ns;if(e.status==std::string("pending"))e.status="pending-retired";}copy_ns+=w.copy_end_ns-w.copy_begin_ns;w.state.store(6,std::memory_order_release);w.cv.notify_all();if(!w.cv.wait_for(lock,std::chrono::seconds(5),[&]{return w.state.load()==0||w.state.load()==7;}))fatal("retire acknowledgement timeout");}drain_ns+=ns()-begin;}
    void host(int32_t* r,int l,const int32_t* ids,int n){
        if(!enabled||!active||r!=host_res||n<1||n>40)return;int dev=l>=24;auto& w=workers[dev];int state=w.state.load(std::memory_order_acquire);
        if(state==7)fatal("worker failed before plan");
        if(w.target==l&&state!=0){
            if(state!=3){++late;if(diagnostic)events[w.event_index].status="late-for-original-target";}
            else{
                bool needed=false;int occurrences=0;for(int i=0;i<n;++i)if(ids[i]==w.incoming){needed=true;++occurrences;}
                if(!needed||host_res[l*512+w.incoming]>=0){++wrong;if(diagnostic)events[w.event_index].status="wrong-or-superseded";retire(dev);}
                else{int victim=-1;float cold=INFINITY;for(int e=0;e<512;++e){if(host_res[l*512+e]<0)continue;bool routed=false;for(int i=0;i<n;++i)routed|=ids[i]==e;if(!routed&&score[l*512+e]<cold){cold=score[l*512+e];victim=e;}}
                    if(victim<0){++wrong;if(diagnostic)events[w.event_index].status="no-safe-victim";retire(dev);}else{
                        int oldslot=host_res[l*512+victim];uint64_t begin=ns();{std::unique_lock<std::mutex> lock(w.mutex);w.victim=victim;w.new_spare=oldslot;w.state.store(4,std::memory_order_release);w.cv.notify_all();if(!w.cv.wait_for(lock,std::chrono::seconds(5),[&]{return w.state.load()==5||w.state.load()==7;}))fatal("metadata publication timeout");if(w.state.load()==7)fatal("metadata publication failure");}
                        publish_wait_ns+=ns()-begin;host_res[l*512+victim]=-1;host_res[l*512+w.incoming]=w.destination;spare[dev]=oldslot;++ready_admits;target_entries+=occurrences;copy_ns+=w.copy_end_ns-w.copy_begin_ns;
                        if(diagnostic){auto& e=events[w.event_index];e.status="target-ready-persistent";e.victim=victim;e.published=ns();e.copy_begin=w.copy_begin_ns;e.copy_end=w.copy_end_ns;by_in[l*512+w.incoming]=w.event_index;by_victim[l*512+victim]=w.event_index;if(readback_checks+readbacks.size()<16)readbacks.push_back(w.event_index);}
                        w.state.store(0,std::memory_order_release);
                    }
                }
            }
        }
        for(int i=0;i<n;++i)if(ids[i]>=0&&ids[i]<512){int j=l*512+ids[i];last_counts[j]+=1;if(diagnostic){if(by_in[j]>=0){if(host_res[j]>=0)++events[by_in[j]].uses;else by_in[j]=-1;}if(by_victim[j]>=0){if(host_res[j]<0)++events[by_victim[j]].victim_entries;else by_victim[j]=-1;}}}
        if(reactive){if(target_layer(l)&&w.state.load()==0){int inc=-1;float best=-1;for(int i=0;i<n;++i){int e=ids[i];if(host_res[l*512+e]<0&&score[l*512+e]>best){best=score[l*512+e];inc=e;}}if(inc>=0)enqueue(dev,l,inc);}return;}
        int oi=origin_index(l);if(oi<0)return;int target=targets[oi],pd=target>=24;auto& worker=workers[pd];if(worker.state.load()!=0){++busy;return;}
        std::array<float,512> confidence{};for(int i=0;i<n;++i){int e=pred_ids[dev][oi*40+i];if(e>=0&&e<512)confidence[e]+=pred_weights[dev][oi*40+i];}
        int inc=-1;float best=0;for(int e=0;e<512;++e)if(host_res[target*512+e]<0){float rank=confidence[e]*(1+.1f*score[target*512+e]);if(rank>best){best=rank;inc=e;}}
        if(forced_expert>=0&&forced_expert<512&&host_res[target*512+forced_expert]<0)inc=forced_expert;
        if(inc>=0)enqueue(pd,target,inc);
    }
    void end_window(bool decay){
        if(!enabled||!active)return;for(int dev=0;dev<2;++dev)if(!reactive)retire(dev);
        if(diagnostic){std::vector<uint8_t> check_bytes(3993600);int olddev;check(cudaGetDevice(&olddev));for(int index:readbacks){auto& e=events[index];int dev=e.layer>=24;check(cudaSetDevice(dev));check(cudaMemcpy(check_bytes.data(),device_slot(dev,e.slot),bytes[e.layer],cudaMemcpyDeviceToHost));if(std::memcmp(check_bytes.data(),blob(e.layer,e.incoming),bytes[e.layer]))fatal("promoted Q4 bytes differ from canonical weights");++readback_checks;}check(cudaSetDevice(olddev));readbacks.clear();}
        uint64_t begin=ns();for(int l:targets)for(int e=0;e<512;++e){int j=l*512+e;float c=last_counts[j];heat[j]+=c;fast[j]=.5f*fast[j]+c;slow[j]=.95f*slow[j]+c;freq[j]+=c;if(c>0)last[j]=window_index;recent[window_index%4][j]=c;
            float total=0;for(auto& x:recent)total+=x[j];float x[16]={std::log1p(heat[j]),std::log1p(fast[j]*2),std::log1p(slow[j]*.2f),std::log1p(c),std::log1p(total),0,0,std::log1p(freq[j]*4/(window_index+1)),std::log1p(float(std::min(10000,window_index-last[j]))),float(last[j]>=0),float(initial[j]>=0),std::log1p(initial_heat[j]),l/47.f,float(l>=24),bytes[l]/3072000.f,0};
            float z=q4_linear::intercept;for(int k=0;k<13;++k)z+=(x[q4_linear::indices[k]]-q4_linear::mean[k])/q4_linear::std[k]*q4_linear::coef[k];score[j]=std::max(0.f,std::expm1(std::clamp(z,0.f,std::log(33.f)))*q4_linear::cal_slope+q4_linear::cal_intercept);if(decay)heat[j]*=.7f;
        }features_ns+=ns()-begin;++window_index;
    }
    void finish(){
        if(!enabled||!active)return;for(int dev=0;dev<2;++dev){retire(dev);int l=reserve_layer[dev],e=reserve_expert[dev];if(host_res[l*512+e]>=0){float best=-1;e=-1;for(int x=0;x<512;++x)if(host_res[l*512+x]<0&&native_heat[l*512+x]>best){best=native_heat[l*512+x];e=x;}}if(e<0)fatal("reserve restoration unavailable");int olddev;check(cudaGetDevice(&olddev));check(cudaSetDevice(dev));check(cudaMemcpy(device_slot(dev,spare[dev]),blob(l,e),bytes[l],cudaMemcpyHostToDevice));host_res[l*512+e]=spare[dev];check(cudaSetDevice(olddev));}
        if(diagnostic){const char* prefix=std::getenv("STRATA_Q4_EARLY_LOG");if(prefix){std::string path=std::string(prefix)+"-request"+std::to_string(request_index)+".jsonl";FILE* file=std::fopen(path.c_str(),"wx");if(!file)fatal("cannot preserve unique diagnostic event log");for(const auto& e:events)std::fprintf(file,"{\"window\":%d,\"layer\":%d,\"incoming\":%d,\"victim\":%d,\"slot\":%d,\"issue_ns\":%llu,\"copy_begin_ns\":%llu,\"copy_end_ns\":%llu,\"published_ns\":%llu,\"uses\":%llu,\"victim_entries\":%llu,\"classification\":\"%s\"}\n",e.window,e.layer,e.incoming,e.victim,e.slot,(unsigned long long)e.issue,(unsigned long long)e.copy_begin,(unsigned long long)e.copy_end,(unsigned long long)e.published,(unsigned long long)e.uses,(unsigned long long)e.victim_entries,e.status);std::fclose(file);}std::fprintf(stderr,"Q4_EARLY_READBACK PASS checks=%llu\n",(unsigned long long)readback_checks);}
        staging_ns=workers[0].staging_cost_ns+workers[1].staging_cost_ns;active=false;std::fprintf(stderr,"Q4_EARLY windows=%d issued=%llu ready=%llu late=%llu wrong=%llu busy=%llu bytes=%llu target_entries=%llu scoring_ms=%.3f publish_wait_ms=%.3f staged_ms=%.3f copy_ms=%.3f drain_ms=%.3f\n",window_index,(unsigned long long)issued,(unsigned long long)ready_admits,(unsigned long long)late,(unsigned long long)wrong,(unsigned long long)busy,(unsigned long long)traffic,(unsigned long long)target_entries,features_ns/1e6,publish_wait_ns/1e6,staging_ns/1e6,copy_ns/1e6,drain_ns/1e6);
    }
    ~Q4EarlyPolicy(){for(int dev=0;dev<2;++dev){auto& w=workers[dev];if(w.thread.joinable()){{std::lock_guard<std::mutex> lock(w.mutex);w.quit=true;w.cv.notify_all();}w.thread.join();}if(configured[dev]){cudaSetDevice(dev);cudaEventDestroy(w.done);cudaStreamDestroy(w.stream);cudaFreeHost(w.staging);cudaFreeHost(w.metadata);cudaFreeHost(pred_ids[dev]);cudaFreeHost(pred_weights[dev]);cudaFreeHost(seq[dev]);}}}
};
inline Q4EarlyPolicy q4_early;
}
