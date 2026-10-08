# Alternating residuals through exact quadratic phases

## Question and status

The accepted even-ground complex construction excludes nondegenerate
alternating binary residuals because they have no norm-one basis. That
is an interface obstruction, rather than a degenerate frame or a wrong
scalar D/E identity. This new hypothesis replaces that interface by a
symplectic Gaussian phase. Exact finite algebra passes; the written
fixed-tape argument below is a proposal awaiting independent review.
No stronger multiplication exponent or odd-ground network is promoted.

The [fresh exact source](../code/alternating_quadratic_phase.py), SHA256
`ba11f29e1f40033bbe2ca37a7167ef8352e6d6ea19fc2f3bd55025ec4202b9b6`,
is frozen. The [completed run](../runs/20261008T030740Z-alternating-quadratic-phase/)
exhausts all 441 distinct alternating planes in ambient dimensions 3..7
and 18 higher-rank or multi-column cases, with 219,024 exact matrix entries.
It uses seed 109 and integer Gaussian pairs, independently evaluating
ambient Fourier sums and bilinear Walsh coefficients. Its certificate
SHA256 is
`96c719e58b3c431e4c2a4d788a75ba2eae6b4e83ba3ea40aa92576f36457d0dc`.
Producer time is 1.652 seconds; this is an algebra control, not a full
finite-network or multiplication-machine implementation.

## Exact operator identity

Let E be a nondegenerate alternating subspace of binary Euclidean space
F_2^n. Its rank r is even, every vector in E has even Hamming weight,
and its orthogonal projector P is symmetric, idempotent and has zero
diagonal. Choose a symplectic basis U with Gram matrix J, whose 2x2
blocks exchange paired coordinates. Define

```
Q(alpha) = wt(U alpha)/2 mod2.
```

Its polar form is B_Q(alpha,beta)=alpha^T J beta. Therefore
Q(alpha+beta)=Q(alpha)+Q(beta)+alpha^T J beta. The signed Gauss sum is
sum_alpha(-1)^Q(alpha)=(-1)^Arf(Q)*2^(r/2).

Use the same original ambient operator
C_E=H_n diag(i^wt(Pz)) H_n, where H is the normalized binary Walsh
matrix. Orthogonal-complement characters make its kernel zero between
different E cosets. On one coset its exact matrix is

```
C_E(alpha,beta)=(-1)^(Arf(Q)+Q(alpha+beta))*2^(-r/2)
              =(-1)^Arf(Q) D_Q H_r P_J D_Q,
```

where D_Q(alpha)=(-1)^Q(alpha) and P_J exchanges paired coordinate
names. The identity follows by translation in the nondegenerate Gauss
sum; it is not an assumption about orthonormal vectors. It remains valid
on arbitrary input coefficients and on every complement coset.

For f columns put Q_f=sum_j Q(alpha_j) and n_child=rf. The ordinary
coordinate complex kernel is C=((1+i)I+(1-i)X)/2. With
S(alpha)=i^wt(alpha), its exact tensor identity is

```
H_(rf)=i^(-rf/2) S C^(rf) S.
```

Since rf is even, all displayed scalars and coefficients are Gaussian
dyadics; no irrational square root needs to enter a fixed-width record.
Consequently C_E^(f) has a factorization through one ordinary C^(rf)
tensor and unit diagonal phases. Equivalently C^(rf) can be executed as
r ordinary C^(f) children, one per coordinate bank. This latter form
preserves the existing rank-weighted recurrence. The algebra alone does
not prove a cheaper variable-shrink recurrence or a free pivot gather.

The Arf sign is necessary. In ambient dimension 3, E=span{110,101} has
Q=1 at all three nonzero vectors and Arf=1. Its (0,0) kernel entry is
-1/2; omitting the sign gives +1/2. This counterexample is preserved in
the certificate.

## Proposed paid-record phase implementation

The ambient frame dimension m and chosen r are fixed finite network
constants; f is variable. After the existing invertible binary frame
adapter, use r banks of f selected address bits. The ambient complement
banks remain spectators. Unit phases act on coefficient records by sign
changes and real/imaginary exchanges, costing O(p) per O(p)-bit record.

A complete address scan can maintain Q_f and wt(alpha) mod4 without
recomputing all f columns per record. Keep one f-bit counter tape per
fixed coordinate bank, with their heads aligned to the same column.
Toggling bit a in column j changes Q_f by
Q(e_a)+sum_b J_ab alpha_(b,j). Read the fixed number of aligned bank
bits, update the one-bit Q accumulator and the mod4 weight accumulator,
then advance all counter heads along the carry and return them. The
aggregate binary carry length over a complete bank-major enumeration
is O(number of records); resetting or overflowing a bank costs O(f)
only once per 2^f values. A fixed number of counter tapes therefore
gives O(Vp)+polynomial setup, rather than O(Vpf). Prefix fibers reuse
the same tapes. Initialization costs O(p) per fiber and is charged to
its complete record traffic. These are sequential counter-head moves,
not random memory reads of partner bits at distance f.

The separate [aligned-counter source](../code/quadratic_phase_counter.py),
SHA256 `508a1175e44186b28395b8985d243e63713368cec16eeb01b6a79969a40dba65`,
checks this exact diagonal scan on 457,412 complete addresses across
18 configurations, including nonadjacent selected banks and complement
spectators. Its symbol-list counters charge every aligned-head move.
Each phase equals a separately recomputed quadratic/hamming value;
total bit flips are below 2V and head moves at most 4mV. Seed: 209;
elapsed: 1.486 seconds. The [completed control](../runs/20261008T032000Z-quadratic-phase-counter/)
is targeted evidence for this new scan, rather than a replay of earlier
accepted networks. Its actual start time is recorded in the protocol;
the descriptive run ID is not an authoritative campaign clock.

The paired-coordinate permutation P_J exchanges a fixed number of
complete f-bit banks. Pay its cost with the accepted bit movement
primitive and the actual coefficient record width. It may alternatively
be incorporated into the right frame adapter, but that optimization
requires an explicit compiler certificate. An arbitrary invertible
fixed-m binary adapter decomposes into a fixed number of word shears
and bank exchanges. These are the same paid movement operations used
by the existing phase interface; the symplectic Gram is not replaced
by the identity.

Thus a candidate alternating phase interface has r old-size complex
children and overhead of the existing movement exponent,

```
r*A(f) + O(Vp*((f*log(p))^tau+1)) + polynomial setup.
```

No extra recursive child is required by the unit phases. This accounting
still requires independent confirmation of the actual word-shear
adapter, endpoint chronology, coefficient growth and additive guard
constant. It does not assert that a single C^(rf) recursive call can
replace those r children at a better cost. Direct diagonal phases and
coordinate permutations do not alter arbitrary dirty coefficient
scratch; the complete new finite network must nevertheless check its
whole input/output contract, including the signed Gauss factors.

## Discriminating next experiments

The already identified odd h9/h11 pair-helper terminal residuals are
nondegenerate alternating planes. Check this new factorization on those
actual residual embeddings and on forward/reverse endpoint operators.
Then screen unshared odd-ground D/E constructions with the same rank
sum. Odd shared stages additionally need an explicit triple matching
with even intersections and a valid join residual; the previous xor1
matching applies only on even ground sets. Complete finite identities,
frame transitions and guard transfer must precede any exponent claim.

The current campaign identity and start are unchanged. During this
experiment the user authorized extending the deadline to 2026-10-08
10:00:00 UTC (12:00 CEST), superseding the historical 08:25:21 UTC end.
