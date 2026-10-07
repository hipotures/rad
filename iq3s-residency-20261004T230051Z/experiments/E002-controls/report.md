# E002: fresh CURRENT controls

| Profile | Actual input range | PP median | TG min/median/max | TTFT median | Primary/stage1 slots |
|---|---:|---:|---:|---:|---:|
| 32k | 28378–28381 | 4739.5 | 153.3/155.9/157.8 | 6.13 | 10240/8477 |
| 128k | 126715–126719 | 5985.2 | 124.2/133.2/153.1 | 21.69 | 10183/8437 |

All six requests produced4096 tokens with zero reuse, using input+output+8 <= actual configured32768/131072. Serial-three cache history follows the predeclared protocol. First measured PP includes lazy graph capture; outliers are preserved. Smaller limits yield modest cache increases, not a free48GiB pool. Exact byte classes follow in the separate diagnostic experiment.

Native suite:62 passed,2 skipped,4 environmental failures (missing Q2_0 PLE and experts.bin fixtures, unprivileged memlock). Python268 OK/7 skipped. These are not an all-tests-pass claim. No engine or weights were patched in this control. CMake4.3/Ninja1.13 differ from preserved build tooling; GCC15.2/CUDA13.4 and flags are recorded. Rebuilt control is the live comparator, not historical scores.

Clean shutdown by owned process group causes a frontend BrokenPipeError after all responses; server exit is cleanup, not an inference crash. No CUDA process remained.
