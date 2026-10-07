#include "strata/research/q4_oracle.hpp"
#include <iostream>
using namespace strata::research;
int main(){std::vector<int32_t> res(48*512,-1);std::vector<float> heat(48*512,0);std::vector<uint64_t> bytes(48,3072000);q4_oracle.res=res.data();q4_oracle.heat=heat.data();q4_oracle.blobs=bytes;q4_oracle.causal_policy=2;q4_tape.current.T=1;for(int l=0;l<48;++l)for(int j=0;j<10;++j)q4_tape.current.routes.ids[l][j]=j;
 res[0]=0;res[20]=1;res[21]=2;heat[21]=10;
 int32_t ids[10]={21,21,21,21,21,21,21,21,21,21};q4_oracle.scorer.observe(0,ids,10,0);
 if(q4_oracle.victim(0,22,48)!=20)return 2; // protected expert0 cannot win
 double a=q4_oracle.victim_value(0,20,48);q4_oracle.future.resize(48*512);q4_oracle.future[20]={{49,100},{100,200}};q4_oracle.victim_view.index=&q4_oracle.future;q4_oracle.victim_view.total_events=100000;
 if(a!=q4_oracle.victim_value(0,20,48))return 3;
 if(q4_oracle.victim_view.audit.next_calls||q4_oracle.victim_view.audit.count_calls)return 4;
 res[20]=-1;if(q4_oracle.victim(0,22,48)!=21)return 5;
 if(q4_oracle.scorer.accept(0,21,48,64,2,heat.data(),0))return 6; // real NO_SWAP
 res[21]=-1;if(q4_oracle.victim(0,22,48)!=-1)return 7;
 auto p=q4_oracle.scorer.risk(0,21,48,2,heat.data());for(double v:p)if(!std::isfinite(v))return 8;
 q4_oracle.scorer.loaded=true;q4_oracle.scorer.heads[0].bias=NAN;q4_oracle.scorer.scale.fill(1);q4_oracle.scorer.cache_version.fill(-1);auto bad=q4_oracle.scorer.risk(0,21,49,3,heat.data());if(q4_oracle.scorer.invalid!=1)return 9;for(double v:bad)if(!std::isfinite(v))return 10;
 std::cout<<"PASS invalid prediction causal fallback; protected victims, changing ownership, empty compatible set, NO_SWAP, unseen-future invariance, zero victim future queries\n";
}
