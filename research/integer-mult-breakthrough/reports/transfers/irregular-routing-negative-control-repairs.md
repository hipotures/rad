# Preserved negative-coverage repairs for the irregular route

Status: **EXACT SOURCE RECOVERY AND FINITE CONTROL COVERAGE**. The positive
route is unchanged across all three producer versions. Two guard-branch
attempts failed a required omission-negative check. Their evidence remains
immutable; neither is relabeled as a successful run.

The original producer SHA256 is
6ba8cb48e71b03a54c9e36620999472d7d3ae2bc68ca15702169ff5c898f2b81.
It passed the first bounded attempt `20261009T091337Z-transfer-irregular-route-first`
and the four-worker ordinary full attempt
`20261009T091732Z-transfer-irregular-route-full`. The same source then failed
`20261009T091732Z-transfer-irregular-shapes-full`: the first sixteen random
inputs per width did not reliably expose an endpoint error when exceptional
repair was omitted. The seeded positive inputs had completed before the final
required-negative assertion; the failed run has no successful certificate.

Repair attempt `20261009T092159Z-transfer-irregular-negative-repair` inserted
a separate deterministic fallback address with selected action zero, first
control value three, second control zero, and zero unselected/guard planes.
The resulting producer is
40f90303265f8531e15f10d66c631b4655404cd76f6b2ebd88bc881885b6e29e.
Its four-worker run `20261009T092349Z-transfer-irregular-shapes-repair` again
failed the required-negative assertion. In f=4 the omitted corrections could
corrupt intermediate words and still cancel at the completed endpoint. An
intermediate failure is not a substitute for a discriminating complete-word
negative.

Repair attempt `20261009T092605Z-transfer-irregular-adversarial-repair` changed
only the fallback's first selected bit of the second control to one. The final
producer is
fbc75032544670ec60c00e43753b2d3bc139a464d9ed91b9b0fd4b77c8f179c3.
The corrected input passes with repair and its true inverse. Without repair
the f=4,K=10 full endpoint differs: the expected address is
618970020219713839706406912 and the wrong endpoint is
1765123311542848828231717974061839499083101574271330690831502640473965056.
The final four-worker attempt `20261009T092728Z-transfer-irregular-shapes-final`
and both current bounded attempts `20261009T094203Z-transfer-irregular-route-bounded`
and `20261009T094203Z-transfer-irregular-shapes-bounded` pass.

The shape wrapper is unchanged throughout, SHA256
dda0edb3353727ebe140347ab5b3e0fbced0677f39d3a5179ff38dcffab13060.
Both imported packed-component sources are also unchanged. All failed original
launch protocols, nonzero return codes, logs and tracebacks are retained.
Inspection used temporary in-memory instrumentation; it did not rewrite a
completed producer or result. The two repair receipts record patch recovery
and the distinction between the fixed positive algorithm and repaired controls.

## Exact ordered recovery

Starting with the current producer in a separate disposable directory, apply
these recovery patches in order with `patch --batch -p1 -i <absolute-path>`:

1. [Adversarial-input recovery](../../fixtures/transfers/irregular-router-adversarial-recovery.patch),
   SHA256 134da34f2d2a3a4d2c513ccefdf6f8c5e8e08b386af49865fdc33af629477d2e,
   restores intermediate 40f90303265f8531e15f10d66c631b4655404cd76f6b2ebd88bc881885b6e29e.
2. [First-negative recovery](../../fixtures/transfers/irregular-router-negative-recovery.patch),
   SHA256 0131b31115b1805ccb52a69ea3ad0f8f1c93b510f649dd5c82953ff4a87ac89d,
   restores original 6ba8cb48e71b03a54c9e36620999472d7d3ae2bc68ca15702169ff5c898f2b81.

The path within both patches is
`research/integer-mult-breakthrough/code/transfers/irregular_activity_router.py`.
Do not apply them to the active research worktree. Both single-step and ordered
two-step hashes were checked in fresh isolated recovery trees. Because the
patches contain only negative-control changes, the original successful inputs
and positive word are recoverable without retaining a downloaded source tree.
Recovery of the original sources is exact; their negative-coverage failures
remain failures when replayed with their original configurations.

For the full mechanism, limitations, paid native bill and reproduction commands
see [the main report](irregular-activity-routing-and-transfer.md). This package
does not prove a fixed-tape runtime, supply a shorter zeta word, or claim kappa.
