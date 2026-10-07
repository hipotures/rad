"""Buffered candidate/reason/state evidence on unchanged early-v1 algorithm."""
from pathlib import Path
import sys
S=Path(sys.argv[1]);p=S/'include/strata/research/q4_early_policy.hpp';s=p.read_text()
def edit(old,new):
 global s
 assert s.count(old)==1,(old[:100],s.count(old))
 s=s.replace(old,new)
edit('const char* status="pending";};', 'const char* status="pending";int proposed_victim=-1,needed=-1,resident_at_target=-1,target_reached=0;std::array<float,48> features{};};')
edit('    std::vector<Event> events;', '''    struct Demand {int32_t window,layer,n,reserved;std::array<int32_t,40> ids,slots;};
    struct Change {int32_t window,layer,expert,old_slot,new_slot;};
    std::vector<Demand> demands;std::vector<Change> changes;
    std::vector<int32_t> last_state;
    std::array<std::vector<float>,64> history64;
    std::vector<float> cpu_history,mapped_history,promotion_history,eviction_history;
    std::vector<int32_t> resident_since;
    std::array<float,48> candidate_features{};int candidate_victim=-1;
    uint64_t diagnostic_features_ns=0;
    std::vector<Event> events;''')
edit('if(diagnostic){events.clear();readbacks.clear();by_in.assign(48*512,-1);by_victim.assign(48*512,-1);readback_checks=0;}', '''if(diagnostic){events.clear();readbacks.clear();demands.clear();changes.clear();by_in.assign(48*512,-1);by_victim.assign(48*512,-1);readback_checks=0;diagnostic_features_ns=0;
            for(auto& h:history64)h.assign(48*512,0);cpu_history.assign(48*512,0);mapped_history=cpu_history;promotion_history=cpu_history;eviction_history=cpu_history;resident_since.assign(48*512,0);
        }''')
edit('bytes3072000 active_capacity_minus1\\n",dev,spare[dev],best/512,best%512);}', 'bytes3072000 active_capacity_minus1\\n",dev,spare[dev],best/512,best%512);} if(diagnostic)last_state.assign(host_res,host_res+48*512);')
edit('    void begin_window(){if(enabled&&active)std::fill(last_counts.begin(),last_counts.end(),0);}', '''    void begin_window(){if(enabled&&active){std::fill(last_counts.begin(),last_counts.end(),0);
        if(diagnostic)for(int j=0;j<48*512;++j)if(last_state[j]!=host_res[j]){changes.push_back({window_index,j/512,j%512,last_state[j],host_res[j]});if(host_res[j]>=0)resident_since[j]=window_index;else{resident_since[j]=-1;++eviction_history[j];}last_state[j]=host_res[j];}
    }}
    float count_past(int j,int horizon)const {float sum=0;for(int q=1;q<=horizon&&q<=window_index;++q)sum+=history64[(window_index-q)%64][j];return sum;}
    void candidate_snapshot(int target,int incoming,int n,const std::array<float,512>& confidence){
        uint64_t t=ns();candidate_features.fill(0);int j=target*512+incoming,dev=target>=24;int victim=-1;float cold=INFINITY;
        for(int e=0;e<512;++e)if(host_res[target*512+e]>=0&&score[target*512+e]<cold){cold=score[target*512+e];victim=e;}
        candidate_victim=victim;auto& f=candidate_features;float total=0,other=0;int rank=0,unique=0;
        for(int e=0;e<512;++e){total+=confidence[e];if(confidence[e]>0)++unique;if(e!=incoming&&host_res[target*512+e]<0){other=std::max(other,confidence[e]);rank+=confidence[e]>confidence[incoming];}}
        f[0]=confidence[incoming];f[1]=confidence[incoming]/std::max(total,1e-9f);f[2]=other;f[3]=confidence[incoming]-other;f[4]=rank;f[5]=n/10.f;f[6]=unique;
        for(int i=0;i<4;++i)f[7+i]=std::log1p(count_past(j,std::array<int,4>{1,4,16,64}[i]));
        f[11]=std::log1p(heat[j]);f[12]=std::log1p(fast[j]);f[13]=std::log1p(slow[j]);f[14]=std::log1p(freq[j]);f[15]=std::log1p(float(std::min(10000,window_index-last[j])));f[16]=last[j]>=0;
        f[17]=std::log1p(cpu_history[j]);f[18]=std::log1p(mapped_history[j]);f[19]=initial[j]>=0;f[20]=host_res[j]>=0;f[21]=workers[dev].state.load();f[22]=spare[dev]>=0;
        f[23]=target/47.f;f[24]=dev;f[25]=bytes[target]/3072000.f;f[26]=std::log1p(score[j]);f[27]=std::log1p(promotion_history[j]);f[28]=std::log1p(eviction_history[j]);
        if(victim>=0){int v=target*512+victim;f[29]=std::log1p(heat[v]);f[30]=std::log1p(score[v]);f[31]=std::log1p(count_past(v,1));f[32]=std::log1p(count_past(v,4));f[33]=std::log1p(count_past(v,16));f[34]=std::log1p(count_past(v,64));f[35]=std::log1p(float(std::min(10000,window_index-last[v])));f[36]=std::max(0,window_index-resident_since[v]);f[37]=std::log1p(eviction_history[v]);f[38]=count_past(v,1)>0;f[39]=1;f[40]=f[26]-f[30];}
        f[41]=window_index;f[42]=bytes[target]/13.2e6f;f[43]=0.293449f;f[44]=4;f[45]=0;f[46]=0;f[47]=0;
        diagnostic_features_ns+=ns()-t;
    }''')
edit('events.push_back({window_index,target,e,-1,w.destination,w.issue_ns});', 'events.push_back({window_index,target,e,-1,w.destination,w.issue_ns});events.back().features=candidate_features;events.back().proposed_victim=candidate_victim;')
edit('if(w.target==l&&state!=0){', 'if(w.target==l&&state!=0){if(diagnostic){events[w.event_index].target_reached=1;events[w.event_index].resident_at_target=host_res[l*512+w.incoming]>=0;}')
edit('if(!needed||host_res[l*512+w.incoming]>=0){++wrong;if(diagnostic)events[w.event_index].status="wrong-or-superseded";retire(dev);}', 'if(diagnostic)events[w.event_index].needed=needed;\n                if(!needed||host_res[l*512+w.incoming]>=0){++wrong;if(diagnostic)events[w.event_index].status=needed?"became-resident-before-publication":"prediction-wrong";retire(dev);}')
edit('e.status="target-ready-persistent";e.victim=victim;', 'e.status="target-ready-persistent";++promotion_history[l*512+w.incoming];++eviction_history[l*512+victim];resident_since[l*512+w.incoming]=window_index;e.victim=victim;')
edit('        for(int i=0;i<n;++i)if(ids[i]>=0&&ids[i]<512)', '''        if(diagnostic){Demand d{window_index,l,n,0,{},{}};d.ids.fill(-1);d.slots.fill(-1);std::vector<int> miss;
            for(int i=0;i<n;++i){d.ids[i]=ids[i];d.slots[i]=host_res[l*512+ids[i]];if(d.slots[i]<0&&std::find(miss.begin(),miss.end(),ids[i])==miss.end())miss.push_back(ids[i]);}
            int nm=(int)miss.size()*72/256;for(int i=0;i<n;++i)if(d.slots[i]<0){int e=ids[i];bool mapped=nm&&std::find(miss.end()-nm,miss.end(),e)!=miss.end();(mapped?mapped_history:cpu_history)[l*512+e]+=1;}demands.push_back(d);
        }
        for(int i=0;i<n;++i)if(ids[i]>=0&&ids[i]<512)''')
edit('if(inc>=0)enqueue(dev,l,inc);', 'if(inc>=0){if(diagnostic){std::array<float,512> conf{};conf[inc]=1;candidate_snapshot(l,inc,n,conf);}enqueue(dev,l,inc);}')
edit('if(inc>=0)enqueue(pd,target,inc);', 'if(inc>=0){if(diagnostic)candidate_snapshot(target,inc,n,confidence);enqueue(pd,target,inc);}')
edit('features_ns+=ns()-begin;++window_index;', '''features_ns+=ns()-begin;if(diagnostic){for(int l:targets)for(int e=0;e<512;++e)history64[window_index%64][l*512+e]=last_counts[l*512+e];last_state.assign(host_res,host_res+48*512);}++window_index;''')
# Keep original compact evidence plus explicit reason/features and fixed-schedule demand/cache evidence.
start=s.index('for(const auto& e:events)std::fprintf(file,')
end=s.index('std::fclose(file);',start)
s=s[:start]+'''for(const auto& e:events){std::fprintf(file,"{\\"window\\":%d,\\"layer\\":%d,\\"incoming\\":%d,\\"victim\\":%d,\\"slot\\":%d,\\"issue_ns\\":%llu,\\"copy_begin_ns\\":%llu,\\"copy_end_ns\\":%llu,\\"published_ns\\":%llu,\\"uses\\":%llu,\\"victim_entries\\":%llu,\\"classification\\":\\"%s\\",\\"proposed_victim\\":%d,\\"needed\\":%d,\\"resident_at_target\\":%d,\\"target_reached\\":%d,\\"right_censored\\":%s,\\"features\\":[",e.window,e.layer,e.incoming,e.victim,e.slot,(unsigned long long)e.issue,(unsigned long long)e.copy_begin,(unsigned long long)e.copy_end,(unsigned long long)e.published,(unsigned long long)e.uses,(unsigned long long)e.victim_entries,e.status,e.proposed_victim,e.needed,e.resident_at_target,e.target_reached,e.window>=window_index-4?"true":"false");for(int j=0;j<48;++j)std::fprintf(file,"%s%.9g",j?",":"",e.features[j]);std::fprintf(file,"]}\\n");}
            auto binary=[&](const char* suffix,const void* ptr,size_t size){std::string name=std::string(prefix)+"-request"+std::to_string(request_index)+suffix;FILE* f=std::fopen(name.c_str(),"wx");if(!f)fatal("diagnostic binary exists");if(size&&std::fwrite(ptr,1,size,f)!=size)fatal("diagnostic binary write failed");std::fclose(f);};
            binary("-demand.bin",demands.data(),demands.size()*sizeof(Demand));binary("-native-changes.bin",changes.data(),changes.size()*sizeof(Change));binary("-initial.bin",initial.data(),initial.size()*sizeof(int32_t));
            std::fprintf(stderr,"Q4_CONDITIONAL_DIAGNOSTIC records=%zu changes=%zu feature_ms=%.3f\\n",demands.size(),changes.size(),diagnostic_features_ns/1e6);
            '''+s[end:]
p.write_text(s)
print('BUFFERED_DIAGNOSTIC_PATCH: same selection/copy/publication/heat; reason split and causal snapshots only',flush=True)
