"""One minimal, asserted information-channel change over preserved live-oracle v3."""
from pathlib import Path
C=Path(__file__).resolve().parents[1]
p=C/'src/decomposition-v1/include/strata/research/q4_oracle.hpp'
s=p.read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
replace('#include "strata/research/q4_tape.hpp"','#include "strata/research/q4_tape.hpp"\n#include "strata/research/q4_future_view.hpp"')
replace('int horizon=0,strategy=0;','int horizon=0,strategy=0;int incoming_horizon=0,victim_horizon=0;static constexpr int eligibility=64;IncomingFutureView incoming_view;VictimFutureView victim_view;')
replace('for(auto& a:spare)a.fill(-1);}', '''for(auto& a:spare)a.fill(-1);
  incoming_horizon=victim_horizon=horizon;
  auto read_h=[](const char* key,int fallback){const char* value=std::getenv(key);if(!value)return fallback;std::string v(value);if(v=="full")return 0;int h=std::atoi(value);require(h==4||h==16||h==64||h==256,"unsupported I/V horizon");return h;};
  incoming_horizon=read_h("STRATA_Q4_ORACLE_INCOMING",incoming_horizon);victim_horizon=read_h("STRATA_Q4_ORACLE_VICTIM",victim_horizon);
 }''')
replace('setup_ns=ns()-t;std::fprintf', 'incoming_view.index=victim_view.index=&future;incoming_view.horizon=incoming_horizon;victim_view.horizon=victim_horizon;incoming_view.total_events=victim_view.total_events=(int)q4_tape.windows.size()*48;setup_ns=ns()-t;std::fprintf')
start=s.index(' int next(');end=s.index(' bool protected_now',start)
s=s[:start]+''' // Scheduler future reads are role-typed. The replay engine retains its own full tape.
 int next(int l,int e,int at)const{return incoming_view.next(l*512+e,at,std::max(0,current)).event;}
 int count(int l,int e,int at,int until)const{return incoming_view.count(l*512+e,at,until,std::max(0,current));}
 double victim_value(int l,int e,int at)const {
  auto nx=victim_view.next(l*512+e,at,at);
  if(nx.status==FutureStatus::Known)return double(nx.event-at);
  if(nx.status==FutureStatus::FiniteTapeEnd)return 1e12;
  // Unknown beyond V is NOT never. Fixed causal heat fallback, identical in all arms.
  return double(victim_horizon+1)-std::log1p(std::max(0.f,heat[l*512+e]));
 }
''' + s[end:]
replace('int nx=next(l,e,at);double value;if(!horizon)value=nx<0?1e12:(nx-at);else value=nx<0?double(horizon+1)-std::log1p(std::max(0.f,heat[l*512+e])):double(nx-at);','double value=victim_value(l,e,at);')
replace('int nx=next(l,e,0);double val=!horizon?(nx<0?1e12:nx):(nx<0?double(horizon+1)-std::log1p(std::max(0.f,heat[l*512+e])):nx);','double val=victim_value(l,e,0);')
replace('int limit=horizon?horizon:64;', 'int limit=incoming_horizon?std::min(eligibility,incoming_horizon):eligibility;')
replace('int vn=next(l,v,current);','int vn=victim_view.next(l*512+v,current,current).event;')
replace('int utility_end=horizon?current+horizon:std::min((int)q4_tape.windows.size()*48-1,current+768);int uses=count(l,expert,current+1,utility_end),damage=count(l,v,current+1,utility_end);', 'int utility_end=std::min((int)q4_tape.windows.size()*48-1,current+768);int uses=count(l,expert,current+1,utility_end),damage=victim_view.count(l*512+v,current+1,utility_end,current);')
replace('planner_ns=publication_ns=drain_ns=restore_ns=ready_entries=late_entries=redundant=protected_reject=opportunities=0;', 'planner_ns=publication_ns=drain_ns=restore_ns=ready_entries=late_entries=redundant=protected_reject=opportunities=0;incoming_view.audit={};victim_view.audit={};')
replace('active=false;tracked=false;\n }', '''std::fprintf(stderr,"Q4_INFORMATION_END E=64 I=%d V=%d protection=full_current_window incoming_next=%llu incoming_count=%llu incoming_unknown=%llu incoming_max_visible=%d victim_next=%llu victim_count=%llu victim_unknown=%llu victim_max_visible=%d eligibility_coupled=%d first_feasible=1 utility_rank_effective=0\\n",incoming_horizon,victim_horizon,(unsigned long long)incoming_view.audit.next_calls,(unsigned long long)incoming_view.audit.count_calls,(unsigned long long)incoming_view.audit.unknown,incoming_view.audit.max_visible_ahead,(unsigned long long)victim_view.audit.next_calls,(unsigned long long)victim_view.audit.count_calls,(unsigned long long)victim_view.audit.unknown,victim_view.audit.max_visible_ahead,incoming_horizon&&incoming_horizon<64);
  active=false;tracked=false;
 }''')
p.write_text(s)
print('Patched independent I/V queries; unchanged scheduler, spares, worker and math.')
