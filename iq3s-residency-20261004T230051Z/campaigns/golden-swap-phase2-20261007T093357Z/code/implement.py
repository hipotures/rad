"""Apply the bounded transaction treatment to verified Phase 1 source."""
from pathlib import Path
import shutil,json
C=Path(__file__).resolve().parents[1]
W=Path('/srv/ai/work/rad/golden-swap-phase2/20261007T093357Z');S=W/'repos/runtime'
p=S/'include/strata/research/q4_oracle.hpp';s=p.read_text()
def replace(a,b):
 global s
 assert a in s,a[:80];s=s.replace(a,b)
replace('struct Q4Oracle {','''// Buffered generation lifecycle evidence; logical units are routed-layer invocations.
struct LifecycleEvent {int32_t generation,first_use,last_use,distinct_uses,evicted_at,released_at,expiry,reason;};
struct Q4Oracle {''')
replace(' int32_t* res=nullptr;', ''' bool transaction_control=false;int post_use_events=0;static constexpr int protection_cap=16;
 std::array<int,48*512> leases{};std::array<int,48> protection_version{};
 std::vector<LifecycleEvent> lifetimes;
 mutable uint64_t protection_veto=0,empty_victims=0,enumeration_ns=0,enumerated=0;
 uint64_t capacity_veto=0,cost_veto=0,victim_cost_veto=0,risk_veto=0,expiry_count=0,release_count=0,late_abort=0;
 uint64_t history_ns=0;int max_protected=0;
 int32_t* res=nullptr;''')
replace('Q4Oracle(){victim_cache_at.fill(-1);','''Q4Oracle(){leases.fill(-1);const char* tc=std::getenv("STRATA_Q4_TRANSACTION_CONTROL");transaction_control=tc&&tc[0]=='1';const char* pu=std::getenv("STRATA_Q4_POST_USE_EVENTS");post_use_events=pu?std::atoi(pu):0;require(post_use_events==0||post_use_events==48,"unsupported post-use interval");victim_cache_at.fill(-1);''')
marker=' int victim(int l,int incoming,int at)const{'
methods=''' // The next verifier layer milestone occurs after preceding GPU expert reads and post work.
 // Actual service is observed from the published plan; policy release waits for that next milestone.
 bool lease_protected(int l,int e)const{return transaction_control&&causal_policy&&leases[l*512+e]>=0;}
 int protected_count(int d,int c)const{int n=0;for(int l=d*24;l<(d+1)*24;++l)if(cls(l)==c)for(int e=0;e<512;++e)n+=leases[l*512+e]>=0;return n;}
 void advance_lifetimes(int at){if(!transaction_control||!causal_policy)return;for(int key=0;key<48*512;++key){int i=leases[key];if(i<0)continue;auto& a=lifetimes[i];if((a.first_use>=0&&at>a.first_use+post_use_events)||at>a.expiry){a.released_at=at;a.reason=a.first_use>=0?1:2;release_count+=a.reason==1;expiry_count+=a.reason==2;leases[key]=-1;++protection_version[key/512];++ownership_generation[key/512];}}}
 void note_publication(int i,int l,int expert,int victim,int at){if(i>=int(lifetimes.size()))lifetimes.resize(i+1,{-1,-1,-1,0,-1,-1,-1,0});int old=incoming_event[l*512+victim];if(old>=0&&old<int(lifetimes.size()))lifetimes[old].evicted_at=at;leases[l*512+victim]=-1;auto& a=lifetimes[i];a.generation=i;a.expiry=events[i].target+48;if(transaction_control&&causal_policy){leases[l*512+expert]=i;++protection_version[l];max_protected=std::max(max_protected,protected_count(l/24,cls(l)));}}
 void note_service(int l,const int32_t* ids,const int32_t* slots,int n,int at){int seen[512]={};for(int j=0;j<n;++j){int e=ids[j],i=incoming_event[l*512+e];if(slots[j]<0||i<0||seen[e]++)continue;auto& a=lifetimes[i];if(a.first_use<0)a.first_use=at;a.last_use=at;++a.distinct_uses;}}
'''
replace(marker,methods+marker)
replace('&&!protected_now(l,b))','&&!protected_now(l,b)&&!lease_protected(l,b))')
replace('int best=-1;double score=-1e100;for(int e=0;e<512;++e){if(res[l*512+e]<0||e==incoming||protected_now(l,e))continue;', '''int best=-1;double score=-1e100;uint64_t enumeration_start=ns();for(int e=0;e<512;++e){++enumerated;if(res[l*512+e]<0||e==incoming||protected_now(l,e))continue;if(lease_protected(l,e)){++protection_veto;continue;}''')
replace('if(causal_policy){victim_cache_at[l]=at;', 'enumeration_ns+=ns()-enumeration_start;if(best<0)++empty_victims;if(causal_policy){victim_cache_at[l]=at;')
replace('events.clear();layers.clear();natives.clear();','events.clear();lifetimes.clear();leases.fill(-1);protection_version.fill(0);capacity_veto=cost_veto=victim_cost_veto=risk_veto=expiry_count=release_count=late_abort=history_ns=0;protection_veto=empty_victims=enumeration_ns=enumerated=0;max_protected=0;layers.clear();natives.clear();')
replace('events.reserve(q4_tape.header.output_budget*240);','events.reserve(q4_tape.header.output_budget*240);lifetimes.reserve(q4_tape.header.output_budget*240);')
replace('auto& e=events[w.index];if(res[w.layer*512+w.expert]>=0)', '''auto& e=events[w.index];if(transaction_control&&causal_policy&&current>e.target+48){++late_abort;retire(w,8);return;}if(transaction_control&&causal_policy&&protected_count(w.dev,w.cls)>=protection_cap){++capacity_veto;retire(w,9);return;}if(res[w.layer*512+w.expert]>=0)''')
replace('v!=w.expert&&!protected_now(w.layer,v)', 'v!=w.expert&&!protected_now(w.layer,v)&&!lease_protected(w.layer,v)')
replace('incoming_event[w.layer*512+w.expert]=w.index;', 'note_publication(w.index,w.layer,w.expert,v,current);incoming_event[w.layer*512+w.expert]=w.index;')
replace('events.push_back(e);', 'events.push_back(e);lifetimes.push_back({int(events.size()-1),-1,-1,0,-1,-1,target+48,0});')
replace('void plan(Worker& w){if(w.state.load()!=0)return;', '''void plan(Worker& w){if(w.state.load()!=0)return;if(transaction_control&&causal_policy&&protected_count(w.dev,w.cls)>=protection_cap){++capacity_veto;return;}''')
replace('if(causal_policy&&double(uses)<copy_entries){++scorer.rejections;', 'if(causal_policy&&double(uses)<copy_entries){++cost_veto;++scorer.rejections;')
replace('if(!scorer.accept(l,v,current,target,causal_policy,heat,victim_threshold))continue;', 'if(!scorer.accept(l,v,current,target,causal_policy,heat,victim_threshold)){++risk_veto;continue;}')
replace('if(double(uses)<copy_entries+victim_loss){++scorer.rejections;', 'if(double(uses)<copy_entries+victim_loss){++victim_cost_veto;++scorer.rejections;')
replace('uint64_t t=ns();if(active){if(last_event', 'uint64_t t=ns();if(active){advance_lifetimes(current);if(last_event')
replace('layers.push_back(a);}', 'layers.push_back(a);if(active)note_service(l,a.ids,a.slots,n,int(a.event));}')
replace('scorer.observe(a.layer,a.ids,a.n,(int)a.event);','uint64_t ht=ns();scorer.observe(a.layer,a.ids,a.n,(int)a.event);history_ns+=ns()-ht;')
replace('write("-native.bin",natives);','write("-native.bin",natives);write("-lifecycle.bin",lifetimes);')
replace('  active=false;tracked=false;', '''  std::fprintf(stderr,"Q4_TC_END enabled=%d post_use_events=%d cap_per_device_class=16 max_protected=%d protection_veto=%llu empty_victims=%llu capacity_veto=%llu cost_veto=%llu victim_cost_veto=%llu risk_veto=%llu expired=%llu released=%llu late_abort=%llu history_ms=%.3f enumeration_ms=%.3f enumerated=%llu\\n",transaction_control&&causal_policy,post_use_events,max_protected,(unsigned long long)protection_veto,(unsigned long long)empty_victims,(unsigned long long)capacity_veto,(unsigned long long)cost_veto,(unsigned long long)victim_cost_veto,(unsigned long long)risk_veto,(unsigned long long)expiry_count,(unsigned long long)release_count,(unsigned long long)late_abort,history_ns/1e6,enumeration_ns/1e6,(unsigned long long)enumerated);
  active=false;tracked=false;''')
p.write_text(s)
for f in ['logistic.txt','logistic.json']:shutil.copy2(C.parent/'golden-swap-phase1-20261006T200037Z'/'models'/f,C/'models'/f)
