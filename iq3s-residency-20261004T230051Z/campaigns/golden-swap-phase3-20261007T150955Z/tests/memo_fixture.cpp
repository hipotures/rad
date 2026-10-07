#include "strata/research/q4_oracle.hpp"
#include <random>
#include <iostream>
using namespace strata::research;
int main(){
 Q4Oracle o;o.causal_policy=1;o.planner_opt=true;o.future.resize(48*512);std::mt19937 gen(730071);
 q4_tape.windows.resize(80);o.incoming_view.index=&o.future;o.incoming_view.total_events=3840;
 for(int key=0;key<48*512;++key)for(int wi=0;wi<80;++wi)if(gen()%7==0)o.future[key].push_back({wi*48+key/512,1+int(gen()%40)});
 uint64_t checked=0;
 for(int at=0;at<3840;++at){o.current=at;int until=std::min(3839,at+768);
  for(int j=0;j<128;++j){int key=gen()%(48*512);auto expected=std::pair{o.next(key/512,key%512,at+1),o.count(key/512,key%512,at+1,until)};auto actual=o.demand(key/512,key%512,at,until);Q4Tape::require(actual==expected,"memo differs from role-typed oracle");++checked;
   // Repeated same-event lookup must hit without inheriting mutable policy state.
   ++o.ownership_generation[key/512];++o.protection_version[key/512];++o.scorer.versions[key/512];Q4Tape::require(o.demand(key/512,key%512,at,until)==expected,"policy state corrupted incoming facts");}
 }
 o.current=0;auto expected=std::pair{o.next(0,0,1),o.count(0,0,1,768)};Q4Tape::require(o.demand(0,0,0,768)==expected,"rewind invalidation");
 o.incoming_horizon=4;o.incoming_view.horizon=4;Q4Tape::require(o.demand(0,0,0,768)==std::pair{o.next(0,0,1),o.count(0,0,1,768)},"finite information fallback");
 for(auto& m:o.demand_memo)m={};o.incoming_horizon=0;o.incoming_view.horizon=0;o.future[0]={{1,10},{768,2},{769,3}};o.current=0;
 Q4Tape::require(o.demand(0,0,0,768)==std::pair{1,12},"inclusive upper/lower");o.current=1;Q4Tape::require(o.demand(0,0,1,769)==std::pair{768,5},"lower removal/upper addition same event");
 std::cout<<"PASS exact query parity checked="<<checked<<" hits="<<o.memo_hits<<" lower="<<o.memo_lower<<" upper="<<o.memo_upper<<" rewind="<<o.memo_rewind<<" bytes="<<sizeof(o.demand_memo)<<"\n";
}
