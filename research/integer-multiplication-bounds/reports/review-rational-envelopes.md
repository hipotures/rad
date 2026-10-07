# Independent review of positive rational support envelopes

The proposed envelope transfer is valid under the controller compiler's
existing constraints. This is a fresh audit after the increasing-source-span
milestone; it does not replace the pinned upstream conditional theorem.
Campaign interval: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Reference revision: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

## Envelope and nondegeneracy

For a nonempty family of source triples with nonempty intersection, let
`C` be its intersection and `V` its union. Define the rational subspace

```text
E(C,V) = {x : x outside V is zero,
              x_i=z for every i in C,
              sum_i x_i=3z}.
```

Every source indicator belongs to this space. For the actual rational
label form `H=I-J/9`, its quadratic form is

```text
x^T H x = sum_{j in V\C} x_j^2 + (|C|-1)z^2.
```

This is positive definite. When `|C|=1`, vanishing of the displayed squares
forces the outside coordinates to zero; the total-sum equation then gives
`z=0`. For `|C|=2` or `3`, the coefficient of `z^2` is positive.
Positivity is a statement over the rationals, separate from the scalar
circuit's characteristic-two arithmetic.

An independent basis follows directly from the constraints. If
`O=V\C` is nonempty, choose a pivot `p` in `O`. Use one vector with value
one on `C`, value `3-|C|` at `p`, and zero elsewhere, together with
`e_j-e_p` for `j` in `O\{p}`. The dimension is `|O|`. A realized
three-point core has `V=C` and gives the original one-dimensional triple
line. The compiler's synthetic triangle/star basis spans exactly this
constraint space over the rationals; an odd triangle's determinant is two.

For realized source families,

```text
E(Ca,Va) subset E(Cb,Vb)
    iff Va subset Vb and Cb subset Ca.
```

The forward implication uses the actual source indicators: each used
coordinate occurs in one indicator, and every coordinate in `Cb` must
occur in every indicator because its total sum fixes `z=1`. The converse
follows immediately from the equations. Thus the compiler's envelope
inclusion test has an exact rational interpretation, including links
between frames with different chosen common points.

## Physical endpoints, targets, and reverse computation

At a leaf, `C=V` is its source triple, so the envelope is exactly the
original input line. Source injection gates and the negative endpoint
rank correction therefore do not acquire a wider input label. At an
addition, support grows and the core shrinks; each child envelope lies in
the parent envelope. Retained-controller links still require successive
gate frames to increase. Every incident physical role can receive the
single positive common gate frame.

For the existing common-point outputs, a target triple meets `V` in just
one point `i` of `C`. Then `x dot 1_T=z` and `sum x=3z`, hence
`B_H(x,1_T)=0`. The entire envelope lies in the physical target complement.
An output controller is checked against the output node's own envelope,
forcing its final physical frame to equal that envelope. Fresh output
copies receive the same valid frame.

Reverse the physical schedule and take orthogonal complements. Forward
increasing envelope frames give increasing complement frames in this
reverse direction. Nondegeneracy of every envelope also gives
nondegeneracy of its complement in the retained nondegenerate ambient
form. Starting target lines lie in those complements, and final source
complements are unchanged because leaf envelopes are the original lines.
No positivity assumption about arbitrary target spans is needed.

The dirty-register identity remains the reviewed `J L V` identity for the
same invertible scalar mixer. Controller links affect the mixer and its
role count, while the enclosing transparent scratch schedule restores
arbitrary scratch. The count remains `R=c+q-links`; the envelope is not a
new scalar gate.

All side transitions remain increasing, and the original central returns
are still the only decreasing transitions. The rank telescoping, extra
endpoint source correction, and substitution of the actual role count in
`W=2N+2v^2(R+h)` remain valid. First/third-stage auxiliary endpoints are
unchanged. Their original orthogonal triple matching still permits the
same same-index stage joining and saves exactly one ambient rank per
merged role. The envelope enlargement cannot add an uncounted endpoint
rank loss because it changes only the internal increasing frames.

## Independent evidence

The new checker [review_envelopes.py](../code/review_envelopes.py) derives
the basis from the equations above, rather than the compiler's graph tags.
Its census compares those bases to the compiler's basis and tests rational
containment and Gram ranks using `fractions.Fraction`.

| Check | Count |
|---|---:|
| Source constraints and canonical span equality | 3,315 |
| Rational envelope inclusion comparisons | 15,625 |
| Rational target orthogonality comparisons | 4,310 |

The scalar tests expand every elementary operation on the complete local
side-invocation basis: input, output, and side dirty-scratch registers.
Both the forward neighbor shear and its transposed reverse shear restore
all side scratch. These tests omit the `h` central registers of the whole
identity shear; the parent's separate `exact_invocation` checks include
those registers, with complete basis sizes 196 at `h=6` and 816 at `h=8`.

| h | Physical roles | Complete side-invocation basis | Physical frame transitions |
|---:|---:|---:|---:|
| 6 | 150 | 190 | 708 |
| 8 | 696 | 808 | 3,888 |
| 10 | 1,840 | 2,080 | 10,360 |
| 50 | 486,200 | Not expanded in this review | 2,714,200 |

At `h=50`, the independent symbolic audit propagates the actual source
intersection and union through all 455,050 logical nodes, checks every
synthetic generator against the equations, verifies both physical frame
timelines and every designated output, and independently checks the
19,600-image stage matching. The compiler selects 8,050 links among
13,700 eligible links, giving `R=494250-8050=486200`.
The large scalar coefficient realization is a separate parent certificate;
the small complete side-basis tests do not stand in for a large dense computation.
The general dirty-mixer identity and transfer proof cover arbitrary size
once that finite mixer realizes its specified map.

Compact results, source hashes, exact commands, and verified interpreter
versions are recorded in the fresh `review-envelopes` run. Reproduce from
the repository root in the pinned math environment:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/integer-multiplication-bounds/code/review_envelopes.py \
  --reference "$REF" --h 6 --output "$OUT"
PYTHONDONTWRITEBYTECODE=1 python research/integer-multiplication-bounds/code/review_envelopes.py \
  --reference "$REF" --h 50 --skip-census --large --output "$OUT"
```

## Further eligibility, outside the current witness

The exact target condition can be broader. Put `k=|C|`, `O=V\C`,
`m=|T intersect C|`, and `n=|T intersect O|`. For nonempty `O`, a target
indicator annihilates the envelope exactly when it is constant on `O`
and

```text
n is 0 or |O|, and m+(3-k)n/|O|=1.
```

For `k=2`, a target containing all of `O` and none of `C` can qualify
when `|O|<=3`; its intersection point may vary between sources. This
opens an additional sharing pattern, but no count or theorem in the
current envelope witness depends on it. Arbitrary mixed source families
can still have degenerate rational spans, as the earlier review records.
