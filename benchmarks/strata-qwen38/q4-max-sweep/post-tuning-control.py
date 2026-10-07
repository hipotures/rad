#!/usr/bin/env python3
"""Keep a measured default reference in selection; calibration is not presumed beneficial."""
import json
import run as r
import topology as t
import tuning

def main():
 done=r.ROOT/'raw/post-tuning-control-selection.json'
 if done.exists():return
 selected=json.loads((r.ROOT/'raw/tuned-selection.json').read_text());mtp=json.loads((r.ROOT/'raw/mtp-selection.json').read_text())
 # Calibrator uses short128-token prompts; local256-token confirmation underperformed default.
 # Compare the complete selected1024-token workload against the original default in one same-topology arm.
 label='MTP-default-baseline-confirm';cfg=t.clone(label,'adapt-adaptive')
 control=tuning.batch(label,cfg,63400,1024,3,True)
 chosen=next(x for x in mtp['results'] if x['candidate']==selected['best'])
 assert chosen.get('status')=='OK' and len(chosen['runs'])==3 and all(x['generated_tokens']==1024 for x in chosen['runs'])
 proof={'status':'OK' if control['status']=='OK' else 'DEFAULT_CONTROL_FAILED','default_control':control,'previous_selected':chosen,'comparison':'Same K22/default adaptive topology, actual~63400, same LONG_TASK, greedy1024tokens, warmup+3 measured requests in independently started engines; unique nonce/no prompt reuse. Only documented runtime settings differ.','short256_confirmation':json.loads((r.ROOT/'raw/tune-best-confirm-done.json').read_text()),'default256_reference':json.loads((r.ROOT/'raw/adapt-adaptive-done.json').read_text())}
 if control['status']=='OK' and (control['median_tg'],control['median_pp'])>(chosen['median_tg'],chosen['median_pp']):
  selected.update(best=label,selection_reason='Default won same1024-token three-run control; calibrated/local settings were measured but not automatically retained.')
 else:selected['selection_reason']='Tuned MTP candidate retained after same1024-token default control; failure is preserved if default control failed.'
 proof['chosen_for_KV']=selected['best'];r.c.save(r.ROOT/'raw/tuned-selection.json',selected);r.c.save(done,proof)
 print('POST TUNING CONTROL',control['status'],'default TG',control.get('median_tg'),'previous TG',chosen['median_tg'],'chosen',selected['best'],flush=True)
if __name__=='__main__':main()
