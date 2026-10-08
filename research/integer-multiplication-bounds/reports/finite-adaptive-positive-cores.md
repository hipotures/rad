# Joint positive common-core and controller choice

The earlier required-descendant-core threshold screens widened many nodes
and lost useful cross-group reuse. This screen chooses each eligible core
and controller link jointly. It uses campaign `20261007T222521Z` and upstream
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

For each unshared pair-star, a binary variable selects `E(C,V)` or `E(A,V)`,
where `C` is its source core and `A` its required descendant common-point
set. Original-edge nesting requires a wide child to have a wide optional
parent. Latent variables not used by conditional controller links are
eliminated via nearest relevant ancestry; the recovered wide choices are
propagated through every optional original ancestor and then checked on
every original edge.

The node order puts inputs first, then sorts by source support size,
decreasing source-core size and original ID. It is a legal order independent
of binary choices. For each possible same-controller link, all four narrow/
wide core combinations are checked exactly. A binary link variable is
forbidden for inadmissible combinations. Unit capacities enforce at most one
retained incoming controller at each previous gate and at most one
predecessor for each later user, as in the root compiler. The objective is
the actual number of retained links, hence actual physical roles.

`finite_adaptive_cores.py` uses SciPy/HiGHS MILP with one HiGHS thread. SciPy
reports that its unrecognized `threads` option is forwarded to HiGHS; this
warning is preserved in full logs. Recovered binary decisions and every
constraint are audited using integer arithmetic. Both the recovered MILP
plan and an independently recomputed maximum-flow plan for its chosen frames
are compiled and checked. The solver's optimality status is reported; no
standalone exact rational dual certificate is claimed.

| Ground/graph | Optional nodes | Relevant binary cores | Link candidates | Roles |
| --- | ---: | ---: | ---: | ---: |
| 8 all-last | 192 | 96 | 192 | 696 |
| 12 all-last | 1,200 | 120 | 528 | 3,864 |
| 16 all-last | 3,584 | 224 | 1,248 | 11,200 |
| 20 all-last | 7,920 | 360 | 1,880 | 24,320 |
| 50 all-last | 160,800 | 2,400 | 13,700 | 486,200 |
| 50 gap23 | 160,800 | 2,400 | 14,228 | 485,360 |

Every case returned zero chosen wide nodes and a closed solver gap. At h50,
the union of admissible links over both core choices is exactly the original
narrow envelope candidate set, so this family does not create additional
candidate links there. The old envelope counts are retained.

All complete scalar maps, both physical frame directions, all source lines
and physical target pairings passed. h8/h12 also passed independent dense
positive-envelope equivalence and every original-edge inclusion, plus both
dirty basis orientations. No h50 dirty test was required for this negative
family because the recovered circuit uses the unchanged narrow frames and
existing compiler.

Evidence runs:

- `20261008T000620Z-finite-adaptive-cores-small` (h8/12, independent+dirty).
- `20261008T000705Z-finite-adaptive-cores-medium` (h16/20).
- `20261008T000730Z-finite-adaptive-cores50`.
- `20261008T000730Z-finite-adaptive-gap23-cores50`.

A bounded replay is:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$PYTHON" research/integer-multiplication-bounds/code/finite_adaptive_cores.py \
  --reference "$REFERENCE" --h 8 12 --time-limit 30 --dirty --independent \
  --output "$FRESH_OUTPUT"
```

This is a scoped negative under the fixed legal schedule and two positive
core labels. It excludes neither other schedules nor indefinite frames
outside the common-core total-sum relation. The next branch selects exact
descendant-target complements only at nodes whose descendant targets share
one point; those target spans are positive and therefore nondegenerate, so
their complements provide a safe indefinite alternative without mixed-core
Gram degeneracy.

Complete row-level certificates are published as intact gzip evidence.
Local original JSON remains unchanged. Follow the topic reproduction guide
to restore missing JSON before running certificate-consuming commands.
