# Precision and recursive budget for Hadamard address routing

Status: exact algebra and a source-reviewed exclusion of the literal
per-residual basis-wrapper substitution. The
available completed complex kernel does not yet supply arbitrary selected
physical address masks independently of the bit router. No stronger saving
is promoted by this note.

## A long-record algebraic interface

Let S be fixed source bits, T a disjoint set of m target bits and
f(S) an m-bit word. Define the diagonal sign at an address by

```
Z_f(S,T) = (-1)^(f(S) dot T).
```

For Hbar=(1/2)[[1,1],[1,-1]], exact multiplication gives

```
Hbar_T Z_f Hbar_T = 2^(-m) P_f,
```

where P_f moves the payload at (S,T) to (S,T xor f(S)). A disjoint
CNOT matching takes f_i equal to its fixed source bit. The source bits
need not be distinct; they must avoid all simultaneous targets. A
coordinate permutation is a product of two disjoint swap involutions.
Three CNOT layers implement each swap involution, so six matching layers
use twelve Hbar calls and six address-sign scans. At most 3b bits of
normalization are restored for b address bits.

All Hbar factors and signs have maximum absolute row sum one. With
truncation error eta per completed Hbar call, a six-layer composition
before its final normalization has error at most 12 eta. Multiplication
by the final power of two amplifies this by at most 2^(3b). Thus storing
nonnegative Q-bit payload words as dyadic disk values requires only
P=Q+3b+O(log b) requested fractional bits to recover the exact permutation
by nearest-integer rounding. The inherited native semantic guard remains
a separate charge; it is not replaced by this elementary bound. Since
the campaign has Q much larger than b, the complex stream is still O(Q)
bits per payload. For one-bit payloads the same encoding would instead
enlarge the record, so this is specifically a long-record interface.

This establishes the arithmetic reduction. Computing the address sign is
charged metadata work and writing it is a payload scan. It does not prove
the physical availability or cost of the two selected-mask transforms.

## The available public layout contract

At pinned CrocSwap science source
43f59ff533598762cbc43a5e14af2bbbc76fabbd, upstream/build/sections/05-layers.tex
specifies consecutive equal K-bit address chunks, selecting one common
offset in each chunk. Its residual-basis changes invoke bit chunk
interchange, ordinary controlled rotations and exact bad-address repair.
The copied-center extension retains that analytic proof map and product
stock W_c^D_c W_b^D_b. Its precision bound C1=1 improves semantic width
without supplying an independent arbitrary-mask transform.

Consequently, gathering arbitrary selected bits with the bit router and
then applying Hbar does not remove the bit cost. The same issue remains
inside the native complex call if its basis changes still use that router.

## A direct self-routing substitution has a finite rank budget

A native residual basis change adds one selected row to another over all
f columns. Its target slot already has the required physical common-offset
layout. The exact identity above can replace one such row addition by two
Hbar calls, and hence two forward C calls with the retained phase wrappers,
on f selected axes. These are recursive children, not free linear scans.

Let R be the total number of such additions in all actually executed
forward and inverse basis wrappers in one native invocation. Under this
literal substitution, the characteristic rank mass changes from s to
s+2R. The inherited complex constants are

```
m = 784,
W = 537696432,
s = 421548223824,
m*W-s = 5778864.
```

A necessary condition for a sublinear complex-only recurrence is

```
s+2R < m*W,
R <= 2889431.
```

This also applies to a grouped child-width moment: when every child width
is less than its parent, a moment already at least one at exponent one is
strictly larger at any smaller exponent. Nonuniform child grouping does
not repair an exceeded rank-mass budget. No literal basis-instruction count
is retained by the inspected public profile, so R must not be read off its
rank histogram.

## A fixed-basis lower-bound discriminator

The following linear-algebra observation is independent of a compiler.
Let F have dimension h, let t_Y range over v distinct nonzero lines and
let V_(X,Y)=t_X^perp tensor t_Y have dimension h-1. Distinct ambient
spaces K_Y=F tensor t_Y intersect only at zero. Fix any one basis of
F tensor F. If a V_(X,Y) is spanned by a subset of that basis, at least
h-1 basis vectors lie in its K_Y. Each basis vector belongs to at most
one of the disjoint K_Y. Thus at most floor(h^2/(h-1)) Y groups can
contain any coordinate V_(X,Y).

For h=28 and v=3276, at most 29 Y groups qualify. Of the v^2 source
pairs, at least

```
(3276-29)*3276 = 10637172
```

have noncoordinate first-stage residuals of this form. The retained
two-stage frame actually grows Y from zero to
im(I-P_X) tensor im(Q_Y), which is exactly V_(X,Y). The eligible
notes/copied-centers-complex.tex states that all physical data fronts remain
and charges 4N rank-27 fronts; its center-copy modification leaves these
exterior calls in place. The scout independently checked this source
transfer, and the inverse agent inspected both pinned statements.

A literal P_M/C/P_M^-1 compiler needs at least one basis row addition in
EACH wrapper of every noncoordinate occurrence. This ONE front family
therefore needs at least 21,274,344 additions, adding at least 42,548,688
recursive rank mass. That exceeds the entire inherited deficit 5,778,864.
It rigorously excludes the literal substitution under one fixed global
coordinate basis; no unavailable instruction total is inferred from a
profile histogram. Persistent noncoordinate frames,
a changed finite network or fusion of adjacent wrappers fall outside the
literal substitution analyzed here.

## Provenance and reproducibility

The Hadamard routing proposal was supplied by the campaign layout agent.
The precision calculation, recurrence charge and disjoint-ambient-space
count here are the inverse agent's independent criticism. The pinned
complex constants are recomputed in the scout's
[changed-native-bridge-joint.json](../../scout/changed-native-bridge-joint.json).
The explicit first-Y front is in references/copied-centers/pr29/two-stage-16-note.tex,
section Two stages, endpoints and the copy correction. The unchanged
physical data fronts are charged in notes/copied-centers-complex.tex.
notes/copied-centers-assembly.tex describes the retained copied-center
semantic guard and product stock at the same science pin. Downloaded source
remains in ignored work/scout/snapshots/pr40-43f59ff53359.

The exact scalar control is [hadamard-routing-budget.json](../runs/20261008T1715Z-hadamard-budget/results/certificate.json),
regenerated by [check_hadamard_budget.py](../code/check_hadamard_budget.py).
It verifies the two-point identity and arithmetic budget; its originally
pending source-transfer flag is preserved unchanged. The completed source
transfer and stronger two-wrapper count are in the
[source-review receipt](../runs/20261008T1723Z-hadamard-source-transfer/results/certificate.json).
Neither receipt executes the all-size physical complex compiler.
