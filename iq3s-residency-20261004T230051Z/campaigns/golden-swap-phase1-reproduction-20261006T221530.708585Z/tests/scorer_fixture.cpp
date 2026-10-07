#include "strata/research/q4_victim_model.hpp"
#include <iostream>
#include <iomanip>
using namespace strata::research;
int main(int argc,char** argv){VictimScorer s;s.reset();if(argc<2||!s.load(argv[1]))return 2;int l,e,at;std::cout<<std::setprecision(17);while(std::cin>>l>>e>>at){std::array<double,13>x;for(auto& v:x)std::cin>>v;auto p=s.predict(x);for(auto v:p)std::cout<<v<<" ";std::cout<<"\n";}return 0;}
