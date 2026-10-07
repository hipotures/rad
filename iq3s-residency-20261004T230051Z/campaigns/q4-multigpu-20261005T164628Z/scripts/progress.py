"""Read campaign artifacts only; no inference/telemetry query."""
import json,pathlib
C=pathlib.Path(__file__).resolve().parents[1]
status=json.loads((C/'STATUS.json').read_text());done=[]
for p in (C/'raw').glob('*/*/raw/run[1-3].json'):
 j=json.loads(p.read_text());done.append({'cell':'/'.join(p.relative_to(C/'raw').parts[:2]),'run':p.stem,'state':j['state'],'TG':j.get('TG'),'PP':j.get('PP')})
files=list((C/'raw').glob('*/*/telemetry/*.jsonl'));active=max(files,key=lambda p:p.stat().st_mtime) if files else None
live=None
if active:
 lines=active.read_text().splitlines()
 for line in reversed(lines[-3:]):
  try:
   row=json.loads(line);live={'file':str(active.relative_to(C)), 'sample_epoch':row['wall_time'],'MemAvailableGiB':row['mem_available_gib'],'CPU':row['system_cpu_pct'],'GPU_util':[g['util_pct'] for g in row.get('gpus',[])],'live':(row.get('metrics') or {}).get('live')};break
  except json.JSONDecodeError:continue
print(json.dumps({'state':status['state'],'running':status.get('running'),'valid_measured':sum(x['state']=='VALID' for x in done),'completed':done,'active':live},indent=2))
