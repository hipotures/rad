# Recovery of the independent PR163 arithmetic parser

Status: **EXACT SOURCE RECOVERY AND SUCCESSFUL REPAIRED REPLAY**.
This is an implementation repair in the owned reviewer. It changes no
external input, mathematical formula, supplied bound or proof contract.

The [initial attempt](../../runs/20261009T081639Z-transfer-pr163-paid-review/report.md)
used source SHA256
`b16ab31dffc61c15b12e9ec7510741132897c463e9fd62b94eb28510bcaf81b7`.
It stopped before completing its certificate comparison because Python's
default 4300-digit integer-string limit rejected the pinned literal
scalar-gap field, which has 5899 digits. The exact stderr, original
configuration and immutable input/source pins are retained. This attempt
is classified as failed; it supplies no successful arithmetic result.

The repaired source is SHA256
`561299d8e28dae2d0610e81a1920aec85cd6dfb5270a8bba1ee59602535a4b92`.
It imports `sys` and sets a bounded 10000-digit parser limit in `main`.
The mathematical fixture remains SHA256
`36e66dc1e4424d2a0ccca1ad2bcf34699edc47cd8cafc0ae8e6d1be2089a224e`.
No floating-point fallback or smaller local-stock replacement is used.

The [recovery patch](../../fixtures/transfers/pr163-review-parser-recovery.patch)
has SHA256
`443004bdb21fbe2f3c80896cc0469e68b5dea1c085b1122b7c8cb77703444f30`.
It transforms the repaired source into the failed source. Applying it
with `patch --batch -p1` to an isolated copy recovered the failed bytes
and their hash exactly. The retained receipt identifies both versions,
the fixture and the checked command. Thus the earlier source can be
reconstructed even if its ignored local snapshot is lost.

The [fresh repaired attempt](../../runs/20261009T081900Z-transfer-pr163-paid-review-repair/report.md)
passes the complete finite scalar/group/row arithmetic, all 47 selected
strict inequalities, seven margins, atom toll and five matched parameter
rows. It uses four workers and imports no external implementation.
The source remains unchanged after the run. The external conditional
kappa and all-size obligations retain the scope stated in the
[independent mathematical review](pr163-paid-balanced-transfer-independent-review.md).
Successful parser recovery is not verification of those external theorems.

Portable bounded replay:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/pr163_balanced_transfer_review.py --workers 1
```

The complete runtime closure is the owned reviewer, the immutable compact
mathematical fixture and standard-library Python. The external complete
source remains obtainable at the fixture's pinned Git commit. Original
attempts, configuration bytes and stderr are preserved without replacement.
