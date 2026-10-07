# v0.1.31 → v0.1.32 comparisons

Controlled version rows use paired payloads. Best-config rows are explicitly NOT_CONTROLLED_A_B; full configurations and raw evidence are in JSON/CSV.

| Metric | v0.1.31 | v0.1.32 | Delta % | Classification |
|---|---:|---:|---:|---|
| Q4 single GPU resident64K PP | 1539.300 | 1518.300 | -1.36 | NOT_CONTROLLED_A_B |
| Q4 single GPU resident64K TG | 43.400 | 40.900 | -5.76 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual63400 PP | 2793.200 | 4474.900 | +60.21 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual63400 TG | 98.700 | 105.500 | +6.89 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual127000 PP | 2956.700 | 4964.600 | +67.91 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual127000 TG | 86.900 | 106.600 | +22.67 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual259500 PP | 3196.600 | 5570.500 | +74.26 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual259500 TG | 92.100 | 95.000 | +3.15 | NOT_CONTROLLED_A_B |
| Controlled sameK24 actual8000 PP | 1519.750 | 1570.900 | +3.37 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual8000 TG | 105.450 | 95.950 | -9.01 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual16000 PP | 2089.550 | 2156.850 | +3.22 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual16000 TG | 102.800 | 89.800 | -12.65 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual31400 PP | 2546.600 | 2614.900 | +2.68 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual31400 TG | 106.700 | 120.700 | +13.12 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual63400 PP | 3004.000 | 3045.000 | +1.36 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual63400 TG | 92.400 | 106.400 | +15.15 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual127000 PP | 3271.700 | 3296.500 | +0.76 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual127000 TG | 87.300 | 101.100 | +15.81 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual259500 PP | 3508.700 | 3521.300 | +0.36 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual259500 TG | 91.700 | 87.500 | -4.58 | CONTROLLED_WHOLE_VERSION_A_B |
| Cold start processREADY single-resident | 104.052 | 137.085 | +31.75 | NOT_CONTROLLED_A_B |
| Cold start processREADY best2GPU | 64.071 | 101.080 | +57.76 | NOT_CONTROLLED_A_B |
| Compaction actual127000 wall s | 61.335 | 56.698 | -7.56 | NOT_CONTROLLED_A_B |
| Compaction actual127000 PP | 3003.500 | 3722.200 | +23.93 | NOT_CONTROLLED_A_B |
| Compaction actual127000 TG | 92.300 | 91.400 | -0.98 | NOT_CONTROLLED_A_B |
| Compaction actual127000 TTFT s | 42.609 | 34.705 | -18.55 | NOT_CONTROLLED_A_B |
| Compaction actual250000 wall s | 109.247 | 71.447 | -34.60 | NOT_CONTROLLED_A_B |
| Compaction actual250000 PP | 3180.600 | 5335.400 | +67.75 | NOT_CONTROLLED_A_B |
| Compaction actual250000 TG | 89.000 | 92.300 | +3.71 | NOT_CONTROLLED_A_B |
| Compaction actual250000 TTFT s | 79.097 | 47.430 | -40.04 | NOT_CONTROLLED_A_B |
