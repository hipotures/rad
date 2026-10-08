#!/usr/bin/env python3
"""Fixed-grid controls for a pending nonuniform complex child contract.

The toy recursion has real near-parent-width cancellation children and
no inner rounding. It is not the enormous finite physical phase graph.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time


def require(c, message):
    if not c:
        raise AssertionError(message)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


class FixedGrid:
    def __init__(self, fractional_bits):
        self.F = fractional_bits
        self.halvings = 0
        self.components_observed = 0
        self.max_grid = 0
        self.recursive_calls = 0
        self.max_active_width = 0

    def observe(self, values):
        for z in values:
            for v in z:
                self.components_observed += 1
                if v:
                    zeros = (abs(v) & -abs(v)).bit_length()-1
                    self.max_grid = max(self.max_grid, self.F-zeros)

    def halves(self, values):
        result = []
        for a, b in values:
            require(a % 2 == b % 2 == 0, 'Fixed fine grid cannot represent an exact half')
            result.append((a//2, b//2))
            self.halvings += 1
        self.observe(result)
        return result

    def pair(self, a, b, inverse=False):
        if inverse:
            z = self.pair(a, neg(b))
            # -i Z C Z on the complete bit pair.
            return (z[0][1], -z[0][0]), (-z[1][1], z[1][0])
        common = add(a, b)
        diff = (b[1]-a[1], a[0]-b[0])
        return self.halves([add(common, diff), add(common, neg(diff))])

    def tensor(self, values, selected, inverse=False):
        out = list(values)
        for bit in selected:
            mask = 1 << bit
            for j in range(len(out)):
                if j & mask:
                    continue
                out[j], out[j | mask] = self.pair(out[j], out[j | mask], inverse)
        self.observe(out)
        return out

    def recursive(self, values, selected, m=4, r=3, inverse=False):
        self.recursive_calls += 1
        e = len(selected)
        if e >= m:
            f = e//m
            active = selected[:r*f]
            require(0 < len(active) < e, 'Arbitrary-width nonuniform child does not shrink')
            self.max_active_width = max(self.max_active_width, len(active))
            # Keep every value on the same preallocated integer grid,
            # including a real temporary three-bit fine-grid excursion.
            tmp = list(values)
            for _ in range(3):
                tmp = self.halves(tmp)
            tmp = [(a*8, b*8) for a, b in tmp]
            tmp = self.recursive(tmp, active, m, r)
            tmp = self.recursive(tmp, active, m, r, inverse=True)
            require(tmp == values, 'Near-parent-width cancellation children did not return exact inputs')
            values = tmp
        # A finite surrogate completion. The actual network is subject to
        # its separate full-volume/frame/tape transfer; no claim of replay.
        return self.tensor(values, selected, inverse)


def closed_tensor(rhs, e, inverse=False):
    # Independent coefficient formula, not a butterfly or recursive map.
    coefficients = []
    for distance in range(e+1):
        z = (1, 0)
        same, different = ((1, -1), (1, 1)) if inverse else ((1, 1), (1, -1))
        for _ in range(e-distance):
            z = mul(z, same)
        for _ in range(distance):
            z = mul(z, different)
        coefficients.append(z)
    den = 1 << e
    result = []
    for x in range(len(rhs)):
        z = (0, 0)
        for y, value in enumerate(rhs):
            if value != (0, 0):
                z = add(z, mul(coefficients[(x ^ y).bit_count()], value))
        require(z[0] % den == z[1] % den == 0,
                'Closed completed operator exceeds the allocated grid')
        result.append((z[0]//den, z[1]//den))
    return result


def fixed_controls():
    probes = basis = outputs = divisions = observed = calls = 0
    examples = []
    for e in range(1, 11):
        size, incoming_p = 1 << e, 13
        F = incoming_p+64*e
        scale = 1 << (F-incoming_p)
        rhs_list = []
        if e <= 6:
            for j in range(size):
                rhs_list.append([(scale if i == j else 0, 0) for i in range(size)])
                basis += 1
        for seed in range(2):
            rhs_list.append([(((17*i+seed)%23-11)*scale,
                              ((7*i+3*seed)%19-9)*scale) for i in range(size)])
        for rhs in rhs_list:
            grid = FixedGrid(F)
            out = grid.recursive(rhs, list(range(e)))
            require(out == closed_tensor(rhs, e), 'Recursive grouped child differs from closed forward tensor')
            restored = grid.recursive(out, list(range(e)), inverse=True)
            require(restored == rhs, 'Full corrected inverse loses a fixed-grid value')
            semantic_divisor = 1 << (F-incoming_p-e)
            require(all(a % semantic_divisor == b % semantic_divisor == 0 for a, b in out),
                    'Completed grouped grid cannot reset semantically')
            blocks = grid.tensor(rhs, range(e))
            grouped = list(rhs)
            if e >= 4:
                f, r = e//4, 3
                union = list(range(r*f))
                one = grid.tensor(rhs, union)
                separate = list(rhs)
                for j in range(r):
                    separate = grid.tensor(separate, range(j*f, (j+1)*f))
                require(one == separate, 'Concatenated selected tensor differs from complete separate blocks')
            require(blocks == out, 'Surrogate completion changed the tensor contract')
            probes += 1;outputs += size
            divisions += grid.halvings;observed += grid.components_observed;calls += grid.recursive_calls
            if e >= 7 and len(examples) < 6:
                examples.append(dict(e=e, fractional_bits=F, incoming_grid=incoming_p,
                                     largest_observed_grid=grid.max_grid,
                                     completed_grid_upper=incoming_p+e,
                                     largest_grouped_child=grid.max_active_width))
    # Explicitly truncate a true incoming-p impulse after the first child.
    grid = FixedGrid(80)
    impulse = [(1 << (80-13), 0), (0, 0)]
    image = grid.tensor(impulse, [0])
    quantum = 1 << (80-13)
    eager = [(a//quantum*quantum, b//quantum*quantum) for a, b in image]
    require(eager != image, 'Negative inner rounding control did not discriminate')
    return dict(complete_probes=probes, complete_basis_columns=basis,
                exact_output_coordinates=outputs, fine_grid_halvings=divisions,
                observed_integer_components=observed, recursive_calls=calls,
                linear_preallocated_grid=True, no_fraction_compaction=True,
                all_halves_exact=True, forward_closed_formula_and_inverse_exact=True,
                grouped_vs_complete_separate_blocks_exact=True,
                negative_eager_child_rounding_discriminated=True, examples=examples)


def stopped_guards():
    checks = 0; examples = []
    for m in (5, 7, 9):
        W = m+3;s = W*m-1;E = 64*(W+m+1)**3;B = s+E
        for r in (1, m//2, m-1):
            for beta in ((1, 7), (1, 2), (2, 3), (1, 16)):
                u, v = beta
                for k in range(11):
                    d = m**k;e = d;cost = 0;levels = 0;weighted = 0
                    while e >= m and e**v >= d**u:
                        f = e//m;next_e = r*f
                        require(0 < next_e < e, 'Nonuniform active width is not a strict integer decrease')
                        cost += s*f+E;weighted += f;levels += 1;e = next_e
                    cost += 8*e
                    require(levels <= d and weighted*(m-r) <= d,
                            'Integer depth or geometric semantic charge failed')
                    require(cost <= (8+B)*d <= 2*B*d,
                            'Nonuniform linear active semantic guard failed')
                    require(cost+18*d < 32*m*B*B*d,
                            'Whole-layer old explicit C0 no longer covers active guard')
                    checks += 1
                    if r == m-1 and k == 10 and len(examples) < 6:
                        examples.append(dict(m=m, r=r, d=d, beta=f'{u}/{v}',
                                             levels=levels, deepest_active=e,
                                             completed_semantic_sum=weighted,
                                             active_guard=cost, active_upper=2*B*d))
    return dict(exact_stopped_cases=checks, examples=examples,
                recurrence='A(e)<=A(rmax floor(e/m))+s floor(e/m)+E',
                geometric='sum floor(e_j/m)<=e/(m-rmax)<=e',
                depth='Every positive active width decreases by at least one, so j<=e',
                active='A(e)<=(8+s+E)e<=2(s+E)e',
                whole='A_layer<=(2B+18)d<32mB^2 d',
                beta_independent=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();require(not args.output.exists(), 'Use a fresh output path')
    t0 = time.monotonic()
    result = dict(status='PASS fixed-grid nonuniform child controls; actual finite tape transfer pending',
                  campaign_start='2026-10-07T22:25:21Z',
                  campaign_original_deadline='2026-10-08T08:25:21Z',
                  campaign_deadline='2026-10-08T10:00:00Z',
                  generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  fixed_grid=fixed_controls(), stopped_guard=stopped_guards(),
                  elapsed_seconds=time.monotonic()-t0,
                  limitations=['Toy exact cancellation recursion, not the actual enormous physical finite phase network',
                               'Grouped nonalternating adapter, arbitrary-width tails and fixed-tape full-volume interface require separate proof',
                               'The literal E bound must include the actual fixed tail C-kernel schedule'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], result['fixed_grid']['fine_grid_halvings'],
          result['stopped_guard']['exact_stopped_cases'], flush=True)


if __name__ == '__main__':
    main()
