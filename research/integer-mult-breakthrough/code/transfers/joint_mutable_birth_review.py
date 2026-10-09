#!/usr/bin/env python3
"""Independent complete dirty review of a genuinely joint mutable-source word.

The fixture is consumed as data. Literal Gaussian operators, clean suffix
matrices, current-data preimages and final mutable-data cleanup are derived
without importing the producer. Every paid child and monomial is bound.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import degenerate_birth_review as arithmetic
import degenerate_birth_fixture_review as hashes
g = arithmetic.g
TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/joint-mutable-birth-review.json'


def scalar_inverse(matrix):
    n = len(matrix)
    rows = [[Q(x) for x in row]+[Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None: raise ValueError('Singular current-data derivative')
        rows[column], rows[pivot] = rows[pivot], rows[column]
        c = rows[column][column]; rows[column] = [x/c for x in rows[column]]
        for i in range(n):
            if i != column and rows[i][column]:
                c = rows[i][column]; rows[i] = [x-c*y for x, y in zip(rows[i], rows[column])]
    return [row[n:] for row in rows]


def clean_word(S):
    a, b = S[0][1], S[1][0]
    if S != [[1, a], [b, 1+a*b]]: raise ValueError('Retained S has a different unit-shear factorization')
    inverse = [[Q(1+a*b), Q(-a)], [Q(-b), Q(1)]]
    out = []
    for source, target, matrix, sign in ((0, 2, S, 1), (2, 0, inverse, -1), (0, 2, S, 1)):
        out += [('birth', 4), ('birth', 5)]
        out += [('add', 4+i, source+j, Q(matrix[i][j])) for i in range(2) for j in range(2) if matrix[i][j]]
        out += [('add', target+i, 4+i, Q(sign)) for i in range(2)]
    return out, inverse


def suffix_response(events, index, cuts=True):
    # Fresh forward suffix, rather than the producer's backward recurrence.
    rows = [[Q(i == j) for j in range(6)] for i in range(6)]
    for event in events[index+1:]:
        if event[0] == 'birth':
            if cuts: rows[event[1]] = [Q(0)]*6
        else:
            _, a, b, c = event; rows[a] = [x+c*y for x, y in zip(rows[a], rows[b])]
    role = events[index][1]
    D = [row[role] for row in rows[:4]]
    G = [row[:4] for row in rows[:4]]
    inverse = scalar_inverse(G)
    preimage = [sum(x*y for x, y in zip(row, D)) for row in inverse]
    return D, preimage


def generic_frame(columns):
    routing = [[g.ONE if a == arithmetic.embed(b, columns) else g.ZERO for b in range(16)] for a in range(16)]
    diagonal = [[g.power(g.IMAGINARY, -a.bit_count()) if a == b else g.ZERO for b in range(16)] for a in range(16)]
    H = g.identity(16)
    for bit in range(2):
        S = [[g.IMAGINARY if a == b and a >> bit & 1 else g.ONE if a == b else g.ZERO for b in range(16)] for a in range(16)]
        H = g.matmul(g.matmul(g.matmul(S, arithmetic.line(1 << bit)), S), H)
    return g.matmul(diagonal, g.matmul(routing, g.matmul(H, g.matmul(g.adjoint(routing), diagonal))))


def frames():
    out = arithmetic.literal_frames()
    out['G'] = generic_frame([6, 8, 1, 2])
    out['R'] = g.matmul(out['G'], out['F'])
    out['gauge'] = g.matmul(out['R'], g.adjoint(out['E']))
    if any(sum(x != g.ZERO for x in row) != 1 for row in out['gauge']):
        raise ValueError('Reflection gauge has a hidden mixing child')
    return out


def retained_normal(form, negative=None):
    r = form['selected_rank_per_column']; mask = (1 << r)-1
    if not 0 <= r <= 4 or form['one_bulk_child_calls'] != int(r > 0):
        raise ValueError('Retained one-child call count differs from selected rank')
    offset = 0 if negative == 'affine' else form['output_affine_offset']
    outputs = [offset ^ arithmetic.embed(a, form['output_columns']) for a in range(16)]
    inputs = [arithmetic.embed(a, form['input_columns']) for a in range(16)]
    if sorted(outputs) != list(range(16)) or sorted(inputs) != list(range(16)):
        raise ValueError('Retained affine routing omits full records')
    for side in ('input', 'output'):
        if [hashes.chirp(form[side+'_quadratic'], a) for a in range(16)] != form[side+'_phase_exponents']:
            raise ValueError('Retained quadratic polynomial differs from complete phase table')
    result = [[g.ZERO]*16 for _ in range(16)]
    for a in range(16):
        for b in range(16):
            if a >> r != b >> r: continue
            phase = form['output_phase_exponents'][a]+form['input_phase_exponents'][b]
            if negative == 'global': phase -= form['output_quadratic']['constant']+form['input_quadratic']['constant']
            result[outputs[a]][inputs[b]] = g.multiply(g.power(g.IMAGINARY, phase), g.c_entry(r, a & mask, b & mask))
    return result


def physical_word(S, F, canonical=False):
    clean, inverse = clean_word(S); events = []; current = ['A1', 'A7']+['I']*4
    matrices = {}; ledger = Counter()
    def move(role, target):
        key = current[role]+'->'+target
        matrices[key] = g.matmul(F[target], g.adjoint(F[current[role]]))
        rank = arithmetic.normal_form(matrices[key])['selected_rank_per_column']
        if rank: ledger[rank] += 1
        events.append(('move', role, key)); current[role] = target
    def add(a, b, c, kind='add'):
        if c:
            if current[a] != current[b]: raise ValueError('A physical scalar gate has unequal actual operators')
            events.append((kind, a, b, Q(c)))
    for role in range(6): move(role, 'E')
    responses = {}
    for index, event in enumerate(clean):
        if index in (8, 16):
            undo = index == 16
            for role in range(6): events.append(('gauge', role, undo)); current[role] = 'E' if undo else 'R'
        if event[0] == 'birth':
            _, role = event; D, P = suffix_response(clean, index); responses[index] = (D, P)
            stage = index//8; target = 2 if stage != 1 else 0; sign = -1 if stage == 1 else 1
            if P != [Q(sign*(i == target+role-4)) for i in range(4)]:
                raise ValueError('Clean future current-data preimage differs from the local stage compensation')
            events.append(('birth', role, index))
            for target, c in enumerate(P): add(target, role, -c, 'compensation')
        else: _, a, b, c = event; add(a, b, c)
    for role in range(6): move(role, 'F')
    cleanup_start = len(events)
    for i in range(2):
        for j in range(2):
            add(4+i, 2+j, -(inverse[i][j]+Q(i == j)), 'cleanup')
            add(4+i, j, -(Q(S[i][j])-Q(i == j)), 'cleanup')
    if canonical:
        a, b = S[0][1], S[1][0]
        add(0, 1, a); add(1, 0, b)
        events += [('sign', 0, -1), ('sign', 1, -1)]
        add(3, 2, -b); add(2, 3, -a)
        for row, label in enumerate((1, 7)):
            events.append(('repair', 2+row, label)); ledger[1] += 1
            events.append(('exchange', row, 2+row))
    return dict(events=events, matrices=matrices, responses=responses, inverse=inverse,
                ledger=dict(sorted(ledger.items())), cleanup_start=cleanup_start, canonical=canonical)


def bind(case, F, spec):
    names = {'F0':'I', 'F1':'A1', 'F2':'A7', 'F3':'E', 'F4':'G', 'F5':'F'}
    if case['ambient_bits'] != 4 or case['payload_stock'] != 6 or case['source_line_labels'] != [1, 7]:
        raise ValueError('Complete initial stock/source labels differ')
    words = {'I':[], 'A1':[['C_line',1]], 'A7':[['C_line',7]], 'F':[['C_full',4]]}
    for name, columns in [('E',[1,6,2,8]),('G',[6,8,1,2])]:
        words[name] = [['quadratic_phase',-1,'weight-all-bits'],['linear_route_inverse',columns],['H_tilde',2],['linear_route',columns],['quadratic_phase',-1,'weight-all-bits']]
    for frame in case['frames']:
        name = names[frame['id']]
        if frame['literal_spec']['word'] != words[name]: raise ValueError('Retained actual frame word differs')
        if hashes.matrix_digest(F[name], frame['matrix_bits']) != frame['matrix_sha256']:
            raise ValueError('Independent frame hash differs')
    if retained_normal(case['reflection_gauge_normal_form']) != F['gauge']:
        raise ValueError('Retained reflection loses an affine/quadratic/global unit')
    if hashes.matrix_digest(F['gauge'],0) != case['reflection_gauge_matrix_sha256']:
        raise ValueError('Independent complete gauge hash differs')
    retained = case['canonical_physical_events'] if spec['canonical'] else case['core_physical_events']
    translated = []; child_entries = 0; affine_negative = global_negative = False
    for event in retained:
        kind = event[0]
        if kind == 'move_one_child':
            _, role, before, after, normal = event
            key = names[before]+'->'+names[after]
            actual = spec['matrices'][key]; candidate = retained_normal(normal)
            if candidate != actual: raise ValueError('Retained child differs from independent literal interface')
            child_entries += 256; translated.append(('move',role,key))
        elif kind == 'raw_source_line_one_child':
            _, role, label, normal = event
            candidate = retained_normal(normal)
            if candidate != F['A'+str(label)]: raise ValueError('Raw source repair differs from literal C line')
            child_entries += 256; translated.append(('repair',role,label))
        elif kind == 'rank_zero_reflected_gauge': translated.append(('gauge',event[1],event[2]))
        elif kind == 'birth_keep_old_value': translated.append(('birth',event[1],event[2]))
        elif kind == 'native_constant_sign': translated.append(('sign',event[1],event[2]))
        elif kind == 'native_full_bank_exchange': translated.append(('exchange',event[1],event[2]))
        else:
            label = {'birth_current_data_compensation':'compensation','final_mutable_preimage_cleanup':'cleanup','add':'add'}[kind]
            translated.append((label,event[1],event[2],Q(*event[3])))
        if kind in ('move_one_child','raw_source_line_one_child'):
            if normal['output_affine_offset']: affine_negative |= retained_normal(normal,'affine') != candidate
            if sum(normal[side+'_quadratic']['constant'] for side in ('input','output'))%4:
                global_negative |= retained_normal(normal,'global') != candidate
    if translated != spec['events']: raise ValueError('Complete retained physical event chronology differs')
    for index, response in case['cut_future_responses'].items():
        D, P = spec['responses'][int(index)]
        if [Q(*x) for x in response['future_response']] != D or [Q(*x) for x in response['current_data_preimage']] != P:
            raise ValueError('Independent forward suffix/current preimages differ')
    if not affine_negative or not global_negative: raise ValueError('Child affine/global controls did not discriminate')
    prefix = [[Q(i == j) for j in range(6)] for i in range(6)]; peak = 1; max_event = None
    scalar_gates = unit_expansion = 0
    for index, event in enumerate(spec['events']):
        if event[0] in ('add','compensation','cleanup'):
            _, a, b, c = event; prefix[a] = [x+c*y for x,y in zip(prefix[a],prefix[b])]
            scalar_gates += 1; unit_expansion += abs(c.numerator)
            value = max(sum(abs(x) for x in row) for row in prefix)
            if value > peak: peak = value; max_event = index
        elif event[0] == 'sign': prefix[event[1]] = [-x for x in prefix[event[1]]]
    if spec['canonical'] and (str(peak) != case['exact_scalar_only_prefix_row_l1'] or max_event != case['maximum_scalar_prefix_event']):
        raise ValueError('Retained scalar-only prefix bound differs')
    key = 'canonical' if spec['canonical'] else 'core'
    if spec['ledger'] != {int(t):n for t,n in case[key+'_histogram'].items()}:
        raise ValueError('Every paid child/complete-stock ledger differs')
    if scalar_gates != case[key+'_scalar_bank_gates'] or unit_expansion != case[key+'_unit_shear_expansion']:
        raise ValueError('Complete scalar gate bill differs')
    return dict(every_event_bound=True,paid_child_matrix_coefficients=child_entries,
        reflection_matrix_coefficients=256,scalar_bank_gates=scalar_gates,unit_shear_expansion=unit_expansion,
        scalar_only_prefix_peak=str(peak),actual_operator_prefix_not_claimed=True,
        affine_and_global_child_mutations_rejected=True)


def replay(spec, initial, columns, F, negative=None):
    data = [list(row) for row in initial]; births = []
    for index, event in enumerate(spec['events']):
        kind = event[0]
        if kind == 'move':
            data[event[1]] = arithmetic.apply(data[event[1]],spec['matrices'][event[2]],columns)
        elif kind == 'gauge':
            matrix = g.adjoint(F['gauge']) if event[2] else F['gauge']
            if negative == 'omit helper gauge phase' and event[1] == 4 and not event[2]:
                matrix = [[g.ONE if x != g.ZERO else g.ZERO for x in row] for row in matrix]
            data[event[1]] = arithmetic.apply(data[event[1]],matrix,columns)
        elif kind == 'birth': births.append((event[2],list(data[event[1]])))
        elif kind == 'repair':
            if negative != 'omit source line': data[event[1]] = arithmetic.apply(data[event[1]],F['A'+str(event[2])],columns)
        elif kind == 'sign': data[event[1]] = [arithmetic.scale(x,Q(event[2])) for x in data[event[1]]]
        elif kind == 'exchange': data[event[1]],data[event[2]] = data[event[2]],data[event[1]]
        else:
            _, a,b,c = event
            if negative == 'omit second compensation' and kind == 'compensation' and index == 23: continue
            if negative == 'future output debit' and kind == 'compensation':
                birth_index = births[-1][0]; D,_ = spec['responses'][birth_index]
                # Replace the complete current-data vector at its first gate.
                if (birth_index,a) in ((0,2),(1,3),(8,0),(9,1),(16,2),(17,3)):
                    for target, coefficient in enumerate(D):
                        if coefficient: data[target] = arithmetic.plus(data[target],data[b],-coefficient)
                    continue
            if negative == 'wrong mutable cleanup' and kind == 'cleanup':
                # Replace the complete cleanup once by historical-source coefficients.
                if index == spec['cleanup_start']:
                    S = spec['S']; I = spec['inverse']
                    for row in range(2):
                        for column in range(2):
                            data[4+row] = arithmetic.plus(data[4+row],data[column],-2*Q(S[row][column]))
                            data[4+row] = arithmetic.plus(data[4+row],data[2+column],-I[row][column])
                continue
            data[a] = arithmetic.plus(data[a],data[b],c)
    return data,births


def expected(spec, initial, columns, F):
    if spec['canonical']: virtual = initial
    else:
        x = [arithmetic.apply(initial[i],g.adjoint(F['A'+str((1,7)[i])]),columns) for i in range(2)]
        zero = [g.ZERO]*len(initial[0]); virtual=[]
        for i in range(2):
            value=list(zero)
            for j in range(2): value=arithmetic.plus(value,initial[2+j],-spec['inverse'][i][j])
            virtual.append(value)
        for i in range(2):
            value=list(zero)
            for j in range(2): value=arithmetic.plus(value,x[j],Q(spec['S'][i][j]))
            virtual.append(value)
        virtual += initial[4:]
    return [arithmetic.apply(row,F['F'],columns) for row in virtual]


def review(payload):
    case, columns = payload; started=time.monotonic(); F=frames(); summaries=[]
    for canonical in (False,True):
        spec=physical_word(case['S'],F,canonical);spec['S']=case['S'];binding=bind(case,F,spec)
        size=1<<(4*columns); checked=dependent=0;digest=sha256()
        for bank in range(6):
            for address in range(size) if columns==1 else (0,):
                initial=[[g.ZERO]*size for _ in range(6)];initial[bank][address]=g.ONE
                actual,births=replay(spec,initial,columns,F)
                if actual!=expected(spec,initial,columns,F): raise ValueError('An independent complete physical column failed')
                if bank<4 and any(index>=8 and any(value != g.ZERO for value in data) for index,data in births): dependent+=1
                digest.update(str(actual).encode());checked+=1
        for field in range(3):
            initial=[[(Q((a*7+bank*11+field*3)%31-15,1<<(bank%3)),Q((a*13+bank*5+field*17)%29-14,1<<((bank+field)%4))) for a in range(size)] for bank in range(6)]
            actual,_=replay(spec,initial,columns,F);wanted=expected(spec,initial,columns,F)
            if actual!=wanted: raise ValueError('An independent complete Gaussian dirty field failed')
            digest.update(str(actual).encode())
        controls={name:replay(spec,initial,columns,F,name)[0]!=wanted for name in ('omit second compensation','future output debit','wrong mutable cleanup','omit helper gauge phase')}
        if canonical: controls['omit source line']=replay(spec,initial,columns,F,'omit source line')[0]!=wanted
        if not all(controls.values()) or not dependent: raise ValueError('A mutable-source/cut/phase control did not discriminate')
        if all(wanted[bank]==initial[bank] for bank in (4,5)): raise ValueError('Wrong raw identity dirty endpoint was not rejected')
        rank=sum(r*n for r,n in spec['ledger'].items())
        if rank != (24 if canonical else 22): raise ValueError('Complete paid rank differs')
        clean,_=clean_word(case['S']);odd=[]
        for index,event in enumerate(clean):
            if event[0]=='birth':
                _,preimage=suffix_response(clean,index,False)
                odd += [str(x) for x in preimage if x.denominator & (x.denominator-1)]
        if not odd: raise ValueError('No-CUT forbidden-domain control did not discriminate')
        summaries.append(dict(canonical=canonical,payload_stock=6,columns=columns,explicit_physical_columns=checked,
            all_f1_physical_columns=columns==1,complete_Gaussian_dirty_fields=3,
            genuinely_source_dependent_later_births=dependent,rank=rank,capacity=24,deficit=24-rank,
            complete_child_histogram=spec['ledger'],all_helpers_visit_full_once=True,
            arbitrary_virtual_dirty_restored=True,actual_dirty_endpoint='C_full times original dirty',
            clean_forward_suffix_cut_bound=True,no_CUT_forbidden_odd_preimages=sorted(set(odd)),
            fixture_binding=binding,negative_controls=controls,output_sha256=digest.hexdigest()))
    return dict(S=case['S'],columns=columns,variants=summaries,seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());fixture=TOPIC/config['fixture']
    helpers=[Path(arithmetic.__file__).resolve(),Path(hashes.__file__).resolve(),Path(g.__file__).resolve()]
    paths=[Path(__file__).resolve(),CONFIG,fixture]+helpers
    for path,digest in config['pinned_inputs'].items():
        if sha256((TOPIC/path).read_bytes()).hexdigest()!=digest:raise ValueError('Pinned fixture or independent helper changed')
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_fixture_sha256=pins,
        seed=None,scope=config['scope'],producer_imports=False,column_layout='column-major; finite tensor permutation conjugate to fixture bit-major, not a native transpose')
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic();cases=[(case,f) for f in ([1] if args.small else [1,2]) for case in json.loads(fixture.read_text())['cases']]
    with ProcessPoolExecutor(max_workers=args.workers) as pool: rows=list(pool.map(review,cases))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest()!=digest for path,digest in pins.items()):raise ValueError('Source changed during immutable review')
    result=dict(status='INDEPENDENT JOINT MUTABLE BIRTH COMPLETE REVIEW PASS',cases=rows,seconds=time.monotonic()-started,
        scope=config['scope'],native_precision_or_routing_theorem=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','seconds','scope')}))


if __name__=='__main__':main()
