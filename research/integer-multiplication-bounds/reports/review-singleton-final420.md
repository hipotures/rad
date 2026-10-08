# Full independent final420 singleton promotion

The completed 420-case successor search's fixed h50 winner passes the
unchanged independent full promotion checker. Its physical side role count
is **473,026**, with candidate identity
`171a84402dbfaba83759e04b307eaa7a0e03e945a9a58bbd10e27e0caaf47102`.
The base-4 singleton positions are `[0]*24+[23]*24+[0,24]`.

The independently verified compiled digest is
`dab8e96f621d7346acbe9811b1c6c5005fc040d6cc9dd61c8cd745b23db712ea`.
The immutable candidate byte hash is
`20ee3c478e30f5ab73c6105d08fe3a81ea1e1bd66095f074a38638856a630834`.
[The terminal run](../runs/20261008T014255Z-review-singleton-final420/)
preserves a copy of those bytes and the independent compact certificate,
whose hash is
`755b28069171a976e1542081ba5136f1188187d52e5d68255285a7f9ccfef333`.

The original reference remains
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. The checker
[review_singleton_positions.py](../code/review_singleton_positions.py)
is unchanged from prior promotions, source digest
`f6222a66a3c042a073aca9febd082e0ab2da814a438e7260665059a52b625bc0`.
It constructs every local graph afresh rather than accepting throughput
cache contents, and independently expands every logical coefficient,
physical fresh copy, retained controller chain and envelope constraint.

| Full h50 quantity | Exact value |
|---|---:|
| Nonzero partial-output coefficients | 63,562,800 |
| Binary additions c | 448,127 |
| Designated partial outputs q | 58,800 |
| Retained controller links | 33,901 |
| Physical roles c+q-links | 473,026 |
| Fresh physical copies | 453,426 |
| Logical frames | 467,727 |
| Forward/reverse-complement physical frame transitions | 2,738,560 |

Every logical support is disjoint and correct. All physical gate outputs,
designated targets, original input lines, canonical output envelopes,
target orthogonality, and both nesting orientations pass. Retained links
use the same source, are acyclic and meet the one-retained-input gate
capacity. Every extra physical copy is counted and verified explicitly.
Role validity does not depend on an assertion that the selected flow is
globally optimal beyond its fixed ordering and frame ansatz.

The unchanged small controls include nonuniform h6/h8 position vectors.
The complete side-invocation bases have dimensions 190 and 795. Including
the central registers gives complete invocation bases 196 and 803, checked
in both forward and inverse orientations. Four full shared three-stage
bank exchanges at seeds 1 and 109 restore every auxiliary value exactly.
These complete small dirty controls accompany the all-coefficient/all-frame
h50 witness; the report does not claim an h50 dense whole-invocation matrix.

The full h50 phase took 83.743 seconds internally. The entire one-process
attempt, including the two small controls, took 101.70 seconds and
3,087,096 KiB peak RSS under `/usr/bin/time -v`. Python 3.14.7 from the
math environment was used, with BLAS/OMP/MKL restricted to one thread.
One dynamically reserved core was released in the wrapper's `finally`
block on terminal result. Other useful campaign workers were preserved.

Relative to the accepted 484,264 witness, this graph has 12,272 **more**
binary additions but 23,510 more retained links, hence 11,238 fewer physical
roles. A screen that minimizes only addition count would discard this
improvement. The finite mathematical transfer is unchanged: positive
rational envelope frames and their reverse complements, transparent dirty
scratch, stage joining, source rank and central rank accounting all use the
previously reviewed proofs. The new compact-control movement/phase assembly
is separately reviewed in [the generic composition audit](review-compact-generic.md).

Reproduce from the RaD root using the immutable candidate copy:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /path/to/math/python -B \
  research/integer-multiplication-bounds/code/review_singleton_positions.py \
  --reference /path/to/upstream-reference \
  --candidate research/integer-multiplication-bounds/runs/20261008T014255Z-review-singleton-final420/results/candidate-input.json \
  --small-controls --output /fresh/path/review-final420.json
```

The protocol records exact source/dependency hashes, input identity,
interpreter, command, external log, timing and reservation release. The
saved candidate is a finite witness, not a new minrank lower bound or an
unconditional certification of the complete integer multiplication theorem.
