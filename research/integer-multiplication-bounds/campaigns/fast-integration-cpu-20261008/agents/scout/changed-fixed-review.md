# Independent review of the changed h23 fixed-basis controller

Reviewed on 2026-10-08 at approximately 15:51–15:54 UTC. The public reference is eligible PR40, science commit `43f59ff533598762cbc43a5e14af2bbbc76fabbd`; this review uses no newer aggregate-main mathematics or quarantined RaD-derived source.

## Result and scope

The new producer `h23-g222222222112-t2-left` is compatible with the inherited ordered `(23,25)` fixed-both construction under the same named native compiler, physical-corner and all-size tape premises. It changes the cancellation-free addition DAG and its original-envelope transitions. It does not change either physical output family, the source triples, the retained centers, the common bases `I+J`, or the reversed data geometry. The changed controller has a strictly passing complete bit moment at

`a_new = 397034999791 / 10^16`.

The reviewed packed transfer parameters therefore support the conditional candidate

`kappa_new = 39703102944100209 / 10^21`,

provided the previously reviewed guarded CRT, long-digit packed transforms, precision and native finite-controller premises remain in force. This is independent source/proof criticism and finite exact checking, not external peer review or a formal proof of the whole tape machine.

## Direct finite support and matching check

The checker [check_changed_fixed_dag.py](code/check_changed_fixed_dag.py) imports no producer, matcher, profiler or scorer. The exact first-run version is preserved as [check_changed_fixed_dag_v1.py](code/check_changed_fixed_dag_v1.py), with its byte hash equal to the first receipt. The current version adds an explicit axis selector for a later h25 check. It reads the binary DAG, independently constructs the 1,771 source triple masks, computes every active sum as a dense exact mask, and checks disjointness and the exact core/cover pair. For every node with a two-point core it also checks the complete pair-star identity, which is the condition permitting the inherited cross-common-point support interning.

It independently reconstructs the expected output order from the pinned aligned point permutation. Every one of the 5,336 original output supports is correct, including all 23 retained total outputs. The totals have the same rank-22 center frames; the local grouping and left association change neither their support nor their geometric projector. There are 38,209 binary nodes and 36,401 active additions.

The supplied 4,273 matched donor links have distinct donors, valid original-envelope inclusions, and the required rank/time orientation. The pinned link serialization omits the occurrence tag identifying a gate-input use or output use. The checker reconstructs admissible occurrences and verifies an injective assignment, rather than silently treating a node ID as a unique use. This establishes a valid matching with `R=36,401+5,336-4,273=37,464`; the independent checker does not need or claim maximum cardinality.

The receipt is [changed-fixed-independent.json](changed-fixed-independent.json). It binds the exact binary DAG, link stream, changed h23 profile, unchanged h25 profile and checker hashes.

## Why the finite physical families transfer

The inherited reversible compiler allocates `additions+outputs` roles, uses fresh nonpivot output slots, and retires nonpivot input occurrences. Its validity is a local condition on disjoint source sums and nested frames, not on balanced addition trees. The changed graph satisfies those conditions. The continuation matching only reuses nested occurrences allowed by the same original-envelope partial-swap rule; enlarged positive labels have not been substituted into the fixed-basis moment.

The fixed-both source audit proves that an actual local transition matrix `A` enters the selected tensor corner as `diag(v) A diag(nu)`, with every scale nonzero for all unchanged source triples. This argument applies to any of the newly generated nested transition matrices: it does not require the old DAG. Consequently the freshly profiled original local matrices retain their ordered corner profiles in the physical controller.

The full `(23,25)` data-corner certificate depends on the two source triples and their fixed rank-one projectors, not on the internal tree producing partial sums. Since those inputs are unchanged, its 4,073,300-pair coverage is reusable. The auxiliary exterior profiles remain `23+529` and `25+525`; source growth remains `1+21` and `1+23`. All 23 and 25 retained-center cleanup identity calls still become the same fixed rank-one complements. The copied transforms themselves keep their actual newly profiled blocks. The separate endpoint charge remains paid.

The five-prime profiler supplies the changed internal matrices. Its fresh receipt reports 71,412 distinct matrices, all evaluated under all five admissible primes, and no modular profile disagreements. The general denominator/numerator proof in [fixed-profile-api.md](fixed-profile-api.md) justifies rational northeast ranks through maximum field ranks. Agreement is a control, not the proof of exactness. The independent checker does not replay these large matrices; their pinned reconstruction and common-basis lemma remain separate, explicit finite premises.

A common final rational address prime can still be chosen outside the finite denominator/nonzero-minor exception set for the new graph. Its exact numerical size and setup constant may change; the graph is fixed, so no new growing advice or exponent appears.

## Complete moment and native constants

The independent controller reconstruction includes both internal profiles, both exterior banks, both source-growth families, every data child and the paid endpoint. Its exact values are

| Quantity | Value |
| --- | ---: |
| `m` | 575 |
| `N` | 4,073,300 |
| first bank | 86,167,200 |
| second bank | 90,850,529 |
| `W` | 185,164,329 |
| copied loss `L` | 2,226,400 |
| total rank `Wm-N+L` | 106,467,642,275 |
| deficit `N-L` | 1,846,900 |
| largest child | 529 |

The independent moment uses a 32-term rational atanh logarithm enclosure and an eighth-degree exponential Taylor enclosure with explicit geometric tails. At `a_new` it proves gap at least

`7440491087679220383761117 / 2^127`, approximately `4.37313e-14`.

This is separate from the coordinator's 24-term/Taylor-upper search. Neither search proves global optimality or optimality over all addition trees.

The native bit halving degree remains 9 and `W.bit_length()` remains 28. The unchanged complex producer has halving degree 20 and wire bits 30. Thus the product-row coefficient is still `9*28+20*30=852`, and degree 2000 retains gap `6548/25`. The complex scalar charge `G=4,793,351,472` and the semantic `E`, `B`, `C0`, `C1=1` remain exactly unchanged: the bit controller is an exact binary map, while these precision constants are constructed from the unchanged complex scalar program. These exact recomputations and all 47 inherited balanced inequalities at a newly balanced auxiliary parameter choice are preserved in [changed-native-bridge.json](changed-native-bridge.json).

The old 47 inequalities include old phase and triangular CRT costs, so their same-epsilon application is not a test of the new algorithm. The reviewed changed ledger uses `epsilon=1-10^-6`, `q=a_new*(1-10^-6)`, `kappa=a_new*(1-10^-5)`, `beta=1/20`, and fixed scalar exponent `zeta=1/1000`. The Fourier gap is `a_new*(8*10^-6+10^-12)>0`, the native lambda gap is `a_new*10^-6/2>0`, the bit-routing gap is `a_new*10^-5>0`, and the stopped complex saving `(19/20)*(717/10^7)` still exceeds `a_new`. The remaining packed, metadata, sparse-LU, scalar-phase and recovery inequalities retain the already reviewed positive gaps.

## Reproduction

The reproducible checker [check_changed_native_bridge.py](code/check_changed_native_bridge.py) independently recomputes every native constant and named changed cost row. Its distinct repeat receipt for the first witness is [changed-native-bridge-reproduced.json](changed-native-bridge-reproduced.json).

Reacquire the eligible snapshot and rebuild the general-h profiler according to [fixed-profile-api.md](fixed-profile-api.md). Regenerate the exact producer using the recorded grouping, threshold two and left association. Run the coordinator's fixed profiler and then the independent checker:

```bash
python3 -B agents/scout/code/check_changed_fixed_dag.py \
  --dag work/changed-dag-h23-20261008T1538Z/h23-g222222222112-t2-left.bin \
  --links work/changed-dag-h23-20261008T1538Z/h23-g222222222112-t2-left.bin.fixed.links \
  --first work/changed-dag-h23-20261008T1538Z/h23-g222222222112-t2-left.bin.fixed_ij_profiles.json \
  --second work/scout/snapshots/pr40-43f59ff53359/research/copied-fixed-reversed/profile-25.json \
  --saving 397034999791/10000000000000000 \
  --output work/scout/<fresh-run>.json
```

Paths in this command are relative to the campaign. The matching/profiling jobs run in the coordinator's assigned slot; snapshots and binaries remain ignored execution payloads. The durable receipts do not claim those downloaded sources or binaries are present in the Git clone.

## Joint changed h25 addendum, 15:58–16:02 UTC

The separate changed h25 producer `h25-g2222222222121-t2-right` also preserves all original output families and the same fixed `(23,25)` physical geometry. The independent direct binary checker, with `--dag-axis second`, verifies 50,570 nodes, 48,239 disjoint additions, every one of the 6,925 original outputs, and all 25 retained centers. Its 5,475 links admit an injective assignment to valid original-envelope target uses, yielding `R25=49,689`. The fresh fixed h25 profile reports 95,139 matrices under all five primes, with zero modular disagreement.

Paired with the independently checked changed h23 producer, the complete controller has `W=182,313,019`, total rank `104,828,139,025`, unchanged `L=2,226,400`, and unchanged deficit `1,846,900`. The independent exact moment supports

`a_joint = 80475950257 / (2*10^15)`

with gap at least `14907858118277991934879991 / 2^128`, approximately `4.38102e-14`. The receipt [changed-joint-independent.json](changed-joint-independent.json) binds the new DAG/links/profile and the already checked h23 profile. It does not silently replace the first witness's inputs or output file.

The same native constants remain valid: bit degree 9, wire bits 28, row coefficient 852, row degree 2000 and gap `6548/25`. The unchanged complex `G` and semantic `C1=1` proof apply for the reasons above. Every named changed packed inequality and all 47 auxiliary rebalanced inequalities pass in [changed-native-bridge-joint.json](changed-native-bridge-joint.json), supporting the conditional candidate

`kappa_joint = 8047514549749743 / (2*10^20)`.

This addendum inherits the same explicit full-matrix reconstruction, simultaneous fixed-corner, general physical compiler, tape, precision and eventual-threshold premises. No unbounded search optimality or unconditional algorithm claim is added.

To reproduce the bridge check, with paths relative to the campaign:

```bash
python3 -B agents/scout/code/check_changed_native_bridge.py \
  --source-root work/scout/snapshots/pr40-43f59ff53359 \
  --controller-receipt agents/scout/changed-joint-independent.json \
  --saving 80475950257/2000000000000000 \
  --output work/scout/<fresh-bridge>.json
```
