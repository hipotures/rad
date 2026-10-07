"""Retrospective read-only compatibility check; never infer a cause from timings."""
from campaign import C, R, load, save
import statistics


def main():
    prior=R/'campaigns/q4-pool-spin-20261005T184831Z'
    rows=[]
    counter_keys=['mtp_proposed','mtp_accepted','verify_windows','local_vram_entries',
                  'cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries']
    for profile in ['32k','128k']:
        for rep in [1,2,3]:
            old=prior/'raw/100us'/profile/f'rep{rep}'
            new=C/'raw/control'/profile/f'rep{rep}'
            a=load(old/'raw/measured.json');b=load(new/'raw/run.json')
            ac=load(old/'config.json');bc=load(new/'config.json')
            aw=load(old/'raw/warmup.json');bw=load(new/'raw/warmup.json')
            ar=load(old/'raw/resource-check.json');br=load(new/'raw/resource-check.json')
            rows.append({'profile':profile,'replicate':rep,'prior_raw':str(old/'raw/measured.json'),'current_raw':str(new/'raw/run.json'),
                'same_input':a['actual_engine_input']==b['actual_engine_input'],
                'same_output':a['actual_output_ids_sha256']==b['actual_output_ids_sha256'],
                'counter_equal':{key:a.get(key)==b.get(key) for key in counter_keys},
                'warmup_equal':{key:aw.get(key)==bw.get(key) for key in ['actual_engine_input','actual_output_ids_sha256','actual_input_tokens','actual_output_tokens']},
                'config_equal':{key:ac.get(key)==bc.get(key) for key in ['exe','args','layer_split','gpu','env','max_total_context','binary_sha256','source_sha','model_revision','tokenizer']},
                'capacity_equal':{key:ar.get(key)==br.get(key) for key in ['primary_slots','helper_or_stage1_slots','cache_MiB_primary','cache_MiB_total']},
                'prior':{key:a.get(key) for key in ['PP','TG','TTFT_s','wall_s']},
                'current':{key:b.get(key) for key in ['PP','TG','TTFT_s','wall_s']}})
    summaries=[]
    for profile in ['32k','128k']:
        selected=[row for row in rows if row['profile']==profile]
        summaries.append({'profile':profile,'prior_medians':{key:statistics.median(row['prior'][key] for row in selected) for key in ['PP','TG','TTFT_s','wall_s']},
            'current_medians':{key:statistics.median(row['current'][key] for row in selected) for key in ['PP','TG','TTFT_s','wall_s']}})
    save(C/'analysis/historical-control-compatibility.json',{'pairs':rows,'summaries':summaries,
        'timing_cause':'Unassigned. Same fresh-process/fixed64 warmup protocol; compare exact outputs, counters and effective fields rather than asserting an exclusive cache-warmup or environment cause.',
        'control_recollection':'Contemporaneous controls were interleaved with the new live candidates for controlled Phase C ratios, not an additional spin sweep. Previous compatible256K controlrep1 was retained; no fourth primary attempt.',
        'prior_campaign_role':'Historical compatibility/sensitivity only; never a residency speedup control.'})
    print('HISTORICAL_COMPATIBILITY',[(r['profile'],r['replicate'],r['same_input'],r['same_output'],all(r['counter_equal'].values())) for r in rows],flush=True)


if __name__=='__main__':
    main()
