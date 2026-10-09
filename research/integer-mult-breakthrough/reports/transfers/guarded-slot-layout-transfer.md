# Same-volume guard allocation by selected-bit preprocessing

Status: **PROPOSED CONDITIONAL ALL-SIZE LAYOUT LEMMA**, with **EXACT FINITE C-FACTORIZATION AND STATIC-GRID CONTROLS**. This provides a possible recursive shape for the [paid packed Toffoli](packed-nonlinear-routing.md). It does not provide a new whole Gaussian network, a contracting characteristic profile, formal verification, or a multiplication exponent.

## State, preprocessing and exact target

Fix h>=4. The current role stream has a complete preceding row prefix, e consecutive complete K-bit axis chunks, and a complete suffix of spectators and payload fields. Bit rho is selected in EACH chunk, with `0<=rho<K`. The target is exactly `C^tensor(e)` on those e selected bits, independently on every dirty field and every row. Other K-bit positions are spectators. Logical volume V and complete record count remain unchanged.

For `e<2h`, perform all e selected-bit C kernels directly. Otherwise set

```text
f = floor(e/h)-1 >= 1,
u = e-h(f+1), 0<=u<h.
```

Divide the first `h(f+1)` chunks into h consecutive slots of `(f+1)K` bits. In EACH slot, pay one elementary C on bit rho of its LAST chunk. Pay the same elementary operation on each of the u remainder chunks. This is `h+u<2h` selected-bit kernels, not h transforms of whole K-bit chunks. Every guard chunk remains a complete K-bit ADDRESS range; exactly one selected bit has been transformed and its other K-1 bits are untouched spectators.

The f active selected bits in each slot are its first f chunks. A guarded Toffoli may use its complete last chunk for carry guards and may disturb those bits internally. Its exact completed endpoint restores every guard bit. No intermediate commutation assumption is made.

Assume a finite native block computes exactly `C^tensor(hf)` on those active bits of every role, identity on guard/remainder bits and all spectators, with arbitrary current dirty inputs and a paid scalar/phase/child ledger. This assumption is the missing WHOLE NETWORK interface. The completed guard kernels and this completed active target act on disjoint selected axes, so their product is exactly the original `C^tensor(e)`. They commute as exact endpoints even if the active network has nontrivial intermediate guard, scratch or role excursions. Preprocessing is paid before invoking that block and is not silently assigned to a free input encoding.

The direct kernel is

```text
C = ((1+i) I + (1-i) X)/2.
```

Splitting one specified address bit, applying its fixed Gaussian-dyadic map to aligned records, and merging is the original elementary selected-kernel supplier. In the common exact record format it costs O(V), including full payload scans and original arithmetic guard requirements. A whole `C_K` supplier is neither used nor inferred from the chunk-routing exponent tau.

## Child compaction and strict decrease

A native rank-t child, `1<=t<=h`, acts on the first t slots' first f selected chunks, after whatever paid native change of basis defines that child. Its active selected width is `e'=tf`. Those chunks are separated by guard holes. Let S be their physical axis indices and let H be missing indices in the first tf positions. The indices in S outside that prefix and the holes H have equal cardinality. Every hole is one of the at most t guard chunks encountered before this prefix ends. Pair each hole with a donor and exchange their ENTIRE equal-width K-bit address chunks.

At most t whole-K exchanges therefore move all tf active chunks into the first tf consecutive positions. The matching is calculated from fixed slot geometry. Recursively apply the exact child to that contiguous active prefix, regarding all remaining chunks as complete spectators. Return every exchange in inverse order before continuing the parent word. Original logical chunk names, guard bits, every spectator bit, row indices and full payload order are restored. Already preprocessed guard chunks are never selected by that child.

This compaction is repeated at each child boundary, preventing ancestor guard holes from accumulating inside a later active group. It touches address chunks only, never the preceding row prefix. It also retains arbitrary coefficients that are already correlated with all earlier dirty operations.

In particular, the nominal same-width child t=h satisfies

```text
e' = h*(floor(e/h)-1) <= e-h < e.
```

The well-founded selected-width measure now decreases, including when the nominal native child rank equals h. Smaller t obey `e'<=t*floor(e/h)`. This is a genuine changed stopping shape, not an improved oracle at the same selected input. Strict decrease alone can allow linear depth, so it does not establish the desired precision or time exponent.

## Complete time, row and precision obligations

Assume complete equal-K exchanges cost `O(V K^tau)` and the native block has a FIXED number of local operations/children with the guarded nonlinear routing bill. Preprocessing costs `O_h(V)`; each child pays at most 2t exchanges including its return. With fixed h and a fixed block, all newly added local work fits

```text
O_h(V((eK)^tau+1)).
```

The nonlinear routes use complete slot width `(f+1)K<=eK`, not a larger virtual address range. Their original metadata and exceptional-record correction terms remain until the long-record parameter conditions justify absorption. Arbitrary data copying, parking, restoration, inverse words, units and scalar temporary fields must remain in the complete native ledger. The Python implementation below does not prove these tape costs.

If W denotes the fixed number of physical scalar roles, a child still has volume exactly V/W after COMPLETE preceding rows are split. An address guard is not an additional scalar birth bank. This allocation introduces no new rows and no new address ranges. To use the [routing-aware stopped recurrence](routing-aware-depth-transfer.md), the root must retain its same sufficient W^L complete row stock, preceding-row preprocessing, padding and legal fixed-tape parking contracts. Guard compaction leaves that prefix unchanged; it cannot manufacture the stock when it was absent.

For a fully paid profile n_t, the old positive-power majorant

```text
Phi(z) = sum_t (n_t/W)*(t/h)^z
```

still controls the new children because `tf<=t*floor(e/h)`. A complete profile with `Phi(sigma)<1`, the declared local overhead, and a decreasing depth budget L therefore inherits the earlier stopped-frontier proof and its `O(d^sigma K^(tau(1-sigma)/(1-tau)) + d Phi(1)^L)` bound. This is a conditional implication: no new contracting n_t is supplied here, and changing guard geometry does not increase the frozen b by itself. The budget remains useful even though selected-width termination is now strict.

Every elementary C increases required denominator depth and component magnitude by at most one bit; its four-term integer numerator needs a bounded extra temporary margin. A complete fixed-grid replay can reserve all needed denominator bits in advance. Whole-K permutations and corrected Toffolis change neither grid nor magnitude. For a new recursively compiled block, exact complete child endpoints plus a uniform literal local-prefix guard are STILL required. Its fixed serial child-width count and these constant additional selected kernels fit the [endpoint-aware O(dL) guard induction](endpoint-aware-guards.md). Choosing L=O(log d) then keeps the original O(d log d) allowance. No fraction reduction or output normalization is a paid operation. Width decrease without the budget or local-prefix contract does not imply that allowance.

## Primary supplier and evidence

The original selected-kernel and routing interfaces are read-only primary inputs at `openai/math` revision `adc7f1241b42e322a6451854ab7e4b4c146bf78a`:

- [02-streams.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/02-streams.tex), SHA256 `606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab`: splitting one specified digit, fixed aligned map and merging costs O(V), including counters, rewinds and full row/suffix shape.
- [05-layers.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex), SHA256 `20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`: selected-bit layer semantics, exact arbitrary-dirty row contract, original complete chunk exchanges, and the leaf supplier `F(e)=O(e)`.

These sources were inspected in the pinned read-only PR127 upstream checkout. They are provenance for the conditional suppliers, not runtime imports or an assertion that our new all-size native block has been proved.

The standalone checker [guarded_slot_layout.py](../../code/transfers/guarded_slot_layout.py), SHA256 `5c5e9b8fdfbc9685582bd75ce6654fa0c78482e8cbe698a7c943811035eba99e`, reads only its [config](../../configs/transfers/guarded-slot-layout.json), SHA256 `f3800fa4209260a223a88e58ab8de4f51def2ae1b07360f461d5d0381d44ca2e`. It imports no producer, finite-frame compiler, existing recurrence checker, or external checkout. It replaces the assumed native block by literal elementary C kernels to discriminate the layout/factorization claim; it does NOT measure an improved recursion.

The [four-worker literal static-grid run](../../runs/20261009T034322Z-transfer-guard-layout-fixed-grid/report.md) passed in 2.349085141 seconds:

| e, K, rho, native t | Complete records | Selected kernels | Whole-K exchanges | First actual child | Evidence |
| --- | ---: | ---: | ---: | --- | --- |
| 8, 1, 0, 4 | 256 | 8 | 4 | 8 to 4 | All 1024 scalar-field columns, 262144 direct tensor coefficients |
| 12, 1, 0, 4 | 16384 | 12 | 8 | 12 to 8 to 4 | Two complete dirty four-field examples, row/suffix origin controls |
| 8, 2, 1, 2 | 65536 | 6 | 2 | 8 to 2 | All K-bit spectator ranges retained |
| 9, 1, 0, 1 | 3072 | 6 | 0 | 9 to 1 | Genuine three-row prefix, paid remainder |

The first case's independent closed tensor oracle uses `((1+i)/2)^e * (-i)^popcount(a XOR b)` for every input/output and field. It does not use the factorization or permutation code. The other cases exercise arbitrary complete Gaussian dirty fields and complete prefix/suffix origins. Omitted guard and duplicated guard reject in all cases; omitted return swaps reject precisely in the cases where return swaps exist.

For each dirty example, the STATIC replay embeds the input common grid into `2^-(3+N) Z`, where N is the exact number of selected kernels. At all times this grid is unchanged. Every four-term numerator is checked even and divided by two as an exact integer; chunk swaps retain all fields. Its final literal integer arrays equal the straight unreduced variable-grid reference at the SAME final physical grid. This binds trailing-zero semantics without using fractions, cancellation-based normalization or a zero-only input. It does not test the internal scalar/child excursions of an undiscovered native block.

## Immutable attempts and reproduction

The [control applicability failure](../../runs/20261009T033934Z-transfer-guard-layout-control-attempt/report.md), source `48324433aca0a1c3e9003b5e673d371b008f5d699a2314333fd2979ec95a90b0`, preserves an incorrect demand that omitting a nonexistent rank-one return swap must fail. The [fresh control repair](../../runs/20261009T033935Z-transfer-guard-layout-control-repair/report.md), source `bfd54a06c1e9fc05139a74327d90934cd74c818921095f912350b8c2d8044151`, passed in 1.578347153 seconds. Its reference grid exponent grows after unreduced numerator kernels. Its original `physical_global_grid_never_reduced` flag describes absence of reduction, not a tested static-grid machine. The later STATIC replay has a fresh ID, protocol, source and explicit additional fields; original bytes are unchanged.

The [fixed-grid recovery patch](../../fixtures/transfers/guard-layout-fixed-grid-recovery.patch) reconstructs bfd54a06 from the current source. Then the [control recovery patch](../../fixtures/transfers/guard-layout-control-recovery.patch) reconstructs 48324433. All hashes were independently exercised by real `git apply` in the [source-recovery run](../../runs/20261009T034420Z-transfer-guard-routing-source-recovery/report.md), including the Toffoli parse failure. The first unstamped bounded smoke reproduced the same control failure; only the separate preserved launch's actual UTC is timing evidence.

Durable protocols/summaries/failures are unchanged raw copies. Completed originals remain in ignored `work/transfers/<same-run-id>/`; source versions are recoverable from current authored code plus the retained patches. Full regeneration needs Python's standard library and the source/config only.

```bash
python3 research/integer-mult-breakthrough/code/transfers/guarded_slot_layout.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/guarded_slot_layout.py \
  --workers 4 --output research/integer-mult-breakthrough/work/transfers/<fresh-actual-UTC>-guard-layout/results
```

The [final bounded one-worker replay](../../runs/20261009T035722Z-transfer-guard-layout-bounded/report.md) passed in 0.165553295 seconds with the final source/config. It omits the exhaustive column expansion but retains dirty static-grid, row/suffix and applicable negative controls.

Each output path must be absent. Recover prior sources into an isolated ignored tree, with the fixed-grid patch followed by the control patch; never overwrite an accepted live checker or completed run.

The leverage is a conditional same-volume route beyond affine address maps, plus strict selected-width decrease for a full-rank child. The next decisive question is a complete canonical Gaussian block whose nonlinear native word has a contracting paid moment. Routing alone neither supplies that block nor asserts kappa above the current accepted value.
