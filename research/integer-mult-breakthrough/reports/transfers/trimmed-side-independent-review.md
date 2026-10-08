# Independent scalar review of the truncated side transform

Status: **EXACT SCALAR CERTIFICATE** in a zero-initialized subset model,
with scoped frame counterexamples. A dirty reversible schedule, producer
operation counts, and native child profile are not certified here.

For odd label weight k, put
`f_k(t)=binom((t-1)/2,(k-1)/2)`. The proposed side map has entries
`g(S,T)=[S=T]-f_k(|S intersect T|)`. It vanishes at every odd intersection,
including the diagonal. For k five, the independently derived Newton
coefficients of g are

```text
(-3/8, 3/8, -1/4, 0, 0, 1).
```

Downward subset sums produce
`a_E=sum_(S containing E) x_S`. Multiplying each rank-r feature by its
Newton coefficient and applying upward subset sums gives
`sum_r c_r*binom(|S intersect T|,r)` in each matrix entry. The binomial Newton
identity gives exactly the proposed g. In particular, the degree-five term
is the input identity x_T, not a zero coefficient. Dropping it produces
diagonal minus one, which violates the intended cancellation.

The independent source uses complete bounded subset Yates passes rather than
the producer's trimmed DAG, imports none of the producer, and checks every
source column. Four workers verify 95,440 output entries at `(h,k)` equal to
`(8,5),(10,5),(10,3),(10,7)`. All odd-incidence zeros and the missing-identity
negative pass. Runtime was 0.621 seconds. This accepts the scalar identity;
it does not independently accept the reported trimmed SSA operation counts.

The low-degree incidence features contain nonorthogonal contributions that
cancel only in the complete output. For any feature E contained in an
odd-weight label S, that label belongs to both its input support and the
direct incidence output support. Its self-pairing is one. A nested common
nondegenerate frame `U<=F<=Mperp` is therefore impossible for that individual
feature: U is not orthogonal to M. The same witness applies to the top-degree
identity feature E=S. The source preserves explicit empty, point, pair and
top-feature examples at each tested dimension.

This blocks a naive independent monotone scatter of these features. It does
not block paid copied-center common-background reads, jointly realized
cancellation, dynamic frames, or the broader noncommuting Lagrangian family.
Every down/up addition, erased intermediate, identity path, phase transition,
helper return and uncompute must be bound to an actual dirty schedule before
scalar counts become physical child counts.

Full-width transitions can be addressed by the [row/depth budget mechanism](same-width-row-budget.md)
only if the complete moment contracts after those operations are included.
Their contribution is the actual volume mass `n_m/W`; an omitted same-width
identity path cannot be called zero cost. A separate endpoint-aware guard
proposal is being developed for exact complete children. No such native
program is assumed by this scalar certificate.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/trimmed_side_review.py \
  --workers 1 --small
```

The CI closure is the [self-contained source](../../code/transfers/trimmed_side_review.py)
only. The bounded path checks all 3,136 entries at h eight, k five plus the
negative and frame witnesses. The [run protocol](../../runs/20261008T223515Z-transfer-trimmed-side-review/protocol.json)
pins the source, cases, command and UTC interval; its results retain all
compact outcomes. There are no external execution dependencies.

The candidate truncated side transform was supplied by the coordinator at
`code/obstructions/trimmed_side_transform.py`. The mathematical Newton identity
is independent of its SSA implementation. This complete-column verifier,
scoped review and deduction were authored with OpenAI Codex; no formal
verification, external novelty or exponent claim is made.
