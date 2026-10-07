"""Opt-in victim scorer; original full/off/current paths retain their decisions."""
from common import *
p=C/'source/runtime/include/strata/research/q4_oracle.hpp';s=p.read_text()
s=s.replace('#include "strata/research/q4_future_view.hpp"','#include "strata/research/q4_future_view.hpp"\n#include "strata/research/q4_victim_model.hpp"')
s=s.replace(' int32_t* res=nullptr;', ' mutable VictimScorer scorer; int causal_policy=0;double victim_threshold=.4;\n int32_t* res=nullptr;')
s=s.replace(' Q4Oracle(){const char* p=', ''' Q4Oracle(){scorer.reset();const char* vp=std::getenv("STRATA_Q4_CAUSAL_VICTIM");if(vp){std::string v(vp);causal_policy=v=="native"?1:v=="recency"?2:v=="logistic"?3:v=="tree"?4:0;require(causal_policy||v=="off","unknown causal victim mode");}if(causal_policy>=3)require(scorer.load(std::getenv("STRATA_Q4_VICTIM_MODEL")),"invalid victim checkpoint");const char* th=std::getenv("STRATA_Q4_VICTIM_THRESHOLD");if(th)victim_threshold=std::atof(th);require(std::isfinite(victim_threshold)&&victim_threshold>=0&&victim_threshold<=1,"invalid victim threshold");const char* p=''',1)
s=s.replace('  auto nx=victim_view.next(l*512+e,at,at);','  if(causal_policy)return scorer.value(l,e,at,causal_policy,heat);\n  auto nx=victim_view.next(l*512+e,at,at);',1)
s=s.replace(' void begin(){if(!configured||!q4_tape.active)return;', ' void begin(){if(!configured||!q4_tape.active)return;scorer.reset();')
s=s.replace('int old=res[w.layer*512+v];uint64_t t=ns();','if(causal_policy&&!scorer.accept(w.layer,v,current,std::max(current,e.target),causal_policy,heat,victim_threshold)){retire(w,5);return;}int old=res[w.layer*512+v];require(old>=0&&v!=w.expert&&!protected_now(w.layer,v),"publication victim changed");uint64_t t=ns();',1)
old='int vn=victim_view.next(l*512+v,current,current).event;if(vn>=0&&vn<=target)continue;'
new='if(causal_policy){if(!scorer.accept(l,v,current,target,causal_policy,heat,victim_threshold))continue;}else{int vn=victim_view.next(l*512+v,current,current).event;if(vn>=0&&vn<=target)continue;}'
assert old in s;s=s.replace(old,new)
s=s.replace('damage=victim_view.count(l*512+v,current+1,utility_end,current);','damage=causal_policy?0:victim_view.count(l*512+v,current+1,utility_end,current);')
s=s.replace(' void observe_cpu(){if(tracked&&q4_tape.active&&!layers.empty())layers.back().cpu_end=ns();}', ' void observe_cpu(){if(tracked&&q4_tape.active&&!layers.empty()){layers.back().cpu_end=ns();if(causal_policy){auto& a=layers.back();scorer.observe(a.layer,a.ids,a.n,(int)a.event);}}}')
s=s.replace('  active=false;tracked=false;', '''  std::fprintf(stderr,"Q4_VICTIM_END policy=%d threshold=%.6f scores=%llu cache_hits=%llu invalid=%llu rejected=%llu feature_ms=%.3f score_ms=%.3f selection_ms=%.3f host_bytes=%zu frozen_weights=1 prefix_only=1 max_cache_age_windows=1\\n",causal_policy,victim_threshold,(unsigned long long)scorer.scores,(unsigned long long)scorer.cache_hits,(unsigned long long)scorer.invalid,(unsigned long long)scorer.rejections,scorer.feature_ns/1e6,scorer.score_ns/1e6,scorer.selection_ns/1e6,scorer.memory_bytes());\n  active=false;tracked=false;''')
# Charge scan/ranking time separately; feature/model timers are nested and cannot be summed with planner.
old='int victim(int l,int incoming,int at)const{int best=-1;'
new='int victim(int l,int incoming,int at)const{uint64_t start=VictimScorer::now();int best=-1;'
assert old in s;s=s.replace(old,new).replace('if(value>score){score=value;best=e;}}return best;}','if(value>score){score=value;best=e;}}if(causal_policy)scorer.selection_ns+=VictimScorer::now()-start;return best;}')
p.write_text(s)
ledger('Integration substrate verified: bbfea295 decomposition-v2 differs from Phase0 capture117bc89 only in typed future views and opt-in unknown handling. Causal branch removes all victim future queries; incoming E64 and first-feasible order unchanged. Current-window safety remains privileged. Scoring cache valid at most one main window; prefix updates invalidate per-layer. Resident age/history omitted, so no stale native-policy placement feature is copied.')
