# Low-selector channels and the paid original-source conversion boundary

The paired-five central and side maps use only the sixteen selector characters
of degree at most two in each thirty-two-bank source cube. This is an exact
algebraic compression. It does not provide a free conversion of the original
source banks to a shared current address frame.

The frozen generator is
[`paired_cube_low_channel_boundary.py`](../../code/complex/paired_cube_low_channel_boundary.py)
and its sole runtime import is the author's previously frozen paired-five scalar
discriminator. The full run
[`20261009T090340Z-complex-paired-low-channel-boundary`](../../runs/20261009T090340Z-complex-paired-low-channel-boundary/report.md)
checks all 672 target rows against all 21 source cubes at seven coordinate
pairs. Its 28,224 integer Walsh transforms contain 451,584 exactly zero
high-degree channels. The altered degree-three character is rejected. The
bounded CI check retains all thirty-two target rows of the first cube and all
source cubes; it is not the full 672-row discovery run.

For a source selector `u` and a target label `T`, the overlap `|S(u) intersect T|`
is an affine polynomial in the selected bits of `u`. Thus
`f5(t)=(t-1)(t-3)/8` has selector degree at most two. The central map `B` has
this property, and `H=B_cube-B` has it as well. Write `Pi_low` for the
orthogonal selector-character projector of degree at most two. Then
`B_cube=2 Pi_low` and `K=I-B_cube`. Consequently `B K=-B`; symmetry gives
`K B=-B`. Since `B_cube K=-B_cube`, both `H K=-H` and `K H=-H` follow.
The run directly checks the zero-character premise. The displayed four
matrix identities are analytical consequences, not independently replayed
full global matrix products. In particular `rank(H)<=v/2` is an algebraic
statement, not an implemented half-stock side word.

The projector identity extends to every odd `k=2r+1`. For Hamming distance
`d=k-t`, the normalized low-character sum is
`2^(1-k) sum_{a:wt(a)<=r} (-1)^(a dot z)`. The standard finite binomial
coefficient identity
`sum_{j=0}^r Kraw_j(d;k)=Kraw_r(d-1;k-1)` follows directly by multiplying
the generating polynomial by `1/(1+x)`. At positive even `d`, complementing
the `r`-subsets of `2r` positions negates every summand because `d-1` is odd.
The sum therefore vanishes. As a polynomial in `t` it has degree at most `r`,
has the roots `1,3,...,k-2`, and is one at `t=k`; hence it equals
`binom((t-1)/2,r)`. This also proves the parity-exchanging involution used by
the paired-cube bank mixer. This derivation concerns scalar selector labels;
it does not equate the bank mixer with one Clifford address primitive.

The first geometric discriminator rejects a named implementation. A whole
five-cube label span has rank six; a single parity class has rank five.
An original norm-one source line is contained in both. Bringing every source
to the whole-cube frame and then back to its original parity frame costs
`5+1`, whereas the direct line-to-parity entrance costs four. Under the
unchanged physical stock this adds two ranks per source per completed core.
Across the retained three-core architecture the deficit changes from
`2v-3*copied_loss` to `-4v-3*copied_loss`. This excludes that explicit
line-to-whole-cube-to-parity excursion even before extra scalar and routing
costs. It is not a lower bound on arbitrary encoded sources, shared frame
chronologies, kernel parking, or delayed dirty births.

An exact cancellation control makes the distinction concrete. The total
selector sum and the first-bit contrast average to a selector face. Its true
source span has rank five, but both inputs were evaluated at the rank-six
whole-cube frame. Moving the resulting role to the smaller actual frame still
requires a rank-one transition. Scalar support cancellation alone does not
make that frame change free. Every whole-cube frame also contains its own
original target label, so it is outside that target's orthogonal cap.

This result motivated the coordinator's separate cap-aware actual-row bases.
Those bases keep the literal source support inside one target-parity cap and
avoid the rejected whole-cube excursion. Their scalar channel counts still
require paid reversible completion, kernel parking, decoder fanout, and an
actual shared chronological word. No attained native recurrence or exponent
is claimed here.

Reproduce the complete or bounded run from the repository root:

```bash
python3 -B research/integer-mult-breakthrough/code/complex/paired_cube_low_channel_boundary.py --workers 4
python3 -B research/integer-mult-breakthrough/code/complex/paired_cube_low_channel_boundary.py --workers 1 --bounded
```

The generator uses only the Python standard library and exact integers; there
are no random inputs or external packages. Optional `--output` creates a new
certificate file exclusively. The config and milestone manifest pin both
source files and immutable full/bounded run receipts. Raw source snapshots and
logs remain separate from the compact tracked results, with their exact
hashes and regeneration commands recorded in each persistence receipt.
