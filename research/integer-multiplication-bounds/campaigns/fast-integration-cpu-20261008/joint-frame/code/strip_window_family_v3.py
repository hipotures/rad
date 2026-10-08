#!/usr/bin/env python3
"""New longer skip windows on the public PR55/57/58 joint-frame architecture.

Credit: Rohan Gupta (Claude assistance), eumemic (Codex assistance), Chafik
Boukhalfa (Codex assistance), and the pinned predecessor notices. This file
authors longer/hybrid windows; it does not claim the imported compiler.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import time


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def controller(first, second):
    a, b = first['h'], second['h']
    assert (a,b) == (23,25)
    m, N = a*b, comb(a,3)*comb(b,3)
    widths, banks, loss = Counter(), [], 0
    for row in (first,second):
        h, copies = row['h'], N//row['v']
        # Serialized joint-frame profiles ALREADY include copied centres.
        assert sum(t*n for t,n in enumerate(row['blocks'])) == h*row['R']+row['loss']
        assert row['loss'] == h*(h-1) and not row['crt_disagreements']
        widths.update({t:n*copies for t,n in enumerate(row['blocks']) if t and n})
        bank = copies*row['R']; banks.append(bank); loss += copies*row['loss']
        widths.update({h:bank,m-2*h:bank})
        widths.update({1:2*N,h-2:2*N})
    widths.update({1:18*N,21:2*N,17:2*N,481:2*N})
    widths[1] += N
    W = 2*N+sum(banks)
    rank = sum(t*n for t,n in widths.items())
    assert rank == m*W-N+loss
    return dict(m=m,N=N,W=W,banks=banks,total_rank=rank,deficit=N-loss,
                maxchild=max(widths),child_multiplicities=dict(widths))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--dimension',required=True,type=int,choices=(23,25))
    ap.add_argument('--config',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--retired-policy',choices=('original','high-rank','low-rank'),default='original')
    args = ap.parse_args()
    assert not sys.flags.optimize
    source = args.source_root.resolve()
    sys.path.insert(0,str(source/'scripts/experiments'))
    import joint_dual_compiler as joint
    import binary_frame_compiler as compiler
    from binary_frame_profile_prepare import prepare
    producer = joint.producer
    compiler_source=(source/'scripts/experiments/binary_frame_compiler.py').read_text()
    if args.retired_policy!='original':
        marker='for s in sorted(retired):'
        assert compiler_source.count(marker)==1
        sign='-' if args.retired_policy=='high-rank' else ''
        compiler_source=compiler_source.replace(marker,'for s in sorted(retired,key=lambda s: ('+sign+"blocks[frames[s]]['rank'],s)):")
        exec(compile(compiler_source,str(source/'scripts/experiments/binary_frame_compiler.py'),'exec'),compiler.__dict__)
    original = producer.skip_suffix
    campaign = Path(__file__).resolve().parents[2]
    scorer = load(campaign/'agents/scout/code/fixed_controller_score.py','cpu_joint_moment')
    search = load(campaign/'code/fixed_moment_family.py','cpu_joint_search')
    baseline = json.loads((source/'certificates/joint-dual-kappa.json').read_text())
    families = json.loads(args.config.read_text())
    args.output.mkdir(parents=True,exist_ok=False)
    protocol = dict(source_commit='bc2f7ed4c20dc18898305ab17165c0c995cbb804',
                    dimension=args.dimension,families=families,retired_policy=args.retired_policy,
                    compiled_source_sha256=hashlib.sha256(compiler_source.encode()).hexdigest(),
                    source=Path(__file__).read_text(),
                    source_certificate_sha256=hashlib.sha256((source/'certificates/joint-dual-kappa.json').read_bytes()).hexdigest(),
                    scope='New longer/hybrid scalar strips; every XOR/dirty basis/frame charged. Finite results require independent mechanism and all-size review.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    binary = args.output/'profiles'
    subprocess.run(['c++','-O3','-std=c++17','-I',str(source/'references/frame-compiler/pr48/scripts/partial_swap'),
                    str(source/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(binary)],check=True)
    seen_dags = {}
    for index, config in enumerate(families):
        started = time.time(); radius = config['radius']; association = config['association']
        assert radius >= 3 and association in ('left','right','balanced')
        def layout(c, vals):
            if config['scope'] == 'top' and getattr(c,'_level',0) != 0:
                return original(c,vals)
            k = len(vals)
            if k not in config.get('target_lengths', list(range(3,26))):
                return original(c,vals)
            if k <= 2:
                return producer.prefix_suffix(c,vals)
            v = [0]+list(vals); A = [0]*(k+1); B = [0]*(k+2)
            for i in range(1,k): A[i] = c.add(A[i-1],v[i])
            for i in range(k,1,-1): B[i] = c.add(v[i],B[i+1])
            def combine(values):
                values = [x for x in values if x]
                if association == 'balanced' and len(values)>1:
                    cut = len(values)//2
                    return c.add(combine(values[:cut]),combine(values[cut:]))
                if association == 'right': values = values[::-1]
                result = 0
                for x in values: result = c.add(result,x)
                return result
            out = []
            for j in range(1,k):
                selected = j % config.get('index_period',1) == config.get('index_residue',0)
                local_radius = radius if selected else 2
                stop = min(k+1,j+local_radius)
                left = combine([A[j-1]]+v[j+1:stop])
                out.append(c.add(left,B[stop]))
            out.append(A[k-1])
            return c.add(A[k-1],v[k]),out
        producer.skip_suffix = layout
        c = producer.graph(args.dimension)
        scalar, frames = c.verify(), c.verify_frames()
        dag_payload = dict(args=[(n,c.args[n]) for n in sorted(c.active)],
                           outputs=sorted(c.outputs.items()), core=c.core, union=c.union)
        dag_hash = hashlib.sha256(json.dumps(dag_payload,separators=(',',':')).encode()).hexdigest()
        if dag_hash in seen_dags:
            receipt = dict(status='EXACT DUPLICATE DAG; no repeated compilation',config=config,
                           same_as_case=seen_dags[dag_hash],dag_sha256=dag_hash,scalar=scalar)
            directory=args.output/('case%02d'%index); directory.mkdir()
            (directory/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print(json.dumps(receipt),flush=True)
            producer.SharedPointCircuit.support_in.cache_clear()
            continue
        seen_dags[dag_hash]=index
        compiler.graph = producer.graph
        compiled, word = compiler.compile_(args.dimension,matching=True,reclaim=True,dirty=True)
        directory = args.output/('case%02d'%index); directory.mkdir()
        word_path = directory/'word.json'
        word_path.write_text(json.dumps(word,separators=(',',':'))+'\n')
        transition_path = directory/'transitions.bin'
        transitions = prepare(word_path,transition_path)
        subprocess.run([str(binary),str(transition_path)],check=True,capture_output=True,text=True)
        profile = json.loads(Path(str(transition_path)+'.profiles.json').read_text())
        partner = baseline['bit']['axes'][1 if args.dimension==23 else 0]
        counts = controller(profile,partner) if args.dimension==23 else controller(partner,profile)
        exact = search.safe_search(scorer,counts)
        full_xors = 4*len(word['ops'])+2*len(word['scatter'])+2*len(word['sources'])
        result = dict(status='FINITE PASS; independent mechanism/transfer review pending',
                      config=config,dag_sha256=dag_hash,scalar=scalar,ordinary_frame_check=frames,
                      compiled=compiled,transitions=transitions,fixed_profile=profile,
                      complete_controller=counts,full_wrapped_xors=full_xors,
                      word_sha256=hashlib.sha256(word_path.read_bytes()).hexdigest(),
                      elapsed_seconds=time.time()-started,**exact)
        (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(event='new_strip_window_complete',h=args.dimension,config=config,
                              R=profile['R'],W=counts['W'],saving=exact['safe_saving'],
                              full_wrapped_xors=full_xors,seconds=result['elapsed_seconds'])),flush=True)
        producer.SharedPointCircuit.support_in.cache_clear()
    producer.skip_suffix = original


if __name__ == '__main__':
    main()
