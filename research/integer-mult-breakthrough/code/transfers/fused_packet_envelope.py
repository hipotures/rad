#!/usr/bin/env python3
"""Exact size-envelope controls separating packet axes from native width.

No data array, product primitive or huge field extension is executed here.
This is a symbolic cost discriminator for explicitly declared toy parameters,
not an accepted old profile, an all-size implementation or a kappa result.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/fused-packet-envelope.json'


def mobius(n):
    count=0;p=2
    while p*p<=n:
        if n%p==0:
            n//=p;count+=1
            if n%p==0:return 0
        p+=1
    if n>1:count+=1
    return -1 if count%2 else 1


def irreducible_count(n):
    numerator=sum(mobius(n//j)*5**j for j in range(1,n+1) if n%j==0)
    if numerator%n:raise ValueError('Finite-field count is not integral')
    return numerator//n


def degree_floor(channels):
    degree=1;remaining=channels;total=0
    while remaining:
        amount=min(remaining,irreducible_count(degree));remaining-=amount;total+=degree*amount;degree+=1
    return total


def probe(log_d):
    started=time.monotonic();d=1<<log_d;K=1<<(log_d//2)
    if log_d%2:raise ValueError('The exact toy K=d^(1/2) requires an even log width')
    # Toy tau=1/2,c=1/2,epsilon=1/16,a=1/1000; every comparison below
    # uses integers, without rounding exponents or allocating2^s records.
    p=d**16;s=log_d;D=1<<s;ratio=Q(3**s,D);field_factor=16*log_d;poly_factor=d**15
    native_allowance_squared=d*K
    field_total=ratio*field_factor;poly_total=ratio*poly_factor
    field_fits=field_total*field_total<=native_allowance_squared
    field_without_K=field_total*field_total<=d
    if field_without_K and not field_fits:raise ValueError('Removing K improved the allowance')
    # Previous polynomial multiplier ratio log(Q)~p/d; target p^(1-a).
    # Cancel d^(15*1000) before exponentiation to retain compact evidence.
    previous_product_row=3**(s*1000)<=2**(s*1000)*d**984
    proposed_inductive_product_row=3**(s*1000)<=2**(s*1000)*d**999
    minimum=degree_floor(D);degree_ratio=Q(minimum,D)
    # Power-two cyclic capacity requires n>=D/2, so ratioN/D>=2^(D/2-s).
    cyclic_log2_ratio=D//2-s
    cyclic_volume_fits=2*cyclic_log2_ratio<=log_d+log_d//2
    small_s=max(1,log_d.bit_length()-2);small_D=1<<small_s
    small_cyclic_log=small_D//2-small_s
    small_cyclic_fits=2*small_cyclic_log<=log_d+log_d//2
    # The stopping scale is H=K for tau=1/2. Linear-width traffic fits
    # at E=H but fails at E=d; K stays fixed in both comparisons.
    root_linear_fits=d*d<=d*K;leaf_linear_fits=K*K<=K*K
    if root_linear_fits or not leaf_linear_fits:raise ValueError('Declared stopping-scale control failed')
    return dict(log2_outer_width=log_d,outer_width=str(d),K=str(K),native_selected_width_equals_outer=True,
                toy_tau='1/2',toy_c='1/2',root_native_power='3/4',epsilon='1/16',target_a='1/1000',
                packet_axes=s,packet_dimension=str(D),named_three_product_leaf_count=str(3**s),
                normalized_leaf_volume_ratio=str(ratio),componentwise_previous_multiplier_ratio=field_factor,
                whole_polynomial_previous_multiplier_ratio=str(poly_factor),
                unit_constant_componentwise_cost_fits_native=field_fits,
                incorrect_omitted_K_componentwise_fit=field_without_K,
                omitted_K_changes_prediction=field_fits!=field_without_K,
                unit_constant_whole_polynomial_cost_fits_native=poly_total*poly_total<=native_allowance_squared,
                previous_multiplier_whole_assembly_product_row_fits=previous_product_row,
                hypothetical_inductive_multiplier_product_row_fits=proposed_inductive_product_row,
                general_dyadic_degree_floor=str(minimum),general_degree_volume_ratio=str(degree_ratio),
                unit_constant_degree_lower_bound_fits_native=degree_ratio*degree_ratio<=native_allowance_squared,
                power_two_cyclic_minimum_log2_volume_ratio=str(cyclic_log2_ratio),
                power_two_cyclic_degree_lower_bound_fits_native=cyclic_volume_fits,
                smaller_packet_axes=small_s,smaller_power_two_cyclic_volume_ratio_log2=small_cyclic_log,
                smaller_cyclic_degree_lower_bound_fits_native=small_cyclic_fits,
                linear_width_traffic_fits_root=root_linear_fits,
                linear_width_traffic_fits_stopping_width=leaf_linear_fits,
                leaf_source_sum_guard_bits=s,three_real_product_operand_extra_bits=s+1,
                uniform_complete_internal_precision_is_a_separate_condition=True,
                no_primitive_or_payload_executed=True,new_exponent=False,seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.workers<1 or (args.output and args.output.exists()):raise ValueError('Positive workers and fresh output required')
    config=json.loads(CONFIG.read_text());paths=(Path(__file__).resolve(),CONFIG)
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,
                  scope=config['scope'],actual_payloads_executed=False,exact_size_ledger_only=True)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic();cases=config['log2_d_cases'][:1] if args.small else config['log2_d_cases']
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(probe,cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in pins.items()):raise ValueError('Source changed during size controls')
    result=dict(status='EXACT PACKET NATIVE AND PRODUCT-ROW ENVELOPES PASS',cases=rows,
                seconds=time.monotonic()-started,scope=config['scope'],primitive_proved=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','seconds','scope')}))


if __name__=='__main__':main()
