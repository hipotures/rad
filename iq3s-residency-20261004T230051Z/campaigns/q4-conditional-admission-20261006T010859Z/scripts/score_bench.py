"""CPU-only single-action scorer cost/parity, no runtime integration or GPU work."""
from pathlib import Path
import json,subprocess,time,hashlib,numpy as np
from campaign import C,load,save
from data import episode
from train import predict,sigmoid
def main():
 model=load(C/'checkpoints/conditional-logistic.json');a=np.array(model['active']);beta=np.array(model['beta']);mean=np.array(model['mean']);std=np.array(model['std']);platt=np.array(model['platt'])
 coeff=np.zeros(48);coeff[a]=beta[1:]/std[a];intercept=beta[0]-np.sum(coeff*mean)
 # Collapse Platt calibration into the CPU dot product (same logit mathematics).
 coeff*=platt[1];intercept=intercept*platt[1]+platt[0]
 x,*_=episode('code-1');features=x.astype(np.float32);p=sigmoid(intercept+features@coeff)
 out=C/'tests/scorer';out.mkdir(exist_ok=True);features.tofile(out/'features.bin');p.astype('<f8').tofile(out/'expected.bin')
 coeffs=','.join(format(float(v),'.17g') for v in coeff)
 header='#pragma once\n#include <cmath>\nnamespace q4_conditional {\ninline constexpr double intercept='+format(float(intercept),'.17g')+';\ninline constexpr double coef[48]={'+coeffs+'};\ninline double probability(const float* x){double z=intercept;for(int i=0;i<48;++i)z+=coef[i]*x[i];return 1/(1+std::exp(-z));}\n}\n'
 (C/'checkpoints/conditional_constants.hpp').write_text(header)
 source='''#include "conditional_constants.hpp"
#include <vector>
#include <fstream>
#include <chrono>
#include <cstdio>
#include <cmath>
int main(int argc,char**argv){std::ifstream f(argv[1],std::ios::binary),e(argv[2],std::ios::binary);f.seekg(0,std::ios::end);size_t n=f.tellg()/sizeof(float)/48;f.seekg(0);std::vector<float>x(n*48);std::vector<double>expected(n);f.read((char*)x.data(),x.size()*4);e.read((char*)expected.data(),n*8);double maxerr=0;for(size_t i=0;i<n;++i)maxerr=std::max(maxerr,std::abs(q4_conditional::probability(x.data()+i*48)-expected[i]));volatile double sum=0;auto start=std::chrono::steady_clock::now();for(int q=0;q<1000;++q)for(size_t i=0;i<n;++i)sum=sum+q4_conditional::probability(x.data()+i*48);double ns=std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-start).count()/(1000*n);std::printf("{\\"rows\\":%zu,\\"ns_per_action\\":%.9g,\\"maximum_probability_error\\":%.9g,\\"sum\\":%.9g}\\n",n,ns,maxerr,(double)sum);return maxerr<1e-10?0:1;}
'''
 (out/'bench.cpp').write_text(source);cmd=['g++','-O3','-std=c++17','-I'+str(C/'checkpoints'),str(out/'bench.cpp'),'-o',str(out/'bench')];t=time.time();compile=subprocess.run(cmd,capture_output=True,text=True,timeout=90);save(out/'compile.json',{'command':cmd,'returncode':compile.returncode,'stdout':compile.stdout,'stderr':compile.stderr,'wall_s':time.time()-t});assert compile.returncode==0
 run=subprocess.run([str(out/'bench'),str(out/'features.bin'),str(out/'expected.bin')],capture_output=True,text=True,timeout=60);save(out/'run.json',{'command':run.args,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr});assert run.returncode==0,run.stdout
 result=json.loads(run.stdout);result['scope']='C++ CPU single-row sigmoid+48feature dot product only. Does not include runtime history extraction/selection, which remains separately diagnosed. No measured inference speed.';result['header_sha256']=hashlib.sha256((C/'checkpoints/conditional_constants.hpp').read_bytes()).hexdigest();result['checkpoint_sha256']=hashlib.sha256((C/'checkpoints/conditional-logistic.json').read_bytes()).hexdigest();save(C/'phase-b/scorer-cost.json',result);print('CPU_SCORER',json.dumps(result),flush=True)
if __name__=='__main__':main()
