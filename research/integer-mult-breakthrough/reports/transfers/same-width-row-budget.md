# Same-width calls with a complete row and depth budget

Status: **EXACT CERTIFICATE** for the declared toy recurrence and
**HYPOTHESIS** for a different native phase architecture. No same-width
one-axis network, improved primitive or multiplication exponent is certified.

## What changes

The historical native recurrence insists that every child width `t` satisfies
`t<m`. A different recursive state may allow `t=m` while decreasing an explicit
remaining depth/row budget. This is a genuine change to the transfer, rather
than a larger exponent obtained from the old frozen child moments.

The full target moment must still contract. A same-width child's contribution
is its complete volume mass `n_m/W`. If `n_m>=W`, any additional positive child
already prevents contraction. The condition `n_m<W` alone is insufficient;
all remaining children, copies and conversions still need to be included.

## A terminating recurrence under explicit hypotheses

For a native profile with `0<t<=m`, choose `sigma=1-s` in `(0,1)` and require

```text
M(s)=sum_t (n_t/W)*(t/m)^sigma < 1.
```

Use the state `(e,L)` and recurse to
`(t*floor(e/m),L-1)`. Stop when `e<m` or `L=0`; the elementary leaf costs
`O(e)` per complete current volume. Every call decreases `L` and the available
complete row stock by a factor W. A single padded preceding row boundary of
at least `W^L` rows supplies all descendants. No selected coordinate is silently
discarded, and a same-width call retains its entire selected address cube.

At level j, the sum of volume-weighted `sigma`-powers is at most
`M(s)^j * e^sigma`, because floors reduce the positive power. If internal
overhead is `O(1)` per current volume, or more generally `O(e^tau)` with
`tau<=sigma`, the complete internal cost is `O(e^sigma/(1-M(s)))`.
Early bounded-width leaves contribute to the same geometric sum.

At the final budget boundary, every leaf width is at most e. Hence its combined
elementary cost is at most

```text
e^s * M(s)^L * e^sigma = e*M(s)^L.
```

Taking `L >= s*log(e)/(-log(M(s)))` makes this at most `e^sigma`.
The required complete row stock is polynomial in e, with explicit exponent
`s*log(W)/(-log(M(s)))`; its row-prefix length is `O(log(e))` with that fixed
coefficient. This prefix must actually fit the proposed physical layout and
be excluded from selected recursive axes. A small moment gap can make the
coefficient extremely large. It cannot be called free padding or advice.

This reasoning certifies a bounded-depth program once its local native map,
complete row allocation and elementary fallback are supplied. It does not
justify an improved-multiplier oracle at the same size. Width-only recursion
would be circular on aligned same-width children; the explicit budget is the
well-founded measure.

## Exact toy certificate

The [independent standard-library checker](../../code/transfers/row_budget_recursion.py)
declares `m=4`, `W=10` and complete child counts `{1:4,2:1,4:6}`. The self-mass
is `3/5`. At `sigma=1/2`,

```text
M = 3/5 + 1/5 + 1/(10*sqrt(2)) < 7/8,
(7/8)^6 < 1/2.
```

Both comparisons are checked rationally. Use `L=3*ceil(log2(e))`, complete
row stock `10^L`, and a leaf cost exactly e. An exact rational dynamic program
checks the declared complete costs, including the same-width calls and floors.
The analytical bound is `T(e,L)<=17*sqrt(e)`; the program compares its square
without floating point. The row-prefix length is bounded by
`12*ceil(log2(e))+1` bits. This is a toy saving of `1/2` for the declared
recurrence, not an integer-multiplication saving.

Four workers checked 22 aligned, remainder, large and early-leaf widths through
65536. Missing final row stock, broken W-way boundaries and unit self-mass with
an additional child are rejected. The checker explicitly preserves the
width-only termination failure as a negative control.

## Precision and other obligations change

A same-width dependency can persist for `L=Theta(log(e))` levels. A declared
guard recurrence of the old linear-per-node form gives

```text
A(e,L) <= A(e,L-1) + s_rank*floor(e/m) + E,
A(e,0)=O(e),
```

and therefore `A(e,L)=O(e*log(e))`, rather than the old `O(e)` guard obtained
from strict width contraction. The checker evaluates this declared ledger;
it does not prove it for an actual Gaussian circuit. A new physical program
must establish a fixed common-grid bound and a paid guard large enough for
its real dependency paths. For every fixed positive zeta, logarithmic growth
can eventually fit `e^(1+zeta)`, but the resulting strict capacity conditions,
rounding, source phases and recovery must be rebuilt.

The row-volume argument also does not prove a native compiler, complete-payload
fixed-tape copying, eligible prime construction, endpoint correction, or
outer FFT/Gaussian integration. If routing has exponent tau above sigma, that
cost remains a barrier. A stronger complex primitive alone cannot use an
unchanged weaker binary router to produce a larger final kappa.

## One-axis candidate and first chronology obstruction

A one-axis primitive could reduce ambient dimension from `h^2` to h, potentially
changing the attainable scale. It must have a lawful complete scalar/frame
schedule. The old tensor-two child list cannot be specialized by replacing
`m=h^2` with `m=h`: its interstage width `m-2h+1` would become negative.
Each actual one-axis frame change must instead be derived from its operations.

The coordinator identified a specific failed completion. One first shear can
save two rank units per data role pair by using source/target frames
`C_U->C_F` and `I->C_Uperp`. Completing the signed exchange with direct scalar
gates at the common full frame requires a rank-one raise and rank-one return;
the two charges erase that data saving before the retained-center charges.
Using the complementary common frame produces the analogous down/up expense
on the other data role. This excludes that naive first-shear/direct-completion
chronology only. It is not a lower bound for shared or differently framed
one-axis programs.

The next decisive task is a new chronology, with a literal reversible word and
complete same-width counts satisfying the moment. Until that exists, the row
budget is an analytical mechanism with an exact toy certificate, not a
realizable conditional exponent.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/row_budget_recursion.py \
  --workers 1
```

For the four-worker evidence, append `--workers 4 --output` followed by a fresh
ignored JSON path. The source generates every declared input and negative
control. No external dependencies, data or machine-local binaries are required.
Both the checker and this deduction were authored with AI assistance.
