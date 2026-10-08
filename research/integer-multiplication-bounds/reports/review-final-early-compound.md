# Independent acceptance of the final direct-first-allocation h53 circuit

The final nominated h53 circuit with 529,181 physical side roles is accepted. This is a new feasible circuit and allocation, not an optimality claim. The independent replay starts with the original graph, applies the newly selected first capacity allocation, and then applies the two subsequent nonempty rounds to their actual changed graphs and inherited frames. It does not replay the older allocation parent's clone jobs. The previous 531,483-role acceptance remains unchanged.

The executed reviewer is [review_early_compound_bit_witness.py](../code/review_early_compound_bit_witness.py), SHA256 `57416fba051128717036292466e2cc6e2c50d481c4cc4f51c961cc214f1546ed`. It uses the frozen independent reconstruction and checks in [review_compound_bit_witness.py](../code/review_compound_bit_witness.py), SHA256 `f7d1d0b922dab0c600cfb743eede2f49f0617bd2ae0e7f9b2bb72ba403a255e4`. No producer allocator, selector, cloner, or aggregate rank function is imported. The all-size induction is the one proved in [review-compound-bit-closure.md](review-compound-bit-closure.md), now applied to a changed first allocation directly from the original graph.

## Immutable inputs and exact circuit identity

The selected completed-cohort case is `439f31afa89e659a2bacb35a7d1474ba67e0410369a5d9cca22dcee4359ff741`, file SHA256 `ca6ce8791888f67474b522a955bbd5465b73b94ee117b8b9a3709a97ff2a767e`. Its policy is `wide-owner`, base 2, seed 104729, at most eight providers and four rounds. The complete v3 reconstruction artifact is external `derived/finite/20261008T091300Z-finite-early-export53/artifact.json`, SHA256 `ba8b4312f2975821d78860797f043519ad43199c704451e12389dacb03ebde98`. These external paths are under campaign root `/srv/ai/work/rad/integer-multiplication-bounds/20261007T222521Z`; the run protocol records full paths and hashes.

The export explicitly identifies `first_batch_from_original=true`. Its parent case supplies the original point ordering and graph identity only. The first, second, and third nonempty batches contain 22,898, 14,837, and 47 clones. The final logical digest is `8bf6098cb667c9be7a13c9c7359ae26e723b56125b2c00d0fff3b3bd8ec7cb04`; the final compiled digest is `c7eed569818909583b4df314dd0e05d809c2254905cebf6f6d405a3296f80484`.

## All-size transfer and what was independently checked

Every round is reconstructed from the actual preceding operands, frame assignments, selected links, and capacities. Earlier enlarged frames are retained literally. A moved controller chain is moved in its entirety; the clone receives its first consumer's frame, which contains its source span and is nested in every later consumer's frame. The two new clone-input retentions use distinct unused gate capacities, and every addition retains a terminating input pivot. The formal child conflict restriction is checked against the current graph, including children introduced by previous rounds. Direct target chains receive only frames whose target orthogonality is valid.

This preserves every scalar gate value by induction. Nondegeneracy and forward nesting yield the reverse complement nesting in the unchanged rational ambient form. Input lines, exact source containment, actual output frames, and all designated target orthogonality are independently checked. Source compatibility is a rational address-frame statement; payload additions remain the original bit-scalar interface. No characteristic-two reduction of the rational frames is used.

Each clone adds one addition and two selected links, so the role count drops by one while `additions + roles` stays fixed. The final values are 571,942 additions, 70,278 designated outputs, 113,039 links, and 529,181 side roles. Reversing all actual rounds recovers the original byte identities and baseline feasible plan. The preserved intermediate role counts are 566,963, 544,065, 529,228, and 529,181.

The complete current h53 graph passed all 86,090,550 output coefficients, 595,368 logical frame checks, 3,346,130 physical frame transitions, all physical scalar additions and targets, and all 23,426 triples in the explicit odd-ground matching. Only the final changed graph receives this complete physical replay. Earlier states are checked through reconstruction identities and the edit proof, rather than another baseline physical replay.

The independent rank timeline scans 21,697,366 actual side events and derives the whole aggregate histogram without importing the producer's rank aggregation. Its rank sum is the exact `s` below. The three disjoint boundary families used by the generic metric basis construction remain unchanged: middle and joined families each occur `(R+h)v^2` times, with kernel dimensions `h^2` and `2h`; the data family occurs `2N` times with kernel dimension `h^2+h-1`. Changed internal side events use the new actual histogram. The constructive finite-family rational isometry theorem applies to the enlarged actual frames. A giant h53 isometry or address table has not been instantiated; the theorem supplies finite computable setup and permits excluding finitely many additional prime denominators.

## Counts, guard, and local negative controls

The exact primitive counts are:

| Quantity | Value |
|---|---:|
| h, v, m | 53, 23,426, 148,877 |
| N | 12,855,661,152,776 |
| W | 606,574,719,772,320 |
| L | 4,624,547,790,252 |
| D = N - 2L | 3,606,565,572,272 |
| s = Wm - D | 90,305,020,948,978,112,368 |

The literal grouped scalar gate count is `G=7868329743799824`. The retained guard `E=14283442573798833498435753557856972000666521088` exceeds the independently counted depth `5790034614712740718608827185772974904391333956`; the exact slack is `8493407959086092779826926372083997096275187132`.

A fresh h12 `late-parent` direct-first-allocation control has three nonempty batches, final R=3,576, and a genuine multi-use moved chain. All 23,760 coefficients, 4,011 logical frames, and 22,316 physical transitions passed, including 3,317 dense rational constraint checks. Its complete side-invocation basis has 4,016 coordinates; adding the twelve central registers gives 4,028 complete dirty invocation basis vectors in each orientation. Both exact maps restore arbitrary dirty auxiliaries. Removing a required clone-input retention and moving only a proper subset of a recovered whole chain are independently rejected.

The current run does not repeat the previous full h8 shared-bank exchange. That boundary is supplied by the frozen 0843 independent complete h8 invocation and whole-exchange control, together with the unchanged matching and all-size stage joining proof. The two protected central variants are separate address tables and proof inputs, as recorded in [review-protected-center.md](review-protected-center.md) and [review-two-disjoint-centers.md](review-two-disjoint-centers.md). This finite acceptance alone does not promote a new composed multiplication exponent.

## Executed evidence and recovery

The completed run is [20261008T0916Z-review-final-early-compound53](../runs/20261008T0916Z-review-final-early-compound53/protocol.json). Its durable [certificate](../runs/20261008T0916Z-review-final-early-compound53/results/certificate.json) has SHA256 `c957b06e16a781c11bc2a454b6c323a666e8ec2d47a17af7fe89089f3518939e` and status `PASS INDEPENDENT CLOSING DIRECT-FIRST-ALLOCATION COMPOUND`. The protocol gives the exact reproduction command, all dependency hashes, immutable reference commit `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, and external full log and export locations. The v3 export is deterministically regenerable from its recorded source and case; it is not claimed to be a small Git payload.

Execution used Python 3.14.7 and one owned CPU slot with a 16 GiB address-space limit. GNU time measured 202.65 seconds, 5,146,096 KiB peak RSS, and zero swap. The slot was released automatically. This final reviewer had no failed scientific attempt. Earlier independent two-center failures and admission-only repair are retained in their own 0854, 0857, and 0859 run identities; earlier finite cohort failures are not replaced by this success. The active deadline is 10:00 UTC on 2026-10-08; the original 08:25:21 UTC deadline remains historical provenance.

The remaining final step is the independently reviewed twelve-row composition with the exact current histogram, generic characteristic, ground-specific 73000 product row-stock bound, and separately identified zero/one/two protected-center variants. That arithmetic is performed outside this finite circuit acceptance.
