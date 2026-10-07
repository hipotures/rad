# Phase B — causal Q4 policy competition

**COMPLETE_MIXED. Freeze two runtime finalists; unchanged100us Q4 remains the reference.**

Training/normalization used dev-code and dev-math only; calibration used cal-prose; hold-code, hold-structured and hold-math are entire independent episodes. Long32/128/256 repository payloads never fit the checkpoint. Last4/16 future windows are censored, not negative labels. Models predict nonexclusive expected counts, not a softmax. Seed20261005.

## Family ledger

| Family | Status | Disposition |
|---|---|---|
| current | MIXED | Shared finite-byte scheduler; all9 episode results preserved. |
| ema | MIXED | Shared finite-byte scheduler; all9 episode results preserved. |
| frequency | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| hybrid-history | MIXED | Shared finite-byte scheduler; all9 episode results preserved. |
| jev-linear | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| jev-mlp | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| jev-temporal-mlp | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| least-stale-inspired | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| markov | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| recency | MIXED | Shared finite-byte scheduler; all9 episode results preserved. |
| static | COMPLETE_NEGATIVE | Shared finite-byte scheduler; all9 episode results preserved. |
| static-development-only | COMPLETE_NEGATIVE | Independent held-out and long-document demand poorly served by2-task development profile; do not replace runtime profile. |
| native-router-H1/H4/H8 | MIXED | H1 has stronger membership but most staged candidates late; H4 ready on dev but85% selected-nonresident predictions wrong; H8 weaker plus third spare. |
| early-linear-hybrid | MIXED | Charged2-spare H4 projection, immutable same-layer slot classes, guarded target publication and persistent retention; small miss reduction with high discarded copy traffic. Live test needed. |
| Basal-semantic-prior | NOT_ATTEMPTED | Only6 independent short task traces; no justified learned semantic-to-Q4-expert map. CPU EagerBackend run_shared flattens full forwards; large checkpoint cost not justified. No Polish/translation benefit claimed. |

## Fixed-trajectory exchange outcomes

| Episode | Policy | Nonlocal entries | Promotion GB | Modeled join s | Victim-absent entries |
|---|---|---:|---:|---:|---:|
| hold-code | current | 48193 | 20.81 | 0.671 | 13496 |
| hold-code | jev-linear | 82025 | 7.16 | 0.148 | 6971 |
| hold-code | jev-mlp | 83740 | 6.80 | 0.135 | 8023 |
| hold-code | jev-temporal-mlp | 93530 | 5.57 | 0.097 | 7368 |
| hold-code | hybrid-history | 59704 | 13.22 | 0.356 | 9332 |
| hold-structured | current | 48692 | 15.94 | 0.527 | 6159 |
| hold-structured | jev-linear | 78449 | 6.60 | 0.154 | 5554 |
| hold-structured | jev-mlp | 78671 | 6.38 | 0.146 | 6112 |
| hold-structured | jev-temporal-mlp | 86118 | 5.30 | 0.103 | 6228 |
| hold-structured | hybrid-history | 59608 | 10.99 | 0.317 | 6092 |
| hold-math | current | 43922 | 16.78 | 0.524 | 8235 |
| hold-math | jev-linear | 68062 | 5.93 | 0.109 | 7856 |
| hold-math | jev-mlp | 68205 | 5.53 | 0.107 | 7816 |
| hold-math | jev-temporal-mlp | 72863 | 4.69 | 0.094 | 7471 |
| hold-math | hybrid-history | 52955 | 9.90 | 0.231 | 6729 |
| 32k | current | 227427 | 87.42 | 3.055 | 151049 |
| 32k | jev-linear | 286089 | 11.95 | 0.097 | 59010 |
| 32k | jev-mlp | 293462 | 9.98 | 0.081 | 53893 |
| 32k | jev-temporal-mlp | 332472 | 6.61 | 0.038 | 37241 |
| 32k | hybrid-history | 228464 | 41.39 | 0.962 | 109882 |
| 128k | current | 267959 | 99.37 | 3.641 | 185345 |
| 128k | jev-linear | 299289 | 14.93 | 0.183 | 82703 |
| 128k | jev-mlp | 309316 | 12.36 | 0.144 | 77838 |
| 128k | jev-temporal-mlp | 339258 | 8.25 | 0.091 | 58405 |
| 128k | hybrid-history | 271831 | 57.20 | 1.573 | 153989 |
| 256k | current | 246896 | 96.48 | 3.409 | 168745 |
| 256k | jev-linear | 287283 | 12.88 | 0.149 | 67908 |
| 256k | jev-mlp | 297806 | 10.56 | 0.105 | 62944 |
| 256k | jev-temporal-mlp | 334354 | 6.98 | 0.047 | 43902 |
| 256k | hybrid-history | 250670 | 50.30 | 1.324 | 134955 |

The cheap hybrid halves long-trace promotion traffic but does not remove nonlocal work; independent short holdouts show a material miss increase. Learned policies reduce traffic more aggressively but under-admit and increase CPU/mapped work. Recency can preserve more hits by spending more bytes. None is a replay throughput winner.

CPU-only linear/MLP costs and feature/update/selection are retained per-policy in replay files.32-unit MLP learning curves fall on development batches; held-out capacity-only coverage~94–95% does not translate into a good finite replacement schedule. The16-window temporal extension is completed negative; no larger retraining after holdout inspection.

## Causal native-router timing and charged spare

| Point | Policy | Ready admissions | Nonlocal/original | Staging GB | Useful resident entries | Victim-absent entries |
|---|---|---:|---:|---:|---:|---:|
| cost-h4-128k-run1 | predictive | 1159 | 263398/267959 | 21.34 | 35532 | 3911 |
| cost-h4-128k-run1 | reactive | 653 | 265449/267959 | 8.05 | 29816 | 3344 |
| cost-h4-256k-run1 | predictive | 1141 | 243128/246896 | 21.92 | 38732 | 3816 |
| cost-h4-256k-run1 | reactive | 568 | 245510/246896 | 8.08 | 31218 | 2724 |
| cost-h4-32k-run1 | predictive | 1032 | 224415/227427 | 18.19 | 27127 | 3591 |
| cost-h4-32k-run1 | reactive | 471 | 226410/227427 | 7.12 | 18039 | 2428 |
| cost-h4-cal-prose | predictive | 322 | 43501/44611 | 6.00 | 9536 | 371 |
| cost-h4-cal-prose | reactive | 172 | 44169/44611 | 2.01 | 6355 | 256 |
| cost-h4-dev-code | predictive | 213 | 31569/32419 | 4.76 | 10315 | 210 |
| cost-h4-dev-code | reactive | 138 | 32061/32419 | 1.62 | 7098 | 177 |
| cost-h4-dev-math | predictive | 166 | 41506/42730 | 4.71 | 12494 | 205 |
| cost-h4-dev-math | reactive | 121 | 42105/42730 | 1.60 | 10831 | 130 |
| cost-h4-hold-code | predictive | 242 | 47188/48193 | 5.06 | 10837 | 323 |
| cost-h4-hold-code | reactive | 154 | 47947/48193 | 1.82 | 7421 | 281 |
| cost-h4-hold-math | predictive | 194 | 42901/43922 | 4.84 | 14468 | 263 |
| cost-h4-hold-math | reactive | 117 | 43534/43922 | 1.62 | 11305 | 210 |
| cost-h4-hold-structured | predictive | 179 | 46996/48692 | 4.17 | 7708 | 297 |
| cost-h4-hold-structured | reactive | 105 | 47933/48692 | 1.54 | 6016 | 134 |

H4 was selected from dev timing/readiness before its3 long-profile and3 holdout transfer traces. Raw gate scores are rankings, not calibrated future probabilities. Only5 origins/targets of48 are covered. Target truth is consulted at the actual host plan; a wrong or late staged candidate cannot publish. Incoming experts remain until later replacement; no per-use restoration. Current adaptive replacement continues. All staged bytes, two reserved native slots and modeled metadata publication waits are charged.

The reactive matched scheduler and raw-router/no-learned ranking are retained as ablations. Projection timestamps follow the original observed trajectory; no predicted TG. H4’s potential miss reduction is small and discarded copy traffic large, making live outcome uncertain. This is a bounded test of an untested mechanism, not an endorsement.

## Phase C freeze

1. **history-v1**: heat*0.2+fast*(2/3); joint incoming/victim four-window utility, copy-size penalty,0.125ms margin,96 total actions and160MiB/device budget. Safe original end-verify copy/publication.
2. **early-v1**: H4 native gate reuse, CPU-only frozen linear victim/ranking, one3.072MB staging spare/device within original cache. Stage early on a dedicated worker; publish device residency only after bytes complete and before CPU releases the target plan. Protect all current routed victims. Native reactive EMA remains.

Before live early inference, a minimal test must prove main-thread stream synchronization can coexist with the separate worker while the graph awaits the host planner. OFF parity, exact native Q4 kernels, wrong/delayed predictions, reader/slot/cancellation stress and diagnostic backing-byte readback precede speed claims. Speed binaries exclude diagnostics. Finalists may lose and remain preserved.

Model constants/checkpoints and source manifests are under checkpoints/, phase-b/learned/, datasets/, sources/. Open-Jev-inspired naming is local numeric research, not published Jev. Basal remains explicitly unattempted under the bounded-data/CPU hypothesis, not disproven.

Implementation provenance update: history-v1 application preflight exposed duplicated serve/CLI selector text. The preserved failed application has no binary/request. history-v2 repairs only patch targeting; the predeclared algorithm and settings remain unchanged.

MTP signal scope: native gate predictions include every currently available drafted verifier row (T1–4), and numeric history/labels count all routed speculative branches, including later-rejected work. No future accept/reject outcome feeds an earlier decision. There is no separate draft model or future true-gate oracle.
