# Transform fusion across normalization interfaces

Status: **FINITE EVIDENCE** and exact finite counterexamples. A useful positive
representation identity is established in an auxiliary finite-field model.
No Gaussian-dyadic circuit, fixed-tape implementation, recurrence saving or
larger kappa is claimed.

## Hypothesis and expected leverage

A different coupling might keep intermediate values in a redundant coefficient
representation, defer normalization, and cancel an adjacent inverse/forward
transform pair. This would change executed operations, unlike relabeling
children in an unchanged positive recurrence.

For a breakthrough, fusion must remove a growing factor from the complete cost
ledger or change its child moments. Saving a fixed number of transforms only
changes a constant. A possible large gain would require one representation to
remain valid through an increasing number of recursive interfaces, including
the operations that form the next child's numerical digits. No such all-size
interface is established by this investigation.

## The exact normalization boundary

Let `F` be an invertible transform on coefficient vectors and let `C_B` carry
nonnegative coefficients into canonical base-B digits. The original boundary
is `F C_B F^-1`, rather than `F F^-1`. Removing the two transforms and retaining
the same spectrum is legal only when `C_B` acts as the identity on the actual
data domain, or when subsequent consumers explicitly accept the redundant
representation and final recovery pays for normalization.

One retained exact case at base four has inputs `[3,1]` and `[3,2]`. Direct
polynomial multiplication gives `[9,9,2]`; canonical carrying gives
`[1,3,0,1]`. Both evaluate to 77 at base four. Their length-four finite-field
spectra are different, so integer-value equality is insufficient to cancel
the normalization interface.

Digit extraction is nonlinear even before a full carry chain. At base four,
`low(3+1)=0`, while `low(3)+low(1)=4`. No free linear conjugation supplies that
operator. This does not exclude a paid nonlinear conversion or a correctly
specified redundant format.

## Positive finite domain

The [independent checker](../../code/transfers/deferred_normalization.py) verifies
direct convolution against finite-field transforms modulo 65537. It also
retains a positive case: redundant coefficients may pass through linear
addition in the same spectral domain, then normalize exactly once at the final
integer-value recovery. This works because evaluation at a fixed radix is a
ring homomorphism from integer polynomials and addition preserves that meaning.

An explicitly enlarged base exceeding every actual coefficient also makes the
carry map the identity. The checker records the enlarged digit width. Changing
the base changes the represented integer unless its encoding is rebuilt; the
test never treats evaluations at different bases as equal. This is a controlled
format change, rather than free precision.

The first run used four independent families and four worker processes. It
checked 384 finite cases with transform lengths 4, 8, 16 and 32. All 96 forced
carry boundaries changed their spectra. The redundant linear and explicitly
carry-free controls recovered their stated values. These are fast
discriminators, not an exhaustive campaign or formal proof of the Gaussian
algorithm's error bounds.

## Padding and complete payload capacity

Combining arbitrary multiplications also requires capacity for their full
degree. The exact negative `(1+x)^4` in a length-four cyclic transform aliases
the leading term:

```text
true coefficients:    [1,4,6,4,1]
cyclic coefficients:  [2,4,6,4]
at base four:         625 versus 370
difference:           4^4-1 = 255.
```

An explicitly paid length-eight transform repairs the example. For a product
of `m` polynomials of degree `ell-1`, a noncyclic transform needs capacity at
least `m*(ell-1)+1`. A modulus also needs to exceed every retained coefficient
or use a correctly paid exact reconstruction. Matching small modular samples
without that bound would be inadequate.

The stress family `(1+x)^m` illustrates redundant-width growth. Its canonical
base-two integer is `3^m`, with only `O(m)` bits. Its complete coefficient vector
contains `m+1` binomial coefficients. For `m` divisible by four, at least `m/2` central
coefficients have bit length proportional to `m`: for `k` between `m/4` and
`3m/4`, symmetry and monotonicity give `binom(m,k)>=binom(m,m/4)`, and
`binom(m,m/4)>=3^(m/4)` by the elementary product formula. Thus complete
variable-width coefficients require `Omega(m^2)` bits in this stress family.

| Factors m | Complete redundant coefficient bits | Canonical integer bits |
|---:|---:|---:|
| 16 | 162 | 26 |
| 64 | 2,805 | 102 |
| 256 | 46,414 | 406 |

This is a **multi-product** obstruction to unrestricted deferred carrying.
Integer multiplication is bilinear in its two operands; its recursive
coefficient products are not a chain multiplying an increasing number of
independent original inputs. The stress case therefore does not refute a
bilinear multilevel spectral representation. It identifies a necessary degree
and precision ledger for a proposed general fusion interface.

## Next decisive question

Can a two-operand, bilinear recursive representation remain spectral through
the next child's digit formation, while keeping complete payload volume,
Gaussian guards and exact recovery within the improved target? The answer must
specify the actual nonlinear digit or carry conversion, or show that no consumer
requires it until the final boundary. The old guarded CRT and packed Gaussian
work cannot be promoted merely because a finite ring identity is correct.

The next candidate should explicitly compare the growing saved transform work
with the full cost of its redundant widths, padding, field conversion, routing
and final recovery. This direction remains a hypothesis worth pursuing; naive
inverse/forward cancellation across an unchanged canonical interface is
refuted by the finite counterexample.

## Reproduction and attribution

Use the standard-library command in [reproduce.md](reproduce.md). The direct
integer convolution, carry map, transform and capacity controls are authored
inside the new research directory. No external producer is imported. Finite
field FFT identities and radix-polynomial evaluation are established algebraic
tools; worldwide novelty is not claimed. The checker and analysis were written
with AI assistance. This exact auxiliary evidence is separate from the
campaign's physical, precision and all-size proof obligations.
