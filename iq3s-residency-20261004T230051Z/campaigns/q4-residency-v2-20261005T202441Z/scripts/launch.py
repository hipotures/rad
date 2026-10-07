"""Frozen foreground launch paths; no build/update and no campaign-deadline override."""
from campaign import C,R,load,save
from q4_multigpu import Q4Session
from lab import owned_stop,api
from pathlib import Path
import argparse,datetime,hashlib,json,os,psutil,signal,subprocess,time

def verify(cfg):
    exe=Path(cfg['exe']).resolve();assert exe.is_file()
    assert hashlib.sha256(exe.read_bytes()).hexdigest()==cfg['binary_sha256'],'Frozen binary hash mismatch'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True).strip()==cfg['source_sha'],'Frozen source SHA mismatch'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=cfg['cwd'],text=True).strip(),'Frozen source dirty'
    model=load(C/'git/model.json');assert model['quant']=='UD-Q4_K_XL' and model['revision']==cfg['model_revision']
    for shard in model['shards']:
        stat=Path(shard['path']).stat()
        assert stat.st_size==shard['bytes'] and stat.st_mtime_ns==shard['mtime_ns'],'Model shard changed: '+shard['path']
    for name,entry in model['files'].items():
        path=Path(name);assert path.stat().st_size==entry['bytes'],'Pack/profile/MTP size changed: '+name
        if entry['bytes']<8*1024**2:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],'Small dependency hash changed: '+name
    for key in ['tokenizer','server_entrypoint','python']:assert Path(cfg[key]).exists(),key
    expected={'CUDA_VISIBLE_DEVICES':'0,1','STRATA_POOL_SPIN_US':'100'}
    assert all(cfg['env'].get(key)==value for key,value in expected.items())
    assert cfg['layer_split']=='24' and cfg['gpu']==[0,1] and cfg['parallel']==1
    args=cfg['args'];required={'--pcie-frac':'.28','--pool-workers':'15','--spec':'4','--spec-min-p':'0.5','--kv':'int8','--kv-resident':'32768','--prefill':'auto','--suffix-draft':'0','--prompt-cache':'0'}
    assert all(args[args.index(key)+1]==value for key,value in required.items())
    assert args[args.index('--max-context')+1]==str(cfg['max_total_context'])
    return {'binary':str(exe),'source':cfg['source_sha'],'binary_sha256':cfg['binary_sha256'],'model_revision':model['revision'],
        'weight_verification':'Previously verified large-file hashes plus current size/mtime; small dependencies rehashed. No model download/update.',
        'frozen_configuration':cfg}

class LaunchSession(Q4Session):
    def __enter__(self):
        try:
            result=super().__enter__();self.budgeted=False
            children=[p for p in psutil.Process(self.proc.pid).children(recursive=True) if Path(p.exe()).resolve()==Path(self.cfg['exe']).resolve()]
            assert len(children)==1;native=children[0];env=native.environ()
            observed={k:v for k,v in env.items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'}
            expected=self.cfg['env'];assert all(observed.get(k)==v for k,v in expected.items())
            assert set(observed)<=set(expected)|{'STRATA_RESEARCH_OUTPUT_IDS'}
            command=native.cmdline();assert command[command.index('--layer-split')+1]=='24'
            save(self.path/'raw/native-process.json',{'pid':native.pid,'create_time':native.create_time(),'exe':native.exe(),'command':command,'effective_environment':observed})
            return result
        except BaseException:self.__exit__();raise

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['start','stop','reproduce'])
    parser.add_argument('--variant',required=True,choices=['control','history-v2','early-v1'])
    parser.add_argument('--profile',choices=['32k','128k','256k'],default='128k')
    parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--check',action='store_true');parser.add_argument('--smoke',action='store_true')
    arg=parser.parse_args();variant_dir=C/'launchers'/arg.variant
    if arg.action=='stop':
        owner=variant_dir/'owned-process.json'
        if owner.exists():
            record=load(owner);owned_stop(record['pid'],record['create_time'])
        print('Owned server stop complete; unrelated processes untouched',flush=True);return
    cfg=load(variant_dir/f'{arg.profile}.json');cfg.update(host=arg.host,port=arg.port)
    print('VERIFIED_CONFIG',json.dumps(verify(cfg),indent=2),flush=True)
    if arg.check:print('CHECK PASS; server not started',flush=True);return
    if arg.action=='reproduce':
        state=load(C/'STATUS.json').get('state','')
        assert state.startswith('COMPLETE') or time.time()>load(C/'deadline.json')['deadline_epoch'],'No extra active-campaign repetitions; replay only after completion/deadline'
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    path=C/('reproductions' if arg.action=='reproduce' else 'manual')/arg.variant/(arg.profile+'-'+stamp)
    stopping=False
    def stop(*_):
        nonlocal stopping;stopping=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    if arg.action=='reproduce':
        # Match the primary fresh-per-attempt protocol. A serial three-request
        # server would have different adaptive-cache and prefill history.
        path.mkdir(parents=True)
        results=[]
        for rep in [1,2,3]:
            if stopping:raise KeyboardInterrupt('Owned reproduction interrupted')
            with LaunchSession(variant_dir,cfg,path/f'rep{rep}',arg.profile,port=arg.port,host=arg.host,console=True) as session:
                warm=session.request('warmup','warmup','warmup',C/'inputs/manifest.json')
                assert warm['state']=='VALID' and warm['actual_output_tokens']==64
                if stopping:raise KeyboardInterrupt('Owned reproduction stopped after warmup')
                r=session.request(f'{arg.profile}-run{rep}','run','measured',C/'inputs/manifest.json')
                results.append(r)
                save(path/f'rep{rep}/results.json',{'runs':[r],'warmup':warm,'protocol':'fresh server for this measured attempt'})
                save(path/'results.json',{'runs':results,'protocol':'fresh server per attempt, identical4096-input/64-output warmup, serial, no retries'})
                assert r['state']=='VALID',r
        return
    with LaunchSession(variant_dir,cfg,path,arg.profile,port=arg.port,host=arg.host,console=not arg.smoke) as session:
        print('HTTP',f'http://{arg.host}:{arg.port}','LOGS',str(path/'logs'),flush=True)
        if arg.smoke:
            result=session.request('warmup','smoke','warmup',C/'inputs/manifest.json')
            assert result['state']=='VALID' and result['actual_output_tokens']==64 and result['actual_engine_input_verified'] and result['reuse']==0,result
            save(path/'smoke.json',{'PASS':True,'result':result,'native_identity':load(path/'raw/native-process.json')})
            print('ADVERTISED_LAUNCH_SMOKE_PASS',arg.variant,arg.profile,str(path),flush=True);return
        from record_ui_metrics import MonitorRecorder
        recorder=MonitorRecorder(session.url,path/'telemetry/ui-monitor',session.proc.pid,session.created,path/'config.json').start()
        print('UI_MONITOR_LOGS',path/'telemetry/ui-monitor',flush=True)
        try:
            while not stopping and session.proc.poll() is None:
                if psutil.virtual_memory().available<12*1024**3:raise RuntimeError('RAM_ABORT')
                time.sleep(1)
        finally:recorder.close()

if __name__=='__main__':main()
