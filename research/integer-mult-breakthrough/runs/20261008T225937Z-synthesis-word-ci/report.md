# Bounded complete-word accounting verifier

The standard-library verifier passes complete h=4 scalar columns and dirty restoration, an omitted-subtraction scalar counterexample, ten graph-versus-chronological rank comparisons, dirty-endpoint and positive-transition omission controls, a degenerate L_E control and32 independent exhaustive binary mincut comparisons. It does not run many-label optimization or certify Gaussian operators, a native recursion, or an exponent.

See [check.json](results/check.json) for all five effective source hashes and the exact scope. Reproduce with `python3 -B research/integer-mult-breakthrough/code/synthesis/verify_word_frames.py`; optionally supply `--output` with a fresh ignored path. The original receipt remains unchanged in ignored `work/synthesis/20261008T230441Z-word-ci/check.json`.
