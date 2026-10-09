# Geometric recursion with nonunit endpoint and literal grid charges

Status: **CONDITIONAL ALL-SIZE NUMERICAL AND EXACT-GRID LEDGER, WITH
COMPLETE FINITE DIRTY-BANK CONTROLS**. This is a new typed endpoint
contract. It does not apply the frozen unitary lemma to zeta, furnish a
native activity codec, supply a shorter Z circuit, or assert an exponent.

## Complete contract

Associate a nonnegative integer selected width e with every call. For
e above a fixed leaf cutoff, every child has width
`w<=theta*e`, with one fixed `0<theta<1`. The number of children is at
most a fixed s. All physical payload fields, dirty banks, copied streams,
parked buffers, normalization temporaries and ancillary records belong
to the normed state.

Require the actual complete forward and inverse child endpoints to have
operator norm at most `2^(a*w+a0)` for fixed a,a0>=0. If an inverse is
never called, its norm is unnecessary, but any called inverse is a
separate actual type. For each node, the PRODUCT OF INDIVIDUAL operator
norms of all local steps in any prefix, suffix or interval is at most
`2^(b*e+b0)`. This includes address-conditioned scalings and their actual
scalar temporaries. Cancellation between local factors separated by a
child may not reduce this charge. A bound on the multiplied local word
with the children omitted is insufficient when the child does not
commute with those factors. Rounded-payload-dependent routing is excluded unless
a separate stability argument is supplied.

The number of local scalar steps may be fixed while their norm grows with
e. This differs from the earlier uniform-B contract. An address diagonal
`c^weight`, with fixed nonzero Gaussian-dyadic unit c and at most e
selected bits, has log norm and inverse log norm O(e). That statement
alone does not bound every prefix of its implementation; its literal
shifts, buffers and compensation must also be covered.

Completed children in a prefix contribute at most
`a*s*theta*e+s*a0` logarithmic norm. Only one descendant remains active.
Thus a sufficient prefix or tail recurrence is

```text
g(e) <= (b+a*s*theta)*e + b0+s*a0 + max_(w<=theta e) g(w).
```

At depth L=O(log(e+1)), the active widths have sum at most
`e/(1-theta)`. Consequently

```text
log2 Gamma(e)
 <= (b+a*s*theta)*e/(1-theta) + O(log(e+1)).
```

No unitarity is assumed. An interval can meet two active stacks; the
same geometric sum gives log norm O(e). For an invertible square total
endpoint E, one conservative alternative is
`||interval|| <= ||prefix|| ||E^-1|| ||tail||`, hence at most
`Gamma(e)^2*2^(a*e+a0)`. Rectangular row embeddings/projections require
the two-stack argument instead of an invented inverse. Both versions
retain a linear logarithmic bound.

## Approximation and signed guards

With N real scalar rounding injections of size at most 2^-q, the complete
final error is at most `N*Gamma(e)*2^-q`. An exact endpoint norm bound
also charges propagation of any prior input error. For desired absolute
precision 2^-t, choose

```text
q >= t+ceil(log2 N)+ceil(log2 Gamma(e))+O(1).
```

The interval bound separately controls intermediate accumulated errors.
A further O(e) reserve, or a correspondingly enlarged magnitude guard,
is sufficient. It is not valid to transport intermediate error using
only the final tail bound.

With fixed s, geometric depth bounds the number of nodes by a polynomial
in e. If each node has at most the complete maximum scalar volume M_max
and polynomial local work, then `log N=O(log M_max+log(e+1)+log p)`.
Thus q is `t+O(log M_max+e+log p)`. When t,log M_max,e are O(p), the
coefficient precision and signed guard remain O(p), subject to the
literal local temporary and actual record-layout contract. This is
numerical feasibility, not a time bound.

For signed input coordinates of magnitude at most 2^R, the exact prefix
norm bounds coefficient magnitudes by
`Gamma(e)*sqrt(M_max)*2^R`. Counted numerical interval errors and local
temporary numerators add their explicitly reserved allowances. A final
zero-row projection is a contraction and can discard only charged error;
intermediate correlated dirty fields cannot be declared zero.

## Exact endpoint grid is also linear under geometric decrease

Suppose the SUM of the grid increments of all local literal factors
and temporary divisions at one node is at most `c*e+c0`, and the COMPLETE
endpoint matrix of a child of width w has grid increase at most `k*w+k0` on
every arbitrary current dirty field. A completed child need not inherit
its entire internal grid excursion. The unresolved-stack ledger gives

```text
grid_excess(e)
 <= (c+k*s*theta)*e/(1-theta) + O(log(e+1)).
```

The same argument gives a linear magnitude guard using the exact norm
ledger. For pure Z_w and signed T_w endpoints, both inverse matrices
are integral, so k=k0=0. Grid charges then come from the actual local
dyadic words and the one active internal excursion. Width-linear local
charges have a convergent geometric sum.

This is a statement about divisibility and exact values in a fixed
GLOBAL physical grid. No Fraction simplification, physical regridding,
or output normalization is free. The native child must act exactly on
all current fields with that physical format and return its promised
endpoint. Mathematical endpoint divisibility can justify trailing zero
bits without deleting or shifting the complete payload. Every literal
arithmetic temporary still needs the proved reserve.

The linear bound is stronger than a conservative e times depth bound
for this special contract. It does not improve a recurrence with a
same-width child, a width-dependent number of overlapping siblings,
or an unsupplied endpoint map.

## A literal discriminating word

The [standard-library source](../../code/transfers/geometric_endpoint_guards.py)
uses two complete arbitrary Gaussian banks and calls actual recursively
constructed Z words. At width e>1, define

```text
D_e = diag(2^e,2^-e) on the two banks,
M_e = (bank0 += 2^-e bank1; bank1 += bank0).
```

Apply D_e, then M_e. Partition the selected axes into three consecutive
groups as equally as possible. Call the corresponding child words on
BOTH banks, leaving the other axes as spectators. Finally undo M_e and
D_e in their true reversed order. For e=1, the endpoint is one lower
zeta addition; its inverse is subtraction. For every e>=2, each nonempty
group has at most e/2 axes.

Bank-only operations commute with the same address operator on both
banks. Thus the full exact endpoint is Z_e on both original dirty banks.
The specified inverse recursively reverses child order and signs, and
is the true inverse physical word. Restored scratch here means the
declared Z_e phase of every bank; raw identity dirt is not claimed.

Each Z_w and inverse has norm at most 2^w. D_e and inverse have norm 2^e,
and each of the four shear steps has norm at most two. A sufficient
local bound is `2^(2e+4)`. The sum of the three child widths is e, so

```text
log2 Gamma(e) <= 3e+4+max_child log2 Gamma(w).
```

The source conservatively uses `Gamma(e)=2^(18e)`. A local unreduced
fractional temporary requires at most 3e extra bits, while the entering
ancestor charges are at most twice each ancestor width. With halving,
`2*sum_(prior ancestors) e_j+3e_current<=4e_root`. Hence the chosen
fixed exact grid is q+4e. Every division is tested for integrality in
that fixed physical grid. A second minimal-grid reference is diagnostic
only and never supplies the actual exact replay.

There are four real-component division steps per internal node. On two
Gaussian banks of D=2^e records they give exactly
`N=8D*(internal nodes)` rounding writes per direction. The rounded
forward endpoint error is bounded by N Gamma ulps. Its rounded undo
also amplifies prior forward error by the exact inverse bound 2^e, so
the complete undo bound is `N Gamma(2^e+1)` ulps. The source chooses

```text
q=t+ceil(log2 N)+18e+e+4.
```

This additional e-bit reserve covers both inverse propagation and a
conservative intermediate interval bound. Complete signed fields, every
stored numerator and the fixed local arithmetic margins are charged.

The full four-worker run passes in 0.361 source seconds:

| e | q | Exact physical grid | Minimal exact prefix excess | Unreduced literal temporary excess | Rounding writes per direction |
| --- | ---: | ---: | ---: | ---: | ---: |
| 3 | 99 | 111 | 6 | 9 | 64 |
| 6 | 193 | 217 | 16 | 18 | 2048 |
| 8 | 297 | 329 | 22 | 25 | 8192 |
| 9 | 317 | 353 | 24 | 27 | 16384 |

All sixteen complete fractional Gaussian dirty fields satisfy exact
direct Z endpoint equality, exact fixed-grid inverse restoration and
rounded full-field forward/undo bounds. The tiny e=3 case binds all
sixteen physical bank columns. Every rounded case has nonzero actual
injections. An all-ones control refutes a false unitary endpoint premise;
an undersized fractional reserve fails an exact division.

Only compact complete-field hashes, error norms, grid/guard counts and
comparison outcomes were captured. The actual arrays are deterministically
regenerable from the fixed seed; they are not claimed to be retained raw
evidence. The direct array accesses are reference operations. The word
uses no row split, native activity codec or faster supplier. Its three
tensor-subblock calls do not provide a contracting same-volume time
moment for an exponent below one.

## Activity-codec integration boundary

A fixed h row word may have fixed g gates while an activity codec issues
f+1 different population-width child calls PER gate. Fixed branching
is then not automatic. If these completed children act on disjoint
complete payload regions, their combined endpoint is block diagonal:
norm and grid charges use the maximum region width, rather than the
sum. This can preserve the O(e) bound. The exact definition of a region
must include all dirty fields, companions, buffers and returned values.
Overlapping calls or a response mixed into another child's region need
a separate paid width-sum or operator argument.

Polynomial branching and geometric depth give
`log N=O(log M_max+log^2(e+1)+log p)`, which is still O(log M_max+e+log p).
It does not repair a missing completed-sibling norm bound. Exponentially
many independently assembled activity regions require their own count
and complete-volume ledger.

The independent synthesis track's hypothetical shorter Z_h word and
activity moment remain unproved components. Gaussian-unit row weights
can contribute O(e) norm and grid charges, but their full literal
implementation, inactive alphabet, prefix codec, payload moves,
guards, native row stock, stopping and strict moments all remain paid.
The precision theorem does not convert a scalar g=11 hypothesis into a
native recurrence. The geometric contract is a useful continuation
criterion only when those actual interfaces are supplied.

## Reproduction and attribution

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/geometric_endpoint_guards.py --workers 1 --small
```

Four workers reproduce the full cases. The source and portable config
are the complete runtime closure, using only the standard library. A
fresh output path is required for every attempt. The run protocol binds
actual UTC start, seed, source/config hashes and captured evidence scope.

Attribution: the coordinator proposed geometric nonunit endpoint charges;
the transfer track independently derived the typed ledger, exact-grid
extension, sibling caveat and literal discriminator. AI-assisted internal
research and finite replay, not formal verification or external review.

## Local-factor contract clarification

The earlier bounded receipt pins report version
`8ef7c23dfe82b93dd27bf4d3303ce592a6bcf97a995eb10e73e891c76fc85456`.
Its local-prefix wording did not explicitly distinguish an operator
product bound from the product of the separate local factor norms. The
current general theorem requires the latter, so it cannot hide local
cancellations across a noncommuting child. Its grid premise similarly
charges the sum of actual local denominator increments. The literal
prototype already meets the stronger norm premise: the product of all
local factor bounds is at most `2^(2e+4)`. Its separate exact 4e grid
argument uses the known bank-specific divisibility structure and was
actually replayed on a fixed grid. Neither source, configuration nor
finite result changed. A retained current-to-original report patch
recovers the exact earlier version; its bounded protocol is unchanged.
