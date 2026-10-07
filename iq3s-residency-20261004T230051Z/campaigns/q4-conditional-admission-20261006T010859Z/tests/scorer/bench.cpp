#include "conditional_constants.hpp"
#include <vector>
#include <fstream>
#include <chrono>
#include <cstdio>
#include <cmath>
int main(int argc,char**argv){std::ifstream f(argv[1],std::ios::binary),e(argv[2],std::ios::binary);f.seekg(0,std::ios::end);size_t n=f.tellg()/sizeof(float)/48;f.seekg(0);std::vector<float>x(n*48);std::vector<double>expected(n);f.read((char*)x.data(),x.size()*4);e.read((char*)expected.data(),n*8);double maxerr=0;for(size_t i=0;i<n;++i)maxerr=std::max(maxerr,std::abs(q4_conditional::probability(x.data()+i*48)-expected[i]));volatile double sum=0;auto start=std::chrono::steady_clock::now();for(int q=0;q<1000;++q)for(size_t i=0;i<n;++i)sum=sum+q4_conditional::probability(x.data()+i*48);double ns=std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-start).count()/(1000*n);std::printf("{\"rows\":%zu,\"ns_per_action\":%.9g,\"maximum_probability_error\":%.9g,\"sum\":%.9g}\n",n,ns,maxerr,(double)sum);return maxerr<1e-10?0:1;}
