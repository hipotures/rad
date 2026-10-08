// RaD: arbitrary rational-beta profiles of transitions from an executed joint word.
// Input is the multiset reconstructed independently from XOR operations and events.
// Signed-class frames are the actual word frames, not scalar-DAG proxies.
// Format: <6I2Q>, then each frame <QI> forced/rank + h signed int8 labels,
// then <2Iq> transition pairs/counts. Nested-space/rank closure is a separate
// independent compiler receipt bound to the full input digest.
// This is newly authored code. Binary I/O uses the credited Apache-2.0 helper.
// Every NE rank is certified from a prime-product integer-minor bound;
// no diagonal-mask or correction-rank shortcut is assumed.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
#include <boost/multiprecision/cpp_int.hpp>
using U=uint32_t;using V=uint64_t;using I=int64_t;
using boost::multiprecision::cpp_int;
#include "binary_io.hpp"

struct Frame {V forced=0;cpp_int den=1;U rank=0;std::vector<int8_t> symbols;std::vector<cpp_int> numerator;};
struct Transition {U a,b,r,primes=0;I count;cpp_int denominator,entry_bound,minor_bound;std::vector<uint8_t> corner;std::vector<std::pair<U,U>> pivots;};
U multiply(U a,U b,U p){return V(a)*b%p;}
U power(U a,U b,U p){U out=1;for(;b;b>>=1,a=multiply(a,a,p))if(b&1)out=multiply(out,a,p);return out;}
U subtract(U a,U b,U p){return a>=b?a-b:a+p-b;}
bool prime(U p){if(p<2)return false;if(!(p&1))return p==2;for(U d=3;V(d)*d<=p;d+=2)if(p%d==0)return false;return true;}
cpp_int ipower(cpp_int a,U n){cpp_int z=1;for(;n;n>>=1,a*=a)if(n&1)z*=a;return z;}
unsigned bits(const cpp_int&x){assert(x>0);return boost::multiprecision::msb(x)+1;}

cpp_int gcd(cpp_int a,cpp_int b){if(a<0)a=-a;if(b<0)b=-b;while(b!=0){cpp_int r=a%b;a=b;b=r;}return a;}
void make_matrix(Frame&F,U h,const cpp_int&betaN,const cpp_int&betaD,U special){
 F.numerator.assign(h*h,0);if(special==0)return;
 if(special==1){for(U i=0;i<h;i++)F.numerator[i*h+i]=1;return;}
 cpp_int wN=3*betaN,wD=betaD,gN=9*betaN-betaD,gD=3*(betaD-h*betaN);
 assert(wD>0&&gD!=0);if(gD<0){gD=-gD;gN=-gN;}
 cpp_int g=gcd(wN,wD);wN/=g;wD/=g;g=gcd(gN,gD);gN/=g;gD/=g;
 U f=popcount64(F.forced);
 if(f==3){
  assert(F.rank==1);F.den=2*wD*gD;
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){
   I fi=(F.forced>>i)&1,fj=(F.forced>>j)&1;
   F.numerator[i*h+j]=(wD*fi-wN)*(gD*fj+gN);
  }
 }else{
  assert(f==1||f==2);I localS=3-f;
  std::map<U,std::pair<I,I>> classes;
  for(I x:F.symbols)if(std::abs(x)>1){auto&c=classes[std::abs(x)];c.first++;c.second+=x>0?1:-1;}
  assert(classes.size()==F.rank);V K=1;
  for(auto&[id,c]:classes)K=std::lcm(K,V(c.first));
  assert(K<=ipower(cpp_int(3),(h+1)/3));
  I vn=0;for(auto&[id,c]:classes)vn+=c.second*c.second*(K/c.first);
  I dn=localS*localS*K+(f-1)*vn;assert(dn>0);
  F.den=wD*gD*K*dn;
  std::vector<I>u(h);for(U i=0;i<h;i++)if(std::abs(F.symbols[i])>1){auto c=classes[std::abs(F.symbols[i])];u[i]=(F.symbols[i]>0?1:-1)*c.second*(K/c.first);}
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){
   I fi=(F.forced>>i)&1,fj=(F.forced>>j)&1;cpp_int num=0;
   if(std::abs(F.symbols[i])>1&&std::abs(F.symbols[i])==std::abs(F.symbols[j])){
    I sign=(F.symbols[i]>0?1:-1)*(F.symbols[j]>0?1:-1);
    num=sign*(F.den/classes[std::abs(F.symbols[i])].first);
   }
   cpp_int wi=wD*fi-wN,zj=gD*fj+gN;
   num+=wD*K*localS*u[i]*zj+gD*K*localS*wi*u[j]+cpp_int(K)*vn*wi*zj-wD*gD*(f-1)*u[i]*u[j];
   F.numerator[i*h+j]=num;
  }
 }
 g=F.den;for(const cpp_int&x:F.numerator)g=gcd(g,x);assert(g>0);
 F.den/=g;for(cpp_int&x:F.numerator)x/=g;
 assert(F.den>0);cpp_int trace=0;for(U i=0;i<h;i++)trace+=F.numerator[i*h+i];assert(trace==F.rank*F.den);
}

int main(int argc,char**argv){
 assert(argc==4||argc==5);auto start=std::chrono::steady_clock::now();std::string basis=argv[2];assert(basis.rfind("beta:",0)==0);auto split=basis.find(':',5);assert(split!=std::string::npos);cpp_int betaN(basis.substr(5,split-5)),betaD(basis.substr(split+1));assert(betaD>0);cpp_int betaG=gcd(betaN,betaD);betaN/=betaG;betaD/=betaG;
 std::ifstream input(argv[1],std::ios::binary);U header[6];read_array(input,header);U h=header[0],v=header[1],R=header[2],nf=header[3],nt=header[4];I singles=header[5];V rank_mass,loss;input.read(reinterpret_cast<char*>(&rank_mass),8);input.read(reinterpret_cast<char*>(&loss),8);assert(h==23||h==25);assert(rank_mass>=loss);
 assert(betaD-h*betaN!=0&&betaN!=0&&betaD-3*betaN!=0&&9*betaN-betaD!=0&&2*betaD-3*(h-3)*betaN!=0&&(h-7)*betaD-3*(h-3)*betaN!=0&&2*betaD-3*(h-1)*betaN!=0);
 std::vector<Frame>frames(nf);assert(nf>=2);
 for(U id=0;id<nf;id++){auto&F=frames[id];input.read(reinterpret_cast<char*>(&F.forced),8);input.read(reinterpret_cast<char*>(&F.rank),4);F.symbols.resize(h);input.read(reinterpret_cast<char*>(F.symbols.data()),h);assert(F.rank<=h&&F.forced<(V(1)<<h));
  if(id<2){assert(F.forced==0&&F.rank==(id==0?0:h));continue;}
  U forced=popcount64(F.forced);assert(forced>=1&&forced<=3);std::map<U,U>classes;
  for(U i=0;i<h;i++){I symbol=F.symbols[i];assert(!(F.forced>>i&1)||std::abs(symbol)<=1);if(std::abs(symbol)>1)classes[std::abs(symbol)]++;}
  assert(F.rank==(forced==3?1:classes.size()));
 }
 std::map<std::pair<U,U>,I>transition_counts;std::vector<I>hist(h+1);hist[1]=singles;U matches=0;
 for(U i=0;i<nt;i++){U a,b;I count;input.read(reinterpret_cast<char*>(&a),4);input.read(reinterpret_cast<char*>(&b),4);input.read(reinterpret_cast<char*>(&count),8);assert(a<nf&&b<nf&&count>0&&frames[b].rank>frames[a].rank);hist[frames[b].rank-frames[a].rank]+=count;assert(transition_counts.emplace(std::make_pair(a,b),count).second);}
 assert(input);V hist_mass=0;for(U r=1;r<=h;r++)hist_mass+=r*hist[r];assert(hist_mass==rank_mass);
 for(U id=0;id<frames.size();id++)make_matrix(frames[id],h,betaN,betaD,id<2?id:2);
 std::vector<I>blocks(h+1);blocks[1]=singles;std::vector<Transition>transitions;cpp_int largest=1;unsigned largest_entry_bits=0,largest_bound_bits=0;
 for(auto&[key,count]:transition_counts)if(count){assert(count>0);U a=key.first,b=key.second;assert(frames[b].rank>=frames[a].rank);U r=frames[b].rank-frames[a].rank;
  if(!r){for(U z=0;z<h*h;z++)assert(frames[b].numerator[z]*frames[a].den==frames[a].numerator[z]*frames[b].den);continue;}
  if(r==1){blocks[1]+=count;continue;}if(a==0&&b==1){blocks[h]+=count;continue;}
  cpp_int den=cpp_int(frames[a].den/gcd(frames[a].den,frames[b].den))*frames[b].den;
  cpp_int af=den/frames[a].den,bf=den/frames[b].den,Z=0;
  for(U z=0;z<h*h;z++){cpp_int entry=bf*frames[b].numerator[z]-af*frames[a].numerator[z];if(entry<0)entry=-entry;if(entry>Z)Z=entry;}
  assert(Z>0);cpp_int bound=ipower(cpp_int(r),(r+1)/2)*ipower(Z,r);largest=std::max(largest,bound);
  largest_entry_bits=std::max(largest_entry_bits,bits(Z));largest_bound_bits=std::max(largest_bound_bits,bits(bound));
  transitions.push_back({a,b,r,0,count,den,Z,bound,std::vector<uint8_t>((h+1)*(h+1)),{}});
 }
 // Distinct primes are proved by trial division, and denominator factors are checked.
 std::vector<U>primes;std::vector<cpp_int>products;cpp_int product=1;
 for(U candidate=2147483647;product<=largest;candidate-=2)if(prime(candidate)){for(auto&F:frames)assert(F.den%candidate);primes.push_back(candidate);product*=candidate;products.push_back(product);}
 std::map<U,V>prime_hist;V field_replays=0;
 for(auto&T:transitions){while(T.primes<products.size()&&products[T.primes]<=T.minor_bound)T.primes++;T.primes++;assert(T.primes<=products.size());prime_hist[T.primes]++;field_replays+=T.primes;}
 std::cerr<<"frames "<<frames.size()<<" matrices "<<transitions.size()<<" primes "<<primes.size()<<" replays "<<field_replays<<" bound_bits "<<largest_bound_bits<<"\n";
 V differing_profiles=0;std::vector<std::vector<U>>matrices(frames.size());
 for(U pi=0;pi<primes.size();pi++){U p=primes[pi];std::vector<uint8_t>needed(frames.size());for(auto&T:transitions)if(pi<T.primes){needed[T.a]=needed[T.b]=1;}
  for(U id=0;id<frames.size();id++){matrices[id].clear();if(!needed[id])continue;auto&F=frames[id];U inv=power((F.den%p).convert_to<U>(),p-2,p);auto&M=matrices[id];M.resize(h*h);
   for(U z=0;z<h*h;z++){cpp_int residue=F.numerator[z]%p;if(residue<0)residue+=p;M[z]=multiply(residue.convert_to<U>(),inv,p);}}
  V done=0;for(auto&T:transitions)if(pi<T.primes){auto&A=matrices[T.a];auto&B=matrices[T.b];std::vector<U>M(h*h);for(U z=0;z<h*h;z++)M[z]=subtract(B[z],A[z],p);
   std::vector<std::pair<U,U>>pivots;
   for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pivots.emplace_back(i,U(j));U inv=power(M[i*h+j],p-2,p);
    for(U k=i+1;k<h;k++){U scale=multiply(M[k*h+j],inv,p);if(scale)for(U col=0;col<=U(j);col++)M[k*h+col]=subtract(M[k*h+col],multiply(scale,M[i*h+col],p),p);}}
   assert(pivots.size()<=T.r);if(pi==0)T.pivots=pivots;else if(pivots!=T.pivots)differing_profiles++;
   std::vector<uint8_t>corner((h+1)*(h+1));U at=0;
   for(U i=0;i<h;i++){int col=at<pivots.size()&&pivots[at].first==i?int(pivots[at++].second):-1;for(U j=0;j<h;j++)corner[(i+1)*(h+1)+j]=corner[i*(h+1)+j]+(int(j)<=col);}
   for(U z=0;z<corner.size();z++)T.corner[z]=std::max(T.corner[z],corner[z]);
   done++;
  }
  std::cerr<<"prime "<<pi+1<<" / "<<primes.size()<<" matrices "<<done<<" seconds "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"\n";
 }
 V mass=0;U longest=0;
 for(auto&T:transitions){T.pivots.clear();auto&C=T.corner;for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=C[(i+1)*(h+1)+j]-C[i*(h+1)+j]-C[(i+1)*(h+1)+j+1]+C[i*(h+1)+j+1];assert(z==0||z==1);if(z)T.pivots.emplace_back(i,j);}
  assert(T.pivots.size()==T.r);U run=0;for(U at=0;at<T.pivots.size();at++){if(at&&T.pivots[at].first==T.pivots[at-1].first+1&&T.pivots[at].second==T.pivots[at-1].second+1)run++;else{if(run){blocks[run]+=T.count;longest=std::max(longest,run);}run=1;}}if(run){blocks[run]+=T.count;longest=std::max(longest,run);}}
 for(U t=1;t<=h;t++){assert(blocks[t]>=0);mass+=t*blocks[t];}assert(mass==rank_mass);
 std::ofstream out(argv[3]);assert(out);out<<"{\"status\":\"PASS EXACT SIGNED-FRAME EXECUTED JOINT WORD PROFILES\",\"basis\":\""<<basis<<"\",\"h\":"<<h<<",\"v\":"<<v<<",\"R\":"<<R<<",\"matched\":"<<matches<<",\"loss\":"<<loss<<",\"rank_sum\":"<<mass<<",\"frames\":"<<frames.size()<<",\"distinct_matrices\":"<<transitions.size()<<",\"field_replays\":"<<field_replays<<",\"different_modular_profiles\":"<<differing_profiles<<",\"maximum_entry_bound_bits\":"<<largest_entry_bits<<",\"maximum_minor_bound_bits\":"<<largest_bound_bits<<",\"prime_product_bits\":"<<bits(product)<<",\"longest_block\":"<<longest<<",\"seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<",\"primes\":[";
 for(U i=0;i<primes.size();i++){if(i)out<<",";out<<primes[i];}out<<"],\"prime_count_histogram\":{";bool first=true;for(auto&[pc,num]:prime_hist){if(!first)out<<",";first=false;out<<"\""<<pc<<"\":"<<num;}out<<"},\"blocks\":[";
 for(U t=0;t<=h;t++){if(t)out<<",";out<<blocks[t];}out<<"],\"rank_histogram\":[";for(U t=0;t<=h;t++){if(t)out<<",";out<<hist[t];}out<<"]}\n";
 if(argc==5){std::ofstream audit(argv[4]);assert(audit);audit<<"{\"h\":"<<h<<",\"basis\":\""<<basis<<"\",\"transitions\":[";first=true;
  for(auto&T:transitions){if(!first)audit<<",";first=false;audit<<"{\"a\":"<<T.a<<",\"b\":"<<T.b<<",\"rank\":"<<T.r<<",\"count\":"<<T.count<<",\"integer_denominator\":\""<<T.denominator<<"\",\"entry_bound\":\""<<T.entry_bound<<"\",\"minor_bound\":\""<<T.minor_bound<<"\",\"prime_count\":"<<T.primes<<",\"pivots\":[";
   for(U k=0;k<T.pivots.size();k++){if(k)audit<<",";audit<<"["<<T.pivots[k].first<<","<<T.pivots[k].second<<"]";}audit<<"]}";}audit<<"]}\n";}
 std::cout<<"h="<<h<<" basis="<<basis<<" R="<<R<<" exact_rank_mass="<<mass<<" matrices="<<transitions.size()<<"\n";
}
