# Strictly nested dirty births through a degenerate donor

A dirty helper can continue directly from a degenerate donor frame into a
strictly larger recipient birth, while retaining its source-dependent old
value and restoring all helpers only after their final life. The exact
finite component removes children of widths 2 and 3, adds width 1, and
removes one physical role. The complete first-moment deficit stays 4.

This extends [the equal-frame control](degenerate-birth-reuse-component.md).
The CUT dirty-offset identity and the paid pair majorization are the
mechanisms inspected in the read-only birth-read reference at commit
`ca8725485a822769f24c2e4e9b8955b31a42b044`, not a claim of newly invented
scalar slot reuse. The new finite extension here binds strictly growing
births with a degenerate actual donor and complete phase adapters.
The four-bit source labels remain `(1,7)` and target labels `(8,14)`.
The donor is `E=span(1,7)`, dimension 2 with radical `span(6)`. The second
recipient is `sigma=14-perp=span(1,6,10)`, dimension 3. E lies strictly
inside sigma. Its actual operator is the pinned canonical `F_sigma`,
including all row and column phases. The relative `F_sigma*F_E^-1` is
one rank-1 child with the retained affine/quadratic wrappers. No projection
matrix for the degenerate E is assumed.

Two input helpers receive the original sources at their line frames and
advance to E. Both sinks advance to E. The first node life forms `a+b`
and reads it into the first sink. The first sink then reaches its final
kernel. The continuing sink and operands advance to sigma. The same node
advances from E to sigma, retains its old value g, subtracts the CUT
future response `g` from the second sink, then forms `2a+3b` and reads it
there. The second g includes the first life’s source contribution and
dirty offsets; it is not fresh independent garbage.

The clean maps are `y0+=x0+x1` and `y1+=2x0+3x1`. There is no source or
workspace uncompute between lives. At the end, sources and helpers reach
full. All real workspace gates and source injections reverse in exact
chronological reverse order. This restores every original virtual dirty
value. Physical dirty outputs are `C_full` times those original values.
Grouped source cleanup before workspace inverse is incorrect and is
detected by an exact Gaussian field.

| Case | Stock | Width 1 | Width 2 | Width 3 | Rank | Capacity | Deficit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Separate node lives | 8 | 11 | 4 | 3 | 28 | 32 | 4 |
| One unrestarted helper | 7 | 12 | 3 | 2 | 24 | 28 | 4 |

Four workers completed the
[actual-time run](../../runs/20261009T023422Z-synthesis-nested-degenerate-birth/report.md).
The f1 baseline/reused cases replay all 128/112 physical basis columns.
The f2 cases replay all 8/7 bank origins and three complete Gaussian
dyadic fields each. No origin-only covariance shortcut is used. Omitted
CUT, omitted later-birth compensation, incorrect inverse source ordering,
and wrong raw-identity dirty targets are rejected. The run pins the
21-file standard-library experiment closure.

The [literal contract](../../fixtures/synthesis/nested-degenerate-birth-contract.json)
retains every actual frame gate word, route, physical event, response cut,
one-child affine map, quadratic phase and direction. Matrix hashes bind
the compact adapters to all coefficients used by the producer. Its
[exporter](../../code/synthesis/dump_birth_contract.py) is retained so
the essential fixture can be regenerated without an ephemeral script.

## General paid-moment consequence

Suppose a **complete valid chronology** has a dead donor ending at actual
`F_E` of dimension e, and an untouched later recipient whose birth
operator is `F_sigma` of dimension s, with `E subset sigma`. Suppose the
donor’s terminal reads are complete and the recipient’s CUT old-value
response can be supplied in its exact birth operator. Retain every future
source injection and workspace operation and reverse them in true order.
These are assumptions on an actual chronology, not on scalar supports
alone.

Before joining roles, their paths include a donor completion of width
`m-e` and recipient entrance of width s. Reuse replaces these by the
width `s-e` interface and removes one role of capacity `m^p`. The change
in the numerator of the recursive moment is

```text
delta_p = (m-e)^p + s^p - (s-e)^p,   0<p<=1.
```

Let `c=s-e`. Both `m-e` and s lie in `[c,m]` and their sum is `m+c`.
Concavity of `x^p+(m+c-x)^p` makes its minimum on that interval occur at
an endpoint. Therefore `delta_p>=m^p`. At p=1 equality gives a rank
decrease of exactly m, preserving the capacity-minus-rank deficit.
For `0<p<1`, `e>0` and `s<m`, strict concavity gives `delta_p>m^p`.
Thus the complete slack `W*m^p - sum_r n_r*r^p` strictly improves after
the role is removed. Existing strict contraction is preserved. This
statement also covers `s=e`, with the zero-width child omitted.

Degeneracy of E does not enter this inequality. The actual nested
Gaussian interface supplies width `s-e` even when E has a radical.
The finite control verifies the nontrivial case `m=4,e=2,s=3` and its
complete dirty/source/sink chronology. The moment lemma cannot supply
the required missing birth response, justify an arbitrary matching, or
replace unpaid gauge/tape/precision operations with free frame labels.

Reproduce the experiment and regenerate its fixture from the dedicated
worktree root, always using fresh output locations:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/nested_degenerate_birth_reuse.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-nested-birth/results
python3 research/integer-mult-breakthrough/code/synthesis/dump_birth_contract.py \
  --producer nested_degenerate_birth_reuse --output <fresh-contract.json>
```

The source is
[nested_degenerate_birth_reuse.py](../../code/synthesis/nested_degenerate_birth_reuse.py).
This is a broader structural reuse mechanism and an exact finite side
component. It is not a complete identity shear, signed exchange, native
tape theorem or new multiplier exponent. The next step is to find a joint
whole-word chronology with compatible strictly growing births, rather
than composing independently completed bodies.
