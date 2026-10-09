# Independent review of the eight-point arithmetic dirty echo

**EXACT FINITE SCALAR REVIEW / ANALYTICAL TRANSCRIPTION REVIEW.** An import-free
literal eight-point construction agrees with the coordinator's Algorithm-5
arithmetic and complete dirty echo. Native phase and routing claims remain
outside this review.

The reviewed primary mechanism is Alman and Rao's
[Algorithm 5, arXiv:2211.06459v2](https://arxiv.org/pdf/2211.06459v2).
The coordinator records its primary-source identity in the source-pin config.
The local body uses 22 additions and one division; the first complete instance
also pays seven leaf scales. The independent source reconstructs all 30
helpers with rational coefficients and all 206 scalar shears. It imports no
producer code.

Four workers independently check every column of the full 46-coordinate map:
eight sources, 30 arbitrary dirty helpers, and eight initially arbitrary sinks.
Eight additional dyadic fields per worker also pass. The forward operator
leaves sources and helpers unchanged and adds the exact sign-formula Walsh
transform to the sinks. Its literal inverse restores all coordinates. The
run checks 19,872 scalar forward/inverse values in about 0.063 seconds.
Deleting the zero-source echo or first inverse pass changes the operator and
is rejected.

For a general linear SSA program, the triangular helper word has the form
`T_x(z)=A z+B x`; its readout can include direct-source aliases, `E x+C z`.
The first read therefore adds `(E+CB)x+CAz`. The first inverse restores `z`.
The zero-source pass omits source shears, produces `Az`, and subtracts `CAz`;
it also omits any direct-source alias at readout. Its inverse again restores
`z`. Thus the full sink update is exactly `(E+CB)x`, with all dirty state
restored. Distinct chronological helper targets and field-linear coefficients
are the required scalar assumptions.

The reviewed clean `7N/4` prefix bound is consistent with seven disjoint
doubled child blocks before the local division. Clean integrality uses their
known factor of two; it cannot be transferred to arbitrary dirty helpers.
The latter need up to one extra fractional bit per three-bit recursion level.
The inverse passes retrace the helper states while readout changes only sinks,
so they do not introduce another independent chain of divisions. Multiplication
temporaries and the larger fixed representation still need to be paid.
This paragraph is analytical source/proof scrutiny, not an independent
all-size executable guard certificate.

Every native scalar shear must act between identical actual address operators.
The review supplies no frame conversion, free initialization, physical dirty
buffer reuse, recursive child profile, packed router or larger exponent.
The arithmetic constant `23/24` is not promoted to a native logarithmic power
saving.

The executable is [wht_dirty_echo_review.py](../../code/complex/wht_dirty_echo_review.py).
Its fresh run protocol pins the reviewed producer and independent source
hashes. Run the bounded review with

```bash
python3 research/integer-mult-breakthrough/code/complex/wht_dirty_echo_review.py \
  --workers 1 --output /tmp/fresh-wht-echo-review.json
```

The finite inputs, signs, seeds, full word and inverse are deterministically
regenerable from this retained standard-library source.
