# Odd h51 finite primitive with the reviewed semantic and bulk estimates

The independently checked odd-ground bit circuit yields a stronger strict
composition without changing the resampling algorithm or its estimates.
The strongest producer row is

\[
\kappa=\frac{31879574566994548341758160620003}{10^{40}}.
\]

This is an exact arithmetic result using an accepted finite input; a
separate assembly review is pending at the time this report was written.
The theorem remains conditional on the retained multiplication and chunk
interfaces and the campaign's reviewed analytic transfers. It is not an
unconditional multiplication bound, a novelty claim, or a practical input
size claim.

## Finite input and exact counts

The bit candidate is
`19945bccf2127679a684a457425017aade6746e66e51d0955fa7d1ff67cadf0d`,
with h=51, base=2, physical roles R=502265, and compiled identity
`5183963ce3e380f2017eeb51a9f83b7ee406ec8537b9053897464e63bd5e18e9`.
Its position vector is six zeros, twenty-five entries 24, and twenty
zeros. The independent finite input is the immutable
[root certificate](../runs/20261008T041200Z-review-odd51/results/certificate.json),
SHA256 `a1ee766e8705772432874250ce9e0398ce928fcb092569513f833f3e647518fa`.

The adapter checks this certificate's actual schema, including both
directions of the complete h7/h11 invocation basis and the two h7 complete
three-stage exchanges. It records 7,002 dirty invocation basis probes and
two exchange controls; it does not substitute the h50 review's four
exchange controls. The explicit odd-ground stage bijection, its inverse,
intersection-one property, nondegenerate rational form, and image hash
are all matched to the producer input.

| Quantity | Exact value |
| --- | ---: |
| v | 20825 |
| m | 132651 |
| N | 9031399015625 |
| W | 453752231686250 |
| L | 3384009916875 |
| D=Wm-s | 2263379181875 |
| s | 60190685022033566875 |
| eta | 307/8164138446 |

The bit central count is **h**, hence L=3v²h². This matters: using the
complex h(h+1) center count for this bit circuit would be incorrect.
The role formula is W=2N+2v²(R+h), with no added identity padding.

The complex input stays the previously accepted h28 R97586 construction:
its center count is 29 and its loss is 3v_complex²·28·29. The newer
controller-reuse complex input is not used in this run.

## Composition and validation

The fresh [adapter](../code/downstream_odd_semantic_bulk_composition.py)
has executed SHA256
`06e9002c963bd3ed06ed5ee00c43371b9a68ed9d44e541f20a27fd826afd969e`.
It imports the frozen semantic/bulk witness generator, checks every
recorded dependency hash, and exactly regenerates all four accepted h50
R472879 rows before substituting the odd finite input. The old parameters,
recurrence, margins, strict slacks, and cutoff certificate are unchanged
in that regression.

It generates four rows, each with positive rational strict slacks (40 for
the original prefix, 41 for the balanced prefix), exact logarithm
enclosures, and compressed bit-length cutoff checks. The compact
conservative balanced witness is
`6375896671771656659629283259679/(2*10^39)`, with common numeric
log2(input b) cutoff 1096386001358401. The tight original-prefix witness is
`15939787232681910604248015281721/(5*10^39)`, with cutoff
6297308145207339265. The tight balanced row stated above has cutoff
258254417031933722624.

These are numeric cutoffs for the listed local inequalities. Additional
eventual thresholds for prime existence, setup absorption, fixed-tape
constant factors and polylogarithmic absorption remain as declared in the
reviewed semantic/bulk proof; the common numeric cutoff alone is not a
complete explicit multiplication threshold.

The transfer chain is the reviewed compact layout and balanced transform,
exact semantic child reset with C1=1 and C0=32m(s+E)², arbitrary routing,
and the bulk phase-cell local inverse with the global downward-rounded
matrix held fixed. It replaces no finite or analytic proof with decimal
rounding. The stronger finite bit saving is a changed circuit input; the
thin adapter itself is exact parameter composition.

## Reproduction and provenance

The run is
[20261008T042624Z-downstream-odd51-semantic-bulk](../runs/20261008T042624Z-downstream-odd51-semantic-bulk/protocol.json).
Its protocol preserves the full command, all input hashes and sizes, one
worker admission record, immutable reference identities, and the external
stdout location. Its compact
[certificate](../runs/20261008T042624Z-downstream-odd51-semantic-bulk/results/certificate.json)
preserves the exact rationals and all strict slacks. Reproduce its command
from the protocol with a **fresh** `--output` path; overwriting a result is
rejected. No finite graph was replayed.

The original upstream is `CrocSwap/integer-mult-bounds` commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; the compact-control upstream is
commit `6e564879f51ae16f23d392e9e196c605f36d90df`. The campaign started
2026-10-07 22:25:21 UTC. Its original deadline was 2026-10-08 08:25:21 UTC;
the user's authorized extension is 2026-10-08 10:00:00 UTC. No clock or
historical run was reset.
