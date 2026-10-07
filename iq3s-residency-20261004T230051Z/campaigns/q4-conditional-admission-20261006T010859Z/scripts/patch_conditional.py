"""Frozen conditional gate before enqueue; preserve original two-spare scheduler."""
from pathlib import Path
import runpy,sys,shutil
C=Path(__file__).resolve().parents[1];S=Path(sys.argv[1])
import json
decision=json.loads((C/'phase-b/live-gate.json').read_text());assert decision['qualifies_live'] and decision['unchanged_policy']=='linear-balanced'
runpy.run_path(str(C/'scripts/patch_diagnostic.py'),run_name='__main__')
shutil.copy2(C/'checkpoints/conditional_constants.hpp',S/'include/strata/research/q4_conditional_constants.hpp')
p=S/'include/strata/research/q4_early_policy.hpp';s=p.read_text()
def edit(old,new):
 global s
 assert s.count(old)==1,(old[:100],s.count(old));s=s.replace(old,new)
edit('#include "strata/research/q4_linear_constants.hpp"','#include "strata/research/q4_linear_constants.hpp"\n#include "strata/research/q4_conditional_constants.hpp"')
edit('bool enabled=false,active=false,reactive=false,diagnostic=false;', 'bool enabled=false,active=false,reactive=false,diagnostic=false,conditional=false,force_reject=false;')
edit('    uint64_t diagnostic_features_ns=0;', '''    uint64_t diagnostic_features_ns=0,gate_ns=0,rejected_before_copy=0,proposals=0;
    std::array<std::vector<uint8_t>,16> previous_wrong,previous_published;
    std::vector<uint8_t> window_wrong,window_published;
    std::array<int,5> proposed_experts{-1,-1,-1,-1,-1};
    bool tracking()const{return diagnostic||conditional;}
    int target_index(int l)const{auto i=std::find(targets.begin(),targets.end(),l);return i==targets.end()?-1:int(i-targets.begin());}''')
edit('if(p)forced_expert=std::atoi(p);}', 'if(p)forced_expert=std::atoi(p);p=std::getenv("STRATA_Q4_CONDITIONAL");conditional=p&&p[0]==\'1\';p=std::getenv("STRATA_Q4_CONDITIONAL_REJECT_ALL");force_reject=p&&p[0]==\'1\';if(conditional&&reactive)throw std::runtime_error("ConditionalH4 andreactive modes are separate matched ablations");}')
# Tracking and buffered instrumentation are separate. Headline gate needs cheap
# prior outcome/victim counters, never full demand/cache trace or readbacks.
s=s.replace('if(diagnostic)', 'if(tracking())')
edit('readback_checks=0;diagnostic_features_ns=0;', 'readback_checks=0;diagnostic_features_ns=0;gate_ns=0;rejected_before_copy=proposals=0;proposed_experts.fill(-1);for(auto& x:previous_wrong)x.assign(48*512,0);for(auto& x:previous_published)x.assign(48*512,0);window_wrong.assign(48*512,0);window_published.assign(48*512,0);')
edit('std::fill(last_counts.begin(),last_counts.end(),0);\n        if(tracking())', 'std::fill(last_counts.begin(),last_counts.end(),0);if(conditional){std::fill(window_wrong.begin(),window_wrong.end(),0);std::fill(window_published.begin(),window_published.end(),0);proposed_experts.fill(-1);}\n        if(tracking())')
edit('changes.push_back({window_index,j/512,j%512,last_state[j],host_res[j]});', 'if(diagnostic)changes.push_back({window_index,j/512,j%512,last_state[j],host_res[j]});')
edit('f[44]=4;f[45]=0;f[46]=0;f[47]=0;', '''f[44]=4;f[45]=0;f[46]=0;f[47]=0;
        if(conditional){int bad=0,good=0;for(int q=1;q<=16&&q<=window_index;++q){bad+=previous_wrong[(window_index-q)%16][j];good+=previous_published[(window_index-q)%16][j];}f[45]=std::log1p(float(bad));f[46]=std::log1p(float(good));f[47]=window_index>0&&previous_wrong[(window_index-1)%16][j];}''')
# Only diagnostic mode records all demand/counterfactual native transactions.
edit('if(tracking()){Demand d{', 'if(diagnostic){Demand d{')
# CPU/mapped history is an inference input. Gather only five targetlayers in
# clean mode, after original publication and before the original CPU plan.
edit('        if(diagnostic){Demand d{', '''        if(conditional&&target_layer(l)&&!diagnostic){std::vector<int> miss;for(int i=0;i<n;++i)if(host_res[l*512+ids[i]]<0&&std::find(miss.begin(),miss.end(),ids[i])==miss.end())miss.push_back(ids[i]);int nm=(int)miss.size()*72/256;for(int i=0;i<n;++i)if(host_res[l*512+ids[i]]<0){int e=ids[i];bool mapped=nm&&std::find(miss.end()-nm,miss.end(),e)!=miss.end();(mapped?mapped_history:cpu_history)[l*512+e]+=1;}}
        if(diagnostic){Demand d{''')
edit('if(readback_checks+readbacks.size()<16)readbacks.push_back(w.event_index);', 'if(diagnostic&&readback_checks+readbacks.size()<16)readbacks.push_back(w.event_index);')
edit('if(tracking()){std::vector<uint8_t> check_bytes', 'if(diagnostic){std::vector<uint8_t> check_bytes')
edit('if(tracking()){const char* prefix=', 'if(diagnostic){const char* prefix=')
# Observe true target membership for REJECTED as well as accepted proposals.
# Otherwise past-failure features disappear when the gate stops copying.
edit('        for(int i=0;i<n;++i)if(ids[i]>=0&&ids[i]<512)', '''        if(conditional){int ti=target_index(l);if(ti>=0&&proposed_experts[ti]>=0){int e=proposed_experts[ti];bool used=false;for(int i=0;i<n;++i)used|=ids[i]==e;window_wrong[l*512+e]=!used;proposed_experts[ti]=-1;}}
        for(int i=0;i<n;++i)if(ids[i]>=0&&ids[i]<512)''')
edit('e.status="target-ready-persistent";++promotion_history', 'e.status="target-ready-persistent";if(conditional)window_published[l*512+w.incoming]=1;++promotion_history')
edit('if(tracking()){if(by_in[j]>=0)', 'if(tracking()&&target_layer(l)){if(by_in[j]>=0)')
old='if(inc>=0){if(tracking())candidate_snapshot(target,inc,n,confidence);enqueue(pd,target,inc);}'
new='''if(inc>=0){if(tracking())candidate_snapshot(target,inc,n,confidence);
            if(conditional){++proposals;proposed_experts[oi]=inc;uint64_t begin=ns();double probability=q4_conditional::probability(candidate_features.data());
                bool accept=!force_reject&&probability>=0.12&&candidate_features[32]<=candidate_features[8]+std::log(3.f)&&candidate_features[39]>0&&candidate_features[21]==0&&candidate_features[22]>0;
                gate_ns+=ns()-begin;if(!accept){++rejected_before_copy;return;}}
            enqueue(pd,target,inc);
        }'''
edit(old,new)
edit('last_state.assign(host_res,host_res+48*512);}++window_index;', 'last_state.assign(host_res,host_res+48*512);}if(conditional){previous_wrong[window_index%16]=window_wrong;previous_published[window_index%16]=window_published;}++window_index;')
edit('staging_ns=workers[0].staging_cost_ns+workers[1].staging_cost_ns;active=false;', '''if(conditional){uint64_t published=0,useful=0,victim_damage=0,unpublished=0,censored=0;for(const auto& e:events){if(e.published){++published;useful+=e.uses;victim_damage+=e.victim_entries;}else ++unpublished;censored+=e.window>=window_index-4;}
            std::fprintf(stderr,"Q4_CONDITIONAL proposals=%llu rejected_before_copy=%llu issued=%llu published=%llu unpublished_bytes=%llu useful_local_entries=%llu victim_absent_entries=%llu right_censored=%llu feature_ms=%.6f score_selection_ms=%.6f threshold=0.12 checkpoint40f43308\\n",(unsigned long long)proposals,(unsigned long long)rejected_before_copy,(unsigned long long)issued,(unsigned long long)published,(unsigned long long)(unpublished*3072000),(unsigned long long)useful,(unsigned long long)victim_damage,(unsigned long long)censored,diagnostic_features_ns/1e6,gate_ns/1e6);}
        staging_ns=workers[0].staging_cost_ns+workers[1].staging_cost_ns;active=false;''')
p.write_text(s)
print('CONDITIONAL_PATCH: frozenp.12 BEFORE enqueue/blob/staging; rejected outcomes still observed; originalpublication/victimguard/physicalspares unchanged; clean no fulltrace/readbacks',flush=True)
