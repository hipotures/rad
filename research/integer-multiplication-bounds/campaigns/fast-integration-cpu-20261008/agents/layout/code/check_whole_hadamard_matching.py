#!/usr/bin/env python3
"""Whole-mask Hadamard routing with spectator cancellation, no selected mask.

Exact all-address algebra and Q-word recovery. Native internal BIT costs remain.
"""
import argparse
import hashlib
import importlib.util
import json
import random
from pathlib import Path
from time import perf_counter


def load(path):
    spec=importlib.util.spec_from_file_location('circuit_helpers',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def phase_turn(real,imag,index,turn):
    a,b=real[index],imag[index]
    if turn==1:real[index],imag[index]=-b,a
    elif turn==2:real[index],imag[index]=-a,-b
    elif turn==3:real[index],imag[index]=b,-a


def run(config,helper):
    started=perf_counter();b=config['address_bits'];q=config['word_bits']
    rng=random.Random(config['seed']);permutation=list(range(b));rng.shuffle(permutation)
    if config.get('single_cycle'):
        order=permutation.copy()
        for i,bit in enumerate(order):permutation[bit]=order[(i+1)%b]
    matchings=helper.involutions(permutation)
    pairs=sum(len(x) for x in matchings)
    correction_phase=(-b+pairs)%4;restoration_bits=3*b
    chunks=config['chunks'];assert sum(chunks)==b
    starts=[];offset=0
    for width in chunks:starts.append(offset);offset+=width
    # All bits occur; fixed chunk-depth groups supply the prescribed order.
    bit_order=[start+depth for depth in range(max(chunks))
               for start,width in zip(starts,chunks) if depth<width]
    assert sorted(bit_order)==list(range(b))
    source=[rng.randrange(-(1<<(q-2)),1<<(q-2)) for _ in range(1<<b)]
    oracle=[0]*len(source)
    for i,word in enumerate(source):oracle[helper.address_map(i,permutation)]=word

    def attempt(p,omit_spectator=False,wrong_phase=False):
        real=[x<<(p-q) for x in source];imag=[0]*len(source)
        ledger={'pair_butterflies':0,'payload_word_reads':0,'payload_word_writes':0,
                'whole_H_calls':0,'diagonal_scans':0}
        for matching in matchings:
            paired={x for pair in matching for x in pair}
            spectators=[x for x in range(b) if x not in paired]
            for repeat in range(3):
                for target in bit_order:
                    helper.half_hadamard(real,target,ledger)
                    helper.half_hadamard(imag,target,ledger)
                ledger['whole_H_calls']+=1
                for i in range(len(real)):
                    turn=2*(sum(((i>>a)&(i>>z)&1) for a,z in matching)%2)
                    if not omit_spectator:turn+=sum((i>>a)&1 for a in spectators)
                    phase_turn(real,imag,i,turn%4)
                ledger['diagonal_scans']+=1
                ledger['payload_word_reads']+=2*len(real)
                ledger['payload_word_writes']+=2*len(real)
        for i in range(len(real)):phase_turn(real,imag,i,0 if wrong_phase else correction_phase)
        shift=p-q-restoration_bits
        recovered=[helper.nearest(x,shift) for x in real]
        recovered_imag=[helper.nearest(x,shift) for x in imag]
        wrong=sum(x!=y or z!=0 for x,y,z in zip(recovered,oracle,recovered_imag))
        return {'work_bits':p,'incorrect_words':wrong,
                'maximum_real_integer_error':max(abs(x-y) for x,y in zip(recovered,oracle)),
                'maximum_imaginary_integer_error':max(abs(x) for x in recovered_imag),'ledger':ledger}

    guard=(12*b).bit_length()+10;p=q+restoration_bits+guard
    positive=attempt(p);assert positive['incorrect_words']==0
    low=attempt(q+restoration_bits-8);assert low['incorrect_words']>0
    spectator=attempt(p,omit_spectator=True)
    # A perfect matching in both involutions would have no spectators. The
    # pinned random/single-cycle controls contain unmatched coordinates.
    assert any(b>2*len(matching) for matching in matchings)
    assert spectator['incorrect_words']>0
    phase=attempt(p,wrong_phase=True)
    if correction_phase:assert phase['incorrect_words']>0
    return {'config':config,'coordinate_permutation':permutation,'matchings':matchings,
            'restoration_bits':restoration_bits,'restoration_fourth_root_phase':correction_phase,
            'positive':positive,'insufficient_precision_negative':low,
            'omitted_spectator_phase_negative':spectator,'omitted_global_phase_control':phase,
            'status':'whole-address H matching circuit and precision controls passed',
            'seconds':perf_counter()-started,
            'limitation':'Direct integer butterflies verify the circuit. Native C internal BIT routing and actual tape charges are inherited conditions, not replaced here.'}


def main():
    parser=argparse.ArgumentParser()
    for key in ['helper','config','output']:parser.add_argument('--'+key,required=True)
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    helper=load(args.helper);rows=[]
    for config in json.loads(Path(args.config).read_text()):
        row=run(config,helper);rows.append(row)
        (out/(config['id']+'.json')).write_text(json.dumps(row,indent=2)+'\n')
        print(json.dumps({'id':config['id'],'status':row['status'],'seconds':row['seconds']}),flush=True)
    result={'rows':rows,'source_hashes':{'driver':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                        'helper':hashlib.sha256(Path(args.helper).read_bytes()).hexdigest()}}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
