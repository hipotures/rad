# VM hardware and MoE residency data-movement study

## Environment and limits

Two RTX 4090 GPUs, CUDA 13.4, driver 615.71.09; guest CPU/RAM/affinity and topology are recorded in inventory.json. Guest-visible MemTotal: 161.13 GiB; affinity allows 16 CPUs. No physical host DRAM channel/CCD topology is inferred.

Two deliberately separate storage paths are tested: /srv/ai through virtiofs, and /home/user/DEV/test20261001_1 through ext4 on virtual /dev/sdb. Host SSD identity, host cache state, physical media bandwidth and write amplification are not observable. Buffered and guest-direct measurements must not be called physical SSD speeds. First pass is after preparation and fdatasync, not a cold-media guarantee.

Core status: MEASUREMENTS_COMPLETE; follow-up status: MEASUREMENTS_COMPLETE. 425 valid sustained performance repetitions from 434 raw records. Default headline windows are 60 seconds × 3 after 15 seconds warmup; supporting windows are 20 seconds × 3. Raw failures/probes/exclusions remain intact.

Direct CUDA P2P is unsupported in both directions, verified by capability probes. It is not represented as zero bandwidth. All peer bridge results are explicit pinned-host staging, with both logical delivered bytes and two transfer legs counted.

## Path and size matrix

| Scenario | Mechanism / rate unit | Mean | Median | Min / max | CV % | Repeats | Measured seconds |
|---|---|---:|---:|---:|---:|---:|---|
| ram-read-t1 | bandwidth_GB_s | 10.713 | 9.154 | 8.409 / 14.577 | 31.425 | 3 | 20.05, 20.06, 20.04 |
| ram-read-t4 | bandwidth_GB_s | 49.939 | 50.708 | 47.846 / 51.263 | 3.672 | 3 | 20.02, 20.00, 20.01 |
| ram-read-t16 | bandwidth_GB_s | 55.054 | 54.971 | 54.895 / 55.295 | 0.386 | 3 | 20.01, 20.00, 20.00 |
| ram-copy-t1 | bandwidth_GB_s | 12.632 | 12.592 | 12.562 / 12.743 | 0.765 | 3 | 20.04, 20.05, 20.00 |
| ram-copy-t4 | bandwidth_GB_s | 19.145 | 19.134 | 19.070 / 19.231 | 0.422 | 3 | 20.04, 20.04, 20.03 |
| ram-copy-t16 | bandwidth_GB_s | 17.899 | 17.902 | 17.886 / 17.909 | 0.066 | 3 | 20.03, 20.05, 20.02 |
| ram-triad-t1 | bandwidth_GB_s | 9.390 | 9.361 | 9.352 / 9.458 | 0.627 | 3 | 20.07, 20.09, 20.09 |
| ram-triad-t4 | bandwidth_GB_s | 14.182 | 14.164 | 14.162 / 14.220 | 0.233 | 3 | 20.02, 20.01, 20.01 |
| ram-triad-t16 | bandwidth_GB_s | 13.300 | 13.307 | 13.268 / 13.326 | 0.224 | 3 | 20.07, 20.06, 20.01 |
| ram-gather-segments | bandwidth_GB_s | 5.256 | 5.255 | 5.254 / 5.260 | 0.067 | 3 | 20.02, 20.00, 20.03 |
| gpu0-local-copy | bandwidth_GB_s | 446.649 | 446.651 | 446.637 / 446.659 | 0.003 | 3 | 20.00, 20.00, 20.00 |
| gpu0-gemm-large | work_rate | 60274807758266.664 | 60288133500600.000 | 60217747468700.000 / 60318542305500.000 | 0.086 | 3 | 20.00, 20.00, 20.00 |
| gpu0-gemm-small | work_rate | 5459544169410.000 | 5464297192960.000 | 5447755243280.000 / 5466580071990.000 | 0.188 | 3 | 20.00, 20.00, 20.00 |
| gpu1-local-copy | bandwidth_GB_s | 446.718 | 446.716 | 446.700 / 446.738 | 0.004 | 3 | 20.00, 20.00, 20.00 |
| gpu1-gemm-large | work_rate | 61117926244433.336 | 61121519699400.000 | 61076655289900.000 / 61155603744000.000 | 0.065 | 3 | 20.00, 20.00, 20.00 |
| gpu1-gemm-small | work_rate | 5496999210446.667 | 5491030029320.000 | 5463199435740.000 / 5536768166280.000 | 0.676 | 3 | 20.00, 20.00, 20.00 |
| both-gpu-gemm | work_rate | 121442537885257.047 | 121426378379435.422 | 121321692682147.188 / 121579542594188.547 | 0.107 | 3 | 20.00, 20.00, 20.00 |
| gpu0-h2d-pageable-4096 | bandwidth_GB_s | 0.634 | 0.631 | 0.605 / 0.667 | 4.893 | 3 | 20.00, 20.00, 20.00 |
| gpu0-h2d-pageable-3145728 | bandwidth_GB_s | 10.802 | 10.803 | 10.785 / 10.817 | 0.147 | 3 | 20.00, 20.00, 20.00 |
| gpu0-h2d-pageable-67108864 | bandwidth_GB_s | 13.005 | 12.995 | 12.993 / 13.027 | 0.143 | 3 | 20.00, 20.00, 20.00 |
| gpu0-h2d-pinned-4096 | bandwidth_GB_s | 0.630 | 0.652 | 0.560 / 0.679 | 9.918 | 3 | 20.00, 20.00, 20.00 |
| gpu0-h2d-pinned-3145728 | bandwidth_GB_s | 12.634 | 12.635 | 12.634 / 12.635 | 0.005 | 3 | 60.00, 60.00, 60.00 |
| gpu0-h2d-pinned-67108864 | bandwidth_GB_s | 13.357 | 13.357 | 13.357 / 13.358 | 0.004 | 3 | 20.00, 20.00, 20.00 |
| gpu0-d2h-pageable-4096 | bandwidth_GB_s | 0.865 | 0.863 | 0.860 / 0.872 | 0.752 | 3 | 20.00, 20.00, 20.00 |
| gpu0-d2h-pageable-3145728 | bandwidth_GB_s | 10.633 | 10.642 | 10.584 / 10.672 | 0.418 | 3 | 20.00, 20.00, 20.00 |
| gpu0-d2h-pageable-67108864 | bandwidth_GB_s | 12.879 | 12.878 | 12.874 / 12.886 | 0.047 | 3 | 20.00, 20.01, 20.00 |
| gpu0-d2h-pinned-4096 | bandwidth_GB_s | 0.920 | 0.920 | 0.910 / 0.929 | 1.031 | 3 | 20.00, 20.00, 20.00 |
| gpu0-d2h-pinned-3145728 | bandwidth_GB_s | 12.503 | 12.503 | 12.502 / 12.504 | 0.007 | 3 | 60.00, 60.00, 60.00 |
| gpu0-d2h-pinned-67108864 | bandwidth_GB_s | 13.180 | 13.180 | 13.180 / 13.181 | 0.005 | 3 | 20.00, 20.00, 20.01 |
| gpu0-stage-expert | bandwidth_GB_s | 6.807 | 6.834 | 6.707 / 6.879 | 1.311 | 3 | 20.00, 20.00, 20.00 |
| gpu0-pinned-double-bulk | bandwidth_GB_s | 13.372 | 13.372 | 13.372 / 13.373 | 0.003 | 3 | 20.00, 20.00, 20.00 |
| gpu0-registration | bandwidth_GB_s | 17.762 | 17.756 | 17.733 / 17.797 | 0.185 | 3 | 20.00, 20.00, 20.00 |
| gpu0-mapped-coalesced | bandwidth_GB_s | 13.449 | 13.449 | 13.448 / 13.449 | 0.004 | 3 | 20.04, 20.00, 20.04 |
| gpu0-mapped-scatter | bandwidth_GB_s | 1.057 | 1.057 | 1.056 / 1.059 | 0.151 | 3 | 20.33, 20.31, 20.27 |
| gpu1-h2d-pageable-4096 | bandwidth_GB_s | 0.653 | 0.654 | 0.650 / 0.656 | 0.444 | 3 | 20.00, 20.00, 20.00 |
| gpu1-h2d-pageable-3145728 | bandwidth_GB_s | 10.791 | 10.794 | 10.760 / 10.819 | 0.277 | 3 | 20.00, 20.00, 20.00 |
| gpu1-h2d-pageable-67108864 | bandwidth_GB_s | 12.998 | 12.992 | 12.989 / 13.012 | 0.100 | 3 | 20.00, 20.01, 20.01 |
| gpu1-h2d-pinned-4096 | bandwidth_GB_s | 0.625 | 0.617 | 0.611 / 0.647 | 3.064 | 3 | 20.00, 20.00, 20.00 |
| gpu1-h2d-pinned-3145728 | bandwidth_GB_s | 12.633 | 12.633 | 12.632 / 12.634 | 0.008 | 3 | 60.00, 60.00, 60.00 |
| gpu1-h2d-pinned-67108864 | bandwidth_GB_s | 13.359 | 13.360 | 13.358 / 13.361 | 0.012 | 3 | 20.00, 20.00, 20.00 |
| gpu1-d2h-pageable-4096 | bandwidth_GB_s | 0.853 | 0.850 | 0.846 / 0.865 | 1.206 | 3 | 20.00, 20.00, 20.00 |
| gpu1-d2h-pageable-3145728 | bandwidth_GB_s | 10.554 | 10.548 | 10.512 / 10.601 | 0.424 | 3 | 20.00, 20.00, 20.00 |
| gpu1-d2h-pageable-67108864 | bandwidth_GB_s | 12.881 | 12.875 | 12.871 / 12.897 | 0.110 | 3 | 20.00, 20.00, 20.00 |
| gpu1-d2h-pinned-4096 | bandwidth_GB_s | 0.918 | 0.912 | 0.909 / 0.934 | 1.489 | 3 | 20.00, 20.00, 20.00 |
| gpu1-d2h-pinned-3145728 | bandwidth_GB_s | 12.505 | 12.504 | 12.503 / 12.507 | 0.016 | 3 | 60.00, 60.00, 60.00 |
| gpu1-d2h-pinned-67108864 | bandwidth_GB_s | 13.180 | 13.180 | 13.180 / 13.180 | 0.002 | 3 | 20.00, 20.00, 20.00 |
| gpu1-stage-expert | bandwidth_GB_s | 6.785 | 6.841 | 6.669 / 6.844 | 1.481 | 3 | 20.00, 20.00, 20.00 |
| gpu1-pinned-double-bulk | bandwidth_GB_s | 13.373 | 13.373 | 13.373 / 13.374 | 0.005 | 3 | 20.00, 20.00, 20.00 |
| gpu1-mapped-coalesced | bandwidth_GB_s | 13.448 | 13.448 | 13.446 / 13.448 | 0.007 | 3 | 20.00, 20.00, 20.00 |
| gpu1-mapped-scatter | bandwidth_GB_s | 1.061 | 1.061 | 1.060 / 1.061 | 0.057 | 3 | 20.23, 20.23, 20.25 |
| both-h2d | bandwidth_GB_s | 26.731 | 26.728 | 26.720 / 26.744 | 0.046 | 3 | 20.00, 20.00, 20.01 |
| both-d2h | bandwidth_GB_s | 26.387 | 26.387 | 26.387 / 26.387 | 0.001 | 3 | 20.00, 20.00, 20.00 |
| both-mixed | bandwidth_GB_s | 26.382 | 26.389 | 26.369 / 26.390 | 0.045 | 3 | 20.00, 20.01, 20.01 |
| gpu0-bidirectional | bandwidth_GB_s | 22.637 | 22.637 | 22.636 / 22.637 | 0.001 | 3 | 20.01, 20.01, 20.01 |
| bridge-0-1-4096-serial | bandwidth_GB_s | 0.345 | 0.344 | 0.342 / 0.350 | 1.188 | 3 | 20.00, 20.00, 20.00 |
| bridge-0-1-3145728-serial | bandwidth_GB_s | 6.162 | 6.162 | 6.162 / 6.163 | 0.009 | 3 | 20.00, 20.00, 20.00 |
| bridge-0-1-67108864-serial | bandwidth_GB_s | 6.627 | 6.627 | 6.627 / 6.628 | 0.007 | 3 | 20.01, 20.01, 20.01 |
| bridge-0-1-bulk-double | bandwidth_GB_s | 8.812 | 8.813 | 8.809 / 8.814 | 0.032 | 3 | 20.01, 20.01, 20.01 |
| bridge-1-0-4096-serial | bandwidth_GB_s | 0.340 | 0.333 | 0.333 / 0.354 | 3.454 | 3 | 20.00, 20.00, 20.00 |
| bridge-1-0-3145728-serial | bandwidth_GB_s | 6.160 | 6.160 | 6.159 / 6.161 | 0.020 | 3 | 20.00, 20.00, 20.00 |
| bridge-1-0-67108864-serial | bandwidth_GB_s | 6.627 | 6.627 | 6.626 / 6.627 | 0.014 | 3 | 20.00, 20.00, 20.01 |
| bridge-1-0-bulk-double | bandwidth_GB_s | 8.811 | 8.811 | 8.810 / 8.813 | 0.022 | 3 | 20.00, 20.01, 20.00 |
| bridge-roundtrip-activation | bandwidth_GB_s | 1.488 | 1.485 | 1.485 / 1.493 | 0.298 | 3 | 20.00, 20.00, 20.00 |
| bridge-bidirectional | bandwidth_GB_s | 16.241 | 16.241 | 16.238 / 16.242 | 0.012 | 3 | 20.00, 20.01, 20.02 |
| virtiofs-read-1048576-direct0-qd1 | bandwidth_GB_s | 7.776 | 7.781 | 7.736 / 7.810 | 0.481 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-read-1048576-direct1-qd8 | bandwidth_GB_s | 2.755 | 2.789 | 2.635 / 2.840 | 3.860 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-randread-4096-direct1-qd1 | bandwidth_GB_s | 0.112 | 0.095 | 0.094 / 0.148 | 27.620 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-randread-4096-direct1-qd16 | bandwidth_GB_s | 0.199 | 0.197 | 0.173 / 0.227 | 13.420 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-randread-262144-direct1-qd8 | bandwidth_GB_s | 2.219 | 2.220 | 2.212 / 2.226 | 0.321 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-randread-3145728-direct1-qd1 | bandwidth_GB_s | 3.442 | 3.605 | 3.104 / 3.618 | 8.518 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-randread-3145728-direct1-qd8 | bandwidth_GB_s | 3.389 | 3.335 | 3.239 / 3.593 | 5.406 | 3 | 20.01, 20.01, 20.01 |
| virtiofs-randread-3145728-direct0-qd1 | bandwidth_GB_s | 11.170 | 11.119 | 11.111 / 11.281 | 0.860 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-write-durable | bandwidth_GB_s | 0.134 | 0.134 | 0.134 / 0.134 | 0.003 | 3 | 20.03, 20.03, 20.03 |
| virtiofs-pipeline-gpu0-b1 | bandwidth_GB_s | 3.002 | 2.998 | 2.982 / 3.026 | 0.746 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-pipeline-gpu0-b3 | bandwidth_GB_s | 3.472 | 3.484 | 3.341 / 3.591 | 3.618 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-pipeline-bulk | bandwidth_GB_s | 3.871 | 3.883 | 3.845 / 3.885 | 0.583 | 3 | 20.00, 20.06, 20.01 |
| virtiofs-pipeline-shared-both | bandwidth_GB_s | 3.402 | 3.491 | 3.211 / 3.503 | 4.859 | 3 | 20.00, 20.00, 20.00 |
| ext4-read-1048576-direct0-qd1 | bandwidth_GB_s | 13.431 | 13.417 | 13.367 / 13.510 | 0.539 | 3 | 20.00, 20.00, 20.00 |
| ext4-read-1048576-direct1-qd8 | bandwidth_GB_s | 6.746 | 6.746 | 6.745 / 6.748 | 0.019 | 3 | 20.00, 20.00, 20.00 |
| ext4-randread-4096-direct1-qd1 | bandwidth_GB_s | 0.058 | 0.057 | 0.057 / 0.058 | 0.529 | 3 | 20.00, 20.00, 20.00 |
| ext4-randread-4096-direct1-qd16 | bandwidth_GB_s | 0.626 | 0.625 | 0.624 / 0.628 | 0.284 | 3 | 20.00, 20.00, 20.00 |
| ext4-randread-262144-direct1-qd8 | bandwidth_GB_s | 6.751 | 6.754 | 6.744 / 6.755 | 0.096 | 3 | 20.00, 20.00, 20.00 |
| ext4-randread-3145728-direct1-qd1 | bandwidth_GB_s | 4.684 | 4.679 | 4.650 / 4.723 | 0.783 | 3 | 20.00, 20.00, 20.00 |
| ext4-randread-3145728-direct1-qd8 | bandwidth_GB_s | 7.099 | 7.099 | 7.098 / 7.100 | 0.014 | 3 | 20.00, 20.00, 20.00 |
| ext4-randread-3145728-direct0-qd1 | bandwidth_GB_s | 13.634 | 13.644 | 13.608 / 13.651 | 0.171 | 3 | 20.00, 20.00, 20.00 |
| ext4-write-durable | bandwidth_GB_s | 0.134 | 0.134 | 0.134 / 0.134 | 0.000 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-gpu0-b1 | bandwidth_GB_s | 3.417 | 3.416 | 3.413 / 3.421 | 0.112 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-gpu0-b3 | bandwidth_GB_s | 4.179 | 4.178 | 4.177 / 4.182 | 0.058 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-gpu1-b1 | bandwidth_GB_s | 3.419 | 3.420 | 3.416 / 3.421 | 0.078 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-gpu1-b3 | bandwidth_GB_s | 4.183 | 4.182 | 4.181 / 4.186 | 0.058 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-stage | bandwidth_GB_s | 3.450 | 3.411 | 3.405 / 3.533 | 2.096 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-readers2 | bandwidth_GB_s | 4.626 | 4.608 | 4.594 / 4.674 | 0.927 | 3 | 20.00, 20.00, 20.00 |
| ext4-pipeline-bulk | bandwidth_GB_s | 5.239 | 5.245 | 5.221 / 5.249 | 0.291 | 3 | 20.04, 20.02, 20.01 |
| ext4-pipeline-shared-both | bandwidth_GB_s | 3.991 | 3.976 | 3.975 / 4.022 | 0.676 | 3 | 20.00, 20.00, 20.00 |
| virtiofs-reverse-durable | bandwidth_GB_s | 0.125 | 0.125 | 0.124 / 0.125 | 0.112 | 3 | 20.07, 20.02, 20.08 |
| ext4-reverse-durable | bandwidth_GB_s | 0.129 | 0.129 | 0.129 / 0.130 | 0.112 | 3 | 20.07, 20.08, 20.11 |
| pipeline-stage-diagnostic-virtiofs | bandwidth_GB_s | 5.449 | 5.461 | 5.345 / 5.542 | 1.818 | 3 | 20.00, 20.00, 20.00 |
| pipeline-stage-diagnostic-ext4 | bandwidth_GB_s | 3.239 | 3.211 | 3.106 / 3.401 | 4.614 | 3 | 20.00, 20.00, 20.00 |
| reverse-active-virtiofs | bandwidth_GB_s | 0.125 | 0.125 | 0.124 / 0.125 | 0.069 | 3 | 20.07, 20.07, 20.08 |
| reverse-active-ext4 | bandwidth_GB_s | 0.129 | 0.129 | 0.129 / 0.129 | 0.003 | 3 | 20.09, 20.07, 20.07 |

Native latency p50/p95/p99 and sample counts are in summary.json by repetition, with raw bounded-batch sampling semantics. fio latency histograms and achieved queue depth are retained in native output. No averaged p99 is presented as a pooled p99. CPU read/copy/triad useful payload differs from estimated read+write traffic. cuBLAS uses FP32 pedantic math; small GEMMs are cache/dispatch-sensitive surrogates, not DRAM bandwidth or LLM tokens/s.

## Concurrent paths and optimizations

See isolated-versus-concurrent.png and per-worker native paths in raw records. Simultaneous two-worker GPU cases use separate actual measurement windows; do not interpret their aggregate as the sum of isolated peaks or a perfectly synchronized common interval. Grouped both-GPU copies have equal completed payload counts by construction. Reusable pinned buffers, explicit pageable-to-pinned staging, double/triple buffering, modest reader concurrency, scattered mapped-host access, and immutable segmented versus contiguous promotion are scoped reversible comparisons. Changes in mechanism and buffer count are explicit in each case.

## Interference envelope

| Pair | Baseline / loaded useful rate (mean) | Achieved H2D GiB/s | Useful-work loss mean % | Loss min / max % | p99 latency increase mean % | Independent pairs |
|---|---:|---:|---:|---:|---:|---:|
| gemm-104857600 | 6.02e+13 / 6.02e+13 | 0.097 | -0.03 | -0.18 / 0.18 | -0.011 | 3 |
| gemm-2147483648 | 6.02e+13 / 5.99e+13 | 1.656 | 0.49 | 0.38 / 0.61 | 0.393 | 3 |
| dispatch-104857600 | 5.48e+12 / 5.52e+12 | 0.097 | -0.61 | -1.24 / -0.11 | -0.396 | 3 |
| dispatch-524288000 | 5.04e+12 / 5.19e+12 | 0.462 | -3.42 | -12.50 / 0.35 | -7.885 | 5 |
| dispatch-2147483648 | 4.88e+12 / 4.85e+12 | 1.651 | 0.27 | -8.67 / 8.14 | 1.062 | 3 |
| cpu-104857600 | 12.9 / 12.9 | 0.097 | 0.16 | -0.27 / 0.44 | 0.878 | 3 |
| cpu-2147483648 | 12.9 / 12.6 | 1.640 | 2.66 | 2.44 / 2.79 | 1.908 | 3 |
| burst30s | 5.5e+12 / 5.48e+12 | 0.098 | 0.27 | -0.50 / 1.71 | 0.433 | 3 |
| both-gpus | 1.21e+14 / 1.21e+14 | 0.925 | 0.24 | 0.04 / 0.49 | UNAVAILABLE | 3 |
| combined | 6e+13 / 5.98e+13 | 0.461 | 0.20 | 0.13 / 0.29 | 0.327 | 3 |
| storage-ext4 | 5.48e+12 / 5.3e+12 | 0.414 | 3.21 | -0.11 / 9.25 | 15.800 | 3 |
| controller | 12.6 / 12.5 | 0.000 | 0.60 | -2.43 / 3.50 | 0.793 | 3 |
| rolling-monitor | 12.8 / 12.8 | 0.000 | 0.15 | 0.05 / 0.21 | -0.151 | 3 |

A/B order alternates by repetition. Negative losses are preserved as observed improvements. Rate pacing is completion-based and conservative; use achieved, not requested traffic rates. The 30-second burst case has only a few events per repetition, so three repetitions do not establish robust burst-tail guarantees. Native five-second cumulative useful-work logs accompany approximately 1 Hz RSS/CPU/GPU/PCIe telemetry. Telemetry aggregate scope includes setup and warmup; it is not claimed as pure measured-phase utilization. No PSS polling occurs.

## Memory, storage safety and visibility

| Check | Evidence / result |
|---|---|
| Logical write budget | 157.250 GiB conservatively reserved across preparation/warmup/tests and earlier preserved preflight, ceiling 512 GiB. Actual traced write totals are stored per ledger entry; unobserved probe writes remain conservatively charged. |
| Minimum observed MemAvailable | 153.919 GiB; per-request RSS peaks in summary. |
| Host allocation ceiling | Buffers remain below min(64 GiB,50% initial available); host available reserve max(16 GiB,15% total), GPU reserve 3 GiB each, free-space reserve max(32 GiB,15% capacity). |
| Corpus | 16 GiB seeded non-sparse corpus per path; exclusively created and fdatasync completed; allocated size and pre/post sampled signatures in manifests. |
| Physical counters | Guest logical I/O and process counters available; host media identity/cache and physical write amplification unavailable. |
| Pinning | CUDA pin/register operations tested; ulimit is recorded, and is not assumed to be an exact CUDA allocation ceiling. |
| Optional infrastructure | No driver/VM/mount/power changes; no raw device writes, global cache drops or model changes. A delegated user-owned cgroup CPU quota is tested in a transient scope (25000/100000, one-quarter of one core), without changing foreign/global limits. GDS not exercised; installed files alone do not establish a direct supported path. |

## Scheduler implications

Threshold cases in scheduler-envelope.json require all three paired repetitions to meet the stated 2%,5%,10% compute-loss limit. These are measured surrogate bounds, not guaranteed production budgets. cost-model.json separates each device/mechanism/buffer count, provides measured lookup ranges, and only accepts a fixed-overhead+bytes/bandwidth fit when residuals support it. Extrapolation is unsupported. Inclusive immutable host backing makes clean GPU eviction unnecessary to read back; the exchange control is separate. Remote per-layer execution must pay the measured explicit-host handoff/round-trip cost without P2P. These data cannot decide the best Qwen runtime or train a predictor.

## Direct numerical answers

1. **Workload-dependent bottlenecks.** GPU0 warm pinned expert-sized (3 MiB) H2D is 12.635 GB/s (CV 0.005%, 3 repetitions) and D2H is 12.503 GB/s (CV 0.007%, 3 repetitions). GPU0 mapped coalesced and scattered reads are 13.449 GB/s (CV 0.004%, 3 repetitions) and 1.057 GB/s (CV 0.151%, 3 repetitions). The scattered kernel is transaction-efficiency-sensitive; this is not a measurement of Strata’s expert kernel. CPU 16-thread read/copy/triad useful payload is 54.971 GB/s (CV 0.386%, 3 repetitions) / 17.902 GB/s (CV 0.066%, 3 repetitions) / 13.307 GB/s (CV 0.224%, 3 repetitions); triad estimates three read/write legs per payload byte. GPU0 FP32 large SGEMM is 60.288 TFLOP/s (CV 0.086%, 3 repetitions) and local-copy payload is 446.651 GB/s (CV 0.003%, 3 repetitions). SGEMM is a compute surrogate and local copy estimates two device-memory legs. No SM occupancy or physical DRAM channel attribution was measured.

2. **Supported background budgets.** The table below gives only actually tested points for which every paired repetition meets the indicated useful-work-loss limit and baseline/loaded repetition CV are each <=5%. Unstable baselines remain in the full results but do not support a transfer budget. It does not select a universal budget by taking the largest rate across different workloads. Negative losses are retained and repeated latency samples are correlated.

| Worst-observed loss ceiling | Workload/transfer pairs satisfying it | Achieved rate GiB/s |
|---|---|---|
| 2% | gemm-104857600; gemm-2147483648; dispatch-104857600; cpu-104857600; burst30s; both-gpus; combined | 0.097; 1.656; 0.097; 0.097; 0.098; 0.925; 0.461 |
| 5% | gemm-104857600; gemm-2147483648; dispatch-104857600; cpu-104857600; cpu-2147483648; burst30s; both-gpus; combined | 0.097; 1.656; 0.097; 0.097; 1.641; 0.098; 0.925; 0.461 |
| 10% | gemm-104857600; gemm-2147483648; dispatch-104857600; dispatch-2147483648; cpu-104857600; cpu-2147483648; burst30s; both-gpus; combined | 0.097; 1.656; 0.097; 1.651; 0.097; 1.641; 0.098; 0.925; 0.461 |

Unstable pairs excluded from supported budgets: dispatch-524288000 (baseline CV 11.77%, loaded 8.7%); storage-ext4 (baseline CV 0.27%, loaded 5.24%). Two additional unchanged-binary repetitions investigate the initial noisy 500MiB/s small-dispatch pair; see raw/followup-v6-revision.json and raw/anomaly-dispatch500-initial3.json.

3. **Burst versus smooth.** Small-dispatch compute at the nominal 100 MiB/s smooth stream loses -0.61% mean, -1.24–-0.11% observed range; equal-nominal-average 3,000 MiB bursts every 30 seconds lose 0.27% mean, -0.50–1.71% observed range. The paired mean p99 increases and achieved rates are in the interference table. The separate boundary-instrumented plot aligns actual burst start/end events with native measurement time, CPU and GPU power. Only about two measured burst events per minute occur; whole-minute p99 can miss rare burst stalls, so these runs do not establish a safe worst-tail guarantee.

4. **Simultaneous consumption by both GPUs.** Grouped 64 MiB H2D and D2H total payload rates are 26.728 GB/s (CV 0.046%, 3 repetitions) / 26.387 GB/s (CV 0.001%, 3 repetitions). For the same 64 MiB size, isolated H2D is 13.357 GB/s (CV 0.004%, 3 repetitions) / 13.360 GB/s (CV 0.012%, 3 repetitions).
Observed both-card H2D is 100.04% of the sum of isolated same-size medians. The concurrent aggregate is measured directly, not assumed from that sum; grouped copies have equal delivered counts by construction.

5. **P2P and host bridging.** Direct CUDA P2P is unsupported both ways. Explicit GPU0→pinned RAM→GPU1 serial 3 MiB bridge is 6.162 GB/s (CV 0.009%, 3 repetitions), with median-of-repetition p50/p99 511.20 us / 513.52 us. The 32 KiB activation round trip p50/p99 is 47.58 us / 69.24 us. Each bridge object additionally updates an 8-byte source validation tag: this extra H2D transaction is included in timing but excluded from the native payload-leg byte counter. Round-trip delivered bytes count both directions; its four transfer legs are not a one-way application bandwidth.

6. **Expert-sized storage evidence.** Both paths have private seeded 16 GiB corpora and their own regular-file write controls. The following table uses 3 MiB random reads with explicit guest O_DIRECT, with no inference about host caches/physical media. p99 is the median of the three repetition-specific fio p99 values, not a pooled p99.

| Visible path | QD1 rate | QD1 p99 | QD8 rate | QD8 p99 |
|---|---|---|---|---|
| virtiofs | 3.605 GB/s (CV 8.518%, 3 repetitions) | 1.958 ms | 3.335 GB/s (CV 5.406%, 3 repetitions) | 12.911 ms |
| ext4 | 4.679 GB/s (CV 0.783%, 3 repetitions) | 1.004 ms | 7.099 GB/s (CV 0.014%, 3 repetitions) | 5.669 ms |

Readiness for an SSD-backed expert tier must be judged against the promotion budget, queue depth and expert miss burst size, rather than one aggregate peak. Guest direct descriptors are recorded in raw/guest-direct-evidence.jsonl. virtiofs and ext4/QEMU block results are visible path/cache measurements; no physical SSD identity or cold-host-cache guarantee is available. Limited fio writes have independent full 256 MiB CRC32C readback after the timed write/final fsync. Actual native fio worker CPU/RSS is supplemented separately from the Python safety wrapper.

7. **Layer split versus remote experts.** Without P2P, frequent per-layer remote work pays the staged transfer/launch/synchronization cost above. Inclusive residency promotions can be infrequent and avoid clean-eviction D2H; the immutable-store diagnostic validates completion before slot publication and skips already-ready IDs. The hardware data do not choose a Qwen runtime: actual expert routing, CPU fallback, MTP acceptance, output summation and useful token latency require same-token model A/B. That Strata experiment is queued separately and cannot be attributed to this surrogate campaign.

8. **Retest after changing attachment or going bare metal.** Repeat inventory and loaded PCIe lane width/P2P first; use the same seeded corpus size and buffered/guest-direct read matrix on the new path. Repeat real file→RAM→GPU pipelines and the paired compute/transfer points near the observed interference knee. Where exposed, add host SSD identity, health and physical counters/cache state; do not assume all rates improve.

9. **Next measurement.** A frozen same-token IQ3_S experiment comparing layer split and original/optimized helper, with identical initial expert capacities, equal warmup and suffix lookup disabled, plus routing/CPU-fallback/PCIe counters, most directly reduces the runtime uncertainty. For a predictive residency design, follow it with a held-out routing/miss trace replay under the measured achieved transfer budgets and paired token latency; no predictor was trained here.

## Scoped before/after optimization observations

| Reversible comparison | Median rate change | Interpretation |
|---|---:|---|
| pageable → reusable pinned, same 3 MiB | +16.95% | Same-case mechanism comparison; distinct path/software cohort retained. |
| explicit bridge one → two buffers, same 64 MiB | +32.98% | Same-case mechanism comparison; distinct path/software cohort retained. |
| real ext4 pipeline one → three buffers, same 3 MiB | +22.31% | Same-case mechanism comparison; distinct path/software cohort retained. |
| real virtiofs pipeline one → three buffers, same 3 MiB | +16.23% | Same-case mechanism comparison; distinct path/software cohort retained. |
| same synthetic delta stream: segments staging → prepared contiguous backing | -1.61% | Same-case mechanism comparison; distinct path/software cohort retained. |

Controller ranked/cooperative/quota rates, core-seconds and rolling-monitor interference are in summary.json. A 25% CPUQuota transient scope means one-quarter of one core; it neither caps memory bandwidth nor promises suppression of instantaneous bursts. Pipeline stage sums overlap and must not be added to reconstruct elapsed wall time. Reservoir store iteration latencies include no-transfer already-resident delta hits; payload bandwidth counts only promoted bytes.

## Combined useful work

GPU useful-work loss for the paired combined CPU/GPU case: 0.20% mean, 0.13–0.29% observed range.
Concurrent CPU useful-byte-rate loss: 1.01% mean, 0.66–1.18% observed range over 3 paired repetitions. This is distinct from GPU FLOP/s; original byte counts and measured durations are retained.

## Exclusions, failures and reproducibility

Earlier preflight run is preserved separately and not pooled across changed orchestrator hashes. One RAM repetition conservatively overlapping a follow-up compiler build is excluded by exact raw path and replaced after core execution. All raw requests and stderr remain. The separate follow-up binary implements actual immutable segmented backing, completion-gated publication, clean eviction and simulated noninclusive exchange, plus decaying rolling counts/ranked-plan drift monitoring. Its hash/cohort is explicit; comparisons are made within each binary.

- ram-read-t1 repetition 3: EXCLUDED_BUILD_BACKGROUND; retained nonperformance record
- peer-0-1 repetition 1: UNSUPPORTED; cudaDeviceCanAccessPeer=false
- peer-0-1 repetition 2: UNSUPPORTED; cudaDeviceCanAccessPeer=false
- peer-0-1 repetition 3: UNSUPPORTED; cudaDeviceCanAccessPeer=false
- peer-1-0 repetition 1: UNSUPPORTED; cudaDeviceCanAccessPeer=false
- peer-1-0 repetition 2: UNSUPPORTED; cudaDeviceCanAccessPeer=false
- peer-1-0 repetition 3: UNSUPPORTED; cudaDeviceCanAccessPeer=false
- virtiofs-first-pass repetition 1: PROBE; retained nonperformance record
- ext4-first-pass repetition 1: PROBE; retained nonperformance record

Plots: transfer-size-throughput-latency.png, interference-envelope.png, isolated-versus-concurrent.png, storage-gpu-pipeline.png, storage-paths.png, burst-compute-power-cpu.png.

Artifacts: inventory.json/txt, campaign_config.json, plan.json, followup-plan.json, progress.json, followup-progress.json, raw/, samples/, results.jsonl, summary.csv/json, cost-model.json, scheduler-envelope.json, sources.json and code/. Reproduce with run_campaign.sh; exact per-case commands are retained for narrow diagnostics.
