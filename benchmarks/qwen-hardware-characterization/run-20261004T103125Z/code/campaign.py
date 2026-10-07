#!/usr/bin/env python3
"""Bounded, resumable VM-path characterization. All writes use private scratch files."""
import argparse, csv, datetime, fcntl, hashlib, json, math, os, pathlib, random, signal, statistics, struct, subprocess, sys, time
ROOT=pathlib.Path(os.environ.get('BENCH_ROOT','/srv/ai/benchmarks/qwen-hardware-characterization')).resolve()
BIN=ROOT/'hwbench'; FIO=ROOT/'deps/fio/fio'; GIB=1<<30; MIB=1<<20
STOP=False

def signum(sig, frame):
    global STOP
    STOP=True
signal.signal(signal.SIGINT,signum); signal.signal(signal.SIGTERM,signum)
def atomic(path, obj):
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(obj,indent=2)+'\n'); os.replace(tmp,path)
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def command(cmd, timeout=20):
    try:
        p=subprocess.run(cmd,shell=isinstance(cmd,str),capture_output=True,text=True,timeout=timeout)
        return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except Exception as e:return {'command':cmd,'status':'UNAVAILABLE','error':str(e)}
def mem():
    return {k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines()) if v.strip().split()[0].isdigit()}
def snapshot(pids=()):
    t=time.monotonic(); info=mem(); cpu=pathlib.Path('/proc/stat').read_text().splitlines()[0].split()[1:]
    processes=[]
    for pid in pids:
        try:
            text=pathlib.Path(f'/proc/{pid}/stat').read_text(); fields=text[text.rfind(')')+2:].split(); io={k:int(v) for k,v in (x.split(':') for x in pathlib.Path(f'/proc/{pid}/io').read_text().splitlines())}
            status=pathlib.Path(f'/proc/{pid}/status').read_text()
            processes.append({'pid':pid,'user_ticks':int(fields[11]),'system_ticks':int(fields[12]),'minor_faults':int(fields[7]),'major_faults':int(fields[9]),'rss_bytes':int(fields[21])*os.sysconf('SC_PAGE_SIZE'),'io':io,'context_switches':[x for x in status.splitlines() if 'ctxt_switches' in x]})
        except (FileNotFoundError,ProcessLookupError,PermissionError):pass
    q=command(['nvidia-smi','--query-gpu=index,uuid,utilization.gpu,utilization.memory,memory.used,memory.free,power.draw,temperature.gpu,clocks.sm,clocks.mem,pcie.link.gen.current,pcie.link.width.current','--format=csv,noheader,nounits'],10)
    gpu=[]
    for line in q.get('stdout','').splitlines():
        vals=[x.strip() for x in line.split(',')]
        if len(vals)!=13:continue
        keys=['index','uuid','utilization_gpu_percent','utilization_memory_percent','vram_used_MiB','vram_free_MiB','power_W','temperature_C','sm_clock_MHz','memory_clock_MHz','pcie_generation','pcie_width']
        # The query has 12 fields; keep parser keyed to the actual request.
    keys=['index','uuid','utilization_gpu_percent','utilization_memory_percent','vram_used_MiB','vram_free_MiB','power_W','temperature_C','sm_clock_MHz','memory_clock_MHz','pcie_generation','pcie_width']
    for line in q.get('stdout','').splitlines():
        vals=[x.strip() for x in line.split(',')]
        if len(vals)!=len(keys):continue
        row={}
        for k,v in zip(keys,vals):
            try:row[k]=float(v)
            except ValueError:row[k]=v if k=='uuid' else None
        gpu.append(row)
    return {'monotonic':t,'wall_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memory':{k:info.get(k) for k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']},'cpu_ticks':[int(x) for x in cpu],'processes':processes,'gpu':gpu,'psi':{x:pathlib.Path('/proc/pressure/'+x).read_text() if pathlib.Path('/proc/pressure/'+x).exists() else None for x in ['cpu','memory','io']}}
def safety(sample, scratch):
    m=sample['memory'];reserve=max(16*GIB,.15*m['MemTotal'])
    if m['MemAvailable']<reserve:return 'MemAvailable below reserved minimum'
    if m['SwapTotal'] and m['SwapTotal']-m['SwapFree']>0:return 'new swap activity'
    for g in sample['gpu']:
        if g.get('temperature_C',0) and g['temperature_C']>=80:return 'GPU temperature >=80 C'
        if g.get('vram_free_MiB',0) is not None and g['vram_free_MiB']<3072:return 'GPU VRAM reserve below 3 GiB'
    for path in scratch:
        u=os.statvfs(path)
        if u.f_bavail*u.f_frsize<max(32*GIB,.15*u.f_blocks*u.f_frsize):return 'filesystem free-space reserve breached'
    return None

def inventory(run,config):
    cmds={'lscpu':['lscpu','-J'],'uname':['uname','-a'],'distribution':['cat','/etc/os-release'],'numa':['numactl','--hardware'],'topology':['nvidia-smi','topo','-m'],'gpus':['nvidia-smi','-q'],'processes':['ps','-eo','pid,ppid,comm,pcpu,pmem,args','--sort=-pcpu'],'lsblk':['lsblk','-J','-o','NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL,TRAN'],'mount_srv':['findmnt','-J','-T','/srv/ai'],'mount_home':['findmnt','-J','-T','/home/user/DEV/test20261001_1'],'nvcc':['/usr/local/cuda/bin/nvcc','--version'],'compiler':['g++','--version'],'cmake':['cmake','--version'],'fio_help':[str(FIO),'--help'],'fio_engines':[str(FIO),'--enghelp'],'fio_sha':['git','-C',str(ROOT/'deps/fio'),'rev-parse','HEAD'],'limits':['bash','-c','ulimit -a'],'pci':['lspci','-vv'],'cgroup':['cat','/proc/self/cgroup'],'gpu_processes':['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],'cuda_probe':[str(BIN),'--mode','probe']}
    raw={k:command(v) for k,v in cmds.items()}
    for k,v in raw.items():(run/'raw'/('inventory-'+k+'.json')).write_text(json.dumps(v,indent=2))
    inv={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':raw,'initial_snapshot':snapshot(),'affinity':sorted(os.sched_getaffinity(0)),'memlock':__import__('resource').getrlimit(__import__('resource').RLIMIT_MEMLOCK),'sysfs':{},'hidden':['host physical DRAM channels/CCD placement','virtiofs host SSD identity and page cache','ext4 virtual block device physical host identity/cache','physical SSD write amplification']}
    for p in ['/proc/sys/vm/nr_hugepages','/sys/kernel/mm/transparent_hugepage/enabled','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/cpuset.cpus.effective','/sys/block/sdb/queue/scheduler','/sys/block/sdb/queue/rotational','/sys/block/sdb/queue/nr_requests']:
        try:inv['sysfs'][p]=pathlib.Path(p).read_text()
        except Exception:inv['sysfs'][p]=None
    inv['cuda']=json.loads(raw['cuda_probe']['stdout'])
    atomic(run/'inventory.json',inv);(run/'inventory.txt').write_text('\n\n'.join(k+'\n'+v.get('stdout',v.get('error',''))+v.get('stderr','') for k,v in raw.items()))
    return inv

def matrix(config):
    out=[]
    def add(id,family,args=None,seconds=None,**kw):out.append({'id':id,'family':family,'args':args or [],'seconds':seconds or config['formal_seconds'],'warmup':config['warmup_seconds'],'repeats':config['formal_repeats'],**kw})
    add('idle-telemetry','A',tool='idle');add('idle-low-cadence','A',tool='idle',cadence=5)
    for op in ['read','copy','triad']:
        for t in [1,4,16]:add(f'ram-{op}-t{t}','B',['--mode','ram','--op',op,'--threads',str(t),'--bytes',str(GIB)],seconds=30 if t not in [1,16] else None)
    add('ram-gather-segments','B',['--mode','ram','--op','gather','--threads','8','--bytes',str(GIB)])
    for d in [0,1]:
        for mode,op in [('local','copy'),('gemm','large'),('gemm','small')]:add(f'gpu{d}-{mode}-{op}','C',['--mode',mode,'--op',op,'--device',str(d),'--bytes',str(256*MIB)])
    add('both-gpu-local','C',['--mode','local','--bytes',str(256*MIB)],concurrent_device=True)
    add('both-gpu-gemm','C',['--mode','gemm'],concurrent_device=True)
    add('gpu0-gemm-low-telemetry','A',['--mode','gemm'],cadence=5)
    for d in [0,1]:
        for direction in ['h2d','d2h']:
            for kind in ['pageable','pinned']:
                for size in [4096,3*MIB,64*MIB]:add(f'gpu{d}-{direction}-{kind}-{size}','D',['--mode','transfer','--device',str(d),'--direction',direction,'--kind',kind,'--bytes',str(size)],seconds=30 if size==4096 else None)
        add(f'gpu{d}-stage-expert','D',['--mode','transfer','--device',str(d),'--kind','stage','--bytes',str(3*MIB)])
        add(f'gpu{d}-pinned-double-bulk','D',['--mode','transfer','--device',str(d),'--buffers','2','--bytes',str(64*MIB)])
        add(f'gpu{d}-registration','D',['--mode','registration','--device',str(d),'--bytes',str(64*MIB)],seconds=30)
        for scatter in [False,True]:add(f'gpu{d}-mapped-'+('scatter' if scatter else 'coalesced'),'D',['--mode','mapped','--device',str(d),'--bytes',str(512*MIB)]+(['--scatter'] if scatter else []))
    for direction in ['h2d','d2h','mixed']:add('both-'+direction,'D',['--mode','transfer','--both','--direction',direction,'--bytes',str(64*MIB),'--buffers','2'])
    add('gpu0-bidirectional','D',['--mode','transfer','--direction','bidir','--buffers','2','--bytes',str(64*MIB)])
    for d in [0,1]:
        for size in [4096,3*MIB,64*MIB]:
            add(f'bridge-{d}-{1-d}-{size}-serial','E',['--mode','bridge','--device',str(d),'--bytes',str(size)],seconds=30 if size==4096 else None)
        add(f'bridge-{d}-{1-d}-bulk-double','E',['--mode','bridge','--device',str(d),'--bytes',str(64*MIB),'--buffers','2'])
        add(f'peer-{d}-{1-d}','E',['--mode','bridge','--device',str(d),'--kind','peer','--bytes',str(64*MIB)])
    add('bridge-roundtrip-activation','E',['--mode','bridge','--bytes','32768','--op','roundtrip'])
    add('bridge-bidirectional','E',['--mode','bridge','--bytes',str(64*MIB),'--buffers','2'],concurrent_device=True)
    for storage in ['virtiofs','ext4']:
        add(storage+'-first-pass','F',tool='fio',storage=storage,rw='read',bs=MIB,direct=False,depth=1,first_pass=True,repeats=1)
        for rw,bs,direct,depth in [('read',MIB,False,1),('read',MIB,True,8),('randread',4096,True,1),('randread',4096,True,16),('randread',256*1024,True,8),('randread',MIB,True,1),('randread',3*MIB,True,1),('randread',3*MIB,True,8),('randread',8*MIB,True,8),('randread',3*MIB,False,1)]:
            add(f'{storage}-{rw}-{bs}-direct{int(direct)}-qd{depth}','F',tool='fio',storage=storage,rw=rw,bs=bs,direct=direct,depth=depth)
        add(storage+'-write-durable','F',tool='fio',storage=storage,rw='write',bs=MIB,direct=True,depth=8,write=True,seconds=20)
        for d in [0,1]:
            for buffers in [1,3]:add(f'{storage}-pipeline-gpu{d}-b{buffers}','G',['--mode','pipeline','--op','random','--kind','pinned','--device',str(d),'--bytes',str(3*MIB),'--buffers',str(buffers),'--direct'],storage=storage)
        add(f'{storage}-pipeline-stage','G',['--mode','pipeline','--op','random','--kind','stage','--bytes',str(3*MIB),'--buffers','3','--direct'],storage=storage)
        add(f'{storage}-pipeline-readers2','G',['--mode','pipeline','--op','random','--kind','pinned','--bytes',str(3*MIB),'--buffers','3','--threads','2','--direct'],storage=storage)
        add(f'{storage}-pipeline-bulk','G',['--mode','pipeline','--op','seq','--kind','pinned','--bytes',str(64*MIB),'--buffers','3','--direct'],storage=storage)
        add(f'{storage}-pipeline-shared-both','G',['--mode','pipeline','--op','random','--kind','pinned','--bytes',str(3*MIB),'--buffers','2','--both','--direct'],storage=storage)
    # Matched A/B: each baseline immediately precedes or follows its loaded case.
    for workload,args in [('gemm',['--mode','gemm']),('dispatch',['--mode','gemm','--op','small']),('cpu',['--mode','ram','--op','triad','--threads','8','--bytes',str(GIB)])]:
        for rate in [100*MIB,500*MIB,2*GIB]:
            for arm in ['A','B']:add(f'interference-{workload}-{rate}-{arm}','H',args+(['--rate',str(rate)] if arm=='B' else []),pair=f'{workload}-{rate}',arm=arm,requested_rate=rate if arm=='B' else 0)
    for arm in ['A','B']:add(f'interference-burst30s-{arm}','H',['--mode','gemm','--op','small']+(['--rate',str(100*MIB),'--burst',str(3000*MIB)] if arm=='B' else []),pair='burst30s',arm=arm,requested_rate=100*MIB if arm=='B' else 0,burst_bytes=3000*MIB if arm=='B' else 0)
    for arm in ['A','B']:add(f'interference-both-gpus-{arm}','H',['--mode','gemm']+(['--rate',str(500*MIB)] if arm=='B' else []),concurrent_device=True,pair='both-gpus',arm=arm,requested_rate=500*MIB if arm=='B' else 0)
    for op in ['contiguous','pack','noninclusive']:add('residency-'+op,'I',['--mode','residency','--op',op])
    add('controller-ranked-plan','I',['--mode','controller'])
    # Bound the breadth before execution; every family remains represented.
    out=[c for c in out if c['id'] not in ['both-gpu-local','idle-low-cadence','gpu1-registration','virtiofs-pipeline-gpu1-b1','virtiofs-pipeline-gpu1-b3','virtiofs-pipeline-readers2','virtiofs-pipeline-stage']
         and not (c['family']=='F' and c.get('bs') in [MIB,8*MIB] and c.get('rw')=='randread')
         and not (c['family']=='H' and c.get('pair') in [f'gemm-{500*MIB}',f'cpu-{500*MIB}'])]
    for c in out:
        headline=(c['family']=='H' or (c['family']=='D' and '-pinned-3145728' in c['id']))
        if not headline and not c.get('first_pass'):
            c['seconds']=min(20,config['formal_seconds'])
        c['headline']=headline
    for arm in ['A','B']:
        add(f'interference-combined-{arm}','H',['--mode','combined']+(['--rate',str(500*MIB)] if arm=='B' else []),pair='combined',arm=arm,requested_rate=500*MIB if arm=='B' else 0,headline=True)
        add(f'interference-storage-ext4-{arm}','H',['--mode','gemm','--op','small']+(['--rate',str(500*MIB)] if arm=='B' else []),pair='storage-ext4',arm=arm,requested_rate=500*MIB if arm=='B' else 0,headline=True,**({'storage':'ext4'} if arm=='B' else {}))
    for storage in ['virtiofs','ext4']:
        add(storage+'-reverse-durable','G',['--mode','reverse','--bytes',str(3*MIB)],seconds=20,storage=storage,write=True,headline=False)
    add('controller-cooperative','I',['--mode','controller','--op','cooperative'],seconds=20,headline=False,nice=10)
    for arm in ['A','B']:
        add(f'interference-controller-{arm}','I',['--mode','ram','--op','triad','--threads','8','--bytes',str(GIB)],seconds=20,pair='controller',arm=arm,headline=False,**({'sidecar':['--mode','controller','--op','cooperative']} if arm=='B' else {}))
    add('process-cuda-initialization-events','A',tool='launch_events',seconds=20,headline=False)
    return out

def safe_file(config,storage,write=False):
    directory=pathlib.Path(config['scratch'][storage]);path=directory/('write.bin' if write else 'corpus.bin')
    if directory.resolve()!=directory or path.is_symlink() or path.parent.resolve()!=directory:raise RuntimeError('scratch path escaped allowlist')
    if not path.exists() or not path.is_file():raise RuntimeError('missing regular owned scratch file')
    return path

def stop_children(children):
    for p in children:
        if p.poll() is None:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
    end=time.monotonic()+10
    while time.monotonic()<end and any(p.poll() is None for p in children):time.sleep(.2)
    for p in children:
        if p.poll() is None:
            state=pathlib.Path(f'/proc/{p.pid}/stat').read_text().split(') ')[1].split()[0]
            if state=='D':raise RuntimeError('benchmark process in uninterruptible I/O; stop scheduling')
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
    for p in children:p.wait(timeout=10)

def run_one(run,config,case,rep):
    id=f"{case['id']}-r{rep}"; stdout=run/'raw'/f'{id}.stdout';stderr=run/'raw'/f'{id}.stderr';telemetry=run/'samples'/f'{id}.jsonl'
    durations=(case['warmup'],case['seconds']);paths=list(config['scratch'].values());safe=safety(snapshot(),paths)
    record={'scenario_id':case['id'],'repetition':rep,'case':case,'software_identity':config['code_hash'],'raw_stdout':str(stdout),'raw_stderr':str(stderr),'telemetry':str(telemetry),'warmup_seconds':case['warmup'],'physical_leg_scope':'known logical transfer legs or estimated read/write traffic; not measured hardware bus transactions','cache_assumptions':'warm steady-state; guest direct does not establish cold host SSD','path':case.get('storage','host/GPU'),'affinity':sorted(os.sched_getaffinity(0)),'unsupported_counters':{'physical_ssd_bytes':'host device/cache not exposed','SM_occupancy':'nvidia-smi utilization is not occupancy','PSS':'intentionally not polled'}}
    if safe:return {**record,'status':'SKIPPED_SAFETY','reason':safe}
    tool=case.get('tool','native');commands=[]
    if tool=='native':
        args=list(case['args'])+['--seconds',str(case['seconds']),'--warmup',str(case['warmup'])]
        if case.get('storage'):args+=['--file',str(safe_file(config,case['storage'],case.get('write',False)))]
        if case.get('concurrent_device'):
            commands=[[str(BIN)]+args+['--device',str(d)] for d in [0,1]]
        else:commands=[[str(BIN)]+args]
        if case.get('nice'):commands=[['nice','-n',str(case['nice'])]+cmd for cmd in commands]
        if case.get('sidecar'):commands.append(['nice','-n','10',str(BIN)]+case['sidecar']+['--seconds',str(case['seconds']),'--warmup',str(case['warmup'])])
        if case.get('write'):
            ledger=json.loads((run/'write-ledger.json').read_text());reservation=128*MIB*(case['seconds']+case['warmup']+5)
            if ledger['reserved_logical_bytes']+reservation>config['max_write_gib']*GIB:return {**record,'status':'SKIPPED_SAFETY','reason':'reverse write budget'}
            ledger['reserved_logical_bytes']+=reservation;ledger['entries'].append({'id':id,'reservation_bytes':reservation});atomic(run/'write-ledger.json',ledger)
    elif tool=='launch_events':commands=[[sys.executable,str(ROOT/'launch_events.py'),str(case['seconds']),str(case['warmup'])]]
    elif tool=='fio':
        path=safe_file(config,case['storage'],case.get('write',False));cmd=[str(FIO),'--name='+id,'--filename='+str(path),'--allow_file_create=0','--rw='+case['rw'],'--bs='+str(case['bs']),'--ioengine=io_uring','--iodepth='+str(case['depth']),'--direct='+str(int(case['direct'])),'--size='+str(path.stat().st_size),'--output-format=json+','--group_reporting=1','--randrepeat=1','--randseed=761','--invalidate=0','--eta=never']
        if case.get('first_pass'):cmd+=['--loops=1'];record['warmup_seconds']=0
        else:cmd+=['--time_based=1','--runtime='+str(case['seconds']),'--ramp_time='+str(case['warmup'])]
        if case.get('write'):
            reservation=128*MIB*(case['seconds']+case['warmup']+5)
            ledger=json.loads((run/'write-ledger.json').read_text())
            if ledger['reserved_logical_bytes']+reservation>config['max_write_gib']*GIB:return {**record,'status':'SKIPPED_SAFETY','reason':'write ledger ceiling'}
            ledger['reserved_logical_bytes']+=reservation;ledger['entries'].append({'id':id,'reservation_bytes':reservation});atomic(run/'write-ledger.json',ledger)
            cmd+=['--rate=128m','--refill_buffers=1','--buffer_compress_percentage=0','--end_fsync=1','--fsync=128','--verify=crc32c','--do_verify=0','--write_iolog='+str(run/'raw'/f'{id}-writes.iolog')]
        else:cmd+=['--readonly']
        commands=[cmd]
    record['commands']=commands;atomic(run/'raw'/f'{id}.command.json',record)
    handles=[];children=[];start=time.monotonic();last=-10;cadence=case.get('cadence',1);deadline=start+180
    if tool=='idle':deadline=start+case['seconds']+5
    dmonout=open(run/'samples'/f'{id}-pcie.txt','w');dmon=subprocess.Popen(['nvidia-smi','dmon','-s','t','-d','1'],stdout=dmonout,stderr=subprocess.STDOUT,start_new_session=True)
    try:
        for i,cmd in enumerate(commands):
            so=open(str(stdout)+(f'.{i}' if len(commands)>1 else ''),'w');se=open(str(stderr)+(f'.{i}' if len(commands)>1 else ''),'w');handles += [so,se]
            children.append(subprocess.Popen(cmd,stdout=so,stderr=se,start_new_session=True))
        rows=[]
        with open(telemetry,'w') as tf:
            while not STOP and time.monotonic()<deadline:
                if tool=='idle' and time.monotonic()-start>=case['seconds']:break
                if tool!='idle' and all(p.poll() is not None for p in children):break
                row=snapshot([p.pid for p in children]);row.update(scenario_id=case['id'],repetition=rep,phase='warmup_or_measurement_native_log_authoritative');rows.append(row);tf.write(json.dumps(row)+'\n');tf.flush()
                reason=safety(row,paths)
                if reason:record.update(status='SKIPPED_SAFETY',reason=reason);break
                if time.monotonic()-last>=5:
                    apps=command(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'])
                    foreign=[int(x.strip()) for x in apps.get('stdout','').splitlines() if x.strip().isdigit() and int(x.strip()) not in [p.pid for p in children]]
                    if foreign:record.update(status='CONTAMINATED',reason='foreign CUDA workload appeared',foreign_pids=foreign);break
                    last=time.monotonic();print(f"[{case['id']}] repetition {rep}/{case['repeats']} elapsed={last-start:.1f}/{sum(durations)}s MemAvailable={row['memory']['MemAvailable']/GIB:.1f}GiB",flush=True)
                time.sleep(cadence)
        if any(p.poll() is None for p in children):record.setdefault('status','INTERRUPTED' if STOP else 'TIMEOUT');stop_children(children)
        for h in handles:h.close()
        record['total_wall_seconds']=time.monotonic()-start
        record['telemetry_peaks']={'rss_bytes':max((sum(p['rss_bytes'] for p in x['processes']) for x in rows),default=0),'memavailable_min':min((x['memory']['MemAvailable'] for x in rows),default=None),'gpu_vram_MiB':{str(d):max((g['vram_used_MiB'] for x in rows for g in x['gpu'] if g['index']==d and g['vram_used_MiB'] is not None),default=None) for d in [0,1]}}
        if record.get('status'):return record
        if tool=='idle':return {**record,'status':'OK','actual_measured_seconds':record['total_wall_seconds'],'verification':'NOT_APPLICABLE','completed_logical_bytes':0}
        outputs=[pathlib.Path(str(stdout)+(f'.{i}' if len(commands)>1 else '')).read_text() for i in range(len(commands))]
        errors=[pathlib.Path(str(stderr)+(f'.{i}' if len(commands)>1 else '')).read_text() for i in range(len(commands))]
        record['returncodes']=[p.returncode for p in children]
        if any(p.returncode!=0 for p in children):
            status='VERIFICATION_FAILED' if any('VERIFICATION_FAILED' in e for e in errors) else 'UNSUPPORTED' if any('Operation not supported' in e or 'Invalid argument' in e or 'io_uring' in e and 'Operation not permitted' in e for e in errors) else 'ERROR'
            return {**record,'status':status,'reason':'\n'.join(errors)[-6000:]}
        if tool in ['native','launch_events']:
            vals=[json.loads(o.strip().splitlines()[-1]) for o in outputs]
            if len(vals)==1:record.update(vals[0])
            elif case.get('sidecar'):record.update(vals[0]);record['sidecar']=vals[1]
            else:
                record['paths']=vals;record.update(status='OK',actual_measured_seconds=max(x['actual_measured_seconds'] for x in vals),completed_logical_bytes=sum(x['completed_logical_bytes'] for x in vals),physical_leg_bytes=sum(x['physical_leg_bytes'] for x in vals),useful_work_count=sum(x['useful_work_count'] for x in vals),verification='PASS',concurrency_note='two independently timed worker windows, overlap reported from native/host timestamps; not sum of isolated peaks')
                record['bandwidth_GB_s']=record['completed_logical_bytes']/record['actual_measured_seconds']/1e9;record['work_rate']=record['useful_work_count']/record['actual_measured_seconds']
                record['traffic_completed_bytes']=sum(x.get('traffic_completed_bytes',0) for x in vals)
        else:
            fio=json.loads(outputs[0]);j=fio['jobs'][0];r=j['write'] if case.get('write') else j['read'];record.update(status='OK',actual_measured_seconds=r['runtime']/1000,completed_logical_bytes=r['io_bytes'],bandwidth_GB_s=r['bw_bytes']/1e9,bandwidth_GiB_s=r['bw_bytes']/GIB,useful_work_count=r['total_ios'],work_rate=r['iops'],verification='CORPUS_SIGNATURE_CHECKED_OUTSIDE_TIMING',fio_error=j['error'],achieved_depth=j.get('iodepth_level'),fio_latency=r.get('clat_ns'),fio_cpu={'user_percent':j.get('usr_cpu'),'system_percent':j.get('sys_cpu')},durability='periodic fsync every 128 MiB and end fsync' if case.get('write') else None)
            if j['error']:record['status']='ERROR'
            if case.get('first_pass'):record['status']='PROBE';record['cache_assumptions']='first process pass after preparation+fdatasync, NOT cold SSD'
        if case.get('write'):
            ledger=json.loads((run/'write-ledger.json').read_text())
            if tool=='fio':
                iolog=(run/'raw'/f'{id}-writes.iolog').read_text().splitlines();actual=sum(int(line.split()[-1]) for line in iolog if len(line.split())>=4 and line.split()[-3]=='write')
            else:actual=record.get('storage_written_total')
            record['total_logical_write_bytes_including_warmup']=actual
            for entry in ledger['entries']:
                if entry['id']==id:entry['actual_logical_bytes']=actual
            atomic(run/'write-ledger.json',ledger)
        if record['status']=='OK' and record.get('actual_measured_seconds',0)<10:record.update(status='ERROR',reason='formal performance window below ten seconds')
        return record
    finally:
        stop_children(children+[dmon]);dmonout.close()
        for h in handles:
            if not h.closed:h.close()

def mix(x):
    mask=(1<<64)-1;x=(x+0x9e3779b97f4a7c15)&mask;x=((x^(x>>30))*0xbf58476d1ce4e5b9)&mask;x=((x^(x>>27))*0x94d049bb133111eb)&mask;return x^(x>>31)
def verify_corpus(path):
    with open(path,'rb') as f:
        for off in [0,4096,3*MIB,path.stat().st_size//2,path.stat().st_size-4096]:
            f.seek(off);words=struct.unpack('<512Q',f.read(4096))
            if any(v!=mix(off//8+j+17) for j,v in enumerate(words)):raise RuntimeError('corpus signature verification failed')
    return {'status':'PASS','bytes_checked':5*4096,'method':'five 4096-byte deterministic offset-dependent signatures; not full-file scan'}

def main():
    global STOP
    ap=argparse.ArgumentParser();ap.add_argument('--resume',type=pathlib.Path);ap.add_argument('--only');ap.add_argument('--initialize-only',action='store_true');args=ap.parse_args()
    ROOT.mkdir(parents=True,exist_ok=True)
    if args.resume:run=args.resume.resolve();config=json.loads((run/'campaign_config.json').read_text())
    else:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=ROOT/('run-'+stamp);run.mkdir();
        for p in ['raw','samples','plots']: (run/p).mkdir()
        homescratch=pathlib.Path('/home/user/DEV/test20261001_1')/('hwchar-scratch-'+stamp)
        override=os.environ.get('BENCH_DATA_DIR');primary=pathlib.Path(override).resolve() if override else run/'scratch-virtiofs'
        if override:primary=primary/('hwchar-scratch-'+stamp)
        scratch={'virtiofs':primary,'ext4':homescratch}
        for p in scratch.values():
            if p.exists() or p.is_symlink():raise RuntimeError('scratch must be newly created')
            p.mkdir(mode=0o700)
        config={'run_directory':str(run),'scratch':{k:str(v.resolve()) for k,v in scratch.items()},'max_campaign_seconds':int(os.environ.get('MAX_CAMPAIGN_SECONDS','21600')),'formal_seconds':float(os.environ.get('FORMAL_SECONDS','60')),'warmup_seconds':float(os.environ.get('WARMUP_SECONDS','15')),'formal_repeats':int(os.environ.get('FORMAL_REPEATS','3')),'max_write_gib':int(os.environ.get('MAX_STORAGE_WRITE_GIB','512')),'corpus_gib_per_path':16,'code_hash':sha(BIN),'python_hash':sha(pathlib.Path(__file__)),'source_hash':sha(ROOT/'src/hwbench.cu'),'created_wall':time.time(),'safety':{'ram_available_min':'max(16 GiB,15% MemTotal)','total_anonymous_pinned_limit':'min(64 GiB,50% initial available)','gpu_free_min_gib':3,'gpu_temperature_abort_C':80,'filesystem_free_min':'max(32 GiB,15% capacity)','watchdog_seconds':180},'build_command':'nvcc -O3 -std=c++17 -arch=sm_89 -Xcompiler=-fopenmp -Xcompiler=-pthread src/hwbench.cu -lcublas -o hwbench'}
        atomic(run/'campaign_config.json',config);inventory(run,config)
        atomic(run/'write-ledger.json',{'reserved_logical_bytes':0,'entries':[]})
        cases=matrix(config);estimate=sum((c['seconds']+c['warmup']+4)*c['repeats'] for c in cases)+900
        atomic(run/'plan.json',{'scenarios':cases,'estimated_seconds':estimate,'estimated_preparation_seconds':900,'estimated_logical_write_GiB':32+2*(20+15+5)*.125*3,'supporting_windows':'20-second supporting matrix windows, 15-second warmup, 3 repeats; 60 seconds for interference and pinned expert-size headline scenarios','anomaly_reserve_seconds':config['max_campaign_seconds']-estimate,'families_required':list('ABCDEFGHI')})
        atomic(run/'progress.json',{'status':'PREPARING','completed':[],'started_wall':time.time(),'running':None,'pending':[c['id'] for c in cases]})
    print('RUN_DIRECTORY='+str(run),flush=True)
    lock=open(run/'lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if config['code_hash']!=sha(BIN) or config['python_hash']!=sha(pathlib.Path(__file__)):raise RuntimeError('code/config identity mismatch; start new campaign or explicit audited migration')
    cases=json.loads((run/'plan.json').read_text())['scenarios'];progress=json.loads((run/'progress.json').read_text());manifest={}
    for storage,directory in config['scratch'].items():
        path=pathlib.Path(directory)/'corpus.bin';manifestpath=run/('scratch-'+storage+'-manifest.json')
        if manifestpath.exists():manifest[storage]=json.loads(manifestpath.read_text());verify_corpus(path);continue
        if path.exists():raise RuntimeError('unmanifested partial corpus; inspect before resume')
        reserve=config['corpus_gib_per_path']*GIB
        st=os.statvfs(directory)
        if st.f_bavail*st.f_frsize-reserve<max(32*GIB,.15*st.f_blocks*st.f_frsize):raise RuntimeError('insufficient filesystem space for corpus reserve')
        ledger=json.loads((run/'write-ledger.json').read_text())
        if ledger['reserved_logical_bytes']+reserve>config['max_write_gib']*GIB:raise RuntimeError('preparation exceeds write budget')
        ledger['reserved_logical_bytes']+=reserve;ledger['entries'].append({'id':'prepare-'+storage,'reservation_bytes':reserve});atomic(run/'write-ledger.json',ledger)
        cmd=[str(BIN),'--mode','prepare','--file',str(path),'--op',str(reserve),'--seconds','120'];atomic(run/'raw'/('prepare-'+storage+'-command.json'),cmd)
        log=open(run/'raw'/('prepare-'+storage+'.stdout'),'w');err=open(run/'raw'/('prepare-'+storage+'.stderr'),'w');p=subprocess.Popen(cmd,stdout=log,stderr=err,start_new_session=True);t=time.monotonic()
        while p.poll() is None and time.monotonic()-t<180 and not STOP:
            print(f'Preparing {storage}: elapsed={time.monotonic()-t:.1f}s target=16GiB',flush=True)
            if safety(snapshot([p.pid]),list(config['scratch'].values())):break
            time.sleep(5)
        if p.poll() is None:stop_children([p])
        log.close();err.close()
        if p.returncode or path.stat().st_size!=reserve:raise RuntimeError('bounded corpus preparation failed; partial file preserved')
        stat=path.stat();m={'path':str(path),'size':stat.st_size,'allocated_bytes':stat.st_blocks*512,'mtime_ns':stat.st_mtime_ns,'seed':17,'pattern':'splitmix64(global_word_index + 17)','fsync':'fdatasync completed','verification':verify_corpus(path),'compression_visibility':'virtiofs host options hidden; ext4 no compression visible','created_exclusively':True};atomic(manifestpath,m);manifest[storage]=m
        # Separate owned file for secondary writes. Never overwrite the read corpus.
        writepath=pathlib.Path(directory)/'write.bin'
        with open(writepath,'xb') as f:
            data=os.urandom(MIB)
            for j in range(256):f.write(data if j==0 else os.urandom(MIB))
            f.flush();os.fdatasync(f.fileno())
        ledger=json.loads((run/'write-ledger.json').read_text());ledger['reserved_logical_bytes']+=256*MIB;ledger['entries'].append({'id':'write-file-prepare-'+storage,'reservation_bytes':256*MIB});atomic(run/'write-ledger.json',ledger)
    progress['status']='READY';atomic(run/'progress.json',progress)
    if args.initialize_only:return
    results=[]
    if (run/'results.jsonl').exists():results=[json.loads(x) for x in (run/'results.jsonl').read_text().splitlines()]
    done={(r['scenario_id'],r['repetition']) for r in results if r['status'] in ['OK','PROBE','UNSUPPORTED','SKIPPED_SAFETY','SKIPPED_TIME_BUDGET']}
    jobs=[(c,r) for c in cases for r in range(1,c['repeats']+1) if not args.only or c['id']==args.only]
    # Interference A/B repetitions are adjacent, alternate order by repeat.
    jobs.sort(key=lambda cr:(0 if not cr[0].get('pair') else 1, cases.index(cr[0]) if not cr[0].get('pair') else min(i for i,c in enumerate(cases) if c.get('pair')==cr[0].get('pair')),cr[1],0 if cr[0].get('arm')==('A' if cr[1]%2 else 'B') else 1))
    total=len(jobs);budget_deadline=progress['started_wall']+config['max_campaign_seconds']
    for index,(case,rep) in enumerate(jobs):
        if (case['id'],rep) in done:continue
        if STOP:break
        if time.time()+case['seconds']+case['warmup']+10>budget_deadline:
            record={'scenario_id':case['id'],'repetition':rep,'case':case,'status':'SKIPPED_TIME_BUDGET','reason':'campaign deadline'}
        else:
            progress.update(status='RUNNING',running={'scenario_id':case['id'],'repetition':rep},completed_requests=len(done),total_requests=total);atomic(run/'progress.json',progress)
            print(f'[scenario {index+1}/{total}] '+case['id'],flush=True);record=run_one(run,config,case,rep)
        with open(run/'results.jsonl','a') as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
        results.append(record);done.add((case['id'],rep));progress['completed'].append({'id':case['id'],'repetition':rep,'status':record['status']});progress['running']=None;atomic(run/'progress.json',progress)
        if record['status'] in ['VERIFICATION_FAILED','SKIPPED_SAFETY','CONTAMINATED'] or any(x in record.get('reason','').lower() for x in ['out of memory','illegal memory','input/output error','xid']):STOP=True
    for storage,m in manifest.items():m['verification_after']=verify_corpus(pathlib.Path(m['path']));atomic(run/('scratch-'+storage+'-manifest.json'),m)
    progress.update(status='STOPPED' if STOP else 'MEASUREMENTS_COMPLETE',running=None,pending=[{'id':c['id'],'repetition':r} for c,r in jobs if (c['id'],r) not in done]);atomic(run/'progress.json',progress)
    print('Campaign measurement phase '+progress['status'],flush=True)
if __name__=='__main__':main()
