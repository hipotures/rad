# A simultaneous pivot bound for the fixed cap decoder

The five-cube actual-row decoder has at most sixteen independent output
directions in each target cube. A simultaneous packet of exclusive dirty
target pivots at one common cut therefore removes at most half of the
original target-bank count within this fixed decoder class. At seven paired
coordinates the exact local bound is fifteen of the thirty-two target banks.
This is not a bound on repeated use of a target at different cuts.

The exact source is
[`target_pivot_rank_boundary.py`](../../code/complex/target_pivot_rank_boundary.py).
Its only imported input is the frozen
[`paired_cap_dirty_completion.py`](../../code/complex/paired_cap_dirty_completion.py).
The completed run is
[`20261009T102721Z-complex-target-pivot-rank`](../../runs/20261009T102721Z-complex-target-pivot-rank/report.md).
All arithmetic is exact standard-library rational arithmetic; no random
seeds or downloaded executable inputs are used.

For a source/target cube intersection `J` of size `j`, the raw block is
`A_j(t,u)=-f5(j-wt(t xor u))`, where `f5(x)=(x-1)(x-3)/8`.
Choose an independent set of actual rows separately in each parity block,
and write `A_j=D_j R_j`. A mathematical right inverse of the full-row-rank
`R_j` gives `D_j=A_j R_j_right_inverse`. Thus every decoder column lies in
the column space of the raw block. Its selector character degree is at most
two. Extending a column from `J` to the five target coordinates does not
raise that degree. Multiple other source cubes with the same `J` duplicate
these output patterns rather than adding new directions.

The exact rank census is:

| Paired coordinate count | Available proper intersections | Channel incidences per target cube | Distinct intersection/decoder patterns | Exact rank |
| --- | --- | ---: | ---: | ---: |
| 6 | 4 | 30 | 30 | 10 |
| 7 | 3, 4 | 120 | 90 | 15 |
| 8 | 2, 3, 4 | 310 | 130 | 16 |
| 9 | 1, 2, 3, 4 | 650 | 140 | 16 |
| 12 | 0, 1, 2, 3, 4 | 3,241 | 141 | 16 |

The full low character sector on five selector bits has dimension
`1+5+10=16`. The six-pair case has only degree two, and the seven-pair case
has degrees one and two. The finite checker reconstructs every available
decoder column, checks every high-sector Walsh coefficient is zero and
computes the exact rational rank. A deliberately added degree-three column
is rejected. Repeating a channel with a different source role ID still has
a nonzero cross-pivot entry and cannot create another exclusive pivot.

If selected simultaneous pivots satisfy `D[p_a,a] != 0` and
`D[p_a,b]=0` for every `a != b`, their rows and columns form a nonzero
diagonal minor. The number of those pivots is at most `rank(D)`. Stacking
all target cubes gives the upper bound `16*binom(p,5)=v/2`; at `p7` it is
`15*binom(7,5)`. This is an optimistic rank bound: actual common frames,
pivot deadlines and source/dirty schedules can impose further restrictions.
No matching achieving the bound has been constructed.

The mathematical right inverse is used only to prove a column-space
statement. It is not a runtime change of basis and supplies no free scalar
inverse. In particular the `j0/j1` raw coefficient `-3/8` cannot be inverted
within the Gaussian-dyadic ring. A physical implementation can retain the
raw aggregate and put that factor in its decoder instead. This source does
not claim a dyadic actual-row-only inverse for those blocks.

The bound assumes the fixed actual-row cap decoder and one simultaneous
exclusive-pivot cut. It does not constrain temporal pivot reuse, a different
factorization whose high output components cancel, arbitrary target mixing,
helper/source stock or a general native circuit. The identity `J M=H` with
low-rank `H` does not by itself force the individual columns of `J` to have
low degree. There is no claim of a complete recurrence or larger exponent.

Reproduce the complete small check with:

```bash
python3 -B research/integer-mult-breakthrough/code/complex/target_pivot_rank_boundary.py
```

The full run checks five exact ranks in 0.139 seconds. It records the two
effective source hashes before and after execution. All compact certificate
bytes are retained unchanged; complete logs and source snapshots remain in
the recorded ignored raw directory and can be archived by the coordinator.
The next discriminator is a sequential same-target schedule whose later
cuts retain the earlier channel contributions and every dirty input column.
