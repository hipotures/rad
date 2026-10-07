#!/usr/bin/env python3
"""Metadata-only direct-I/O audit and supplementary actual-worker RSS/CPU/I/O at 1 Hz."""
import datetime,json,os,pathlib,sys,time
r=pathlib.Path(sys.argv[1]);core=int(sys.argv[2]);c=json.loads((r/'campaign_config.json').read_text());allowed=[pathlib.Path(p) for p in c['scratch'].values()];deadline=c['created_wall']+c['max_campaign_seconds'];seen=set();tracked={};last_discovery=0
with open(r/'raw/guest-direct-evidence.jsonl','a') as out,open(r/'samples/owned-worker-1hz.jsonl','a') as samples:
 while time.time()<deadline:
  try:os.kill(core,0)
  except ProcessLookupError:break
  if time.monotonic()-last_discovery>=5:
   last_discovery=time.monotonic()
   for path in pathlib.Path('/proc').iterdir():
    if not path.name.isdigit():continue
    try:
     exe=(path/'exe').readlink()
     if exe.name not in ['fio','hwbench','operations']:continue
     files=[]
     for fd in (path/'fd').iterdir():
      target=fd.readlink()
      if target.name not in ['corpus.bin','write.bin'] or target.parent not in allowed:continue
      info=(path/'fdinfo'/fd.name).read_text();flags=int(next(x for x in info.splitlines() if x.startswith('flags:')).split()[1],8);files.append({'fd':fd.name,'path':str(target),'flags_octal':oct(flags),'O_DIRECT':bool(flags&os.O_DIRECT)})
     if files:
      pid=int(path.name);tracked[pid]={'pid':pid,'process_group':os.getpgid(pid),'executable':str(exe),'files':files}
      if pid not in seen:out.write(json.dumps({'wall_time':time.time(),**tracked[pid]})+'\n');out.flush();seen.add(pid)
    except (FileNotFoundError,PermissionError,ProcessLookupError,StopIteration):pass
  for pid,meta in list(tracked.items()):
   path=pathlib.Path('/proc')/str(pid)
   try:
    stat=(path/'stat').read_text();fields=stat[stat.rfind(')')+2:].split();io={k:int(v) for k,v in (x.split(':') for x in (path/'io').read_text().splitlines())};cmd=(path/'cmdline').read_bytes().decode().replace('\0',' ')
    samples.write(json.dumps({'monotonic':time.monotonic(),'wall_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**meta,'user_ticks':int(fields[11]),'system_ticks':int(fields[12]),'minor_faults':int(fields[7]),'major_faults':int(fields[9]),'rss_bytes':int(fields[21])*os.sysconf('SC_PAGE_SIZE'),'io':io,'phase':'postwrite_verification' if '-postverify' in cmd else 'workload_including_warmup'})+'\n');samples.flush()
   except (FileNotFoundError,ProcessLookupError,PermissionError):tracked.pop(pid,None)
  time.sleep(1)
