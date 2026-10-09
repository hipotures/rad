# Literal shared-center release with arbitrary dirty helpers

The supplied component realizes the virtual map `(x,y,z) -> (x,y+Kx,z)`.
It uses v source banks, v sink banks and v independent arbitrary-dirty
auxiliary banks. Its actual physical endpoints and child calls are explicit.
It is **center-only**: it does not supply `(I-K)x`, a complete integer
multiplier or a larger kappa.

## Scalar factorization and complete dirty cancellation

Let B be an invertible in-place dyadic v-by-v basis word, with its first q
rows equal to a center bank G. Let D decode that bank, so `K=D*G`.
The single-total basis from the complex track has q=`choose(h,2)` and
v=`choose(h,5)`. It replaces pair feature (0,1) by the total and retains
every other pair star. Its decoder numerators are divided by 32.

The virtual program is

```text
z <- Bz;       y <- y - D*z[0:q];   z <- B^-1*z
z <- z + x
z <- Bz;       y <- y + D*z[0:q];   z <- B^-1*z
z <- z - x
```

The first scatter subtracts `K*z_initial`; the second adds
`K*(z_initial+x)`. Both basis inverses are paid. Every initial z coordinate
is arbitrary. Thus the program restores x and z and adds Kx to y without
requiring a zero bank. It is independently checked against the center
polynomial `K[T,S]=(intersection(T,S)-1)*(intersection(T,S)-3)/8`, rather
than merely replaying the producer decoder.

## Actual Gaussian frame chronology

Write `C_T=(1+i)I/2+(1-i)X^T/2` and `F=C_h` on one selected address column.
All T labels have weight five, hence odd norm and weight one modulo four.
The initial physical frames are `C_T*x`, `y`, and `z`; the required final
frames are `F*x`, `(F*C_T^-1)*(y+Kx)`, and **`F*z`**. Virtual dirty
restoration does not mean identity on the raw dirty input.

1. Run the early B, negative scatter and B inverse with every helper and
   sink in the actual identity Gaussian frame.
2. Move helper j from identity to C_T and inject its matching physical
   source. The source already has exactly that same C_T operator.
3. Move every helper to the full F operator. Run the late B there, including
   all actual scalar scales and raw bank exchanges.
4. Apply F inverse to exactly the q feature banks. Scatter their decoded
   values into the sinks while both operands have the identity operator.
5. Apply F to those q feature banks, then run B inverse with every helper
   again in precisely the same full F operator.
6. Move each source to F, subtract it from its matching full-frame helper,
   and move each sink to `F*C_T^-1`.

All these operators are literal Gaussian dyadic convolutions; no abstract
Lagrangian label is substituted for a data operation. The inverse full
operator is `C_h^*=C_h*X^ones`, so it retains a full-width child call plus an
address translation. The raw B exchanges occur between equal operators;
their data movement is separate from recursive child calls.

For f selected columns, apply the same address operator independently to
each column. B and D act with fixed scalar coefficients on whole banks and
commute with those common address operators. The two-column finite control
explicitly tests this lifting; coefficients are not incorrectly raised to f.

## Paid relative frame interface

Put `alpha=(1+i)/2`, `beta=(1-i)/2`. For an address difference d,
`C_h(d)=alpha^h*(-i)^weight(d)`. Since `weight(T)=1 mod4`,

```text
(C_h*C_T^-1)(d)
 = beta*C_h(d) + alpha*C_h(d xor T)
 = 2*beta*C_h(d)  if d dot T = 0,
 = 0              otherwise.
```

Its support is `T-perp`, of dimension h-1. Choose any binary basis S of
that perpendicular space and its dot-dual basis M, so `S^T*M=I`.
The restricted dot form is invertible: its radical is the intersection of
T-perp with span(T), which is zero because T has odd norm. The form may be
alternating; no norm-one basis assumption is made.

Use output routing columns `(S,T)` and input routing columns `(M,T)`.
For matching quotient bit c, original output and input addresses are
`S*a+c*T` and `M*b+c*T`. The nonzero block is one C_(h-1) child with unit
chirps

```text
output phase = i^(-(weight(S*a)-weight(a)))
input phase  = i^(-(weight(M*b)-weight(b)))
```

The identity follows by expanding binary XOR weights modulo four and using
`(S*a) dot (M*b)=a dot b`. The chirps are quadratic fourth-root phases of
linear address maps. Both input/output affine maps and these phase operations
remain paid native obligations. The line C_T itself is one C_1 child under
routing with first column T and remaining columns a basis of T-perp.

The producer reconstructs every coefficient for all 21 weight-five labels
at h=7. It also rejects a weight-three label in the no-offset interface;
that case would require a different affine offset and is outside this formula.

## Actual component rank ledger

The stock is `W=3v`. The exact per-column child-width histogram is

| Width | Multiplicity | Purpose |
| ---: | ---: | --- |
| 1 | v | zero-to-line helper injections |
| h-1 | 3v | helper line-to-full, source line-to-full, sink zero-to-kernel |
| h | 2q | feature full-to-zero reset and zero-to-full return |

Hence total rank charge is `Wh-2v+2qh`, with endpoint floor `Wh-2v` and
closed feature loss exactly `2qh`. The full-width self mass is `2q/W`; those
calls are retained rather than forbidden because they have the parent width.
The full moment and permitted recursion depth still require a complete word.

| h | v | q | W*h | Component rank charge | Component deficit |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 15,504 | 190 | 930,240 | 906,832 | 23,408 |
| 28 | 98,280 | 378 | 8,255,520 | 8,080,128 | 175,392 |
| 30 | 142,506 | 435 | 12,825,540 | 12,566,628 | 258,912 |

These are algebraic counts for this Kx component. They cannot be substituted
for an old center cost unless the old chronology is actually removed and a
complete side/center word attains the combined ledger. In particular this
construction uses v physical helper banks, which is distinct from a scalar
addition count used as an auxiliary budget proxy.

## Completed finite evidence

The [producer](../../code/synthesis/closed_center_release.py) and
[completed run](../../runs/20261009T010435Z-synthesis-closed-center-release/report.md)
retain four cases:

- Orthogonal three-label color center, f=1: all 72 physical source/sink/dirty
  address basis columns are explicitly replayed.
- The same color center, f=2: nine origin-address bank columns determine all
  576 address basis columns by common-XOR translation covariance.
- Single-total h=7: all 63 scalar bank columns and all 63 physical origin-bank
  columns pass; covariance determines all 8,064 address basis columns. Every
  phase coefficient and paid relative normal form is checked for all 21 labels.
- Single-total h=8: all 168 scalar source/sink/dirty bank columns pass. Its
  full physical matrix is not numerically replayed in this run.

Translation covariance is exact: C_T and C_h are convolution operators;
constant-coefficient bank additions/scales and raw bank exchanges commute
with simultaneous address XOR on every bank. Checking each bank's address-zero
column therefore determines every translated column of the linear operator.
This proof is stated separately from the number of explicitly computed
columns. Complex linearity similarly covers arbitrary real/imaginary inputs.

Removing a required feature full-frame return produces an independent dirty
input counterexample. This controls the difference between virtual and raw
physical restoration. The [bounded verifier](../../code/synthesis/verify_closed_center_release.py)
passes in about 0.7 seconds and preserves its
[complete check receipt](../../runs/20261009T010718Z-synthesis-closed-center-ci/report.md).
It exercises both color tensor cases, all total-base scalar columns, one
noncoordinate h=7 affine/chirp interface, the omitted-return control and
the weight-three rejection. It does not replay the full h=7 origin-bank run.

The first producer protocol omitted a transitive loaded optional capacity
module, `five_subset_envelope.py`. Its function is unused by this component;
it is unchanged from checkpoint 8135f5e4 and separately pinned in
[dependency provenance](../../runs/20261009T010435Z-synthesis-closed-center-release/results/dependency-provenance.json).
The bounded verifier records the complete 16-file closure.

The raw directory namespace `20261009T012000Z` was manually chosen before
execution and is 924.180 seconds later than the actual recorded start
`2026-10-09T01:04:35.820277+00:00`. It is a unique path label, not a start-time
measurement. The durable run ID follows the actual protocol timestamp.
[Namespace provenance](../../runs/20261009T010435Z-synthesis-closed-center-release/results/namespace-provenance.json)
records this mismatch; the original protocol bytes remain unchanged.

## Reproduction and integration limit

Both commands need only the Python standard library and a fresh ignored output:

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/closed_center_release.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-center>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_closed_center_release.py --output research/integer-mult-breakthrough/work/synthesis/<fresh-check>/check.json
```

The decisive next obligation is a joint I-K side chronology. Sources must
continue from their original line operators to full and sinks from identity
to their matching kernel operators. An early side dirty echo that has already
moved a sink to its kernel cannot simply be followed by the central zero-frame
scatter without paying its return. Likewise, computing each side row only
after its helper reaches full introduces per-output lowering/return costs.
The next component must state those missing gates, helper stocks, required
physical dirty outputs and every actual source/sink return. The center result
establishes one concrete primitive; it does not settle that integration.
