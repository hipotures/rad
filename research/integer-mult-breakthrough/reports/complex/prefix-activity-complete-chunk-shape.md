# Complete-chunk prefix codes for variable activity

Status: **EXACT FINITE ADDRESS AND PHYSICAL OPERATOR CONTROLS**, with an
**ALL-SIZE PREFIX SHAPE LEMMA**. The codec preserves the complete cube,
including every unselected guard bit. It does not supply fast native data
routing, grouping by child width, or a faster zeta primitive. No kappa is
asserted.

## Address shape

Use h slots, f columns and K bits per chunk. The original chunk at
`(slot*f+column)*K` contains one selected bit at offset `K-1`. The last
slot is the target; the other h-1 slots contain controls. A column is
active when all selected control bits are zero. This is the oriented
active pair 0/1. A separate paid fixed-h address map would be needed for
an arbitrary source/target pair.

For each column emit a prefix symbol consisting of its complete control
chunks. If inactive, also emit the complete target chunk. If active, defer
that target chunk. Concatenate all f prefix symbols, followed by all
deferred targets in column order. Exactly hf chunks remain, with no
additional address bits. If w columns are active, the final wK bits are
complete target chunks; the first `(hf-w)K` bits identify the group.

The local code is prefix-free. An active code consists of h-1 control
chunks with their selected bits zero. An inactive code cannot begin with
such a control prefix. There are

    A = 2^((h-1)(K-1)) active prefix symbols,
    I = (2^h-2) 2^(h(K-1)) inactive prefix symbols.

Their Kraft sum is

    A 2^(-(h-1)K) + I 2^(-hK) = 1.

Concatenating exactly f symbols preserves prefix-freeness. Their deferred
target chunks supply the free tail. The decoder reads f control prefixes,
reads an extra target exactly at each inactive symbol, and assigns the
remaining complete tail chunks to the active columns. This proves an
exact permutation of all `2^(hfK)` addresses.

Every valid fixed prefix is one aligned contiguous block of `2^(wK)`
records. The number of such blocks with width w is

    binomial(f,w) A^w I^(f-w).

Multiplying by the block length and dividing by total records gives
`binomial(f,w) (2/2^h)^w (1-2/2^h)^(f-w)`. Thus the volume-weighted
active count has the binomial law independently of K. This calculation
includes all inactive symbols and all K-1 unselected bits per chunk.

## Exact data operator

Let the active row addition have coefficient `c=(1-i)/2`, a dyadic unit
with inverse `1+i`. On an active pair its matrix is

    G(c) = [[1,0],[c,1]] = diag(1,c) Z_1 diag(1,c^-1).

The full f-column operator acts as identity on every inactive alphabet
symbol. Conjugating by the prefix permutation gives the direct sum of
`G(c)^tensor w` on the complete tail cubes. Each tail block is implemented
as `diag(c^wt) Z_w diag(c^-wt)`, counting weight only in the selected
tail bits. Unselected tail bits are spectators. The inverse uses Z_w^-1
and retains the same actual diagonal gauges.

The exact finite source verifies both directions on every basis column
using complete sparse maps, including zeros outside the generated
support. It also applies the actual forward and inverse to four arbitrary
Gaussian-dyadic fields in every record. These checks concern the full
physical operator, not only a source-origin sample or covariance argument.

## What remains unpriced

Python integer address encoding and vector indexing are permutation
oracles. Moving complete record payloads into this order on the retained
fixed tapes remains a new native obligation. Computing the prefix code
of one address in polynomial metadata time does not execute that data
permutation. The known fixed-h Boolean address wrappers do not automatically
implement this f-dependent codec.

Groups of the same w need not be adjacent in prefix order. Applying one
uniform-width bulk supplier to all of them requires batching or an
explicit separate dispatch contract. A future batching step must preserve
every entire record, original prefix tag, tail guard bit and record order,
with its forward and reverse movement costs. No free sort or f-pass
classification is included in the volume lemma.

The w=0 groups contain complete spectator payloads and still require
movement. Actual child calls need the whole Gaussian block and guard
endpoint contract, source/row counts, field precision, same-width endpoint
work and a well-founded supplier. Neither the codec nor the binomial law
establishes these obligations. The
[weighted-union capacity hypothesis](weighted-union-product-basis.md)
continues to require a real shorter zeta word and a paid activity route.

## Finite evidence and reproduction

The [full run](../../runs/20261009T064406Z-complex-prefix-activity-shape/report.md)
uses four workers with `(h,f,K)` equal to `(3,1,1)`, `(3,2,1)`,
`(3,1,2)` and `(3,2,2)`. All 4232 complete addresses round-trip. All
8464 physical forward/inverse basis columns and 16928 arbitrary Gaussian
fields pass. Every group is checked against its full aligned tail cube;
all binomial volume counts are exact. Omitting child gauges, dropping an
active target or cropping its guard bits is rejected. Source time is
0.419229 seconds for this finite arithmetic checker.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/prefix_activity_shape.py --workers 1 --bounded
```

Use four workers without `--bounded` for the full cases. The source is
standalone standard-library Python. Configs preserve its hash and seeds;
all addresses, matrices and fields deterministically regenerate. No
failed attempt occurred. Original source/protocol/results remain unchanged.

Attribution: the complex track derived the complete-chunk prefix codec
and checked its physical operator. The synthesis track independently
develops the elementary row-gate activity algebra and zeta circuits.
This is AI-assisted internal research, not formal verification or external
peer review.
