#!/usr/bin/env python3
"""Retain literal joint-birth adapters and mutable final-source cleanup."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import joint_mutable_birth_swap as b


def coefficient(c):return [c.numerator,c.denominator]


def export():
    cases=[]
    for a,z in ((1,2),(2,1)):
        S=[[1,a],[z,1+a*z]];spec=b.bind(S);h=spec['h']
        frame_order=sorted(spec['frames'],key=lambda E:(len(E),E))
        frame_ids={E:'F'+str(i) for i,E in enumerate(frame_order)}
        frames=[]
        for E in frame_order:
            f=spec['frames'][E]
            encoded=json.dumps([f['numerator'],f['denominator_bits']],separators=(',',':')).encode()
            frames.append(dict(id=frame_ids[E],subspace=E,literal_spec=b.cf.frame_spec(E,h),
                               matrix_bits=f['denominator_bits'],matrix_sha256=sha256(encoded).hexdigest()))
        temporal=[];prefix=[[Q(i==j) for j in range(6)] for i in range(6)]
        max_row_l1=1;max_event=None;scalar_gates=0;scalar_unit_expansion=0
        def scalar(target,source,c,kind='add'):
            nonlocal max_row_l1,max_event,scalar_gates,scalar_unit_expansion
            if not c:return
            temporal.append([kind,target,source,coefficient(c)])
            prefix[target]=[x+c*y for x,y in zip(prefix[target],prefix[source])]
            scalar_gates+=1;scalar_unit_expansion+=abs(c.numerator)
            norm=max(sum(abs(x) for x in row) for row in prefix)
            if norm>max_row_l1:max_row_l1=norm;max_event=len(temporal)-1
        for role,E in enumerate(((1,),(7,),(),(),(),())):
            M,bits,nf=spec['entry'][E]
            temporal.append(['move_one_child',role,frame_ids[E],frame_ids[spec['E']],nf])
        for index,event in enumerate(spec['events']):
            if index in (8,16):
                temporal += [['rank_zero_reflected_gauge',role,index==16] for role in range(6)]
            if event[0]=='birth':
                _,role=event;old=list(prefix[role]);response=spec['responses'][index]
                temporal.append(['birth_keep_old_value',role,index])
                for target,c in enumerate(response['current_data_preimage']):
                    if c:scalar(target,role,-c,'birth_current_data_compensation')
            else:_,target,source,c=event;scalar(target,source,c)
        full=tuple(1<<k for k in range(h));M,bits,nf=spec['finish']
        temporal += [['move_one_child',role,frame_ids[spec['E']],frame_ids[full],nf] for role in range(6)]
        cleanup_start=len(temporal);I=spec['inverse']
        for row in range(2):
            for column in range(2):
                scalar(4+row,2+column,-(I[row][column]+Q(row==column)),'final_mutable_preimage_cleanup')
                scalar(4+row,column,-(Q(S[row][column])-Q(row==column)),'final_mutable_preimage_cleanup')
        expected=[[Q(0)]*6 for _ in range(6)]
        for row in range(2):
            for column in range(2):expected[row][2+column]=-I[row][column];expected[2+row][column]=Q(S[row][column])
        expected[4][4]=1;expected[5][5]=1
        if prefix!=expected:raise ValueError('The exported paid scalar cleanup does not exactly restore the dirty rows')
        core=list(temporal);core_scalar_gates=scalar_gates;core_unit_expansion=scalar_unit_expansion
        scalar(0,1,Q(a));scalar(1,0,Q(z))
        for role in (0,1):
            temporal.append(['native_constant_sign',role,-1]);prefix[role]=[-x for x in prefix[role]]
        scalar(3,2,Q(-z));scalar(2,3,Q(-a))
        for row,U in enumerate(spec['U']):
            normal=b.cf.compile_nested((),(U,),h)
            temporal.append(['raw_source_line_one_child',2+row,U,normal])
            temporal.append(['native_full_bank_exchange',row,2+row])
        cases.append(dict(S=S,inverse=[[coefficient(x) for x in row] for row in I],ambient_bits=h,payload_stock=6,
                          source_line_labels=spec['U'],donor_common_subspace=spec['E'],right_middle_subspace=spec['G'],
                          right_middle_operator='F_right_middle_subspace*C_full, with F on the RIGHT',frames=frames,
                          reflection_gauge_normal_form=spec['gauge_normal_form'],
                          reflection_gauge_matrix_sha256=sha256(json.dumps([spec['gauge'][0],spec['gauge'][1]],separators=(',',':')).encode()).hexdigest(),
                          clean_events=[[event[0],*event[1:3],coefficient(event[3])] if event[0]=='add' else event for event in spec['events']],
                          cut_future_responses={str(index):{key:[coefficient(x) for x in row] for key,row in response.items()} for index,response in spec['responses'].items()},
                          core_physical_events=core,canonical_physical_events=temporal,cleanup_start_core_event=cleanup_start,
                          core_scalar_bank_gates=core_scalar_gates,core_unit_shear_expansion=core_unit_expansion,
                          canonical_scalar_bank_gates=scalar_gates,canonical_unit_shear_expansion=scalar_unit_expansion,
                          exact_scalar_only_prefix_row_l1=str(max_row_l1),maximum_scalar_prefix_event=max_event,
                          scalar_prefix_scope='Virtual six-bank scalar rows with all phase/frame coordinates factored out; this is not an actual-operator or all-size precision bound.',
                          core_histogram=spec['core_histogram'],canonical_histogram=spec['canonical_histogram'],
                          core_rank=22,canonical_rank=24,capacity=24,
                          final_dirty_endpoint='C_full times original virtual dirty; all helper rows exactly identity in the final full frame'))
    return dict(schema='joint-mutable-birth-physical-contract-v1',producer='code/synthesis/joint_mutable_birth_swap.py',
                producer_sha256=sha256(Path(b.__file__).read_bytes()).hexdigest(),
                exporter_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                matrix_hash_serialization='UTF-8 JSON [integer Gaussian numerator matrix,denominator_bits], compact comma/colon, no newline',
                selected_column_layout='bit-major: ambient_bit*columns+column',
                scalar_coefficients='Applied once per bank, never raised to number of selected columns',cases=cases)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('Do not overwrite a completed joint-birth contract')
    fixture=export();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(fixture,indent=2)+'\n')
    print(json.dumps(dict(path=str(args.output),bytes=args.output.stat().st_size,producer_sha256=fixture['producer_sha256'],
                          exporter_sha256=fixture['exporter_sha256'],scalar_row_l1=[c['exact_scalar_only_prefix_row_l1'] for c in fixture['cases']])))


if __name__=='__main__':main()
