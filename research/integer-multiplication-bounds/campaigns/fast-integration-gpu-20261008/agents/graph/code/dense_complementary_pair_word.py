#!/usr/bin/env python3
"""Dense complementary pair synthesis with explicitly paid frame retirement.

The complementary source identity and pair matrix direction were proposed
by the campaign coordinator. Physical binary synthesis and paid reclamation
reuse eumemic's PR57 compiler in the pinned Avi Eisenberg PR62 snapshot.
Every downward terminal frame transfer is charged; no signal-aware projection
or accepted exponent is inferred from the reduced role count.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import inspect
from itertools import combinations
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

from check_compiled_witness import contained
import joint_region_search_v3 as region
from joint_linear_form_carriers import linear_rank
from joint_word_check_paid_decreases import check


def ordinary_frame(h, common):
    return (h-1,1<<common,tuple(1 if i==common else i+2 for i in range(h)))


def terminal_frame(h, common, triple):
    a,b = sorted(set(triple)-{common})
    symbols = [1 if i==common else i+2 for i in range(h)]
    symbols[a],symbols[b] = h+2,-(h+2)
    return h-2,1<<common,tuple(symbols)


def build(h):
    triples = list(combinations(range(h),3))
    v = len(triples)
    blocks,uses,value_uses,owner,signal,order = [],[],defaultdict(list),{},{},[]
    for i,triple in enumerate(triples,1):
        mask = sum(1<<j for j in triple)
        frame = (1,mask,tuple(int(mask>>j&1) for j in range(h)))
        blocks.append(dict(nodes=[i],frame=frame,inputs=[],uses=[],source=True,
                           rank=1,coeff={i:1},outvalues=[i],outbasis=[1],candidates=[],selected=set()))
        owner[i] = i-1
        signal[i] = 1<<(i-1)
        order.append(i-1)
    outputs, coefficient_receipts = {},[]
    value = v+1
    for common in range(h):
        inputs = [i+1 for i,t in enumerate(triples) if common in t]
        frame = ordinary_frame(h,common)
        g = len(blocks)
        coefficients, rows, nodes = {},[],[]
        pending = []
        for target in triples:
            if common not in target:
                continue
            omitted = set(target)-{common}
            row = sum(1<<i for i,x in enumerate(inputs) if not omitted.intersection(triples[x-1]))
            coefficients[value] = row
            nodes.append(value)
            rows.append(row)
            signal[value] = sum(1<<(inputs[i]-1) for i in range(len(inputs)) if row>>i&1)
            owner[value] = g
            outputs[common,target] = value
            pending.append((value,terminal_frame(h,common,target),common,target))
            value += 1
        full = (1<<len(inputs))-1
        coefficients[value] = full
        nodes.append(value)
        signal[value] = sum(1<<(x-1) for x in inputs)
        owner[value] = g
        outputs[common,(common,)] = value
        pending.append((value,frame,common,(common,)))
        value += 1
        blocks.append(dict(nodes=nodes,frame=frame,inputs=inputs,uses=[],source=False,
                           rank=h-1,coeff=coefficients,outvalues=nodes.copy(),
                           outbasis=region.COMPILER.basis(coefficients.values()),candidates=[],selected=set()))
        order.append(g)
        for source in inputs:
            u = len(uses)
            uses.append((source,g,None))
            value_uses[source].append(u)
            blocks[owner[source]]['uses'].append(u)
        for x, terminal, c, target in pending:
            if len(target)==1:
                sink = g
            else:
                sink = len(blocks)
                # A terminal address declaration, not a computation block.
                blocks.append(dict(nodes=[],frame=terminal,inputs=[],uses=[],source=False,
                                   rank=h-2,coeff={},outvalues=[],outbasis=[],candidates=[],selected=set()))
            assert contained(terminal,frame)
            u = len(uses)
            uses.append((x,sink,(c,target)))
            value_uses[x].append(u)
            blocks[g]['uses'].append(u)
        q = len(inputs)
        rank = linear_rank(rows)
        if (h-1)%2==0:
            for i,row in enumerate(rows):
                square = 0
                for j in range(q):
                    if row>>j&1:
                        square ^= rows[j]
                assert square == (1<<i)^(full if q%2 else 0)
            assert rank == q-(q%2)
            if q%2:
                assert linear_rank(rows+[full])==q
        coefficient_receipts.append(dict(common=common,q=q,ordinary_matrix_rank=rank,
                                         including_center_rank=linear_rank(rows+[full]),
                                         coefficient_sha256=sha256(json.dumps(rows).encode()).hexdigest(),
                                         exact_pair_square_identity_checked=(h-1)%2==0))
    for g,b in enumerate(blocks):
        if b['source']:
            assert len(b['uses'])==3
    circuit = SimpleNamespace(inputs=triples,outputs=outputs)
    return (circuit,blocks,uses,value_uses,owner,signal,order,contained),coefficient_receipts


def compile_paid(built,h):
    namespace = dict(region.COMPILER.__dict__)
    text = inspect.getsource(region.COMPILER.compile_)
    text = text.replace('baseline_pr48_roles={23:36432,25:48329}[h]',
                        'baseline_pr48_roles={23:36432,25:48329}.get(h)')
    text = text.replace("assert contains(blocks[old]['frame'],blocks[g]['frame']);hist[blocks[g]['rank']-blocks[old]['rank']]+=1", 
                        "assert contains(blocks[old]['frame'],blocks[g]['frame']) or contains(blocks[g]['frame'],blocks[old]['frame']);delta=blocks[g]['rank']-blocks[old]['rank'];stats['paid_rank_decreases']+=max(0,-delta);hist[abs(delta)]+=1")
    text = text.replace("assert mass==h*R+h*(h-1)","assert mass==h*R+h*(h-1)+2*stats['paid_rank_decreases']")
    namespace['build'] = lambda dimension:built
    exec(compile(text,'<dense-paid-decrease-compiler>','exec'),namespace)
    return namespace['compile_'](h,matching=True,reclaim=True,dirty=True)


def evaluate(h, work):
    started = time.monotonic()
    target = work/'raw'/f'h{h}-dense-paid-decrease'
    target.mkdir(parents=True,exist_ok=False)
    try:
        built,coefficients = build(h)
        compiled,word = compile_paid(built,h)
        word.update(frame_format='positive-signed-v1')
        raw = (json.dumps(word,separators=(',',':'))+'\n').encode()
        path = target/'word.json.gz'
        with path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as gz:
                gz.write(raw)
        independent = check(path,target/'signed-transitions.bin')
        if h in (23,25):
            assert word['R']==3*len(built[0].inputs)+h
            assert independent['paid_rank_decreases']==3*len(built[0].inputs)
        result = dict(status='DISCOVERY dense complementary word with fully charged nested decreases PASS',
                      case_id=f'h{h}-dense-paid-decrease',configuration=dict(h=h,mechanism='dense-complementary-pair-synthesis',retirement='paid-nested-decrease'),
                      compiled=compiled,independent=independent,coefficient_receipts=coefficients,
                      actual_compute_regions=len(built[6]),terminal_address_declarations=len(built[1])-len(built[6]),
                      word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                      extra_rank_charge=independent['extra_rank_charge'],
                      limitation='No free signal-aware retirement. Old source-pair rank deficit/recurrence cannot be reused after extra decreases; exact physical profile and changed full assembly required. Finite dirty replay is F2; inherited address realization remains conditional.')
    except Exception as error:
        import traceback
        traceback.print_exc()
        result = dict(status='failed',case_id=f'h{h}-dense-paid-decrease',h=h,error=repr(error))
    result.update(seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=result['case_id'],status=result['status'],R=result.get('compiled',{}).get('roles'),
                         extra_rank_charge=result.get('extra_rank_charge'),seconds=result['seconds'],error=result.get('error'))),flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--dimensions',nargs='+',type=int,default=[10,23,25])
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    region.initialize(args.source,args.work)
    result = dict(status='running',command=sys.argv,rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for h in args.dimensions:
        result['rows'].append(evaluate(h,args.work))
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
