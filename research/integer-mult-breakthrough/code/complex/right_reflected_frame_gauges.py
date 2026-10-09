#!/usr/bin/env python3
"""Exact monomial gauges for right-background canonical Clifford frames.

Right F_E*C_full represents L_(Eperp), including degenerate E. Its
difference from canonical F_(Eperp) is an actual paid monomial operator,
not a free gauge identification. This compiler retains that operator.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
from time import perf_counter

import scalable_subspace_interfaces as exact


COMPILER_SHA = '3da400b0b157cc28b546113e63a150e4b1672c71a5f2c74e724ac8fc3d1f4851'


def full(n):
    return tuple(1 << j for j in range(n))


def reflected_word(E, n):
    """G_E=(F_(Eperp)*C_full)*F_E^-1, in temporal execution order."""
    R = exact.reference.perpendicular(E, n)
    return (exact.inverse_word(exact.literal_word(E, n))
            + exact.literal_word(full(n), n) + exact.literal_word(R, n))


def compile_monomial(word, n):
    X, Z = exact.tableau(word, n)
    if any(x or p & 1 for x, z, p in Z):
        raise ValueError('The actual word is not monomial')
    offset, null = exact.solve_affine([z for x,z,p in Z],
                                    sum((p//2) << j for j,(x,z,p) in enumerate(Z)), n)
    if null:
        raise AssertionError('Monomial output position is not unique')
    columns = [x for x,z,p in X]
    if len(exact.basis(columns)) != n:
        raise AssertionError('Monomial route is singular')
    numerator, path_rank, free = exact.path_sum_at_zero(word,n,offset)
    phases = [p for p in range(4) if numerator == tuple(v << path_rank for v in exact.UNITS[p])]
    if len(phases) != 1:
        raise AssertionError('Monomial normalization is not a Gaussian fourth root')
    constant = phases[0]
    def unit(y):
        x,z,p = exact.pauli_combination(X,y)
        return (constant+p+2*exact.dot(z,offset)) % 4
    q = exact.fit_quadratic(unit,n)
    normal = dict(n=n,selected_rank_per_column=0,one_bulk_child_calls=0,
                  output_affine_offset=offset,output_columns=columns,
                  input_columns=list(full(n)),
                  output_quadratic=exact.serialize_quadratic(exact.Quadratic(n)),
                  input_quadratic=exact.serialize_quadratic(q),
                  global_unit_exponent=constant,
                  compilation=dict(path_variables=path_rank,summed_free_variables=free,
                                   full_address_arrays_allocated=False))
    exact.assert_complete_tableau(normal,word)
    return normal


def reflection_gauge(E,n):
    E = exact.basis(E)
    normal = compile_monomial(reflected_word(E,n),n)
    normal['canonical_source_subspace'] = list(E)
    normal['right_target_subspace'] = list(exact.reference.perpendicular(E,n))
    return normal


def add_quadratics(a,b):
    if len(a.linear)!=len(b.linear):
        raise ValueError('Quadratic sizes differ')
    q=exact.Quadratic(len(a.linear))
    q.constant=(a.constant+b.constant)%4
    q.linear=[(x+y)%4 for x,y in zip(a.linear,b.linear)]
    q.cross=[x^y for x,y in zip(a.cross,b.cross)]
    return q


def compile_canonical_to_right(E,F,n):
    """Actual F_E -> F_F*C_full, one child at d(E,Fperp)."""
    R=exact.reference.perpendicular(F,n)
    normal=exact.compile_interface(E,R,n)
    gauge=reflection_gauge(R,n)
    # A rank-zero normal is X_offset*P*diag(i^q) on the physical input.
    q=exact.parse_quadratic(gauge['input_quadratic'])
    added=q.substitute(normal['output_affine_offset'],normal['output_columns'])
    normal['output_quadratic']=exact.serialize_quadratic(add_quadratics(
        exact.parse_quadratic(normal['output_quadratic']),added))
    normal['global_unit_exponent']=(normal['global_unit_exponent']
                                  +q.evaluate(normal['output_affine_offset']))%4
    normal['output_affine_offset']=(gauge['output_affine_offset']
        ^exact.embed(normal['output_affine_offset'],gauge['output_columns']))
    normal['output_columns']=[exact.embed(column,gauge['output_columns'])
                              for column in normal['output_columns']]
    normal['actual_right_target_subspace']=list(exact.basis(F))
    normal['actual_frame_convention']='canonical source to RIGHT target F_F*C_full'
    word=(exact.inverse_word(exact.literal_word(E,n))
          +exact.literal_word(full(n),n)+exact.literal_word(F,n))
    exact.assert_complete_tableau(normal,word)
    return normal


def compile_right_to_canonical(E,F,n):
    """Actual F_E*C_full -> F_F, retaining two monomial stages.

    The first stage is an exact rank-zero reflected gauge inverse; the
    second stage is one canonical distance-width child. Both stream
    executions remain paid. An input affine offset is not discarded.
    """
    R=exact.reference.perpendicular(E,n)
    gauge_word=exact.inverse_word(reflected_word(R,n))
    gauge=compile_monomial(gauge_word,n)
    normal=exact.compile_interface(R,F,n)
    original_word=(exact.inverse_word(exact.literal_word(E,n))
                   +exact.inverse_word(exact.literal_word(full(n),n))
                   +exact.literal_word(F,n))
    compiled=exact.compiled_word(gauge)+exact.compiled_word(normal)
    if exact.tableau(original_word,n)!=exact.tableau(compiled,n):
        raise AssertionError('Right-to-canonical complete Pauli images differ')
    y=gauge['output_affine_offset']
    coordinate=exact.coordinates(y,normal['input_columns'],n)
    rank=normal['selected_rank_per_column']
    spectator=coordinate & ~((1<<rank)-1)
    x=normal['output_affine_offset']^exact.embed(spectator,normal['output_columns'])
    value=exact.reconstructed_entry(normal,x,y)
    unit=(gauge['input_quadratic']['constant']+gauge['output_quadratic']['constant'])%4
    expected=exact.multiply_gaussian(value,exact.UNITS[unit])
    actual,path_rank,free=exact.path_sum_at_zero(original_word,n,x)
    if path_rank<rank or actual!=tuple(v << (path_rank-rank) for v in expected):
        raise AssertionError('Right-to-canonical global coefficient differs')
    return dict(n=n,selected_rank_per_column=rank,one_bulk_child_calls=int(rank>0),
                stages=[gauge,normal],actual_source_right_subspace=list(exact.basis(E)),
                actual_target_canonical_subspace=list(exact.basis(F)),
                complete_Pauli_generators_checked=2*n,exact_global_coefficient_checked=True)


def matrix_product(A,B):
    size=len(A)
    result=[[(0,0)]*size for _ in range(size)]
    for x in range(size):
        for y in range(size):
            value=(0,0)
            for k in range(size):
                term=exact.multiply_gaussian(A[x][k],B[k][y])
                value=(value[0]+term[0],value[1]+term[1])
            result[x][y]=value
    return result


def literal_relative_matrix(E,F,n):
    # F_F*C_full*F_E^-1, exact integer numerator and power-two grid.
    a=exact.reference.frame_matrix(E,n)
    b=exact.reference.frame_matrix(F,n)
    c=exact.reference.frame_matrix(full(n),n)
    adjoint=[[(a['numerator'][y][x][0],-a['numerator'][y][x][1])
              for y in range(1<<n)] for x in range(1<<n)]
    return (matrix_product(b['numerator'],matrix_product(c['numerator'],adjoint)),
            len(E)+len(F)+n)


def small_probe(n):
    spaces=exact.reference.all_subspaces(n)
    entries=transitions=0
    digest=sha256()
    for E in spaces:
        R=exact.reference.perpendicular(E,n)
        gauge=reflection_gauge(E,n)
        matrix,grid=literal_relative_matrix(E,R,n)
        for x in range(1<<n):
            for y in range(1<<n):
                wanted=tuple(v << grid for v in exact.reconstructed_entry(gauge,x,y))
                if matrix[x][y]!=wanted:
                    raise AssertionError('Reflected monomial gauge matrix failed')
        entries+=(1<<n)**2
        digest.update(json.dumps(gauge,sort_keys=True).encode())
    # Every odd endpoint and every nested donor to its RIGHT birth.
    for T in range(1,1<<n):
        if T.bit_count()%2==0:
            continue
        R=exact.reference.perpendicular((T,),n)
        for E in spaces:
            if len(exact.basis(E+R))!=len(R):
                continue
            normal=compile_canonical_to_right(E,(T,),n)
            simple=exact.compile_interface(E,R,n)
            simple['output_affine_offset']^=T
            # Compare actual coefficients; redundant metadata may differ.
            for x in range(1<<n):
                for y in range(1<<n):
                    if exact.reconstructed_entry(normal,x,y)!=exact.reconstructed_entry(simple,x,y):
                        raise AssertionError('Pinned odd RIGHT birth is not X_T*F_(Tperp)')
            if normal['selected_rank_per_column']!=n-1-len(E):
                raise AssertionError('Nested RIGHT birth lost its geodesic width')
            entries+=(1<<n)**2;transitions+=1
    sample=reflection_gauge((3,),n)
    corrupted=json.loads(json.dumps(sample))
    corrupted['output_affine_offset']^=1
    try:
        exact.assert_complete_tableau(corrupted,reflected_word((3,),n))
    except AssertionError:
        pass
    else:
        raise AssertionError('Unpaid reflection gauge negative was accepted')
    return dict(n=n,all_reflected_gauges=len(spaces),complete_matrix_entries=entries,
                all_odd_nested_right_births=transitions,
                gauge_sha256=digest.hexdigest(),wrong_gauge_rejected=True)


def large_probe(n):
    rng=random.Random(127003+n)
    random_rows=[]
    while len(random_rows)<n//3:
        value=rng.randrange(1,1<<n)
        if len(exact.basis(random_rows+[value]))>len(random_rows):
            random_rows.append(value)
    even_pairs=tuple(3<<(2*j) for j in range(n//2))
    cases=[(),full(n),(7,),exact.reference.perpendicular((7,),n),even_pairs,tuple(random_rows)]
    digest=sha256()
    for E in cases:
        gauge=reflection_gauge(E,n)
        if gauge['selected_rank_per_column']:
            raise AssertionError('Reflection gauge acquired an unpaid C child')
        digest.update(json.dumps(gauge,sort_keys=True).encode())
    T=7
    donor=exact.reference.perpendicular((T,),n)[:n//2]
    birth=compile_canonical_to_right(donor,(T,),n)
    reverse=compile_right_to_canonical(donor,(T,),n)
    expected=n-1-len(donor)
    if birth['selected_rank_per_column']!=expected or reverse['selected_rank_per_column']!=expected:
        raise AssertionError('Forward/reverse nested reflected interfaces have wrong rank')
    return dict(n=n,seed=127003+n,reflected_gauges=len(cases),
                complete_generator_images=(len(cases)+2)*2*n,
                exact_global_coefficients=True,degenerate_even_pair_case=True,
                nested_forward_reverse_rank=expected,
                gauge_sha256=digest.hexdigest(),full_address_arrays_allocated=False)


def run_case(case):
    return small_probe(case) if case<5 else large_probe(case)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    args=parser.parse_args()
    if not 1<=args.workers<=4:
        raise ValueError('Use one to four workers')
    files=[Path(__file__),Path(exact.__file__),Path(exact.reference.__file__)]
    if sha256(files[1].read_bytes()).hexdigest()!=COMPILER_SHA or \
            sha256(files[2].read_bytes()).hexdigest()!=exact.REFERENCE_SHA:
        raise AssertionError('Pinned actual-frame compiler dependencies changed')
    hashes={file.name:sha256(file.read_bytes()).hexdigest() for file in files}
    protocol=dict(started_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                  native_threads_each=1,source_sha256=hashes,large_seed_rule='127003+n',
                  scope='Actual monomial reflection gauges and one-child interface metadata only; native complete-stream routing and stock remain paid obligations.')
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    timer=perf_counter()
    cases=[3] if args.bounded else [3,4,16,32,64]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results=list(pool.map(run_case,cases))
    if any(sha256(file.read_bytes()).hexdigest()!=hashes[file.name] for file in files):
        raise AssertionError('Effective source changed during reflection controls')
    certificate=dict(status='PASS RIGHT REFLECTED ACTUAL-FRAME GAUGES',protocol=protocol,
                     completed_utc=datetime.now(timezone.utc).isoformat(),
                     elapsed_seconds=perf_counter()-timer,cases=results,
                     scope='Exact finite physical phase interfaces and an all-size algebraic construction. No native payload bound, helper-capacity saving or new kappa is certified.')
    if args.output:
        (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(certificate,indent=2),flush=True)


if __name__=='__main__':
    main()
