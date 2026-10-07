// Validate bounded host signal collection and record schema without a model.
#include "strata/research/lab_signals.hpp"
#include <cassert>
int main(int argc,char** argv) {
    assert(argc==2);
    using namespace strata::research;
    signals.enabled=false;signals.activation(5,1,nullptr);
    assert(signals.activations.empty());
    signals.enabled=true;signals.prefix=argv[1];signals.width=4;signals.begin();
    trace.active=false;float x[8]={1,2,3,4,5,6,7,8};signals.activation(5,2,x);
    assert(signals.activations.empty());
    trace.active=true;trace.request=1;trace.window=7;trace.token_base=2;
    trace.windows.resize(1);signals.activation(4,2,x);
    assert(signals.activations.empty());
    signals.activation(5,2,x);
    assert(signals.activations.size()==1 && signals.values.size()==8);
    assert(signals.activations[0].token_base==2 && signals.activations[0].window==7);
    assert(signals.values[7]==8);
    trace.windows.resize(65);signals.activation(5,2,x);
    assert(signals.activations.size()==1);
    signals.cpu(0,0,25,0,11,13,0);assert(signals.boundaries.size()==1);
    assert(signals.boundaries[0].end_ns==13);
    std::filesystem::create_directories(std::filesystem::path(signals.prefix).parent_path());
    signals.flush();signals.begin();
    assert(signals.activations.empty() && signals.values.empty() && signals.boundaries.empty());
    return 0;
}
