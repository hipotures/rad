# E020: wider GPU router lookahead

The horizon was frozen from development/calibration tasks before examining held-out and benchmark labels. Selected horizon: 8 layers. Native routing weights are confidence ranks, not calibrated future-use probabilities. Both benchmark traces preserve actual output IDs, routing, MTP windows, execution paths, resident sets, heat and first-head bits. All timing runs are diagnostic.

| Task | Policy | Copy GB/s | Admissions | Ready tail % | Promotion MB | Restore MB | Modeled restore wait s |
|---|---|---:|---:|---:|---:|---:|---:|
| dev-code | rank-first | 1.8 | 138 | 12.21 | 272.64 | 313.04 | 0.1009 |
| dev-code | rank-first | 12.6 | 138 | 16.79 | 272.64 | 313.04 | 0.0000 |
| dev-code | heat-guarded | 1.8 | 4 | 3.05 | 7.27 | 8.86 | 0.0000 |
| dev-code | heat-guarded | 12.6 | 4 | 3.05 | 7.27 | 8.86 | 0.0000 |
| dev-math | rank-first | 1.8 | 176 | 4.70 | 349.85 | 399.72 | 0.2666 |
| dev-math | rank-first | 12.6 | 176 | 10.74 | 349.85 | 399.72 | 0.0000 |
| dev-math | heat-guarded | 1.8 | 3 | 2.68 | 6.02 | 6.84 | 0.0000 |
| dev-math | heat-guarded | 12.6 | 3 | 2.68 | 6.02 | 6.84 | 0.0000 |
| cal-prose | rank-first | 1.8 | 211 | 0.92 | 409.16 | 446.64 | 17.7315 |
| cal-prose | rank-first | 12.6 | 211 | 13.74 | 409.16 | 446.64 | 0.0000 |
| cal-prose | heat-guarded | 1.8 | 50 | 0.92 | 94.41 | 105.06 | 2.8302 |
| cal-prose | heat-guarded | 12.6 | 50 | 8.42 | 94.41 | 105.06 | 0.0000 |
| hold-code | rank-first | 1.8 | 181 | 13.33 | 347.01 | 393.14 | 0.3610 |
| hold-code | rank-first | 12.6 | 181 | 17.78 | 347.01 | 393.14 | 0.0000 |
| hold-code | heat-guarded | 1.8 | 7 | 8.33 | 16.15 | 16.15 | 0.0000 |
| hold-code | heat-guarded | 12.6 | 7 | 8.33 | 16.15 | 16.15 | 0.0000 |
| hold-structured | rank-first | 1.8 | 204 | 4.47 | 395.98 | 432.33 | 1.0173 |
| hold-structured | rank-first | 12.6 | 204 | 9.76 | 395.98 | 432.33 | 0.0000 |
| hold-structured | heat-guarded | 1.8 | 6 | 0.00 | 13.00 | 13.47 | 0.0629 |
| hold-structured | heat-guarded | 12.6 | 6 | 1.22 | 13.00 | 13.47 | 0.0000 |
| hold-math | rank-first | 1.8 | 206 | 2.03 | 398.28 | 435.61 | 4.7390 |
| hold-math | rank-first | 12.6 | 206 | 11.38 | 398.28 | 435.61 | 0.0000 |
| hold-math | heat-guarded | 1.8 | 19 | 0.81 | 34.33 | 39.30 | 0.6717 |
| hold-math | heat-guarded | 12.6 | 19 | 7.72 | 34.33 | 39.30 | 0.0000 |
| 32k | rank-first | 1.8 | 100 | 6.85 | 208.23 | 229.58 | 0.0354 |
| 32k | rank-first | 12.6 | 100 | 9.59 | 208.23 | 229.58 | 0.0000 |
| 32k | heat-guarded | 1.8 | 0 | 0.00 | 0.00 | 0.00 | 0.0000 |
| 32k | heat-guarded | 12.6 | 0 | 0.00 | 0.00 | 0.00 | 0.0000 |
| 128k | rank-first | 1.8 | 107 | 8.82 | 216.50 | 244.35 | 0.4996 |
| 128k | rank-first | 12.6 | 107 | 11.76 | 216.50 | 244.35 | 0.0000 |
| 128k | heat-guarded | 1.8 | 3 | 1.96 | 4.53 | 6.53 | 0.0076 |
| 128k | heat-guarded | 12.6 | 3 | 2.94 | 4.53 | 6.53 | 0.0000 |

The queue model charges exact physical slot classes, one admission per origin, distinct in-window reservations, victim restoration and baseline promotion traffic. Victims are earlier same-device layers. The fixed trajectory and optimistic host observation deadlines do not model changed scheduling or output. Restore waits are not measured request slowdowns. This evaluates one temporary schedule; it does not close persistent placement or all wider predictors.

Artifacts: v1/selection.json, v1/analysis/, v1/transactions/inputs/, v1/transactions/results/, and diagnostic source/build identity in v1/build/.
