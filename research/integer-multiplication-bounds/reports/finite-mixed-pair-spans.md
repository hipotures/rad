# An exact frame criterion for mixed two-point source sums

## Scope

This lemma extends the source-span audit beyond sums with a common point.
It applies to sums combining both members of a fixed pair. It supplies exact
nondegeneracy tests for such graphs, including explicit degeneracies that a
scalar optimizer must avoid. It does not by itself improve the multiplication
bound or assert that a whole compiled mixed-source graph passes the transfer.

The setting is the pinned rational form `I-J/9` on triple indicators. Let
`A={a,b}` be a fixed pair, and let `Gamma` be an edge graph on points outside
`A`. Its aggregated scalar inputs are

```text
y_uv = x_{a,u,v} + x_{b,u,v} for each edge {u,v} of Gamma.
```

Let `U_Gamma` be the rational span of every source triple indicator in this
aggregate family. Source ancestry, rather than a numerical scalar test, defines
the frame. The exact criterion is

```text
U_Gamma is nondegenerate iff
  sum over nonbipartite connected components C of |C|
  + sum over bipartite connected components C of 4*l_C*r_C/(l_C+r_C)
  != 8.
```

Isolated vertices are omitted. Here `l_C,r_C` are the two bipartition sizes.
The same sum being less than 8 is equivalent to positive definiteness of the
source span. Values larger than 8 give a nondegenerate indefinite span.

## Derivation

Put `d_A=e_a-e_b` and `p_A=(e_a+e_b)/2`. For a nonempty graph, the difference
of the two source indicators on any edge is `d_A`, and their average is

```text
p_A + e_u + e_v.
```

The difference line has positive squared norm 2 and is orthogonal to all
average indicators, both for the Euclidean form and the original `I-J/9`.
Let `W_Gamma` be the rational column span of the unsigned edge incidence
vectors `e_u+e_v` on outside coordinates. Every average-source combination
has the form

```text
p_A * sum(v)/2 + v, with v in W_Gamma.
```

The original inner product on two such combinations is

```text
v dot w - sum(v)*sum(w)/8.
```

Thus `U_Gamma` is an orthogonal direct sum of the positive difference line
and `W_Gamma` equipped with `I-J/8`. All quantities are rational; no
finite-field lift is used.

Since the Euclidean form on `W_Gamma` is nondegenerate, the matrix determinant
lemma gives singularity of this rank-one update precisely when the squared
norm of the Euclidean projection of the all-ones vector onto `W_Gamma` is 8.
Connected components have disjoint coordinates, so their projection norms add.

For each component, vectors in the Euclidean orthogonal complement of its
unsigned incidence span obey `z_u+z_v=0` on every edge. An odd cycle forces
`z=0`, so a connected nonbipartite component contributes its full number of
vertices. A bipartite component's orthogonal complement is the line taking
values `+1,-1` on its two sides. Its projection norm is

```text
l+r - (l-r)^2/(l+r) = 4*l*r/(l+r).
```

This proves the displayed criterion and the rank formula used by the checker.
For a connected nonbipartite component the unsigned incidence rank is its
vertex count; for a bipartite component it is one less. The mixed source span
has the sum of these ranks plus the one difference line.

## Exact independent checks

The checker selects original triple vectors by rational Gaussian elimination,
forms their integer Gram matrix (entry `intersection_size-1`), and evaluates
its determinant using checked fraction-free elimination. This calculation is
independent of the connected-component criterion. All 18 retained examples
agree with the criterion and its exact dimension prediction.

| Source edge graph | Projection norm squared | Result |
| --- | ---: | --- |
| Clique on 7 outside vertices | 7 | Positive definite |
| Clique on 8 | 8 | Degenerate |
| Clique on 9 | 9 | Indefinite, nondegenerate |
| Complete bipartite 1 by 7 | 7/2 | Positive definite |
| Complete bipartite 3 by 5 | 15/2 | Positive definite |
| Complete bipartite 4 by 4 | 8 | Degenerate |
| Complete bipartite 3 by 6 | 8 | Degenerate |
| Complete bipartite 6 by 6 | 12 | Indefinite, nondegenerate |
| Two disjoint cliques on 4 vertices | 8 | Degenerate |

The tests also include cliques on 3 through 6, 10 and 12 vertices, complete
bipartite 2 by 6 and 4 by 5 graphs, and a triangle plus a complete bipartite
2 by 3 component. The latter confirms that component contributions must be
added before applying the singularity threshold.

## Circuit application being screened

A target containing a full global pair, `T=A union {c}`, has two old partial
contributions from common points `a,b`. Their disjoint sum is

```text
sum over {u,v} outside A, c not in {u,v} of y_uv.
```

It is therefore a single-vertex exclusion map on the aggregated pair inputs.
The contribution from common point `c` remains unchanged. The experimental
whole graph globally interns its new sums against the existing paired graph
and across different choices of `A`, then removes dead nodes. Every output
coefficient is checked exactly before its role count is compared. Every new
source node without a common point is screened using this lemma.

This remains a circuit-search application, not a transferred witness. In
particular, a zero determinant at any active node invalidates the unchanged
nondegenerate source-span transfer until a replacement frame argument is
supplied. An indefinite but nondegenerate span is allowed by the pinned
complement-frame lemma; positivity is a sufficient condition rather than a
mandatory one.

## Reproduction and recovery

- [Exact frame checker](../code/finite_mixed_spans.py).
- [18-case certificate](../runs/20261007T225030Z-finite-mixed-spans/results/certificate.json).
- [Whole mixed-output scalar screen](../code/finite_mixed_circuit_screen.py).

```bash
python3 research/integer-multiplication-bounds/code/finite_mixed_spans.py \
  --output /tmp/mixed-pair-span-checks.json
```

The frame checks use only the Python standard library and took 0.027 wall
seconds. The whole scalar screen additionally imports read-only scripts from
the pinned CrocSwap reference commit. All code and compact results are
deterministically regenerable; no irreplaceable inputs or external package
dependencies are required.
