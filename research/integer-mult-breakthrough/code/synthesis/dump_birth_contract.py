#!/usr/bin/env python3
"""Export compact literal finite birth adapters without overwriting evidence."""
import argparse
import importlib
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


def matrix_hash(M,bits):
    return sha256(json.dumps([M,bits],separators=(',',':')).encode()).hexdigest()


def export(module):
    fixture=dict(schema='literal-birth-cut-contract-v2',producer_module=module.__name__,
                 producer_sha256=sha256(Path(module.__file__).read_bytes()).hexdigest(),
                 hash_serialization='UTF-8 JSON [integer Gaussian numerator matrix,denominator_bits], separators=(comma,colon), no trailing newline; rows and columns in ordinary binary order',
                 selected_column_layout='bit-major: address bit index = ambient_bit*columns+column',
                 scalar_coefficient_semantics='One constant coefficient per entire payload bank; it is not raised to the number of selected columns.',cases=[])
    for reuse in (False,True):
        spec=module.schedule(reuse);cf=module.cf
        frame_order=sorted(spec['frames'],key=lambda E:(len(E),E))
        frame_ids={E:'F'+str(i) for i,E in enumerate(frame_order)}
        transition_order=sorted(spec['operators'],key=lambda key:(len(key[0]),key[0],len(key[1]),key[1]))
        transition_ids={key:'T'+str(i) for i,key in enumerate(transition_order)}
        frames=[]
        for E in frame_order:
            f=spec['frames'][E]
            frames.append(dict(id=frame_ids[E],subspace=E,literal_spec=cf.frame_spec(E,spec['h']),
                               matrix_bits=f['denominator_bits'],matrix_sha256=matrix_hash(f['numerator'],f['denominator_bits'])))
        transitions=[]
        for key in transition_order:
            M,bits,inverse,nf=spec['operators'][key]
            transitions.append(dict(id=transition_ids[key],from_frame=frame_ids[key[0]],to_frame=frame_ids[key[1]],
                                    execute_rising_normal_form_inverse=inverse,rising_matrix_bits=bits,
                                    rising_matrix_sha256=matrix_hash(M,bits),one_child_normal_form=nf))
        events=[]
        for event in spec['events']:
            if event[0]=='move':_,role,key=event;events.append(['move',role,transition_ids[key]])
            elif event[0]=='add':_,a,z,c=event;events.append(['add',a,z,[c.numerator,c.denominator]])
            else:events.append(event)
        fixture['cases'].append(dict(reuse=reuse,ambient_bits=spec['h'],source_labels=spec['U'],target_labels=spec['T'],
                                     donor_subspace=spec['E'],recipient_subspace=spec.get('recipient',spec['E']),
                                     clean_events=spec['logical'],cut_birth_responses={str(i):row for i,row in spec['responses'].items()},
                                     physical_events=events,frames=frames,transitions=transitions,payload_stock=spec['stock'],
                                     initial_frame_ids=[frame_ids[spec['initial'][i]] for i in range(spec['stock'])],
                                     final_frame_ids=[frame_ids[spec['final'][i]] for i in range(spec['stock'])],
                                     child_width_histogram=spec['histogram'],rank_charge=spec['rank'],deficit=spec['deficit']))
    return fixture


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer',required=True,choices=['degenerate_birth_reuse_probe','nested_degenerate_birth_reuse'])
    parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise ValueError('Never overwrite a completed birth contract')
    module=importlib.import_module(args.producer);fixture=export(module)
    fixture['exporter_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(fixture,indent=2)+'\n')
    print(json.dumps(dict(output=str(args.output),bytes=args.output.stat().st_size,
                          producer_sha256=fixture['producer_sha256'],exporter_sha256=fixture['exporter_sha256'])))


if __name__=='__main__':main()
