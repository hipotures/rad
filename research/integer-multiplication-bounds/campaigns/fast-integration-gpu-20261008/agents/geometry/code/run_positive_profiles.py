#!/usr/bin/env python3
"""Fresh actual positive labels and complete fixed-basis physical-profile run."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,math,os,shutil,struct,subprocess,time


def run(witness,binary,basis,work,output):
    assert not work.exists() and not output.exists();work.mkdir(parents=True)
    original=json.loads(witness.read_text())
    if 'rows' in original:
        assert len(original['rows'])==1;original=original['rows'][0]
    source=original.get('producer',original);dag=Path(source['dag_path'])
    labels=Path(str(dag)+'.positive');usefile=Path(source['witness_path'])
    for path,key in [(dag,'dag_sha256'),(labels,'positive_sha256'),(usefile,'witness_sha256')]:
        assert sha256(path.read_bytes()).hexdigest()==source[key]
    local=work/'dag.bin';shutil.copy2(dag,local);shutil.copy2(labels,Path(str(local)+'.positive'))
    links=json.loads(usefile.read_text());assert links['h']==source['h'];assert len(links['links'])==source['matched']
    selected=work/'selected-uses.bin';selected.write_bytes(struct.pack('<2I',links['n'],len(links['links']))+b''.join(struct.pack('<2I',*row) for row in links['links']))
    selected_json=work/'selected-uses.json';selected_json.write_text(json.dumps(links)+'\n')
    native=work/'physical-profiles.json';audit=work/'transition-audit.json'
    command=[str(binary),str(local),str(selected),basis,str(native),str(audit)]
    environment=os.environ.copy()
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:environment[key]='1'
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    with (work/'native.log').open('wb') as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=environment)
        (work/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=started),indent=2)+'\n')
        print(json.dumps(dict(status='RUNNING',pid=child.pid,command=command)),flush=True)
        exit_code=child.wait()
    completion=dict(exit_code=exit_code,elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat())
    (work/'completion.json').write_text(json.dumps(completion,indent=2)+'\n')
    assert exit_code==0,completion
    result=json.loads(native.read_text())
    for key in ['h','v','R','matched','loss']:assert result[key]==source[key]
    assert result['rank_histogram']==source['histogram']
    assert result['rank_sum']==source['rank_sum']
    h=result['h'];copied=result['blocks'][:];copied[1]+=h;copied[h]-=h
    assert min(copied)>=0 and sum(t*n for t,n in enumerate(copied))==h*source['R']+source['loss']
    producer=dict(source,dag_path=str(local),witness_path=str(selected_json),witness_sha256=sha256(selected_json.read_bytes()).hexdigest())
    alpha=4e-5;phi=sum(n*t*math.expm1(alpha*math.log(575/t)) for t,n in enumerate(copied) if t and n)
    retained=dict(status='Exact actual positive-frame local profiles; full multiplication assembly is separate',producer=producer,
                  fixed_profile=result,selected_links=links,configuration=dict(basis='I-4/[3(h+3)]J' if basis=='negative' else 'I+J',
                  frame_family='actual signed positive labels',matching='retained positive selected-use map'),
                  copied_blocks=copied,local_phi=dict(alpha=alpha,value=phi),completion=completion,
                  provenance=dict(input_witness=str(witness),input_sha256=sha256(witness.read_bytes()).hexdigest(),
                  native_command=command,binary_sha256=sha256(binary.read_bytes()).hexdigest(),
                  authored_source_sha256=sha256(Path(__file__).with_name('positive_frame_profiles.cpp').read_bytes()).hexdigest(),
                  transition_audit=str(audit),transition_audit_sha256=sha256(audit.read_bytes()).hexdigest()),
                  retained_utc=datetime.now(timezone.utc).isoformat())
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(retained,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',h=h,R=source['R'],basis=basis,local_phi=phi,**completion)),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--witness',type=Path,required=True);ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--basis',choices=['negative','fixed'],required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();run(a.witness,a.binary,a.basis,a.work,a.output)
