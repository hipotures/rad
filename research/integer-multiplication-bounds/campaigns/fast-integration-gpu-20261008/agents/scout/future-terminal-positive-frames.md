# Reachable terminal constraints and signed positive frames

This note supplies an address-space lemma for the proposed compiler that uses
future terminal obligations. It does not establish a new physical network or
an integer-multiplication exponent. The independent controls are recorded in
[`gpu-parameter-results/future-terminal-positive-frame-kernels-20261008T2212.json`](gpu-parameter-results/future-terminal-positive-frame-kernels-20261008T2212.json).

Fix a common coordinate (c). Write

\[
\Gamma_c=\{x:\sum_i x_i=3x_c\},\qquad
K_{c,a,b}=\Gamma_c\cap\{x:x_a+x_b=0\}.
\]

For a set of required future ordinary terminals, make a graph on the
coordinates other than (c), with edge \(\{a,b\}\) for every required terminal
\(K_{c,a,b}\). The correct universal space is the intersection of all these
terminal spaces. No premise that the payload array is a ridge function is
used. The separate arbitrary-array counterexample to a free terminal gauge
change remains valid; see [the array scope note](dense-terminal-array-transfer-scope.md).

On a connected bipartite component choose signs \(\sigma_i\in\{1,-1\}\)
that change across every edge. The equations force all outside coordinates
in that component to have the form \(t\sigma_i\). The component therefore
contributes one independent column, with outside entries \(2\sigma_i\),
core entry \(\sum_i\sigma_i\), and zero entries elsewhere. The core entry
follows from \(2x_c=\sum_{i\ne c}x_i\). An isolated coordinate is a one-vertex
bipartite component and contributes a column. In a component with an odd
cycle, propagation forces \(t=-t\), so the component contributes no column
over the rationals. These observations prove completeness as well as
containment in every required terminal.

The signed columns are positive for the inherited form \(H_0=I-J/9\).
For every \(x\in\Gamma_c\),

\[
x^T H_0x=\sum_i x_i^2-\frac{(\sum_i x_i)^2}{9}
=\sum_{i\ne c}x_i^2.
\]

The right side is positive for a nonzero vector in \(\Gamma_c\). Columns of
different components have disjoint outside supports, so their \(H_0\) Gram
matrix is diagonal and positive. Thus the intersection admits the same
exact signed positive-frame projector formulas already used for actual
compiled words.

The result gives both an opportunity and a precise obstruction. A connected
bipartite graph on excluded coordinates can retain one signed direction
that an original cover would set to zero. A complete graph on at least
three excluded coordinates has an odd cycle and retains none there. This
does not rule out sparse future cones, alternative scalar circuits, shared
producers, or different physical allocations.

If a producer's required future terminal set contains a consumer's set,
the producer intersection is contained in the consumer intersection.
This is a subspace monotonicity statement. A compiler must still establish
every actual operand inclusion, insertion chronology, role allocation,
scalar source support, dirty restoration, endpoint and paid transition.
An equal or smaller subspace count alone proves no cost or role saving.

The independent check exhausts all 64 graphs on four outside coordinates,
then tests 128 separately seeded graphs at dimensions 23 and 25. It computes
the exact rank of each literal constraint matrix by Fraction Gaussian
elimination, tests every column against every constraint, computes all Gram
entries, and checks every positive source triple containing the common
coordinate. The 192 cases cover 32,832 source-line controls. In each case,
a source triple is contained exactly when both its outside vertices avoid
all required future terminal pairs. The graph proof above establishes the
general lemma; the finite controls test its implementation.

From the campaign directory, reproduce the compact receipt at a fresh path:

```bash
python3 agents/scout/code/check_future_terminal_positive_frames.py \
  --seed 202610082212 --random-cases 64 --output "$FRESH_RECEIPT"
```

The inherited terminal, copied-center and physical array framework comes
from Avi Eisenberg's interval-strip/pair assembly in PR #62
(`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`) and eumemic's joint-frame
compiler in PR #57 (`cd350f76c9bc01489ec83568bded532cb69be938`), together
with the directly credited predecessors in the pinned sources. This
AI-assisted lemma and its independent checker extend the current campaign's
signed positive-frame work. They make no claim that the complete inherited
construction originated here.
