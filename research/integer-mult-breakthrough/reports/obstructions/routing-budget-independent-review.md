# Independent review of the routing-aware stopped recurrence

Status: **ACCEPTED CONDITIONAL ANALYTICAL BOUND AND BOUNDED EXACT REPLAY**.
Acceptance covers the stated cost interface, not an implemented native circuit
or multiplication exponent. No additional formal verification is claimed.

The coordinator reviewed [the transfer statement](../transfers/routing-aware-depth-transfer.md)
and independently reconstructed its three cost terms. Every child carries its
complete volume factor 1/W and width at most (t/m)e, while the root chunk width
K remains fixed. Thus weighted sigma-potential at depth j is at most
Phi(sigma)^j d^sigma. For e>H and tau<=sigma, actual overhead K^tau e^tau is
at most K^tau H^(tau-sigma)e^sigma. Summing depths gives the claimed internal
geometric-series bound when Phi(sigma)<1. Same-width children terminate through
the separate decreasing budget L; width-only induction would be circular.

At a stopped frontier, sigma-potential does not increase on replacing a parent
by its children. Width-stopped leaves therefore cost at most
d^sigma H^(1-sigma). Remaining budget leaves are all at depth L, and their
first-width potential gives d Phi(1)^L. These leaf classes are disjoint;
bounding them separately does not drop either class. Taking
H=Theta(K^(tau/(1-tau))) balances the routing and early-leaf terms. The result
has exponent `r=sigma+[c tau/(1-tau)](1-sigma)` when `K=Theta(d^c)`.

The numerical examples compare two sufficient analyses under the same declared
cost ledger. With tau=sigma=1/2 and c=1/4, r=5/8. The coarse common-power rule
balances 1/2+1/(8 beta) and 1/2+beta/2 at beta=1/2, yielding 3/4.
For sigma=3/4, the improved r=13/16. A coarse bound at that power would require
both beta>=2/5 and beta<=1/4, which is impossible. Its balanced value is
(5+sqrt(3))/8. These are improvements to sufficient bounds, not algorithmic
lower bounds or measured hardware speedups.

The coordinator independently ran the source-only bounded replay after the
guard correction: thirty complete rational recurrences and all negative
controls passed. The test includes row divisibility, decreasing same-width
budget, complete moment mass and the fixed K charge. The complete profiles
have serial width sums 15e/2 and 19e/2, so conservative precision coefficients
eight and ten are appropriate. The first attempt's coefficient eight for both
profiles is invalid; its preserved failure and correction do not change the
time comparisons.

The row stock W^L, preceding-prefix preprocessing, tape parking, exact all-field
child endpoints, complete routing companion ranges and uniform local-prefix
guards remain physical interface obligations. A mathematical recurrence with
that declared overhead is not an implementation satisfying them. This review
accepts no new Gaussian word, no native child histogram, no altered PR37 ledger
and no outer CRT/Gaussian recovery. Even perfect stopping cannot raise the
frozen complex characteristic saving above its own root, which remains below
1e-4. A structural primitive change or different outer mechanism is still needed.

Reproduce the independently exercised scope from the worktree root:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/routing_budget_transfer.py --workers 1 --small
```

The original corrected run pins its exact source and complete eighty-case
four-worker evidence. This review is internal team mathematical criticism,
not external peer review. A fresh native integration must receive its own
protocol and operation-by-operation ledger.
