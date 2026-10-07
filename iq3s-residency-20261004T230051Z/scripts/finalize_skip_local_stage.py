"""Attach correctness, resources and the unconfirmed attribution caveat to E019."""
import statistics
from lab import ROOT,load,save
out=ROOT/'experiments/E019-skip-local-host-plan'
s=load(out/'summary.json')
s['state']='COMPLETE_MIXED_PROVISIONAL_ATTRIBUTION'
s['correctness']={'full_actual_output_router_heat_parity':str(out/'diagnostic-v1/summary.json'),
 'native_Python_realIQ':str(out/'v1/tests/failure-audit.json'),
 '10_identical_answers':str(out/'v1/correctness/skip-local-host-plan-v1/ground-truth-checks.json')}
s['additional_explicit_GPU_bytes_relative_E016v2']=0
s['policy_change']='None. True routing, EMA admissions and all mixed expert paths unchanged.'
s['reference_E016v2']=[]
for profile in ['32k','128k']:
 rows=[]
 for n in [1,2,3]:
  b=load(ROOT/f'experiments/E016-device-plan-ids/v2/{profile}/raw/run{n}.json')
  c=load(out/f'v1/{profile}/raw/run{n}.json')
  assert b['output_text_sha256']==c['output_text_sha256']
  counts=['mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','offloaded_entries']
  rows.append({'run':n,'reference_TG':b['TG'],'candidate_TG':c['TG'],
    'TG_delta_pct':100*(c['TG']/b['TG']-1),'same_logical_counts':all(b.get(k)==c.get(k) for k in counts)})
 s['reference_E016v2'].append({'profile':profile,'rows':rows})
s['decision']='Do not select solely from this batch. Complete new same-binary OFF guard and source-grounded GPU phase diagnosis; no extra unchanged ON requests.'
save(out/'summary.json',s)
with (out/'report.md').open('a') as f:
 f.write('''\n## Mechanism, correctness and interpretation\n\nThis opt-in suppresses only unused host plan/group/pointer construction and mapped CPU-row zeroing when every actual routed entry is local and the corrected GPU plan already owns those rows. Actual usage/heat, local-entry counts, layers and expert totals still update. Mixed CPU/mapped groups retain their original dispatch. The independent PLE fence and stable per-layer IDs are mandatory; helper/peer/batched paths remain out of scope. No expert capacity, cache policy, GPU arithmetic or routing changes.\n\nThe full diagnostic matches every actual output ID, speculative input/acceptance, router entry, execution path, initial/final heat/residency and first-head bit at both profiles. All footer categories reconcile. The 10-prompt clean battery has ten identical answers; default-off tests retain only the four previously documented environment/fixture failures.\n\nClean medians are 175.4/158.7 TG versus 155.9/133.2 in the original control. All six visible outputs and MTP/counts are unchanged, so the improvement is not explained by a new free-generation trajectory. Nevertheless, prior same-output guards also changed TG substantially, and one OFF guard reached 174.5 at32K. Serial batches/binary identity remain confounds. A same-binary original-path guard is therefore predeclared as E022, with no additional unchanged ON repetitions. The difference is provisional until that falsification and the phase diagnosis are complete.\n\nNo additional GPU bytes are allocated beyond safe E016. Exact per-profile slots/classes are retained inside each24GiB envelope. Source039ea29916d3155514688fb6d5a5de6129d69675; cleanbinary58aab77cd65222e9396d68b428591b44118172c1353a6e8e01f67b94ccfb649c. No deployment or normal launcher switch.\n''')
print(s['state'])
