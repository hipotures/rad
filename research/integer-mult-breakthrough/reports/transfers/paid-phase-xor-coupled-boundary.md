# Paid phase conjugation and the unchanged activity controller

Status: **EXACT LOCAL GAUSSIAN ALGEBRA AND A SCOPED FAILED RECURSION
LEDGER**. An XOR by an immutable mask has an exact phase-conjugation
implementation. Substituting the standard two-zeta C factorization into
that implementation pays four full same-volume Z calls. In the existing
e=3f+12+u activity layout, that one route already has a failed large-width
power moment. This excludes the stated replacement proof, not every
Fourier route, coupled primitive or sharing architecture.

## Exact phase route

Write alpha=(1+i)/2, beta=(1-i)/2, C=[[alpha,beta],[beta,alpha]],
S=diag(1,i), and H=[[1,1],[1,-1]]. Then

    Htilde = S C S = alpha H,
    Htilde_f = S_f C_f S_f = alpha^f H_f.

Both Htilde_f and C_f are unitary. For a mask G computed from immutable
control fields, the diagonal D_G at target address x is
(-1)^(G dot x). Exact coefficientwise conjugation is

    X_G = Htilde_f D_G Htilde_f^-1.

The temporal word is inverse Htilde, then D_G, then forward Htilde.
It moves arbitrary complete Gaussian fields by target address x to x XOR G.
The controls, unselected planes and companion values are row parameters.
They stay unchanged in the finite algebra controls. No native permutation
of complete records is inferred from a Python list implementation.
Evaluating G and its parity phase, representing target/control shapes,
and physically supplying the C call remain explicit native obligations.

The inverse is paid exactly. With Zphase=diag(1,-1),

    C_f^-1 = (-i)^f Zphase_f C_f Zphase_f.

The global unit (-i)^f multiplies every coefficient in the complete
record once. It is not raised again by the number of independent Gaussian
fields or polynomial coefficients. Omitting it corrupts the literal
endpoint whenever it is nontrivial. The finite f=4 unit is already one,
so that case alone cannot detect the omission; f=1,2,3 give witnesses.
The forward/inverse conjugation therefore has two full C_f calls, with
all scalar phase wrappers and native mask work separately paid.

## Full two-zeta factorization and inverse

Let Z=[[1,0],[1,1]]. The exact identity

    H = Z diag(1,-2) Z^T

gives

    C_f = S_f^-1 alpha^f Z_f diag((-2)^weight) Z_f^T S_f^-1.

Its literal inverse is

    C_f^-1 = S_f Z_f^-T diag((-2)^(-weight)) Z_f^-1 alpha^(-f) S_f.

The inverse uses the actual inverse zeta endpoints, not a free uncompute
on dirty records. All coefficients are Gaussian dyadic; alpha^(-f)=(1-i)^f
is integral and the inverse weight diagonal has denominator at most 2^f.
Substituting both complete factorizations into X_G pays four Z-type calls:
Z, Z^T, Z^-1 and Z^-T, each on the same f selected bits and the same
complete record volume V. Native conversion between transpose/difference
forms is a separate paid operation if not supplied as a typed interface.
Treating those four calls as available is an optimistic lower bill for
the proposed replacement, not proof that they already have fast native
implementations. A constant two-call conversion at the outside of a
finished independent supplier is compatible with this identity.

An exact fixed-grid local execution reserves up to 2f added denominator
bits over the inverse and forward C factorizations. Integer/phase
wrappers add no fractional grid. Intermediate zeta and weight scalings
can amplify values exponentially in f; a conservative local row-norm
bound is 2^(6f+2) times the input component magnitude. These charges do
not become free when the completed XOR returns the original grid and
magnitudes. They are local analytic bounds; no native whole-network
guard or outer integer recovery follows from the finite Fraction replay.

## Changed primitive versus the unchanged controller

In the current all-width activity shape, the node has

    e=3f+12+u, 0<=u<3.

The twelve selected guard axes and the residual u axes are actual paid
target axes. They are not dropped from the parent selected width. The
target f-band of one packed XOR occupies the existing complete K-bit
chunks, with the other bands serving as controls and restored companions.
Suppose one replaces even a single such mandatory full-volume route by
the four Z_f calls above. Its power-p child mass alone is

    4 (f/e)^p.

For 0<p<=1 and 0<f/e<1, it is at least 4f/e. If f>12+u, then 4f/e>1.
Thus it fails for every such p at all sufficiently large widths, before
the other activity-word calls, guards, phases, metadata and repair fees.
The limiting mass is 4/3^p>1. This is specific to the retained three-band
same-volume controller. A different ratio, a paid smaller-volume call,
sharing of neighboring conjugations or a truly fused word changes it.

The same conclusion holds for a positive two-type potential. The proposed
Z_e invocation's one route requires two C_f calls. Each C_f requires two
Z_f calls. Their cycle product is 4(f/e)^p. Multiplying the C and Z type
potentials by positive constants cannot change that product. Allowing
different fixed powers does not rescue this particular asymptotic cycle:
the Z-to-C fixed-ratio edge requires p_C<=p_Z and the C-to-Z same-width
edge requires p_Z<=p_C, so they must agree. This does not preclude a
different coupled assembly, changed volume normalization or packet format.

Counting only two Z calls can give a misleading pass. The exact controls
retain that omitted-conversion negative separately from the actual
four-call failure. Removing one literal paid zeta factor also changes the
Gaussian operator and gives an explicit finite counterexample. Neither
a smaller numeric characteristic nor well-founded width decrease alone
establishes the complete transfer.

## Evidence and reproduction

The [standalone source](../../code/transfers/phase_xor_coupled_budget.py)
imports only the standard library and independently defines exact Gaussian
arithmetic and tensor C, zeta and chirp operators. It checks every column
of both C factorizations and every target-mask XOR at f=1,2,3,4. The
four-worker first attempt is
`20261009T110134Z-transfer-phase-xor-first`, actual start
2026-10-09T11:01:34.442041+00:00. It passes 4,680 complete mask-column
coefficients and 7,680 arbitrary Gaussian field values across all three-bit
controls, two-bit guards, one-bit companions and four complete fields.
The true XOR inverse restores each full field. Global-unit and omitted-zeta
factor negatives discriminate. Thirty-six exact rational power tests retain
the failed four-child bill and the misleading two-child comparisons.

Source SHA256 is
a92e0344b65c7b1826504a076741bb5a1e277ac5284f8e9ec1e69d9a32f7e2ed,
unchanged before and after. The bounded replay uses f=1,2 and the full
power controls. All attempts use fresh actual-UTC namespaces and retain
their exact source/config/protocol and compact outcomes.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/phase_xor_coupled_budget.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/phase_xor_coupled_budget.py --workers 4
```

The Fourier character-conjugation identity and zeta factorization are
standard elementary algebra, not a novelty claim. AI assistance was used
to derive and instrument the explicit paid controller comparison.
No native C/Z supplier, physical bit router, general circuit lower bound,
or new kappa is claimed. A useful next escape must change the actual
same-volume cycle mass rather than waive one of its completed calls.
