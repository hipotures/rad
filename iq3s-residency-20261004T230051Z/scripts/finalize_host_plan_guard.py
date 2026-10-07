"""Record the falsification without discarding valid measurements or outliers."""
from lab import ROOT, load, save
base=ROOT/'experiments/E022-host-plan-off-guard'
a=load(base/'summary.json')
cells={(c['profile'],c['role']):c for c in a['cells']}
rows=[]
for profile in ['32k','128k']:
    on=cells[profile,'reference']['statistics'];off=cells[profile,'candidate']['statistics']
    rows.append({'profile':profile,'ON_TG':on['TG'],'OFF_TG':off['TG'],
       'ON_vs_OFF_TG_delta_pct':100*(on['TG']['median']/off['TG']['median']-1),
       'ON_vs_OFF_wall_delta_pct':100*(on['wall_s']['median']/off['wall_s']['median']-1),
       'same_binary':True,'same_capacity':True,
       'all_paired_outputs_same':all(p['same_output_hash'] for c in a['comparisons'] if c['profile']==profile for p in c['paired'])})
result={'state':'COMPLETE_NEGATIVE_ATTRIBUTION','comparisons':rows,
    'decision':'The apparent128k+19% versus an earlier control is not an isolated host-plan effect: same-binaryOFF reaches159.0 versus158.7ON.32kON175.4 versusOFF163.6 has strongly overlapping per-run ranges and inconsistent paired effects. No portable gain or deployment recommendation.',
    'limits':'Serial batches at different wall times; three valid runs each. Same output/MTP/accounting rules out those trajectory explanations for these paired differences, not scheduling/binary-layout/VM effects. No more repetitions.',
    'next':'Same-binary diagnostic GPU/host phase timing, then source-supported direct output-row candidate if justified.',
    'raw_comparison':str(base/'summary.json')}
save(base/'attribution.json',result)
with (base/'report.md').open('a') as f:
    f.write('\n## Attribution guard\n\n'+result['decision']+'\n\n'+result['limits']+'\n')
print(result)
