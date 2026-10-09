# Activity compaction retains its paid routing exponent

Status: **CONDITIONAL NATIVE COST AND STOPPING DISCRIMINATOR**. The current
selected-only compaction fixes an important physical layout interface.
Its inherited cost proof does not supply a routing exponent arbitrarily
close to zero. This is a limitation of the stated construction and bound,
not a lower bound on all fixed-tape routing or multiplication algorithms.

## Actual inherited supplier

The primary source is `04-swap.tex` at openai/math revision
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, SHA256
`412b170ccaab38dba96e95e3cbfae09f4876a9818f8d278776a746b0f8044906`.
Its arbitrary-width interchange lemma supplies O(V L^tau) on complete
payloads, including padding and cleanup. The explicitly established
value is tau=1-2^-50. The preceding power-width theorem permits another
fixed tau only when a supplied finite bit-network rank/stock inequality
supports it. It does not quantify over arbitrarily small tau.
See the [immutable primary source](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/04-swap.tex).

The pinned `05-layers.tex`, SHA256
`20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`,
implements a packed selected-bit addition by eight rotations and at most
sixteen such chunk exchanges. Rotations with preceding controls and the
fixed final selected-bit permutation have O(V) movement, apart from
their separately charged metadata. Bringing each target after its
controls is the reason the full-width exchanges remain in the bill.

The [selected-only Benes component](../synthesis/benes-control-fiber-native-interface.md)
uses eighteen packed words per stage and 2 log2(f)-1 stages. A forward
and inverse around a child therefore use O(log f) complete words.
The constant stock placements use at most 240 complete K-bit exchanges
for the whole component. With full-slot width L=Theta(fK), the directly
inherited movement bound is

    O(V [(fK)^tau+1] log(f+1) + V K^tau).

The metadata and complete exceptional-record repair add, conservatively,

    O(log(f+1) [M(A^3+C_G(A))
                + delta M A(R+A)]),
    V=M R, delta=O(f 2^-K).

Here C_G includes actual control-label reconstruction, switch-mask
generation and canonical permutation metadata. For a fixed-degree
polynomial C_G, A=O(p), f<=d<=p, long payload R exceeding every fixed
polynomial in p, and K/log p tending to infinity, these added terms are
o(V) after including the logarithmic factor. This simplification must
be checked over the actual child family, not just a root rectangle.
It does not delete the full-width exchange term.

The original finite address and Gaussian controls validate their declared
operators. They are not measured fixed-tape runtimes. This review reads
their source and report but does not repeat the producer's large run.
The non-power-of-two width path, complete guard processing, child row
traversal and all primitive endpoint contracts remain separate.

## What disjoint cylinders improve

Complete width fibers give the correct binomial payload-volume weights
and a block-diagonal completed operator. Endpoint norms combine by a
maximum across those fibers; a fiber-aware geometric precision lemma can
therefore avoid multiplying norms across every width class. The paid
seven-tape grouping adds O(V log(f+1)+M A^3) under its record contracts.
These facts do not speed up global whole-slot exchanges that occur
before the child call. No bound O(V(EK)^eta) for eta<tau follows from
relabeling the fibers or replacing record counts with their probability.
The displayed bill alone also does not prove that a faster algorithm is
impossible.

If a genuinely stronger chunk-exchange or control-order supplier is
proved, the same packed chronology may consume it. A route that avoids
the exchanges altogether would instead need a new complete-payload
proof for its current, following and borrowed control fields. Numerical
mask evaluation or RAM gathering is insufficient.

## Two separate stopping ledgers

For the original-style cutoff e>=d^beta, K=d^c, a potential power p must
absorb the actual local movement. Since K<=e^(c/beta), its power part is
e^[tau(1+c/beta)]. A sufficient strict comparison, also absorbing the
logarithmic stage count, is

    tau(1+c/beta) < p < 1.

The assumed child moment must independently be strictly less than one
at that p. Stopping with O(V e) elementary work below d^beta gives the
potential bound O(V d^[p+beta(1-p)]), up to the fixed charged constants.
Its selected-width saving is (1-beta)(1-p), and it is smaller than
1-tau. Dropping the K factor and checking only tau<p can falsely accept
an incompatible parameter set; the exact retained control demonstrates
this error.

The separately proposed balanced cutoff uses
H=K^[tau/(1-tau)]. Under its own complete row, local cost and strict
moment contracts, tau<=p<1 and H<d give the bound

    O(V d^p H^(1-p) log(d+1)).

The logarithm covers the current compaction stage count. Its selected
width saving for K=d^c is

    (1-p) [1-c tau/(1-tau)] <= 1-tau,
    c tau < 1-tau.

This uses a different stopping proof and cannot silently replace the
original cutoff assumptions. Both ledgers expose the same inherited
direct-interface cap 1-tau=2^-50. This is a cap on savings certified by
these routing bounds, not on a multiplier that changes the supplier,
packing, assembly or cost model. No kappa is inferred from it.

The hypothetical eleven-gate Z3 word has an ideal child moment below one
at p=97/100, by 11^100<12^97. The frozen routing exponent is greater
than 97/100, so that attractive choice fails both routing interfaces.
Choosing p very near one can restore moment compatibility, but leaves
the tiny inherited routing slack. The twelve-gate baseline has no
sublinear child moment in either ledger. A shorter word and a stronger
routing supplier are distinct substantive requirements.

## Reproduction and scope

The [exact rational control](../../code/transfers/activity_native_tau_budget.py)
compares both stopping contracts, their slack bounds and the omitted-K
negative without importing any producer or using floating point. Improved
routing cases are explicit hypothetical interfaces, not found algorithms.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/activity_native_tau_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/activity_native_tau_budget.py --workers 4
```

These checks require only standard-library Python. The primary source
was obtained independently through `gh api` at the immutable revision;
its ignored source location and exact acquisition command are retained
in the run protocol. No external code was executed or modified. The
coordinator owns input-manifest and CI registration.
