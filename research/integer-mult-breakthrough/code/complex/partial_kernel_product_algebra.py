#!/usr/bin/env python3
"""Exact bilinear fusion when a Gaussian transform axis is left partial.

The product algebra is q_C(a,b)=C^-1((Ca) pointwise (Cb)), not coefficient
XOR convolution. Tensor controls compare a direct signed dyadic tensor,
the literal Gaussian transform product, and a transform-avoiding three-call
recursion. Real-input conjugacy and minimal character rows are retained.
This source supplies no native multiplier or carry/precision interface.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time


SIGNS = (((1,1),(1,-1)),((-1,1),(1,1)))


def add(a,b):
    return a[0]+b[0],a[1]+b[1]


def multiply(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def C_apply(values,inverse=False):
    size = len(values)
    f = size.bit_length()-1
    if size != 1 << f:
        raise ValueError('complete binary cube required')
    values = list(values)
    alpha,beta = ((1,-1),(1,1)) if inverse else ((1,1),(1,-1))
    for j in range(f):
        out = [(0,0)]*size
        for x in range(size):
            if x >> j & 1:
                continue
            y = x^(1 << j)
            out[x] = add(multiply(alpha,values[x]),multiply(beta,values[y]))
            out[y] = add(multiply(beta,values[x]),multiply(alpha,values[y]))
        values = out
    return values,f


def q_literal(A,B):
    a,ga = C_apply(A)
    b,gb = C_apply(B)
    c,gc = C_apply([multiply(x,y) for x,y in zip(a,b)],inverse=True)
    return c,ga+gb+gc


def q_direct(A,B):
    size = len(A)
    f = size.bit_length()-1
    output = []
    for z in range(size):
        value = (0,0)
        for x in range(size):
            for y in range(size):
                sign = 1
                for j in range(f):
                    sign *= SIGNS[z >> j & 1][x >> j & 1][y >> j & 1]
                term = multiply(A[x],B[y])
                value = add(value,(sign*term[0],sign*term[1]))
        output.append(value)
    return output,f


def q_three_product(A,B):
    if len(A)==1:
        return [multiply(A[0],B[0])],0,1
    half = len(A)//2
    a0,a1 = A[:half],A[half:]
    b0,b1 = B[:half],B[half:]
    P,g,p = q_three_product(a0,b0)
    Q,h,q = q_three_product(a1,b1)
    R,k,r = q_three_product([add(x,y) for x,y in zip(a0,a1)],
                            [add(x,y) for x,y in zip(b0,b1)])
    if g!=h or g!=k:
        raise AssertionError('three-product child grids do not align')
    lower = [(x[0]-2*y[0],x[1]-2*y[1]) for x,y in zip(R,Q)]
    upper = [(x[0]-2*y[0],x[1]-2*y[1]) for x,y in zip(R,P)]
    return lower+upper,g+1,p+q+r


def q_real_packed(A,B):
    """A bijective real-to-half-Gaussian packing, not sparse address padding.

    Pack a0,a1 as ((a0+a1)+i(a0-a1))/2. One C_(f-1) produces half
    the spectrum; the other half follows by complement conjugacy. Multiply
    the retained halves, invert C_(f-1), and recover real a0/a1 by Re±Im.
    No claim is made about arbitrary dirty Gaussian input/output banks.
    """
    if any(im for re,im in A+B):
        raise ValueError('the half-spectrum contract requires real operand fields')
    half = len(A)//2
    def pack(values):
        return [(x[0]+y[0],x[0]-y[0]) for x,y in zip(values[:half],values[half:])]
    a,ga = C_apply(pack(A))
    b,gb = C_apply(pack(B))
    product = [multiply(x,y) for x,y in zip(a,b)]
    decoded,gc = C_apply(product,inverse=True)
    # Each input pack has one denominator bit. Product clears both, then
    # the inverse child's bits are retained without truncation.
    output = [(re+im,0) for re,im in decoded]+[(re-im,0) for re,im in decoded]
    return output,2+ga+gb+gc,dict(Gaussian_products=half,complex_transform_widths=[ga,gb,gc],
                                  input_real_fields=2*len(A),output_real_fields=len(A),
                                  independent_half_spectrum_real_fields=2*half,
                                  packed_input_grid_charge=1,
                                  complete_output_grid_bits=2+ga+gb+gc,
                                  arbitrary_dirty_Gaussian_contract=False)


def equal(A,g,B,h):
    grid = max(g,h)
    return [(x << (grid-g),y << (grid-g)) for x,y in A] == [
        (x << (grid-h),y << (grid-h)) for x,y in B]


def characterize_one_axis(grid):
    scale = 1 << grid
    roots = []
    for a in range(-scale,scale+1):
        for b in range(-scale,scale+1):
            # A unital character has row(u,1-u); multiplicativity on e0²
            # requires u²-u+1/2=0, with u=(a+ib)/2^grid.
            x,y = multiply((a,b),(a,b))
            if (x-scale*a+(1 << (2*grid-1)),y-scale*b)==(0,0):
                roots.append([a,b])
    expected = sorted([[scale//2,-scale//2],[scale//2,scale//2]])
    if sorted(roots)!=expected:
        raise AssertionError('one-axis Gaussian-dyadic character screen has a noncanonical root')
    return dict(fractional_bits=grid,unital_character_u_numerators=roots,
                exact_equation='u^2-u+1/2=0',roots='(1+i)/2 and (1-i)/2')


def probe(f):
    size = 1 << f
    seed = 202610090429+f
    rng = Random(seed)
    arbitrary = [[(rng.randrange(-5,6),rng.randrange(-5,6)) for _ in range(size)] for _ in range(2)]
    real = [[(rng.randrange(-5,6),0) for _ in range(size)] for _ in range(2)]
    checked = 0
    products = None
    for A,B in (arbitrary,real):
        direct,gd = q_direct(A,B)
        literal,gl = q_literal(A,B)
        third,gt,products = q_three_product(A,B)
        if not equal(direct,gd,literal,gl) or not equal(direct,gd,third,gt):
            raise AssertionError('partial Gaussian product fusion does not match the exact signed tensor')
        if products!=3**f:
            raise AssertionError('actual transform-avoiding Gaussian scalar product count differs from3^f')
        checked += 3*2*size
        unit = [(1,0)]*size
        identity,g = q_three_product(A,unit)[:2]
        if not equal(identity,g,A,0):
            raise AssertionError('tensor product algebra did not keep unit allones')
    A,B = real
    packed,gpacked,packed_contract = q_real_packed(A,B)
    reference,greference = q_direct(A,B)
    if not equal(packed,gpacked,reference,greference):
        raise AssertionError('real half-volume packed product differs from the complete Gaussian tensor algebra')
    checked += 2*size
    a,g = C_apply(A)
    b,h = C_apply(B)
    mask = size-1
    if any(a[x^mask]!=(a[x][0],-a[x][1]) or b[x^mask]!=(b[x][0],-b[x][1]) for x in range(size)):
        raise AssertionError('real-input Gaussian spectra do not have exact complement conjugacy')
    product = [multiply(x,y) for x,y in zip(a,b)]
    if any(product[x^mask]!=(product[x][0],-product[x][1]) for x in range(size)):
        raise AssertionError('pointwise bilinear consumer did not retain real conjugacy')
    decoded,extra = C_apply(product,inverse=True)
    if any(im for re,im in decoded):
        raise AssertionError('real tensor product algebra returned nonreal coefficients')
    # Every spectral coordinate is an actual character; dense evaluation is
    # therefore not replaced by calling the scalar product rank optimal.
    basis_columns = []
    for x in range(size):
        basis = [(0,0)]*size
        basis[x]=(1,0)
        values,bits = C_apply(basis)
        if bits!=f or any(value==(0,0) for value in values):
            raise AssertionError('Gaussian character form is not dense')
        restored,again = C_apply(values,inverse=True)
        if not equal(restored,bits+again,basis,0):
            raise AssertionError('independent character matrix lost exact invertibility')
        basis_columns.append(values)
    generator_values = []
    for j in range(f):
        t = [(1 if not x >> j & 1 else -1,0) for x in range(size)]
        values,g = C_apply(t)
        if any(re or abs(im)!=(1 << g) for re,im in values):
            raise AssertionError('tensor generator character values are not±i')
        generator_values.append(values)
        square,sg = q_three_product(t,t)[:2]
        if not equal(square,sg,[(-1,0)]*size,0):
            raise AssertionError('missing Gaussian product generator did not square to minus unit')
    if len({tuple(value[x][1] >> f for value in generator_values) for x in range(size)})!=size:
        raise AssertionError('all2^f split character sign choices were not retained')
    q00,g00 = q_three_product([(1,0)]+[(0,0)]*(size-1),[(1,0)]+[(0,0)]*(size-1))[:2]
    if f==1 and equal(q00,g00,[(1,0),(0,0)],0):
        raise AssertionError('incorrect coefficient-XOR product negative did not reject')
    return dict(missing_axes=f,coefficient_count=size,seed=seed,exact_product_fields=checked,
                tensor_structure_grid_bits=f,literal_transform_product_grid_bits=3*f,
                transform_avoiding_Gaussian_products=products,split_algebra_minimum_products=size,
                named_three_product_volume_ratio=dict(numerator=3**f,denominator=2**f),
                dense_minimum_character_entries=size*size,
                unit='Allones coefficient vector',generators_square='Minus unit',
                real_conjugacy='z[x xor(2^f-1)] = conjugate(z[x]); retained by pointwise multiplication.',
                independent_real_input_fields=size,independent_half_spectrum_real_fields=2*(size//2),
                real_half_volume_product=packed_contract,
                no_free_sparse_address_embedding=True,
                coefficient_XOR_negative=f==1,
                character_matrix_sha256=sha256(json.dumps(basis_columns).encode()).hexdigest(),
                scope='Exact finite bilinear algebra, not unrestricted dirty Gaussian circuit, carry map, native routing or asymptotic multiplier.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    before = sha256(Path(__file__).read_bytes()).hexdigest()
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [1,2] if args.bounded else [1,2,4,6]
    if args.workers == 1:
        cases = [probe(f) for f in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe,tasks))
    characters = [characterize_one_axis(grid) for grid in (1,2,3,4)]
    if sha256(Path(__file__).read_bytes()).hexdigest()!=before:
        raise AssertionError('source changed during run')
    result = dict(status='PASS EXACT PARTIAL GAUSSIAN PRODUCT ALGEBRA',started_utc=utc,
                  completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=before,
                  workers=args.workers,bounded=args.bounded,cases=cases,one_axis_characters=characters,
                  required_old_assembly_complex_saving=dict(numerator=20,denominator=189981),
                  note='The retained old-assembly threshold is a reference requirement; a new product assembly needs a new complete recurrence. No threshold is claimed satisfied.',
                  seconds=time.monotonic()-started,
                  scope='Finite algebraic fusion and character/density discriminator. Complete product types, native time/volume, numerical guards, carrying and end-to-end kappa remain open.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),fields=sum(c['exact_product_fields'] for c in cases),
                          product_counts=[c['transform_avoiding_Gaussian_products'] for c in cases],seconds=result['seconds'])),flush=True)


if __name__ == '__main__':
    main()
