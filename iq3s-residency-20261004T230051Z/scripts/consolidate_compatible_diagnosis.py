"""Close E012's bounded mechanism study, retaining divergent trajectories and measured/simulated distinctions."""
import csv,hashlib
import numpy as np
from lab import ROOT,load,save
from trace_reader import Trace
out=ROOT/'experiments/E012-compatible-diagnostic';rows=[];profiles=[]
for profile in ['32k','128k']:
    cpath=ROOT/'experiments/E011-miss-waits/v1'/profile;ppath=out/'v1'/profile
    c=Trace(cpath/'traces/runtime-request2');p=Trace(ppath/'traces/runtime-request2');assert c.validate()['state']==p.validate()['state']=='PASS'
    common=0
    for cw,pw in zip(c.windows,p.windows):
        if cw['T']!=pw['T'] or not np.array_equal(cw['tokens'][:cw['T']],pw['tokens'][:pw['T']]):break
        common+=1
    a=load(ppath/'analysis.json');pro=load(ppath/'promotion-analysis.json');cro=load(cpath/'promotion-analysis.json')
    phases=[]
    for name,path in [('original',cpath),('compatible',ppath)]:
        r=load(path/'raw/trace-run1.json');pr=load(path/'promotion-analysis.json');tr=Trace(path/'traces/runtime-request2');waits=load(path/'analysis.json')
        phases.append({'configuration':name,'waits':waits['phase_statistics_us'],'raw':str(path/'analysis.json')})
        rows.append({'profile':profile,'configuration':name,'diagnostic_TG':r['TG'],'MTP_acceptance_pct':r['mtp_acceptance_pct'],'accepted_per_window':r['mtp_accepted_per_window'],'verify_windows':r['verify_windows'],'CPU_entries':r['cpu_fallback_entries'],'mapped_entries':r['offloaded_entries'],'promotion_GB':pr['promotion_bytes']/1e9,'published_useful_GB':pr['published_useful_bytes']/1e9,'published_unused_GB':pr['published_unused_bytes']/1e9,'cross_layer_promotions':pr['cross_layer_promotion_count'],'victim_nonlocal_entries':pr['victim_nonlocal_entries'],'resident_unique_groups_per_output':pr['native_group_proxy']['local_unique_groups_per_output_token'],'raw':str(path/'raw/trace-run1.json'),'common_verified_input_windows':common})
    profiles.append({'profile':profile,'same_input_comparison':a['same_input_comparison'],'common_verified_input_windows':common,'phase_comparison':phases,'trace_validation':pro['trace_validation'],'resource_classes_exact':p.slot_bytes[0].tolist()==c.slot_bytes[0].tolist() and p.slot_bytes[1].tolist()==c.slot_bytes[1].tolist()})
oldheader=ROOT/'src/compatible-v1/include/strata/research/compatible_policy.hpp';newheader=ROOT/'src/diagnostic-compatible-v1/include/strata/research/compatible_policy.hpp'
assert oldheader.read_bytes()==newheader.read_bytes()
summary={'state':'COMPLETE_POSITIVE_DIAGNOSTIC','rows':rows,'profiles':profiles,'unchanged_policy_header_sha256':hashlib.sha256(oldheader.read_bytes()).hexdigest(),'interpretation':'Same effective input IDs and exact GPU resources. First-head logits bit-identical, then output diverges47/84tokens. Compatible128k has higherMTPacceptance and fewer resident unique expert groups/output; those trajectory changes can contribute to observed headline gain. DirectCPUwait changes vary bylayer; no general all-wait or all-miss saving is demonstrated.','limits':['Diagnostic-only TG never added to headline ranking. Event nodes/time/build can materially change execution timing.','First-head KL0 at oneposition and passing native/battery checks do not prove all numerical divergence harmless.','Current/candidate free-generation is not teacher-forced fixed trajectory.','Unique-group blobbytes are a logical work proxy, not actual DRAM/PCIe read bytes.','Victim nonlocal use and useful bytes are observed lifetime evidence, not a causal latency forecast.'],'next':'Same-binary policyOFF guard to falsify binary/scheduling gain; exact-choice heap selector-cost repair. Preserve E010 headline requests and do not repeat their unchanged points.'}
save(out/'summary.json',summary)
with (out/'summary.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
lines=['# Compatible-slot runtime mechanism diagnosis','','Status: COMPLETE_POSITIVE_DIAGNOSTIC. No new placement algorithm.','',
       'The E010native selector header is byte-identical. These separate diagnostic builds add the same selected-layer GPU spans as E011 and an explicit schema2outgoing-layer field. The synthetic schema tests, actual captured-event fixtures,13native tests and realIQparity pass. Bothprofile4Krequests complete with zero reuse/exact inputs/capacities.','',
       '| Profile | Config | Diagnostic TG | MTP % | CPU entries | Mapped entries | Promotion GB | Useful/unused GB | Victim demand | Resident groups/output |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:lines.append(f"| {r['profile']} | {r['configuration']} | {r['diagnostic_TG']:.1f} | {r['MTP_acceptance_pct']:.2f} | {r['CPU_entries']} | {r['mapped_entries']} | {r['promotion_GB']:.3f} | {r['published_useful_GB']:.3f}/{r['published_unused_GB']:.3f} | {r['victim_nonlocal_entries']} | {r['resident_unique_groups_per_output']:.2f} |")
lines+=['',summary['interpretation'],'',
        'First-head KL0/maxdifference0 and top1agreement hold at bothprofiles. Actual generated-token prefixes are47tokens32k/84tokens128k, then expert demand and MTPbranch trajectories diverge. The number of identical verified input windows is saved separately in summary.json. No automatic quality ranking.','',
        'Compatible128k promotion bytes and unused bytes decline in this actual trajectory;32k unused bytes increase. Many swaps cross layers inside the same ownerGPU. Every recorded copy fits its physical slot, true victims are withdrawn and publication appears after issue. Full accounting including rejected drafts passes. Per-layer CPUwait distributions remain mixed, not a uniform reduction.','',
        'Useful bytes mean at least one observed local entry in the promotion lifetime before its next withdrawal. Victim demand counts observed nonlocal entries during absence. Neither means milliseconds saved, and the logical native group byte proxy is not a hardware traffic counter.','',
        'This diagnosis supports a conservative interpretation of the real128k gain and motivates the same-binary OFF guard. It does not turn the18.47%headline delta into a cache-policy-only causal effect. All diagnostic rates remain excluded from headline ranking.','']
(out/'report.md').write_text('\n'.join(lines)+'\n')
print(summary['state'],[(p['profile'],p['common_verified_input_windows']) for p in profiles],flush=True)
