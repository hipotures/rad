# Routing-aware stopping with complete rows and a decreasing depth budget

Status: **PROPOSED CONDITIONAL ANALYTICAL TRANSFER LEMMA**, supported by
**EXACT DECLARED-RECURRENCE CONTROLS**. No native Gaussian circuit, new
characteristic root or larger multiplication exponent is certified here.

The earlier sufficient transfer bounds every internal routing operation by
one power of its current selected width after substituting a worst-case
relation between the root's chunk width and the stopping threshold. That
can lose slack. Summing the actual current-width costs across the complete
recursive tree gives a sharper bound under the same routing interface. It
also admits same-width children when a separate depth/row budget decreases.

## Explicit interface and full moment

Fix a finite native profile with ambient width m, W physical role streams and
complete recursive call counts n_t for `0<t<=m`. A call acts on one role stream
of volume exactly `V/W`; all calls, complete payloads, wrappers, inverses and
copy/restoration operations must occur in this declared profile or in its
local overhead. A same-width call is allowed. Its volume charge is `n_m/W`.

Define the full normalized width moment

```text
Phi(z) = sum_t (n_t/W)*(t/m)^z.
```

Assume `0<tau<=sigma<1` and `Phi(sigma)<1`. In particular
`Phi(1)<1`. The root's long-chunk width K remains present in every call;
it does not shrink with a child's selected width. The complete paid local
overhead per current volume is at most

```text
A*((e*K)^tau+1),
```

with a uniform constant A. This includes binary nonlinear routing, affine
translations, scalar gates, full-field movement and copies, row splitting,
stack parking/return, descriptors and at most m-1 remaining selected
directions. Each native child has width `t*floor(e/m)`, keeping its complete
selected address cube, and remaining budget one smaller. The budget-zero
or bounded-width elementary leaf performs every selected C kernel at cost
at most `B*e` per complete current volume.

Exact all-field endpoint semantics are a separate required part of this
interface. A frame label, projective unit or sampled zero-scratch identity
does not establish them. The interface must specify and prove the actual
Gaussian word and fixed-tape algorithm; the following lemma cannot supply
an improved oracle at the same size.

## Stopping rule and weighted tree proof

Use the recursive state `(e,L)`. Stop when `e<=H` or `L=0`, with

```text
H = max(m, ceil(K^(tau/(1-tau)))).
```

At an internal node `e>H`,
`e^tau<=e^sigma*H^(tau-sigma)`. Let a node's volume weight be the product
of its `1/W` factors along its complete call path. At depth j, the sum of
its weighted sigma-powers is at most `Phi(sigma)^j*d^sigma`: floor rounding
can only decrease the positive power, and earlier stopping removes nodes.
Thus the entire internal routing cost is bounded by

```text
O(K^tau*d^sigma*H^(tau-sigma)/(1-Phi(sigma))).
```

The constant `+1` is absorbed because `(e*K)^tau>=1`. No routing call has
been removed; its volume and actual selected width enter this sum.

Replacing an internal node by its children never increases the total
weighted sigma-potential when `Phi(sigma)<=1`. Consequently the complete
stopped frontier has weighted sigma-potential at most `d^sigma`. Each
early leaf of width at most H costs at most its sigma-power times
`H^(1-sigma)`, so their combined cost is

```text
O(d^sigma*H^(1-sigma)).
```

Every remaining budget leaf occurs at depth L. Its elementary cost is its
actual width, and the first-width moment controls their total:

```text
O(d*Phi(1)^L).
```

These are disjoint leaf classes. The separate upper bounds can be added;
neither a large same-width budget leaf nor an early leaf is omitted.
For sufficiently large K, the two first terms balance, giving

```text
F(d,L) = O(d^sigma*K^(tau*(1-sigma)/(1-tau)) + d*Phi(1)^L).
```

If `K=Theta(d^c)` and
`u=c*tau/(1-tau)<1`, set

```text
r = sigma+u*(1-sigma) < 1,
L >= (1-r)*log(d)/(-log(Phi(1))).
```

The complete stopped cost is `O(d^r)`. Rounding H and L affects only
constants. Every invocation terminates by decreasing L, including an
aligned same-width child. This proof sums paid routing work; it does not
replace it by a free bit permutation or a nonlinear CRT relabeling.

## Complete row stock, tape stack and precision

The root must possess at least `W^L` complete preceding rows. Pad that one
preceding row range to the next multiple of `W^L`. If its original range is
at least `W^L`, this padding increases volume by less than a factor two.
Each native call splits rows by `u=W*g+w` and retains the same suffix cube
and all fields in each role. At depth j every stream has rows divisible by
`W^(L-j)`; every descendant has at least its own required `W^(L-j)` stock.
The added rows are genuine zero payloads. They may be deleted only after
the proved complete endpoint returns each original row independently and
returns every padded row to zero.

The preceding prefix has at most `L*log2(W)+O(1)=O(log(d))` required bits.
One conservative implementation borrows `ceil(log2(W))*L` complete chunks,
applies their selected kernels individually and then uses those chunks as
the row prefix. This costs `O(V*log(d))` and leaves the remaining selected
axes disjoint. Their final exact operators commute with that preprocessing.
If K is large, fewer complete chunks can supply the same range, but this
reduction is unnecessary for the stated time power. Reserving any routing
companion must still leave its full required chunk range; a collapsed,
nonbinary row index is not a free replacement for a complete companion.

At every node, park inactive role streams on a LIFO tape, copy the complete
active stream into the child area, and restore the parked streams at return.
No child operation may traverse an ancestor's parked payload. With the
declared fixed number of calls and roles, these operations cost O(V) per
node and are included in the local overhead. The call descriptor stack
has depth L. There are at most `s^L=d^O(1)` nodes for fixed total call count
s. The record formats and actual fixed-tape layout still need a native
implementation meeting this interface.

For precision, the [endpoint-aware guard](endpoint-aware-guards.md) applies
if every returned child is exactly its complete `C^tensor(width)` target,
every actual local arithmetic prefix/temporary is charged, and the total
serial child width per node is at most `q*e+q0` for fixed q,q0. It gives
internal grid and magnitude allowances `O(d*L)=O(d*log(d))`. The physical
global grid can remain fixed; exact child identities imply the trailing
zeros. The proof never invokes an uncharged normalization or fraction
reduction. Different native words can have the same endpoint and radically
different internal excursions, so the local-prefix hypothesis is essential.

In the original long-record parameter band, `d<=p^epsilon`, `epsilon<1`,
this guard fits `o(p)`. Its complete record length is superpolynomial in p
and its address descriptors have O(p) bits. The original paid routing bound
then absorbs polynomial per-record setup and guarded exceptional repairs
uniformly, provided the complete records and companion chunks survive each
row split. The relevant original interface is
[05-layers.tex at adc7f124](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex),
SHA-256 `20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`.
The [paid packed translation review](paid-packed-translations.md) separately
records the constant-control specialization and its full-payload conditions.
This lemma does not automatically verify those physical conditions for a
new circuit.

## Exact discriminators and comparison with the coarse bound

The [authored recurrence checker](../../code/transfers/routing_budget_transfer.py)
uses no producer or external library. Its declared local cost is
`ceil(sqrt(e*K))+(e mod4)`, explicitly retaining both the root routing chunk
and the leftover directions. For the tested roots `K>=4`, this is at most
`2*sqrt(e*K)` at every internal node. All powers and moment enclosures are
checked rationally; floating ratios are display values only.

Both profiles have `m=4`, `W=10`, `tau=1/2`,
`K=ceil(d^(1/4))` and `H=K`:

| Profile | Complete children | Sigma | Moment upper | Budget L | Improved power r | Coarse sufficient minimum |
| --- | --- | --- | --- | --- | --- | --- |
| Router dominates | `{1:4,2:1,4:6}` | 1/2 | 7/8 | ceil(log2(d)) | 5/8 | 3/4 |
| Primitive dominates | `{1:2,2:2,4:8}` | 3/4 | 99/100 | 3 ceil(log2(d)) | 13/16 | `(5+sqrt(3))/8` |

For the first profile, `Phi(1)=3/4`. The exact inequality
`(3/4)^8<1/8` bounds final budget leaves by `d^(5/8)`. The complete
recurrence satisfies

```text
F(d,L) <= 18*sqrt(d*K).
```

For the second profile, `Phi(1)=19/20` and `Phi(1/2)>1`, so summing the
routing moment alone would fail. Yet `Phi(3/4)<99/100`. The exact inequality
`(19/20)^16<1/2` supplies the three-times-logarithmic budget, and

```text
F(d,L) <= 202*d^(3/4)*K^(1/4).
```

The earlier conservative same-overhead rule needs a common power above
both `tau*(1+c/beta)` and `sigma+beta*(1-sigma)`. For the first profile,
their minimum is 3/4, achieved at beta=1/2. For the second it is
`(5+sqrt(3))/8`, about 0.841506. At the improved power 13/16 the old
inequalities would require both `beta>=2/5` and `beta<=1/4`, an exact
contradiction. The gain therefore comes from sharper accounting, not a
changed profile or an omitted routing charge. It is a comparison of these
sufficient rules, not a lower bound on all algorithms using that profile.

Four workers verify 80 complete stopped recurrences in 2.570 seconds. Root
widths run from `2^8` to `2^128`, with separate aligned and remainder
schedules. The dynamic program retains exact rational costs, every leaf
and the full row stock. Integer power comparisons establish each claimed
bound. The [compact result](../../runs/20261008T231946Z-transfer-routing-budget-guard-repair/results/summary.json)
retains every raw result field, with its original hash and recovery path.

Negative controls reject missing final row stock, a broken W-way boundary,
unit self-mass with additional positive children and width-only same-width
recursion. An unpaid K-free time claim already fails at the root: for
`d=2^64`, `K=2^16`, the paid router is `2^40`, exceeding the false bound
`18*2^32`. This is why the real routing chunk remains in the improved bound.

The recurrence profiles are explicit hypothetical arithmetic costs. No
Gaussian native motif with those counts is supplied. These computations
certify the stated recurrence inequalities and controls, not physical
execution or a multiplication exponent. The declared numeric guard field
in the receipt is a ledger illustration, not an implemented phase program.
Its serial-width coefficients are independently derived from the complete
profiles: 15/2 and 19/2, conservatively rounded to eight and ten.

The [initial attempt](../../runs/20261008T231214Z-transfer-routing-budget/report.md)
used an undercharged uniform coefficient eight for the second profile's
illustrative numeric guard. That field is invalid for the second profile;
the exact time and row comparisons remain valid. Its immutable result and
source correction patch are preserved. The fresh attempt above corrects
the illustration and adds an explicit undercharge negative; it does not
replace or overwrite the earlier output.

## Leverage and remaining bottlenecks

The lemma changes the original sufficient stopping analysis while retaining
its routing width cost. It can preserve more of a favorable complex moment
and supports genuine same-width calls without circular recursion. It is
therefore relevant to the new one-axis or nonmonotone native architectures.

It does not increase the full moment's characteristic root. Since
`r>=sigma`, the resulting primitive saving is below both the complex
characteristic saving and the available binary routing saving. Even in
the limit of negligible chunk growth, the frozen complex saving near
`7.1744622e-5` remains below the requested `1e-4`. A stronger primitive or
a genuinely different outer organization is still necessary. The PR37
balanced assembly uses a different paid ledger; its sufficient constraints
are not changed by this report without a fresh operation-by-operation bind.

Next: independently review the weighted frontier argument, then bind an
actual complete one-axis/cancellation native word to this time/row/depth
contract. Complete moments, scalar coefficients, paid affine/chunk routing,
precision and the outer CRT/Gaussian/FFT recovery must agree on the same
program before an end-to-end saving can be accepted. This is mathematical
work developed with OpenAI Codex, not external peer review or a formal proof.

## Reproduction

From the breakthrough worktree root:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/routing_budget_transfer.py \
  --workers 1 --small
```

This bounded source-only check tests thirty recurrences and all negative
controls. The full four-worker command, deterministic profile definitions,
integer width schedules, source hash and pre-execution Git head are in the
[protocol](../../runs/20261008T231946Z-transfer-routing-budget-guard-repair/protocol.json).
Use a fresh output path for every attempt.
