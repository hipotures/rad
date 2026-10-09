#!/usr/bin/env python3
"""Literal nonlinear matching-frame screen with certified one-child edges.

An admitted matrix is reconstructed as input unit phases/permutation, one
C^tensor r child, output permutation/unit phases. The permutations are kept
as data and exactly synthesized into affine-conjugated three-bit Toffolis.
Native use is conditional on an existing fourth complete guarded address
slot; this finite operator screen does not supply that whole-stream layout.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import lagrangian_frame_interfaces as general
import native_frame_wrapper_plan as wrappers


GENERAL_SHA = '1b9bce1af1b7ac39eafa9e765c5e58b362875ec0df1f81e91c80ada5d666b109'
WRAPPER_SHA = '3b2fa9fb3e992104ffdde75f5bbd407782691792c9189cf875324a509b1b069d'
WITNESS_SHA = '8ae3dd3489d18251dd540e2d7e5925c00e61f830bd67b6de9308df381894d96f'
UNITS = ((1,0),(0,1),(-1,0),(0,-1))


def multiply(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def matrix_product(A,B):
    M,g = A
    N,h = B
    size = len(M)
    out = []
    for row in range(size):
        values = []
        for col in range(size):
            x=y=0
            for j in range(size):
                a,b = multiply(M[row][j],N[j][col])
                x,y = x+a,y+b
            values.append((x,y))
        out.append(values)
    return out,g+h


def adjoint(A):
    M,g = A
    return [[(M[j][i][0],-M[j][i][1]) for j in range(len(M))] for i in range(len(M))],g


def matrix_word(word,n):
    columns,grid = [],None
    for x in range(1 << n):
        column,g = general.literal_column(word,n,x)
        if grid is not None and grid != g:
            raise AssertionError('literal matrix uses inconsistent grids')
        grid = g
        columns.append(column)
    return [[columns[x][y] for x in range(1 << n)] for y in range(1 << n)],grid


def graph_word(A):
    n = len(A)
    Q = dict(constant=0,linear=[A[j][j] for j in range(n)],
             cross=[[i,j,2] for i in range(n) for j in range(i+1,n) if A[i][j]])
    return ([('H',j,-1) for j in range(n)]+[('Q',Q)]+[('H',j,1) for j in range(n)])


def retained_ports():
    path = Path(__file__).parents[2]/'fixtures/complex/noncommuting-four-incidence.json'
    if sha256(path.read_bytes()).hexdigest() != WITNESS_SHA:
        raise AssertionError('original four physical ports changed')
    fixture = json.loads(path.read_text())
    n = fixture['n']
    return fixture,[matrix_word(graph_word(A),n) for A in
                    fixture['incoming_symmetric_matrices']+fixture['outgoing_symmetric_matrices']]


def matchings(remaining):
    if not remaining:
        yield ()
        return
    a = remaining[0]
    for j in range(1,len(remaining)):
        b = remaining[j]
        rest = remaining[1:j]+remaining[j+1:]
        for suffix in matchings(rest):
            yield ((a,b),)+suffix


def matching_matrix(pairs,size):
    matrix = [[(0,0)]*size for _ in range(size)]
    for a,b in pairs:
        matrix[a][a] = matrix[b][b] = (1,1)
        matrix[a][b] = matrix[b][a] = (1,-1)
    return matrix,1


def toffoli(x):
    return x ^ int((x & 6) == 6)


def nonlinear_wrap(A,mode):
    M,g = A
    out = [[M[toffoli(y) if mode in ('left','conjugate') else y]
               [toffoli(x) if mode in ('right','conjugate') else x]
            for x in range(len(M))] for y in range(len(M))]
    return out,g


def unit_exponent(value,grid,rank,alpha):
    for e,u in enumerate(UNITS):
        a,b = multiply(alpha,u)
        if (value[0] << rank,value[1] << rank) == (a << grid,b << grid):
            return e
    return None


def factor_one_child(A):
    """Admit only complete flat blocks equivalent to the binary Walsh table.

    Dephasing one row/column turns C^r into a real Walsh character table. Its
    rows form an elementary abelian sign group. Group closure plus distinct
    column characters yields actual input/output coordinates and all gauges;
    reconstructing every original coefficient is the final acceptance test.
    """
    matrix,grid = A
    size = len(matrix)
    rows = [tuple(j for j,v in enumerate(row) if v != (0,0)) for row in matrix]
    columns = [tuple(i for i in range(size) if matrix[i][j] != (0,0)) for j in range(size)]
    q = len(rows[0])
    if not q or q & (q-1) or any(len(row)!=q for row in rows) or any(len(col)!=q for col in columns):
        return None,'nonuniform support degree'
    rank = q.bit_length()-1
    alpha = (1,0)
    for _ in range(rank):
        alpha = multiply(alpha,(1,1))
    phase = [[None]*size for _ in range(size)]
    for i in range(size):
        for j in rows[i]:
            phase[i][j] = unit_exponent(matrix[i][j],grid,rank,alpha)
            if phase[i][j] is None:
                return None,'nonuniform Gaussian-dyadic magnitude or non-fourth-root gauge'
    input_route = [-1]*size
    output_route = [-1]*size
    input_phase = [0]*size
    output_phase = [0]*size
    unseen = set(range(size))
    blocks = []
    while unseen:
        first = min(unseen)
        C = list(rows[first])
        R = list(columns[C[0]])
        if len(R)!=q or any(rows[i] != tuple(C) for i in R) or any(columns[j] != tuple(R) for j in C):
            return None,'support component is not a complete square block'
        unseen.difference_update(R)
        signs = []
        for i in R:
            mask = 0
            for bit,j in enumerate(C):
                e = (phase[i][j]-phase[i][C[0]]-phase[R[0]][j]+phase[R[0]][C[0]]) % 4
                if e not in (0,2):
                    return None,'dephased table is not real Walsh'
                mask |= (e//2) << bit
            signs.append(mask)
        stock = set(signs)
        if len(stock)!=q or any(a^b not in stock for a in stock for b in stock):
            return None,'dephased rows do not form a Walsh character group'
        basis = general.exact.basis(signs)
        if len(basis)!=rank:
            return None,'Walsh sign-group rank differs from selected width'
        row_coordinates = [general.exact.coordinates(mask,basis,q) for mask in signs]
        column_coordinates = [sum((b >> bit & 1) << a for a,b in enumerate(basis)) for bit in range(q)]
        if len(set(row_coordinates))!=q or len(set(column_coordinates))!=q:
            return None,'Walsh character coordinates are not bijective'
        block = len(blocks)
        for i,a in zip(R,row_coordinates):
            output_route[(block << rank)|a] = i
            output_phase[i] = (phase[i][C[0]]+a.bit_count()) % 4
        for j,b in zip(C,column_coordinates):
            input_route[j] = (block << rank)|b
            input_phase[j] = (phase[R[0]][j]-phase[R[0]][C[0]]+b.bit_count()) % 4
        blocks.append(dict(rows=R,columns=C))
    if sorted(input_route)!=list(range(size)) or sorted(output_route)!=list(range(size)):
        raise AssertionError('admitted route drops or duplicates an address')
    plan = dict(n=size.bit_length()-1,rank=rank,input_route=input_route,output_route=output_route,
                input_phase=input_phase,output_phase=output_phase,
                global_units='Included exactly once in the retained phase arrays.',
                blocks=blocks)
    if not reconstructed_equal(plan,A):
        raise AssertionError('Walsh-equivalent block factoring did not reconstruct literal coefficients')
    return plan,None


def reconstructed_equal(plan,A):
    M,g = A
    r = plan['rank']
    alpha = (1,0)
    for _ in range(r):
        alpha = multiply(alpha,(1,1))
    inverse_out = [0]*len(M)
    for k,v in enumerate(plan['output_route']):
        inverse_out[v] = k
    for i in range(len(M)):
        for j in range(len(M)):
            a,b = inverse_out[i],plan['input_route'][j]
            expected = (0,0)
            if a >> r == b >> r:
                e = (plan['output_phase'][i]+plan['input_phase'][j]
                     -((a^b)&((1 << r)-1)).bit_count()) % 4
                expected = multiply(alpha,UNITS[e])
            if (M[i][j][0] << r,M[i][j][1] << r) != (expected[0] << g,expected[1] << g):
                return False
    return True


def transpose_word(a,b,n):
    """Swap two three-bit addresses with one affine-conjugated Toffoli."""
    if n != 3 or a == b:
        raise ValueError('this exact finite router requires three distinct active bits')
    columns = [a^b]
    for j in range(n):
        if len(general.exact.basis(columns+[1 << j])) > len(columns):
            columns.append(1 << j)
    if len(columns)!=n:
        raise AssertionError('affine transposition basis did not complete')
    inverse = general.exact.inverse_columns(columns)
    offset = 6 ^ general.exact.embed(a,inverse)
    return [('GL',list(inverse)),('NOT',offset),('TOFFOLI',1,2,0),('NOT',offset),('GL',columns)]


def apply_route_word(word,x):
    for gate in word:
        if gate[0] == 'GL':
            x = general.exact.embed(x,gate[1])
        elif gate[0] == 'NOT':
            x ^= gate[1]
        else:
            x ^= ((x >> gate[1] & 1)*(x >> gate[2] & 1)) << gate[3]
    return x


def route_word(permutation):
    n = len(permutation).bit_length()-1
    if sorted(permutation)!=list(range(1 << n)):
        raise ValueError('whole address route must be a permutation')
    if n != 3:
        raise ValueError('only the exact three-bit route synthesis is claimed')
    current = list(range(1 << n))
    word = []
    for source,target in enumerate(permutation):
        if current[source] == target:
            continue
        a,b = current[source],target
        word += transpose_word(a,b,n)
        current = [b if value==a else a if value==b else value for value in current]
    if current != list(permutation) or any(apply_route_word(word,x)!=permutation[x] for x in range(len(current))):
        raise AssertionError('literal affine/Toffoli route word differs from retained permutation')
    return word


def execute_plan(plan,values,f=1):
    n,r = plan['n'],plan['rank']
    def phase(values,exponents):
        return [wrappers.routes.unit(value,sum(exponents[wrappers.column_vector(a,n,f,j)]
                                               for j in range(f))) for a,value in enumerate(values)]
    def route(values,permutation):
        def destination(a):
            for j in range(f):
                a = wrappers.replace_column(a,permutation[wrappers.column_vector(a,n,f,j)],n,f,j)
            return a
        return wrappers.routes.scatter(values,destination)
    values = phase(values,plan['input_phase'])
    values = route(values,plan['input_route'])
    for slot in range(r):
        for j in range(f):
            values = wrappers.C_factor(values,(n-slot-1)*f+j)
    values = route(values,plan['output_route'])
    values = phase(values,plan['output_phase'])
    return values,r*f


def tensor_reference(A,values,f=1):
    M,g = A
    n = len(M).bit_length()-1
    out = []
    for y in range(len(values)):
        fields = [0,0,0,0]
        for x,payload in enumerate(values):
            coefficient = (1,0)
            for j in range(f):
                coefficient = multiply(coefficient,M[wrappers.column_vector(y,n,f,j)]
                                         [wrappers.column_vector(x,n,f,j)])
            for pair in (0,2):
                a,b = multiply(coefficient,payload[pair:pair+2])
                fields[pair],fields[pair+1] = fields[pair]+a,fields[pair+1]+b
        out.append(tuple(fields))
    return out,g*f


def is_clifford(A):
    M,g = A
    n = len(M).bit_length()-1
    for j in range(n):
        for kind in ('X','Z'):
            if kind == 'X':
                MP = [[row[x ^ (1 << j)] for x in range(len(M))] for row in M]
            else:
                MP = [[tuple((-1 if x >> j & 1 else 1)*a for a in value)
                       for x,value in enumerate(row)] for row in M]
            N,ng = matrix_product((MP,g),adjoint(A))
            shift = None
            phases = []
            for x in range(len(M)):
                nonzero = [y for y in range(len(M)) if N[y][x]!=(0,0)]
                if len(nonzero)!=1:
                    return False
                y = nonzero[0]
                if shift is None:
                    shift = x^y
                if x^y != shift:
                    return False
                e = unit_exponent(N[y][x],ng,0,(1,0))
                if e is None:
                    return False
                phases.append(e)
            if not any(all(phases[x] == (phases[0]+2*general.exact.dot(z,x)) % 4
                           for x in range(len(M))) for z in range(len(M))):
                return False
    return True


def score(common,ports):
    relative = [matrix_product(common,adjoint(port)) for port in ports[:2]]
    relative += [matrix_product(port,adjoint(common)) for port in ports[2:]]
    plans,rejections = [],[]
    for A in relative:
        plan,reason = factor_one_child(A)
        plans.append(plan)
        rejections.append(reason)
    return (sum(p['rank'] for p in plans) if all(p is not None for p in plans) else None),plans,rejections,relative


def probe(task):
    family,bounded = task
    fixture,ports = retained_ports()
    n = fixture['n']
    candidates = []
    if family == 'matching':
        candidates = [(dict(matching_pairs=[list(p) for p in pairs]),matching_matrix(pairs,1 << n))
                      for pairs in matchings(tuple(range(1 << n)))]
    else:
        for L in general.all_lagrangians(n):
            word = general.frame_word(L,n)['actual_word']
            candidates.append((dict(source_lagrangian=list(L),source_actual_word=word,wrapper=family),
                               nonlinear_wrap(matrix_word(word,n),family)))
    if bounded:
        candidates = candidates[:3]
    rows = []
    retained = []
    minimum = None
    for label,common in candidates:
        value,plans,rejections,relative = score(common,ports)
        nonclifford = not is_clifford(common)
        row = dict(label=label,nonclifford=nonclifford,admitted=value is not None,
                   total_rank=value,edge_ranks=[None if p is None else p['rank'] for p in plans],
                   rejections=rejections)
        rows.append(row)
        if value is not None and (minimum is None or value < minimum):
            minimum = value
            retained = [dict(label=label,nonclifford=nonclifford,total_rank=value,edge_plans=plans,
                             common_matrix=common[0],common_grid=common[1])]
        elif value == minimum and value is not None and len(retained)<3:
            retained.append(dict(label=label,nonclifford=nonclifford,total_rank=value,edge_plans=plans,
                                 common_matrix=common[0],common_grid=common[1]))
    return dict(family=family,candidates=len(candidates),nonclifford=sum(r['nonclifford'] for r in rows),
                admitted=sum(r['admitted'] for r in rows),minimum=minimum,
                rank_histogram={str(value):sum(r['total_rank']==value for r in rows)
                                for value in sorted({r['total_rank'] for r in rows if r['total_rank'] is not None})},
                raw_cases=rows,retained=retained)


def retained_controls(cases):
    fixture,ports = retained_ports()
    n = fixture['n']
    original = general.exact.basis((v >> n)|((v & ((1 << n)-1)) << n)
                                   for v in fixture['common_lagrangian_basis'])
    baseline = matrix_word(general.frame_word(original,n)['actual_word'],n)
    value,plans,rejections,relative = score(baseline,ports)
    if value != 5:
        raise AssertionError('one-child nonlinear factoring did not retain the known exact five-rank baseline')
    representatives = [dict(label='retained-Clifford-five-rank-baseline',edge_plans=plans,
                             common_matrix=baseline[0],common_grid=baseline[1])]
    representatives += [entry for c in cases for entry in c['retained'][:1]]
    controls = []
    for entry in representatives:
        common = (entry['common_matrix'],entry['common_grid'])
        value,plans,_,matrices = score(common,ports)
        fields = 0
        route_gates = []
        for plan,A in zip(plans,matrices):
            plan['input_route_word'] = route_word(plan['input_route'])
            plan['output_route_word'] = route_word(plan['output_route'])
            route_gates.append(sum(g[0]=='TOFFOLI' for g in plan['input_route_word']+plan['output_route_word']))
            for f in (1,2):
                raw = [wrappers.routes.payload(a) for a in range(1 << (n*f))]
                actual,g = execute_plan(plan,raw,f)
                expected,eg = tensor_reference(A,raw,f)
                grid = max(g,eg)
                if [[v << (grid-g) for v in row] for row in actual] != [[v << (grid-eg) for v in row] for row in expected]:
                    raise AssertionError('retained nonlinear one-child wrapper differs from full literal tensor payload')
                fields += 4*len(raw)
            wrong = dict(plan,output_phase=list(plan['output_phase']))
            wrong['output_phase'][0] = (wrong['output_phase'][0]+1) % 4
            if reconstructed_equal(wrong,A):
                raise AssertionError('omitted/corrupt per-address unit negative did not discriminate')
        entry['edge_plans'] = plans
        controls.append(dict(label=entry['label'],total_rank=value,fields=fields,
                             route_toffoli_gates=route_gates,global_phase_negative=True,
                             scope='Literal whole f1/f2 four-field edge wrappers. Fourth guarded address companion and native stream/precision contract remain conditional.'))
    return representatives,controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    files = [Path(__file__),Path(general.__file__),Path(general.exact.__file__),Path(general.exact.reference.__file__),
             Path(wrappers.__file__),Path(wrappers.routes.__file__)]
    before = {p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if before[Path(general.__file__).name]!=GENERAL_SHA or before[Path(wrappers.__file__).name]!=WRAPPER_SHA:
        raise AssertionError('pinned exact dependencies changed')
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(family,args.bounded) for family in ('matching','left','right','conjugate')]
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe,tasks))
    representatives,controls = retained_controls(cases)
    if before != {p.name:sha256(p.read_bytes()).hexdigest() for p in files}:
        raise AssertionError('effective source changed during run')
    certificate = dict(status='PASS EXACT FINITE SCREEN',started_utc=utc,completed_utc=datetime.now(timezone.utc).isoformat(),
                       workers=args.workers,bounded=args.bounded,effective_sources=before,cases=cases,
                       retained_representatives=representatives,complete_edge_controls=controls,
                       seconds=time.monotonic()-started,
                       scope='Fixed three-bit nonlinear matching/common-frame families, complete one-C-child matrix certificates. No whole canonical multiplier, new kappa or unconditional native nonlinear routing claim.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(status=certificate['status'],candidates=sum(c['candidates'] for c in cases),
                          minima={c['family']:c['minimum'] for c in cases},
                          nonclifford=sum(c['nonclifford'] for c in cases),
                          fields=sum(c['fields'] for c in controls),seconds=certificate['seconds'])),flush=True)


if __name__ == '__main__':
    main()
