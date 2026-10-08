# Dirty trimmed-zeta realization and a scoped monotone-frame obstruction

**Status: exact characteristic-zero scalar realization and exact finite rank audit of one declared compiler. A nonmonotone physical circuit and a multiplication exponent remain open.**

The coordinator's truncated Yates circuit evaluates the five-subset side kernel with substantially fewer arithmetic operations than independent weighted trees. This experiment makes its arbitrary-dirty scratch implementation explicit and checks a natural frame compiler. Four mixer passes reuse one stock of SSA roles. The tested monotone frame compiler nevertheless has zero total rank deficit: each output retains its own label until a final rank descent spends the boundary saving.

## Scalar circuit and reusable dirty stock

For five-subsets T,U of an h-element label set, the side coefficient depends on t=|T intersect U|. Its values at t=0,...,5 are

```text
(-3/8, 0, 1/8, 0, -3/8, 0).
```

The Newton coefficients are `(-3/8, 3/8, -1/4, 0, 0, 1)`. The last coefficient is essential: omitting the identity feature leaves a nonzero self coefficient. The coordinator's [trimmed_side_transform.py](../../code/obstructions/trimmed_side_transform.py) first computes truncated downward features, applies the nonzero weights, and assembles upward outputs. Mathematical zeros and aliases belong to that clean scalar DAG; they are not assumed to be available as free physical zeros.

Allocate one arbitrary-dirty auxiliary for every authored SSA node, including the original input nodes. An addition node c=a+b is implemented by the invertible shears `c+=a; c+=b`; a scale node c=alpha*a by `c+=alpha*a`. Let M be this topological mixer and J scatter its final output roles to the data sinks. For independent input data x and arbitrary initial auxiliary d, the complete scalar word is

```text
M; -J; M^-1; inject x; M; +J; M^-1; subtract x.
```

The first `M;-J;M^-1` subtracts the dirty output contribution. The second adds that contribution plus the desired map of x. All auxiliary columns return to d, all source columns return to x, and the sinks receive exactly the side transform. A nonunit dyadic coefficient is allowed in an additive shear because its inverse only negates the coefficient; no division by that coefficient is required.

There are four mixer passes, but they reuse the same R physical SSA auxiliaries. The total stock is `W=R+2v`, where `v=binom(h,5)`. The exact scalar shear count is `4*number_of_mixer_edges+4v`, including both scatters and both data injections. This does not establish a native tape layout, a frame chronology, or a recursive invocation count.

Every source, sink, and arbitrary-dirty column was replayed over rational numbers for h=8 and h=9. Both positive replays passed. Reversing the first echo's sign and omitting the final source subtraction each produce an explicit single-column counterexample; these four negative controls passed too.

| h | v | Reused SSA auxiliaries R | Complete stock W | Paid scalar shears |
|---:|---:|---:|---:|---:|
| 8 | 56 | 1,066 | 1,178 | 8,156 |
| 9 | 126 | 2,075 | 2,327 | 15,912 |

## The frame family includes degenerate support spaces

Use the symplectic space of binary pairs `(x,y)` with pairing `x dot y' + y dot x'`. The zero and full graph frames are respectively `{(a,0)}` and `{(b,b)}`. For any binary subspace E, define

```text
L_E = { (a+b,b) : a in E^perp, b in E }.
```

This is an h-dimensional Lagrangian even when E has a radical. Its intersection with L_F has dimension

```text
h - dim(E+F) + dim(E intersect F),
```

and therefore its distance is `dim(E)+dim(F)-2dim(E intersect F)`. If `E subset F`, the distance is simply the difference in dimensions. No nondegenerate chart assumption is used. The complex track independently derived the same family and its zero-to-full geodesic characterization.

For an odd-weight top label t_T, the source endpoint is `E=span(t_T)` and the side-output endpoint is `E=t_T^perp`. These endpoints agree with the conventional rank-one projector and complementary-projector graph frames because `t_T dot t_T=1`.

## Declared monotone compiler and exact telescope

The audited geometry starts every auxiliary at zero. It moves the input auxiliaries to their one-dimensional source labels. At each mixer shear, both participating roles are moved to the union of their current support subspaces; these frames are retained for subsequent uses. Every output then moves to its prescribed `t_T^perp` endpoint, every auxiliary finally completes to the full frame, and both data boundary completions of rank h-1 are charged.

This is an optimistic endpoint/support telescope. It counts one source-span growth and one completion, rather than supplying a literal chronological Gaussian address word for all four scalar mixer passes. Copy, scatter, echo, return, gauge and tape obligations still need an integrated compiler. The certificate's phrase "complete local rank ledger" means complete stock and endpoints for this optimistic geometry; it must not be read as an actual complete physical invocation histogram. The coordinator independently reviewed the scalar echo and raised this distinction.

Let D be the sum, over outputs, of the dimension lost when intersecting their retained frame with their prescribed kernel. The total rank charge telescopes exactly to

```text
R*h + 2D + 2v*(h-1) = W*h - 2v + 2D.
```

The top identity route ensures each output retains its own t_T. Since that label is not in `t_T^perp`, each output loses at least one dimension, hence `D>=v`. This compiler's rank charge is therefore at least `W*h`. For all four tested h values, every output reaches the full h-dimensional subspace and then loses exactly one dimension. The charge equals capacity.

| h | v | R | W | Rank charge = W*h | Full-width calls |
|---:|---:|---:|---:|---:|---:|
| 8 | 56 | 1,066 | 1,178 | 9,424 | 464 |
| 9 | 126 | 2,075 | 2,327 | 20,943 | 816 |
| 20 | 15,504 | 167,537 | 198,545 | 3,970,900 | 46,609 |
| 24 | 42,504 | 442,262 | 527,270 | 12,654,480 | 118,452 |

The complete rank histograms are retained in the certificate. Same-width calls are admitted and their stock ratios are below one; rejecting them categorically would be incorrect. The zero deficit itself prevents a positive exponent improvement for this local histogram: at a=0 the moment equals one, and at every positive a the width-weighted moment is larger, because this histogram contains proper smaller-width calls.

This is an abstract optimistic ledger for the declared retained-SSA monotone geometry. Further obligations can only worsen its nonnegative rank deficit if the same geometry is retained, so it already rejects that restricted construction. It is not an arbitrary-frame lower bound, a native Gaussian phase-word certificate, or a full integrated multiplier recurrence. Logical support containment is a property of this geometry, not a requirement on all possible gate frames. Nonmonotone choices, joint cancellation before separate output materialization, changed scalar words, and other complete source/sink geometries remain outside the result.

## Reproduction and next discriminator

From the repository root, run:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/trimmed_zeta_dirty_probe.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-TRIMMED-DIRTY/results
```

Only Python's standard library is required. The four workers perform two complete scalar-column replays and two large exact frame audits. The original run took approximately 13.65 seconds. Its effective-source hashes, deterministic cases and worker count are in the [protocol](../../runs/20261008T223911Z-synthesis-trimmed-zeta/results/protocol.json); the [certificate](../../runs/20261008T223911Z-synthesis-trimmed-zeta/results/certificate.json) contains the histograms and corruption witnesses. Original JSON remains unchanged under ignored `work/synthesis/20261008T2240Z-trimmed-zeta/results/`; the historical shortened directory name is retained explicitly rather than implying a second run.

The next discriminator is a joint nonmonotone gate-frame optimization of an actual cancellation word, including all physical roles, the essential identity route, and every source/sink boundary. Independent per-output retirement or omission of the identity term does not answer that question. The dirty compiler and rank telescope were developed with OpenAI Codex; this report claims no external novelty, formal verification, or new kappa.
