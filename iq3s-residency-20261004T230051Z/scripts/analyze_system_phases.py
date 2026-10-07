"""Derive per-request PP/decode system telemetry at its actual one-Hz resolution."""
import json, statistics
from lab import ROOT,load,save
summary=load(ROOT/'summary.json');rows=[]
def stats(values):
    v=[x for x in values if x is not None]
    return {'min':min(v),'mean':statistics.mean(v),'median':statistics.median(v),'max':max(v)} if v else None
for cell in summary['measured_cells']:
    for raw in cell['raw_paths']:
        r=load(raw)
        if r['state']!='VALID':continue
        start=r['started_epoch'];first=start+r['TTFT_s'];end=start+r['wall_s']
        samples=[json.loads(line) for line in open(r['telemetry']['path'])]
        phases={}
        for phase,lo,hi in [('prefill',start,first),('decode',first,end)]:
            s=[x for x in samples if lo<=x['wall_time']<hi]
            q={'samples':len(s),'system_CPU_pct':stats([x.get('system_cpu_pct') for x in s]),
               'process_CPU_pct_one_core_100':stats([sum(p['cpu_pct'] for p in x['processes']) for x in s if x.get('processes')]),
               'sum_process_RSS_GiB':stats([sum(p['rss_gib'] for p in x['processes']) for x in s if x.get('processes')]),
               'RAM_used_GiB':stats([x.get('ram_used_gib') for x in s]),
               'MemAvailable_GiB':stats([x.get('mem_available_gib') for x in s]),'GPUs':{}}
            for device in (0,1):
                g=[g for x in s for g in x.get('gpus',[]) if g['index']==device]
                q['GPUs'][str(device)]={field:stats([x.get(field) for x in g]) for field in ['util_pct','power_w','vram_mib','sm_mhz']}
            # Process read_bytes are physical process counters, never an expert logical-read substitute.
            io=[]
            for x in s:
                if x.get('processes'):io.append(sum(p['read_bytes'] for p in x['processes']))
            q['physical_process_read_bytes_observed_delta']=max(io)-min(io) if len(io)>1 else None
            phases[phase]=q
        rows.append({'experiment':cell['experiment'],'name':cell['name'],'profile':cell['profile'],
                     'raw':raw,'phases':phases,'logical_expert_file_reads':'UNAVAILABLE'})
save(ROOT/'analysis/system-phases/summary.json',{'state':'COMPLETE_DERIVED_TELEMETRY','rows':rows,
    'limits':['One-Hz samples with subprocess/query time; phase boundaries are client TTFT/end, not exact GPU kernels.',
      'First process CPU sample is an unprimed psutil value. System CPU uses the VM-wide 0–100% scale; process sum uses one core=100%.',
      'RSS sum can count shared mappings more than once. MemAvailable measures system memory pressure.',
      'Read-byte delta misses phase-edge traffic and process lifetime changes; it is not logical expert or PLE traffic.',
      'PCIe dmon samples remain separate, cannot identify per-token burst causes.']})
print('Derived system phases for',len(rows),'requests')
