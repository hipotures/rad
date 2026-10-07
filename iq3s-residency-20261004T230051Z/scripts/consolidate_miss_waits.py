"""Finish E011 without treating instrumentation rates or selected-layer sums as global gains."""
import csv
from lab import ROOT,load,save
out=ROOT/'experiments/E011-miss-waits';analyses=[];rows=[]
for profile in ['32k','128k']:
    a=load(out/'v1'/profile/'analysis.json');analyses.append(a)
    for layer,ph in a['phase_statistics_us'].items():
        for phase,s in ph.items():
            rows.append({'profile':profile,'layer':int(layer),'phase':int(phase),'phase_name':a['phase_definitions'][phase],'all_median_us':s['all']['median'],'all_p95_us':s['all']['p95'],'CPU_zero_median_us':s['CPU_zero']['median'] if s['CPU_zero'] else None,'CPU_nonzero_median_us':s['CPU_nonzero']['median'] if s['CPU_nonzero'] else None,'CPU_nonzero_p95_us':s['CPU_nonzero']['p95'] if s['CPU_nonzero'] else None,'mapped_nonzero_median_us':s['mapped_nonzero']['median'] if s['mapped_nonzero'] else None,'mapped_nonzero_n':s['mapped_nonzero']['n'] if s['mapped_nonzero'] else 0,'source':str(out/'v1'/profile/'analysis.json')})
summary={'state':'COMPLETE_POSITIVE_DIAGNOSTIC','rows':rows,'profiles':[{'profile':a['profile'],'span_count':a['span_count'],'buffer_CPU_bytes':a['buffer_CPU_bytes'],'same_input_comparison':a['same_input_comparison'],'trace_validation':a['trace_validation']} for a in analyses],'interpretation':'All4096output IDs, allMTPwindowT/acceptances and allrouter entries exactly match previousv7 diagnostics, first-head logits bit-identical at bothprofiles. Direct GPU spans distinguish mostly overlappedCPUwork from occasional exposedCPUwait and expensive mapped execution. This is not a policy or global TG gain.','instrumentation':'Same-trajectory diagnosticTG differs +21.5%32k/-9.45%128k across separate builds/time. Cannot certify<=1% overhead or claim a causal node speedup from onepair. All diagnosticTG excluded from headline ranking.','limits':['3selectedlayers only; no48layer extrapolation or overlappingwait subtraction.','GPU clock elapsed resolution observed roughly1us; event/launch floors included.','Mapped groups rare but around164-195us vs9us empty launch; CPU wait median4-6us, CPU-positive p95around66-150us and outliers.','HostGPUreach wait is not equivalent to exposedCPU/mapped/boundary latency.'],'next':'E012 unchanged compatible-policy diagnostic and same-input head/trajectory accounting; strengthen surprising128k live gain before recommending a winner.'}
save(out/'summary.json',summary)
with (out/'summary.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
lines=['# Selected-layer GPU wait diagnosis','','Status: COMPLETE_POSITIVE_DIAGNOSTIC. No algorithm change.','','The48external CUDA timing events bracket four phases at layers2,24,40 after the existing graph replay/synchronization. Bothprofiles pass full accounting, exact output/router/MTP trajectory comparison, and one-position numeric head parity (KL0/maxdifference0). Event fixture,13targeted native tests and realIQexpert parity pass.','',
       '| Profile | Layer | Phase | Median us | P95 us | CPU-positive median/P95 us | Mapped-positive median us (N) |','|---|---:|---|---:|---:|---:|---:|']
for r in rows:
    cp=f"{r['CPU_nonzero_median_us']:.1f}/{r['CPU_nonzero_p95_us']:.1f}" if r['CPU_nonzero_median_us'] is not None else 'unavailable'
    mp=f"{r['mapped_nonzero_median_us']:.1f} ({r['mapped_nonzero_n']})" if r['mapped_nonzero_median_us'] is not None else 'unavailable'
    lines.append(f"| {r['profile']} | {r['layer']} | {r['phase_name']} | {r['all_median_us']:.1f} | {r['all_p95_us']:.1f} | {cp} | {mp} |")
lines+=['',summary['interpretation'],'',summary['instrumentation'],'',
        'The CPU-completion span brackets only the GPU wait kernel before returned rows are copied; it includes event/doorbell floors. Most CPU-positive groups have only a few microseconds exposed after local expert compute, but the tail can be much larger. Mapped-positive groups are measurably more expensive than the empty mapped launch. These phases are not the time for allCPUexpert arithmetic, and not the total critical path. Do not multiply the selected-layer results by48.','',
        'The32k/128k CPU record buffers written are714816/834624bytes; reserve capacity is120000records(5.76MB). There are no explicit newGPUbuffers; internal CUDAevent memory is unknown. Original expert slot/class capacities match. All histories, rows, clocks and tests are retained.','',
        'Reproducer: variants/diagnostic-v8/diagnose-profiles.sh with a fresh --attempt name. This tested launcher is diagnostic only and remains separate from clean headline binaries.','']
(out/'report.md').write_text('\n'.join(lines)+'\n')
print(summary['state'],flush=True)
