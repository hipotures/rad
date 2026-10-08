# Even grounds for the shared complex D/E circuit

The unchanged shared-bank complex construction was evaluated at 15 distinct
even grounds: 22 through 48, and 52. Ground 28 has the largest certified
finite complex saving among these cases. Its exact lower enclosure strictly
supports `b = 3794/10^11`, where the complex recurrence exponent is `1-b`.
This is a finite certificate; compatibility with the new compact-control
assembly and the final integer-multiplication saving require separate review.

The source is [finite_complex_ground_scan.py](../code/finite_complex_ground_scan.py).
It imports the original `downstream_complex_certificate.case` without changing
any logical-map, binary-frame, residual, terminal, matching, or guard assertion.
The original upstream reference remains at commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; the newly acquired compact-control
reference `6e564879f51ae16f23d392e9e196c605f36d90df` is a distinct input.

| Ground | Physical roles | Certified saving, approximate |
| --- | ---: | ---: |
| 22 | 43,601 | 4.93328e-9 |
| 24 | 58,498 | 2.80698e-8 |
| 26 | 76,321 | 3.64234e-8 |
| 28 | 97,586 | 3.79402e-8 |
| 30 | 122,342 | 3.64608e-8 |
| 32 | 151,092 | 3.36985e-8 |
| 34 | 183,846 | 3.05779e-8 |
| 36 | 221,221 | 2.74443e-8 |
| 38 | 263,083 | 2.45372e-8 |
| 40 | 310,206 | 2.18758e-8 |
| 42 | 362,212 | 1.95246e-8 |
| 44 | 420,204 | 1.74231e-8 |
| 46 | 483,720 | 1.55857e-8 |
| 48 | 553,714 | 1.39614e-8 |
| 52 | 712,748 | 1.12925e-8 |

Ground 50 had already been checked in the earlier shared-complex work and was
excluded from this cohort. The table displays rounded values; ranking used
exact rational lower enclosures, retained in the compact summary. No floating
point comparison certifies the selected saving.

For ground 28, `v=3276`, `m=21952`, `c=91034`, and there are `2v=6552`
designated outputs. The compiled role count is `R=c+2v=97586`. Full sharing
of the first and third banks gives

```
N = 35158608576
W = 2165559937632
L = 26143580736
D = 2N - 2L = 18030055680
s = Wm - D = 47538353720841984
eta = D/(Wm) = 15/39549272
```

The circuit has 7,780,500 nonzero side coefficients, reconstructed exactly
from formal input supports. Every addition has disjoint summands. Every
binary-frame edge is nested and has an explicit norm-one witness whenever
its residual is nonzero; terminal complements are nondegenerate and
nonalternating. The exact partner involution maps all 3,276 triples, with
2,912 disjoint and 364 intersection-two partner pairs. The middle join
residual has dimension 21,896, and each removed bank role removes rank 21,952.

The grouped scalar-gate count is 12,567,850,311,744, strictly below `6W` by
425,509,314,048. The retained guard constant is
`E=649965960410303909636134444816737704000`, and
`B=649965960410303909636181983170458545984`. The strict additive operation-depth
slack is `528097346539639752649229256075950985916`; `2 <= s < m^5` passes.

The ground-28 witness is [winner.json](../runs/20261008T012330Z-finite-complex-even-grounds/results/winner.json),
SHA-256 `ddd974155f8ddbdf3efe7ed4c85fe122138def40314702c98f023ae996e38ea8`.
Its circuit digest is
`824f836dff479b13c62d8e1fce18cb4e3a4e69b12d2b1d3c25dc2e0d6c7d4f24`.
The scan source digest is
`068babb91a64b49525f2542a4058c0a43df2a459a67b1fa096aa92cd54e55ca5`.
Source dependencies and input hashes are recorded in the external protocol,
whose SHA-256 is `f9072e7a847f5e86a60455ecbd660b6031073d45842d801c6fa568ff4f26bed2`.

The seven-worker cohort completed all 15 cases in 15.379 seconds, using one
BLAS thread per process and a six-GiB address-space limit. Its last checkpoint
retains the stale label `Running`; the completed `summary.json`, all 15 case
files, and the outer terminal protocol are the authoritative terminal state.
The seven slots were immediately returned to the active bit-circuit pool.

For reproduction, use the pinned math environment and a fresh output path:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$RAD_MATH_PYTHON" -B research/integer-multiplication-bounds/code/finite_complex_ground_scan.py \
  --reference "$RAD_OLD_UPSTREAM" --workers 7 --worker-address-space-gib 6 \
  --run-dir "$RAD_FRESH_OUTPUT"
```

The exact recorded command and host paths are in the
[run protocol](../runs/20261008T012330Z-finite-complex-even-grounds/protocol.json).
All external evidence is deterministically regenerable under
`$RAD_WORK_ROOT/derived/finite/20261008T012330Z-finite-complex-even-grounds/`;
complete execution logs are under the corresponding `logs/finite/` directory.
The readable winner and exact table are retained in the run's results directory.

Independent ground-28 replay subsequently passed in
[the root frame audit](../runs/20261008T013158Z-review-complex28/results/independent-audit.json).
It independently checked 94,310 logical frames, 162,286 frame edges, all
7,780,500 output coefficients, and 559,308 forward/reverse physical transitions
in 1.831 seconds. The separate
[64-term count/log review](../runs/20261008T014008Z-review-complex28-counts/results/certificate.json)
also passed. Confirmation of the compact-control assembly is recorded by
the downstream composer and critical review, independently of this scan.
The original dirty
and shared three-stage controls cover the generic circuit at ground 8; this
scan does not rerun a ground-28 Cartesian dirty exchange, which would contain
billions of scratch coordinates.
