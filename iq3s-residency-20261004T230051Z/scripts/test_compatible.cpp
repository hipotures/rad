// Synthetic owner/size/selection/publication invariants; no model or GPU mutation.
#include "strata/research/compatible_policy.hpp"
#include <cassert>
#include <cstring>
#include <set>
int main() {
    std::vector<float> heat(16,0);heat[5]=10;heat[2]=5;heat[10]=7;
    std::vector<int32_t> res={0,1,-1,-1,2,-1,-1,-1,0,2,-1,-1,1,-1,-1,-1};
    const auto before=res;std::vector<uint64_t> blobs={32,64,64,32},s0={32,64,64},s1={64,32,64};
    auto swaps=strata::research::select_compatible(heat.data(),res.data(),4,4,2,blobs,s0,s1,2);
    assert(swaps.size()==2 && swaps[0].layer==1 && swaps[0].out_layer==0 && swaps[0].in==1);
    assert(res==before);std::set<std::pair<int,int>> seen;
    for(const auto& swap:swaps) {
        const int gpu=swap.layer>=2;assert(gpu==(swap.out_layer>=2));
        const auto& bytes=gpu?s1:s0;const int victim=swap.out_layer*4+swap.out,inc=swap.layer*4+swap.in;
        const int slot=res[victim];assert(slot>=0 && res[inc]<0 && blobs[swap.layer]<=bytes[slot]);
        assert(seen.insert({gpu,slot}).second);
        // Between-window withdrawal, incomplete copy and complete publication.
        res[victim]=-1;assert(res[inc]<0);bool ready=false;
        if(ready)res[inc]=slot;assert(res[inc]<0);
        ready=true;if(ready)res[inc]=slot;assert(res[inc]==slot);
    }
    auto invalid=before;invalid[0]=9;
    assert(strata::research::select_compatible(heat.data(),invalid.data(),4,4,2,blobs,s0,s1,2).empty());
    assert(strata::research::select_compatible(heat.data(),before.data(),4,4,0,blobs,s0,s1,2).empty());
    assert(strata::research::select_compatible(heat.data(),before.data(),4,4,2,blobs,s0,s1,0).empty());
    heat.assign(16,0);assert(strata::research::select_compatible(heat.data(),before.data(),4,4,2,blobs,s0,s1,2).empty());
}
