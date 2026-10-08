# Sparse repair with source-closed buffers

Status: a written support/movement lemma and independent finite controls.
Gaussian accuracy and the direct band-LU precision lemma are separate
obligations. This does not by itself establish a multiplication exponent.

## Targets, source packets and charged copies

Let every regular tensor kernel have physical radius R, and take cell side
lambda with R/lambda=O(d^-3). Two grids are translated by lambda/2 in every
coordinate. A point failing both grids lies in a face strip of grid0 on one
axis i and a face strip of grid1 on a DISTINCT axis j. Same-axis intersection
is empty when4R<=lambda. Include O(1) rounding margins for fractional forward
cores; require sigma*lambda/2-1>2R in that case.

Create one packet for every ordered pair(i,j) and its two coarse cell labels.
Both constrained coordinates are expanded by their actual source radius R;
all other coordinates are complete. A source face field has width at most4R
per cell, up to fixed rounding constants. The SUM of packet source volumes,
including every duplicated copy, is at most

`C*d*(d-1)*(R/lambda)^2*V = O(d^-4 V)`.

This is stronger than bounding only the union of output targets. It does
not multiply that density by(1+2R/lambda)^d: every unconstrained axis in each
packet is already complete. Overlapping pair packets are explicitly charged.

For inverse phase-edge outputs add full slabs for each axis with centered
phase distance at most delta=d^-4 from an edge. Expand their constrained axis
by R_exception=O(d^(17/2)); their other axes remain complete. Each phase pocket
has length Theta(delta/theta)=Theta(d^12), so this expansion preserves
O(delta) one-axis density. The sum of all such source packets is O(d^-3 V).
Separate original-period cut slabs of widthO(lambda_F+R_F+lambda_I+R_exception)
have superpolynomially small density, because each physical period exceeds
every fixed power of d and Q. Forward cuts cannot be covered by the much
smaller inverse phase pockets.

For the forward operator all row stencils have radiusR_F. For the inverse,
regular destination rows use radiusR_I and exceptional rows useR_exception.
Regular bad-grid packets exclude exceptional destinations. This distinction
is essential: expanding their two constrained faces by the much larger
R_exception could make regular repair volume essentially full.

## One payload scan, then paid ordinary sorts

Read the original payload once. Its nested coordinate counter determines
all expanded-packet membership predicates; emit one copy for every matching
packet, together with its packet label and coordinate address. Bounds above
charge the SUM of these emitted copies. Conservative predicate cost
O(d^2 b^2) bits per record is dominated by Q=Theta(d^18) for epsilon>1/2,
where d=Theta(b^epsilon). This statement permits arithmetic on metadata;
it does not assume constant-time floor, division or address lookup.

Use an ordinary fixed-tape merge sort to make the currently processed axis
contiguous in every packet. Each sort reads/writes the emitted Q-bit payload
and costs O(V_sparse*b). There are at most d axis stages. The final sort by
original output address and merge into the retained regular grid stream have
the same charge. Thus movement costs

`O(V_sparse*d*b)=O(V*b/d^2)=O(V)` for epsilon>1/2,

up to smaller logarithmic terms. Record n or V here already includes Q-bit
coefficients; multiplying this cost by Q again would double charge payload.
The packet keys use a fixed number of tapes; the number of packet labels is
data, rather than a growing number of physical tapes. Give every repaired
target a deterministic smallest eligible packet owner; only that owner's
result is returned. Extra packet computation and duplicate sources are paid.

## Do not crop all dimensions after each axis

For a final destination set B and separable finite row operators A_i, let E_k
be B expanded by source stencils only in axes k+1,...,d. Read E_0, apply A_1
and retain E_1, then A_2 and retain E_2, until E_d=B. Each destination in E_k
has every required input in E_(k-1). A stencil radius is chosen using the
FINAL destination row of that axis. This remains true for phase-dependent
row stencils. Tensor operators on distinct axes commute exactly, but their
intermediate support does not permit premature cropping in unprocessed axes.

Rectangular packet bounds can instead retain larger Cartesian E_k; the same
containment proof and source volume charge apply. For phase slabs, free axes
are complete, so their full inverse passes consume no extra halo volume.
The constrained axis uses a finite principal window with a proved resolvent
error, rather than pretending that discarded cyclic sources are zero.

## Arithmetic remaining inside repair

Forward and regular-inverse one-axis kernels use ordinary polynomial-size
overlap windows and conventional integer convolution. Q and window sides
are polynomial in b, so normalized arithmetic costs polylog(b) per payload
bit. This invokes a conventional unconditional multiplication bound, rather
than the desired improved multiplication oracle.

For phase-exception inverse repair the raw physical correction matrix is
near identity and can be truncated to half-bandwidthw=O(sqrt(Q/u))=O(sqrt d).
Direct band LU costs O(w^2) Q-bit arithmetic per coefficient. Across at most
d stages its normalized charge is
`O(d^-3*d*w^2*polylog(b))=O(d^-1*polylog(b))`.
The inverse branch is checking pivot, roundoff and truncation details.

## Exact finite controls and limitations

The independently authored checker
[sparse_tensor_repair.py](../code/sparse_tensor_repair.py) uses integer,
row-dependent band operators in seven different2/3/4-dimensional periodic
boxes. It compares source-closed sparse evaluation against a complete
rectangular address oracle and direct nested tensor sums. It imports no
Gaussian producer or historical repair implementation.

The completed certificate records119,616 full records,69,960 repaired
destinations and42,352 direct tensor terms. Every source containment and
charged-copy bound passes. Deliberately cropping to final targets after each
axis disagrees at68,595 destinations. Small boxes have large exception
fractions; these tests establish finite identities, not asymptotic density.
No tape machine or Gaussian all-size theorem is certified by the finite PASS.

Reproduce from this campaign directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
 code/sparse_tensor_repair.py --workers 7 \
 --output work/fresh-sparse-repair/certificate.json
```

The source digest and
per-case sizes, exact checks and elapsed seconds are in the compact result.
Sparse support and packet accounting are campaign-derived; locality,
Gaussian factors and conventional merge sorting are credited separately.
