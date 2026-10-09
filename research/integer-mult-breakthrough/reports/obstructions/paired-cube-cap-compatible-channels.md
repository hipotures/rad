# Target-cap-compatible channels for larger paired cubes

**EXACT ALGEBRAIC RESULT AND FINITE SUPPORT CERTIFICATES.** For the
five-coordinate paired-cube side, 211 raw overlap/pattern channels admit
141 independent actual-row channels within common future-cap flags.
Their joint scalar span has dimension only 16. These are three different
quantities. None is an attained physical workspace stock, a paid native
word, or a multiplier exponent.

The mechanism is motivated by the paired-cube decomposition reviewed in
[external PR163](pr163-reproduction-and-scope.md), and by the complex
track's larger-cube scalar/complete-baseline investigation. The present
integer-rational calculations import no external producer. The independent
complex-primitives review accepts the parity-cap argument and the small
block ranks. Literal dirty-bank completions are a separate live experiment.

## Side rows and actual source supports

Write `k=2r+1`. A source cube selects one coordinate from each of `k`
coordinate pairs. Its source label for selector `u` is the sum, over F2,
of those selected coordinate unit vectors. The central scalar polynomial is

    B_k(x) = product_(s=1..r) (x-(2s-1)) / (2^r r!).

Within a complete source cube this is twice the low-degree Walsh projector.
Its radial degree is `r`, it vanishes at odd overlaps `1,3,...,k-2`, and
its diagonal value is one. These conditions uniquely identify the displayed
polynomial. The [independent reflection producer](odd-cube-clifford-boundary.md)
supplies a separate direct Walsh kernel calculation.

For distinct source and target cubes let `J` be their common coordinate
pairs, `j=|J|<k`, and `t` the target choices on `J`. The cross-cube side
row is the negative of

    F_J,t(u) = B_k(j-wt(u_J+t)).

The sign does not affect the following ranks or supports. All source bits
outside `J` are spectators. For a nonzero entry the match count is even.
Thus every literal source label lies in the target's binary perpendicular
cap. Rows with the same parity of `t` have exactly the same support; the
opposite class has disjoint support. Target choices outside the source
cube do not affect the cap restriction on that source span.

For `j>0` this complete support spans a `k`-dimensional binary frame; for
`j=0` it spans dimension `k+1`, which is allowed by disjoint targets.
The producer checks those actual labels and caps, rather than inferring
support from rank. Expanding a nonempty-overlap support to the full cube
introduces an explicit label outside the target cap and is rejected.
These binary support facts do not by themselves supply actual Gaussian
phase representatives or a permissible dirty-bank chronology.

The model realizes every proper `J` when the total number of coordinate
pairs is at least `2k`. The finite label embedding uses `2k` pairs. With
fewer pairs some intersections are impossible and must be omitted from
the census. In particular, the complex track's `p=9,k=5` baseline has no
disjoint-cube `j=0` class. No multiplicity of target cubes is declared free:
the census groups algebraically identical query flags, while every
physical target delivery remains to be paid.

## Exact spectrum and all-size channel census

The matrix on the `j` relevant selectors is XOR-circulant. Its eigenvalue
at a Walsh character of weight `a` is

    lambda_j,a = 2^(j-k+1) sum_(b=0..r-a) (-1)^b C(k-j,b)
               = 2^(j-k+1) (-1)^(r-a) C(k-j-1,r-a),

where the last binomial is zero outside `0<=r-a<k-j`. To derive it,
restrict the complete low-Walsh projector to the `k-j` fixed opposite
selector bits and sum their character signs. Pascal's identity gives
the alternating partial sum. Therefore

    R_j = sum_(a=max(0,j-r)..min(j,r)) C(j,a).

For `j>0` translation by one selector bit exchanges the two parity
classes, so each contributes exactly `R_j/2`. Choosing independent actual
rows separately in each class retains the same physical cap. This avoids
using a global Walsh basis whose literal support spans an incompatible
full-cube frame.

Counting a separate algebraic basis for each proper intersection flag gives

    S_k = sum_(j=0..k-1) C(k,j) R_j
        = 3^k - 2 sum_(a=r+1..k) C(k,a) 2^(k-a).

Indeed, putting `j=a+b` turns each summand into the multinomial count for
three colors with the first two color counts at most `r`. Their forbidden
events are disjoint because `k=2r+1`. The weighted tail is at most
`4^k/2^(r+1)`, by multiplying every forbidden term by `2^a` and bounding
with the full binomial sum. Consequently `S_k/3^k` tends to one and
`S_k/2^k` grows asymptotically as `(3/2)^k` in this distinct-cap census.

| k | Raw channels `3^k-2^k` | Independent cap channels `S_k` | Source banks |
| --- | ---: | ---: | ---: |
| 3 | 19 | 13 | 8 |
| 5 | 211 | 141 | 32 |
| 7 | 2,059 | 1,429 | 128 |
| 9 | 19,171 | 13,981 | 512 |
| 11 | 175,099 | 133,893 | 2,048 |
| 13 | 1,586,131 | 1,264,173 | 8,192 |

By contrast, all these row spaces together span precisely the global
low-character sector of dimension `2^(k-1)`: every character of weight
at most `r` occurs for a suitable `J`, and none of higher weight occurs.
The gap between this global rank and the separate cap census is a concrete
representation problem. Changing encoded inputs or sharing chronological
flags could escape the separate census. It is not a circuit lower bound.

## Kernel parking and evidence boundary

An invertible completion of a rank-`R_j` block with `2^j` independent
dirty inputs must preserve its `2^j-R_j` kernel directions somewhere.
If each cap block independently retains all its input slots, its full
slot count returns to `2^j`. For `k=5`, the weighted missing directions
are `211-141=70`: 20 from overlap three and 50 from overlap four.
Calling the corresponding independent completions a 141-role circuit
would omit their kernel parking. Shared originals, shared parking or
compensated chronological reuse may change physical stock and must
receive a complete frame, old-read and inverse ledger.

The complete finite producer checks `k=3,5,7`, every relevant selector
entry, exact rational row reconstruction and all literal source supports.
Its ranks are respectively `[1,2,2]`, `[1,2,4,6,6]`, and
`[1,2,4,8,14,20,20]`. Every decoder coefficient in these retained actual-row
bases is integral; this is a finite observation, not an all-size gate bound.
The four-worker request completed in `0.282743` seconds at
[run 20261009T090947Z](../../runs/20261009T090947Z-paired-cube-cap-channels/report.md).

The separate [spectral census producer](../../code/obstructions/paired_cube_cap_channel_census.py)
checks the alternating-binomial formula, active degree band, parity rank,
multinomial identity and weighted-tail bound for `k=3,5,7,9,11,13`.
Its four-worker attempt started at `2026-10-09T09:14:41 UTC` and took
`0.0455674` seconds. The analytical proof above gives the all-size scope;
finite cases alone do not prove it. The two producers have distinct
methods and preserve their original source bytes.

From the repository root, choose a fresh directory for each command:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/paired_cube_cap_channels.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/cap-rows
python3 -B research/integer-mult-breakthrough/code/obstructions/paired_cube_cap_channel_census.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/cap-census
```

Both support `--workers 1 --bounded` using standard-library Python. The
first also imports the published odd-cube kernel source; the census is
self-contained. The decisive next test is a paid dirty-bank completion
and full target-flag chronology that improves on the explicit per-edge
baseline. No numerical parameter sweep or larger kappa is justified by
these row ranks alone.
