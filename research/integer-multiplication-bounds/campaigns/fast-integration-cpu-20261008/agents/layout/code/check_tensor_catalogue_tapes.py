#!/usr/bin/env python3
"""Exact rounded prefix tensors with paid sequential outer tape staging.

Native multiplication internals are separately charged as four integer child
products per complex prefix. This is not a bit-level Turing-machine simulator.
"""
import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from random import Random
from time import perf_counter


def trunc(value,bits):return (abs(value)>>bits)*(-1 if value<0 else 1)


def cmul(a,b,p):
    return trunc(a[0]*b[0]-a[1]*b[1],p),trunc(a[0]*b[1]+a[1]*b[0],p)


class Tape:
    def __init__(self,width,rows=()):self.width=width;self.rows=list(rows);self.head=0;self.movement=0
    def read(self):
        value=self.rows[self.head];self.head+=1;self.movement+=self.width;return value
    def append(self,value):
        assert self.head==len(self.rows);self.rows.append(value);self.head+=1;self.movement+=self.width
    def seek(self,position):self.movement+=abs(position-self.head)*self.width;self.head=position


def run(config):
    started=perf_counter();radices=config['radices'];d=len(radices);p=config['bits'];scale=1<<p
    assert p>=sum(math.ceil(math.log2(r)) for r in radices)
    rng=Random(config['seed'])
    choices=[(Fraction(3,5),Fraction(4,5)),(Fraction(-4,5),Fraction(3,5)),
             (Fraction(5,13),Fraction(-12,13)),(Fraction(-12,13),Fraction(-5,13)),
             (Fraction(1,2),Fraction(1,3)),(Fraction(-1),Fraction(0)),(Fraction(0),Fraction(1))]
    exact=[[rng.choice(choices) for _ in range(r)] for r in radices]
    fixed=[[tuple(int(value*scale) for value in pair) for pair in axis] for axis in exact]
    width=2*(p+2);catalogue=Tape(width,[pair for axis in fixed for pair in axis])
    old=Tape(width,[(scale,0)]);movement=0;products=0;volumes=[];offset=0
    for axis,r in enumerate(radices):
        new=Tape(width);catalogue.seek(offset)
        for _ in range(len(old.rows)):
            prefix=old.read()
            # One scratch-word write and reset, and one read/reset per child.
            movement+=2*width
            for _ in range(r):
                factor=catalogue.read();movement+=2*width
                value=cmul(prefix,factor,p)
                assert value[0]*value[0]+value[1]*value[1]<=scale*scale
                new.append(value);products+=1
            catalogue.seek(offset)
        old.seek(0);new.seek(0)
        movement+=old.movement+new.movement;old=new;old.movement=0
        offset+=r;catalogue.seek(offset);volumes.append(len(old.rows))
    movement+=catalogue.movement
    V=math.prod(radices);assert len(old.rows)==V and sum(volumes)<2*V
    maximum=Fraction(0);checked=0
    # Independent exact rational oracle; no exact denominator is stored in
    # the proposed producer. The optional exhaustive reference is test work.
    sample=config.get('oracle_samples',V)
    selected=set(range(V)) if sample>=V else set(rng.sample(range(V),sample))|{0,V-1}
    for index,key in enumerate(itertools.product(*(range(r) for r in radices))):
        if index not in selected:continue
        reference=(Fraction(1),Fraction(0));rounded=(scale,0)
        for i,j in enumerate(key):
            a,b=reference;c,e=exact[i][j];reference=(a*c-b*e,a*e+b*c)
            rounded=cmul(rounded,fixed[i][j],p)
        assert rounded==old.rows[index],('prefix order changed',index)
        error=max(abs(Fraction(word,scale)-value) for word,value in zip(rounded,reference))
        assert error<=Fraction(4*d,scale),(config,index,error)
        maximum=max(maximum,error);checked+=1
    assert movement<=12*width*sum(volumes)+4*width*V
    return {'config':config,'status':'growing-prefix tape movement and exact rounding checks passed',
        'final_records':V,'prefix_records_generated':sum(volumes),'prefix_volume_ratio':sum(volumes)/V,
        'complex_prefix_products':products,'native_integer_child_products':4*products,
        'outer_tape_bits_moved':movement,'record_width_bits':width,
        'movement_per_final_record_bit':movement/(V*width),'reference_outputs_checked':checked,
        'maximum_component_error_numerator':maximum.numerator,'maximum_component_error_denominator':maximum.denominator,
        'error_envelope':'4*d*2^-P','fixed_outer_tapes':'old/new prefix buffers, one concatenated catalogue, one prefix scratch word',
        'seconds':perf_counter()-started,
        'limitations':['paid word-head movement, not a binary-instruction tape simulator',
                       'four exact finite integer products charged per complex prefix; native M(CP) cost remains separate',
                       'independent exact oracle denominators are test-only and never producer records']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);rows=[]
    for i,config in enumerate(json.loads(Path(args.config).read_text())):
        row=run(config);rows.append(row);(out/f'row-{i}.json').write_text(json.dumps(row,indent=2)+'\n')
    result={'status':'explicit tensor catalogue tape controls passed','rows':rows,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'seconds':[r['seconds'] for r in rows]}))


if __name__=='__main__':main()
