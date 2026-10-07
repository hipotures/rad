"""Report the matched-module guard rather than the more favorable old-control delta."""
from lab import ROOT,load,save
base=ROOT/'experiments/E025-direct-parts-off-guard';a=load(base/'summary.json')
cells={(c['profile'],c['role']):c for c in a['cells']};rows=[]
for profile in ['32k','128k']:
    on=cells[profile,'reference']['statistics'];off=cells[profile,'candidate']['statistics']
    rows.append({'profile':profile,'ON_TG':on['TG'],'OFF_TG':off['TG'],
      'ON_vs_OFF_TG_delta_pct':100*(on['TG']['median']/off['TG']['median']-1),
      'ON_vs_OFF_wall_delta_pct':100*(on['wall_s']['median']/off['wall_s']['median']-1),
      'same_binary':True,'same_capacity':True,
      'all_paired_outputs_same':all(p['same_output_hash'] for c in a['comparisons'] if c['profile']==profile for p in c['paired'])})
result={'state':'COMPLETE_MIXED','rows':rows,
 'decision':'Direct rows regress32k versus same-binaryOFF and retain an apparent128k median advantage. Paired effects are mixed and ranges overlap. This is a workload/batch-dependent observation, not a portable20.57% win versus an earlier binary. No production switch or extra unchanged repetition.',
 'correctness':'Captured two-device row ownership,63nativepass/2skip/4knownenvironmentfail,Python268pass/7skip,realIQ0fail,10sameanswers,and repaired fullactual4096ID/router/path/MTP/cache/heat/head parity at both profiles.',
 'resource':'Zero additional explicit GPU buffers; old hit_out retained for equal capacity. Driver graph allocations may differ and are not assumed free; normal telemetry retains peaks.',
 'repair':'diagnostic-v1 omitted first-head capture; retained INVALID_DIAGNOSTIC_CAPTURE. Newdiagnostic-v2 repairs only diagnostics, unchanged clean binary.',
 'next':'Keep candidate for independent-workload followup. Do not select a universal baseline from three serial repetitions.'}
save(base/'attribution.json',result)
with (base/'report.md').open('a') as f:
    f.write('\n## Interpretation\n\n'+result['decision']+'\n\n'+result['correctness']+'\n\n'+result['resource']+'\n')
direct=ROOT/'experiments/E023-direct-parts'
save(direct/'guard-conclusion.json',result)
with (direct/'report.md').open('a') as f:
    f.write('\n## Same-binary guard\n\n'+result['decision']+'\n\nSee ../E025-direct-parts-off-guard/attribution.json for ON-versus-OFF deltas and raw references.\n')
print(result)
