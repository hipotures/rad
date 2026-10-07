"""One declared candidate-OFF guard; not another production-control repetition."""
from campaign import C,load,save,guard,Session,status
from pathlib import Path
import os,psutil,signal

def main():
 guard();assert load(C/'phase-c/matrix-progress.json')['completed']==18
 save(C/'logs/off-speed-guard-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'timeout_s':600})
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned guard timeout')))
 cfg=load(C/'configs/conditional-off-32k.json');cfg['variant_overrides'].update(charged_resident_capacity_reduction_per_device=0,scope='OFF performance guard, no early workers/reservations/scorer; metadata clarified only')
 path=C/'diagnostics/conditional-off-clean/32k';assert not path.exists(),'Preserve completed/incomplete guard; no retries'
 status('OFF_PERFORMANCE_GUARD',phase='C',running='one fresh32K4096 candidate-OFF point',next_exact_action='Compare exact IDs/MTP/routing/capacity and timing to preserved primary control, then diagnostics')
 with Session(C,cfg,path,'32k',port=18144) as s:
  warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64
  r=s.request('32k-run1','run','diagnostic');assert r['state']=='VALID' and r['actual_output_tokens']==4096
  save(path/'results.json',{'warmup':warm,'runs':[r],'headline':False,'purpose':'One candidate-OFF source/code-generation guard; not a fourth repetition of primary control'})
 a=load(C/'raw/control/32k/rep1/results.json')['runs'][0];keys=['actual_input_tokens','actual_output_ids_sha256','mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries'];parity={k:a[k]==r[k] for k in keys};parity['actual_engine_input']=a['actual_engine_input']==r['actual_engine_input'];a_cap=load(C/'raw/control/32k/rep1/raw/resource-check.json');b_cap=load(path/'raw/resource-check.json');parity['capacities']=all(a_cap[k]==b_cap[k] for k in ['primary_slots','helper_or_stage1_slots'])
 out={'raw_result':str(path/'results.json'),'parity':parity,'PASS_parity':all(parity.values()),'control_reference_TG':a['TG'],'candidate_OFF_TG':r['TG'],'candidate_OFF_PP':r['PP'],'TG_ratio_vs_earlier_primary_rep1':r['TG']/a['TG'],'wall_ratio_vs_earlier_primary_rep1':r['wall_s']/a['wall_s'],'timing_caveat':'Single later-time guard, not contemporaneous replicated A/B. Cannot attribute a timing difference solely to source/compiler or solely to gating. No baseline repetition or parameter change.'}
 save(C/'analysis/off-speed-guard.json',out);print('OFF_GUARD',out,flush=True)
if __name__=='__main__':main()
