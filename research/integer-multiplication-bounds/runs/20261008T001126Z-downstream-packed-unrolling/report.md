# Exact packed-recurrence unrolling candidates

All three strict assembly rows and 163 scalar recurrence/balance identities passed. This changes the estimate of the same movement algorithm. It is a small relative gain; the complete transfer awaits independent review.

| Primitive | Kappa | Ratio to 2^-59, rounded down | Improvement over old bound |
|---|---|---|---|
| unchanged-h50 | 4394441151417/500000000000000000000000000000 | 5.066445704197 | 1.000000002964654 |
| envelope-h50 | 4803028936777/500000000000000000000000000000 | 5.537515348459 | 1.000000003099398 |
| verified-asymmetric-p52q48 | 2404771744437/250000000000000000000000000000 | 5.545026115664 | 1.000000003101437 |

See [derivation](../../reports/downstream-packed-unrolling.md), [certificate](results/certificate.json) and [protocol](protocol.json).
