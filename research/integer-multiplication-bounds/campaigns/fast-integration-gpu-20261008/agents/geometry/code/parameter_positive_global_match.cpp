// RaD: rational-beta variable-cardinality global physical-moment matching over valid components.
// RaD: actual positive-frame matrix-moment matching, including paid 2-to-1 exchanges.
// Discovery-only field costs; exact physical profiling and literal compiler are mandatory.
// Copyright 2026 icekylinx. Licensed under Apache-2.0.
// Adapted with AI assistance from the archived partial-swap research producer.
// Underlying circuit modules: jacklightChen/integer-mult-bounds, PR7
// commit 6725c6a17b17871a35353fd29157f4ed851bc114; original credits retained.
#include <algorithm>
#include <cmath>
#include <random>
#include <unordered_map>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
using U=uint32_t;using V=uint64_t;
#include "binary_io.hpp"
#include <map>
#include <numeric>
#include <iomanip>
#include <boost/multiprecision/cpp_int.hpp>
#include <queue>
#include <limits>
using I=int64_t;using boost::multiprecision::cpp_int;
struct Frame {V forced=0;cpp_int den=1;U rank=0;std::vector<int8_t> symbols;std::vector<cpp_int> numerator;};
cpp_int ipower(cpp_int a,U n){cpp_int z=1;for(;n;n>>=1,a*=a)if(n&1)z*=a;return z;}
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

// RaD GPU campaign: moment-sensitive adjacency and cardinality-preserving exchanges.
// Input basis/containment/Hopcroft--Karp follow pinned icekylinx PR36.
// Discovery weights use long double; accepted moments are checked rationally.
int main(int argc,char**argv){assert(argc==7); U seed=std::stoul(argv[4]), mode=std::stoul(argv[5]);std::string basis=argv[3];assert(basis.rfind("beta:",0)==0);auto split=basis.find(':',5);assert(split!=std::string::npos);cpp_int betaN(basis.substr(5,split-5)),betaD(basis.substr(split+1));assert(betaD>0);cpp_int betaG=gcd(betaN,betaD);betaN/=betaG;betaD/=betaG;std::string prefix=argv[6];std::ifstream f(argv[1],std::ios::binary);U hdr[4];read_array(f,hdr);U h=hdr[0],v=hdr[1],n=hdr[2],q=hdr[3];
std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);readv(f,args);readv(f,core);readv(f,cover);readv(f,roots);readv(f,kind);readv(f,active);
std::vector<U>ranks(n),degree(n),begin(n+1);V c=0,inputs=0,loss=0;
for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){c++;assert(args[x][0]<x&&args[x][1]<x);ranks[x]=popcount64(cover[x])-popcount64(core[x]);for(U y:args[x])degree[y]++;}else{ranks[x]=1;inputs++;}}
assert(inputs==v);
auto oldranks=ranks;
std::ifstream lf(argv[2],std::ios::binary);U lh[2];read_array(lf,lh);assert(lh[0]==h&&lh[1]==n);std::vector<V>forced(n);std::vector<int8_t>symbols(V(n)*h);readv(lf,ranks);readv(lf,forced);readv(lf,symbols);
for(U x:roots)degree[x]++;for(U x=1;x<n;x++)begin[x+1]=begin[x]+degree[x];
std::vector<U>uses(begin.back()),cursor(begin.begin(),begin.end()-1);for(U x=1;x<n;x++)if(active[x]&&args[x][0]){uses[cursor[args[x][0]]++]=2*x;uses[cursor[args[x][1]]++]=2*x+1;}for(U j=0;j<q;j++)uses[cursor[roots[j]]++]=(1U<<31)|j;
auto nd=[&](U e)->U{return e>>31?roots[e&0x7fffffff]:e/2;};
auto before=[&](U a,U b){U x=nd(a),y=nd(b);if(ranks[x]!=ranks[y])return ranks[x]<ranks[y];if(oldranks[x]!=oldranks[y])return oldranks[x]<oldranks[y];V ox=a>>31?V(n)+(a&0x7fffffff):x,oy=b>>31?V(n)+(b&0x7fffffff):y;return ox<oy;};
auto incl=[&](U a,U b){U x=nd(a),y=nd(b);if(forced[y]&~forced[x])return false;int expect[66]{};bool seen[66]{};
for(U i=0;i<h;i++){int sx=symbols[V(x)*h+i],sy=symbols[V(y)*h+i];if(!sy){if(sx)return false;}else if(sy==1){if(sx!=1)return false;}else{int k=sy<0?-sy:sy,z=sy<0?-sx:sx;if(seen[k]){if(expect[k]!=z)return false;}else{seen[k]=true;expect[k]=z;}}}return true;};
// Discovery costs use actual signed positive projectors; promotion needs full CRT.
std::vector<Frame>frames(2);frames[1].rank=h;std::vector<U>fi(n);std::map<std::pair<V,std::vector<int8_t>>,U>frame_lookup;
for(U x=1;x<n;x++)if(active[x]){std::vector<int8_t>sy(symbols.begin()+V(x)*h,symbols.begin()+V(x+1)*h);auto key=std::make_pair(forced[x],sy);auto z=frame_lookup.find(key);if(z==frame_lookup.end()){U id=frames.size();Frame F;F.forced=forced[x];F.rank=ranks[x];F.symbols=std::move(sy);frames.push_back(std::move(F));frame_lookup.emplace(std::move(key),id);fi[x]=id;}else{fi[x]=z->second;assert(frames[fi[x]].rank==ranks[x]);}}
const U prime=2147483647;auto mul=[&](U a,U b)->U{return V(a)*b%prime;};auto power=[&](U a,U b)->U{U r=1;for(;b;b>>=1,a=mul(a,a))if(b&1)r=mul(r,a);return r;};auto sub=[&](U a,U b)->U{return a>=b?a-b:a+prime-b;};
std::vector<std::vector<U>>matrices(frames.size());
for(U id=0;id<frames.size();id++){auto&F=frames[id];make_matrix(F,h,betaN,betaD,id<2?id:2);assert(F.den%prime);U inv=power((F.den%prime).convert_to<U>(),prime-2);auto&M=matrices[id];M.resize(h*h);for(U z=0;z<h*h;z++){cpp_int residue=F.numerator[z]%prime;if(residue<0)residue+=prime;M[z]=mul(residue.convert_to<U>(),inv);}}
const long double m=575.0L,alpha=0.00004L;auto phi=[&](U r){return r?r*std::expm1(alpha*std::log(m/r)):0.0L;};
const long double exterior=phi(h)+phi(575-2*h);std::unordered_map<V,long double>costs;U deficient_costs=0;
auto cost=[&](U a,U b){V key=(V(a)<<32)|b;auto z=costs.find(key);if(z!=costs.end())return z->second;assert(frames[b].rank>=frames[a].rank);U r=frames[b].rank-frames[a].rank;if(r<=1)return costs[key]=r*phi(1);if(a==0&&b==1)return costs[key]=phi(h);
 std::vector<U>M(h*h);for(U k=0;k<h*h;k++)M[k]=sub(matrices[b][k],matrices[a][k]);std::vector<std::pair<U,U>>pivots;
 for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pivots.emplace_back(i,U(j));U inv=power(M[i*h+j],prime-2);for(U k=i+1;k<h;k++){U scale=mul(M[k*h+j],inv);if(scale)for(U c0=0;c0<=U(j);c0++)M[k*h+c0]=sub(M[k*h+c0],mul(scale,M[i*h+c0]));}}
 assert(pivots.size()<=r);if(pivots.size()!=r){deficient_costs++;return costs[key]=r*phi(1);}U run=0;long double value=0;for(U j=0;j<pivots.size();j++){if(j&&pivots[j].first==pivots[j-1].first+1&&pivots[j].second==pivots[j-1].second+1)run++;else{value+=phi(run);run=1;}}return costs[key]=value+phi(run);
};
auto benefit=[&](U donor,U j){U use=uses[j],target=nd(use),value=use>>31?target:args[target][use&1];return cost(fi[donor],1)+cost(0,fi[value])+cost(fi[value],fi[target])-cost(fi[donor],fi[target]);};
std::vector<std::vector<U>>edges(n);std::mt19937_64 rng(seed);
for(U donor=1;donor<n;donor++)if(active[donor]&&args[donor][0]){
 for(U value:args[donor])for(U j=begin[value];j<begin[value+1];j++)if(before(donor*2,uses[j])&&incl(donor*2,uses[j]))edges[donor].push_back(j);
 if(mode==1||mode==2||mode>=4)std::stable_sort(edges[donor].begin(),edges[donor].end(),[&](U a,U b){return benefit(donor,a)>benefit(donor,b);});
 if(mode==3)std::shuffle(edges[donor].begin(),edges[donor].end(),rng);
}
auto adjacency=[&](U donor,auto&& action){for(U j:edges[donor])if(action(j))return true;return false;};
std::vector<U>donors;for(U x=1;x<n;x++)if(active[x]&&args[x][0]&&adjacency(x,[](U){return true;}))donors.push_back(x);
if(mode==2)std::stable_sort(donors.begin(),donors.end(),[&](U a,U b){return edges[a].size()<edges[b].size();});
if(mode>=3)std::shuffle(donors.begin(),donors.end(),rng);
std::vector<U>leftmatch(n),rightmatch(uses.size()),distance(n,UINT32_MAX),queue;V matches=0;U phase=0,inf=UINT32_MAX,shortest=inf;
while(true){queue.clear();shortest=inf;for(U x:donors){if(!leftmatch[x]){distance[x]=0;queue.push_back(x);}else distance[x]=inf;}for(U at=0;at<queue.size();at++){U x=queue[at];if(distance[x]>=shortest)continue;adjacency(x,[&](U j){U y=rightmatch[j];if(!y)shortest=distance[x]+1;else if(distance[y]==inf){distance[y]=distance[x]+1;queue.push_back(y);}return false;});}if(shortest==inf)break;
auto aug=[&](auto&&self,U x)->bool{bool ok=adjacency(x,[&](U j){U y=rightmatch[j];if((!y&&distance[x]+1==shortest)||(y&&distance[y]==distance[x]+1&&self(self,y))){leftmatch[x]=j+1;rightmatch[j]=x;return true;}return false;});if(!ok)distance[x]=inf;return ok;};V gained=0;for(U x:donors)if(!leftmatch[x]&&aug(aug,x)){matches++;gained++;}std::cerr<<"h="<<h<<" phase "<<++phase<<" length "<<shortest<<" gained "<<gained<<" total "<<matches<<"\n";assert(gained);}
V initial_cardinality=matches;U improvements=0,cardinality_losses=0,cardinality_gains=0;
if(mode){for(U pass=0;pass<8;pass++){U gain=0;for(U x:donors){
 U ox=leftmatch[x]?leftmatch[x]-1:UINT32_MAX;
 for(U j:edges[x]){if(j==ox)continue;U y=rightmatch[j];
 if(!y){if(mode>=5&&ox==UINT32_MAX){leftmatch[x]=j+1;rightmatch[j]=x;matches++;cardinality_gains++;gain++;break;}if(ox!=UINT32_MAX&&benefit(x,j)>benefit(x,ox)+1e-18L){rightmatch[ox]=0;rightmatch[j]=x;leftmatch[x]=j+1;gain++;break;}continue;}
 if(y==x)continue;
 if(ox==UINT32_MAX){if(benefit(x,j)>benefit(y,j)+1e-18L){leftmatch[y]=0;rightmatch[j]=x;leftmatch[x]=j+1;gain++;break;}continue;}
 if(mode>=5&&benefit(x,j)>benefit(x,ox)+benefit(y,j)+exterior+1e-18L){leftmatch[y]=0;rightmatch[ox]=0;leftmatch[x]=j+1;rightmatch[j]=x;matches--;cardinality_losses++;gain++;break;}
 if(std::find(edges[y].begin(),edges[y].end(),ox)!=edges[y].end()&&benefit(x,j)+benefit(y,ox)>benefit(x,ox)+benefit(y,j)+1e-18L){leftmatch[x]=j+1;leftmatch[y]=ox+1;rightmatch[j]=x;rightmatch[ox]=y;gain++;break;}
 }}improvements+=gain;if(!gain)break;}}

// Solve independent bipartite components by successive shortest augmenting paths.
// Weights include the exterior role charge, so cardinality is not forced.
// Floating finite-field weights are discovery evidence; exact CRT gates follow.
if(mode==6){
 struct FlowEdge{U to,rev;int cap;long double cost;};
 std::vector<U>parent(n+uses.size());std::iota(parent.begin(),parent.end(),0);
 auto find=[&](U x){U y=x;while(parent[y]!=y)y=parent[y];while(parent[x]!=x){U z=parent[x];parent[x]=y;x=z;}return y;};
 for(U x:donors)for(U j:edges[x]){U a=find(x),b=find(n+j);if(a!=b)parent[b]=a;}
 std::map<U,std::vector<U>>components;for(U x:donors)components[find(x)].push_back(x);
 std::fill(leftmatch.begin(),leftmatch.end(),0);std::fill(rightmatch.begin(),rightmatch.end(),0);matches=0;
 U max_component_donors=0,max_component_uses=0;V arcs_total=0;long double total_utility=0;
 for(auto&[root,ds]:components){
  std::unordered_map<U,U>local_use;std::vector<U>us;
  for(U x:ds)for(U j:edges[x])if(local_use.emplace(j,us.size()).second)us.push_back(j);
  U D=ds.size(),E=us.size(),S=0,T=D+E+1,size=T+1;
  max_component_donors=std::max(max_component_donors,D);max_component_uses=std::max(max_component_uses,E);
  std::vector<std::vector<FlowEdge>>network(size);
  auto add=[&](U a,U b,long double c){U i=network[a].size(),j=network[b].size();network[a].push_back({b,j,1,c});network[b].push_back({a,i,0,-c});return i;};
  std::vector<long double>potential(size,0);std::vector<std::array<U,3>>arcs;
  for(U d=0;d<D;d++)add(S,1+d,0);
  for(U u=0;u<E;u++)add(1+D+u,T,0);
  for(U d=0;d<D;d++)for(U j:edges[ds[d]]){
   U u=local_use.at(j),node=1+D+u;long double utility=benefit(ds[d],j)+exterior;
   U a=add(1+d,node,-utility);arcs.push_back({d,a,j});potential[node]=std::min(potential[node],-utility);
  }
  for(U u=0;u<E;u++)potential[T]=std::min(potential[T],potential[1+D+u]);
  U flow=0;const long double inf=std::numeric_limits<long double>::infinity();
  while(true){
   std::vector<long double>distance(size,inf);std::vector<U>prev_node(size),prev_edge(size);distance[S]=0;
   using Item=std::pair<long double,U>;std::priority_queue<Item,std::vector<Item>,std::greater<Item>>heap;heap.push({0,S});
   while(!heap.empty()){
    auto [dv,node]=heap.top();heap.pop();if(dv>distance[node]+1e-18L)continue;
    for(U k=0;k<network[node].size();k++){
     const auto&e=network[node][k];if(!e.cap)continue;
     long double reduced=e.cost+potential[node]-potential[e.to];assert(reduced>-1e-11L);if(reduced<0)reduced=0;
     long double next=dv+reduced;
     if(next+1e-18L<distance[e.to]){distance[e.to]=next;prev_node[e.to]=node;prev_edge[e.to]=k;heap.push({next,e.to});}
    }
   }
   if(!std::isfinite(distance[T]))break;
   long double path_cost=distance[T]+potential[T]-potential[S];if(path_cost>=-1e-15L)break;
   for(U node=0;node<size;node++)if(std::isfinite(distance[node]))potential[node]+=distance[node];
   for(U node=T;node!=S;node=prev_node[node]){U from=prev_node[node],k=prev_edge[node];auto&e=network[from][k];assert(e.cap==1);e.cap=0;network[node][e.rev].cap=1;}
   flow++;
  }
  U selected=0;for(auto [d,k,j]:arcs)if(network[1+d][k].cap==0){U x=ds[d];assert(!leftmatch[x]&&!rightmatch[j]);leftmatch[x]=j+1;rightmatch[j]=x;selected++;matches++;total_utility+=benefit(x,j)+exterior;}
  assert(selected==flow);arcs_total+=arcs.size();
 }
 assert(matches<=initial_cardinality);
 std::cerr<<std::setprecision(20)<<"GLOBAL components "<<components.size()<<" max_donors "<<max_component_donors<<" max_uses "<<max_component_uses<<" arcs "<<arcs_total<<" selected "<<matches<<" initial_max_cardinality "<<initial_cardinality<<" total_utility "<<total_utility<<"\n";
}

std::vector<int64_t>hist(h+1);for(U x=1;x<n;x++)if(active[x]){assert(degree[x]);U r=ranks[x];if(args[x][0]){hist[r]+=degree[x]-1;hist[h-r]++;for(U y:args[x]){assert(r>=ranks[y]);hist[r-ranks[y]]++;}}else hist[1]+=degree[x];}
for(U j=0;j<q;j++){U r=ranks[roots[j]];if(kind[j]){hist[r]++;hist[h]++;loss+=r;}else{assert(r<=h-1);hist[h-1-r]++;hist[1]++;}}
V changed=0;for(U donor:donors)if(leftmatch[donor]){U e=uses[leftmatch[donor]-1],target=nd(e),value=e>>31?target:args[target][e&1];assert(value==args[donor][0]||value==args[donor][1]);if(value==args[donor][0])changed++;U ru=ranks[donor],rv=ranks[value],rt=ranks[target];assert(rt>=ru&&ru>=rv);hist[h-ru]--;hist[rv]--;hist[rt-rv]--;hist[rt-ru]++;}
V R=c+q-matches,sum=0;for(U r=0;r<=h;r++){assert(hist[r]>=0);sum+=r*hist[r];}assert(sum==h*R+2*loss);
std::ofstream wb(prefix+".uses.bin",std::ios::binary);U wh[2]={n,U(matches)};write_array(wb,wh);
std::ofstream wit(prefix+".uses.json");wit<<"{\"h\":"<<h<<",\"n\":"<<n<<",\"seed\":"<<seed<<",\"mode\":"<<mode<<",\"exchanges\":"<<improvements<<",\"links\":[";U wi=0;for(U donor:donors)if(leftmatch[donor]){U use=uses[leftmatch[donor]-1];U we[2]={donor,use};write_array(wb,we);if(wi++)wit<<",";wit<<"["<<donor<<","<<use<<"]";}wit<<"]}"<<std::endl;assert(wit&&wb);assert(wi==matches);std::cerr<<"WEIGHTED basis "<<argv[3]<<" costs "<<costs.size()<<" initial_cardinality "<<initial_cardinality<<" losses "<<cardinality_losses<<" gains "<<cardinality_gains<<" deficient_costs "<<deficient_costs<<" exchanges "<<improvements<<"\n";
std::cout<<"{\"h\":"<<h<<",\"v\":"<<v<<",\"c\":"<<c<<",\"q\":"<<q<<",\"baseline_R\":"<<c+q<<",\"matched\":"<<matches<<",\"R\":"<<R<<",\"orientation_changes\":"<<changed<<",\"rank_sum\":"<<sum<<",\"loss\":"<<loss<<",\"histogram\":[";for(U r=0;r<=h;r++){if(r)std::cout<<",";std::cout<<hist[r];}std::cout<<"]}"<<std::endl;
}
