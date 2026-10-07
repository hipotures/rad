#include "strata/research/q4_victim_model.hpp"
#include <iostream>
#include <iomanip>
using namespace strata::research;
int main(){VictimScorer s;s.reset();int l,n,ev;std::cout<<std::setprecision(17);while(std::cin>>l>>n>>ev){int32_t ids[40];for(int j=0;j<n;++j)std::cin>>ids[j];s.observe(l,ids,n,ev);int e;std::cin>>e;auto x=s.features(l,e,ev+1);for(double v:x)std::cout<<v<<" ";std::cout<<"\n";}}
