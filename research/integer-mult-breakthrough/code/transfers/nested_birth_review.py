#!/usr/bin/env python3
"""Independent physical and retained-fixture review of strict nested births.

Uses only independent Gaussian/frame primitives. The scalar role remains dirty
across the two births, with its actual cut response paid in the larger frame.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import degenerate_birth_review as base
import degenerate_birth_fixture_review as binding
g=base.g


TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/nested-birth-review.json'


def word(reuse,frames):
    stock=7 if reuse else 8;current=['A1','A7']+['I']*(stock-2)
    operations=[];histogram=Counter();adapters={}
    def move(role,destination):
        before=current[role]
        if before==destination:return
        key=before+'->'+destination
        if key not in adapters:
            matrix=g.matmul(frames[destination],g.adjoint(frames[before]))
            adapters[key]=(matrix,base.normal_form(matrix))
        operations.append(('move',role,key));histogram[adapters[key][1]['selected_rank_per_column']]+=1
        current[role]=destination
    def add(a,b,c,category='scalar'):
        if current[a]!=current[b]:raise ValueError('Unequal actual frames at a scalar gate')
        operations.append(('add',a,b,Q(c),category))
    def cut(role,response,index):
        if any(c and current[2+j]!=current[role] for j,c in enumerate(response)):
            raise ValueError('A cut read is not in the actual birth frame')
        operations.append(('cut',role,tuple(response),index))
    cut(4,(1,2),0);cut(5,(1,3),1)
    move(4,'A1');add(4,0,1,'source');move(5,'A7');add(5,1,1,'source')
    for role in (2,3,4,5):move(role,'E')
    move(6,'E');cut(6,(1,0),2);add(6,4,1,'workspace');add(6,5,1,'workspace');add(2,6,1)
    # First sink is retired. The continuing sink, operands and reused donor
    # now share the strictly larger actual kernel14 frame, not a free gauge.
    move(2,'K8');move(3,'K14');move(4,'K14');move(5,'K14')
    second=6 if reuse else 7
    move(second,'K14');cut(second,(0,1),3)
    add(second,4,2,'workspace');add(second,5,3,'workspace');add(3,second,1)
    for role in list(range(2))+list(range(4,stock)):move(role,'F')
    add(second,5,-3,'undo-workspace');add(second,4,-2,'undo-workspace')
    add(6,5,-1,'undo-workspace');add(6,4,-1,'undo-workspace')
    add(5,1,-1,'undo-source');add(4,0,-1,'undo-source')
    return dict(stock=stock,initial=['A1','A7']+['I']*(stock-2),final=current,
        operations=operations,histogram=dict(sorted(histogram.items())),adapters=adapters,reuse=reuse)


def bind(case,spec,frames):
    if case['donor_subspace']!=[1,6] or case['recipient_subspace']!=[1,6,10]:
        raise ValueError('Retained donor/recipient subspaces differ')
    if case['payload_stock']!=spec['stock'] or [binding.FRAME_NAMES[x] for x in case['initial_frame_ids']]!=spec['initial']:
        raise ValueError('Complete initial stock/phase anchors differ')
    if [binding.FRAME_NAMES[x] for x in case['final_frame_ids']]!=spec['final']:
        raise ValueError('Complete final source/sink/dirty anchors differ')
    for frame in case['frames']:
        if frame['subspace']!=binding.SOURCE_SUBSPACES[frame['id']]:raise ValueError('Frame subspace changed')
        if binding.matrix_digest(frames[binding.FRAME_NAMES[frame['id']]],frame['matrix_bits'])!=frame['matrix_sha256']:
            raise ValueError('Independent frame matrix differs from retained hash')
    transitions={};globals_rejected=offsets_rejected=False
    for transition in case['transitions']:
        before,after=(binding.FRAME_NAMES[transition[key]] for key in ['from_frame','to_frame'])
        actual=g.matmul(frames[after],g.adjoint(frames[before]));form=transition['one_child_normal_form']
        retained=binding.reconstruct(form);inverse=transition['execute_rising_normal_form_inverse']
        if (g.adjoint(retained) if inverse else retained)!=actual:raise ValueError('Retained child adapter differs from independent literal matrix')
        if binding.matrix_digest(g.adjoint(actual) if inverse else actual,transition['rising_matrix_bits'])!=transition['rising_matrix_sha256']:
            raise ValueError('Independent rising matrix differs from retained coefficient hash')
        if form['output_affine_offset']:
            offsets_rejected|=binding.reconstruct(form,'omit affine offset')!=retained
        if sum(form[side+'_quadratic']['constant'] for side in ['input','output'])%4:
            globals_rejected|=binding.reconstruct(form,'omit global phase')!=retained
        transitions[transition['id']]=before+'->'+after
    events=[]
    for event in case['physical_events']:
        if event[0]=='move':events.append(('move',event[1],transitions[event[2]]))
        elif event[0]=='add':events.append(('add',event[1],event[2],Q(*event[3])))
        else:events.append(('cut',event[1],tuple(event[3]),{0:0,1:1,4:2,8:3}[event[2]]))
    independent=[op[:-1] if op[0]=='add' else op for op in spec['operations']]
    if events!=independent or not globals_rejected or not offsets_rejected:
        raise ValueError('Retained physical word or affine/global negative differs')
    if {int(t):n for t,n in case['child_width_histogram'].items()}!=spec['histogram']:
        raise ValueError('Complete retained histogram differs')
    return dict(retained_transition_coefficients=256*len(transitions),actual_event_sequence_matched=True,
        global_phase_and_affine_negatives_rejected=True)


def review(payload):
    case,columns=payload;reuse=case['reuse'];frames=base.literal_frames();spec=word(reuse,frames);receipt=bind(case,spec,frames)
    stock,size=spec['stock'],1<<(4*columns);checked=dependent=0;digest=sha256()
    for bank in range(stock):
        for address in range(size) if columns==1 else (0,):
            data=[[g.ZERO]*size for _ in range(stock)];data[bank][address]=g.ONE
            actual,birth=base.replay(spec,data,columns)
            if actual!=base.expected(spec,data,columns,frames):raise ValueError('A complete physical initial column failed')
            if bank<2 and birth:dependent+=1
            digest.update(str(actual).encode());checked+=1
    for field in range(3):
        data=[[(Q((a*7+bank*11+field*3)%31-15,1<<(bank%3)),
                Q((a*13+bank*5+field*17)%29-14,1<<((bank+field)%4))) for a in range(size)] for bank in range(stock)]
        actual,_=base.replay(spec,data,columns);wanted=base.expected(spec,data,columns,frames)
        if actual!=wanted:raise ValueError('A complete arbitrary-dirty Gaussian field failed')
        digest.update(str(actual).encode())
    negatives=['group negative sources before undo']+(['omit reuse response','omit later birth cut'] if reuse else [])
    controls={negative:base.replay(spec,data,columns,negative)[0]!=wanted for negative in negatives}
    if not all(controls.values()) or reuse and not dependent:raise ValueError('A source-dependent CUT/inverse negative failed')
    if all(wanted[bank]==data[bank] for bank in range(4,stock)):raise ValueError('Wrong raw identity dirty endpoint was not rejected')
    expected_hist={1:12,2:3,3:2} if reuse else {1:11,2:4,3:3}
    rank=sum(t*n for t,n in spec['histogram'].items())
    if spec['histogram']!=expected_hist or rank!=4*stock-4:raise ValueError('Paid full stock/rank differs')
    return dict(reuse=reuse,columns=columns,stock=stock,rank_per_column=rank,complete_child_histogram=spec['histogram'],
        deficit=4,donor_dimension=2,recipient_dimension=3,donor_radical=[6],
        explicit_physical_columns=checked,full_f1_column_coverage=columns==1,full_dirty_fields=3,
        source_dependent_reuse_births=dependent,arbitrary_virtual_dirty_restored=True,
        actual_dirty_endpoint='C_full times original dirty',negative_controls=controls,
        retained_fixture_binding=receipt,output_sha256=digest.hexdigest())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());fixture=TOPIC/config['fixture']
    paths=[Path(__file__).resolve(),CONFIG,fixture,Path(base.__file__).resolve(),Path(binding.__file__).resolve(),Path(g.__file__).resolve()]
    for path,digest in config['pinned_inputs'].items():
        if sha256((TOPIC/path).read_bytes()).hexdigest()!=digest:raise ValueError('Pinned fixture/independent helper changed')
    hashes={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    data=json.loads(fixture.read_text());cases=[(case,columns) for columns in ([1] if args.small else [1,2]) for case in data['cases']]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_fixture_sha256=hashes,
        seed=None,scope=config['scope'],producer_imports=False)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(review,cases))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest()!=digest for path,digest in hashes.items()):raise ValueError('Source changed during immutable attempt')
    result=dict(status='INDEPENDENT STRICT NESTED DIRTY BIRTH REVIEW PASS',cases=rows,seconds=time.monotonic()-started,
        scope=config['scope'],native_canonical_primitive=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
