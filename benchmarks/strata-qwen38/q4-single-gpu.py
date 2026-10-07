#!/usr/bin/env python3
"""Small Q4 test: one smoke, 3 requests at 64K, exact saved IQ3 quality inputs."""
import csv
import json
import os
from pathlib import Path
import re
import signal
import statistics
import subprocess
import time
import uuid
import campaign as c

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/q4-single-gpu'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'raw').mkdir(exist_ok=True)
(OUT/'telemetry').mkdir(exist_ok=True)
c.BASE=OUT
c.RESULTS=OUT
c.URL='http://127.0.0.1:18082'
LABEL='UD-Q4_K_XL-1GPU'
QUALITY=BASE/'results/quality/UD-Q4_K_XL'
KEYS=['A-coding-debug','B-mathematical-reasoning','C-repository-architecture']

def summarize(rows,smoke,startup,error=None):
    samples=[json.loads(line) for p in (OUT/'telemetry').glob('*.jsonl') for line in p.read_text().splitlines()]
    engine_log=(OUT/'smoke.log').read_text() if (OUT/'smoke.log').exists() else ''
    resident=re.findall(r'cache complement ready: resident ([\d.]+) GiB, pinned ([\d.]+) GiB',engine_log)
    residency=resident[-1] if resident else None
    summary={'model':'Unsloth UD-Q4_K_XL','revision':'38bb39ee97821de2c9009abb7e93950eec396e66',
        'strata_head':(BASE/'STRATA_HEAD').read_text().strip(),'config':str(OUT/'config.json'),
        'resident_budget_gib':budget,'mem_available_before_start_gib':available,
        'load_ok':bool(startup),'smoke_ok':bool(smoke),'startup':startup,
        'resident_expert_gib':float(residency[0]) if residency else None,
        'pinned_expert_gib':float(residency[1]) if residency else None,
        'residency_note':'Upstream RAM budget stores GPU-cache complement, not a duplicate of every GPU-cached expert. Read logs and tier counters to distinguish full RAM from RAM+VRAM coverage.',
        'speed_runs':rows,'speed_median':{},'quality_files':{},'problem':error,
        'peak_ram_used_gib':max((s['ram_used_gib'] for s in samples),default=None),
        'peak_rss_gib':max((sum(p['rss_gib'] for p in s['processes']) for s in samples),default=None),
        'peak_vram_gib':max((g['vram_gib'] for s in samples for g in s.get('gpus',[]) if g['index']==0),default=None),
        'gpu1_peak_vram_gib':max((g['vram_gib'] for s in samples for g in s.get('gpus',[]) if g['index']==1),default=None),
        'min_mem_available_gib':min((s['mem_available_gib'] for s in samples),default=None),
        'storage_note':'/srv/ai is virtiofs; file_blobs/file_mb are logical routed-expert file reads, not physical host SSD counters.'}
    if len(rows)==3:
        for key in ['actual_prompt_tokens','generated_tokens','pp_tps','prompt_processing_wall_s','ttft_s','tg_tps','decode_wall_s','peak_ram_used_gib','peak_rss_gib','peak_vram0_gib']:
            summary['speed_median'][key]=statistics.median(r[key] for r in rows)
        summary['decode_expert_file_reads']=[r['expert_tiers'] for r in rows]
        summary['decode_expert_file_mb_total']=sum(r['expert_tiers'].get('file_mb',0) or 0 for r in rows)
    for key in KEYS:
        path=QUALITY/(key+'.txt')
        if path.exists():summary['quality_files'][key]=str(path)
    c.save(OUT/'summary.json',summary)
    lines=['# Q4 single GPU — small sanity test',
        'CUDA_VISIBLE_DEVICES=0, GPU0 only; 65536 context, INT8 KV, spec4/min-p0.5, vision off, no speed projection. Existing pinned pack; no downloads, no experts.bin, no engine patches.',
        '```json\n'+json.dumps(summary,indent=2,ensure_ascii=False)+'\n```',
        'Quality requests were copied from saved final IQ3_S raw requests, with only model name changed. A max_tokens1536, B/C8192, same exact messages and sampling. No quality ranking. Maxima are 1-second sampled maxima across startup, smoke, speed and quality; RSS is sum of server+engine.']
    (OUT/'summary.md').write_text('\n\n'.join(lines)+'\n')
    return summary

def export_telemetry(name,number):
    path=OUT/'telemetry'/f'{name}.jsonl'
    samples=[json.loads(line) for line in path.read_text().splitlines()]
    rows=[]
    for s in samples:
        row={'timestamp':s['wall_time'],'phase':s.get('metrics',{}).get('live',{}).get('state'),
            'ram_used_gib':s['ram_used_gib'],'mem_available_gib':s['mem_available_gib'],
            'rss_gib':sum(p['rss_gib'] for p in s['processes']),
            'system_cpu_pct':s['system_cpu_pct'],'process_cpu_pct':sum(p['cpu_pct'] for p in s['processes']),
            'process_read_bytes':sum(p['read_bytes'] for p in s['processes'])}
        for i in [0,1]:
            g=next((g for g in s.get('gpus',[]) if g['index']==i),{})
            for field in ['util_pct','power_w','vram_gib']:row[f'gpu{i}_{field}']=g.get(field)
        rows.append(row)
    with (OUT/f'telemetry-64k-{number}.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return {'gpu0_util_pct_mean':statistics.mean(r['gpu0_util_pct'] for r in rows),
        'gpu0_power_w_mean':statistics.mean(r['gpu0_power_w'] for r in rows),
        'system_cpu_pct_mean':statistics.mean(r['system_cpu_pct'] for r in rows),
        'process_cpu_pct_mean':statistics.mean(r['process_cpu_pct'] for r in rows)}

available=c.psutil.virtual_memory().available/c.GIB
budget=min(80,max(0,available-24))
assert budget>0
verified=json.loads((BASE/'results/raw/q4-sha256.json').read_text())
assert len(verified)==4 and all(x['actual_sha256']==x['sha256'] and x['bytes']==x['actual_bytes'] for x in verified)
for x in verified:
    assert (Path('/srv/ai/models/strata/models/UD-Q4_K_XL')/x['file']).stat().st_size==x['bytes']
assert not Path('/srv/ai/models/strata/packs/ud-q4_k_xl/experts.bin').exists()
cfg=json.loads((BASE/'UD-Q4_K_XL-runtime.json').read_text())
args=cfg['args']
args[args.index('--resident-budget-gib')+1]=str(budget)
args[args.index('--max-context')+1]='65536'
if '--kv-resident' in args:
    i=args.index('--kv-resident');del args[i:i+2]
cfg.pop('layer_split',None)
cfg.update(gpu=0,port=18082,log=str(OUT/'smoke.log'))
assert '--layer-split' not in args and '--experimental-speed-projection' not in args
c.save(OUT/'config.json',cfg)
run=c.Campaign(OUT/'config.json',LABEL)
run.log=OUT/'smoke.log'
run.cfg['log']=str(run.log)
run.config=OUT/'config.json'
c.save(run.config,run.cfg)
smoke=None;startup=None;rows=[];proc=None;problem=None
try:
    assert available>=24
    command=[str(c.REPO/'.venv/bin/python'),'-m','serve.server','--engine','strata','--config',str(run.config),
             '--host','127.0.0.1','--port','18082']
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='0',STRATA_DECODE_TIMING='1')
    server_log=(OUT/'server.log').open('w')
    proc=subprocess.Popen(command,cwd=c.REPO,env=env,stdout=server_log,stderr=subprocess.STDOUT,start_new_session=True)
    run.pid=proc.pid
    c.save(OUT/'server-state.json',{'pid':proc.pid,'command':command,'CUDA_VISIBLE_DEVICES':'0'})
    with c.Sampler(proc.pid,'startup') as sampler:
        deadline=time.monotonic()+1800
        while time.monotonic()<deadline:
            health=c.api('/health')
            if isinstance(health,dict) and health.get('loaded') is True and health.get('status')=='ok':
                assert health['max_context']==65536 and not health['images']
                startup={'health':health,'metrics':c.api('/metrics')};break
            if proc.poll() is not None:raise RuntimeError(f'Server exited {proc.returncode}; see server.log and smoke.log')
            time.sleep(1)
        else:raise RuntimeError('Startup did not reach READY')
    c.save(OUT/'startup.json',dict(startup,telemetry=sampler.summary()))
    smoke=run.request([{'role':'system','content':'You are a helpful coding assistant.'},
        {'role':'user','content':'Explain binary search and its time complexity in clear English. Give a short Python example.'}],64,'smoke','smoke')
    assert smoke['text'].strip() and smoke['generated_tokens']==64
    assert smoke['draft_tokens']>0,'MTP not active'
    assert smoke['peak_vram1_gib']<.1,'GPU1 unexpectedly used'
    c.save(OUT/'smoke.json',smoke)
    print('Smoke passed; waiting for manual text review marker',flush=True)
    deadline=time.monotonic()+3600
    while not (OUT/'smoke-reviewed.json').exists():
        assert time.monotonic()<deadline,'Smoke review timeout'
        time.sleep(2)
    for n in [1,2,3]:
        messages,count,_=run.exact_prompt(63300,uuid.uuid4().hex)
        assert 63000<=count<=63500 and count+256+8<=65536
        print(f'64K run{n}: exact prompt tokens={count}',flush=True)
        rec=run.request(messages,256,f'speed-64k-{n}','measured','64K',n)
        rec.update(export_telemetry(f'speed-64k-{n}',n))
        c.save(OUT/f'speed-64k-{n}.json',rec);rows.append(rec)
        summarize(rows,smoke,startup)
    QUALITY.mkdir(parents=True,exist_ok=True)
    for key in KEYS:
        source=BASE/'results/raw'/f'IQ3_S-quality-{key}-request.json'
        payload=json.loads(source.read_text())
        c.save(OUT/'raw'/f'quality-source-{key}.json',payload)
        assert payload['temperature']==0 and payload['reasoning_effort']=='none'
        rec=run.request(payload['messages'],payload['max_tokens'],f'quality-{key}','quality')
        sent=json.loads((OUT/'raw'/f'quality-{key}-request.json').read_text())
        assert {k:v for k,v in sent.items() if k!='model'}=={k:v for k,v in payload.items() if k!='model'}
        rec.update(quality_source=str(source),single_gpu=True,configured_context=65536)
        c.save(QUALITY/(key+'.json'),rec)
        (QUALITY/(key+'.txt')).write_text(rec['text'])
        if rec['generated_tokens']==payload['max_tokens']:
            problem=f'Quality {key} reached identical IQ3_S output limit; saved response may be truncated.'
    skipped=QUALITY/'SKIPPED.txt'
    if skipped.exists():skipped.rename(QUALITY/'SKIPPED-multi-gpu.txt')
except Exception as e:
    problem=repr(e)
    print('STOP:',problem,flush=True)
finally:
    summary=summarize(rows,smoke,startup,problem)
    if proc and proc.poll() is None:
        os.killpg(proc.pid,signal.SIGTERM)
        try:proc.wait(timeout=20)
        except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL)
    print(json.dumps({k:summary[k] for k in ['load_ok','smoke_ok','resident_expert_gib','speed_median','quality_files','problem']},indent=2),flush=True)
