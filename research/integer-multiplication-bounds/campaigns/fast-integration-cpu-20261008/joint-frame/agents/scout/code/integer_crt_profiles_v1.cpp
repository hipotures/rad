// Independent all-corner integer CRT profiler, prepared with OpenAI Codex.
// Apache-2.0. Projector formulas are credited to the pinned PR58/PR48 chain:
// icekylinx, Dominik Scholz, Zhihao Chen, Swapnil Jain, Rohan Arun,
// Chafik Boukhalfa, Aurel Prosz and RaD/hipotures; retain upstream notices.
// Unlike that implementation, every profiled matrix uses integer numerators
// and twelve certified moduli with a generic determinant bound. No low-rank
// minor bound or modular projector inverse is used.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using U=uint32_t; using V=uint64_t; using I=int64_t;
struct Frame {V c,u; U rank;};
struct Matrix {I den=1; std::vector<I> a;};
template<class T> void read(std::ifstream& f,T& x){f.read(reinterpret_cast<char*>(&x),sizeof(x));assert(f);}
int main(int argc,char**argv){
 assert(argc>=16); std::ifstream in(argv[1],std::ios::binary);assert(in);
 U h,v,R,nf,nt,singles;read(in,h);read(in,v);read(in,R);read(in,nf);read(in,nt);read(in,singles);
 assert(h==23||h==25);V expected,loss;read(in,expected);read(in,loss);assert(expected==V(h)*R+loss);
 std::vector<Frame> f(nf);for(auto& a:f){read(in,a.c);read(in,a.u);read(in,a.rank);}
 const I H=std::stoll(argv[3]);std::vector<V> primes;
 for(int i=4;i<argc;i++){V p=std::stoull(argv[i]);assert(p>(V(1)<<61)&&p<(V(1)<<63));primes.push_back(p);}assert(primes.size()==12);
 std::vector<Matrix> cache(nf);
 auto matrix=[&](U id)->const Matrix&{
  assert(id<nf);auto& M=cache[id];if(!M.a.empty())return M;
  M.a.assign(h*h,0);if(id==0)return M;
  if(id==1){for(U i=0;i<h;i++)M.a[i*h+i]=1;return M;}
  auto F=f[id];assert((F.c&~F.u)==0);U c=__builtin_popcountll(F.c);V out=F.u&~F.c;U n=__builtin_popcountll(out);
  if(c==3){assert(F.c==F.u&&F.rank==1);M.den=6*(h+1);
   for(U i=0;i<h;i++)for(U j=0;j<h;j++)M.a[i*h+j]=(3+I((F.c>>i)&1))*(3*I(h+1)*I((F.c>>j)&1)-10);
  }else{
   assert(c==1||c==2);I s=3-c,d=s*s+(c-1)*n;M.den=3*(h+1)*d;assert(d>0&&F.rank==n);
   for(U i=0;i<h;i++)for(U j=0;j<h;j++){
    I oi=(out>>i)&1,oj=(out>>j)&1,wi=3+I((F.c>>i)&1),zj=3*I(h+1)*I((F.c>>j)&1)-10;
    M.a[i*h+j]=M.den*I(i==j)*oi+s*oi*zj+3*I(h+1)*s*wi*oj+I(n)*wi*zj-3*I(h+1)*I(c-1)*oi*oj;
   }
  }return M;
 };
 std::vector<V> blocks(h+1);blocks[1]=singles;V matrices=0,disagreements=0,whole_identity=0;
 for(U event=0;event<nt;event++){
  U a,b;I count;read(in,a);read(in,b);read(in,count);assert(a<nf&&b<nf&&count>0&&f[b].rank>f[a].rank);
  U rank=f[b].rank-f[a].rank;if(rank<=2){blocks[1]+=V(count)*rank;continue;}
  if(a==0&&b==1){blocks[h]+=count;whole_identity++;continue;}
  if(a>1&&b>1){assert((f[b].c&~f[a].c)==0&&(f[a].u&~f[b].u)==0);}
  const Matrix&A=matrix(a);const Matrix&B=matrix(b);std::vector<I> numerator(h*h);
  for(U i=0;i<h*h;i++){numerator[i]=A.den*B.a[i]-B.den*A.a[i];assert(-H<=numerator[i]&&numerator[i]<=H);}
  std::vector<int> corner((h+1)*(h+1));std::vector<std::pair<U,U>> first;
  for(V p:primes){
   auto mul=[&](V x,V y)->V{return (__uint128_t)x*y%p;};
   auto sub=[&](V x,V y)->V{return x>=y?x-y:x+p-y;};
   auto power=[&](V x,V y)->V{V ans=1;for(;y;y>>=1,x=mul(x,x))if(y&1)ans=mul(ans,x);return ans;};
   std::vector<V> M(h*h);for(U i=0;i<h*h;i++)M[i]=numerator[i]>=0?V(numerator[i]):p-V(-numerator[i]);
   std::vector<std::pair<U,U>> pivots;
   for(U i=0;i<h;i++){
    int j=h-1;while(j>=0&&M[i*h+j]==0)j--;if(j<0)continue;
    pivots.emplace_back(i,U(j));V inv=power(M[i*h+j],p-2);
    for(U k=i+1;k<h;k++){V z=mul(M[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)M[k*h+col]=sub(M[k*h+col],mul(z,M[i*h+col]));}
   }
   assert(pivots.size()<=rank);if(first.empty())first=pivots;else disagreements+=(pivots!=first);
   std::vector<int> C((h+1)*(h+1));for(auto [row,col]:pivots)C[(row+1)*(h+1)+col]=1;
   for(U i=1;i<=h;i++)for(int j=int(h)-1;j>=0;j--){
    C[i*(h+1)+j]+=C[(i-1)*(h+1)+j]+C[i*(h+1)+j+1]-C[(i-1)*(h+1)+j+1];
    corner[i*(h+1)+j]=std::max(corner[i*(h+1)+j],C[i*(h+1)+j]);
   }
  }
  std::vector<std::pair<U,U>> pivots;
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){
   int z=corner[(i+1)*(h+1)+j]-corner[i*(h+1)+j]-corner[(i+1)*(h+1)+j+1]+corner[i*(h+1)+j+1];
   assert(z==0||z==1);if(z)pivots.emplace_back(i,j);
  }assert(pivots.size()==rank);
  U run=0;for(U j=0;j<pivots.size();j++){
   if(j&&pivots[j].first==pivots[j-1].first+1&&pivots[j].second==pivots[j-1].second+1)run++;
   else{if(run)blocks[run]+=count;run=1;}
  }if(run)blocks[run]+=count;matrices++;
 }
 char extra;assert(!in.read(&extra,1));V mass=0;for(U t=1;t<=h;t++)mass+=t*blocks[t];assert(mass==expected);
 std::ofstream out(argv[2]);assert(out);
 out<<"{\"status\":\"ALL-CORNER INTEGER CRT PROFILE PASS\",\"h\":"<<h<<",\"v\":"<<v<<",\"R\":"<<R<<",\"loss\":"<<loss<<",\"rank_sum\":"<<mass<<",\"frames\":"<<nf<<",\"distinct_matrices\":"<<matrices<<",\"all_corner_moduli\":"<<primes.size()<<",\"differing_modular_profiles\":"<<disagreements<<",\"whole_identity_transitions\":"<<whole_identity<<",\"blocks\":[";
 for(U t=0;t<=h;t++){if(t)out<<",";out<<blocks[t];}out<<"]}\n";
 std::cerr<<"ALL-CORNER INTEGER CRT PASS h="<<h<<" matrices="<<matrices<<" modular differences="<<disagreements<<"\n";
}
