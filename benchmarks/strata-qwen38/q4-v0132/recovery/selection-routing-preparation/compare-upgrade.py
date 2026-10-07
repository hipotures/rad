from final_identity import final_label
"""Separate controlled upgrade results from best-config before/after comparisons."""
from pathlib import Path
import json,statistics,csv,time
R=Path(__file__).resolve().parent;B=R.parent
def load(p):return json.loads(Path(p).read_text())
def med(rows,key):return statistics.median(x[key] for x in rows)
rows=[]
def add(metric,old,new,classification,oldcfg,newcfg,evidence,note):
    rows.append({'metric':metric,'v0131':old,'v0132':new,'delta_percent':100*(new/old-1) if old and new is not None else None,'classification':classification,'v0131_config':oldcfg,'v0132_config':newcfg,'evidence':evidence,'note':note})

if __name__=='__main__':
    for marker in ['phase-final-matrix-terminal.json','phase-compaction-terminal.json','phase-compaction-old-control-terminal.json']:
        assert load(R/'raw'/marker)['status']=='COMPLETE'
    old=load(B/'results/q4-single-gpu/summary.json');new=[load(R/'raw'/f'BASELINE-resident-v0132-run{i}.json') for i in range(1,4)]
    assert len(old['speed_runs'])==3 and all(x['generated_tokens']==256 and x['cache_reused_tokens']==0 for x in old['speed_runs'])
    for key,metric in [('pp_tps','Q4 single GPU resident64K PP'),('tg_tps','Q4 single GPU resident64K TG')]:
        add(metric,med(old['speed_runs'],key),med(new,key),'NOT_CONTROLLED_A_B',old['config'],str(R/'configs/BASELINE-resident-v0132.json'),[str(B/'results/q4-single-gpu/summary.json'),*[str(R/'raw'/f'BASELINE-resident-v0132-run{i}.json') for i in range(1,4)]],'Three actual outputs256 each. Oldactual63300/new63400; unique unpaired prompts, independent pack paths and naturally different allocations; no attribution to runtime alone.')
    for target in [63400,127000,259500]:
        before=[load(B/'q4-max-sweep/raw'/f'FINAL-A-{target}-run{i}.json') for i in range(1,4)]
        after=[load(R/'raw'/f'{final_label()}-ctx{target}-run{i}.json') for i in range(1,4)]
        for key,metric in [('pp_tps','PP'),('tg_tps','TG')]:
            add(f'Q4 best2GPU actual{target} {metric}',med(before,key),med(after,key),'NOT_CONTROLLED_A_B',str(B/'q4-max-sweep/configs/FINAL-A.json'),str(R/'configs/FINAL-v0132-Q4.json'),[str(B/'q4-max-sweep/raw'/f'FINAL-A-{target}-run{i}.json') for i in range(1,4)]+[str(R/'raw'/f'{final_label()}-ctx{target}-run{i}.json') for i in range(1,4)],'Best-config before/after, not runtime-only A/B; final attempt2 adds an explicit offline/no-tools system instruction, so prompts are not controlled pairs. Layer split/KV/prefill/CPU/PCIe/MTP may differ; consult both full configurations.')
    for item in load(R/'comparison-pp-control.json')['rows']:
        for key,metric in [('pp_tps','PP'),('tg_tps','TG')]:
            add(f'Controlled sameK24 actual{item["target"]} {metric}',item[key]['v0131'],item[key]['v0132'],'CONTROLLED_WHOLE_VERSION_A_B',str(R/'controls/v0131/configs/PP-CONTROL.json'),str(R/'controls/v0132/configs/PP-CONTROL.json'),[str(R/'comparison-pp-control.json')],'Pair-identical APIpayloads, same CLI settings and byte-identical dense/MTP/profile; natural allocator differences belong to runtime. Not isolated prompt-fix patch causality.')
    for topology,oldpath,newpath in [('single-resident',B/'q4-max-sweep/raw/T0-control-startup.json',R/'raw/BASELINE-resident-v0132-startup.json'),('best2GPU',B/'q4-max-sweep/raw/FINAL-A-startup.json',R/'raw'/f'{final_label()}-startup.json')]:
        before=load(oldpath);after=load(newpath)
        add('Cold start processREADY '+topology,before['cold_start_s'],after['cold_start_s'],'NOT_CONTROLLED_A_B',str(oldpath),str(newpath),[str(oldpath),str(newpath)],'Fresh process exec to healthREADY; physical filesystem cold cache not controlled, no drop_caches. Best split/config may differ. Timing excludes PSS snapshots.')
    for target in [127000,250000]:
        oldpath=R/'controls/v0131-compaction/raw'/f'COMPACTION-v0131-control-{target}.json';newpath=R/'raw'/f'COMPACTION-FINAL-v0132-{target}.json';before=load(oldpath);after=load(newpath)
        assert load(oldpath.with_name(oldpath.stem+'-request.json'))==load(newpath.with_name(newpath.stem+'-request.json'))
        for key,metric in [('total_wall_s','wall s'),('pp_tps','PP'),('tg_tps','TG'),('ttft_s','TTFT s')]:
            add(f'Compaction actual{target} {metric}',before[key],after[key],'NOT_CONTROLLED_A_B',before['config'],after['config'],[str(oldpath),str(newpath)],'Exact identical saved transcript/request, <=4096 output cap; natural output lengths may differ. Immutableoldruntime comparison stored only in new namespace, oldcampaign staysfrozen. Best configurations differ.')
    for row in rows:
        for cfg in [row['v0131_config'],row['v0132_config']]:assert Path(cfg).exists(),'Incorrect comparison config path '+cfg
    (R/'comparison-upgrade.json').write_text(json.dumps({'status':'COMPLETE_REQUIRES_REPORT_REVIEW','created':time.time(),'rows':rows,'scope':'Controlled upgrade pair rows are separate from best-config before/after; no inference that tuning gains are solely a runtime upgrade.'},indent=2))
    with (R/'comparison-upgrade.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]));writer.writeheader()
        for row in rows:writer.writerow({k:json.dumps(v) if isinstance(v,list) else v for k,v in row.items()})
    lines=['# v0.1.31 → v0.1.32 comparisons','','Controlled version rows use paired payloads. Best-config rows are explicitly NOT_CONTROLLED_A_B; full configurations and raw evidence are in JSON/CSV.','','| Metric | v0.1.31 | v0.1.32 | Delta % | Classification |','|---|---:|---:|---:|---|']
    for row in rows:lines.append(f'| {row["metric"]} | {row["v0131"]:.3f} | {row["v0132"]:.3f} | {row["delta_percent"]:+.2f} | {row["classification"]} |')
    (R/'comparison-upgrade.md').write_text('\n'.join(lines)+'\n');print(len(rows),'comparison metrics assembled.')
