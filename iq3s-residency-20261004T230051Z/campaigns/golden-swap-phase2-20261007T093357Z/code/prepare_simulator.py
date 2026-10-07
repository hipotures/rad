from common import *
s=(P1/'scripts/offline.cpp').read_text()
s=s.replace('q4_oracle.current=ev;','q4_oracle.current=ev;q4_oracle.advance_lifetimes(ev);')
s=s.replace('q4_oracle.active=true;','q4_oracle.active=true;q4_oracle.incoming_event.assign(48*512,-1);')
s=s.replace('if(r[w.layer*512+w.expert]>=0){w.state.store(0);continue;}', 'e.copy_end=(uint64_t)(now*1e6)+1;if(q4_oracle.transaction_control&&q4_oracle.causal_policy&&(ev>e.target+48||q4_oracle.protected_count(w.dev,w.cls)>=q4_oracle.protection_cap)){e.status=8;++q4_oracle.late_abort;w.state.store(0);continue;}if(r[w.layer*512+w.expert]>=0){e.status=2;w.state.store(0);continue;}')
s=s.replace('latest_victim[w.layer*512+v]=w.index;', 'q4_oracle.note_publication(w.index,w.layer,w.expert,v,ev);q4_oracle.incoming_event[w.layer*512+w.expert]=w.index;latest_victim[w.layer*512+v]=w.index;')
s=s.replace('double staging=e.bytes/25e6,copy=e.bytes/13.2e6;', 'e.stage_begin=(uint64_t)(now*1e6)+1;e.stage_end=e.stage_begin+1;double staging=e.bytes/25e6,copy=e.bytes/13.2e6;')
s=s.replace('   now+=event_ms;', '''   int32_t service_slots[40];for(int j=0;j<q4_tape.current.T*10;++j)service_slots[j]=r[l*512+q4_tape.current.routes.ids[l][j]];q4_oracle.note_service(l,q4_tape.current.routes.ids[l],service_slots,q4_tape.current.T*10,ev);
   now+=event_ms;''')
a='  uint64_t pub=0,late=0,pbytes=0,repeated=0,unused_bytes=0;'
b='''  // Drain is charged as completed ordinary payload; never publish after observation end.
  for(auto& a:q4_oracle.workers)for(auto& w:a)if(w.dev>=0&&w.state.load()==1){auto& e=q4_oracle.events[w.index];e.copy_end=(uint64_t)(std::max(now,ready[w.dev][w.cls])*1e6)+1;e.status=4;w.state.store(0);}
  uint64_t outcome_bytes[4]={},outcome_n[4]={},early_bytes=0,distinct_uses=0,recurring=0;uint64_t decision_hash=1469598103934665603ull;
  for(size_t i=0;i<q4_oracle.events.size();++i){auto& e=q4_oracle.events[i];auto& a=q4_oracle.lifetimes[i];int category=!e.publish_ns?0:e.uses?1:a.evicted_at>=0?2:3;outcome_bytes[category]+=e.bytes;++outcome_n[category];early_bytes+=category==2&&a.evicted_at<e.target?e.bytes:0;distinct_uses+=a.distinct_uses;recurring+=a.distinct_uses>=2;for(uint64_t v:{uint64_t(e.layer),uint64_t(e.incoming),uint64_t(e.victim+1),uint64_t(e.published_at+1)}){decision_hash^=v;decision_hash*=1099511628211ull;}}
  const char* prefix=std::getenv("STRATA_Q4_SIM_LOG");if(prefix){auto write=[&](const char* name,auto& values){FILE* f=std::fopen((std::string(prefix)+name).c_str(),"wbx");require(f,"sim artifact exists");Q4Tape::io(f,values.data(),values.size(),true);std::fclose(f);};write("-admissions.bin",q4_oracle.events);write("-lifecycle.bin",q4_oracle.lifetimes);}
  uint64_t pub=0,late=0,pbytes=0,repeated=0,unused_bytes=0;'''
assert a in s;s=s.replace(a,b)
marker='<<",\\\"modeled_event_ms\\\":\"<<event_ms'
fields=['completed_unpublished_bytes','published_used_bytes','evicted_without_use_bytes','no_use_resident_end_bytes']
insert=''
for i,k in enumerate(fields):insert+='<<",\\\"'+k+'\\\":\"<<outcome_bytes['+str(i)+']'
for k,v in [('evicted_before_first_target_bytes','early_bytes'),('distinct_uses','distinct_uses'),('recurring_admissions','recurring'),('decision_hash','decision_hash'),('protection_veto','q4_oracle.protection_veto'),('capacity_veto','q4_oracle.capacity_veto'),('cost_veto','q4_oracle.cost_veto'),('victim_cost_veto','q4_oracle.victim_cost_veto'),('risk_veto','q4_oracle.risk_veto'),('lease_expired','q4_oracle.expiry_count'),('lease_released','q4_oracle.release_count'),('max_protected','q4_oracle.max_protected')]:insert+='<<",\\\"'+k+'\\\":\"<<'+v
assert marker in s;s=s.replace(marker,insert+marker)
(C/'code/offline.cpp').write_text(s)
