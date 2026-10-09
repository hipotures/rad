#!/usr/bin/env python3
"""Regenerate and verify the fixed source168/170 paired lifetime fixture.

No frame or lifetime optimization is run. Sources, authored code and
decompressed fixtures are hash-gated before external imports. Deterministic
carrier compilation is rerun and checked against the exact saved arcs; this
also preserves its frame-interning order. The scalar graph, rational frames,
gauges and partner chronology are regenerated; changed frames and aliases receive complete finite
and all-variable F2 replay, independent rank/prime witnesses, paid fallback and
stopped moment checks. Final complex/transfer assembly is a separate gate.
Prepared for RaD with OpenAI assistance; inherited Apache-2.0 source retained.
"""
import argparse
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode=True


def need(ok,msg):
    if not ok:raise ValueError(msg)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(fixture,manifest,name):
    rec=manifest['fixtures'][name];path=fixture/rec['path']
    need(sha(path)==rec['gzip_sha256'],'compressed fixture pin '+name)
    data=gzip.decompress(path.read_bytes())
    need(len(data)==rec['bytes'] and hashlib.sha256(data).hexdigest()==rec['sha256'],
         'decompressed fixture pin '+name)
    return data


def main():
    need(not sys.flags.optimize,'assertions enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source168',type=Path,required=True)
    ap.add_argument('--source170',type=Path,required=True)
    ap.add_argument('--fixture',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();need(not args.output.exists(),'fresh output required');args.output.mkdir(parents=True)
    started=time.monotonic();s168=args.source168.resolve();s170=args.source170.resolve();fixture=args.fixture.resolve()
    manifest=json.loads((fixture/'fixture-manifest.json').read_text())
    inputs=json.loads((fixture/'source-inputs.json').read_text())
    for key,root in [('source168',s168),('source170',s170)]:
        for name,rec in inputs[key]['files'].items():
            need((root/name).stat().st_size==rec['bytes'] and sha(root/name)==rec['sha256'],
                 'external source pin '+key+'/'+name)
    for name,rec in manifest['code'].items():
        need(sha(fixture/name)==rec['sha256'],'authored code pin '+name)
    raw={name:unpack(fixture,manifest,name) for name in manifest['fixtures']}
    from bit_168_lifetime_integration import load,merged_graph,SPECS
    from audit_bit_projectors import audit
    gen=load('immutable168_generator',s168/'research/paired-cube-bit/paired_cube_bit_word.py')
    graph,merge=merged_graph(gen,SPECS,json.loads(raw['allbutone.json']))
    frozen=json.loads(raw['arcs.json'])
    # The source compiler interns extra join frames while building its matching
    # adjacency. Skipping that stage with frozen arcs preserves the spaces but
    # renumbers exported frame IDs. Replay deterministic compilation and bind
    # its complete arc set to the supplied fixed witness before export.
    counts,witness=gen.compile_word(graph,frozen=None,plain_k=8)
    actual_arcs=sorted([x-1,witness['usecode'][u]] for x,u in witness['arcs'].items())
    need(actual_arcs==sorted(frozen),'exact deterministic carrier arcs equal frozen witness')
    gauges,H,Y,word=gen.select_gauges(graph,counts,witness)
    row=gen.profile(counts,gauges,H,Y)
    exports=gen.export(12,graph,counts,witness,word,row);exports['profile']=row
    baseline=args.output/'exports';baseline.mkdir()
    for name,value in exports.items():
        encoded=gen.dumps(value).encode();filename=name+'_p12.json'
        need(hashlib.sha256(encoded).hexdigest()==manifest['exports'][filename]['sha256'],
             'fresh scalar/frame/chronology regeneration '+filename)
        (baseline/filename).write_bytes(encoded)
    print(json.dumps(dict(stage='fixed graph/arcs/frames/gauges regenerated',seconds=time.monotonic()-started,
                         R=row['R'],W=row['W_per_vertex'])),flush=True)
    sys.path.insert(0,str(s170/'research/paired-cube-bit'))
    lifetime=load('retained170_lifetime',s170/'research/paired-cube-lifetime/bit.py')
    experiment=lifetime.Experiment(baseline=baseline,p=12,quiet=True)
    plan=args.output/'frozen-plan.json';plan.write_bytes(raw['frames.json'])
    experiment.load(plan,require_pins=True)
    profile=experiment.verified_profile(replay=True,controls=True)
    expected=json.loads(raw['profile.json'])
    # Numerical roots are discovery diagnostics and are not proof inputs.
    comparable=lambda value:{k:v for k,v in value.items() if k!='numerical_root'}
    need(comparable(profile)==comparable(expected),'complete finite physical profile exact equality')
    primes=audit(experiment)
    parameters=load('retained170_native_arithmetic',s170/'research/paired-cube-lifetime/parameters.py')
    moment=parameters.select_supplier(parameters.counts(profile),bit=True)
    atom=parameters.choose_atom(moment['saving'])
    need(str(moment['saving'])==manifest['coarse_saving'],'exact paid native grid endpoint')
    need(str(atom['effective_saving'])==manifest['ordinary_saving'],'exact paid atom supplier')
    result=dict(status='PASS_SOURCE_BOUND_FINITE',candidate_id=manifest['candidate_id'],
                verified_utc=datetime.now(timezone.utc).isoformat(),profile=profile,
                prime_receipt={k:v for k,v in primes.items() if k!='frame_witnesses'},
                native_moment=moment,paid_atom=atom,merge=merge,
                plan_sha256=hashlib.sha256(raw['frames.json']).hexdigest(),
                profile_sha256=hashlib.sha256(raw['profile.json']).hexdigest(),
                fixture_manifest_sha256=sha(fixture/'fixture-manifest.json'),source_inputs_sha256=sha(fixture/'source-inputs.json'),
                source_fingerprints_verified=True,authored_code_fingerprints_verified=True,
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                inherited_contracts=['weighted local-ring uniform compiler','proper projector atom adapters',
                                     'ordinary wrapper restoration','compensated physical birth','completed-core sharing'],
                exclusions=['independent reflected chronological replay','full complex/precision/transfer/row-stock assembly',
                            'accepted final multiplication kappa'])
    for name,value in [('receipt.json',result),('prime-witnesses.json',primes),('profile.json',profile),
                       ('moment.json',moment)]:
        (args.output/name).write_text(json.dumps(parameters.js(value),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],coarse=str(moment['saving']),ordinary=str(atom['effective_saving']),
                         physical_R=profile['physical_R'],W=profile['W_per_vertex'],
                         prime_frames=primes['actual_used_frames'],seconds=result['wall_seconds'])),flush=True)


if __name__=='__main__':main()
