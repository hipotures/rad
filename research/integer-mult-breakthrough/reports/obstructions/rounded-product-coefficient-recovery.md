# Approximate Gaussian transforms with exact product coefficient recovery

Status: **CONDITIONAL ALL-SIZE SENSITIVITY WITH EXACT FINITE CONTROLS**.
This is a complete coefficient-recovery interface for a defined product
format, not a new native multiplier or proof of the old integer assembly.

Let C_s be the tensor of the normalized Gaussian kernel
`[[alpha,beta],[beta,alpha]]`, alpha=(1+i)/2, beta=(1-i)/2. Treat each of
its D=2^s records as a polynomial in R=Z[i][X]/(X^r+1). Define

```text
Q_s(A,B) = C_s^-1 ((C_s A) * (C_s B)),
```

where multiplication is coefficient-complete negacyclic multiplication at
each record. The one-axis map is

```text
q0 = (a0*b0+a0*b1+a1*b0-a1*b1)/2,
q1 = (-a0*b0+a0*b1+a1*b0+a1*b1)/2.
```

Tensoring these identities and extending bilinearly to R proves that
`2^s Q_s(A,B)` has Gaussian integer coefficients for all Gaussian integer
inputs. The required scale cannot be silently replaced by one.

## Complete error ledger

Use the Frobenius norm over every complex coefficient in every record.
Young's inequality for each negacyclic record and Cauchy-Schwarz imply

```text
||P*Q||_F <= sqrt(r) ||P||_F ||Q||_F.
```

The sign in wrapped coefficients does not increase the bound. Summing
squares over the records gives the same inequality for the complete array.
Both forward and inverse C_s are unitary for this norm. If approximate
forward endpoints have arbitrary complete error fields of norms epsA and
epsB, exact products of those actual approximate arrays have error at most

```text
sqrt(r) (||A||_F epsB + ||B||_F epsA + epsA epsB).
```

Add epsI for the approximate inverse on the ACTUAL approximate product
array. Its guarantee on only ideal inputs would be insufficient. Any
rounding in multiplication, normalization, projection or scale application
must be added separately; exact product arithmetic is the contract here.
After multiplication by2^s, a total norm error below1/4 permits exact
nearest-integer recovery of both coordinates of every Gaussian coefficient.

For an explicit conservative reserve, let A1 and B1 be integer bounds on
the input real/imaginary L1 norms. They bound the Frobenius norms. Set

```text
t = s + ceil(log2(r*(A1+B1+1))) + 4,
epsA,epsB <= 2^-t,
epsI <= 2^(-s-4).
```

Using sqrt(r)<=r, the scaled error is at most1/8. This is strictly inside
the required recovery interval. The reserve is logarithmic in polynomial
degree, coefficient-array length and input magnitude, with the explicit
s-bit recovery scale charged. Connecting these endpoint tolerances to a
native literal word still requires its full numerical and layout contract.

## Exact finite evidence and limits

Nine four-worker cases use s1/s2/s4, r1/r2/r4 and four Gaussian fields.
All828 Gram entries establish their exact unitarity; all616 recovered
coefficients match complete exact references. The checker introduces
nonzero admitted adversarial errors throughout both forward arrays and the
inverse endpoint. It retains squared errors, bounds and complete scaled
targets. The errors are explicit perturbations satisfying the stated
contract, not a simulation of a faster native transform. Polynomial
multiplication uses complete rational coefficient reference arithmetic.

Unit-input controls reject zero fractional precision, missing2^s scale and
a skipped inverse. The proof was independently checked by the transfer
agent, including tensor integrality and the actual-product inverse scope.
AI-assisted internal review and finite checks are not formal verification.

The appropriate next integration test is a literal rounded forward and
inverse program meeting these complete tolerances, with exact full products,
followed by the separate integer-assembly carrying and layout proof.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/rounded_product_recovery.py \
  --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/rounded-product
```

Use `--workers 1 --bounded` for four smaller cases. Standard-library
Python3.11+ suffices. Choose a fresh output path for every attempt.
