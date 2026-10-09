# Rebalanced rectangle circuits and a complete dirty zeta shear

Status: **EXACT FINITE ARITHMETIC WORD AND SCOPED ALL-SIZE WIRE FORMULA**.
No faster native zeta supplier or complete multiplication exponent is supplied.

## Source-led question

Alman and Li's [arXiv:2509.14489v1](https://arxiv.org/html/2509.14489v1),
*Kronecker Powers, Orthogonal Vectors, and the Asymptotic Spectrum*, dated
17 September 2025, studies depth-two linear-circuit rebalancing. Their
Sections 1.4 and 2 distinguish circuit wires from a transform's depth and
give an asymptotic spectrum formulation. The paper is a primary reference,
not a native fixed-tape implementation. Its improved disjointness circuits
are not reconstructed or adopted here. The immutable PDF acquisition
receipt pins its original bytes and remains separate from authored code.

This investigation independently reconstructs the elementary two-rectangle
example and its full dirty arithmetic word. The question is whether an
asymmetric circuit decomposition can be used without silently clearing its
internal channels or interpreting wire count as native time.

## Exact elementary family

Let R_h[x,y]=1[x & y=0], and N=2^h. The one-axis matrix R_1 admits either
of these partitions of its three ones into two disjoint rectangles:

```text
({0,1} x {0}) + ({0} x {1}),
({0} x {0,1}) + ({1} x {0}).
```

At each recursive leaf choose the partition that doubles the smaller of
its row and column supports. Complement every final row label to obtain
the exact subset-zeta matrix Z_h[x,y]=1[y subset x]. There are N rectangle
channels, and every required coefficient is covered exactly once.

For a leaf whose nontrivial branch was chosen t times, its support product
is 2^t. Row and column support sizes are powers of two, so their sum is
at least 2^floor(t/2)+2^ceil(t/2). The balanced policy attains this lower
bound at every leaf. There are binomial(h,t) such leaves, regardless of
the adaptive orientation choices. Consequently the exact wire optimum
within these two literal one-axis partitions is

```text
W_h = sum_t binomial(h,t) [2^floor(t/2)+2^ceil(t/2)],
W_0=2, W_1=5, W_h=2 W_(h-1)+W_(h-2),
W_h = Theta((1+sqrt(2))^h).
```

The producer independently checks the small Bellman recurrence over all
allowed adaptive orientations. The all-size proof above is scoped to this
two-partition family, not all sparse factorizations or arbitrary circuits.

## Complete arbitrary-dirty word

Write Z_h=U V^T for the retained rectangle supports. With arbitrary x, y
and internal channel c, use the chronological word

```text
y -= U c;
c += V^T x;
y += U c;
c -= V^T x.
```

Its complete endpoint is (x, y+Z_h x, c). Every source and dirty channel
is restored; the inverse reverses the four actual stages and signs. The
first cut uses the original dirty c and cannot be omitted. The word pays
2 W_h arithmetic wire uses, rather than W_h with freely initialized gates.
It is a two-bank additive shear with N additional internal channels, not
an in-place native Z_h primitive. Any exact factorization of the full
invertible Z_h requires at least N channels by rank; changing this stock
needs a side term, a different topology or a different interface.

All retained coefficients are integers. For input magnitude at most B,
every source channel sum is at most N B, and every sink accumulation is
bounded by N(1+N)B plus the initial data. A coarse bound 2^(2h+2) B
therefore covers these four arithmetic stages, requiring O(h) extra guard
bits. It does not bound prefixes of an unsupplied native implementation.

## Cost discriminator and open leverage

The full scalar-vector arithmetic realization has work proportional to
R W_h when each value occupies R bits. Relative to its N R data volume,
the wire overhead is Theta(((1+sqrt(2))/2)^h). It grows exponentially in
the selected width h. When h is at least a positive power of outer d and
K is polynomial in d, this direct full-width evaluation exceeds a budget
polynomial in hK. This excludes this direct realization in that parameter
range; it does not exclude a packed native implementation.

A logarithmic packet h=gamma log2(d) is different. Its normalized wire
overhead is Theta(d^(gamma log2((1+sqrt(2))/2))). Such a packet can fit
a polynomial local budget in principle. It still needs actual full-payload
movement, stock allocation and a composition across all remaining axes.
Repeating a cheap packet without accounting for their number does not
give a complete transform saving. Coefficient widths, helper channels
and the full selected width must be bound to the assembly's parameters.

The next possible escape is a native sparse-factor realization that shares
dirty channels or releases them dynamically, with a complete endpoint
and actual recursive profile. The ordinary wire bound motivates that
question; it supplies neither such a release nor a native time theorem.

## Finite evidence and reproduction

The [four-worker run](../../runs/20261009T051605Z-zeta-rectangle-rebalancing/)
checks h=3,4,5,6, all matrix coefficients, all 3N source/target/helper
linear columns and four dense integer payload fields. The dirty word and
its true inverse pass, and deleting the old-dirty cut fails. Wire counts
are 29,70,169,408; the four-stage word pays twice each count. The complete
wire formula and its independent integer recurrence agree for h=0 through
48. All producer source and original run bytes remain unchanged.

The raw output label contains an anticipated time. Its actual launch was
05:16:05.516999 UTC; the protocol and persistence receipt retain this
distinction. No failed scientific attempt is hidden by that namespace.

From the worktree root, run a fresh full experiment:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/zeta_rectangle_rebalancing.py \
  --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/zeta-rectangles
```

The bounded check uses `--workers 1 --bounded` with a fresh optional
output path. Python's reference vector indexing is an arithmetic oracle,
not evidence of fixed-tape movement time. The proof and finite controls
are internal mathematical evidence, not formal verification.
