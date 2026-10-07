// Shared selector for deterministic replay/runtime equivalence, no CUDA required.
#include "templates/persistent_policy.hpp"
extern "C" {
struct Row{double utility;int32_t layer,in,out_layer,out,slot,pad;uint64_t bytes;};
int select_persistent_bridge(const float*h,const float*p,const uint64_t*l,const uint64_t*b,const int32_t*r,
 const uint64_t*bl,const uint64_t*s0,int n0,const uint64_t*s1,int n1,uint64_t window,float alpha,Row*out){
 strata::research::PersistentConfig cfg;cfg.prediction_weight=alpha;
 auto rows=strata::research::select_persistent(h,p,l,b,r,48,512,25,std::vector<uint64_t>(bl,bl+48),std::vector<uint64_t>(s0,s0+n0),std::vector<uint64_t>(s1,s1+n1),window,96,cfg);
 for(size_t i=0;i<rows.size();++i){auto&v=rows[i];out[i]={v.utility_us,v.layer,v.in,v.out_layer,v.out,v.slot,0,v.bytes};}return rows.size();
}
}
