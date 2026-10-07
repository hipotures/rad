from common import *
s=(DEC/'scripts/offline.cpp').read_text()
# Stable policies share identical simulated copies/spares; logical interval pacing remains an assumption.
s=s.replace('heat[l*512+e]+=1.f;}};','heat[l*512+e]+=1.f;}if(q4_oracle.causal_policy)q4_oracle.scorer.observe(l,w.routes.ids[l],w.T*10,wi*48+l);};')
s=s.replace('   demand(wi,l);\n   for(auto&a:q4_oracle.workers)', '   for(auto&a:q4_oracle.workers)',1)
s=s.replace('   for(int j=0;j<q4_tape.current.T*10;++j){int e=', '   demand(wi,l);\n   for(int j=0;j<q4_tape.current.T*10;++j){int e=',1)
s=s.replace('(25+wi+1)%4','(q4_tape.header.initial_rounds+wi+1)%4')
# Do not publish a completed copy whose current eligible victim fails the same guard.
s=s.replace('if(v>=0){int old=', 'if(v>=0&&(!q4_oracle.causal_policy||q4_oracle.scorer.accept(w.layer,v,ev,std::max(ev,e.target),q4_oracle.causal_policy,heat.data(),q4_oracle.victim_threshold))){int old=')
s=s.replace('w.state.store(0);now+=.045;}}}', 'w.state.store(0);now+=.045;}else if(q4_oracle.causal_policy){e.status=5;w.state.store(0);}}}')
s=s.replace('<<",\\"measured_model_TG\\":null}"','<<",\\"scorer_feature_ms\\":"<<q4_oracle.scorer.feature_ns/1e6<<",\\"scorer_model_ms\\":"<<q4_oracle.scorer.score_ns/1e6<<",\\"scorer_selection_ms\\":"<<q4_oracle.scorer.selection_ns/1e6<<",\\"scores\\":"<<q4_oracle.scorer.scores<<",\\"cache_hits\\":"<<q4_oracle.scorer.cache_hits<<",\\"rejections\\":"<<q4_oracle.scorer.rejections<<",\\"invalid_predictions\\":"<<q4_oracle.scorer.invalid<<",\\"host_model_bytes\\":"<<q4_oracle.scorer.memory_bytes()<<",\\"measured_model_TG\\":null}"')
marker='<<",\\\"modeled_event_ms\\\":\"<<event_ms'
insert='<<",\\\"scorer_feature_ms\\\":\"<<q4_oracle.scorer.feature_ns/1e6<<",\\\"scorer_model_ms\\\":\"<<q4_oracle.scorer.score_ns/1e6<<",\\\"scorer_selection_ms\\\":\"<<q4_oracle.scorer.selection_ns/1e6<<",\\\"scores\\\":\"<<q4_oracle.scorer.scores<<",\\\"cache_hits\\\":\"<<q4_oracle.scorer.cache_hits<<",\\\"rejections\\\":\"<<q4_oracle.scorer.rejections<<",\\\"invalid_predictions\\\":\"<<q4_oracle.scorer.invalid<<",\\\"host_model_bytes\\\":\"<<q4_oracle.scorer.memory_bytes()'+marker
assert marker in s;s=s.replace(marker,insert)
(C/'scripts/offline.cpp').write_text(s)
