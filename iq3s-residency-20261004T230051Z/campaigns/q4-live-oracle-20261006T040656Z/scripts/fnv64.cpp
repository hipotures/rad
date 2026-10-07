#include <cstdint>
#include <cstddef>
extern "C" uint64_t q4_fnv(const uint8_t* p,size_t n,uint64_t x){for(size_t i=0;i<n;++i){x^=p[i];x*=1099511628211ull;}return x;}
