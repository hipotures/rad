"""Compare matched scoped events without extrapolating them into global TG."""
import csv
import numpy as np
from lab import ROOT,load,save
base=ROOT/'experiments/E021-device-plan-waits';attempt=base/'v1'
assert load(attempt/'collection.json')['state']=='PASS'
rows=[];host=[]
def distribution(a):
    a=np.asarray(a,dtype=float)
    return {'n':len(a),'median':float(np.median(a)),'p95':float(np.percentile(a,95)),
            'mean':float(a.mean())} if len(a) else None
for profile in ['32k','128k']:
    by_mode={}
    for mode in ['off','on']:
        folder=attempt/mode/profile;assert load(folder/'parity.json')['state']=='PASS'
        with (folder/'analysis-rows.csv').open() as f:
            by_mode[mode]={(int(r['window']),int(r['layer']),int(r['group']),int(r['phase'])):r for r in csv.DictReader(f)}
    assert by_mode['off'].keys()==by_mode['on'].keys()
    for layer in [2,24,40]:
        for phase in range(5):
            for category in ['all-local','CPU','mapped']:
                pairs=[];hostpairs=[]
                for key,r in by_mode['off'].items():
                    if key[1]!=layer or key[3]!=phase:continue
                    cpu,mapped,remote=map(int,[r['CPU'],r['mapped'],r['remote']])
                    include=(cpu+mapped+remote==0 if category=='all-local' else cpu>0 if category=='CPU' else mapped>0)
                    if not include:continue
                    q=by_mode['on'][key]
                    assert [r[x] for x in ['CPU','mapped','local','remote','T','tokens']]==[q[x] for x in ['CPU','mapped','local','remote','T','tokens']]
                    pairs.append((float(r['gpu_us']),float(q['gpu_us'])))
                    if phase==0:hostpairs.append((float(r['host_dispatch_us']),float(q['host_dispatch_us'])))
                if pairs:
                    off,on=np.asarray(pairs).T
                    rows.append({'profile':profile,'layer':layer,'phase':phase,'category':category,
                        'OFF':distribution(off),'ON':distribution(on),'paired_ON_minus_OFF_us':distribution(on-off)})
                if hostpairs:
                    off,on=np.asarray(hostpairs).T
                    host.append({'profile':profile,'layer':layer,'category':category,
                        'OFF':distribution(off),'ON':distribution(on),'paired_ON_minus_OFF_us':distribution(on-off)})
save(base/'summary.json',{'state':'COMPLETE_SCOPED_DIAGNOSTIC','same_binary':True,
    'full_parity':'PASS actual output/router/MTP/path/cache/heat/first-head bits at both profiles',
    'GPU_phases':rows,'host_dispatch':host,
    'limitations':['Only layers2/24/40; never multiply by48 or sum overlapping timers into TG.',
      'Events add diagnostic overhead; separate serial OFF/ON runs, not a randomized hardware trial.',
      'GPU resident/doorbell phase is separate from host plan wait; host and GPU clocks cannot be subtracted.',
      'The final copy/row-scatter is source-supported but outside these five scoped timers. E023 tests it directly.']})
flat=[]
for r in rows:
    flat.append({k:v for k,v in r.items() if k not in ['OFF','ON','paired_ON_minus_OFF_us']}|
                {'n':r['OFF']['n'],'OFF_median_us':r['OFF']['median'],'ON_median_us':r['ON']['median'],
                 'paired_delta_median_us':r['paired_ON_minus_OFF_us']['median']})
with (base/'summary.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
text='# E021: same-binary scoped coordination waits\n\n'
text+='All recorded outputs, router decisions, MTP, paths, resident sets, heat and first-head bits match. This is diagnostic timing only.\n\n'
text+='| Profile | Layer | Phase | Category | N | OFF median us | ON median us | Paired delta us |\n|---|---:|---:|---|---:|---:|---:|---:|\n'
for r in flat:
    text+=f'| {r["profile"]} | {r["layer"]} | {r["phase"]} | {r["category"]} | {r["n"]} | {r["OFF_median_us"]:.3f} | {r["ON_median_us"]:.3f} | {r["paired_delta_median_us"]:.3f} |\n'
text+='\nPhase0: plan wait and copy;1: resident expert compute;2: mapped wait/compute;3: CPU completion wait;4: device planning and demand doorbell. Host dispatch distributions are preserved separately in summary.json. CPU-zero is not always all-local; mapped work is explicitly separate.\n\n'
text+='These selected-layer phases do not establish total exposed request cost. Kernel/event floors, cross-stream overlap and VM variation remain. No multiplication by48 or sum of medians is a measured speedup. The next source-supported experiment removes the final redundant GPU row-zero/copy/add operations with exact CPU/GPU row ownership; those operations were not included in these five phases.\n'
(base/'report.md').write_text(text)
print('Completed',len(rows),'GPU strata and',len(host),'host strata')
