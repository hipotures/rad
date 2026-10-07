#include "q4_history_policy.hpp"
extern "C" int select_q4(const float* heat,const float* fast,const int* resident,const unsigned long long* bytes,void* output){
 strata::research::Q4HistoryPolicy p;p.enabled=true;p.active=true;p.nl=48;p.ne=512;p.fast.assign(fast,fast+48*512);p.bytes.assign(bytes,bytes+48);std::vector<float> h(heat,heat+48*512);std::vector<int> r(resident,resident+48*512);struct S{float gain;int layer,in,out;};std::vector<S> result;p.select(h,r,result,96);std::copy(result.begin(),result.end(),(S*)output);return result.size();}
