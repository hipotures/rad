# Reviewed phase inverse and singleton circuit composition

Campaign `20261007T222521Z` remains active until its immutable deadline
2026-10-08 08:25:21 UTC. This checkpoint supports the strict conditional
bound

    T(n) = O(n (log n)^(1-kappa)),
    kappa = 4819020256931 / (5 * 10^29).

The saving exceeds `5.555952085351 * 2^-59`, and in particular exceeds
`11/2^60`. This combines changed finite and analytic constructions, followed
by exact strict parameter tuning. The retained complete upstream theorem
and unaffected machine interfaces remain assumptions. A full multiplication
machine and a machine-checked proof of that theorem were not implemented.

## What changed

The finite bit construction uses uniform ground 50 with the aligned
singleton placed at position 23 for common points 0 through 47, and at
position 24 for common points 48 and 49. Positive support envelopes and
retained controller chains reduce its side roles from 486,200 to 485,360.
Its parameters are

| Quantity | Exact value |
|---|---:|
| Side roles per invocation | 485360 |
| Retained controller links | 8170 |
| Tensor dimension `m` | 125000 |
| Data triples `N` | 7529536000000 |
| Physical roles `W` | 388009283200000 |
| Decreasing rank `L` | 2881200000000 |
| Deficit `D=N-2L` | 1767136000000 |
| Edge rank sum `s=Wm-D` | 48501158632864000000 |
| Deficit fraction `eta` | 23/631262500 |

The independently replayed complete graph contains 63,562,800 partial
scalar coefficients, 434,730 disjoint physical additions and 465,760 fresh
copies. The review checks all 454,330 logical labels and 2,709,640 physical
forward/reverse frame transitions. Small cases separately check complete
dirty shears and full three-stage exchange. See
[singleton construction](finite-singleton-gaps.md) and
[independent full witness](review-singleton-witness.md). The latter records
the initial missing-NumPy environment failure and successful pinned replay.

The Gaussian inverse partitions into constant-phase cells. Each interior
is diagonally similar to a Toeplitz block. Four short convolutions apply
its Gohberg--Semencul inverse; a circular banded Schur system handles the
cell boundaries. Exact setup is reused across tensor lines. Residual-based
rounding controls completed maps without an exponential number-of-cells
penalty. Its fixed tapes, precision, normalization, guard, prime and partial
cell interfaces passed [independent all-size review](review-phase-cell-inverse.md).

The final small improvement retains the global chunk factor outside the
packed recurrence's geometric sum. Its correct stopped-leaf lower bound
gives an exact rational balance, with a full
[independent recurrence review](review-packed-unrolling.md). The gain from
this last estimate alone is about three parts per billion; the much larger
improvement comes from the phase inverse and finite construction.

## Verification and scope

The phase-only composition gives `9638040483941/10^30`. Its independent
adapter replay checks 32 strict conditions in each of optimized and
conservative modes, all four cutoffs, and all 120 other supplied motif
ceilings. The best supplied pair is now 50/50/50. The old 52/48/52 motif
has lower saving under these reviewed models.

The exact-unroll composition gives the headline above. Its independent
adapter reuses the separately authored full packed verifier, executes 960
complete stopped recurrence controls, recomputes the primitive logarithm
enclosures with longer independent series, and bounds all 120 alternative
guard-family ceilings. This establishes dominance within the declared
11-by-11 finite grid and reviewed guard/recurrence family. It is not an
optimum over all label geometries, circuits, movement algorithms or
integer multiplication methods.

The common explicit cutoff is

    log2(b) >= 6132477715457, where b = ceil(log2(n)).

The BHP prime theorem's eventual threshold and retained interfaces impose
additional eventual cutoffs. The bound is asymptotic, with no practical
runtime implication at available input sizes. Arithmetic and finite
verification confidence is high; all-size analytic claims are manually
reviewed mathematical arguments rather than a formal proof. Literature
priority for the overall construction has not been established.

The original complex h50 primitive is retained in this checkpoint. A new
complex side construction and indefinite bit frames are fresh hypotheses,
excluded here until their full transfers are independently accepted.

## Evidence and reproduction

Terminal producer and review runs are:

- `20261008T001933Z-singleton-phase-composition`
- `20261008T002337Z-review-singleton-phase`
- `20261008T002445Z-singleton-packed-composition`
- `20261008T002539Z-review-singleton-packed`

The previous unchanged-grid phase composition and independent review are
`20261008T000209Z-asymmetric-phase-repaired` and
`20261008T000519Z-review-asymmetric-phase`. Their failed serialization
attempt and exact old source are preserved separately. The finite input
is `20261008T000730Z-finite-singleton-transfer`; the full independent
singleton replay is `20261008T002315Z-review-singleton-witness`.

[Reproduction instructions](../reproduce.md) give ordered fresh-output
commands. All exact input/source hashes, settings, commands and terminal
logs are retained in the run protocols and gzip evidence. Downloaded
sources, environments and numerical NPZ files remain external with recovery
manifests. The campaign clock has not been reset.
