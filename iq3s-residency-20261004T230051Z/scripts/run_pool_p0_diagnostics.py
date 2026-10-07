"""After clean P0, trace each profile's CPU-heaviest workload without headline instrumentation."""
import hashlib, json, statistics, subprocess
import numpy as np
from lab import ROOT, Session, load, save
from trace_reader import Trace
base=ROOT/'experiments/E026-pool-generalization';summary=load(base/'summary.json')
assert summary['state']=='COMPLETE_MEASUREMENTS'
selection={}
for profile in ['32k','128k']:
    choices=[c for c in summary['cells'] if c['profile']==profile and c['role']=='default']
    def cpu_rate(c):
        runs=[load(p) for p in c['raw_paths']]
        values=[r['cpu_fallback_entries']/r['actual_output_tokens'] for r in runs if r.get('actual_output_tokens') and r.get('cpu_fallback_entries') is not None]
        return statistics.median(values) if values else -1
    selection[profile]=max(choices,key=cpu_rate)['family']
save(base/'diagnostic-v1/selection.json',{'selection':selection,'rule':'Largest median clean CPU fallback entries/actual generated token/profile, including preserved natural EOS when counters exist; selection made after clean matrix, before wait diagnostics','headline':False})
for role in ['default','sleep100us']:
    name='pool-p0-diag-'+role;source=ROOT/'variants'/('diagnostic-coordination-off-v1' if role=='default' else 'diagnostic-pool-wait-v1')
    target=ROOT/'variants'/name;target.mkdir()
    for profile in ['32k','128k']:
        cfg=load(source/f'{profile}.json');cfg['build_variant']=name;cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py')
        save(target/f'{profile}.json',cfg)
    (target/'README.md').write_text('# P0 selected-layer CPU completion wait diagnostics\n\nSame existing E021 event binary. No headline speed claims.\n')
    for profile in ['32k','128k']:
        family=selection[profile];path=base/'diagnostic-v1'/profile/role
        assert not path.exists();save(path/'protocol.json',{'family':family,'role':role,'profile':profile,'headline':False,'selected_layers':[2,24,40],'warmup_output':64,'output_budget':4096})
        with Session(name,profile,path) as s:
            assert s.request('warmup','warmup','warmup',base/'workloads/manifest.json')['state']=='VALID'
            r=s.request(f'{family}-{profile}-run1','trace-run1','diagnostic',base/'workloads/manifest.json')
            save(path/'results.json',{'run':r,'headline':False})
        print('DIAGNOSTIC',role,profile,family,flush=True)
SPAN=np.dtype([(x,'<u8') for x in ['window','observed_ns']]+[(x,'<i4') for x in ['device','layer','group','phase','tokens','token_base']]+[('gpu_ms','<f4'),('reserved','<i4')])
def dist(a):
    a=np.asarray(a,float)
    return {'n':len(a),'median':float(np.median(a)),'p95':float(np.percentile(a,95)),'max':float(a.max())} if len(a) else None
rows=[];parities=[]
for profile in ['32k','128k']:
    traces={}
    for role in ['default','sleep100us']:
        path=base/'diagnostic-v1'/profile/role;prefix=path/'traces/runtime-request2';t=Trace(prefix);validation=t.validate();save(path/'validation.json',validation);assert validation['state']=='PASS',validation
        traces[role]=t;groups={};windows={int(w['number']):w for w in t.windows}
        for l,e in t.grouped():
            layer=int(l['layer'])
            if layer not in [2,24,40]:continue
            w=int(l['window']);T=int(windows[w]['T']);start=int(e['token'].min());group=0 if start==0 else 1
            groups[(w,layer,group)]={'CPU':int(np.count_nonzero(e['path']==-1)),'mapped':int(np.count_nonzero(e['path']==1)),'local':int(np.count_nonzero(e['path']==0)),'remote':int(np.count_nonzero(e['path']==2))}
        spans=np.fromfile(str(prefix)+'-miss-spans.bin',SPAN);assert np.isfinite(spans['gpu_ms']).all()
        for layer in [2,24,40]:
            for category in ['all-local','CPU-positive']:
                a=[]
                for span in spans:
                    if int(span['phase'])!=3 or int(span['layer'])!=layer:continue
                    g=groups[(int(span['window']),layer,int(span['group']))]
                    if (g['CPU']>0 if category=='CPU-positive' else g['CPU']+g['mapped']+g['remote']==0):a.append(float(span['gpu_ms'])*1000)
                rows.append({'profile':profile,'family':selection[profile],'role':role,'layer':layer,'category':category,'completion_wait_us':dist(a)})
    b,c=traces['default'],traces['sleep100us']
    parities.append({'profile':profile,'same_output_IDs':bool(np.array_equal(b.output_ids,c.output_ids)),'same_router_IDs':bool(np.array_equal(b.entries['expert'],c.entries['expert'])),'same_paths':bool(np.array_equal(b.entries['path'],c.entries['path'])),'same_MTP':bool(np.array_equal(b.windows['T'],c.windows['T']) and np.array_equal(b.windows['accepted'],c.windows['accepted']))})
save(base/'diagnostic-v1/summary.json',{'state':'COMPLETE_DIAGNOSTIC','selection':selection,'waits':rows,'parity':parities,'limits':['Three selected layers only; cannot extrapolate/sum48layers.','GPU event nodes and full buffered traces change timing; all diagnosticTGexcluded.','Phase3 includes event/doorbell floor. Distinct demand/category frequencies retained, not assumed paired.']})
for row in rows:print(row,flush=True)
