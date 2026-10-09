#!/usr/bin/env python3
"""Import-free exact column-branching bound for the retained four ports.

The source independently builds the actual Fourier/chirp matrices from the
small immutable fixture. A common-frame adapter's support expands by at
most 2^r for each C^r child; monomial and diagonal wrappers do not expand it.
Two crossed port products certify the already-attained minimum rank five.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time


FIXTURE_SHA = '8ae3dd3489d18251dd540e2d7e5925c00e61f830bd67b6de9308df381894d96f'
UNITS = ((1,0),(0,1),(-1,0),(0,-1))


def multiply(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def product(A,B):
    M,g = A
    N,h = B
    out = []
    for row in M:
        values = []
        for col in range(len(N)):
            x=y=0
            for a,R in zip(row,N):
                u,v = multiply(a,R[col])
                x,y = x+u,y+v
            values.append((x,y))
        out.append(values)
    return out,g+h


def adjoint(A):
    M,g = A
    return [[(M[j][i][0],-M[j][i][1]) for j in range(len(M))] for i in range(len(M))],g


def quadratic(A,x):
    n = len(A)
    return (sum(A[j][j]*(x >> j & 1) for j in range(n))
            +sum(2*A[i][j]*(x >> i & 1)*(x >> j & 1)
                 for i in range(n) for j in range(i+1,n))) % 4


def fourier_chirp(A):
    n = len(A)
    size = 1 << n
    convolution = []
    for d in range(size):
        a=b=0
        for z in range(size):
            u,v = UNITS[quadratic(A,z)]
            sign = -1 if (d&z).bit_count() & 1 else 1
            a,b = a+sign*u,b+sign*v
        convolution.append((a,b))
    return [[convolution[x^y] for x in range(size)] for y in range(size)],n


def Htilde(n,bit):
    size = 1 << n
    rows = [[(0,0)]*size for _ in range(size)]
    for x in range(size):
        for y in (x,x^(1 << bit)):
            sign = -1 if (x&y) >> bit & 1 else 1
            rows[y][x] = (sign,sign)
    return rows,1


def support(A):
    M,_ = A
    return [sum(row[j]!=(0,0) for row in M) for j in range(len(M))]


def maxsupport(A):
    return max(support(A))


def unitary(A):
    M,g = product(A,adjoint(A))
    return all(value==((1 << g,0) if i==j else (0,0))
               for i,row in enumerate(M) for j,value in enumerate(row))


def c_width(A):
    counts = support(A)
    q = counts[0]
    if any(value!=q for value in counts) or not q or q & (q-1):
        raise AssertionError('attaining adapter did not have uniform power-two support')
    return q.bit_length()-1


def run(bounded):
    fixture = Path(__file__).parents[2]/'fixtures/complex/noncommuting-four-incidence.json'
    if sha256(fixture.read_bytes()).hexdigest()!=FIXTURE_SHA:
        raise AssertionError('physical port fixture changed')
    data = json.loads(fixture.read_text())
    n = data['n']
    ports = [fourier_chirp(A) for A in data['incoming_symmetric_matrices']+data['outgoing_symmetric_matrices']]
    if not all(unitary(port) for port in ports):
        raise AssertionError('independent Fourier/chirp ports are not exact unitaries')
    crosses = []
    for out,inc,expected in ((3,0,8),(2,1,4)):
        actual = product(ports[out],adjoint(ports[inc]))
        degrees = support(actual)
        if degrees != [expected]*(1 << n):
            raise AssertionError('crossed column support premise differs from eight/four')
        crosses.append(dict(output_port=out,input_port=inc,column_supports=degrees,
                            maximum_column_support=expected,necessary_adapter_width=expected.bit_length()-1,
                            literal_matrix=actual[0],literal_grid_bits=actual[1]))
    # This is the original concrete attaining common operator, not a label-
    # only substitute. Temporal Htilde_onbit2 then K_code3 gives K3*Htilde2.
    common = product(ports[0],Htilde(n,2))
    if not unitary(common):
        raise AssertionError('retained original common representative is not unitary')
    incoming = [product(common,adjoint(port)) for port in ports[:2]]
    outgoing = [product(port,adjoint(common)) for port in ports[2:]]
    ranks = [c_width(A) for A in incoming+outgoing]
    if ranks != [1,1,1,2]:
        raise AssertionError('original exact five-width representative was not retained')
    for out,inc,expected in ((1,0,8),(0,1,4)):
        if maxsupport(product(outgoing[out],incoming[inc]))!=expected:
            raise AssertionError('crossed source/sink product does not cancel the common representative')
    seed = 202610090409
    rng = Random(seed)
    controls = 64 if bounded else 1024
    for _ in range(controls):
        matrices = []
        for _ in range(2):
            rows = [[(rng.randrange(-2,3),rng.randrange(-2,3))
                     if rng.randrange(3)==0 else (0,0) for _ in range(8)] for _ in range(8)]
            matrices.append((rows,0))
        A,B = matrices
        if maxsupport(product(A,B)) > maxsupport(A)*maxsupport(B):
            raise AssertionError('column support submultiplicativity control failed')
    # Cancellations may reduce support, so using equality rather than the
    # upper bound is observably wrong even for two nonzero unitaries.
    C = ([[ (1,1),(1,-1)],[(1,-1),(1,1)]],1)
    if maxsupport(product(C,adjoint(C))) != 1 or maxsupport(C)*maxsupport(adjoint(C)) != 4:
        raise AssertionError('strict-cancellation negative control did not distinguish equality')
    return dict(status='PASS EXACT LOCAL COLUMN-BRANCHING BOUND',fixture_sha256=FIXTURE_SHA,
                independent_port_formula='K_A[y,x]=2^-n sum_z i^q_A(z) (-1)^((x xor y) dot z)',
                crossed_products=crosses,necessary_total_width=sum(c['necessary_adapter_width'] for c in crosses),
                attaining_original_common_word='K_code3 * Htilde_onbit2',attaining_edge_widths=ranks,
                known_lower_bound_attained=True,seed=seed,seeded_support_controls=controls,
                cancellation_equality_negative=True,
                hypothesis_interface='Each single-bank adapter is a product of C^r children and arbitrary monomial/diagonal wrappers; its charge includes the sum of all child widths.',
                scope='Any invertible common address frame with the four fixed physical ports. Multiple helpers, altered ports/chronology and nonstandard children are outside this bound.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    before = sha256(Path(__file__).read_bytes()).hexdigest()
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    result = run(args.bounded)
    if sha256(Path(__file__).read_bytes()).hexdigest()!=before:
        raise AssertionError('source changed during execution')
    result.update(started_utc=utc,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=before,seconds=time.monotonic()-started,bounded=args.bounded)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','necessary_total_width','attaining_edge_widths','seeded_support_controls','seconds')}),flush=True)


if __name__ == '__main__':
    main()
