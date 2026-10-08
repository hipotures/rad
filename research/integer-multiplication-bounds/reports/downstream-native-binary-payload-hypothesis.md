# Binary address shears with fixed odd-prime payloads

This fresh hypothesis keeps the native address set binary. The entries of
the wire arrays use the fixed payload alphabet F3, or F5 in a control. A
payload symbol takes constant space; it does not turn an e-bit address
bank into a q-ary bank of volume q^e. No stronger movement exponent is
accepted by this report.

For a nondegenerate binary subspace U, let P_U be its orthogonal
projector. The frame acts on two binary address banks by

```
Phi_U(H,D) = (H + P_U D, D).
```

All additions in this address formula are in F2. For nested labels
V = U perpendicular E, the relative frame is Phi_E. Complementary source
and routed sink labels give P_U + P_(U-perp) = I. The unchanged scalar
common-frame argument therefore returns the complete word-XOR permutation
on every role, including arbitrary scratch. The source rank exception is
zero in this representation. The rational scalar circuit is reduced
modulo an odd prime only in its payload operations: its halves remain
units, its exact dyadic identity survives reduction, and its restored
scratch includes the center registers.

Every binary matrix A has an exact lower-lower Bruhat factorization
`A = E1 Pi E2`, with E1 and E2 invertible lower triangular and Pi a partial
permutation containing rank(A) ones. Applying E1 and E2 on the two banks,
then one word exchange at each pivot with the prescribed neighboring
word-XOR updates, realizes `H <- H + A D`. The executable verifies the
orientation and the complete final address permutation. This ideal
factorization does not establish a tape cost for the triangular updates.

The old linear scan lemma performs ordinary integer modular-affine
updates. It cannot be substituted for bitwise word-XOR. At width three,
XOR by the binary mask 010 gives the permutation
`[2,3,0,1,6,7,4,5]`. The control excludes all 32 unit-affine maps modulo
eight. This separates the two interfaces without claiming a lower bound
for other algorithms.

With the currently supported compact word-XOR, the new ideal rank count
only gives the recurrence

```
F(e) <= (s_complex / W_complex) F(e/m)
        + O(e^tau_old polylog(e)).
```

Since the forcing exponent tau_old is larger than the prospective complex
rank exponent, this bound does not improve native bit movement. A cheaper
triangular XOR, a count-preserving coupled phase construction, or a
proved amortized basis schedule remains necessary. The earlier negative
for an independent per-edge basis compiler is retained separately; the
Bruhat algebra avoids treating that compiler as a universal obstruction.

The fresh exact control passed 706 binary factorizations, 57,716 complete
joint binary addresses, all 1,019 dirty basis vectors of the h=8 scalar
invocation over F3, 16 additional arbitrary F3/F5 word probes, and 5,440
complete common-frame operator rows. It checks all scratch restoration
and endpoint signs. Host matrix and word operations in this tester are
references, not charged fixed-tape procedures.

Source: [downstream_binary_bruhat_payload.py](../code/downstream_binary_bruhat_payload.py).
Run: [20261008T033039Z-downstream-binary-bruhat-payload](../runs/20261008T033039Z-downstream-binary-bruhat-payload/).
The accepted R472879+h28 composition supplies immutable count metadata;
no finite graph is replayed. The original reference remains pinned at
bcd4ebde8692383539f8a48734e5fbf3a18a32c2. The campaign retains its original
start 2026-10-07T22:25:21Z and historical deadline 08:25:21Z, with the
explicitly authorized extension to 2026-10-08T10:00:00Z. No novelty or
unconditional multiplication claim is made.
