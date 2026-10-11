#!/usr/bin/env python3
"""Field discovery of ordered corner loci in actual signed-word transitions.

The modular elimination order is the independently validated native signed
profile algorithm: rightmost pivot, elimination below, then contiguous runs
whose row and column both increase by one. Exact rational CRT remains a
separate acceptance gate. A sample size of zero screens the COMPLETE actual word, charging its rank-one and full-space terms. Nonzero sample sizes remain discovery controls.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import time

import cupy as cp
import numpy as np

from signed_positive_frame_interfaces import columns


CUDA = r'''
__device__ unsigned mul(unsigned a,unsigned b,unsigned p){return (unsigned)((unsigned long long)a*b%p);}
__device__ unsigned power(unsigned a,unsigned b,unsigned p){unsigned z=1;while(b){if(b&1)z=mul(z,a,p);a=mul(a,a,p);b>>=1;}return z;}
extern "C" __global__ void profiles(const int*base,const int*rs,const int*cs,const int*tot,
 const int*betas,const int*stars,const int*hints,int h,int nm,int n,unsigned p,
 double exponent,double*scores,signed char*out){
 int problem=blockIdx.x;if(problem>=n)return;int k=problem%nm,bid=problem/nm;
 unsigned beta=betas[bid],star=stars[bid],cross=mul(beta,star,p);
 __shared__ unsigned M[625],factors[25];__shared__ int pivot,prevrow,prevcol,run,rank;
 for(int z=threadIdx.x;z<h*h;z+=blockDim.x){int i=z/h,j=z%h;
  long long v=base[k*h*h+z];v-=mul(beta,cs[k*h+j],p);v-=mul(star,rs[k*h+i],p);v+=mul(cross,tot[k],p);
  v%=p;if(v<0)v+=p;M[z]=(unsigned)v;
 }
 if(threadIdx.x==0){prevrow=-2;prevcol=-2;run=0;rank=0;scores[problem]=0;}
 __syncthreads();
 for(int i=0;i<h;i++){
  if(threadIdx.x==0){pivot=h-1;while(pivot>=0&&!M[i*h+pivot])pivot--;out[problem*h+i]=(signed char)pivot;
   if(pivot>=0){rank++;if(i==prevrow+1&&pivot==prevcol+1)run++;else{if(run)scores[problem]+=pow((double)run,exponent);run=1;}prevrow=i;prevcol=pivot;}
  }
  __syncthreads();
  if(pivot>=0){
   if(threadIdx.x==0){unsigned inv=power(M[i*h+pivot],p-2,p);for(int k2=i+1;k2<h;k2++)factors[k2]=mul(M[k2*h+pivot],inv,p);}
   __syncthreads();
   for(int z=threadIdx.x;z<h*h;z+=blockDim.x){int row=z/h,col=z%h;if(row>i&&col<=pivot){unsigned t=mul(factors[row],M[i*h+col],p);M[z]=M[z]>=t?M[z]-t:M[z]+p-t;}}
   __syncthreads();
  }
  __syncthreads();
 }
 if(threadIdx.x==0){if(run)scores[problem]+=pow((double)run,exponent);if(rank!=hints[k])scores[problem]=1.e100;}
}
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def rational_reconstruct(a, p, bound=180):
    r0, r1, t0, t1 = p, a, 0, 1
    while abs(r1) > bound:
        q = r0 // r1
        r0, r1, t0, t1 = r1, r0 - q * r1, t1, t0 - q * t1
    if t1 < 0:
        r1, t1 = -r1, -t1
    if not 0 < t1 <= bound or math.gcd(r1, t1) != 1 or (r1 - a * t1) % p:
        return None
    return F(r1, t1)


from mixed_coframe_gpu_interfaces import read_binary, base_matrix, FLAG


def actual_matrix(matrix, beta, h, p):
    b = beta.numerator * pow(beta.denominator % p, -1, p) % p
    star = (1 - 9 * b) * pow(9 * (1 - h * b) % p, -1, p) % p
    rs, cs, total = matrix.sum(axis=1) % p, matrix.sum(axis=0) % p, int(matrix.sum() % p)
    return (matrix - b * cs[None, :] - star * rs[:, None] + (b * star % p) * total) % p


def cpu_pivots(matrix, p):
    rows = matrix.tolist()
    h, pivots = len(rows), []
    for i in range(h):
        j = next((j for j in range(h - 1, -1, -1) if rows[i][j]), -1)
        pivots.append(j)
        if j < 0:
            continue
        inv = pow(rows[i][j], -1, p)
        for k in range(i + 1, h):
            scale = rows[k][j] * inv % p
            for col in range(j + 1):
                rows[k][col] = (rows[k][col] - scale * rows[i][col]) % p
    return pivots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--graph-receipt', type=Path, required=True)
    ap.add_argument('--device', type=int, choices=(0, 1), required=True)
    ap.add_argument('--sample', type=int, default=128)
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--prime', type=int, required=True)
    ap.add_argument('--bit-saving', type=F, default=F('0.0000514'))
    ap.add_argument('--control-beta', type=F, required=True)
    ap.add_argument('--tested-catalogue', type=Path)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--wait-summary', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    args.output.mkdir(parents=True)
    graph = json.loads(args.graph_receipt.read_text())
    binary = Path(graph['profile_transition_path'])
    assert digest(binary) == graph['profile_transition_sha256']
    h, v, roles, singles, mass, loss, frames, transitions = read_binary(binary)
    assert graph['transition_format'] == 'RADCOF01'
    assert graph['independent']['frame_format'] == 'mixed-signed-complemented-v1'
    tested = {args.control_beta}
    if args.tested_catalogue:
        old = json.loads(args.tested_catalogue.read_text())
        for family in old['families']:
            if family['transition_sha256'] == graph['profile_transition_sha256']:
                for text in family['tested_bases']:
                    _, numerator, denominator = text.split(':')
                    tested.add(F(int(numerator), int(denominator)))
    candidates = [row for row in transitions if frames[row[1]][0] - frames[row[0]][0] > 1
                  and row[:2] != (0, 1)]
    complete_word = args.sample == 0
    if complete_word:
        args.sample = len(candidates)
    # Stable diverse transition sampling: force populations at each residual rank,
    # then hash-select disjoint remaining actual transitions.
    ranked = sorted(candidates, key=lambda row: hashlib.sha256(f'{args.seed}:{row}'.encode()).digest())
    selected, seen_rank = [], set()
    for row in ranked:
        rank = frames[row[1]][0] - frames[row[0]][0]
        if rank not in seen_rank:
            selected.append(row)
            seen_rank.add(rank)
    used = set(selected)
    selected += [row for row in ranked if row not in used][:args.sample - len(selected)]
    assert len(selected) == args.sample
    p = args.prime
    assert 3 < p < 2 ** 20
    assert all(p % divisor for divisor in range(2, math.isqrt(p) + 1))
    cache = {fid: base_matrix(frames[fid], h, p) for row in selected for fid in row[:2]}
    matrices = np.asarray([(cache[b] - cache[a]) % p for a, b, _ in selected], np.int64)
    rs = matrices.sum(axis=2) % p
    cs = matrices.sum(axis=1) % p
    total = matrices.sum(axis=(1, 2)) % p
    ranks = np.asarray([frames[b][0] - frames[a][0] for a, b, _ in selected], np.int32)
    weights = np.asarray([count for _, _, count in selected], np.float64)
    excluded = {0, pow(h, -1, p), pow(3, -1, p), pow(9, -1, p),
                2 * pow(3 * (h - 3), -1, p) % p,
                (h - 7) * pow(3 * (h - 3), -1, p) % p,
                2 * pow(3 * (h - 1), -1, p) % p}
    beta_values = np.asarray([b for b in range(p) if b not in excluded], np.int32)
    stars = np.asarray([(1 - 9 * int(b)) * pow(9 * (1 - h * int(b)) % p, -1, p) % p
                        for b in beta_values], np.int32)
    protocol = {'utc': stamp(), 'classification': 'DISCOVERY ONLY: ACTUAL SIGNED TRANSITION CORNER LOCI',
                'h': h, 'v': v, 'R': roles, 'word_sha256': graph['word_sha256'],
                'transition_sha256': digest(binary), 'graph_receipt_sha256': digest(args.graph_receipt),
                'prime': p, 'device': args.device, 'seed': args.seed, 'selected_transitions': selected,
                'selected_transition_count': len(selected), 'field_basis_values': len(beta_values),
                'complete_actual_word_field_screen': complete_word,
                'actual_complete_word_rank_mass': mass, 'source_sha256': digest(__file__),
                'cuda_sha256': hashlib.sha256(CUDA.encode()).hexdigest(),
                'screening_bit_saving': str(args.bit_saving),
                'objective': 'Actual child-width moment in one proven field; exact rational CRT and complete assembly are mandatory before acceptance.',
                'excluded_field_beta_values': sorted(excluded)}
    protocol['already_tested_actual_word_bases'] = sorted(map(str, tested))
    if args.tested_catalogue:
        protocol['tested_catalogue_sha256'] = digest(args.tested_catalogue)
    # Independent Fraction Gram inversion checks the closed modular matrices.
    geometry_code = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
    sys.path.insert(0, str(geometry_code))
    from mixed_coframe_gpu_interfaces import projector
    checked_signatures, gram_controls = set(), []
    for fid in sorted(cache, key=lambda x: (0 if frames[x][1] & FLAG else 1, frames[x][0], x)):
        rank, forced, symbols = frames[fid]
        if fid < 2:
            continue
        signature = (bool(forced & FLAG), (forced & ~FLAG).bit_count(), any(x < -1 for x in symbols), rank)
        if signature in checked_signatures:
            continue
        checked_signatures.add(signature)
        exact = projector(h, forced, symbols,
                          f'beta:{args.control_beta.numerator}:{args.control_beta.denominator}')
        reduced = np.asarray([[int(x.numerator * pow(x.denominator % p, -1, p) % p)
                               for x in row] for row in exact], np.int64)
        assert np.array_equal(actual_matrix(cache[fid], args.control_beta, h, p), reduced)
        gram_controls.append({'frame': fid, 'rank': rank,
                              'forced_coordinates': (forced & ~FLAG).bit_count(),
                              'complemented_source_span': bool(forced & FLAG),
                              'has_negative_component': any(x < -1 for x in symbols),
                              'exact_rational_matrix_entries': h * h})
        if len(gram_controls) == 12:
            break
    assert gram_controls
    protocol['independent_fraction_gram_controls'] = gram_controls
    protocol['gram_source_sha256'] = digest(Path(__file__).resolve().parent / 'mixed_coframe_gpu_interfaces.py')
    protocol['ordinary_gram_source_sha256'] = digest(geometry_code / 'review_positive_physical_profiles.py')
    protocol['transition_format'] = 'RADCOF01'
    protocol['coframe_scope'] = 'P0_Gamma-P0_normal cache checked independently against a direct source-span kernel basis and Fraction Gram inverse; CUDA elimination unchanged.'
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    if args.wait_summary:
        while not args.wait_summary.exists():
            time.sleep(5)
        previous = json.loads(args.wait_summary.read_text())
        assert previous['device'] == args.device and (previous.get('state') == 'complete bounded GPU questions' or previous.get('status') == 'COMPLETE ACTUAL SIGNED CORNER FIELD DISCOVERY')
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8 * 1024 ** 3)
    kernel = cp.RawKernel(CUDA, 'profiles')
    fixed = [cp.asarray(x.astype(np.int32)) for x in (matrices, rs, cs, total, ranks)]
    exponent = 1 - float(args.bit_saving)
    control_b = args.control_beta.numerator * pow(args.control_beta.denominator % p, -1, p) % p
    control_s = (1 - 9 * control_b) * pow(9 * (1 - h * control_b) % p, -1, p) % p
    score = cp.empty(args.sample, cp.float64)
    pivots = cp.empty((args.sample, h), cp.int8)
    kernel((args.sample,), (128,), (*fixed[:4], cp.asarray([control_b], dtype=cp.int32),
           cp.asarray([control_s], dtype=cp.int32), fixed[4], np.int32(h), np.int32(args.sample),
           np.int32(args.sample), np.uint32(p), np.float64(exponent), score, pivots))
    actual = pivots.get()
    for index in range(min(32, args.sample)):
        expected = cpu_pivots(actual_matrix(matrices[index], args.control_beta, h, p), p)
        assert actual[index].tolist() == expected
    fixed_moment = 0.0
    if complete_word:
        fixed_moment = float(singles) + sum(count for a, b, count in transitions if frames[b][0] - frames[a][0] == 1)
        fixed_moment += sum(count * h ** exponent for a, b, count in transitions if (a, b) == (0, 1))
    baseline = fixed_moment + float(cp.sum(score * cp.asarray(weights)).get())
    assert baseline < 1e90
    all_scores = np.empty(len(beta_values), np.float64)
    started = time.monotonic()
    with (args.output / 'progress.jsonl').open('x') as stream:
        for start in range(0, len(beta_values), args.batch):
            stop = min(start + args.batch, len(beta_values))
            n = (stop - start) * args.sample
            out = cp.empty(n, cp.float64)
            pv = cp.empty((n, h), cp.int8)
            kernel((n,), (128,), (*fixed[:4], cp.asarray(beta_values[start:stop]),
                   cp.asarray(stars[start:stop]), fixed[4], np.int32(h), np.int32(args.sample),
                   np.int32(n), np.uint32(p), np.float64(exponent), out, pv))
            reduced = cp.sum(out.reshape(stop - start, args.sample) * cp.asarray(weights), axis=1).get()
            all_scores[start:stop] = reduced + fixed_moment
            if start % (16 * args.batch) == 0 or stop == len(beta_values):
                obs = {'utc': stamp(), 'field_basis_values_completed': stop,
                       'actual_matrices_screened': stop * args.sample,
                       'elapsed_seconds': time.monotonic() - started,
                       'best_sample_moment': float(all_scores[:stop].min()), 'control_sample_moment': baseline}
                stream.write(json.dumps(obs) + '\n'); stream.flush(); print(json.dumps(obs), flush=True)
    np.save(args.output / 'field-beta-values.npy', beta_values)
    np.save(args.output / 'sample-moments.npy', all_scores)
    best = []
    for index in np.argsort(all_scores):
        value = rational_reconstruct(int(beta_values[index]), p)
        if value is not None and value not in tested and value not in {F(0), F(1, h), F(1, 3), F(1, 9),
                F(2, 3 * (h - 3)), F(h - 7, 3 * (h - 3)), F(2, 3 * (h - 1))}:
            best.append({'beta': str(value), 'field_beta': int(beta_values[index]),
                         'sample_moment': float(all_scores[index]),
                         'improvement_over_control': baseline - float(all_scores[index])})
            if len(best) == 48:
                break
    summary = {**protocol, 'finish_utc': stamp(), 'status': 'COMPLETE ACTUAL SIGNED CORNER FIELD DISCOVERY',
               'field_basis_values_completed': len(beta_values),
               'actual_matrices_screened': len(beta_values) * args.sample,
               'cpu_modular_pivot_controls': min(32, args.sample),
               'fixed_rank1_and_full_space_moment': fixed_moment,
               'best_field_beta_values': [{'field_beta': int(beta_values[i]), 'moment': float(all_scores[i]), 'gain': baseline-float(all_scores[i])} for i in np.argsort(all_scores)[:48]],
               'control_beta': str(args.control_beta), 'control_sample_moment': baseline,
               'elapsed_seconds': time.monotonic() - started, 'rational_screening_leads': best,
               'limitations': ['A complete one-field word screen is discovery; rational ranks, DATA and assembly remain unchecked.',
                               'Field loci may be unlucky rational nonzero-minor reductions.',
                               'Every promising basis needs actual full-word rational CRT, complete DATA, stock and strict assembly.']}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'matrices': summary['actual_matrices_screened'],
                      'best_leads': best[:8]}), flush=True)


if __name__ == '__main__':
    main()
