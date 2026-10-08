# Independent review: full rotated middle runs

The accepted h51 clone network with 500,703 auxiliary roles supports the
explicit primitive saving
`a=757098445646893/62500000000000000000000`, approximately
`1.21135751303503e-8`, after removing the artificial h² cap on its rotated
middle-bank pivot runs. This is a strict characteristic improvement, with
a complete all-size primitive transfer subject to the retained fixed
finite-table setup. A new complete multiplication composition must still
check the other margins and the quantitative row divisor below.

The independent executable [review_uncapped_middle.py](../code/review_uncapped_middle.py)
uses rational elimination and the independent 64-term logarithm intervals;
it imports no producer characteristic. The terminal
[run](../runs/20261008T0533Z-review-uncapped-middle/protocol.json)
checks all four supplied old/new two-family and tensor-data witnesses.
Its [certificate](../runs/20261008T0533Z-review-uncapped-middle/results/certificate.json)
also joins the completed changed-clone finite audit to the separate
all-size clone proof. The stronger primitive saving above is not itself
a final integer-multiplication kappa.

## Exact physical grouping

Keep the previously reviewed fixed basis cycle `(3,1,2)`, every rational
frame, and every lower/lower factor table. For a triple t with least
coordinate a, the canonical partial permutation of `I-P_t` has diagonal
runs of lengths a and `h-a-2`, one off-diagonal pivot, and one zero row.
The middle residual is `(I-P_t) tensor I_(h²)`. Tensoring the existing
lower/lower factors with the identity gives its canonical partial
permutation. Its increasing source/target runs consequently have lengths

`a h²`, `(h-a-2)h²`, and `h²`, omitting the zero-length prefix.

The final h² run includes the off-diagonal base pivot. Both source and
target coordinates increase consecutively within that run, so the
segmented componentwise arithmetic and one width-rb interchange apply.
No pivot permutation or gather is inserted. Only the splitting of an
existing consecutive run changes. The maximum run is
`r_max=h²(h-2)=127449<m=132651`, attained when a=0. Six complete rational
middle matrices at h6/h8 reproduce these actual uncapped lengths, ranks
and off-diagonal blocks; the previous cap is explicitly distinguished.

The exact number of triple labels of minimum a is `C(h-a-1,2)`. There
are `(R+h)v` copies per triple label, where `v=C(h,3)`. The independent
histogram therefore conserves the entire middle rank

`T=(R+h)v² h²(h-1)`.

Relative to the capped moment `T ln(h²)`, the added moment is

`(R+h)v h² sum_a C(h-a-1,2) [a ln a+(h-a-2)ln(h-a-2)]`.

Terms of length zero are omitted. This is precisely the old fixed-axis
middle first moment; it is positive. Joined and exact tensor-data
profiles remain unchanged and disjoint from the middle family. All
remaining rank-one calls are retained individually. Role count, total
rank and the completed scalar/dirty maps remain unchanged.

## Integer widths, recurrence and row stock

For an arbitrary integer e, retain the already reviewed decomposition
`e=m floor(e/m)+t`, `0<=t<m`. Constant-size tails use the same exact
short-field crossing schedule. A grouped child has integer width
`r floor(e/m)`, and its role volume is V/W. The fixed triangular factors
still cost O(V); the completed main/tail identity restores the row bitmap
and arbitrary scratch. This construction retains the fixed number of
tapes and does not inflate volume by a run length.

Every nonbase child obeys

`r floor(e/m) <= (1-2/h)e < e`.

The normalized recurrence is
`F(e)<=sum_r (n_r/W)F(r floor(e/m))+C`. Thus the same power induction
applies whenever `sum_r n_r r^(1-a)<W m^(1-a)`. The depth has changed:

`D<=ceil(log_(h/(h-2)) e)<=ceil((h/2)ln e)<=26 ceil(log2 e)` at h51.

The h-fold shrink and the old `p^100` row estimate are not carried over.
Complete row divisibility by `W^D` is sufficient. Since W<2^49 and the
retained routing invocations have `e<=C*p` for a fixed setup constant C,
for `p>=C` and `log2(p)>=25` we obtain

`log2(W^D)<49*26*(2 log2(p)+1)<2600 log2(p)`.

An untouched suffix reservoir of width
`ell>=p^(1-epsilon)/2` therefore supplies the divisor once
`p^(1-epsilon)>5200 log2(p)`. In terms of p=6b, the conservative sufficient
condition is

`b^(1-epsilon)>10400(log2(b)+8)`.

Padding the complete row stock to a multiple of the divisor costs at
most a factor two. This is a new compressed-power cutoff obligation for
the final composer; it is asymptotically satisfied for every fixed
epsilon<1. Fixed C and finite-table prime/setup thresholds remain
separate eventual conditions. They have not been silently replaced by
a numerical bound on C.

## Exact characteristic evidence

The independent audit reconstructs the whole integer middle histogram,
the joined Jensen moment, and the exact data histogram. All logarithm
lower intervals are safely floored to a common `2^-256` grid before
thousands of terms are added. Let M be the resulting lower first moment,
`s=Wm-D`, `D=N-2L`, and let `L_m` enclose ln m from above. For each supplied
positive a it verifies the stronger normalized sufficient inequality

`D-a(s L_m-M)-a² s L_m²/[2(1-a L_m)]>0`, with `a L_m<1`.

This follows by bounding the normalized positive exponentials in the
full rank characteristic. It independently accepts:

| Bit side roles | Variant | Explicit accepted a |
| ---: | --- | --- |
| 502265 | Two families | `1105165109799833/10^23` |
| 502265 | Exact tensor data | `12078089355696927/10^24` |
| 500703 | Two families | `11081354331641529/10^24` |
| 500703 | Exact tensor data | `757098445646893/(625*10^20)` |

The changed 500703 input is pinned to the full independent clone
certificate SHA256
`42957dbe7471fa007bc0ab889e1f588b82267e8012ec47cd84883828c5e0662c`.
The previous capped characteristic is strictly weaker in every row.
The producer's first schema-only failure is retained separately as run
052722 and source `downstream_uncapped_middle_characteristic_v1.py`;
the executed repaired producer is run052835.

## Scope and reproduction

The [global-axis review](review-global-axis-batching.md) supplies the
simultaneous frame/table conjugation and fixed odd-prime setup. Uncapping
changes no table entries and needs no additional bad-prime exclusions
beyond that accepted basis. The separate h28 complex scalar network and
its numerical guard remain unchanged. The changed 500703 input's whole
identity/dirty interface is established by the
[clone promotion followup](review-clone-promotion-followup.md).

The run used Python3.14.7, one CPU worker, a 16GiB address-space limit,
one thread per numerical library and a 120s timeout. Its exact command
and source/input hashes are in the protocol. It finished in 3.78s with
26360KiB peak RSS and zero swaps, releasing its owned reservation. The
prototype checks six full matrices, not the giant h51 factor table; the
all-size tensor-profile argument above supplies that boundary. The
complete multiplication headline remains conditional on retained
upstream dependencies and awaits its fresh composition certificate.
