"""After headlines only: same history policy plus existing buffered transaction trace."""
from campaign import C,R,load,save,V2Session,guard
from trace_reader import Trace
from observed_admissions import analyze as admissions
from pathlib import Path
import hashlib,json,subprocess,time

def main():
    guard();assert load(C/'phase-c/matrix-exit.json')['exit_code']==0,'No builds/profiling while primary matrix active'
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    py=str(R/'src/control/.venv/bin/python');base=load(C/'git/builds/cost-router-v1/identity.json')
    identity=C/'git/builds/history-diagnostic/identity.json'
    if not identity.exists():
        with (C/'logs/history-diagnostic-build.log').open('x') as log:
            result=subprocess.run([py,str(C/'scripts/build.py'),'history-diagnostic','--base-source',base['source'],'--base-head',base['source_sha'],'--patch','patch_history.py'],cwd=C,stdout=log,stderr=subprocess.STDOUT,timeout=2400)
        assert result.returncode==0,'Preserve diagnostic integration failure; do not substitute another policy'
    ident=load(identity);path=C/'diagnostics/history-diagnostic/32k'
    if (path/'results.json').exists():return
    assert not path.exists(),'Preserve and explicitly repair unfinished diagnostic attempt'
    cfg=load(C/'configs/history-v2-32k.json');cfg.update(exe=ident['exe'],cwd=ident['source'],Strata_HEAD=ident['source_sha'],source_sha=ident['source_sha'],binary_sha256=ident['binary_sha256'],build_variant='history-diagnostic',headline_instrumentation='DIAGNOSTIC_ONLY: exact same history selector plus existing buffered demand/admission trace')
    cfg['env']['STRATA_LAB_TRACE']=str(path/'trace')
    with V2Session(C,cfg,path,'32k',port=18136) as session:
        warm=session.request('warmup','warmup','warmup');assert warm['state']=='VALID'
        r=session.request('32k-run1','run','diagnostic')
        assert r.get('actual_engine_input_verified') and r.get('reuse')==0 and r['state']!='FAILED',r
        prefix=str(path/'trace-request2')
        save(path/'results.json',{'runs':[r],'warmup':warm,'headline':False,'trace_prefix':prefix,
            'algorithm':'Same frozen history-v2 header and patch; only prior buffered trace/cost hooks added. No score/threshold changes.'})
    trace=Trace(prefix);validation=trace.validate();save(path/'trace-validation.json',validation)
    assert validation['state']=='PASS',validation
    result=admissions(trace);save(path/'observed-admissions.json',result)
    # These demand/path counts describe this diagnostic's actual trajectory,
    # not a fabricated fixed-trajectory speed comparison to the clean binary.
    per_layer=[]
    for layer in range(48):
        count=0;paths={str(value):0 for value in [-1,0,1,2]}
        for meta,entries in trace.grouped():
            if int(meta['layer'])!=layer:continue
            count+=len(entries)
            for value in [-1,0,1,2]:paths[str(value)]+=int((entries['path']==value).sum())
        per_layer.append({'layer':layer,'entry_count':count,'path_counts':paths,'native_blob_bytes':int(trace.blob_bytes[layer])})
    save(path/'per-layer-routing.json',per_layer)
    saved=load(C/'raw/history-v2/32k/rep1/raw/run.json')
    parity={'same_input':r['actual_engine_input']==saved['actual_engine_input'],
        'same_output':r['actual_output_ids_sha256']==saved['actual_output_ids_sha256'],
        'counters_equal':{key:r.get(key)==saved.get(key) for key in ['mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries']},
        'limitation':'Diagnostic timings excluded even if IDs/counters match; transaction costs/victim absence are not exclusive request latency.'}
    save(path/'clean-parity.json',parity)
    patch=subprocess.check_output(['git','diff','6f32ec070f23ced9f50e704d854d775da52591ab',ident['source_sha'],'--binary'],cwd=ident['source'])
    (C/'git/patches/history-diagnostic.diff').write_bytes(patch)
    save(C/'phase-c/history-transactions.json',{'identity':ident,'parity':parity,
        'summary':{key:value for key,value in result.items() if key not in ['rows','window_block_working_set']},'raw':str(path/'raw/run.json'),'transaction_rows':str(path/'observed-admissions.json'),
        'limitations':result['limitations']+['Observed incoming publication is at safe end-of-window; it cannot prefetch the earlier original current-window miss. Predictions are history-based, not native early router.']})
    print('HISTORY_TRANSACTION_DIAGNOSTIC_COMPLETE',result['promotions'],result['bytes'],flush=True)

if __name__=='__main__':main()
