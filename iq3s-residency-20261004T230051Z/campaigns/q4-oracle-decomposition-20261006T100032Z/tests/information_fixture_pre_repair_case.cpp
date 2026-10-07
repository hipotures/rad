#include "strata/research/q4_oracle.hpp"
#include "legacy_oracle.hpp"
#include <iostream>
using namespace strata::research;
void ok(bool b,const char* why){Q4Tape::require(b,why);}
int main(){
 std::vector<std::vector<std::pair<int,int>>> a(24576),b(24576);
 a[1]={{104,1},{116,2},{164,3},{165,5},{500,9}};b[1]={{104,1},{116,2},{164,3},{170,999},{700,9999}};
 IncomingFutureView i{&a,64,1000};IncomingFutureView j{&b,64,1000};
 ok(i.next(1,105,100).event==116,"inclusive future next");ok(i.next(1,164,100).event==164,"H inclusive endpoint");
 ok(i.next(1,165,100).status==FutureStatus::UnknownBeyondHorizon,"H+1 unknown");
 ok(i.count(1,101,999,100)==j.count(1,101,999,100),"incoming suffix noninterference");
 VictimFutureView v{&a,64,1000},w{&b,64,1000};ok(v.next(1,165,100).status==w.next(1,165,100).status,"victim suffix noninterference");
 i.horizon=0;ok(i.next(1,165,100).event==165,"full can observe suffix");
 v.horizon=16;ok(v.next(1,117,100).status==FutureStatus::UnknownBeyondHorizon,"victim16 unknown");
 i.horizon=0;v.horizon=4;ok(i.next(1,105,100).event==116&&v.next(1,105,100).event==-1,"roles remain independent");
 v.horizon=64;ok(v.next(1,800,950).status==FutureStatus::FiniteTapeEnd,"finite tape end distinct from unknown");
 std::cout<<"PASS typed-view-endpoints-suffix-and-role-isolation\n";
 ok(q4_tape.replaying,"fixture requires real preserved tape");
 std::vector<int32_t> r=q4_tape.initial_res,lr=r;std::vector<float> heat=q4_tape.initial_heat;std::vector<uint64_t> sizes(48,3072000);sizes[2]=3993600;for(int l:{4,30,46,47})sizes[l]=3584000;
 Q4Oracle o;LegacyOracle old;o.configured=old.configured=true;
 auto src=[](int,int){return (const uint8_t*)1;};auto dst=[](int,int){return (void*)1;};
 o.runtime(r.data(),heat.data(),sizes,{nullptr,nullptr},src,dst);old.runtime(lr.data(),heat.data(),sizes,{nullptr,nullptr},src,dst);
 o.events.reserve(10000);old.events.reserve(10000);int comparisons=0;
 for(int at=0;at<(int)q4_tape.windows.size()*48;at+=257){q4_tape.index=at/48;q4_tape.current=q4_tape.windows[at/48];o.current=old.current=at;
  for(int l:{0,2,4,24,30,47}){int incoming=0;o.incoming_view.horizon=0;o.victim_view.horizon=0;ok(o.victim(l,incoming,at)==old.victim(l,incoming,at),"F/F original victim equivalence");}
  for(int d=0;d<2;++d)for(int c=0;c<3;++c){if(d==1&&c==2)continue;auto& x=o.workers[d][c];auto& y=old.workers[d][c];x.dev=y.dev=d;x.cls=y.cls=c;o.spare[d][c]=old.spare[d][c]=0;
   const size_t before=o.events.size(),lb=old.events.size();o.plan(x);old.plan(y);ok((o.events.size()>before)==(old.events.size()>lb),"F/F issue equivalence");
   OracleEvent full{};if(o.events.size()>before){full=o.events.back();auto e=old.events.back();ok(full.layer==e.layer&&full.incoming==e.incoming&&full.target==e.target,"F/F candidate equivalence");}
   x.state.store(0);y.state.store(0);o.incoming_horizon=o.incoming_view.horizon=64;const size_t cb=o.events.size();o.plan(x);
   ok((o.events.size()>cb)==(o.events.size()>before+((o.events.size()>cb)?1:0)),"I64 issue equivalence");
   if(o.events.size()>cb){auto e=o.events.back();ok(e.layer==full.layer&&e.incoming==full.incoming&&e.target==full.target,"incoming64 first-feasible equivalence");}
   x.state.store(0);o.incoming_horizon=o.incoming_view.horizon=0;++comparisons;
  }
 }
 for(auto& row:o.workers)for(auto& x:row)x.dev=-1;for(auto& row:old.workers)for(auto& x:row)x.dev=-1;
 std::cout<<"PASS original-full-and-incoming64-decision-equivalence comparisons="<<comparisons<<"\n";
 // Role changes must not retain cached full victim/incoming scores.
 o.current=100;o.incoming_view.horizon=64;o.victim_view.horizon=4;o.victim_horizon=4;
 o.future[1]={{104,1},{105,1},{500,1}};
 ok(o.next(0,1,101)==104,"incoming role has64");
 ok(o.victim_view.next(1,105,100).status==FutureStatus::UnknownBeyondHorizon,"same identity reclassified victim has4");
 o.future[1]={{104,1},{600,999}};ok(o.victim_view.next(1,105,100).status==FutureStatus::UnknownBeyondHorizon,"victim suffix after role change independent");
 std::fill(r.begin(),r.end(),-1);r[1]=1;r[2]=2;heat[1]=0;heat[2]=100;
 for(int z=0;z<10;++z)q4_tape.current.routes.ids[0][z]=0;
 o.future[1]={{105,1},{500,2}};o.future[2]={{150,1},{600,2}};
 int victim_before=o.victim(0,3,100);ok(victim_before==1,"unknown victim uses causal coldness, not exact next-use");
 o.future[1]={{700,999}};o.future[2]={{106,999}};
 ok(o.victim(0,3,100)==victim_before,"bounded victim DECISION suffix invariant with same state and P");
 o.incoming_view.horizon=0;ok(o.next(0,1,101)==700,"identity incoming full view differs legitimately");
 ok(o.victim(0,3,100)==victim_before,"role change cannot cache full incoming utility into victim");
 std::cout<<"PASS reclassified-identity-no-cached-score-leak\n";
}
