// Shared production candidate state logic, no private duplicated model of it.
#include "strata/research/persistent_runtime.hpp"
#include <cassert>
#include <cstdlib>
#include <iostream>
int main(){setenv("STRATA_LAB_PERSISTENT","1",1);strata::research::PersistentRuntime state;assert(state.enabled);std::vector<int32_t>r(48*512,-1);std::vector<uint64_t>blob(48,1048576),s0{1048576,2097152},s1=s0;r[0]=0;r[512]=1;r[25*512]=0;r[26*512]=1;assert(state.validate(r,blob,s0,s1));r[2*512]=0;assert(!state.validate(r,blob,s0,s1));r[2*512]=-1;blob[0]=3000000;assert(!state.validate(r,blob,s0,s1));blob[0]=1048576;
 state.begin();state.window=20;state.issue(2,3,0,0,0,1048576);r[0]=-1;assert(state.validate(r,blob,s0,s1));assert(!state.admissions[0].published&&r[2*512+3]<0);state.publish(2*512+3,0);r[2*512+3]=0;int ids[10]={3,3,3,3,3,3,3,3,3,3};state.window=21;state.observe(2,1,ids,r.data());assert(state.admissions[0].uses==10&&state.admissions[0].use_windows==1&&state.admissions[0].first_use>=state.admissions[0].published);state.window=22;state.observe(2,1,ids,r.data());assert(state.admissions[0].uses==20&&state.admissions[0].use_windows==2);
 bool caught=false;try{state.publish(2*512+3,0);}catch(const std::runtime_error&){caught=true;}assert(caught);caught=false;try{state.publish(25*512+5,0);}catch(const std::runtime_error&){caught=true;}assert(caught);
 state.issue(3,4,2,3,0,1048576);assert(state.admissions[0].evicted);r[2*512+3]=-1;state.observe(2,1,ids,r.data());assert(state.admissions[1].victim_uses==10);state.publish(3*512+4,0);r[3*512+4]=0;assert(state.validate(r,blob,s0,s1));std::cout<<"PASS shared state: fit, unique ownership, reserved slots, publication identity, repeated reuse, eviction, victim damage\n";}
