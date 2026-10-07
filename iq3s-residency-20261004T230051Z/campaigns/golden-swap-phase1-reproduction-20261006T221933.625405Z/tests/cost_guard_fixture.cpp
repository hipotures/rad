#include "strata/research/q4_oracle.hpp"
#include <iostream>
using namespace strata::research;
int main(){auto& o=q4_oracle;std::vector<int32_t>r(48*512,-1);std::vector<float>h(48*512,0);o.res=r.data();o.heat=h.data();o.blobs.assign(48,3072000);o.blobs[2]=3993600;for(int l:{4,30,46,47})o.blobs[l]=3584000;o.causal_policy=2;o.victim_threshold=.2;o.scorer.reset();o.victim_cache_at.fill(-1);o.ownership_generation.fill(0);r[20]=1;o.future.resize(48*512);o.incoming_view.index=&o.future;o.incoming_view.total_events=144;o.incoming_view.horizon=0;o.current=44;o.events.reserve(32);o.source=[](int,int){return (const uint8_t*)1;};o.spare[0][0]=0;q4_tape.windows.resize(3);
 for(auto& w:q4_tape.windows){w.T=1;for(int l=0;l<48;++l)for(int j=0;j<10;++j)w.routes.ids[l][j]=30;}q4_tape.current=q4_tape.windows[0];o.future[30]={{48,1}};auto& w=o.workers[0][0];w.dev=0;w.cls=0;o.plan(w);if(!o.events.empty()||o.scorer.rejections==0)return 2;
 o.future[30]={{48,20}};o.plan(w);if(o.events.size()!=1||o.events[0].incoming!=30||o.events[0].target!=48)return 3;o.plan(w);if(o.events.size()!=1)return 4;w.state.store(0);w.dev=-1;
 // A legal publication increments ownership generation; newly admitted colder resident must be considered.
 o.current=45;int first=o.victim(0,30,45);if(first!=20)return 5;r[21]=2;o.scorer.fast[20]=10;o.scorer.slow[20]=10;++o.ownership_generation[0];o.scorer.cache_version.fill(-1);int next=o.victim(0,30,45);if(next!=21)return 6;
 if(o.victim_view.audit.next_calls||o.victim_view.audit.count_calls)return 7;
 std::cout<<"PASS NO_SWAP copy floor, sufficient demand admission, duplicate candidate/inflight suppression, victim cache ownership invalidation, zero victim future queries\n";
}
