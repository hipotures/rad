#!/usr/bin/env python3
"""Exact multiplicative-core Walsh/C reduction with dirty-bank replay.

The D-1 nonzero field coordinates form a cyclic convolution. The zero
coordinate is preserved with invertible border shears. Signed radix integer
products implement that convolution without calling Walsh/C recursively.
Field/log routing, native tape cost, precision and asymptotic transfer remain
open. Same-volume products are not assumed to be smaller recursive calls.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import time

from lagrangian_graph_completion import image,solve
import pauli_tensor_discriminator as g

PRIMITIVE={3:0b1011,4:0b10011,5:0b100101,6:0b1000011}
I=(Q(0),Q(1));MINUS_I=(Q(0),Q(-1))


def inverse(z):
    norm=z[0]*z[0]+z[1]*z[1]
    return z[0]/norm,-z[1]/norm


class Field:
    def __init__(self,n):
        self.n=n;self.d=1<<n;self.polynomial=PRIMITIVE[n];self.multiply_calls=0
    def mul(self,a,b):
        answer=0;self.multiply_calls+=1
        while b:
            if b&1:answer^=a
            a<<=1;b>>=1
            if a&self.d:a^=self.polynomial
        return answer
    def trace(self,a):
        answer=0
        for _ in range(self.n):answer^=a;a=self.mul(a,a)
        if answer not in (0,1):raise ValueError('Finite field trace left the prime field')
        return answer


def geometry(n):
    F=Field(n);d=F.d;L=d-1;powers=[];a=1
    for _ in range(L):powers.append(a);a=F.mul(a,2)
    if a!=1 or sorted(powers)!=list(range(1,d)):
        raise ValueError('Primitive polynomial/generator does not enumerate every nonzero field element')
    G=tuple(sum(F.trace(F.mul(1<<i,1<<j))<<i for i in range(n)) for j in range(n))
    dual=tuple(solve(G,1<<j) for j in range(n))
    for x in range(d):
        for y in range(d):
            if F.trace(F.mul(image(dual,x),y))!=((x&y).bit_count()%2):
                raise ValueError('Field trace/standard binary-dot duality failed')
    kernel=[1 if not F.trace(a) else -1 for a in powers]
    if sum(kernel)!=-1:raise ValueError('Nonzero character sum lost the zero coordinate')
    if any(sum(kernel[j]*kernel[(j+shift)%L] for j in range(L))!=(d-1 if shift==0 else -1) for shift in range(L)):
        raise ValueError('Cyclic core autocorrelation is not D*I-J')
    # Input order reverses exponent indices; output order is the dual trace basis.
    inputs=[0]+[powers[-j%L] for j in range(L)];outputs=[0]+[image(G,a) for a in powers]
    if sorted(inputs)!=list(range(d)) or sorted(outputs)!=list(range(d)):
        raise ValueError('Discrete-log/inverse-dual address lists are not full permutations')
    return dict(n=n,d=d,L=L,polynomial=F.polynomial,powers=powers,trace_Gram_columns=G,
                dual_columns=dual,kernel=kernel,input_order=inputs,output_order=outputs,
                field_multiply_calls_in_exact_geometry_checks=F.multiply_calls)


def packed_component(values,kernel,digit_bits):
    B=1<<digit_bits
    def encode(xs):
        z=0
        for x in reversed(xs):z=(z<<digit_bits)+x
        return z
    a=encode(values);k=encode(kernel);product=a*k;remaining=product;digits=[]
    for _ in range(2*len(values)-1):
        z=remaining%B
        if z>=B//2:z-=B
        digits.append(z);remaining=(remaining-z)//B
    if remaining:raise ValueError('Balanced-digit integer product overflowed its claimed guard')
    L=len(values);result=[digits[i]+(digits[i+L] if i+L<len(digits) else 0) for i in range(L)]
    return result,dict(variable_integer_bits=abs(a).bit_length(),fixed_kernel_integer_bits=abs(k).bit_length(),
                       product_integer_bits=abs(product).bit_length(),packed_digit_bits=digit_bits,
                       ordinary_product_digits=2*L-1,cyclic_output_digits=L)


def convolution(values,geo,inverse_core=False,corrupt=False):
    L=geo['L'];D=geo['d'];k=geo['kernel']
    numerator=[k[-j%L]-1 for j in range(L)] if inverse_core else list(k);kernel_denominator=D if inverse_core else 1
    if corrupt:
        j=next(j for j,z in enumerate(numerator) if z);numerator[j]=0
    denominator=max(q.denominator for z in values for q in z)
    real=[int(z[0]*denominator) for z in values];imag=[int(z[1]*denominator) for z in values]
    if any(Q(real[j],denominator)!=values[j][0] or Q(imag[j],denominator)!=values[j][1] for j in range(L)):
        raise ValueError('Common dyadic coefficient denominator was not exact')
    maximum=max([abs(z) for z in real+imag]+[0]);kernel_max=max(abs(z) for z in numerator)
    bound=L*maximum*kernel_max;bits=max(1,(2*bound).bit_length())
    r,rr=packed_component(real,numerator,bits);i,ii=packed_component(imag,numerator,bits)
    result=[(Q(a,denominator*kernel_denominator),Q(b,denominator*kernel_denominator)) for a,b in zip(r,i)]
    return result,dict(direction='inverse' if inverse_core else 'forward',real_product=rr,imag_product=ii,
                       exact_input_denominator=denominator,exact_kernel_denominator=kernel_denominator,
                       signed_ordinary_coefficient_absolute_bound=bound)


def direct_core(values,geo,inverse_core=False):
    L=geo['L'];D=geo['d'];k=geo['kernel'];output=[]
    for i in range(L):
        z=g.ZERO
        for j in range(L):
            coefficient=Q(k[(j-i)%L]-1,D) if inverse_core else Q(k[(i-j)%L])
            z=g.add(z,(coefficient*values[j][0],coefficient*values[j][1]))
        output.append(z)
    return output


def c_transform(values,geo,backward=False,normalization='late',corruption=None):
    n=geo['n'];D=geo['d'];a=g.power(g.ALPHA,n);events=[];record={};peak=Q()
    def note(label):
        nonlocal peak
        current=max(abs(q) for z in values for q in z)
        if not record or current>peak:peak=current;record.update(stage=label,maximum_real_or_imaginary_component=str(current))
        events.append(label)
    def scales(coefficients):
        for j,c in enumerate(coefficients):values[j]=g.mul(c,values[j])
    def unorder(order,ordered):
        result=[g.ZERO]*D
        for j,address in enumerate(order):result[address]=ordered[j]
        return result
    note('initial')
    if not backward:
        scales([g.power(MINUS_I,j.bit_count()) for j in range(D)]);note('input fourth-root chirps')
        if normalization=='early':scales([a]*D);note('early global Gaussian normalization')
        values=[values[j] for j in geo['input_order']];note('paid discrete-log input permutation')
        for j in range(1,D):values[j]=g.add(values[j],g.neg(values[0]))
        note('nonzero border subtraction')
        core,receipt=convolution(values[1:],geo);values[1:]=core;note('nonzero cyclic core through signed integer products')
        if corruption!='omit zero-coordinate scale':values[0]=g.scale(values[0],D)
        note('zero-coordinate dyadic scale')
        if corruption!='omit zero-border sum':
            z=g.ZERO
            for q in values[1:]:z=g.add(z,q)
            values[0]=g.add(values[0],g.neg(z))
        note('zero-border sum subtraction')
        values=unorder(geo['output_order'],values);note('paid inverse-dual output permutation')
        scales([g.power(MINUS_I,j.bit_count()) for j in range(D)])
        if normalization=='late':scales([a]*D)
        note('output fourth-root chirps and normalization')
    else:
        scales([g.power(I,j.bit_count()) for j in range(D)])
        if normalization=='late':scales([inverse(a)]*D)
        note('inverse output chirps and optional initial normalization')
        values=[values[j] for j in geo['output_order']];note('paid dual-output input permutation')
        z=g.ZERO
        for q in values[1:]:z=g.add(z,q)
        values[0]=g.add(values[0],z);note('inverse zero-border sum addition')
        values[0]=(values[0][0]/D,values[0][1]/D);note('inverse zero-coordinate dyadic scale')
        core,receipt=convolution(values[1:],geo,True,corruption=='truncate inverse kernel');values[1:]=core
        note('inverse nonzero cyclic core through signed integer products')
        for j in range(1,D):values[j]=g.add(values[j],values[0])
        note('inverse nonzero border addition')
        values=unorder(geo['input_order'],values);note('paid inverse discrete-log input permutation')
        scales([g.power(I,j.bit_count()) for j in range(D)])
        if normalization=='early':scales([inverse(a)]*D)
        note('inverse input chirps and optional final normalization')
    return values,dict(chronology=events,peak=record,integer_interface=receipt)


def full_word(x,y,dirty,geo,normalization='late',corruption=None):
    x,r1=c_transform(list(x),geo,normalization=normalization,corruption=corruption)
    y=[g.add(a,b) for a,b in zip(y,x)]
    x,r2=c_transform(x,geo,True,normalization,corruption if corruption=='truncate inverse kernel' else None)
    dirty,r3=c_transform(list(dirty),geo,normalization=normalization)
    return (x,y,dirty),[r1,r2,r3]


def probe(n):
    started=time.monotonic();geo=geometry(n);D=geo['d'];C=g.tensor_c(n);rng=random.Random(20261008+n)
    generic=[(Q(rng.randrange(-1024,1025),4),Q(rng.randrange(-1024,1025),4)) for _ in range(D-1)]
    forward,forward_r=convolution(generic,geo);backward,inverse_r=convolution(forward,geo,True)
    if forward!=direct_core(generic,geo) or backward!=generic or backward!=direct_core(forward,geo,True):
        raise ValueError('Signed integer convolution or inverse failed independent cyclic sums')
    controls=[];hashes={};column_checks=0;integer_products=0;word_peaks={}
    for placement in ('late','early'):
        digest=sha256();peaks=Q()
        for bank in range(3):
            for address in range(D):
                for value in (g.ONE,I):
                    initial=[[g.ZERO]*D for _ in range(3)];initial[bank][address]=value
                    result,receipts=full_word(*initial,geo,placement)
                    expected=[list(initial[0]),list(initial[1]),[g.ZERO]*D]
                    if bank==0:
                        for a in range(D):expected[1][a]=g.add(expected[1][a],g.mul(C[a][address],value))
                    if bank==2:
                        for a in range(D):expected[2][a]=g.mul(C[a][address],value)
                    if list(result)!=expected:raise ValueError('Complete cyclic-reduction source/sink/dirty columns failed')
                    column_checks+=1;integer_products+=6
                    for r in receipts:
                        peak=Q(r['peak']['maximum_real_or_imaginary_component'])
                        if peak>peaks:peaks=peak
                    for a,arr in enumerate(result):digest.update(json.dumps([bank,address,g.text_complex(value),a,[g.text_complex(z) for z in arr]],separators=(',',':')).encode())
        hashes[placement]=digest.hexdigest();word_peaks[placement]=str(peaks)
        # Every zero coordinate and dirty column was independent above; these
        # matched single-payload failures guard the border/inverse clauses.
        for corruption in ('omit zero-coordinate scale','omit zero-border sum','truncate inverse kernel'):
            x=[g.ZERO]*D;x[0]=g.ONE;zero=[g.ZERO]*D
            result,receipts=full_word(x,zero,zero,geo,placement,corruption)
            expected=(x,[C[a][0] for a in range(D)],zero);bad=[]
            for bank in range(3):
                for a in range(D):
                    if result[bank][a]!=expected[bank][a]:bad.append((bank,a))
            if not bad:raise ValueError('Matched cyclic-border/inverse corruption was not detected')
            bank,a=bad[0];controls.append(dict(normalization=placement,corruption=corruption,
                                               single_initial_payload=dict(bank=0,address=0,Gaussian_value=['1','0']),
                                               output_bank=bank,output_address=a,expected=g.text_complex(expected[bank][a]),observed=g.text_complex(result[bank][a])))
    # Explicit buffer witness: late normalization multiplies the lone zero
    # source by D before its canceling border sum. Reordering global scalar
    # normalization reduces this observed peak but still needs paid precision.
    single=[g.ZERO]*D;single[0]=g.ONE
    _,late=c_transform(single,geo);_,early=c_transform(single,geo,normalization='early')
    return dict(status='EXACT CYCLIC REDUCTION AND NONCIRCULAR INTEGER REPLAY PASS',active_bits=n,dimension=D,
                geometry=geo,complete_Gaussian_initial_columns=3*D,real_imaginary_directions_each=2,
                complete_column_direction_checks=column_checks,normalization_placements=['late','early'],
                all_column_hashes=hashes,verification_only_integer_products=integer_products,
                algorithm_cyclic_convolutions_per_data_dirty_word=3,algorithm_real_fixed_kernel_integer_products=6,
                generic_forward_integer_interface=forward_r,generic_inverse_integer_interface=inverse_r,
                matched_single_payload_controls=controls,word_basis_component_peaks=word_peaks,
                zero_source_temporary_peak=dict(late=late['peak'],early=early['peak'],source_endpoint_maximum='1',sink_endpoint_component_bound=str(max(abs(q) for row in C for z in row for q in z))),
                seconds=time.monotonic()-started,
                scope='Complete finite Gaussian source/sink/dirty word, exact field permutations, zero-border factorization and explicit balanced signed-integer convolution. Same-volume fixed-kernel products, discrete-log routing, field generation, tape movement and buffer precision are paid unresolved native costs. No improved multiplier oracle or exponent is assumed.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--bounded',action='store_true');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    paths=[Path(__file__),Path(g.__file__),Path(__file__).with_name('lagrangian_graph_completion.py')]
    hashes={f:sha256(f.read_bytes()).hexdigest() for f in paths};specs=[3] if args.bounded else [3,4,5,6]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  source_sha256={f.name:v for f,v in hashes.items()},random_seed_for_generic_components='20261008+n',
                  primitive_polynomials=PRIMITIVE)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,n):n for n in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('status','active_bits','dimension','complete_column_direction_checks','seconds')}),flush=True)
    if any(sha256(f.read_bytes()).hexdigest()!=v for f,v in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
