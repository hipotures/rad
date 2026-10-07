// Validate the buffered trace schema and publication lifecycle without CUDA or model weights.
#include "strata/research/lab_trace.hpp"
#include <cassert>
int main(int argc,char** argv) {
    assert(argc==2);
    strata::research::Trace t;t.enabled=true;t.prefix=argv[1];
    std::vector<int32_t> resident={0,-1,1,-1};std::vector<float> usage(4,0);
    t.begin(resident,4,{128},usage);
    int32_t tokens[4]={17,18,19,20};t.begin_window(0,31,4,tokens);
    int32_t ids[3]={0,1,3},kind[3]={0,1,-1};t.token_base=2;
    t.decision(0,1,3,ids,kind,resident.data(),1,2,3,4,5);
    assert(t.entries.size()==3 && t.entries[0].path==0 && t.entries[1].path==1 && t.entries[2].path==-1);
    assert(t.entries[2].token==2 && t.entries[0].slot==0 && t.entries[1].slot==-1);
    t.promotion(0,1,0,0,128);assert(t.promotions[0].observed_ready==0);
    resident[0]=-1;t.ready(1,0);resident[1]=0;
    assert(t.promotions[0].observed_ready>=t.promotions[0].issue);
    t.accept(2);t.finish_window(3);t.output_ids={17,18,19};t.flush(resident,usage);
    assert(!t.active && t.final[1]==0 && t.windows[0].accepted==2 && t.windows[0].produced==3);
    return 0;
}
