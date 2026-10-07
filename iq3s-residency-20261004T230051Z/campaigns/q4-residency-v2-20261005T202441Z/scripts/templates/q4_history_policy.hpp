// Local Q4 Residency v2 cheap joint-utility finalist. Disabled by default.
// Changes only safe end-of-window admissions; expert arithmetic is unchanged.
#pragma once
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <vector>
namespace strata::research {
struct Q4HistoryPolicy {
    bool enabled=false,active=false;
    const int32_t* table=nullptr;
    int nl=0,ne=0,split=24;
    std::vector<float> fast,counts;
    std::vector<uint64_t> bytes;
    uint64_t windows=0,promotions=0,promotion_bytes=0,selector_ns=0;
    Q4HistoryPolicy(){const char* p=std::getenv("STRATA_Q4_HISTORY");enabled=p&&p[0]=='1';}
    void configure(const int32_t* r,int layers,int experts,const std::vector<uint64_t>& blobs){
        if(!enabled)return;
        if(layers!=48||experts!=512||blobs.size()!=48)throw std::runtime_error("Q4 history requires frozen48x512 geometry");
        table=r;nl=layers;ne=experts;bytes=blobs;fast.assign(nl*ne,0);counts.assign(nl*ne,0);
    }
    void begin_request(){if(!enabled)return;active=true;std::fill(fast.begin(),fast.end(),0);windows=promotions=promotion_bytes=selector_ns=0;}
    void begin_window(){if(enabled&&active)std::fill(counts.begin(),counts.end(),0);}
    void observe(const int32_t* r,int layer,const int32_t* ids,int n){
        if(!enabled||!active||r!=table||layer<0||layer>=nl)return;
        for(int i=0;i<n;++i){if(ids[i]<0||ids[i]>=ne)throw std::runtime_error("Q4 history invalid expert ID");counts[layer*ne+ids[i]]+=1;}
    }
    void end_window(){if(enabled&&active){for(size_t i=0;i<fast.size();++i)fast[i]=.5f*fast[i]+counts[i];++windows;}}
    template<class Swap> void select(const std::vector<float>& heat,const std::vector<int32_t>& resident,std::vector<Swap>& swaps,int max_swaps){
        if(!enabled||!active)return;
        auto begin=std::chrono::steady_clock::now();
        if(heat.size()!=fast.size()||resident.size()!=fast.size())throw std::runtime_error("Q4 history residency geometry");
        struct Choice {double priority;int l,in,out;};std::vector<Choice> options;options.reserve(512);
        std::vector<std::pair<float,int>> incoming,victims;incoming.reserve(ne);victims.reserve(ne);
        for(int l=0;l<nl;++l){
            incoming.clear();victims.clear();
            for(int e=0;e<ne;++e){size_t j=l*ne+e;float score=.2f*heat[j]+(2.f/3.f)*fast[j];
                if(resident[j]>=0)victims.emplace_back(score,e);else if(score>=1)incoming.emplace_back(score,e);}
            std::sort(incoming.begin(),incoming.end(),[](auto a,auto b){return a.first!=b.first?a.first>b.first:a.second<b.second;});
            std::sort(victims.begin(),victims.end());double copy_ms=bytes[l]/13.2e6+.0042;
            for(size_t i=0;i<std::min(incoming.size(),victims.size());++i){double benefit=(incoming[i].first-victims[i].first)*.25-copy_ms;
                if(benefit<=.125)break;options.push_back({benefit/bytes[l],l,incoming[i].second,victims[i].second});}
        }
        std::sort(options.begin(),options.end(),[](const Choice& a,const Choice& b){if(a.priority!=b.priority)return a.priority>b.priority;if(a.l!=b.l)return a.l<b.l;if(a.in!=b.in)return a.in<b.in;return a.out<b.out;});
        std::array<uint64_t,2> used{};swaps.clear();
        for(const auto& c:options){int device=c.l>=split;if((int)swaps.size()>=max_swaps)break;if(used[device]+bytes[c.l]>160ull*1024*1024)continue;
            used[device]+=bytes[c.l];swaps.push_back({float(c.priority),c.l,c.in,c.out});}
        promotions+=swaps.size();for(const auto& s:swaps)promotion_bytes+=bytes[s.layer];
        selector_ns+=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-begin).count();
    }
    void finish(){if(!enabled||!active)return;active=false;std::fprintf(stderr,"Q4_HISTORY windows=%llu promotions=%llu bytes=%llu selector_ms=%.3f\n",(unsigned long long)windows,(unsigned long long)promotions,(unsigned long long)promotion_bytes,selector_ns/1e6);}
};
inline Q4HistoryPolicy q4_history;
}
