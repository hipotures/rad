# Exact phase-cell inverse run

All 5 cases passed exact phase conjugation, every local Gohberg–Semencul column identity, Schur diagonal dominance/bandwidth, rounded cyclic solves, and the independent infinite-Gaussian residual enclosure. Signed real/imaginary probes are covered.

| s/t | u | Cell lengths | Interior lengths | Work bits | Target bits |
|---|---|---|---|---|---|
| 15/16 | 4 | [8, 7] | [4, 3] | 256 | 16 |
| 31/32 | 4 | [16, 15] | [12, 11] | 512 | 20 |
| 63/64 | 4 | [32, 31] | [28, 27] | 768 | 24 |
| 63/66 | 4 | [11, 21, 21, 10] | [7, 17, 17, 6] | 384 | 24 |
| 64/67 | 4 | [11, 21, 22, 10] | [7, 17, 18, 6] | 384 | 24 |

Elapsed: 420.164482 seconds, one CPU worker. Full-run observed resident memory remained below 32 MiB. The certificate contains exact rational intervals and residual bounds. These are finite prototypes; the new asymptotic precision/tape transfer remains pending independent review.

See [full derivation](../../reports/downstream-phase-cell-inverse.md) and [protocol](protocol.json).
