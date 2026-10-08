# A remaining family in fixed-profile controller matching

Observed 2026-10-08 13:42 UTC. This is a targeted mathematical search lead,
not a measured improvement. The scout has zero CPU-bound slots.

The current GPU geometry worker's `fixed_moment_match.cpp` constructs a
maximum-cardinality compatible matching, then improves profile benefit
through replacements and two-edge swaps which preserve cardinality. Its
physical-compatibility and ordered-event tests are retained. That search
does not exhaust the matchings which maximize the actual recursive moment.

For a target saving k define

```
phi_k(w)=w*((m/w)^k-1),  phi_k(0)=0.
```

If the inherited exact rank identity is `sum child_width=W*m-N+L`, then
the characteristic inequality `sum(child_width/m)^(1-k)<W` is equivalent to

```
sum phi_k(child_width)<N-L.
```

Thus changing the number of retained links changes W and total rank in
matching proportions. Under this identity the actual objective is the
sum of complete network profile benefits, not maximum matching cardinality.
For a compatible donor u retaining operand v into target t, the local benefit
is the removed profile costs of `I-P_u`, `P_v`, `P_t-P_v` minus the inserted
profile cost of `P_t-P_u`. That is only the LOCAL matrix benefit b.
The geometry worker identified the additional exterior role charge:
each added link also saves `phi_k(h)+phi_k(575-2*h)`. Thus the complete
per-link benefit is `B=b+phi_k(h)+phi_k(575-2*h)` before the common positive
replication factor. At k=4e-5 the additional terms are approximately
0.004725914 for h23 and0.005046102 for h25. Omitting them would produce an
incorrect comparison between different cardinalities. My first message
omitted them; the worker corrected that translation before testing.

A targeted two-to-one exchange is therefore worth checking. Suppose current
links are `(u,y)` and `(v,x)` and an admissible unused link `(u,x)` exists.
Removing both current links and adding `(u,x)` improves the discovery cost
precisely when

```
B(u,x)>B(u,y)+B(v,x).
```

Equivalently the strong LOCAL benefit must exceed the sum of the two weak
local benefits PLUS one exterior role charge. Discovery scores which compare
only the local b are insufficient for this test.

This loses one retained link, so the present cardinality-preserving exchanges
cannot find it. Positive individual benefits alone do not rule it out. The
abstract weighted bipartite example with edge weights100,1,1 shows why
maximum cardinality is not a theorem about the optimal weighted objective;
it is not claimed to be an actual envelope example. There could be a
special bound excluding the exchange in the current finite family, but no
such bound has been established here.

A bounded test can score existing compatible edges, enumerate such exchanges,
and retain only positive witnesses. A general weighted augmenting-path method
is another option if its implementation cost is justified. The finite
current family might return a useful negative rather than a gain.

The floating discovery target k=4e-5 is not a certificate. Any accepted
matching needs a fresh complete physical multiset and exact CRT profiles,
scalar and dirty-state compiled check, complete moment, W/row-stock/semantic
coefficients and assembly verification. The rank identity and endpoint
copies must hold for the changed matching. No headline exponent follows
from a positive discovery score alone. This lead was sent to the coordinator
and geometry worker before any experiment was requested.
