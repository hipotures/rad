#!/usr/bin/env python3
"""Source-build replay on freshly source-recovered DAG and actual positive labels."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,time
from run_positive_profiles import run


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dag',type=Path,required=True);p.add_argument('--expected',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',default='g++')
    p.add_argument('--matcher-source',type=Path);p.add_argument('--profiler-source',type=Path);a=p.parse_args()
    assert not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True);start=time.monotonic();code=Path(__file__).parent
    expected=json.loads(a.expected.read_text());producer=expected['producer'];labels=Path(str(a.dag)+'.positive')
    assert sha256(a.dag.read_bytes()).hexdigest()==producer['dag_sha256']
    assert sha256(labels.read_bytes()).hexdigest()==producer['positive_sha256']
    basis=expected['fixed_profile']['basis'];config=expected['configuration']
    matcher_name=Path(expected['weighted_provenance']['matcher_command'][0]).name
    matcher_source=a.matcher_source or code/(matcher_name+'.cpp')
    profile_source=a.profiler_source or code/('positive_transpose_profiles.cpp' if basis.endswith('-transpose') else 'parameter_positive_profiles.cpp' if basis.startswith('beta:') else 'positive_frame_profiles.cpp')
    assert matcher_source.exists() and profile_source.exists()
    assert sha256(matcher_source.read_bytes()).hexdigest()==expected['weighted_provenance']['matcher_source_sha256']
    assert sha256(profile_source.read_bytes()).hexdigest()==expected['provenance']['authored_source_sha256']
    commands=[]
    for source,name in [(matcher_source,'matcher'),(profile_source,'profiler')]:
        command=[a.compiler,'-O3','-std=c++17',str(source),'-o',str(a.work/name)];commands.append(command)
        subprocess.run(command,check=True)
    command=[str(a.work/'matcher'),str(a.dag),str(labels),basis,str(config['seed']),str(config['mode']),str(a.work/'weighted')];commands.append(command)
    with (a.work/'discovery.json').open('wb') as out,(a.work/'matcher.log').open('wb') as err:
        child=subprocess.Popen(command,stdout=out,stderr=err)
        (a.work/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command),indent=2)+'\n');assert child.wait()==0
    selected=json.loads((a.work/'weighted.uses.json').read_text());assert selected==expected['selected_links']
    copied=(json.dumps(selected)+'\n').encode();assert sha256(copied).hexdigest()==producer['witness_sha256']
    fresh=dict(producer);fresh.update(json.loads((a.work/'discovery.json').read_text()));fresh.update(dag_path=str(a.dag),witness_path=str(a.work/'weighted.uses.json'),witness_sha256=sha256((a.work/'weighted.uses.json').read_bytes()).hexdigest())
    input_file=a.work/'input.json';input_file.write_text(json.dumps(dict(producer=fresh))+'\n')
    profile_file=a.work/'rebuilt-witness.json';run(input_file,a.work/'profiler',basis,a.work/'physical-profile',profile_file,authored_source=profile_source)
    rebuilt=json.loads(profile_file.read_text());assert rebuilt['fixed_profile']['blocks']==expected['fixed_profile']['blocks']
    assert rebuilt['copied_blocks']==expected['copied_blocks'];assert rebuilt['producer']['histogram']==producer['histogram']
    check=code.parent.parent/'graph/code/check_compiled_witness.py';compiled=a.work/'literal-compiled.json'
    command=['python3',str(check),'--witness',str(profile_file),'--output',str(compiled)];commands.append(command);subprocess.run(command,check=True)
    audit=json.loads(compiled.read_text());assert audit['rows'][0]['roles']==producer['R']
    result=dict(status='PASS FRESH SOURCE BUILD, EXACT WEIGHTED MAP HASH, ALL CRT CHILD COUNTS AND LITERAL POSITIVE COMPILER',h=producer['h'],R=producer['R'],basis=basis,seed=config['seed'],mode=config['mode'],
                source_only_input='Fresh graph source-recovery DAG and positive labels; dependency source/fixture stages are recorded by sibling graph recovery',
                expected_witness=str(a.expected),expected_witness_sha256=sha256(a.expected.read_bytes()).hexdigest(),
                scalar_dag_sha256=producer['dag_sha256'],positive_labels_sha256=producer['positive_sha256'],selected_map_sha256=producer['witness_sha256'],
                compiler_version=subprocess.check_output([a.compiler,'--version'],text=True).splitlines()[0],commands=commands,
                source_sha256={str(source):sha256(source.read_bytes()).hexdigest() for source in [Path(__file__),matcher_source,profile_source,code/'binary_io.hpp']},
                literal_compiler_receipt=str(compiled),literal_compiler_sha256=sha256(compiled.read_bytes()).hexdigest(),
                elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','h','R','elapsed_seconds')}),flush=True)
