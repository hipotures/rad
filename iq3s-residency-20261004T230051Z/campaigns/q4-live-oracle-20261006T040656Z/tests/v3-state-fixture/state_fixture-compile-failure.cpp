// Initial-state contract tests: meaningful mutations fail; unwritten tail is excluded.
#include "strata/research/q4_state.hpp"
#include <filesystem>
#include <iostream>
using namespace strata::research;
int main(int argc,char** argv){
 if(argc!=2)return 2;std::filesystem::path dir=argv[1];std::filesystem::create_directories(dir);
 strata::core::SessionState s0{},s1{};strata::core::QsaState q{};strata::core::ModelGeometry g{};
 q.max_cells=64;q.n_pages=16;q.n_slots=1;q.kv_mode=1;q.kv_int8=true;
 uint8_t* keys=nullptr;uint8_t* vals=nullptr;uint16_t* ks=nullptr;uint16_t* vs=nullptr;
 auto alloc=[](auto** p,size_t n){Q4Tape::require(cudaHostAlloc(p,n,cudaHostAllocMapped)==cudaSuccess,"fixture pinned allocate");std::memset(*p,0,n);};
 alloc(&keys,16*2048);alloc(&vals,16*2048);alloc(&ks,16*64);alloc(&vs,16*64);
 q.host.k_q=keys;q.host.v_q=vals;q.host.k_scale=ks;q.host.v_scale=vs;
 q4_tape.active=true;q4_tape.path=(dir/"state-contract-tape").string();q4_tape.replaying=false;
 q4_state.begin(s0,s1,q,g,8);q4_tape.replaying=true;q4_state.begin(s0,s1,q,g,8);
 int passed=1;
 auto must_fail=[&](const char* name){bool failed=false;try{q4_state.begin(s0,s1,q,g,8);}catch(const std::exception& e){failed=true;std::cout<<"EXPECTED_REJECTION "<<name<<" "<<e.what()<<"\n";}Q4Tape::require(failed,"mutation escaped state contract");++passed;};
 s0.ple_token=99;must_fail("PLE_token");s0.ple_token=-1;
 keys[0]=7;must_fail("written_host_K");keys[0]=0;
 ks[0]=4;must_fail("written_host_K_scale");ks[0]=0;
 keys[2*2048]=23;q4_state.begin(s0,s1,q,g,8);++passed;keys[2*2048]=0; // Two written pages; this is the next unwritten page.
 q.max_cells=65;must_fail("KV_geometry");q.max_cells=64;
 q4_tape.path=(dir/"missing-sidecar").string();must_fail("missing_sidecar");
 cudaFreeHost(keys);cudaFreeHost(vals);cudaFreeHost(ks);cudaFreeHost(vs);
 q4_tape.active=false;std::cout<<"STATE_CONTRACT_TESTS_PASS "<<passed<<"\n";return 0;
}
