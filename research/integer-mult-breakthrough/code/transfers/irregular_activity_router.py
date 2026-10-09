#!/usr/bin/env python3
"""General-width switched-position compaction with twelve complete guards.

The fixed odd-size network and stock placement are authored here. Each local
XOR consumes the synthesis track's frozen eight-rotation/correction component.
Exact finite address-word composition is tested; native tape cost and faster
recursive zeta endpoints remain conditional, and no exponent is claimed.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import random
import time


TOPIC = Path(__file__).resolve().parents[2]
WORD = TOPIC/'code/synthesis/benes_guarded_control_word.py'
WORD_SHA = 'b3f85a39a2c737dd91ba9888b6fe94c2b6da79a3e386c75ba8cddd9dfd169242'
BASE = TOPIC/'code/synthesis/benes_control_fiber_probe.py'
BASE_SHA = '0090d94c72943abc24ac77bf01db254134f5c4d069fce47e53c7747fc470b02f'
if sha256(WORD.read_bytes()).hexdigest()!=WORD_SHA or sha256(BASE.read_bytes()).hexdigest()!=BASE_SHA:
    raise ValueError('Both frozen component sources must match')
SPEC=importlib.util.spec_from_file_location('irregular_router_packed_component',WORD)
w=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def invert_permutation(pi):
    if sorted(pi)!=list(range(len(pi))):
        raise ValueError('A complete bijective wire permutation is required')
    result=[0]*len(pi)
    for i,j in enumerate(pi):
        result[j]=i
    return tuple(result)


def permute_bits(value,pi):
    return sum(((value>>i)&1)<<j for i,j in enumerate(pi))


@lru_cache(maxsize=8192)
def irregular_layers(pi):
    """Alternate edge colors on input/output pair cycles and the odd path.

    The unpaired input and output wires, when present, are both routed through
    the ceil(n/2) subnet. Their single alternating path has equal endpoint
    colors; the disjoint cycles are even. No absent wire or address bit is added.
    """
    pi=tuple(pi)
    inverse=invert_permutation(pi)
    n=len(pi)
    if n<2:
        return ()
    if n==2:
        return (((0,1,int(pi[0]==1)),),)
    neighbors=[set() for unused in range(n)]
    for i in range(n):
        if i^1<n:
            neighbors[i].add(i^1)
        if pi[i]^1<n:
            neighbors[i].add(inverse[pi[i]^1])
    colors=[None]*n
    forced=(n-1,inverse[n-1]) if n%2 else ()
    for seed in tuple(forced)+tuple(range(n)):
        wanted=0 if seed in forced else (0 if colors[seed] is None else colors[seed])
        if colors[seed] is not None:
            require(colors[seed]==wanted,'The odd input/output path must have compatible endpoint colors')
            continue
        colors[seed]=wanted
        todo=[seed]
        while todo:
            i=todo.pop()
            for j in neighbors[i]:
                if colors[j] is None:
                    colors[j]=1-colors[i]
                    todo.append(j)
                else:
                    require(colors[j]==1-colors[i],'An alternating switch component cannot contain an odd cycle')
    child=[[-1]*((n+1)//2),[-1]*(n//2)]
    for i,j in enumerate(pi):
        require(child[colors[i]][i//2]==-1,'A subnet input must receive one wire')
        child[colors[i]][i//2]=j//2
    upper,lower=[irregular_layers(tuple(p)) for p in child]
    middle=[]
    for index in range(max(len(upper),len(lower))):
        layer=[]
        for color,plan in enumerate((upper,lower)):
            if index<len(plan):
                layer.extend((2*a+color,2*b+color,bit) for a,b,bit in plan[index])
        middle.append(tuple(layer))
    front=tuple((2*j,2*j+1,colors[2*j]) for j in range(n//2))
    back=tuple((2*j,2*j+1,colors[inverse[2*j]]) for j in range(n//2))
    return (front,*middle,back)


def complete_matching(layer,f):
    used=set()
    pairs=[]
    for a,b,bit in layer:
        require(0<=a<f and 0<=b<f and a!=b and a not in used and b not in used,
                'Each network layer must be a disjoint matching')
        require(bit in (0,1),'Every switch mask must be binary')
        used.update((a,b))
        pairs.append((a,b,bit))
    spare=[i for i in range(f) if i not in used]
    pairs.extend((spare[j],spare[j+1],0) for j in range(0,len(spare)-1,2))
    require(len(pairs)==f//2,'Zero-mask pairs must use actual bypass wires, not padded wires')
    return tuple(pairs)


@lru_cache(maxsize=256)
def layer_templates(f):
    return tuple(tuple((a,b) for a,b,unused in complete_matching(layer,f))
                 for layer in irregular_layers(tuple(range(f))))


def alignment(pairs,f):
    g,u=f//4,f%4
    pi=[-1]*f
    for i,(a,b,unused) in enumerate(pairs):
        if i<2*g:
            pi[a]=i
            pi[b]=2*g+i+(u if i>=g else 0)
        else:
            pi[a],pi[b]=3*g,3*g+1
    if f%2:
        source=next(i for i,x in enumerate(pi) if x==-1)
        pi[source]=3*g+u-1
    invert_permutation(pi)
    return tuple(pi)


@lru_cache(maxsize=128)
def local_shape(f):
    if f<4:
        raise ValueError('This guarded router requires f>=4; smaller widths are a paid base case')
    g,u=f//4,f%4
    starts=(0,g+1,2*g+2,3*g+3+u)
    guards=tuple(start+g for start in starts)
    active=tuple(i for i in range(f+4) if i not in guards)
    residual=tuple(3*g+3+i for i in range(u))
    require(len(active)==f and guards[-1]==f+3,'The full slot must end in a complete existing guard')
    return starts,guards,active,residual


@lru_cache(maxsize=128)
def stock_layout(f):
    starts,guards,active,unused=local_shape(f)
    labels=[(role,i) for role in range(3) for i in range(f)]+[(3,i) for i in range(12)]
    swaps=[]
    for role in range(3):
        for q,guard in enumerate(guards):
            target=role*(f+4)+guard
            donor=labels.index((3,4*role+q))
            if donor!=target:
                labels[target],labels[donor]=labels[donor],labels[target]
                swaps.append((target,donor))
    desired={role*(f+4)+i:role for role in range(3) for i in active}
    wrong=[i for i,role in desired.items() if labels[i][0]!=role]
    require(len(wrong)<=48,'Twelve real guard placements must cause at most48 band mismatches')
    for target in wrong:
        role=desired[target]
        if labels[target][0]==role:
            continue
        donor=next(i for i in wrong if labels[i][0]==role and desired[i]!=role)
        labels[target],labels[donor]=labels[donor],labels[target]
        swaps.append((target,donor))
    require(len(swaps)<=60 and all(labels[i][0]==role for i,role in desired.items()),
            'Full role placement must use a constant number of actual whole-chunk swaps')
    orders=tuple(tuple(labels[role*(f+4)+i][1] for i in active) for role in range(3))
    require(all(sorted(order)==list(range(f)) for order in orders),'Every canonical band label must survive placement')
    return tuple(swaps),orders


def apply_stock(value,f,K,inverse=False):
    swaps,unused=stock_layout(f)
    for a,b in (reversed(swaps) if inverse else swaps):
        value=w.swap_chunks(value,a,b,K)
    return value


def active_positions(f,K):
    return tuple(i*K+K-1 for i in local_shape(f)[2])


def linear_pair(slots,pi,f,K,literal=True,omit_repair=False):
    slots=list(slots)
    inverse=invert_permutation(pi)
    positions=active_positions(f,K)
    width=(f+4)*K
    identity=tuple(range(f))
    for donor,target,route in ((1,0,identity),(0,1,identity),(1,0,identity),
                               (1,0,pi),(0,1,inverse),(1,0,pi)):
        mask=w.scatter_selected(permute_bits(w.extract_selected(slots[donor],positions),route),positions)
        before=(slots[donor],slots[2])
        if literal:
            slots[target],slots[2]=w.packed_xor(mask,slots[target],slots[2],width,K,omit_repair)
        else:
            slots[target]^=mask
        if not omit_repair:
            require((slots[donor],slots[2])==before,'Every full-band donor and companion must restore')
    return tuple(slots)


def active_mask(y,z,f,pattern):
    full=(1<<f)-1
    return (~((y^(full if pattern[0] else 0))|(z^(full if pattern[1] else 0))))&full


def stable_route(active,f):
    order=[i for i in range(f) if active>>i&1]+[i for i in range(f) if not active>>i&1]
    return invert_permutation(order)


@lru_cache(maxsize=8192)
def control_layers(y,z,f,orders,pattern):
    cy=permute_bits(y,orders[1])
    cz=permute_bits(z,orders[2])
    route=stable_route(active_mask(cy,cz,f,pattern),f)
    inverse_action=invert_permutation(orders[0])
    physical=tuple(inverse_action[route[label]] for label in orders[0])
    return irregular_layers(physical)


def residual_swap(x,switch,f,K,literal,omit_repair):
    starts,guards,unused,residual=local_shape(f)
    require(len(residual)>=2,'A real residual pair is required')
    labels=list(range(f+4))
    wanted=(residual[0],guards[0],residual[1],guards[1],guards[2],guards[3])
    swaps=[]
    for target,label in enumerate(wanted):
        donor=labels.index(label)
        if donor!=target:
            labels[target],labels[donor]=labels[donor],labels[target]
            swaps.append((target,donor))
            x=w.swap_chunks(x,target,donor,K)
    require(len(swaps)<=6,'The residual placement must use at most six actual whole-K swaps')
    width=2*K
    mask=(1<<width)-1
    pieces=[(x>>(j*width))&mask for j in range(3)]
    selected=1<<(K-1)
    for donor,target in ((1,0),(0,1),(1,0)):
        offset=selected if switch and pieces[donor]&selected else 0
        before=(pieces[donor],pieces[2])
        if literal:
            pieces[target],pieces[2]=w.packed_xor(offset,pieces[target],pieces[2],width,K,omit_repair)
        else:
            pieces[target]^=offset
        if not omit_repair:
            require((pieces[donor],pieces[2])==before,'A residual donor or complete companion must restore')
    x=(x&~((1<<(6*K))-1))|sum(value<<(j*width) for j,value in enumerate(pieces))
    for a,b in reversed(swaps):
        x=w.swap_chunks(x,a,b,K)
    return x


def stage(slots,f,K,index,orders,pattern,literal=True,wrong_decode=False,
          omit_residual=False,omit_repair=False):
    before=slots
    pairs=tuple((a,b,0) for a,b in layer_templates(f)[index])
    pi=alignment(pairs,f)
    inverse=invert_permutation(pi)
    x,y,z=linear_pair(slots,pi,f,K,literal,omit_repair)
    positions=active_positions(f,K)
    control_y=w.extract_selected(y,positions)
    if not wrong_decode:
        control_y=permute_bits(control_y,pi)
    control_z=w.extract_selected(z,positions)
    actual=complete_matching(control_layers(control_y,control_z,f,orders,pattern)[index],f)
    require(tuple((a,b) for a,b,unused in actual)==layer_templates(f)[index],
            'Control values may alter switch masks, not the fixed network skeleton')
    switch_bits=[bit for unused_a,unused_b,bit in actual]
    starts,unused_guards,unused_active,residual=local_shape(f)
    g=f//4
    quarter_width=(g+1)*K
    qmask=(1<<quarter_width)-1
    quarters=[(x>>(start*K))&qmask for start in starts]
    local_positions=tuple(i*K+K-1 for i in range(g))
    for target,donor,companion,which in w.QUARTER_EVENTS:
        selected_switch=sum(switch_bits[which*g+i]<<i for i in range(g))
        offset=w.scatter_selected(w.extract_selected(quarters[donor],local_positions)&selected_switch,local_positions)
        previous=(quarters[donor],quarters[companion])
        if literal:
            quarters[target],quarters[companion]=w.packed_xor(offset,quarters[target],quarters[companion],
                                                             quarter_width,K,omit_repair)
        else:
            quarters[target]^=offset
        if not omit_repair:
            require((quarters[donor],quarters[companion])==previous,'A complete quarter donor/companion must restore')
    for start,value in zip(starts,quarters):
        x=(x&~(qmask<<(start*K)))|(value<<(start*K))
    if len(residual)>=2 and not omit_residual:
        x=residual_swap(x,switch_bits[2*g],f,K,literal,omit_repair)
    result=linear_pair((x,y,z),inverse,f,K,literal,omit_repair)
    if not omit_repair:
        require(result[1:]==before[1:],'Both immutable full control slots must restore at the layer endpoint')
        selected=sum(1<<position for position in positions)
        require((result[0]^before[0])&~selected==0,'All action guard and unselected planes must restore')
    return result


def compact(address,f,K,pattern=(0,0),inverse=False,literal=True,
            wrong_decode=False,omit_residual=False,omit_repair=False):
    if K<1:
        raise ValueError('A positive complete chunk width is required')
    unused,orders=stock_layout(f)
    placed=apply_stock(address,f,K)
    width=(f+4)*K
    mask=(1<<width)-1
    slots=tuple((placed>>(role*width))&mask for role in range(3))
    indices=range(len(layer_templates(f)))
    if inverse:
        indices=reversed(tuple(indices))
    for index in indices:
        slots=stage(slots,f,K,index,orders,pattern,literal,wrong_decode,omit_residual,omit_repair)
    placed=sum(value<<(role*width) for role,value in enumerate(slots))
    return apply_stock(placed,f,K,inverse=True)


def reference(address,f,K,pattern):
    positions=[tuple((role*f+i)*K+K-1 for i in range(f)) for role in range(3)]
    x,y,z=[w.extract_selected(address,p) for p in positions]
    wanted=permute_bits(x,stable_route(active_mask(y,z,f,pattern),f))
    mask=sum(1<<i for i in positions[0])
    return (address&~mask)|w.scatter_selected(wanted,positions[0])


def topology_controls():
    count=0
    for n in range(1,8):
        template=None
        for pi in permutations(range(n)):
            plan=irregular_layers(pi)
            labels=list(range(n))
            skeleton=[]
            for layer in plan:
                pairs=complete_matching(layer,n)
                skeleton.append(tuple((a,b) for a,b,unused in pairs))
                for a,b,bit in pairs:
                    if bit:
                        labels[a],labels[b]=labels[b],labels[a]
            require(tuple(labels)==invert_permutation(pi),'Every complete finite permutation must route exactly')
            if template is None:
                template=tuple(skeleton)
            require(tuple(skeleton)==template,'The skeleton must depend only on n')
            require(len(plan)<=max(0,2*(n-1).bit_length()-1),'The logarithmic irregular depth bound must hold')
            count+=1
    try:
        irregular_layers((0,0,2))
    except ValueError:
        rejected=True
    else:
        rejected=False
    require(rejected,'A nonbijective requested route must be rejected')
    return dict(all_permutations_through_n7=count,odd_endpoint_coloring_checked=True,
                fixed_complete_matching_skeleton=True,invalid_permutation_rejected=True)


def probe(task):
    f,K,seed=task
    start=time.monotonic()
    rng=random.Random(seed)
    n=(3*f+12)*K
    samples=64
    wrong_decode=None
    wrong_residual=None
    wrong_repair=None
    cases=0
    for pattern in ((0,0),(0,1),(1,0),(1,1)):
        for unused in range(samples):
            address=rng.getrandbits(n)
            expected=reference(address,f,K,pattern)
            actual=compact(address,f,K,pattern)
            require(actual==expected and compact(actual,f,K,pattern,inverse=True)==address,
                    'Every literal irregular full-address word and true inverse must agree')
            if wrong_decode is None:
                wrong=compact(address,f,K,pattern,literal=False,wrong_decode=True)
                if wrong!=expected:
                    wrong_decode=dict(original=address,wrong=wrong,expected=expected,pattern=pattern)
            if f%4>=2 and wrong_residual is None:
                wrong=compact(address,f,K,pattern,literal=False,omit_residual=True)
                if wrong!=expected:
                    wrong_residual=dict(original=address,wrong=wrong,expected=expected,pattern=pattern)
            if wrong_repair is None and cases<16:
                try:
                    wrong=compact(address,f,K,pattern,omit_repair=True)
                except (AssertionError,ValueError) as error:
                    wrong_repair=dict(original=address,rejected=str(error),pattern=pattern)
                else:
                    if wrong!=expected:
                        wrong_repair=dict(original=address,wrong=wrong,expected=expected,pattern=pattern)
            cases+=1
    if wrong_repair is None:
        # Random long guards rarely force an actual carry failure. Both first
        # control-selected bits are one and every unselected/guard plane is
        # zero here, forcing a nonzero two-bit full-slot mask at the first
        # linear shear. The corrected complete word must still pass.
        address=((1<<((f+1)*K-1))|(1<<((f+2)*K-1))|
                 (1<<((2*f+1)*K-1)))
        pattern=(0,0)
        expected=reference(address,f,K,pattern)
        actual=compact(address,f,K,pattern)
        require(actual==expected and compact(actual,f,K,pattern,inverse=True)==address,
                'The adversarial complete guard-plane input must pass with repair')
        try:
            wrong=compact(address,f,K,pattern,omit_repair=True)
        except (AssertionError,ValueError) as error:
            wrong_repair=dict(original=address,rejected=str(error),pattern=pattern,
                              deterministic_zero_guard_planes=True)
        else:
            if wrong!=expected:
                wrong_repair=dict(original=address,wrong=wrong,expected=expected,pattern=pattern,
                                  deterministic_zero_guard_planes=True)
    require(wrong_decode is not None and wrong_repair is not None,'Control decoding and repair negatives must discriminate')
    require(f%4<2 or wrong_residual is not None,'Every tested real residual-pair path must discriminate')
    swaps,orders=stock_layout(f)
    return dict(status='PASS LITERAL GENERAL-WIDTH ACTIVITY ROUTE',f=f,K=K,seed=seed,
                full_address_samples=cases,full_address_bits=n,existing_complete_guard_chunks=12,
                added_address_bits=0,quarter_selected_width=f//4,residual_selected_coordinates=f%4,
                stock_full_K_swaps=len(swaps),stage_count=len(layer_templates(f)),
                packed_words_per_stage_upper=21,residual_full_K_swaps_per_stage_upper=12,
                literal_rotations_per_stage_upper=168,label_orders=[list(order) for order in orders],
                negative_controls=dict(omitted_control_decode=wrong_decode,
                    omitted_residual_pair=wrong_residual,omitted_exceptional_repair=wrong_repair),
                native_tape_cost_proved=False,recursive_child_supplied=False,exponent_claim=False,
                seconds=time.monotonic()-start)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    require(args.workers>0,'A positive worker count is required')
    source=Path(__file__).resolve()
    closure={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in (source,WORD,BASE)}
    tasks=((6,1,20261009171),) if args.bounded else (
        (5,1,20261009171),(6,2,20261009172),(9,6,20261009173),(17,6,20261009174))
    started=datetime.now(timezone.utc).isoformat()
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=started,source_closure=closure,
            tasks=tasks,workers=args.workers,scope='Exact finite composition with frozen packed XOR component; no native time or exponent'),indent=2)+'\n')
    topology=topology_controls()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(probe,tasks))
    require(closure=={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in (source,WORD,BASE)},
            'The entire effective source closure must remain unchanged')
    summary=dict(status='PASS IRREGULAR GUARDED ACTIVITY ROUTING',topology=topology,cases=rows,
                 full_address_samples=sum(row['full_address_samples'] for row in rows),
                 no_power_of_two_padding=True,native_or_exponent=False)
    if args.output:
        (args.output/'certificate.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({key:value for key,value in summary.items() if key!='cases'},sort_keys=True))


if __name__=='__main__':
    main()
