# Prime supply for the long-digit chooser

Checked 2026-10-08 14:23 UTC. Primary source: R. C. Baker, G. Harman and
J. Pintz, *The Difference Between Consecutive Primes, II*, Proceedings of
the London Mathematical Society (3), 83(3), November 2001, pages 532–562,
[DOI 10.1112/plms/83.3.532](https://doi.org/10.1112/plms/83.3.532).
Theorem 1 on original page 532 supplies a prime between `x-x^(21/40)`
and `x` for every sufficiently large `x`. The threshold is effective in
principle; this paper gives no numerical value. The publisher's 2016 online
hosting date is distinct from the 2001 journal issue. The
[original paper](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/BakerHarmanPintz.pdf)
is pinned as a downloaded input in [prime-gap-source.json](prime-gap-source.json).

## Enough distinct nearby primes

Write `eta=c_theta*d^-16`. For each binary axis capacity `t`, the required
prime interval for `eta<=t/s-1<=2eta` is

`I_t=[t/(1+2eta),t/(1+eta)]`.

Its width is `W=eta*t/((1+eta)(1+2eta))>=eta*t/4` eventually.
Choose `H=ceil(2*t^(21/40))`. Once `W>2*d*H+2`, place `d` disjoint
subintervals of length `H`, separated by gaps of length `H`, inside `I_t`.
Each upper endpoint is at most `t`; its Baker–Harman–Pintz prime window has
length at most `t^(21/40)<H`. The primary theorem thus gives a distinct prime
in every subinterval. Endpoints may be rounded to integers with the displayed
two-unit slack. All these primes are odd eventually.

The sufficient growth condition is

`eta*t^(19/40)/d -> infinity`.

For the campaign chooser, `log2(t)>=ell=Theta(b^(1-epsilon))` and
`d=Theta(b^epsilon)`, so

`log2(eta*t^(19/40)/d)=(19/40)*ell-17*log2(d)+log2(c_theta) -> infinity`

for every fixed `epsilon<1`. This works also when `epsilon>1/2`; it does not
use the older insufficient comparison of `log(t)` with `1/eta`.
If several axes have the same capacity, select distinct primes from the common
interval. For other capacities, either their intervals are disjoint or choose
one of the available `d` primes not previously used. Thus pairwise coprimality
is explicit rather than inferred from independent single-prime existence.

## Construction and cutoff

Enumerate candidates in `I_t`, test primality by deterministic trial division,
and retain previously unused primes. Even the crude charge
`poly(d,log t)*t^(3/2)` is `2^O(ell)=n^o(1)` for the actual maximum axis
capacity, whose binary width is below `2ell`. This is charged setup on fixed
tapes and does not require a prime advice table. If a finite input fails to
supply enough primes, use the conventional base algorithm; eventually the
theorem guarantees that this branch is unnecessary.

This establishes an eventual constructive prime supply. It does not provide
an explicit numerical `x0` or a numerical full-machine input threshold. No
claim about a practical cutoff follows from the asymptotic argument.
