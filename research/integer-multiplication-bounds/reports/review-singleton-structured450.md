# Full independent structured450 singleton promotion

The completed 450-case structured search's fixed h50 winner passes the
unchanged independent full promotion checker with **472,985** physical
side roles. Its candidate identity is
`2af21b3008b368a4d6533a1fe5df2b4dc82979de24ac58260e708c2da8a16b04`,
and its base-4 positions are `[0]*6+[23]*26+[0]*18`.

The independently reconstructed compilation matches immutable producer
digest `a915626899ba308501e0abae7d187822fe29cd655941375996d0cbcfcaada077`.
Candidate byte SHA256 is
`6b1b790d03b8a946a1478ce8a64e45299e2325b139733cecc6ea198cb770dedb`.
[Run 20261008T021221Z](../runs/20261008T021221Z-review-singleton-structured450/)
preserves those candidate bytes, exact command, source/dependency identities,
log and certificate. Certificate SHA256 is
`eaff85ab21350a96a5179014dcb91f650f71c5aa81d2e912e2c623b01c27e217`.

The original immutable reference remains
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. The reviewer
[review_singleton_positions.py](../code/review_singleton_positions.py)
is unchanged, SHA256
`f6222a66a3c042a073aca9febd082e0ab2da814a438e7260665059a52b625bc0`.
It rebuilds all local graphs without accepting a throughput cache,
expands every logical coefficient and independently checks physical
fresh copies, controller chains and envelope equations.

| Full h50 quantity | Exact value |
|---|---:|
| Nonzero partial-output coefficients | 63,562,800 |
| Additions c | 448,068 |
| Designated outputs q | 58,800 |
| Retained links | 33,883 |
| Physical roles c+q-links | 472,985 |
| Fresh physical copies | 453,385 |
| Logical frames | 467,668 |
| Forward/reverse-complement physical transitions | 2,738,242 |

All source supports are disjoint and correct. Every physical gate output
and designated target is exact, all input frames are the original lines,
all output envelopes are correct, and every designated target is
orthogonal to its side frame. Both forward and reverse-complement
inclusions pass. Retained links use the same source, are acyclic, and
meet the separate one-retained-input gate capacities. All fresh physical
copies are included explicitly. Validity does not depend on a global
optimizer claim beyond the fixed graph/order/frame ansatz.

The nonuniform h6/h8 controls again cover complete side-invocation
bases of dimensions 190 and 795; including central registers yields
complete invocation bases 196 and 803 in both orientations. Four complete
shared three-stage exchanges at seeds 1 and 109 exchange both banks and
restore every auxiliary value. This does not claim a dense h50
whole-invocation matrix. The complete small dirty controls accompany the
full h50 scalar/frame/controller witness and the explicit all-size proof.

The full h50 phase took 76.291 seconds internally. The entire attempt
took 91.43 seconds and 3,099,704 KiB peak RSS under time -v, using
Python 3.14.7 and one BLAS/OMP/MKL thread. Its one reserved core was
released in the wrapper's finally block on completion; other useful
campaign workers were retained.

Relative to accepted R473026, additions decrease by 59 and links
decrease by 18, for a net role reduction of 41. The rational positive
envelopes, dirty-scratch chronology, reverse complements, source/central
rank accounting and stage join proof are unchanged. Composing this new
finite witness with compact/balanced estimates requires a separate exact
arithmetic certificate. A new arbitrary-routing hypothesis is not used
by this promotion.

Reproduce with the saved immutable candidate and fresh output path:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /path/to/math/python -B \
  research/integer-multiplication-bounds/code/review_singleton_positions.py \
  --reference /path/to/upstream-reference \
  --candidate research/integer-multiplication-bounds/runs/20261008T021221Z-review-singleton-structured450/results/candidate.json \
  --small-controls --output /fresh/path/review-structured450.json
```

This is an accepted finite conditional-transfer witness, not a universal
rank lower bound or an unconditional multiplication theorem certificate.
