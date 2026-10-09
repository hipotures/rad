#!/usr/bin/env python3
"""Exact sufficient-ledger conflict and complete tensor-packet controls.

Available ordinary routing saving alpha, desired activity saving b and balanced
assembly parameter a are separate. Failed certification inequalities are not
time lower bounds. Small exact Z packets check complete fields, inverse and
the invalid disjoint-row and packet-local precision shortcuts.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import time


def require(value, message):
    if not value:
        raise AssertionError(message)


def direct_margin(alpha, b, beta, c):
    require(0<beta<1 and 0<alpha<1 and 0<b<1 and c>=0, 'Valid positive savings and stopping parameters required')
    return 1-b-(1-alpha)*(1+c/beta)


def packet_gap(alpha, saving, gamma, c):
    require(0<gamma<=1 and 0<saving<1 and c>=0, 'Valid packet width and supplier powers required')
    return gamma*(alpha-saving)-c*(1-alpha)


def regime_controls():
    public_a0=F(37165860768041,62500000000000000)
    public_theta=F(594323213359226694617,10**24)
    public_old=F(384599,10**10)
    public_alpha=(1-public_theta)*public_a0+public_theta*public_old
    inputs=[
        ('self_dependent',F(1,10000),F(9,100000),F(9,100000),F(1,20),F(1,10**6)),
        ('weaker_than_assembly',F(1,10000),F(9,100000),F(9,200000),F(1,20),F(0)),
        ('original_available_atom',F(1,10000),F(9,100000),F(1,2**50),F(1,20),F(1,10**8)),
        ('independent_conditional_atom',F(1,5000),F(9,50000),public_alpha,F(1,20),F(1,10**6)),
        ('larger_target_same_atom',F(1,1000),F(9,10000),public_alpha,F(1,20),F(1,10**6)),
        ('hypothetical_stronger_atom',F(1,100),F(9,1000),F(1,50),F(1,20),F(1,10**6)),
    ]
    rows=[]
    for name,b,a,alpha,beta,c in inputs:
        require(a<(1-beta)*b, 'Every case must preserve the actual balanced assembly inequality')
        margin=direct_margin(alpha,b,beta,c)
        weak_route=alpha<=a
        if weak_route:
            require(margin < -beta*b, 'The self-dependent sufficient direct ledger must fail strictly')
            require(alpha<b, 'The balanced H cutoff also cannot have p>=tau')
        packet=[]
        stopped_saving=(1-beta)*b
        for gamma in (F(1),F(1,2),F(1,4)):
            gap=packet_gap(alpha,stopped_saving,gamma,c)
            if weak_route:
                require(gap<0, 'Smaller packets cannot reverse the same ordinary-routing gap')
            packet.append({'gamma':str(gamma),'stopped_supplier_saving':str(stopped_saving),
                           'target_total_power':str(1-gamma*stopped_saving),
                           'charged_routing_total_power':str(1-gamma*alpha+c*(1-alpha)),
                           'strict_margin':str(gap),'power_compatible':gap>0})
        rows.append({'regime':name,'b':str(b),'a':str(a),'alpha':str(alpha),
                     'beta':str(beta),'c':str(c),'direct_margin':str(margin),
                     'direct_power_compatible':margin>0,'routing_at_most_assembly_parameter':weak_route,
                     'packet_comparison':packet})
    require([row['direct_power_compatible'] for row in rows]==[False,False,False,True,False,True],
            'Failed and independently stronger regimes must be separated')
    # Wrongly identifying an independently available alpha with the assembly
    # output fails its own retained inequality, even when routing is compatible.
    require(public_alpha >= (1-F(1,20))*F(1,5000), 'The field/interface conflation negative must discriminate')
    return {'public_conditional_alpha':str(public_alpha),'regimes':rows,
            'available_alpha_is_not_assembly_a':True,'conditional_or_hypothetical_constants_only':True}


def apply_axes(values, axes, inverse=False):
    values=list(values)
    for axis in reversed(tuple(axes)) if inverse else axes:
        for index in range(len(values)):
            if index >> axis & 1:
                other=values[index^(1<<axis)]
                values[index]=values[index]-other if inverse else values[index]+other
    return values


def partition(width, packet_width):
    return tuple(tuple(range(start,min(width,start+packet_width)))
                 for start in range(0,width,packet_width))


def packet_apply(values, packets, inverse=False):
    values=list(values)
    for axes in reversed(packets) if inverse else packets:
        values=apply_axes(values,axes,inverse)
    return values


def direct_zeta(values):
    return [sum(values[source] for source in range(len(values)) if source & target == source)
            for target in range(len(values))]


def packet_probe(task):
    width,packet_width=task
    packets=partition(width,packet_width)
    n=1<<width
    coefficients=0
    for source in range(n):
        original=[int(i==source) for i in range(n)]
        expected=[int(source&target==source) for target in range(n)]
        actual=packet_apply(original,packets)
        require(actual==expected and packet_apply(actual,packets,True)==original,
                'Every complete tensor-packet column and true inverse must agree')
        coefficients+=n
    # Two complete row fibers and four Gaussian fields, represented by all
    # eight components. Neither row may be silently assigned just one packet.
    fields=[]
    for row in range(2):
        for component in range(8):
            original=[F(1) if component==0 else F((i+3*component+7*row)%17-8,8)
                      for i in range(n)]
            actual=packet_apply(original,packets)
            require(actual==direct_zeta(original) and packet_apply(actual,packets,True)==original,
                    'All complete row fibers and arbitrary Gaussian fields must restore')
            fields.append(actual)
    require(fields[0][-1]==n, 'Completed packets accumulate the full selected-width magnitude')
    require(n > 1<<packet_width, 'Packet-local precision alone must fail on all-one input')
    delta=[int(i==0) for i in range(n)]
    wanted=packet_apply(delta,packets)
    wrong=[apply_axes(delta,packets[row%len(packets)]) for row in range(2)]
    require(all(value!=wanted for value in wrong), 'Disjoint-row volume credit cannot implement a tensor product')
    return {'width':width,'packet_width':packet_width,'packet_axes':[list(axes) for axes in packets],
            'complete_columns':n,'exact_matrix_coefficients':coefficients,
            'complete_rows':2,'Gaussian_fields_per_row':4,'full_component_values':16*n,
            'full_selected_width_magnitude':n,'misleading_packet_only_bound':1<<packet_width,
            'wrong_disjoint_row_allocation_rejected':True,'packet_only_magnitude_guard_rejected':True,
            'scope':'Exact toy Z algebra and complete-field accounting; twelve-guard native router and its fixed-tape costs are not executed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    require(args.workers>0, 'A positive worker count is required')
    own=Path(__file__).resolve()
    digest=sha256(own.read_bytes()).hexdigest()
    started=datetime.now(timezone.utc).isoformat()
    tick=time.monotonic()
    tasks=[(4,2)] if args.bounded else [(4,2),(5,2),(6,3),(8,3)]
    if args.workers==1:
        rows=[packet_probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows=list(pool.map(packet_probe,tasks))
    regimes=regime_controls()
    require(sha256(own.read_bytes()).hexdigest()==digest, 'Source must remain unchanged')
    result={'status':'PASS scoped self-bootstrap ledger and tensor-packet controls',
            'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
            'seconds':time.monotonic()-tick,'workers':args.workers,'bounded':args.bounded,
            'source_sha256':digest,'regime_controls':regimes,'packet_controls':rows,
            'scope':'Exact arithmetic consequences of declared sufficient ledgers and finite complete Z packet algebra; no routing lower bound, native supplier, public theorem reproduction, or new kappa'}
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('regime_controls','packet_controls')},sort_keys=True))


if __name__=='__main__':
    main()
