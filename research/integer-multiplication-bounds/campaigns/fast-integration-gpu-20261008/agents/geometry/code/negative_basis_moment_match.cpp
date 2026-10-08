// New exact basis L_h=I-4/[3(h+3)]J. New coefficient bounds and source certificate are separate.
// RaD GPU campaign: original-envelope matching weighted by actual fixed-basis matrix profiles.
// Matching/frame primitives from credited PR38/36/32; discovery objective and exchanges are new.
// RaD GPU fast-integration: run changed DAGs, retain selected use IDs.
// Immediate source PR38 cc794077f6c103e24ec0939be765cd1521239aab; inherited notices below.
// Adapted from PR35 at 9c345a2; selected dimensions 23/25.
// Retain extra primes for all source-growth and core-change cases.
// Exact bounded-minor inequalities are checked by verify.py. Original credit below.
// Copyright 2026 icekylinx. Apache-2.0; AI-assisted handoff integration.
// Original round3_rankone_profiles.cpp. Requires GCC/Clang unsigned __int128.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <map>
#include <unordered_map>
#include <cmath>
#include <random>
#include <iomanip>
using U=uint32_t;using V=uint64_t;
#include "binary_io.hpp"
int main(int argc,char**argv){assert(argc==5);U seed=std::stoul(argv[2]),mode=std::stoul(argv[3]);std::mt19937_64 rng(seed);std::ifstream f(argv[1],std::ios::binary);U hdr[4];read_array(f,hdr);U h=hdr[0],v=hdr[1],n=hdr[2],q=hdr[3];assert(h==23||h==25);
std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);readv(f,args);readv(f,core);readv(f,cover);readv(f,roots);readv(f,kind);readv(f,active);
std::vector<U>ranks(n),degree(n),begin(n+1);V c=0,inputs=0,loss=0;
for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){c++;assert(args[x][0]<x&&args[x][1]<x);ranks[x]=popcount64(cover[x])-popcount64(core[x]);for(U y:args[x])degree[y]++;}else{ranks[x]=1;inputs++;}}
assert(inputs==v);for(U x:roots)degree[x]++;for(U x=1;x<n;x++)begin[x+1]=begin[x]+degree[x];
std::vector<U>uses(begin.back()),cursor(begin.begin(),begin.end()-1);for(U x=1;x<n;x++)if(active[x]&&args[x][0]){uses[cursor[args[x][0]]++]=2*x;uses[cursor[args[x][1]]++]=2*x+1;}for(U j=0;j<q;j++)uses[cursor[roots[j]]++]=(1U<<31)|j;
auto nd=[&](U e)->U{return e>>31?roots[e&0x7fffffff]:e/2;};
auto before=[&](U a,U b){U x=nd(a),y=nd(b);if(ranks[x]!=ranks[y])return ranks[x]<ranks[y];V ox=a>>31?V(n)+(a&0x7fffffff):x,oy=b>>31?V(n)+(b&0x7fffffff):y;return ox<oy;};
auto incl=[&](U a,U b){U x=nd(a),y=nd(b);return !(core[y]&~core[x])&&!(cover[x]&~cover[y]);};
struct Frame{V core,cover;U rank;};std::vector<Frame>frames{{0,0,0},{0,0,h}};std::map<std::pair<V,V>,U>frame_lookup;std::vector<U>fi(n);
for(U x=1;x<n;x++)if(active[x]){auto key=std::make_pair(core[x],cover[x]);auto z=frame_lookup.find(key);if(z==frame_lookup.end()){U id=frames.size();frames.push_back({core[x],cover[x],ranks[x]});frame_lookup[key]=id;fi[x]=id;}else fi[x]=z->second;}
V p=2305843009213693951ULL;
auto mul=[&](V a,V b)->V{return (__uint128_t)a*b%p;};
auto power=[&](V a,V b)->V{V r=1;for(;b;b>>=1,a=mul(a,a))if(b&1)r=mul(r,a);return r;};
auto sub=[&](V a,V b)->V{return (a+p-b)%p;};
std::vector<std::vector<V>>matrix_cache(frames.size());
auto matrix=[&](U id)->const std::vector<V>&{auto&A=matrix_cache[id];if(!A.empty())return A;A.assign(h*h,0);if(id==0)return A;if(id==1){for(U i=0;i<h;i++)A[i*h+i]=1;return A;}
 auto f=frames[id];U c=popcount64(f.core);V out=f.cover&~f.core;U nn=popcount64(out);
 if(c==3){V factor=power(2*(h+3),p-2);for(U i=0;i<h;i++)for(U j=0;j<h;j++){V wi=((f.core>>i)&1)?h-1:p-4;V zj=1+((f.core>>j)&1);A[i*h+j]=mul(mul(wi,zj),factor);}return A;}
 assert(c==1||c==2);V s=3-c,d=s*s+(c-1)*nn,den=(h+3)*d,inv=power(den,p-2);
 for(U i=0;i<h;i++)for(U j=0;j<h;j++){V oi=(out>>i)&1,oj=(out>>j)&1,wi=((f.core>>i)&1)?h-1:p-4,zj=1+((f.core>>j)&1);
  V num=(s*(h+3)*oi*zj+mul(s*wi%p,oj)+mul(mul(nn,wi),zj))%p;num=sub(num,(h+3)*(c-1)*oi*oj);A[i*h+j]=(V(i==j&&oi)+mul(num,inv))%p;
 }return A;};

const long double alpha=0.00004L,m=575.0L;
auto phi=[&](U width){return width?width*std::expm1(alpha*std::log(m/width)):0.0L;};
std::unordered_map<V,long double> costs;
auto cost=[&](U aa,U bb)->long double{
 V key=(V(aa)<<32)|bb;auto old=costs.find(key);if(old!=costs.end())return old->second;
 assert(frames[bb].rank>=frames[aa].rank);U rr=frames[bb].rank-frames[aa].rank;
 if(!rr)return costs[key]=0; if(rr<=2)return costs[key]=rr*phi(1);
 if(aa==0&&bb==1)return costs[key]=phi(h);
 const auto&A=matrix(aa);const auto&B=matrix(bb);std::vector<V>M(h*h);for(U z=0;z<h*h;z++)M[z]=sub(B[z],A[z]);
 std::vector<std::pair<U,U>>pv;for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pv.push_back({i,U(j)});V iv=power(M[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(M[k*h+j],iv);if(z)for(U c0=0;c0<=U(j);c0++)M[k*h+c0]=sub(M[k*h+c0],mul(z,M[i*h+c0]));}}
 assert(pv.size()==rr);long double result=0;U run=0;for(U i=0;i<pv.size();i++){if(i&&pv[i].first==pv[i-1].first+1&&pv[i].second==pv[i-1].second+1)run++;else{result+=phi(run);run=1;}}result+=phi(run);return costs[key]=result;
};
auto benefit=[&](U donor,U j){U e=uses[j],target=nd(e),value=e>>31?target:args[target][e&1];
 return cost(fi[donor],1)+cost(0,fi[value])+cost(fi[value],fi[target])-cost(fi[donor],fi[target]);
};
std::vector<std::vector<U>>edges(n);
for(U donor=1;donor<n;donor++)if(active[donor]&&args[donor][0]){
 for(U value:args[donor])for(U j=begin[value];j<begin[value+1];j++)if(before(2*donor,uses[j])&&incl(2*donor,uses[j]))edges[donor].push_back(j);
 if(mode==4)std::shuffle(edges[donor].begin(),edges[donor].end(),rng);
 if(mode)std::stable_sort(edges[donor].begin(),edges[donor].end(),[&](U a,U b){return benefit(donor,a)>benefit(donor,b);});
}
auto adjacency=[&](U donor,auto&&action){for(U j:edges[donor])if(action(j))return true;return false;};
std::vector<U>donors;for(U x=1;x<n;x++)if(active[x]&&args[x][0]&&!edges[x].empty())donors.push_back(x);
if(mode==2)std::stable_sort(donors.begin(),donors.end(),[&](U a,U b){return edges[a].size()<edges[b].size();});
if(mode>=3)std::shuffle(donors.begin(),donors.end(),rng);
std::vector<U>leftmatch(n),rightmatch(uses.size()),distance(n,UINT32_MAX),queue;V matches=0;U phase=0,inf=UINT32_MAX,shortest=inf;
while(true){queue.clear();shortest=inf;for(U x:donors){if(!leftmatch[x]){distance[x]=0;queue.push_back(x);}else distance[x]=inf;}for(U at=0;at<queue.size();at++){U x=queue[at];if(distance[x]>=shortest)continue;adjacency(x,[&](U j){U y=rightmatch[j];if(!y)shortest=distance[x]+1;else if(distance[y]==inf){distance[y]=distance[x]+1;queue.push_back(y);}return false;});}if(shortest==inf)break;
auto aug=[&](auto&&self,U x)->bool{bool ok=adjacency(x,[&](U j){U y=rightmatch[j];if((!y&&distance[x]+1==shortest)||(y&&distance[y]==distance[x]+1&&self(self,y))){leftmatch[x]=j+1;rightmatch[j]=x;return true;}return false;});if(!ok)distance[x]=inf;return ok;};V gained=0;for(U x:donors)if(!leftmatch[x]&&aug(aug,x)){matches++;gained++;}std::cerr<<"h="<<h<<" phase "<<++phase<<" length "<<shortest<<" gained "<<gained<<" total "<<matches<<"\n";assert(gained);}

U improvements=0;
for(U pass=0;pass<12;pass++){U gain=0;for(U x:donors){U ox=leftmatch[x]?leftmatch[x]-1:UINT32_MAX;
 for(U j:edges[x]){if(j==ox)continue;U y=rightmatch[j];
 if(!y){if(ox!=UINT32_MAX&&benefit(x,j)>benefit(x,ox)+1e-15L){rightmatch[ox]=0;rightmatch[j]=x;leftmatch[x]=j+1;gain++;break;}continue;}
 if(y==x)continue;
 if(ox==UINT32_MAX){if(benefit(x,j)>benefit(y,j)+1e-15L){leftmatch[y]=0;rightmatch[j]=x;leftmatch[x]=j+1;gain++;break;}continue;}
 if(std::find(edges[y].begin(),edges[y].end(),ox)!=edges[y].end()&&benefit(x,j)+benefit(y,ox)>benefit(x,ox)+benefit(y,j)+1e-15L){leftmatch[x]=j+1;leftmatch[y]=ox+1;rightmatch[j]=x;rightmatch[ox]=y;gain++;break;}
 }}improvements+=gain;if(!gain)break;}
std::string outprefix=argv[4];std::ofstream out(outprefix+".uses.bin",std::ios::binary);U header[2]={n,U(matches)};write_array(out,header);
std::ofstream js(outprefix+".uses.json");js<<"{\"h\":"<<h<<",\"n\":"<<n<<",\"seed\":"<<seed<<",\"mode\":"<<mode<<",\"links\":[";U written=0;long double total=0;
for(U donor:donors)if(leftmatch[donor]){U use=uses[leftmatch[donor]-1];U edge[2]={donor,use};write_array(out,edge);if(written++)js<<",";js<<"["<<donor<<","<<use<<"]";total+=benefit(donor,leftmatch[donor]-1);}
assert(written==matches);js<<"]}\n";assert(js&&out);
std::cout<<std::setprecision(20)<<"{\"h\":"<<h<<",\"v\":"<<v<<",\"c\":"<<c<<",\"q\":"<<q<<",\"matched\":"<<matches<<",\"R\":"<<c+q-matches<<",\"seed\":"<<seed<<",\"mode\":"<<mode<<",\"exchange_improvements\":"<<improvements<<",\"profile_cost_cache\":"<<costs.size()<<",\"discovery_total_benefit\":"<<total<<",\"status\":\"discovery; full CRT profile and dirty compilation required\"}\n";
}
