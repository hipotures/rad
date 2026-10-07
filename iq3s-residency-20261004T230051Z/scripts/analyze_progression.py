"""Derive bracketed 1-Hz client-wall decode progression without inventing per-token timing."""
import csv
import json
import statistics
from lab import ROOT, load, save
summary=load(ROOT/'summary.json')
out=ROOT/'analysis/decode-progression'
out.mkdir(exist_ok=True)
records=[]
for cell in summary['measured_cells']:
    for path in cell['raw_paths']:
        r=load(path)
        if r['state']!='VALID':continue
        samples=[json.loads(x) for x in open(r['telemetry']['path'])]
        end=r['started_epoch']+r['wall_s']
        start=r['started_epoch']+r['TTFT_s']
        points=[(0,start)]
        for sample in samples:
            n=((sample.get('metrics') or {}).get('live') or {}).get('generated')
            stamp=sample['wall_time']
            if n is not None and start<=stamp<=end and points[-1][0]<n<=r['actual_output_tokens']:
                points.append((n,stamp))
        if points[-1][0]<r['actual_output_tokens']:
            points.append((r['actual_output_tokens'],end))
        bounds={0:{'estimate':start,'lower':start,'upper':start},4096:{'estimate':end,'lower':end,'upper':end}}
        for n in [512,1024,2048]:
            for (n0,t0),(n1,t1) in zip(points,points[1:]):
                if n0<=n<=n1:
                    bounds[n]={'estimate':t0+(t1-t0)*(n-n0)/(n1-n0),'lower':t0,'upper':t1}
                    break
        intervals=[]
        for lo,hi in [(0,512),(512,1024),(1024,2048),(2048,4096)]:
            if lo not in bounds or hi not in bounds:continue
            b,e=bounds[lo],bounds[hi]
            elapsed=e['estimate']-b['estimate'];slow=e['upper']-b['lower'];fast=e['lower']-b['upper']
            intervals.append({'start':lo,'end':hi,'TG_estimate':(hi-lo)/elapsed if elapsed>0 else None,
                'TG_lower_bound':(hi-lo)/slow if slow>0 else None,'TG_upper_bound':(hi-lo)/fast if fast>0 else None,
                'cumulative_TG_estimate':hi/(e['estimate']-start) if e['estimate']>start else None,
                'max_boundary_bracket_s':max(b['upper']-b['lower'],e['upper']-e['lower'])})
        records.append({'experiment':cell['experiment'],'name':cell['name'],'profile':cell['profile'],
            'raw':path,'basis':'API live.generated integer counts at1Hz; linear interpolation bracketed by actual samples. First-content anchor and end-of-response include frontend buffering; these are client-wall rates, not exact engine timings.',
            'points':points,'bounds':bounds,'intervals':intervals,'final_engine_TG':r['TG'],
            'interval_cache_or_MTP':'UNAVAILABLE in clean binary; separate diagnostic traces retain actual counts.'})
rows=[]
for cell in summary['measured_cells']:
    rs=[r for r in records if (r['experiment'],r['profile'])==(cell['experiment'],cell['profile'])]
    row={'name':cell['name'],'profile':cell['profile'],'raw_runs':len(rs),'engine_TG_median':cell['statistics']['TG']['median']}
    for i,label in enumerate(['0-512','512-1K','1K-2K','2K-4K']):
        values=[r['intervals'][i]['TG_estimate'] for r in rs if len(r['intervals'])>i and r['intervals'][i]['TG_estimate'] is not None]
        row[label]=statistics.median(values) if values else None
        uncertainty=[r['intervals'][i]['max_boundary_bracket_s'] for r in rs if len(r['intervals'])>i]
        row[label+'-max-bracket-s']=max(uncertainty) if uncertainty else None
    rows.append(row)
save(out/'summary.json',{'state':'COMPLETE_APPROXIMATE','rows':rows,'runs':records,
    'limits':'Do not infer exact per-token or causal cache/MTP acceleration from1Hz counts. Full brackets retained. No extra requests or instrumentation.'})
with (out/'summary.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print([(r['name'],r['profile'],r['0-512'],r['2K-4K']) for r in rows])
