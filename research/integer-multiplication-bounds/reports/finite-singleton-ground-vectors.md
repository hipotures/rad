# Actual-role ground sweep under the compact family

The fresh 31-case sweep checked three near-half early-singleton prefixes at
even grounds 38 through 58. Two ground-50 vectors were excluded because their
IDs were already present in the completed or live predecessor protocols.
Every new candidate passed the complete unchanged scalar-map, positive-frame,
physical coefficient/frame, designated-target, and pinned stage-matching
checks. The four-worker cohort took 280.793 seconds, with no errors.

The source is [finite_singleton_ground_vectors.py](../code/finite_singleton_ground_vectors.py),
SHA-256 `7ae2041a0de3a46da6f94b7286503407b68afc3f0ee775f565adba28525313cf`.
It imports the frozen exact evaluator and verified direct envelope constructor.
Candidate IDs, all excluded planned IDs, source hashes, resource limits, and
exact commands are retained in the
[run protocol](../runs/20261008T013845Z-finite-bit-ground-vectors/protocol.json).
The original upstream `bcd4ebde8692383539f8a48734e5fbf3a18a32c2` remains
immutable. The compact-model arithmetic is a separate dependency at
`6e564879f51ae16f23d392e9e196c605f36d90df`.

For each ground `h`, the new recipes use late position `h/2-2`, final positions
`[0,h/2-1]`, and an early zero-position prefix of length `h/2-1`, `h/2+1`, or
`h/2+3`. The first is best at every screened ground. The ground-50 anchor was
reused byte-for-byte, rather than re-evaluated. Best actual role counts are:

| Ground | Best roles |
| --- | ---: |
| 38 | 197,846 |
| 40 | 233,147 |
| 42 | 272,348 |
| 44 | 315,754 |
| 46 | 363,516 |
| 48 | 415,909 |
| 50 | 473,026 |
| 52 | 535,200 |
| 54 | 602,562 |
| 56 | 675,407 |
| 58 | 753,800 |

For unequal factors `(p,q,p)`, with `vp=binom(p,3)` and `vq=binom(q,3)`, the
exact reused-bank counts are

```
N = vp^2 vq
m = p^2 q
W = 2N + vp vq (Rp+p) + vp^2 (Rq+q)
L = 2 vp vq p^2 + vp^2 q^2
D = N - 2L
s = Wm - D
eta = D/(Wm)
```

Only positive-deficit motifs are ranked. The exact rational saving enclosures
select equal ground 50 over all screened unequal combinations. This differs
from the earlier quadratic/phase composition's accepted `(52,48,52)` choice.
The five leading primitive saving lower enclosures are approximately:

| First/third ground | Middle ground | Bit saving lower |
| --- | --- | ---: |
| 50 | 50 | 3.182246148733375e-9 |
| 50 | 52 | 3.179499866755804e-9 |
| 52 | 48 | 3.1785544785522615e-9 |
| 52 | 50 | 3.1763117769134134e-9 |
| 50 | 48 | 3.171498276036095e-9 |

The exact equal-ground winner has `W=378532824320000`,
`D=1767136000000`, `m=125000`, `s=47316601272864000000`, and
`eta=23/615845000`. Its independently promoted 473,026-role candidate is
`171a84402dbfaba83759e04b307eaa7a0e03e945a9a58bbd10e27e0caaf47102`.
The other grounds' new vectors remain finite candidates; they were not all
independently promoted with separate dirty/stage controls.

With the independently checked ground-28 shared complex witness, the
unchanged tight compact composer returns the strict rational arithmetic
witness

```
kappa = 1988903839793768677409884189549 /
        1250000000000000000000000000000000000000
      = approximately 1.591123071835015e-9.
```

This uses actual compiled roles and exact guard/leaf/movement inequalities.
It remains conditional on the independently reviewed compact movement,
reservation, deterministic repair, phase, and assembly interfaces. The
scoped upper comparison `a/(2+a)` is an upper bound for this retained
parameter family, not an unrestricted algorithmic ceiling.

The complete exact matrix, candidate records and hashes are deterministically
regenerable under
`$RAD_WORK_ROOT/derived/finite/20261008T013845Z-finite-bit-ground-vectors/`.
The readable compact result is
[compact-summary.json](../runs/20261008T013845Z-finite-bit-ground-vectors/results/compact-summary.json).
The exact command in the protocol uses four single-thread CPU processes,
12-GiB per-process address-space bounds, and a 20-minute attempt cap. The
four reservations were deducted from the active bit pool and released
automatically when this cohort ended. The 665 overlapping periodic resource
samples show a maximum campaign RSS sum of 75,794,931,712 bytes, below the
96-GiB ceiling; the minimum system available memory was 91,595,169,792 bytes.
RSS sums can double-count shared pages, and between-sample peaks can be missed.
The compact [resource envelope](../runs/20261008T013845Z-finite-bit-ground-vectors/results/resource-envelope.json)
records the sample scope and source paths.

Further useful work is finer schedule search at ground 50, or a construction
that reduces role counts enough for a different ground to cross the exact
50/50 margin. Repeating a ground-size choice from the older composition
without this changed-family rescore would miss the current best.
