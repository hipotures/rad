// Fixed I+J ordered-profile surrogate for ORIGINAL-envelope matching ties.
// Authored for the CPU campaign. Gram formulas adapted from icekylinx's
// Apache-2.0 full_profiles23.cpp at eligible PR40 commit43f59ff533598762.
// This one-field ranking is heuristic; the selected matching must be fully
// reprofiled by the unchanged five-prime rational reconstruction afterward.
#pragma once
#include <limits>
#include <stdexcept>

class FixedMatchingSurrogate {
    struct Frame { V core, cover; U rank; };
    static constexpr V prime = 2305843009213693951ULL;
    U h;
    std::vector<Frame> frames;
    std::vector<U> node_frame;
    std::vector<std::vector<V>> matrices;
    std::unordered_map<V,double> scores;
    static V mul(V a,V b) { return (__uint128_t)a*b%prime; }
    static V sub(V a,V b) { return (a+prime-b)%prime; }
    static V power(V a,V b) {
        V result=1;
        for(;b;b>>=1,a=mul(a,a)) if(b&1) result=mul(result,a);
        return result;
    }
    const std::vector<V>& matrix(U id) {
        auto& A=matrices[id];
        if(!A.empty()) return A;
        A.assign(h*h,0);
        if(id==0) return A;
        if(id==1) { for(U i=0;i<h;i++) A[i*h+i]=1; return A; }
        const auto f=frames[id];
        const U c=popcount64(f.core);
        const V out=f.cover&~f.core;
        const U nn=popcount64(out);
        if(c==3) {
            const V inv=power(6*(h+1),prime-2);
            for(U i=0;i<h;i++) for(U j=0;j<h;j++) {
                const V wi=3+((f.core>>i)&1);
                const V zj=((f.core>>j)&1)?3*(h+1)-10:prime-10;
                A[i*h+j]=mul(mul(wi,zj),inv);
            }
            return A;
        }
        assert(c==1||c==2);
        const V s=3-c, d=s*s+(c-1)*nn;
        const V inv=power(3*(h+1)*d,prime-2);
        for(U i=0;i<h;i++) for(U j=0;j<h;j++) {
            const V oi=(out>>i)&1,oj=(out>>j)&1;
            const V wi=3+((f.core>>i)&1);
            const V zj=((f.core>>j)&1)?3*(h+1)-10:prime-10;
            V num=(mul(s*oi,zj)+3*(h+1)*s*wi*oj+mul(nn*wi,zj))%prime;
            num=sub(num,3*(h+1)*(c-1)*oi*oj);
            A[i*h+j]=(V(i==j&&oi)+mul(num,inv))%prime;
        }
        return A;
    }
    double profile(U a,U b) {
        if(a==b) return 0;
        assert(frames[b].rank>=frames[a].rank);
        const U rr=frames[b].rank-frames[a].rank;
        if(rr<=2) return 0; // Same conservative singleton fallback as base.
        if(a==0&&b==1) return h*std::log(double(h));
        const V key=(V(a)<<32)|b;
        auto found=scores.find(key);
        if(found!=scores.end()) return found->second;
        const auto& A=matrix(a); const auto& B=matrix(b);
        std::vector<V> M(h*h);
        for(U i=0;i<h*h;i++) M[i]=sub(B[i],A[i]);
        std::vector<std::pair<U,U>> pivots;
        for(U i=0;i<h;i++) {
            int j=int(h)-1;
            while(j>=0&&!M[i*h+j]) j--;
            if(j<0) continue;
            pivots.push_back({i,U(j)});
            const V inv=power(M[i*h+j],prime-2);
            for(U k=i+1;k<h;k++) {
                const V z=mul(M[k*h+j],inv);
                if(z) for(U col=0;col<=U(j);col++)
                    M[k*h+col]=sub(M[k*h+col],mul(z,M[i*h+col]));
            }
        }
        assert(pivots.size()==rr);
        double result=0;
        U run=0;
        for(U j=0;j<pivots.size();j++) {
            if(j&&pivots[j].first==pivots[j-1].first+1&&
                  pivots[j].second==pivots[j-1].second+1) run++;
            else { if(run) result+=run*std::log(double(run)); run=1; }
        }
        if(run) result+=run*std::log(double(run));
        assert(std::isfinite(result));
        scores[key]=result;
        return result;
    }
public:
    FixedMatchingSurrogate(U dimension,const std::vector<V>& core,
                           const std::vector<V>& cover,const std::vector<U>& rank,
                           const std::vector<uint8_t>& active):h(dimension) {
        frames={{0,0,0},{0,0,h}};
        node_frame.assign(core.size(),0);
        std::map<std::pair<V,V>,U> lookup;
        for(U x=1;x<core.size();x++) if(active[x]) {
            auto key=std::make_pair(core[x],cover[x]);
            auto pos=lookup.find(key);
            if(pos==lookup.end()) {
                U id=U(frames.size());
                frames.push_back({core[x],cover[x],rank[x]});
                lookup[key]=id;
                node_frame[x]=id;
            } else node_frame[x]=pos->second;
        }
        matrices.resize(frames.size());
    }
    double gain(U donor,U value,U target) {
        const U d=node_frame[donor],v=node_frame[value],t=node_frame[target];
        // Max-cardinality matchings have the same total rank and W. The
        // first derivative near tau=1 favors increased sum(t*log(t)).
        return profile(d,t)-profile(d,1)-profile(0,v)-profile(v,t);
    }
    size_t profiled_pairs() const { return scores.size(); }
    size_t frame_count() const { return frames.size(); }
};

inline V scout_splitmix(V x) {
    x+=0x9e3779b97f4a7c15ULL;
    x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;
    x=(x^(x>>27))*0x94d049bb133111ebULL;
    return x^(x>>31);
}
