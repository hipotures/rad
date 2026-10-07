// Follow-up exercises: real immutable segmented store and rolling residency monitor.
// Reuse the frozen timing/error/safety primitives without changing the main campaign binary.
#define main common_entry
#include "operations-common.cuh"
#undef main
void rolling_monitor(Args a){
    const size_t N=24576,TOP=512;
    std::vector<float> rolling(N,0);std::vector<uint32_t> ids(N),previous(TOP);
    std::vector<unsigned char>oldset(N,0);std::iota(ids.begin(),ids.end(),0);
    uint64_t sequence=0,drift_events=0,plan_delta=0;
    auto s=sustain(a,[&](bool measured,Stats&r){
        int cluster=(sequence/128)%2;
        for(size_t i=0;i<N;i++)rolling[i]=rolling[i]*.98f+float(mix(i+sequence)%7)+((i%2)==cluster?2.f:0.f);
        std::partial_sort(ids.begin(),ids.begin()+TOP,ids.end(),[&](auto x,auto y){return rolling[x]>rolling[y]||(rolling[x]==rolling[y]&&x<y);});
        uint64_t added=0;for(size_t j=0;j<TOP;j++)added+=!oldset[ids[j]];
        std::fill(oldset.begin(),oldset.end(),0);for(size_t j=0;j<TOP;j++)oldset[ids[j]]=1;
        if(measured){plan_delta+=added;if(added>TOP/4)drift_events++;r.work++;r.bytes+=N*sizeof(float);}
        sequence++;
        if(a.op=="cooperative")std::this_thread::sleep_for(std::chrono::milliseconds(10));
    });
    for(size_t i=0;i<N;i++)if(!std::isfinite(rolling[i]))throw std::runtime_error("VERIFICATION_FAILED: monitor scores");
    for(size_t j=1;j<TOP;j++)if(rolling[ids[j]]>rolling[ids[j-1]])throw std::runtime_error("VERIFICATION_FAILED: ranked plan");
    std::cerr<<"MONITOR_DIAGNOSTICS {\"candidate_ids\":24576,\"top_ids\":512,\"score_decay\":0.98,\"drift_events\":"<<drift_events<<",\"total_added_plan_ids\":"<<plan_delta<<",\"memory_bytes\":"<<(rolling.size()*4+ids.size()*4+oldset.size()+previous.size()*4)<<",\"pacing\":\""<<a.op<<"\"}"<<std::endl;emit(s);
}
struct Expert{std::vector<unsigned char>gate,up,down,blob;uint64_t fingerprint;};
uint64_t signature(const std::vector<unsigned char>&x){uint64_t v=0;auto p=(const uint64_t*)x.data();for(size_t j=0;j<x.size()/8;j++)v^=mix(p[j]+j);return v;}
void immutable_store(Args a){
    std::vector<Expert>experts(96);for(size_t id=0;id<experts.size();id++){
        size_t bytes=(1+id%8)*(1ULL<<20),third=(bytes/3/8)*8;auto&e=experts[id];
        e.gate.resize(third);e.up.resize(third);e.down.resize(bytes-2*third);e.blob.resize(bytes);
        fill(e.gate.data(),e.gate.size(),id*30001+11);fill(e.up.data(),e.up.size(),id*30001+17);fill(e.down.data(),e.down.size(),id*30001+23);
        memcpy(e.blob.data(),e.gate.data(),e.gate.size());memcpy(e.blob.data()+third,e.up.data(),e.up.size());memcpy(e.blob.data()+2*third,e.down.data(),e.down.size());e.fingerprint=signature(e.blob);
    }
    std::vector<Buffer*>slots;for(int j=0;j<4;j++)slots.push_back(new Buffer(a.device,8ULL<<20,"pinned"));
    std::vector<unsigned char>exchange(8ULL<<20);std::vector<int>resident(4,-1);std::vector<uint64_t>generation(4,0);uint64_t sequence=0,published=0,clean_evictions=0,exchange_bytes=0,already_resident_skips=0;
    auto s=sustain(a,[&](bool measured,Stats&r){
        size_t slot=sequence%4,id=mix(sequence+27)%experts.size();
        // The incoming residency delta excludes IDs already published in any slot.
        if(std::find(resident.begin(),resident.end(),int(id))!=resident.end()){if(measured)already_resident_skips++;sequence++;return;}
        auto b=slots[slot];const auto&e=experts[id];size_t n=e.blob.size();
        CU(cudaSetDevice(a.device));CU(cudaStreamSynchronize(b->stream));
        if(resident[slot]>=0){if(a.op=="exchange"){
            size_t old=experts[resident[slot]].blob.size();CU(cudaMemcpyAsync(exchange.data(),b->d,old,cudaMemcpyDeviceToHost,b->stream));CU(cudaStreamSynchronize(b->stream));check(exchange.data(),experts[resident[slot]].blob.data(),old);if(measured)exchange_bytes+=old;
        }else if(measured)clean_evictions++;resident[slot]=-1;}
        if(a.op=="pack"){
            memcpy(b->h,e.gate.data(),e.gate.size());memcpy((char*)b->h+e.gate.size(),e.up.data(),e.up.size());memcpy((char*)b->h+e.gate.size()+e.up.size(),e.down.data(),e.down.size());
        }else memcpy(b->h,e.blob.data(),n);
        CU(cudaMemcpyAsync(b->d,b->h,n,cudaMemcpyHostToDevice,b->stream));CU(cudaStreamSynchronize(b->stream));
        // Publication occurs only after completion. A resident ID never names an in-flight copy.
        CU(cudaStreamQuery(b->stream));resident[slot]=int(id);generation[slot]=sequence+1;
        uint64_t word;CU(cudaMemcpy(&word,b->d,8,cudaMemcpyDeviceToHost));if(word!=*(const uint64_t*)e.blob.data()||generation[slot]!=sequence+1)throw std::runtime_error("VERIFICATION_FAILED: stale slot publication");
        if(measured){r.work++;r.bytes+=n;r.legs+=n+8;published++;}sequence++;
    });
    for(size_t j=0;j<slots.size();j++){
        if(resident[j]>=0){const auto&e=experts[resident[j]];std::vector<unsigned char>v(e.blob.size());CU(cudaSetDevice(a.device));CU(cudaMemcpy(v.data(),slots[j]->d,v.size(),cudaMemcpyDeviceToHost));check(v.data(),e.blob.data(),v.size());}
        delete slots[j];
    }
    for(const auto&e:experts)if(signature(e.blob)!=e.fingerprint)throw std::runtime_error("VERIFICATION_FAILED: immutable backing changed");
    s.legs+=exchange_bytes;
    std::cerr<<"STORE_DIAGNOSTICS {\"immutable_experts\":96,\"gpu_slots\":4,\"published\":"<<published<<",\"already_resident_delta_skips\":"<<already_resident_skips<<",\"clean_evictions_without_D2H\":"<<clean_evictions<<",\"exchange_D2H_bytes\":"<<exchange_bytes<<",\"host_backing_unchanged\":true,\"exchange_note\":\"validation oracle retained outside simulated noninclusive cache\"}"<<std::endl;emit(s);
}
void timed_pipeline(Args a){
    int fd=open(a.file.c_str(),O_RDONLY|O_DIRECT|O_NOFOLLOW);struct stat fs;if(fd<0||fstat(fd,&fs)||!S_ISREG(fs.st_mode))throw std::runtime_error("diagnostic pipeline requires regular file");
    std::vector<Buffer*>bs;std::vector<cudaEvent_t>begin(a.buffers),end(a.buffers);
    for(int j=0;j<a.buffers;j++){bs.push_back(new Buffer(a.device,a.bytes,"stage"));CU(cudaEventCreate(&begin[j]));CU(cudaEventCreate(&end[j]));}
    uint64_t seq=0;double read_seconds=0,stage_seconds=0,enqueue_seconds=0,wait_seconds=0,copy_gpu_ms=0;uint64_t completed=0;
    auto st=sustain(a,[&](bool measured,Stats&r){for(int j=0;j<a.buffers;j++){
        auto b=bs[j];CU(cudaSetDevice(b->dev));CU(cudaStreamSynchronize(b->stream));off_t offset=(mix(++seq)%(fs.st_size/a.bytes))*a.bytes;
        double t=now();if(pread(fd,b->h,a.bytes,offset)!=ssize_t(a.bytes))throw std::runtime_error("pipeline pread failed");double read=now()-t;
        t=now();memcpy(b->p,b->h,a.bytes);double stage=now()-t;
        t=now();CU(cudaEventRecord(begin[j],b->stream));CU(cudaMemcpyAsync(b->d,b->p,a.bytes,cudaMemcpyHostToDevice,b->stream));CU(cudaEventRecord(end[j],b->stream));double enqueue=now()-t;
        if(measured){read_seconds+=read;stage_seconds+=stage;enqueue_seconds+=enqueue;}
    }
    for(int j=0;j<a.buffers;j++){auto b=bs[j];CU(cudaSetDevice(b->dev));double t=now();CU(cudaStreamSynchronize(b->stream));float elapsed;CU(cudaEventElapsedTime(&elapsed,begin[j],end[j]));if(measured){wait_seconds+=now()-t;copy_gpu_ms+=elapsed;completed++;r.bytes+=a.bytes;r.legs+=2*a.bytes;r.work++;}}
    });
    for(int j=0;j<a.buffers;j++){bs[j]->verify();CU(cudaEventDestroy(begin[j]));CU(cudaEventDestroy(end[j]));delete bs[j];}close(fd);
    std::cerr<<"PIPELINE_DIAGNOSTICS {\"completed_objects\":"<<completed<<",\"read_host_seconds_sum\":"<<read_seconds<<",\"pageable_to_pinned_seconds_sum\":"<<stage_seconds<<",\"enqueue_host_seconds_sum\":"<<enqueue_seconds<<",\"drain_wait_seconds_sum\":"<<wait_seconds<<",\"H2D_same_device_event_ms_sum\":"<<copy_gpu_ms<<",\"queue_scope\":\"bounded three-buffer pipeline; overlapping sums must not be added to estimate wall time\",\"instrumented\":true}"<<std::endl;emit(st);
}
int main(int argc,char**argv){signal(SIGTERM,sig);signal(SIGINT,sig);try{auto a=parse(argc,argv);if(a.mode=="pipeline-stages")timed_pipeline(a);else if(a.mode=="monitor")rolling_monitor(a);else if(a.mode=="store")immutable_store(a);else return common_entry(argc,argv);return halted?130:0;}catch(std::exception&e){std::cerr<<e.what()<<std::endl;return 2;}}
