# Controlled runtime comparison — K=24

Identical paired API payloads; full arena, INT8, spec4/min-p0.5, default workers/PCIe, auto prefill, max262144. Dense/MTP/profile bytes identical. Whole-version comparison; no isolated patch-causality claim.

| Actual tokens | n/version | PP v0.1.31 | PP v0.1.32 | PP delta | TG v0.1.31 | TG v0.1.32 | TG delta |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8000 | 2 | 1519.75 | 1570.90 | +3.37% | 105.45 | 95.95 | -9.01% |
| 16000 | 2 | 2089.55 | 2156.85 | +3.22% | 102.80 | 89.80 | -12.65% |
| 31400 | 3 | 2546.60 | 2614.90 | +2.68% | 106.70 | 120.70 | +13.12% |
| 63400 | 3 | 3004.00 | 3045.00 | +1.36% | 92.40 | 106.40 | +15.15% |
| 127000 | 3 | 3271.70 | 3296.50 | +0.76% | 87.30 | 101.10 | +15.81% |
| 259500 | 3 | 3508.70 | 3521.30 | +0.36% | 91.70 | 87.50 | -4.58% |

All measured requests generated256 tokens, tokenizer/API counts matched, and reuse was zero. At32K–256K cells n=3; 8K/16K n=2. Medians are limited by this sample size and substantial TG variability. These are controlled K24 measurements, not yet final tuned production results.

Raw request/result evidence: controls/v0131/raw/ and controls/v0132/raw/.
