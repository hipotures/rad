// Capacity and modeled transfer simulations, never inference throughput.
#include "strata/research/q4_oracle.hpp"
#include <iostream>
#include <iomanip>
using namespace strata::research;
static void require(bool ok,const char* why){Q4Tape::require(ok,why);}
static std::vector<uint64_t> blob_sizes(){std::vector<uint64_t>b(48,3072000);b[2]=3993600;for(int l:{4,30,46,47})b[l]=3584000;return b;}
static std::vector<int32_t> initial=q4_tape.initial_res;
static std::vector<float> initial_heat=q4_tape.initial_heat;
int main(int argc,char**argv){require(argc>=2,"offline mode missing");std::string mode=argv[1];std::vector<int32_t> r=initial;std::vector<float> heat=initial_heat;auto bytes=blob_sizes();q4_oracle.blobs=bytes;uint64_t local=0,cpu=0,mapped=0,copybytes=0,proms=0,victims=0;int W=(int)q4_tape.windows.size();std::vector<int> slot_class[2];for(int d=0;d<2;++d){int mx=-1;for(int l=d*24;l<(d+1)*24;++l)for(int e=0;e<512;++e)mx=std::max(mx,r[l*512+e]);slot_class[d].assign(mx+1,-1);for(int l=d*24;l<(d+1)*24;++l)for(int e=0;e<512;++e)if(r[l*512+e]>=0)slot_class[d][r[l*512+e]]=q4_oracle.cls(l);}
 q4_oracle.configured=true;q4_oracle.runtime(r.data(),heat.data(),bytes,{nullptr,nullptr},[](int,int){return (const uint8_t*)1;},[](int,int){return (void*)1;});q4_oracle.events.reserve(W*240);q4_tape.active=true;
 auto demand=[&](int wi,int l){auto& w=q4_tape.windows[wi];int kinds[512];std::fill(kinds,kinds+512,-2);std::vector<int> misses;for(int j=0;j<w.T*10;++j){int e=w.routes.ids[l][j];if(kinds[e]!=-2)continue;kinds[e]=r[l*512+e]>=0?0:-1;if(kinds[e]<0)misses.push_back(e);}int m=(int(misses.size())*72)>>8;for(int i=int(misses.size())-m;i<int(misses.size());++i)kinds[misses[i]]=1;for(int j=0;j<w.T*10;++j){int e=w.routes.ids[l][j];if(kinds[e]==0)++local;else if(kinds[e]==1)++mapped;else ++cpu;heat[l*512+e]+=1.f;}};
 if(mode=="current"){
  struct Swap{float gain;int l,in,out;};
  for(int wi=0;wi<W;++wi){for(int l=0;l<48;++l)demand(wi,l);if((25+wi+1)%4)continue;std::vector<Swap> swaps;for(int l=0;l<48;++l){std::vector<std::pair<float,int>>cand,vict;for(int e=0;e<512;++e)if(r[l*512+e]>=0)vict.emplace_back(heat[l*512+e],e);else if(heat[l*512+e]>=2)cand.emplace_back(heat[l*512+e],e);std::sort(cand.begin(),cand.end(),[](auto&a,auto&b){return a.first>b.first;});size_t n=std::min(cand.size(),vict.size());std::partial_sort(vict.begin(),vict.begin()+n,vict.end(),[](auto&a,auto&b){return a.first<b.first;});for(size_t j=0;j<n;++j){if(cand[j].first<vict[j].first+1.5f)break;swaps.push_back({cand[j].first-vict[j].first,l,cand[j].second,vict[j].second});}}std::sort(swaps.begin(),swaps.end(),[](auto&a,auto&b){return a.gain>b.gain;});if(swaps.size()>96)swaps.resize(96);for(auto&s:swaps){r[s.l*512+s.in]=r[s.l*512+s.out];r[s.l*512+s.out]=-1;copybytes+=bytes[s.l];++proms;}for(float&v:heat)v*=.7f;}
 }else if(mode=="capacity"){
  q4_oracle.horizon=0;for(int wi=0;wi<W;++wi){q4_tape.current=q4_tape.windows[wi];for(int l=0;l<48;++l){int seen[512]={};for(int j=0;j<q4_tape.current.T*10;++j){int e=q4_tape.current.routes.ids[l][j];if(seen[e]++||r[l*512+e]>=0)continue;int v=q4_oracle.victim(l,e,wi*48+l);if(v<0)continue;r[l*512+e]=r[l*512+v];r[l*512+v]=-1;++proms;copybytes+=bytes[l];}demand(wi,l);}}
 }else if(mode=="transfer"){
  std::vector<int> latest_victim(48*512,-1);int horizon=argc>2?std::atoi(argv[2]):0;q4_oracle.horizon=horizon;q4_oracle.strategy=argc>3?std::atoi(argv[3]):0;q4_oracle.active=true;
  // Identical charged physical spare accounting; conservative same-class and current-window protection.
  q4_tape.current=q4_tape.windows[0];for(int d=0;d<2;++d)for(int c=0;c<3;++c){if(d==1&&c==2)continue;int pick=-1;double best=-1e100;for(int l=d*24;l<(d+1)*24;++l)if(q4_oracle.cls(l)==c)for(int e=0;e<512;++e){if(r[l*512+e]<0||q4_oracle.protected_now(l,e))continue;int nx=q4_oracle.next(l,e,0);double s=!horizon?(nx<0?1e12:nx):(nx<0?double(horizon+1)-std::log1p(std::max(0.f,heat[l*512+e])):nx);if(s>best){best=s;pick=l*512+e;}}require(pick>=0,"spare");auto&w=q4_oracle.workers[d][c];w.dev=d;w.cls=c;q4_oracle.spare[d][c]=r[pick];r[pick]=-1;}
  // One physically modeled copy queue/device (class streams share the link). Times are assumptions,
  // not recorded wall-time triggers and not claimed model TG. Real live policy uses logical events.
  double now=0,link[2]={},ready[2][3]={};double event_ms=.57;
  for(int ev=0;ev<W*48;++ev){int wi=ev/48,l=ev%48;q4_tape.current=q4_tape.windows[wi];q4_tape.index=wi;q4_oracle.current=ev;
   for(auto&a:q4_oracle.workers)for(auto&w:a)if(w.dev>=0){if(w.state.load()==1&&ready[w.dev][w.cls]<=now){auto&e=q4_oracle.events[w.index];int v=q4_oracle.victim(w.layer,w.expert,ev);if(r[w.layer*512+w.expert]>=0){w.state.store(0);continue;}if(v>=0){int old=r[w.layer*512+v];require(slot_class[w.dev][old]==w.cls&&slot_class[w.dev][q4_oracle.spare[w.dev][w.cls]]==w.cls,"physical slot class violated");r[w.layer*512+v]=-1;r[w.layer*512+w.expert]=q4_oracle.spare[w.dev][w.cls];q4_oracle.spare[w.dev][w.cls]=old;e.victim=v;e.publish_ns=(uint64_t)(now*1e6)+1;e.published_at=ev;e.status=ev<=e.target?1:3;latest_victim[w.layer*512+v]=w.index;w.state.store(0);now+=.045;}}}
   demand(wi,l);
   for(auto&a:q4_oracle.workers)for(auto&w:a)if(w.dev>=0){int before=w.state.load();q4_oracle.plan(w);if(before==0&&w.state.load()==1){auto&e=q4_oracle.events[w.index];double staging=e.bytes/25e6,copy=e.bytes/13.2e6;ready[w.dev][w.cls]=std::max(now+staging,link[w.dev])+copy;link[w.dev]=ready[w.dev][w.cls];copybytes+=e.bytes;++proms;}}
   for(int j=0;j<q4_tape.current.T*10;++j){int e=q4_tape.current.routes.ids[l][j];victims+=r[l*512+e]<0&&latest_victim[l*512+e]>=0;}
   now+=event_ms;if(l==47){now+=2.5;if((25+wi+1)%4==0)for(float&v:heat)v*=.7f;}
  }
  uint64_t pub=0,late=0,pbytes=0;for(auto&e:q4_oracle.events)if(e.publish_ns){++pub;pbytes+=e.bytes;late+=e.status==3;}
  std::cout<<"{\"mode\":\"transfer\",\"horizon\":"<<horizon<<",\"strategy\":"<<q4_oracle.strategy<<",\"issued\":"<<proms<<",\"copied_bytes\":"<<copybytes<<",\"published\":"<<pub<<",\"published_bytes\":"<<pbytes<<",\"late_publications\":"<<late<<",\"local\":"<<local<<",\"cpu\":"<<cpu<<",\"mapped\":"<<mapped<<",\"victim_absent_observations\":"<<victims<<",\"modeled_event_ms\":"<<event_ms<<",\"assumed_staging_GB_s\":25,\"assumed_H2D_GB_s\":13.2,\"measured_model_TG\":null}"<<std::endl;
  for(auto&a:q4_oracle.workers)for(auto&w:a)w.dev=-1;return 0;
 }else require(false,"offline mode unknown");
 std::cout<<"{\"mode\":\""<<mode<<"\",\"local\":"<<local<<",\"cpu\":"<<cpu<<",\"mapped\":"<<mapped<<",\"promotions\":"<<proms<<",\"copy_bytes\":"<<copybytes<<",\"measured_model_TG\":null}"<<std::endl;
}
