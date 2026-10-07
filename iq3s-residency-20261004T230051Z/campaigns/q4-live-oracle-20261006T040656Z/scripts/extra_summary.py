"""Separate replay-overhead, independent-task and bounded-horizon evidence from headline matrix."""
from pathlib import Path
import json,statistics,hashlib
C=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def row(label):
 p=C/'raw'/label;r=load(p/'results.json')['runs'][0]
 ids=load(r['actual_output_ids_path']);fp=C/'phase-a'/f'{label}-fidelity.json'
 return {'label':label,'valid':r['state']=='VALID','input':r['actual_input_tokens'],'output':r['actual_output_tokens'],'PP':r['PP'],'decode_s':r['decode_s'],'equivalent_tok_s':r['actual_output_tokens']/r['decode_s'],'TTFT_s':r['TTFT_s'],'wall_s':r['wall_s'],'MTP_proposed':r['mtp_proposed'],'MTP_accepted':r['mtp_accepted'],'output_ids':ids,'fidelity':load(fp) if fp.exists() else None}
def compact(r):return {k:v for k,v in r.items() if k not in ['output_ids','fidelity']}
def generate(include_extra=True):
 natural=[row(f'overhead-v3-natural-attempt{n}') for n in [1,2,3]];replay=[row(f'overhead-v3-replay-attempt{n}') for n in [1,2,3]];original=row('original-natural-development-v3');capture=row('development-capture-v3');pairs=[]
 for a,b in zip(natural,replay):
  assert a['valid'] and b['valid'] and b['fidelity']['state']=='PASS'
  pairs.append({'natural':a['label'],'replay':b['label'],'same_output_ids':a['output_ids']==b['output_ids'],'same_MTP':(a['MTP_proposed'],a['MTP_accepted'])==(b['MTP_proposed'],b['MTP_accepted']),'decode_replay_over_natural':b['decode_s']/a['decode_s'],'wall_replay_over_natural':b['wall_s']/a['wall_s'],'attestation_s':b['fidelity']['initial_state']['setup_ms']/1000,'lookup_ms':b['fidelity']['lookup_ms']})
 overhead={'natural':[compact(x) for x in natural],'replay':[compact(x) for x in replay],'paired':pairs,'median_paired_decode_time_ratio':statistics.median(x['decode_replay_over_natural'] for x in pairs),'median_paired_wall_ratio':statistics.median(x['wall_replay_over_natural'] for x in pairs),'original_binary_output_matches_all_natural':all(original['output_ids']==x['output_ids'] for x in natural),'capture_output_matches_all_natural':all(capture['output_ids']==x['output_ids'] for x in natural),'original_binary_reference':compact(original),'recording':compact(capture),'caveat':'Short 256-output development workload only. Recording overhead separate; not primary 4096-tape decode.'}
 (C/'phase-a/overhead-v3-summary.json').write_text(json.dumps(overhead,indent=2)+'\n')
 if not include_extra:return overhead
 independent=[]
 for n in [1,2,3]:
  a=row(f'independent-code4-v3-current-attempt{n}');b=row(f'independent-code4-v3-oracle-attempt{n}');assert a['fidelity']['state']=='PASS' and b['fidelity']['state']=='PASS';assert a['fidelity']['initial_state']['SHA256']==b['fidelity']['initial_state']['SHA256'];assert a['fidelity']['tape']['work_sha256']==b['fidelity']['tape']['work_sha256'];independent.append({'attempt':n,'current':compact(a),'oracle':compact(b),'same_work':True,'same_initial_state':True,'same_output_ids':a['output_ids']==b['output_ids'],'throughput_oracle_over_current':a['decode_s']/b['decode_s'],'wall_oracle_over_current':b['wall_s']/a['wall_s']})
 out={'workload':'Independent substantive Python zipfile archive implementation task; separate source content from main repository benchmark','pairs':independent,'median_paired_throughput_ratio':statistics.median(x['throughput_oracle_over_current'] for x in independent),'median_paired_wall_ratio':statistics.median(x['wall_oracle_over_current'] for x in independent),'copy_check':'ON in all six arms, sampled D2H copied-byte checks charged to candidate; diagnostic/application confirmation, not clean 4096headline'}
 (C/'phase-c/independent-v3-summary.json').write_text(json.dumps(out,indent=2)+'\n')
 short=row('short64-v3-32k-attempt1');out={'run':compact(short),'fidelity':short['fidelity']['state'],'horizon':64,'unit':'future main-model routed-layer invocation, full T-by10 batch','same_input_and_work_as_primary_32K':short['fidelity']['tape']['work_sha256']==load(C/'phase-a/v3-current-32k-attempt1-fidelity.json')['tape']['work_sha256'],'information_restriction':'Both admission and victim future bounded; unknown beyond horizon uses causal heat','comparison_caveat':'One later scoped live confirmation; not fresh interleaved A/B with completed three-attempt primary matrix. Do not report statistically controlled short-horizon ranking.'}
 (C/'phase-c/short64-v3-summary.json').write_text(json.dumps(out,indent=2)+'\n');print('EXTRA_SUMMARIES_COMPLETE',flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--overhead-only',action='store_true');a=p.parse_args();generate(not a.overhead_only)
