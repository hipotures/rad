"""Exercise every advertised script through real startup, health and64-token output."""
from campaign import C,load,save,guard
from pathlib import Path
import subprocess,time,datetime

def main():
    assert load(C/'phase-c/matrix-exit.json')['exit_code']==0,'No launcher tests during headline matrix'
    records=[]
    for variant in ['control','history-v2','early-v1']:
        for profile in ['32k','128k','256k']:
            guard();out=C/'analysis/launcher-smokes'/variant/profile
            if (out/'result.json').exists():records.append(load(out/'result.json'));continue
            assert not out.exists(),'Retain failure; repair launcher explicitly'
            out.mkdir(parents=True);host='0.0.0.0' if variant=='early-v1' and profile=='128k' else '127.0.0.1'
            cmd=[str(C/'launchers'/variant/f'start-{profile}.sh'),'--smoke','--host',host,'--port','18140']
            before={str(p) for p in (C/'manual'/variant).glob('*')} if (C/'manual'/variant).exists() else set()
            start=time.time()
            with (out/'launcher.log').open('x') as log:
                completed=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=1020)
            after={str(p) for p in (C/'manual'/variant).glob('*')};new=after-before
            record={'variant':variant,'profile':profile,'command':cmd,'exit_code':completed.returncode,'wall_s':time.time()-start,'attempts':sorted(new),'log':str(out/'launcher.log')}
            save(out/'result.json',record)
            assert completed.returncode==0,record
            assert len(new)==1 and load(Path(next(iter(new)))/'smoke.json')['PASS'],record
            assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'Launcher leftGPU process'
            records.append(record);print('LAUNCH_PATH_PASS',variant,profile,flush=True)
    save(C/'phase-c/advertised-launch-smokes.json',{'state':'PASS','paths':records,'count':len(records),'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual advertised start scripts; health/current native identity/config and fixed64 output, explicit wildcard override onearly128K. All stopped; no production/user launcher changed.'})

if __name__=='__main__':main()
