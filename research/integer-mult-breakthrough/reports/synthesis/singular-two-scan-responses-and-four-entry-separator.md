# Singular two-scan responses and a four-entry separator

## Changed hypothesis

This experiment lifts the invertible one-bank diagonal restriction.
It asks whether `Z_f` can be a sum of responses

```
Z_f = sum_l S_l diag(w_l) T_l,
```

where `S_l,T_l` are prefix or difference in natural or alternating
complement-shear order, and `w_l` may contain zeros or nonunits. There
is no a priori bound on the number of summands. The outside address
gauges are fixed to identity; separate arbitrary row/column gauges,
other orders and deeper products remain outside this family.

The leverage would be constant-count native responses with one reusable
arbitrary dirty helper. For a single response `B A`, the four exact shears

```
z += A x;   y += B z;   z -= A x;   y -= B z
```

give `y += B A x` while preserving `x` and the original dirty `z`.
Here `A=T` and `B=S diag(w)`, which may be singular. This construction
needs an additive native scan response that preserves its source and
restores any temporary tapes. Neither invertibility nor a free inverse
of `w` is assumed. All four responses and coefficient operations remain
paid; the current experiment only binds their exact finite operators.

## Small exact positive

The sixteen scan-pair families give `16N` scalar coefficient variables.
Complete exact capacity checks at `f=2,3,4,5` produce:

| Width | `N` | Rank of response span in both tested fields | Zeta in span |
| --- | ---: | ---: | --- |
| 2 | 4 | 13 | yes |
| 3 | 8 | 52 | yes |
| 4 | 16 | 149 | no |
| 5 | 32 | 341 | no |

These are separate exact `F_3` and `F_5` computations, not inferred
rational ranks. At `f=2` and `f=3`, independent exact rational elimination
then finds dyadic witnesses. The `f=3` witness uses eight nonzero
scan-pair groups with thirty nonzero diagonal coefficients. It is
implemented by thirty-two abstract additive scan shears through the
same arbitrary dirty helper. Complete replay checks all twenty-four
source/sink/helper columns and the inverse. The coefficient ledger and
zeros are retained in the original certificate.

This is a finite positive in a wider response space than the preceding
one-bank products. It neither improves elementary gate count nor gives
an all-size native supplier. A finite positive cannot justify assuming
the larger widths have the same response identity.

Source:
[two_scan_response_span_probe.py](../../code/synthesis/two_scan_response_span_probe.py).
Evidence:
[capacity run](../../runs/20261009T110406Z-synthesis-two-scan-response-span/report.md).

## Exact all-size obstruction in this family

The failures at four bits admit a short structural explanation, stronger
than the finite real-field exclusions. Set

```
u=e_5-e_7,  v=e_0-e_2,  N=2^f>=16.
```

For every natural/complement-shear prefix or difference `S`,

```
support(u^T S) subset A={4,5,6,7,N-6,N-8}.
```

For every such `T`,

```
support(T v) subset B={0,1,2,3,N-1,N-3}.
```

The sets are disjoint for `N>=16`. Therefore for any diagonal `w`, over
every field and also over the complex numbers,

```
u^T S diag(w) T v = 0.
```

Linearity gives the same zero for any number of response summands.
The zeta target instead satisfies

```
u^T Z_f v = Z[5,0]-Z[5,2]-Z[7,0]+Z[7,2] = 1.
```

Thus the entire fixed two-scan response family is impossible for every
`f>=4`, including arbitrary complex, singular and cancellation-allowing
middle coefficients. The helper construction cannot enlarge the stated
linear response span merely by repeating or recombining its summands.

Here is the complete support derivation. Natural prefix row differences
are supported at `{6,7}`, and natural difference row differences at
`{4,5,6,7}`. The complement map fixes even labels and maps odd `x` to
`N-x`. Its prefix row difference is supported at `{5,N-6}`, and its
difference row difference at `{5,7,N-6,N-8}`. Natural prefix column
differences are supported at `{0,1}`, and natural differences at
`{0,1,2,3}`. Complement prefix column differences are supported at
`{0,N-1}`, and complement differences at `{0,2,N-1,N-3}`. These four
lists yield exactly the two containing sets above. Each statement is
an integral support identity, so no characteristic or sign assumption
is hidden in the proof.

Fresh exact integer controls bind all 22,272 complete generator
coefficients at `f=4,5,6,8,10`. A changed-functional negative rejects,
and a surviving `f=3` response correctly rejects extending the
obstruction below its stated threshold. The written all-size support
argument is not a formal proof package.

Source:
[two_scan_response_four_entry_obstruction.py](../../code/synthesis/two_scan_response_four_entry_obstruction.py).
Evidence:
[four-entry run](../../runs/20261009T110914Z-synthesis-four-entry-response-obstruction/report.md).

## Interpretation and paid boundaries

This result does not exclude arbitrary multipath circuits, outside
diagonal gauges, nonlex orders other than the chosen complement map,
non-diagonal intertwiners, or longer scan products. The support separator
depends on those actual order choices and the fixed target labels.

Even the small positive must pay native additive source preservation,
helper endpoints, complete record buffers, address ordering and undo,
all coefficient multiplication, common dyadic grids and every internal
prefix. A whole prefix of width `f` has `2^f` row amplification. Complete
Gaussian dirty restoration at an abstract shear boundary does not
automatically price the native implementation inside that shear. No
recursive moment or kappa follows from this package.

The next useful family must escape the separator, for example by actual
different orders, outside amplitude factors, or a longer interference
word. Repeating the excluded sixteen responses does not do so.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/two_scan_response_span_probe.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/FRESH-response/results
python3 -B research/integer-mult-breakthrough/code/synthesis/two_scan_response_four_entry_obstruction.py --output research/integer-mult-breakthrough/work/synthesis/FRESH-separator/certificate.json
```

The second command also has a bounded mode and an optional fresh output
file. The first retains its original full coefficient witness and all
finite operator capacities in an immutable fresh attempt. Exact source
closures and original raw paths/hashes are recorded with the runs.
