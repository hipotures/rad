# Descendant common cores and indefinite target complements

These are finite-frame screens in campaign `20261007T222521Z`, using immutable
upstream `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. They do not improve the
accepted support-envelope compiler. All authored source and exact small
evidence are retained because the indefinite construction establishes an
additional valid frame family, while the common-core screen isolates a loss
of useful cross-group reuse.

## Required descendant common coordinates

For a node, let `C` be the intersection of source triples, `V` their union,
and `A` the set of designated common points of all descendant partial outputs.
Every source triple contains `A`, so `A` is a nonempty subset of `C`. Along a
child-to-parent edge, `V` grows and `A` shrinks. The envelope `E(A,V)` imposes
equal coordinates `z` on `A`, total coordinate sum `3z`, and zero coordinates
outside `V`. Its restricted `I-J/9` norm is

    sum(outside-A x_j^2) + (|A|-1) z^2.

This is positive on the envelope, including the `|A|=1` case because the
total-sum relation determines `z` from the outside coordinates. Every
designated target intersects `V` only in its designated point in `A`, hence
the envelope is orthogonal to the physical target. Every input envelope was
checked to remain exactly its original triple line.

`finite_descendant_common_frames.py` also keeps `E(C,V)` below a support-size
threshold and switches to `E(A,V)` above it. Since support size cannot shrink
along original edges, these mixed labels remain nested. The imported
controller/compiler and its scalar and frame checks were unchanged.

| Ground | Threshold | Relaxed nodes | Compiled roles | Original support envelope |
| --- | ---: | ---: | ---: | ---: |
| 8 | 0 | 192 | 768 | 696 |
| 12 | 0 | 1,200 | 3,972 | 3,864 |
| 50 | 0 | 160,800 | 488,550 | 486,200 |
| 50 | 24 | 136,800 | 486,200 | 486,200 |
| 50 | 40 | 117,600 | 486,200 | 486,200 |
| 50 | 48 | 55,200 | 486,200 | 486,200 |

All six cases checked the complete scalar map, original-edge nesting, both
physical frame directions, source-copy lines and every designated target.
The small run also checked both dirty basis orientations. The large cases
took 56–62 seconds each with one BLAS thread. Widening all unshared stars loses
more old cross-group controller links than it creates; uniform thresholds
retain the original role count. Adaptive per-node choices remain unexplored
by this screen and are not excluded by the earlier fixed-source-core
dominance lemma.

The exact outcomes are in runs
`20261007T233730Z-finite-descendant-common-small`,
`20261007T233430Z-finite-common-threshold24`,
`20261007T233445Z-finite-common-threshold40`,
`20261007T233500Z-finite-common-threshold48`, and
`20261007T234800Z-finite-common-threshold0`.

## Exact descendant target-span complements

Let `T_n` be the rational span of all descendant physical target indicators
and `H=9I-J`. A new candidate label is `U_n=T_n^perp`. Descendant target sets
shrink along child-to-parent edges, so these labels nest. Ambient `H` is
nondegenerate for ground size other than 9. The label is nondegenerate exactly
when `T_n` is nondegenerate; it need not be positive.

The pinned manuscript `upstream/build/sections/03-motifs.tex`, lines 469–525,
defines projection along the orthogonal complement and uses nondegeneracy,
nesting and projector-difference rank. It does not require positive frames.
For nondegenerate `U` contained in nondegenerate `V`, the orthogonal
projectors satisfy `P_U P_V=P_V P_U=P_U`, so `P_V-P_U` is an idempotent of rank
`dim V-dim U`. The same implication gives reversed complement nesting.

`finite_target_complements.py` computes primitive integer bases and exact
rational Gram inertia. It falls back to the old positive envelope at every
degenerate target-span node and **all its original ancestors**: a suppressed
parent therefore has suppressed children. This is the required direction.
For a nonsuppressed parent and suppressed child, the child source envelope
is orthogonal to every descendant target of the parent, so it lies in the
parent's target complement. Every edge is also checked directly. Input
complements were independently required to equal the original triple line;
no nonlinear input kernel occurred.

| Ground | Degenerate target nodes | Suppressed ancestors | Indefinite frames | Roles | Positive envelope roles |
| --- | ---: | ---: | ---: | ---: | ---: |
| 6 | 0 | 0 | 0 | 162 | 150 |
| 8 | 0 | 0 | 0 | 792 | 696 |
| 12 | 270 | 490 | 3,210 | 4,110 | 3,864 |

All restricted frame Gram forms were exactly nonsingular. The h12 case had
490 positive fallback frames and 3,210 indefinite frames. Independent dense
elimination checked 687, 1,696 and 7,400 inclusion/reverse-complement pairs,
respectively. Each case also checked 50 exact projector differences for rank
and idempotence, every physical output pairing, both scalar dirty basis
orientations, and original source-line compatibility. The h12 run completed
in 24.21 seconds. No h50 dense run was justified after these negative counts.

The root compiler's returned descriptive field `nondegeneracy` still says
“Every retained frame has a common point.” That unchanged imported string is
not the certificate for these generic indefinite frames. Their authoritative
nondegeneracy evidence is the exact Gram inertia in this generator and the
independent projector checks; no verifier assertion was removed or weakened.

Evidence is retained in
`20261007T234700Z-finite-target-complements-small` and
`20261007T234730Z-finite-target-complements12`. A bounded reproduction is:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$PYTHON" research/integer-multiplication-bounds/code/finite_target_complements.py \
  --reference "$REFERENCE" --h 6 8 12 --independent --dirty \
  --output "$FRESH_OUTPUT"
```

`PYTHON` is the campaign math interpreter, with versions pinned in topic
configs; `REFERENCE` is an immutable checkout of the named upstream commit.
Run protocols contain exact source hashes and completed result hashes. The
next informative frame experiment is joint node-label/controller selection,
which could keep narrow frames where old links need them and widen only
selected following frames. This report makes no optimum claim over that
larger family.
