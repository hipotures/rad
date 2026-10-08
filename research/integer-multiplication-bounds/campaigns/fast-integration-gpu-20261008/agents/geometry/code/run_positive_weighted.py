#!/usr/bin/env python3
"""Actual positive-frame matrix-weighted matching followed by complete CRT profiles."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,math,os,subprocess,time
from run_positive_profiles import run


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--matcher',type=Path,required=True)
    ap.add_argument('--profiler',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,required=True);ap.add_argument('--live-output',type=Path)
    a=ap.parse_args();assert 1<=a.workers<=6 and not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True)
    configs=json.loads(a.input.read_text());start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    env=os.environ.copy()
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='1'
    def job(config):
        case=config['case_id'];work=a.work/case;work.mkdir();input_file=Path(config['witness']);original=json.loads(input_file.read_text());p=original['producer']
        command=[str(a.matcher),p['dag_path'],p['dag_path']+'.positive',config['basis'],str(config['seed']),str(config['mode']),str(work/'weighted')]
        with (work/'discovery.json').open('wb') as stdout,(work/'matcher.log').open('wb') as stderr:
            child=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=env)
            (work/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
            print(json.dumps(dict(status='MATCHER RUNNING',case_id=case,pid=child.pid,command=command)),flush=True)
            rc=child.wait()
        assert rc==0,dict(case_id=case,exit_code=rc)
        discovery=json.loads((work/'discovery.json').read_text());producer=dict(p);producer.update(discovery)
        uses=work/'weighted.uses.json';producer.update(witness_path=str(uses),witness_sha256=sha256(uses.read_bytes()).hexdigest())
        interim=work/'weighted-input.json';interim.write_text(json.dumps(dict(producer=producer,configuration=config))+'\n')
        profiled=work/'complete-profile.json';run(interim,a.profiler,config['basis'],work/'profile',profiled)
        retained=json.loads(profiled.read_text());retained['configuration'].update(matching='Actual positive physical matrix moments',seed=config['seed'],mode=config['mode'],
            lost_link_charge='Phi(h)+Phi(575-2h)',matching_discovery='One finite field; accepted profiles reconstructed with full bounded-minor CRT')
        if config['basis'].startswith('beta:'):
            retained['configuration']['data_status']='Changed rational-beta source family; requires its complete source-pair data certificate or proved conjugate transfer'
        retained['weighted_provenance']=dict(original_witness=str(input_file),original_witness_sha256=sha256(input_file.read_bytes()).hexdigest(),
             config=config,matcher_command=command,matcher_source_sha256=sha256(Path(__file__).with_name(a.matcher.name+'.cpp').read_bytes()).hexdigest(),
             matcher_binary_sha256=sha256(a.matcher.read_bytes()).hexdigest(),matcher_log=str(work/'matcher.log'),
             matcher_log_sha256=sha256((work/'matcher.log').read_bytes()).hexdigest(),baseline_local_phi=original['local_phi'])
        final=work/'retained-witness.json';final.write_text(json.dumps(retained,indent=2)+'\n')
        h=producer['h'];alpha=retained['local_phi']['alpha'];exterior=h*math.expm1(alpha*math.log(575/h))+(575-2*h)*math.expm1(alpha*math.log(575/(575-2*h)))
        value=retained['local_phi']['value'];baseline=original['local_phi']['value']+p['R']*exterior
        return dict(case_id=case,h=h,basis=config['basis'],seed=config['seed'],mode=config['mode'],R=producer['R'],local_phi=value,
                    complete_axis_phi=value+producer['R']*exterior,baseline_complete_axis_phi=baseline,improvement=baseline-value-producer['R']*exterior,
                    profile=retained['fixed_profile'],retained_witness=str(final),retained_witness_sha256=sha256(final.read_bytes()).hexdigest())
    rows=[];failures=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures={pool.submit(job,c):c for c in configs}
        for future in as_completed(futures):
            try:rows.append(future.result())
            except Exception as error:failures.append(dict(configuration=futures[future],error=repr(error)))
            status=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),failed=len(failures),total=len(configs),elapsed_seconds=time.monotonic()-start,workers=a.workers)
            (a.work/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
            if a.live_output:
                from refresh_geometry_status import refresh
                refresh(a.work,a.live_output,'Mapped-center profiles remain active; next actual source-specific side cleanup and rational-beta profiles')
    result=dict(status='COMPLETE' if not failures else 'COMPLETE WITH FAILURES',started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),
                elapsed_seconds=time.monotonic()-start,workers=a.workers,rows=rows,failures=failures,input=str(a.input),input_sha256=sha256(a.input.read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
