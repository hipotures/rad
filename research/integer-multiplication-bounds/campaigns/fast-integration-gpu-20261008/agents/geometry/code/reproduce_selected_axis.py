#!/usr/bin/env python3
"""Portable complete fixed ORIGINAL E(C,M) selected-axis recovery.

The scalar DAG must first be recovered using the graph branch's recorded
construction. This script verifies its identity, freshly computes original
frames and matching, and checks actual fixed-basis matrix profiles. No external
source checkout or previously compiled local executable is required.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import os
import shlex
import shutil
import struct
import subprocess
import sys
import time
from original_envelope_labels import encode

HERE = Path(__file__).resolve().parent


def document(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path,'rt',encoding='utf-8') as stream:
        return json.load(stream)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dag',type=Path,required=True)
    ap.add_argument('--expected',type=Path,required=True,help='Retained selected axis JSON or its complete gzip copy')
    ap.add_argument('--work',type=Path,required=True,help='Fresh disposable directory')
    ap.add_argument('--compiler',default=os.environ.get('CXX','c++'))
    ap.add_argument('--compiled-checker',type=Path,help='Explicit graph/check_compiled_witness.py; defaults to the sibling retained source')
    ap.add_argument('--skip-compiled',action='store_true',help='Omit the separate compiler review; report that narrower scope')
    args = ap.parse_args()
    assert not args.work.exists(), 'Each recovery attempt needs fresh storage'
    expected = document(args.expected)
    config = expected['configuration']
    seed = config['seed']
    mode = config['mode']
    original = args.dag.resolve()
    assert sha256(original.read_bytes()).hexdigest() == expected['producer']['dag_sha256']
    h,v,n,q = struct.unpack_from('<4I',original.read_bytes())
    assert h == expected['producer']['h'] and h in (23,25)
    work = args.work.resolve()
    builds = work/'builds'
    derived = work/'derived'
    logs = work/'logs'
    for path in (builds,derived,logs):
        path.mkdir(parents=True)
    env = os.environ.copy()
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
        env[name] = '1'
    commands = []
    start = time.monotonic()

    def run(command,name):
        commands.append(command)
        with (logs/(name+'.stdout')).open('w') as out, (logs/(name+'.stderr')).open('w') as err:
            subprocess.run(command,check=True,env=env,stdout=out,stderr=err)

    for source,name in [('fixed_moment_match.cpp','matcher'),('fixed_selected_profiles.cpp','profiler')]:
        run([*shlex.split(args.compiler),'-O3','-std=c++17',str(HERE/source),'-o',str(builds/name)],'compile-'+name)
    dag = derived/'dag.bin'
    shutil.copy2(original,dag)
    prefix = derived/'weighted'
    run([str(builds/'matcher'),str(dag),str(seed),str(mode),str(prefix)],'matching')
    uses = derived/'exact-uses.json'
    run([str(builds/'profiler'),str(dag),str(derived/'exact-links.bin'),str(uses),str(prefix)+'.uses.bin'],'profiles')
    producer = document(logs/'profiles.stdout')
    profile = document(Path(str(dag)+'.round3_rankone_certified_profiles.json'))
    for key in ('h','v','c','q','matched','R','loss','rank_sum','histogram'):
        assert producer[key] == expected['producer'][key], 'Producer mismatch: '+key
    for key in ('h','v','R','loss','rank_sum','blocks','crt_disagreements'):
        assert profile[key] == expected['fixed_profile'][key], 'Physical profile mismatch: '+key
    assert document(uses)['links'] == expected['selected_links']['links'], 'Changed selected-use identities'
    labels = Path(str(dag)+'.positive')
    encode(dag,labels)
    producer.update(dag_path=str(dag),dag_sha256=sha256(dag.read_bytes()).hexdigest(),
                    positive_sha256=sha256(labels.read_bytes()).hexdigest(),
                    witness_path=str(uses),witness_sha256=sha256(uses.read_bytes()).hexdigest())
    retained = work/'axis.json'
    retained.write_text(json.dumps(dict(producer=producer,fixed_profile=profile,selected_links=document(uses),configuration=config),indent=2)+'\n')
    run([sys.executable,str(HERE/'independent_axis_review.py'),'--record',str(retained),'--output',str(work/'independent-axis-review.json')],'independent-axis')
    if not args.skip_compiled:
        checker = args.compiled_checker or HERE.parents[1]/'graph/code/check_compiled_witness.py'
        assert checker.is_file()
        run([sys.executable,str(checker),'--witness',str(retained),'--frame-source','original-envelope',
             '--output',str(work/'independent-compiled-review.json')],'independent-compiled')
    manifest = dict(status='PASS SELECTED ORIGINAL FIXED AXIS RECOVERY',h=h,v=v,n=n,q=q,roles=producer['R'],
                    seed=seed,mode=mode,elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat(),
                    commands=commands,input_sha256={str(original):expected['producer']['dag_sha256'],
                                                  str(args.expected):sha256(args.expected.read_bytes()).hexdigest()},
                    source_sha256={str(p.relative_to(HERE)):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),HERE/'fixed_moment_match.cpp',HERE/'fixed_selected_profiles.cpp',HERE/'binary_io.hpp',HERE/'original_envelope_labels.py',HERE/'independent_axis_review.py']},
                    complete_selected_uses_match=True,complete_physical_block_histogram_matches=True,
                    independently_compiled=not args.skip_compiled,
                    limitations=['Scalar DAG regeneration belongs to the separate graph recovery protocol',
                                 'Common ambient source/data geometry uses pinned public evidence',
                                 'Global recurrence and 47 assembly conditions are separate coordinator checks'])
    (work/'recovery-result.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('status','h','roles','seed','mode','elapsed_seconds','independently_compiled')}),flush=True)


if __name__ == '__main__':
    main()
