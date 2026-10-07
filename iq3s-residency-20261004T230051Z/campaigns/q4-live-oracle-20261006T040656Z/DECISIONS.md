# Decisions

- Frozen Q4/100us serving reference unchanged.
- Main comparison must use the same replay binary and tape.
- No learned predictor, pool/architecture tuning or historical timing control.
- Oracle uses logical milestones, real copies and charged physical spare capacity.

## 2026-10-06 — contract v2 repair before final matrix

The full-scope deadline pilot moved local demand from 89.664% to 99.450% and measured 130.4 replay-equivalent tok/s versus 102.6 current on the same v1 binary. It issued 66,097 actual copies totaling 208.019 GB versus current native adaptation's 87.418 GB. Native head divergence began at window 15, as expected from placement-dependent arithmetic. This is encouraging scoped evidence, not a final controlled result: sparse QSA selections were not frozen. Version 2 freezes these selections and checks the warmup-carried native adaptation counter. Preserve v1; recapture v2 and use one common v2 binary in both final arms. No predictor training and no unrelated tuning.

## Freeze main matrix

Version2 pair1 is valid: same full-work hash including attention selections, equivalent initial state, all48layers and3classes, real copies. Current104.4versusfull-oracle122.5equivalenttok/s. Preserve this as attempt1 (do not add three more identicalruns). Freeze source3760e8e4ac46347f2bdec2d20b794b8a96ace980 / binary8e1d59caed959434bae87927ff9e20ff1bd010310358cdde581c4ce6345939d4 and full-deadline strategy for the final18-request matrix. Counterbalance CO/OC/CO percontext; one recorded tape/profile repeated for timing repeatability. Independent6991input/1024output Python archive-import task is separate, after matrix/overhead checks. No predictor or pool/cache tuning.

## Initial-state contract strengthening

Before final headline matrix, source audit showed that streamed-KV page residency and persistent GDN/PLE/MTP state were not explicitly attested at the prefill/decode boundary. Version2 checks expert slots/heat and successful natural arithmetic but that alone does not prove equivalence of KV service state. Add a separate version3 initial-state checksum sidecar and compare every relevant KV map/control array, numerical pools/indexer/GDN/PLE state in both arms. No hidden tensor substitution, cache reset, policy change or extra expert allocation is introduced by this attestation. Read/hash cost is common setup and separately reported in request wall. Preserve v2 tapes and first valid scoped pair; final full-initial-state points will use v3, with at most3attempts per new protocol point. If exact initial maps differ, preserve failure and choose explicit canonicalization rather than falsely claiming identical state.

## Initial-state contract repair v3

Before final repetitions, extended the common runtime with strict numerical/state sidecars. All scheduler settings remain unchanged. The final matrix is versioned v3; v1/v2 pilots remain preserved and excluded from final headline aggregation. Fresh capture32K passed140component attestation (623,320,868bytes), setup528.487ms. Actual Q4 expert parity passed all3classes at layers0/2/4/24/30; CPU/GPU activation quantization can differ numerically by the existing native math.

## Retain256Ksetup timing anomaly

First256Koracle replay improved decode52.0335->46.5734s, but observed totalwall194.6283->199.8987s because common initial-state verification took14.084s versus3.807s in the paired current arm. State/work hashes match. Residency is inactive at that step. This is unexplained preprocessing drift, retained as VALID, never a favorable-run exclusion. Final min/median/max and paired ratios must include it. No runtime or threshold tuning follows this observation.

## Final bounded decision

All 18 v3 primary attempts are valid. Full future improves paired replay decode at all three profiles; the independent source-content task confirms a separate gain. H64 is a retained negative churn result. Stop adding inference runs. Complete artifact/reproducer audits and cleanup, then finish early. The unchanged original Q4/100us baseline remains real-use; no predictor or production switch is authorized by this replay result.
