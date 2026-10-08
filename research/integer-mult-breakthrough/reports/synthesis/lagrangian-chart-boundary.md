# A graph-completion criterion for full Lagrangian frame gains

**Status: EXACT STRUCTURAL LEMMA AND FINITE RANK-METRIC CERTIFICATE. No scalar circuit, dirty wrapper or exponent improvement is claimed.**

The complex track found a four-terminal common-frame example whose best cost is 6 among symmetric graph frames and 5 among all Lagrangian frames. This independent certificate verifies that example without importing the discovery code and proves a criterion explaining when the larger representation can help. A strict gain requires terminal intersections to jointly generate a direction outside the graph chart.

## Abstract model and constructive lemma

Write the binary symplectic space as pairs (x,y) in F2^n times F2^n, with pairing

```text
<(x,y),(x',y')> = x dot y' + y dot x'.
```

Let V be the vertical Lagrangian `{(0,y)}`. A symmetric matrix A defines the graph Lagrangian `G_A={(x,Ax)}`. Graphs are exactly the Lagrangians transverse to V. The abstract Fourier-rank distance is

```text
d(L,G) = n - dim(L intersect G).
```

Let S be an isotropic subspace with `S intersect V=0`. Then **S is contained in a symmetric graph**. Conversely, a subspace containing a nonzero vertical vector cannot be contained in any graph.

For the constructive direction, choose a basis of S as columns `(X,Y)`, where X and Y have n rows and r columns. Transversality gives rank(X)=r; isotropy gives the symmetry of `X^T Y`. Extend the columns of X to an invertible n-by-n matrix T. Specify the first r columns of C by `C[:,1:r]=T^T Y`. Its upper left block is `X^T Y`, hence symmetric. Specify the first r entries of its remaining columns by symmetry and choose the bottom right block zero. Thus C is symmetric. Set

```text
B = T^(-T) C T^(-1).
```

B is symmetric and `BX=Y`, so G_B contains S. The construction uses exact binary row operations and keeps the entire coordinate dimension.

Now fix graph terminals G_i and any Lagrangian candidate L. Define

```text
S = sum_i (L intersect G_i).
```

S is isotropic because it lies in L. If S has no nonzero vertical direction, its graph completion G_B contains every `L intersect G_i`. Therefore

```text
d(G_B,G_i) <= d(L,G_i) for every i.
```

This conclusion also holds for every positive weighted sum of the terminal distances. Consequently a strict improvement of the full-Lagrangian optimum over the graph optimum requires every improving candidate's joint intersection span S to contain a nonzero vertical direction. This condition is necessary for a strict gain; a vertical direction alone does not establish that a gain exists.

The statement is an all-dimension algebraic lemma. The finite controls below verify the implementation and example, not the proof by extrapolation.

## Independent four-terminal witness

Encode a vector as `x + 2^n y`. For n=3, the four supplied symmetric graph matrices have upper-triangle binary codes 3,23,35,56, with coordinates ordered `(0,0),(0,1),(0,2),(1,1),(1,2),(2,2)`. Their canonical low-pivot bases in this independent checker are

```text
G0 = span(25,10,4)
G1 = span(57,42,28)
G2 = span(25,10,36)
G3 = span(1,50,52).
```

The candidate `L*=span(25,10,32)` is isotropic of dimension three. Its distances to these terminals are (1,1,1,2), of total 5. Their intersections with L* are

```text
S0 = span(25,10)
S1 = span(57,42)
S2 = span(25,10)
S3 = span(51).
```

The sum is L* itself and contains the vertical vector 32. An explicit cross-terminal generation is `25 XOR 57=32`; each summand belongs to a different terminal intersection. Thus retaining all these intersections inside one graph is impossible.

The checker independently enumerates all 64 symmetric graph matrices and all 135 three-dimensional Lagrangians. The latter enumeration examines every triple among the 63 nonzero six-dimensional vectors, keeps exactly the independent isotropic spans, and deduplicates their exact canonical bases. Every Lagrangian has such a basis, so this covers the complete finite model. The optimum costs are exactly

```text
minimum among symmetric graphs: 6,
minimum among all Lagrangians: 5.
```

The full model has exactly one minimizer at cost 5. This is a 1/6 local rank-metric reduction for this four-incidence problem. It is not a measured machine speedup, integrated controller saving, or improvement of the integer-multiplication exponent. The finite symplectic labels also do not specify all residual Gaussian phase choices of physical representatives.

## Controls and interpretation

Four workers completed the independent certificate in approximately 0.27 seconds:

- 512 exact isotropic partial-space graph completions each at n=4,5,16, including every possible dimension through randomized independent basis choices.
- Random four-terminal candidates at n=4 and5: 881 transverse joint spans were completed into graphs with no increased terminal distance. The other 143 joint spans contained vertical obstructions; no optimum conclusion is inferred for those samples.
- Complete graph/Lagrangian optimum enumeration for the supplied n=3 witness.
- Nonisotropic and explicitly vertical partial spaces are rejected by the graph-completion implementation.

All randomness is reproducible from seeds recorded in the protocol. The random cases supplement the constructive theorem; their frequencies do not estimate the occurrence of strict optimal gains under any research distribution.

This result identifies a concrete restriction to lift. Searching only symmetric graph frames misses at least one abstract optimum. It also supplies a cheap filter: if a proposed nongraph candidate's terminal intersections remain jointly transverse, an equally good graph is constructible and the larger representation has not helped that gate.

The complex track is binding its discovery to a literal four-incidence linear shear with a paid Gaussian-dyadic representative. That is the next separate verification obligation. A useful integrated result must supply its scalar map, endpoint and phase lifts, source/sink maps, dirty restoration, complete child histogram, movement/precision charges, and a contracting recurrence. This independent rank certificate supplies none of those missing interfaces. The earlier stationary-intertwiner and fixed-chronology negatives retain their original scopes and do not prohibit this changed geometry.

## Reproduction and provenance

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/lagrangian_graph_completion.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-RUN/results
```

- [Independent source](../../code/synthesis/lagrangian_graph_completion.py).
- [Protocol, all exact optimum distributions and controls](../../runs/20261008T221011Z-synthesis-graph-completion/results/).
- The witness was discovered by the complex-track [Lagrangian median screen](../../code/complex/lagrangian_phase_screen.py) and supplied as integer bases/codes. This independent checker imports no complex-track code. The completion argument, implementation, and internal review were developed with OpenAI Codex. No external novelty or formal-verification claim is made.

Only standard-library Python is required. The ignored original receipts remain in `work/synthesis/20261008T221011Z-graph-completion/results`; the durable copy retains all essential complete optimum counts, seeds, source hash and controls.
