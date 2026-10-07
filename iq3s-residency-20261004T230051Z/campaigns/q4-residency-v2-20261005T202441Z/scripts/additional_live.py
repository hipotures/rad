"""Bounded held-out confirmation and matched diagnostic mechanism ablations."""
from campaign import C,load,save,V2Session,guard,status,point
import argparse,datetime

def declare():
    plan={'declared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'independent':{'payload':'hold-code','actual_input':72,'output':1024,'context_limit':32768,
            'variants':['control','history-v2','early-v1'],'replicates':3,'protocol':'Fresh server each attempt; identical4096-input/64-output warmup; rotate variant order per replicate. Entire task excluded from fit/calibration. Short-input application latency, not a128K-document confirmation.'},
        'ablations':{'profile':'32k','payload':'32k-run1','output':4096,'variants':['early-diagnostic','early-reactive-diagnostic'],
            'attempts_per_point':1,'purpose':'Same two-spare scheduler and CPU linear victim model; native prediction ON/OFF. Detailed ready/use/late/victim outcomes outside headline speed. No extra parameter tuning.'},
        'rules':'Never exceed3 attempts at an unchanged point. Retain EOS/failures. No reset after unfavorable results.'}
    path=C/'phase-c/additional-plan.json'
    if not path.exists():save(path,plan)

def independent():
    declare();variants=['control','history-v2','early-v1']
    for rep in [1,2,3]:
        for variant in variants[rep-1:]+variants[:rep-1]:
            guard();path=C/'independent'/variant/f'rep{rep}'
            if (path/'results.json').exists():continue
            assert not path.exists(),'Preserve and diagnose unfinished held-out attempt'
            cfg=load(C/'configs'/f'{variant}-32k.json')
            status('C_INDEPENDENT',phase='C',running={'variant':variant,'replicate':rep,'payload':'hold-code'},next_exact_action='Fixed warmup plus one1024-output held-out application request; no additional repeats')
            with V2Session(C,cfg,path,'32k',port=18136) as s:
                warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID'
                r=s.request('hold-code','run','independent-application')
                save(path/'results.json',{'runs':[r],'warmup':warm,'headline':False,'application_confirmation':True})
                assert r.get('actual_engine_input_verified') and r.get('reuse')==0
                # EOS is application behavior, retained and not rewritten for4096 throughput.
                assert r['state']!='FAILED',r

def diagnostics():
    declare()
    for variant in ['early-diagnostic','early-reactive-diagnostic']:
        guard();path=C/'diagnostics'/variant/'32k'
        if (path/'results.json').exists():continue
        assert not path.exists(),'Preserve and diagnose unfinished diagnostic'
        cfg=load(C/'configs/early-v1-32k.json');cfg['build_variant']=variant
        cfg['env']['STRATA_Q4_EARLY_DIAGNOSTIC']='1';cfg['env']['STRATA_Q4_EARLY_LOG']=str(path/'early-events')
        if 'reactive' in variant:cfg['env']['STRATA_Q4_EARLY_REACTIVE']='1'
        cfg['headline_instrumentation']='DIAGNOSTIC_ONLY: buffered events plus16 readbacks; never headlineTG'
        with V2Session(C,cfg,path,'32k',port=18136) as s:
            warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID'
            r=s.request('32k-run1','run','diagnostic')
            save(path/'results.json',{'runs':[r],'warmup':warm,'headline':False,'prediction_enabled':'reactive' not in variant,
                'causality':'Reactive issues after actual miss; publication at later target is never credited as prefetch of original demand.'})
            assert r.get('actual_engine_input_verified') and r.get('reuse')==0 and r['state']!='FAILED',r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['declare','independent','diagnostics']);a=p.parse_args()
    {'declare':declare,'independent':independent,'diagnostics':diagnostics}[a.action]()
