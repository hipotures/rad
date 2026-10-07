"""Separate timing/row diagnostic; never replace the frozen speed candidate binary."""
import pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]);subprocess.run([sys.executable,str(root/'scripts/patch_persistent_runtime_v2_fixed.py'),str(src)],check=True)
p=src/'include/strata/research/persistent_runtime.hpp';s=p.read_text();s=s.replace('std::vector<float> prediction;','std::vector<uint64_t>prediction_observed,actual_observed,nonlocal_observed;uint64_t enqueue_ns=0,join_ns=0;\n std::vector<float> prediction;')
s=s.replace('prediction.assign(48*512,0.f);','prediction.assign(48*512,0.f);prediction_observed.assign(48*512,0);actual_observed.assign(48*512,0);nonlocal_observed.assign(48*512,0);')
s=s.replace('uint64_t issue=0,published=0','uint64_t prediction_time=0,demand_before_copy=0,miss_before_copy=0,enqueue_begin=0,enqueue_return=0,issue=0,published=0')
s=s.replace('host_prediction_entries=select_ns=pending_wait_ns=0;','host_prediction_entries=select_ns=pending_wait_ns=enqueue_ns=join_ns=0;')
s=s.replace('const auto*w=host_weights[dev]+i*max_tokens*k;','const auto*w=host_weights[dev]+i*max_tokens*k;const uint64_t observed=persistent_ns();')
s=s.replace('prediction[targets[i]*512+in[q]]+=w[q]*10.f;','prediction[targets[i]*512+in[q]]+=w[q]*10.f;prediction_observed[targets[i]*512+in[q]]=observed;')
s=s.replace('int slot,uint64_t bytes){if(!enabled)return;','int slot,uint64_t bytes,uint64_t begin_copy,uint64_t return_copy){if(!enabled)return;')
s=s.replace('row.issue=persistent_ns();','row.issue=persistent_ns();row.prediction_time=prediction_observed[a];row.enqueue_begin=begin_copy;row.enqueue_return=return_copy;enqueue_ns+=return_copy-begin_copy;')
s=s.replace('pending_ms=%.3f; safe-boundary','pending_ms=%.3f enqueue_ms=%.3f join_ms=%.3f; safe-boundary').replace('select_ns/1e6,pending_wait_ns/1e6);','select_ns/1e6,pending_wait_ns/1e6,enqueue_ns/1e6,join_ns/1e6);')
s=s.replace('issue_ns,published_ns','prediction_observed_ns,enqueue_begin_ns,enqueue_return_ns,issue_ns,copy_complete_observed_upperbound_publish_ns')
s=s.replace('"%d,%d,%d,%d,%d,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\\n"','"%d,%d,%d,%d,%d,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\\n"')
s=s.replace('(unsigned long long)a.bytes,(unsigned long long)a.issue','(unsigned long long)a.bytes,(unsigned long long)a.prediction_time,(unsigned long long)a.enqueue_begin,(unsigned long long)a.enqueue_return,(unsigned long long)a.issue')

s=s.replace('  for(int q=0;q<tokens*k;++q){int e=actual[q];', '  const uint64_t actual_time=persistent_ns();\n  for(int q=0;q<tokens*k;++q){int e=actual[q];')
s=s.replace('last[at]=window;', 'last[at]=window;actual_observed[at]=actual_time;if(resident[at]<0)nonlocal_observed[at]=actual_time;')
s=s.replace('row.prediction_time=prediction_observed[a];', 'row.prediction_time=prediction_observed[a];row.demand_before_copy=actual_observed[a];row.miss_before_copy=nonlocal_observed[a];')
s=s.replace('prediction_observed_ns,enqueue_begin_ns', 'prediction_observed_ns,last_actual_demand_before_copy_ns,last_nonlocal_demand_before_copy_ns,enqueue_begin_ns')
s=s.replace('"%d,%d,%d,%d,%d,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\\n"', '"%d,%d,%d,%d,%d,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\\n"')
s=s.replace('(unsigned long long)a.prediction_time,(unsigned long long)a.enqueue_begin', '(unsigned long long)a.prediction_time,(unsigned long long)a.demand_before_copy,(unsigned long long)a.miss_before_copy,(unsigned long long)a.enqueue_begin')
p.write_text(s)
p=src/'src/program/generate.cpp';s=p.read_text();start=s.index('        auto adapt = [&]() -> bool {');end=s.index('        // #477: write the learned profile',start);a=s[start:end]
anchor='                if (slot < 0 || b == nullptr ||';assert a.count(anchor)==1;a=a.replace(anchor,'                const uint64_t persistent_enqueue_begin = strata::research::persistent_ns();\n'+anchor)
old='persistent.issue(s.layer, s.in, out_layer, s.out, slot, lab_blob[(size_t)s.layer]);';assert a.count(old)==1;a=a.replace(old,'persistent.issue(s.layer, s.in, out_layer, s.out, slot, lab_blob[(size_t)s.layer], persistent_enqueue_begin, strata::research::persistent_ns());');s=s[:start]+a+s[end:]
anchor='                    ++dec_windows; dec_T += T;\n                }\n                if (adapt_thr.joinable()) adapt_thr.join();'
assert s.count(anchor)==1, 'Expected the unique successful serve-mode join after draft timing'
# Only the successful serve-mode join is measured; error cleanup and CLI joins are unchanged.
s=s.replace(anchor,'                    ++dec_windows; dec_T += T;\n                }\n                const uint64_t persistent_join_begin = strata::research::persistent_ns();\n                if (adapt_thr.joinable()) adapt_thr.join();\n                if (lab_persistent) persistent.join_ns += strata::research::persistent_ns() - persistent_join_begin;',1)
p.write_text(s)
