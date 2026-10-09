# Independent aligned guard-row geometry and conditional transfer review

Status: **INDEPENDENT ANALYTICAL AND SOURCE REVIEW**. The corrected row
allocation and the non-stable rehydration permutation are accepted under
the explicit interfaces below. A complete canonical native network,
its internal precision and its fixed-tape execution remain unsupplied.
This report establishes no larger characteristic root or multiplication
exponent.

## The original allocation and the separate corrected interface

The original [retired guard allocation](../../code/obstructions/retired_guard_row_pool.py)
is an exact finite allocation/reference-C experiment. It pools an old row
index with a fresh guard cube and then splits the combined index modulo W.
That does not generally preserve an independent complete guard cube in
each role. For example, with one old row, a four-point guard cube and W=3,
the three role fibers have fresh guard sets `{0,3}`, `{1}` and `{2}` before
padding. Padding the combined index does not establish a guard factor of
size four in every fiber. This is a limitation of that proposed native
interpretation, rather than a failure of its finite Gaussian allocation
identity. Its original source and evidence must remain unchanged.

The new [aligned source](../../code/obstructions/aligned_guard_row_pool.py)
uses a stronger interface. Fix h and W, keep the root chunk width K fixed,
and write the current selected width as

```text
e = 2h(g+1)+u,    0 <= u < 2h.
q = 2h+u,        G = 2^(qK).
```

The call first performs the selected elementary C on each of its q
terminal/remainder guard chunks. Each is one selected C, rather than a
full C_K. All K-1 remaining coordinates of each chunk are retained. These
q complete K-bit chunks become a fresh row factor G, leaving 2hg selected
active coordinates. This promotion is a change of tensor layout; its paid
physical implementation is part of the interface.

For R old complete rows, pad ONLY that old range to
`R' = W*ceil(R/W)`, with zero fields in every added record. Split the old
row as `old = W*k+w`, independently of every fresh guard coordinate.
Each role then has the exact product shape

```text
{0,...,ceil(R/W)-1} x {0,...,G-1} x complete active address cube,
R_child = ceil(R/W)*G.
```

No quotient representative or incomplete guard fiber replaces this fresh
cube. Each role has at least G rows. On the next recursive call, some
coordinates of the old G factor may participate in its old-row split;
that next call must preserve its OWN new G factor instead. At a child
endpoint the parent's row factor and layout must be returned exactly.
Complete all-field endpoint semantics are essential: agreement on zero
scratch or selected basis columns does not establish this restoration.

The split is bijective on the padded index ranges. After complete rowwise
canonical C endpoints, every added zero row is still zero and can be
removed. Existing nonzero and dirty fields return in their original row
order. The original rows' zero padding, complete payload movement,
metadata, returns and erasure are paid operations.

## Rehydration without preserving active coordinate order

Stable insertion of the guards into the active chunks can move Theta(g)
chunks. It is unnecessary for the full active C tensor. Consider the
2hg active chunks followed by the 2h fresh terminal guard chunks; the u
remainder guard chunks may stay in the preceding row factor. For guard j,
assign its complete chunk to position `(j+1)*(g+1)-1` by swapping its
CURRENT position with that target. Track positions after every swap.

There are at most 2h whole-K swaps. Distinct targets prevent any already
fixed guard from being displaced by a later assignment. Afterward every
terminal guard position holds the intended guard, and every nonterminal
position holds exactly one original active chunk. Their order can change.
Thus the rehydrated role has 2h complete equal `(g+1)K` subslots and a
common unchanged preceding row factor. In particular the row quotient
`k` and all u remainder guard chunks remain unchanged.

Let P be this literal chunk permutation, O the original active selected
bit set and N its image among the new nonterminal chunks. A network with
the complete physical endpoint `C_N tensor I_else` satisfies

```text
P^-1 (C_N tensor I_else) P = C_O tensor I_else.
```

Each swap moves a whole K-bit chunk without changing bit offsets within
it. Hence P maps the selected offset rho to rho in the new chunk and maps
all K-1 unselected bits as spectators. The displayed equality holds on
every physical address and arbitrary Gaussian payload; it includes all
unselected bits, the already transformed guard-selected bits, the old
row prefix and every record field. It is not an equality only on the
selected coefficient array.

The already completed guard C operators commute with the returned active
endpoint, since their selected axes are disjoint. Their selected bits
are not transformed a second time. Every local native wrapper must
restore the complete guard chunks and must be guard-independent wherever
this commutation is invoked. This requirement is stronger than merely
having a guard cube of the correct cardinality.

The paid original whole-chunk exchange interface gives at most 2h swaps
for rehydration and 2h for its inverse, per required layout conversion.
With a fixed finite network, the total number of these conversions is a
fixed constant depending on that network. It cannot be charged as a
free numeric index map. No stable-order insertion is claimed.

Most importantly, the canonical active network must be generated and
proved in the NEW slot grouping. Scalar gates, child masks, phase frames,
chirps, affine offsets, global units and any copies must all bind to
those same physical descriptors. Permutation symmetry of the final
C tensor does not validate unchanged old port descriptors, partial
outputs or a sampled phase word. The literal finite source checks the
permutation conjugation with C reference children; it does not supply
that complete network.

## Padding and a weighted recurrence without a node-count assertion

The relative padding factor at a node is

```text
eta(R) = W*ceil(R/W)/R <= 1+(W-1)/R.
```

If the root has R=1, its first padding costs a fixed factor W. This is
paid once and absorbed only as a fixed profile constant. Each nonroot
call retains a fresh parent cube, so `R>=2^(2hK)`. Therefore, uniformly
at nonroot nodes,

```text
eta(R) <= 1+epsilon_K,    epsilon_K = W*2^(-2hK).
```

Let the complete paid profile have n_r calls of rank r, `0<r<=h`, each
on one complete role stream. Define

```text
Phi(p) = sum_r (n_r/W)*(r/h)^p.
```

Require a strict margin `Phi(p)<1`, with `0<tau<=p<1`, and complete local
time at most `A*V*((eK)^tau+1)`. This bound must include guard preprocessing,
all row/layout movement, every wrapper, metadata, scalar temporaries,
exception repair, parking and returns. Every actual child width is at
most `(r/h)*e`. A full-rank child still decreases width by at least 2h,
because it acts on `2hg=e-2h-u`. This gives a well-founded width induction
even though its ratio approaches one.

For large enough K,

```text
q_p = (1+epsilon_K)*Phi(p) < 1.
```

Uniformly inflate the complete weights to
`(1+epsilon_K)*n_r/W`. This pays local padding at every nonroot node; it
does not need an estimate on the unweighted number of nodes. In
particular, a full-rank branch can have Theta(d) depth, and a branching
tree need not have a polynomial number of nodes.

Use the stopping width `H=max(4h,ceil(K^(tau/(1-tau))))` and charge a
complete elementary leaf at most `B*V*e`. A direct width induction proves

```text
F(e) <= C*e^p*H^(1-p),
C >= max(B, 2A*(1+epsilon_K)/(1-q_p)),
```

up to the harmless rounding constants. Indeed, for `e<=H`,
`e<=e^p H^(1-p)`. For `e>H`, the routing term obeys
`(eK)^tau<=e^p H^(1-p)`, and the sum of children's proposed bounds is at
most `q_p*C*e^p H^(1-p)`. Choose C to absorb the remaining strict margin.
Same-rank children have smaller integer width, so this induction has no
circular same-size improved oracle.

Including the paid fixed root padding gives

```text
F(d) = O(d^p*K^(tau*(1-p)/(1-tau))).
```

For `K=Theta(d^c)` and `c*tau/(1-tau)<1`, this is a sublinear selected-width
power. It is a conditional time conclusion for a supplied profile and
complete overhead contract. It neither creates a favorable Phi nor
increases a frozen characteristic root.

The maximum root-to-leaf depth is O(d), and the nonroot padding product
is at most `exp(O(d*epsilon_K))`. It tends to one when `K/log(d)->infinity`.
This path statement is separate from the strict weighted-moment proof;
it must not be used to infer a polynomial total node count.

## Numerical, layout and transfer obligations

Unlike the earlier [logarithmic-depth stopping theorem](routing-aware-depth-transfer.md),
this interface does not require an initial W^L row stock. It also does
not inherit that theorem's O(d log d) numerical guard. Under the
[endpoint-aware precision contract](endpoint-aware-guards.md), a worst-case
depth O(d) gives O(d^2) grid and magnitude allowances. The local-prefix
and complete arbitrary-dirty endpoint assumptions must be proved for
the actual new word, including every buffer and inverse. Endpoint
permutation symmetry alone does not bound internal excursions.

At every node there must be at least one whole long record per row. The
old row prefix can grow to O(dK) address bits; it cannot be charged as if
only the child's eK bits existed. Uniform metadata and bad-set repair
must be bounded using that actual prefix and the retained record length.
Likewise, the current volume includes all fields and the zero-padding
rows. A logarithmic old scheduling clock, free row repacking or a free
normalization step is not inherited.

The needed native operations remain conditional on the original paid
equal-complete-chunk exchange, elementary selected C and packed wrapper
interfaces. The fresh guard geometry makes those interfaces plausible;
it does not prove their integration into a complete all-size canonical
network. A changed row theorem cannot promote a framed identity shear or
an incomplete partial supplier to canonical C. Complete scalar and
phase ledgers, numerical bounds, fixed-tape layout and the outer exact
integer recovery must all agree before a larger kappa can be accepted.

## Evidence and reproducibility scope

The independent work here is analytical reconstruction and source review.
It did not import or independently execute either producer. The corrected
producer's finite controls use exact reference C children. Its K1 cases
cover four arbitrary Gaussian fields and full padded allocation/return;
its separate K1 rehydration controls check the actual chunk permutation
on every address. Those are producer observations, not an independent
native reproduction or formal proof. The dated receipt pins the exact
reviewed source versions and records these distinctions.

For original paid operator definitions, see
[02-streams.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/02-streams.tex)
and
[05-layers.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex).
Their immutable local inputs are read-only reference material. This
report changes the row/width interface explicitly; it does not assert
that the original native theorem already proves the new construction.
