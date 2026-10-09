# Odd-cube reflections and the single-Clifford boundary

**EXACT FINITE EVIDENCE AND ANALYTICAL OBSTRUCTION.** The majority reflection
on every odd cube of dimension at least five is not a single Clifford
operation. This excludes a particular frame implementation. It does not
exclude a paid scalar word mixing a fixed number of banks in one common
physical frame, and supplies no multiplier exponent.

## Reflection, parity encoding and exact kernel

Let `k=2r+1`, and let `Pi_r` project onto Walsh characters of degree at most
`r` on the `k`-cube. Define `K_k=I-2Pi_r`. Its Fourier eigenvalues are `-1`
at weights at most `r` and `+1` otherwise, so it is a real symmetric
involution. For two addresses at Hamming distance `d`, its entry is

    1[d=0] - 2^(1-k) sum_(t=0..r) sum_j (-1)^j C(d,j) C(k-d,t-j).

The summation ranges retain every valid binomial term. This is the direct
low-degree projector calculation, independent of a proposed bank word.
For odd `k`, complementing a Fourier index reverses its eigenvalue. Pairing
each index with its complement therefore makes every even-distance kernel
entry zero. The transform exchanges the even and odd parity sectors.

Encode a source as `(u, parity(u))` and a target as
`(v, 1+parity(v))`, with the final bits taken modulo two. Their distance is
`t+1-(t mod 2)`, where `t=wt(u+v)`. The opposite-parity block `Q` is thus an
XOR-circulant matrix on `k-1` bits. Direct Walsh transformation gives

    Q = 2^(-(k-1)) W diag(s(alpha)) W,
    s(alpha) = -1 if wt(alpha)<=r, +1 otherwise,

where `W` is the unnormalized Walsh matrix. In the parity order, the full
reflection is `[0,Q;Q,0]`. This equality describes the mathematical input
and output labels. A physical implementation must separately pay its
frame transitions and readout association; the equality does not grant a
free bank permutation or address transform.

For `k=3`, the nonzero radial entries are `-1/2` at distance one and `+1/2`
at distance three. For `k=5`, they are `-3/8,+1/8,-3/8` at distances
one, three and five. The unequal magnitudes are suggestive, but the Pauli
argument below is the actual Clifford obstruction.

## All-size Pauli obstruction

A Clifford operation must conjugate each Pauli operation to another Pauli.
In Fourier coordinates, `Z_j` toggles the index bit `j`. Conjugating by the
diagonal sign `s` attaches the phase

    s(alpha) s(alpha+e_j) = -1 exactly when wt(other index bits)=r.

A monomial Pauli with that fixed toggle has an affine-character phase,
`(-1)^(a dot alpha+c)`, up to a constant unit. For `r>=2`, the displayed
phase is `+1` at zero and at every unit vector in the other coordinates.
An affine character with these values is identically `+1`. A vector of
weight `r` has phase `-1`, a contradiction. Both the full reflection and
its parity block fail the Pauli condition. Conjugation by the Walsh
Clifford does not change this conclusion.

For `r=1`, the phase is parity on the remaining one or two bits. Indeed
the three-dimensional full sign and the two-dimensional block sign are
quadratic Boolean phases, giving the familiar Clifford case. This proof
uses the Pauli definition and exact phase values; it is not a numerical
classification or a general linear-circuit lower bound.

## Complete finite discriminator

[The standalone integer producer](../../code/obstructions/odd_cube_clifford_boundary.py)
constructs both kernels without importing any other campaign producer.
For `k=3,5,7,9`, it checks every XOR-circulant Gram shift, every Fourier
eigenvalue, every opposite-parity source/target entry and the complete
first row of `K Z_0 K`. Circulancy makes the Gram-shift check a complete
matrix orthogonality check. One changed kernel coefficient must fail.

| Cube dimension | Full matrix size | Nonzero entries in conjugated Pauli row | Parity-block row support |
| --- | --- | --- | --- |
| 3 | 8 | 1 | 1 |
| 5 | 32 | 8 | 8 |
| 7 | 128 | 32 | 32 |
| 9 | 512 | 128 | 128 |

The complete attempt started at `2026-10-09T08:34:48 UTC`, requested four
workers and took `0.0877251` seconds. Its exact source identity, commands
and unchanged source receipt are in
[the run](../../runs/20261009T083448Z-odd-cube-clifford-boundary/report.md).
There is no sampling, random seed, external solver or native timing claim.
The complex-primitives agent independently reviewed the sign-derivative
argument and accepted this scope; that is internal mathematical review,
not formal verification or external peer review.

From the repository root, use a new output directory:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/odd_cube_clifford_boundary.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/odd-cube/results
```

The bounded `--workers 1 --bounded` command checks `k=3,5` and needs only
this source and standard-library Python. The next research question is
whether a fully paid larger-cube bank word and side chronology can still
improve the complete moment. This obstruction requires that extra cost
to be explicit rather than replacing it with one Clifford frame.
