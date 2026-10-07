#!/usr/bin/env python3
"""Run fio write/CRC correctness strictly inside a fresh GPU warmup, outside measurements."""
import json,pathlib,subprocess,time,sys
R=pathlib.Path(sys.argv[1]);ROOT=R.parent;target='gpu1-h2d-pinned-3145728';deadline=time.time()+1800
while time.time()<deadline:
 p=json.loads((R/'progress.json').read_text());running=p.get('running') or {}
 if running.get('scenario_id')==target and running.get('repetition')==1:break
 if p['status']!='RUNNING':raise RuntimeError('core not live/running')
 time.sleep(.5)
else:raise RuntimeError('probe warmup not reached')
start=time.monotonic();wall=time.time();out={'status':'SMOKE','target_warmup':running,'start_monotonic':start,'start_wall':wall,'steps':[]}
def put():tmp=R/'raw/fio-write-correctness-smoke.tmp';tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(R/'raw/fio-write-correctness-smoke.json')
D=R/'scratch-fio-write-smoke';D.mkdir(mode=0o700);file=D/'write.bin'
ledger=json.loads((R/'write-ledger.json').read_text());ledger['reserved_logical_bytes']+=2*(1<<30);ledger['entries'].append({'id':'fio-write-correctness-smoke','reservation_bytes':2*(1<<30),'scope':'prep, seed, warmup-only smoke'});(R/'write-ledger.json.tmp').write_text(json.dumps(ledger,indent=2)+'\n');(R/'write-ledger.json.tmp').replace(R/'write-ledger.json')
commands=[[str(ROOT/'hwbench'),'--mode','prepare','--file',str(file),'--op',str(256<<20),'--seconds','10'],[str(ROOT/'deps/fio/fio'),'--name=crc-seed-smoke','--filename='+str(file),'--allow_file_create=0','--size=256m','--rw=write','--bs=1m','--ioengine=io_uring','--iodepth=8','--direct=1','--verify=crc32c','--do_verify=0','--refill_buffers=1','--end_fsync=1','--output-format=json'],[str(ROOT/'deps/fio/fio'),'--name=crc-timed-smoke','--filename='+str(file),'--allow_file_create=0','--size=256m','--rw=write','--bs=1m','--ioengine=io_uring','--iodepth=8','--direct=1','--verify=crc32c','--do_verify=0','--refill_buffers=1','--end_fsync=1','--rate=128m','--time_based=1','--runtime=4','--output-format=json']]
for cmd in commands:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=max(1,11-(time.monotonic()-start)));out['steps'].append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});put()
 if p.returncode:out['status']='VERIFICATION_FAILED';put();raise RuntimeError('fio write probe failed')
out.update(end_monotonic=time.monotonic(),end_wall=time.time());out['measured_overlap']=out['end_monotonic']-start>=12
if out['measured_overlap']:out['status']='CONTAMINATED_PROBE_WINDOW_OVERRUN'
else:out['timing_scope']='Probe completed in first 12 seconds after observing new request; requested GPU warmup is at least 15 seconds plus initialization. No measured-window overlap.'
put()
