# Independent review of the alternating quadratic phase interface

The alternating residual construction in
[alternating-quadratic-phase.md](alternating-quadratic-phase.md) is valid
as a replacement for an individual nondegenerate alternating edge
residual. It uses exactly r ordinary f-axis complex children for a
rank-r residual. Its fixed-tape overhead has the retained compact-control
movement exponent. The proof below supplies the actual spaced-bit scan,
selected-only paired permutation and guard accounting that were still
proposed in the producer report. No odd-ground complete finite network,
shared matching or improved multiplication exponent is established by
this review.

Review date: 2026-10-08. The frozen producer report has SHA256
`53d2dcf748bd6a2269d05e79d4bd673dff5ea2511ce90905aed9864d648dd803`.
The interfaces are those of CrocSwap/integer-mult-bounds at
`6e564879f51ae16f23d392e9e196c605f36d90df`, with its original exact
phase construction inherited from
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. Originals are unchanged.

## Algebra on every ambient coset

Let E be a nondegenerate alternating subspace of binary Euclidean
space F2^m, of rank r. Its vectors have even Hamming weight and r is
even. The orthogonal projector P is symmetric and idempotent. In
particular P_ii = e_i dot P(e_i) = P(e_i) dot P(e_i) = 0. Choose
a symplectic basis U with Gram J consisting of paired exchange blocks.
Define Q(a)=wt(Ua)/2 modulo two. Hamming-weight polarization gives

```
Q(a+b)=Q(a)+Q(b)+a^T J b.
Q(a)=sum_i l_i a_i + sum_pairs a_(2i)*a_(2i+1),
l_i=wt(Ue_i)/2 mod2.
Arf(Q)=sum_pairs l_(2i)*l_(2i+1) mod2.
```

The last equality follows by multiplying the two-coordinate Gauss sums.
Thus the finite constant Arf sign and the fixed linear coefficients are
computable when preparing the residual basis; no variable-size oracle is
needed.

For the retained ambient frame
`C_E=H_m diag_z(i^wt(Pz)) H_m`, write the Fourier summation variable
uniquely as z=Ua+y with y in E-perpendicular. Summation over y vanishes
unless the address difference lies in E. When that difference is Ud,
the remaining sum is

```
2^-r sum_a (-1)^(Q(a)+d^T J a)
=(-1)^(Arf(Q)+Q(d))*2^(-r/2).
```

Translation a to a+d proves the identity. Every ambient E-coset has
this same kernel, and distinct cosets have zero connecting entries.
An arbitrary invertible extension of U can therefore label its cosets;
the extension is not required to preserve the dot product. This proves
the all-input operator identity

```
C_E = P_M [(-1)^Arf(Q) D_Q H_r P_J D_Q tensor I] P_M^-1.
```

Here P_M changes address coordinates, D_Q is the sign diagonal, and P_J
exchanges the paired coordinate names. It is not a replacement of J by
the identity Gram. The displayed real kernel is self-inverse. For nested
nondegenerate U0 subset V=U0 perpendicular E, projection decomposes
orthogonally and Hamming weights add modulo four. Consequently both
`C_V C_U0^-1` and its reverse are precisely C_E. Also
`C_U0perp C_U0=C_full` remains valid. The formal endpoint telescoping and
the two orientation interfaces do not acquire a missing sign.

For f columns put N=rf and Q_f=sum_j Q(a_j). The ordinary complex
kernel C=((1+i)I+(1-i)X)/2 satisfies

```
H_N=i^(-N/2) S C^tensor N S,
S(a)=i^wt(a).
```

Since r is even, N/2 is an integer, the scalar is a fourth root, and
all coefficients are Gaussian dyadics. Implementing C^tensor N as r
successive ordinary C^tensor f children supplies exactly r rank-counted
children, all on the retained size f. No call on an enlarged rf-axis
group, irrational scalar, free gather or altered shrink factor is used.

## Actual complete-field scan

The original `05-layers.tex` layout has m consecutive banks, each
containing f chunks of the round's supplied common width K. The selected
position is rho+jK in bank a. It has fK physical bits, rather than f
contiguous selected bits. Other complete prefix, front, back and
spectator fields intervene, and the outer row index may have arbitrary
mixed cardinality. Each fixed row nevertheless supplies a complete
within-row address rectangle. The balanced transform uses a different
supplied K for different groups, but all banks in one group still have
the same K and rho.

Prepare one full fK-bit counter tape per bank and one fK-symbol mask
tape, whose symbol at j is one exactly when j modulo K equals rho.
All their heads remain aligned to the same physical position j. An
ordinary complete-address counter also traverses the spectator fields.
When its binary carry toggles a bank bit, advance all aligned heads to
that bit's within-bank position. Read the mask there. At a selected
bit of active bank a the update is

```
Q_f <- Q_f xor l_a xor current partner-bank bit,
wt_selected <- wt_selected + 1 - 2*old_bit mod4.
```

The partner is the fixed J-mate of a, read under its aligned head.
Unselected chunk bits and complement banks do not change either phase
accumulator. Their actual counter symbols are still toggled. At the
end of an increment return the heads to zero. Passing a bank boundary
also returns them from its last position to zero before traversing
another bank. No partner bit at distance f or fK is read by a random
seek. A sequential mask removes any need for division by K at every
record. Its construction and all counters take O(p) setup symbols.

An increment with carry length l costs at most 2l moves on the global
counter and at most 2l on each aligned tape, including bank resets.
Over N_rec complete consecutive binary addresses the total toggles are
below 2*N_rec. Thus the counter traffic is O(N_rec) with a fixed
number of tapes determined by the fixed finite motif. The argument is
unchanged if physical lexicographic order visits the banks in the
opposite order; it only relabels the fixed carry sequence. Spectators
before, after or between banks are included in the global carry.
Initialization at a new outer prefix row costs O(p), bounded by that
row's coefficient traffic. No power-of-two assumption on its outer
row cardinality is used.

Use the upstream volume convention: **V is logical bit volume**. Each
coefficient record has O(p) bits, and sign changes and real/imaginary
exchanges cost O(p) per record. The full diagonal therefore costs O(V),
including aligned counter movement and initialization. The producer's
`Vp` display is consistent if its V instead counts coefficient records;
with the upstream bit-volume convention there is no extra p factor.
This clarification is in this follow-up; the producer report is frozen.

## Paid paired permutation and unchanged guard

P_J swaps the selected f-bit words of each paired bank. It must preserve
the K-1 unused bits in every chunk. For one pair use exactly three
compact selected-word row additions:

```
y <- y xor x; x <- x xor y; y <- y xor x.
```

The retained compact-control proposition applies in either physical
order of x and y. The existing reserved front and back fields are
complete for every ordered pair, remain outside the row partition,
and are restored before the next shear or child. With r fixed this is
a fixed number of calls, with cost O(V*((f*log p)^tau+1)). It neither
swaps whole fK-bit banks nor requires an additional selected-bit gather.
The original Gaussian elimination implements P_M and P_M^-1 with a
fixed number of the same row additions. Direct coordinate-map controls
below check their algebra; their fixed-tape realization uses this
retained theorem rather than a new unmeasured adapter optimization.

One alternating edge can be executed in this order: right D_Q, P_J,
right S, r ordinary children, left S, left D_Q, constant unit
`(-1)^(f*Arf)*i^(-rf/2)`. Each D_Q costs at most one coefficient sign;
each S costs at most one sign and one multiplication by i; the constant
unit costs at most two such operations. There are at most eight extra
elementary coefficient operations per alternating edge. A nonzero
alternating edge has r>=2, so their count is at most s/2 when s is the
sum of all residual ranks. The additional charge is at most 4s.

Under the retained scalar-gate bound, the original 24W^3, inverse
wrappers 4s and endpoint/bank corrections 4W+4 can therefore be bounded
together by

```
24W^3+8s+4W+4 < 64*(W+m+1)^3 = E,  s<Wm.
```

The same large E still suffices. Unit phases preserve the coefficient
grid and modulus, and selected address permutations restore complete
encodings before arithmetic resumes. Ordinary children still return
exact C^tensor f on arbitrary coefficients. Thus the accepted semantic
guard recurrence `A(e)<=A(e/m)+s*e/m+E` and its linear whole-layer guard
remain valid for a fully verified network incorporating these edges.
A new scalar schedule must separately verify the stated gate bound.

The resulting edge overhead, with bit-volume V, is

```
r ordinary f-axis calls + O(V*((f*log p)^tau+1)) + polynomial setup.
```

Summing over a fixed network preserves its existing rank-weighted time
recurrence. The whole-network scalar identity, forward/reverse physical
frame transitions, arbitrary dirty input contract, source/sink signs
and shared-stage matching are still independent obligations. This review
does not automatically validate an odd-h shared complex motif.

## Independent controls and counterexamples

[review_alternating_phase.py](../code/review_alternating_phase.py) imports
no producer. A general binary Gram-system solver builds the projectors;
integer Walsh sums test every ambient difference, including zero support
outside E. A second pipeline uses Gaussian-integer numerators, selected
word shears and ordinary two-point C kernels on actual spaced chunk bits.
It compares against direct embedded E-convolution on arbitrary complex
integer data and a complete small input basis. The counter experiment
uses symbol tapes for the complete physical address, all bank bits and
the mask, explicitly charging their head movements. Comparison phases
are recomputed independently from the integer address.

The [fresh run](../runs/20261008T033809Z-review-alternating-phase/) passed
441 distinct alternating planes and three higher-rank spaces, 49,672
ambient differences, of which 47,812 must vanish between cosets, 8,512
operator output values, 243,200 complete spaced-counter addresses across
11 configurations, and both nested orientations and complement endpoints
in three explicit configurations. It includes f=2, offset zero and the
last chunk position, nonadjacent active banks, multiple symplectic pairs,
and nonempty spectator intervals. The operator pipeline tests ordinary
children and physical selected-bit permutations; it is not a full large
finite network replay.

Three exact boundary witnesses are retained. The plane
`span{110,101}` has Arf one: its diagonal kernel is -1/2, whereas
omitting Arf gives +1/2. With K=2,rho=1, physical address one changes
only an unselected chunk bit; treating that bit as a selected coordinate
incorrectly changes Q from zero to one for this plane. Swapping whole
two-bit banks would move that address from one to four; the selected-only
paired permutation correctly leaves it at one. These explain why the
sign, mask and selected-only shears are required.

Reviewer source SHA256:
`e88707928f8289a3f20bb06ba25a7b7b9a5290ec48a5ae7e4caa8a70a4661c08`.
Certificate SHA256:
`09c31c6610babbb4294936043e5b357d790f1d3148652a88f4ceb3cdf1d4cb88`.
Seed 607, Python 3.14.4, one worker, 1.08 seconds elapsed, 23,664 KiB
peak RSS. The protocol records source/producer hashes, exact command,
actual 03:36:32 UTC start, immutable original campaign start,
historical deadline and the authorized 10:00 UTC extension. Its
descriptive run name is not an authoritative start clock. The owned
CPU reservation was released in finally; no job was interrupted.
