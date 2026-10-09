# A quantitative shared-release bound for coherent scalar words

Status: **SCOPED ALL-SIZE MATHEMATICAL LEMMA**, independently reviewed by two
research agents, with exact finite geometry and cancellation controls. The
scope is a constant-scalar virtual-bank model with common actual frames.
This is not a general arithmetic-circuit or integer-multiplication lower bound.

The earlier [zero-excess lemma](geodesic-transport-boundary.md) characterized
shortest paths. This extension allows arbitrary Lagrangian intermediate
frames and quantifies a shared defect space. It replaces a tempting per-output
release sum by a central fitting-rank requirement.

## Frame metric

Work over F2 in a symplectic space of dimension 2h. Fix the full diagonal
Lagrangian D. Identify its vector (t,t) with label t and write

```text
E(A)=A intersect D;
distance(A,B)=h-dim(A intersect B).
```

For any Lagrangians A and B,

```text
distance(A,B) >= dim E(A)+dim E(B)-2dim(E(A) intersect E(B)).
```

To prove this, put C=A intersect B. The sum E(A)+E(B)+C is isotropic: both E
spaces lie in D, and C is orthogonal to each because it lies in both endpoints.
Its intersection with E(A)+E(B) is exactly E(A) intersect E(B). Indeed if
a+b lies in C with a in E(A), b in E(B), membership in both A and B forces
both a and b into their common diagonal intersection. The sum has dimension

```text
dim E(A)+dim E(B)-2dim commonE+dim C <= h,
```

which gives the claim. Isotropy is essential; the verifier retains a
two-dimensional non-isotropic counterexample.

At a transition A to B, let ell=dim E(A)-dim commonE. The metric bound is
the diagonal dimension increase plus 2ell. Summing along every bank telescopes
the dimension increases, while retaining every downward or oblique loss.

## Coherent scalar model and the shared defect space

Let the source labels t be distinct odd binary vectors. In fixed virtual bank
bases, every bank has a row of source coefficients over a scalar field F.
Gaussian-dyadic coefficients may be relaxed to Q(i) for a lower bound. The
initial row on source bank t is e_t. Sink and arbitrary-dirty helper banks
initially have zero source rows; their independent dirty fields are separate.

A frame transition changes a bank's address frame and preserves its virtual
source row. A scalar shear, scale or swap is allowed at **the same actual
address operator**, and acts by constant F-coefficients on those rows. Equal
Lagrangian labels alone are insufficient. Address-dependent phases, residual
Pauli gauges between unequal actual operators, and operator-valued mixtures
are outside this scalar model. Their cost or semantics cannot be removed by
the following argument.

For a label subspace E, let V_E be the span of source units e_t for t in E.
Maintain one shared F-subspace Z of source rows. The invariant is

```text
row on bank A belongs to V_{E(A)}+Z.
```

It holds initially for the original one-line source anchors, zero sinks and
dirty helpers. Exactly common-frame scalar gates preserve it. A transition
with ell=0 has E(A) contained in E(B), so it also preserves it. At any transition
with ell>0, adjoin that bank's current row to Z. This raises dim Z by at most
one, preserves the invariant at the new frame, and only enlarges the permitted
space for all other banks. It uses the actual current row, including prior
cancellations. A zero row raises no rank.

Therefore

```text
dim Z <= number of loss events <= sum ell.
```

No separate defect space is created for every output. A single row in Z may
be used by many outputs. Arbitrary dirty-helper echoes and inverse words are
included as long as their scalar updates satisfy the stated premises.

## Endpoint fitting rank

Use the original endpoint geometry: source t goes from its one-line anchor
to full; sink s goes from zero to s-perpendicular; R dirty helpers go from
zero to full. With v sources and v sinks, the diagonal dimension baseline is

```text
B0=(2v+R)h-2v=Wh-2v.
```

If the complete source-to-sink map is the identity, the final sink row e_s
is an orthogonal-supported row plus z_s in Z. Put z_s into row s of K.
Then K has unit diagonal and every distinct odd-intersection entry is zero;
all its rows lie in Z. Consequently

```text
minrank_F(central fitting pattern) <= rank_F K <= dim Z;
total paid rank >= Wh-2v+2*minrank_F(central fitting pattern).
```

For the odd k=2d+1 subset family, the independently retained
[paired identity minor](central-minrank-and-field-boundary.md) supplies
`minrank >= binom(floor((h-1)/2),d)` over any field. The rational polynomial
factorization gives a different upper bound; its availability does not
implement a circuit attaining the release lower bound. At h=20,k=5 the
necessary single-copy excess is at least 72, while the polynomial center
rank is 190. This leaves substantial room for a shared central topology.

The lemma does not prove an additive two-rank penalty for each of v outputs.
It also does not prove that two ranks per central feature can be attained:
one loss event may drop many diagonal directions, so its actual price can be
larger than the defect-space rank.

## Tensor scope

For f address copies, use dimension hf and source subspaces T_t made of f
copies of the line t. Define V_E by complete containment of T_t in E. The same
proof gives excess at least twice the fitting rank. It does **not by itself**
multiply that lower bound by f: a loss of one diagonal direction can invalidate
containment of T_t and add one scalar row to Z.

If every frame transition is restricted to f repeated copies of the same
single-copy frame, each loss is f times an integer single-copy loss. In that
additional separable model, the argument gives excess at least 2f times the
fitting rank. Applying this stronger bound to arbitrary entangled hf-dimensional
frames would require another proof. Neither bound is a complete tensor native
child ledger.

## Exact evidence and independent review

The [new source](../../code/obstructions/coherent_release_bound.py) uses the
independent binary geometry generator and exact rational source-row algebra.
Four workers check every pair of Lagrangians through h=3, 4,096 seeded pairs
at h=4, and sixteen seeded cancellation words with arbitrary intermediate
Lagrangians. Every transition, shared-defect rank, exact endpoint decomposition
and complete rank sum is checked. The random words are not claimed to restore
all dirty fields or implement the final identity. Their endpoint matrix has
a corresponding fitting completion for its actual forbidden coefficients.

A separate full three-bank dirty echo exactly implements one odd self transfer
and attains baseline four plus excess two at h=2. Omission of unequal-frame
copy charges is rejected. The isotropy counterexample and distinction between
actual frames and labels remain explicit controls or model boundaries.

The [full attempt](../../runs/20261009T000203Z-coherent-release-bound/protocol.json)
finished in 2.213 seconds. Its [compact result](../../runs/20261009T000203Z-coherent-release-bound/results/full.json)
retains the exact counts, hashes and seeded word ledgers. Both independent
complex and synthesis agents reviewed the metric, invariant and fitting-rank
deductions and accepted them with the actual-frame and constant-scalar
restrictions. These reviews are internal research criticism, not formal
verification or external peer review.

## Next discriminator

The constructive [dyadic center basis](../complex/dyadic-center-null-basis.md)
can be consistent with this bound if a complete word concentrates nongeodesic
releases into a small shared space. Merely naming center coordinates does not
pay the scalar basis, source/sink adapters or frame losses. The next test is a
different central/side topology whose actual full child moment crosses the
target after those operations are included. Residual-gauge constructions are
a separate possible escape from the present model.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/coherent_release_bound.py \
  --workers 1 --bounded
```

The analytical argument and program were developed with OpenAI Codex assistance.
No new multiplication exponent is asserted.
