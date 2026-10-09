# Complete channels of the additive weighted-scan class

Status: **MATHEMATICAL RESULT WITH EXPLICIT OPERATOR RESTRICTIONS**, supported
by exact finite linear solves and literal quotient controls. It is not a
general streaming lower bound, native integration theorem, or new exponent.

## Question and changed mechanism

Prefix scans can have exponentially large coordinate support at linear
contiguous-record traffic. The preceding
[finite scan pre/post control](streaming-scan-boundary-preflight.md) therefore
does not inherit bounded-coordinate-support exclusions. Its derived post
was dense and lacked a fast factorization. This experiment asks whether
both sides of a missing Fourier block can lie in an explicitly cheap scan
sum class, with arbitrary coefficients and cancellations allowed.

Let `D=2^f` and `F=C_1^tensor f`, where
`C_1=[[alpha,beta],[beta,alpha]]`, `alpha=(1+i)/2`, `beta=(1-i)/2`.
Then `F*1=1`. Define `L_D` to contain arbitrary diagonal entries and
off-diagonal entries of the form

```text
X_ij = u_i+v_j       for i>j,
X_ij = a_i+b_j       for i<j.
```

The two triangles have independent coefficients. This is a finite sum of
row-weighted and column-weighted prefix/suffix scans, plus pointwise
weights. Its dimension is `5D-6`. Arbitrary per-address coefficients are
permitted in the mathematical model; generating or storing them is not
assumed free in a native implementation.

The exact channel condition is `X in L_D` and `F*X in L_D`. Here X need
not be invertible, unitary, dyadic, positive, or cancellation-free. The
linear space is first solved over `Q(i)`; the proof below holds over any
complex coefficient extension. Analysis divisions are not native scalar
operations.

## All-size classification

For every `f>=4`, write `m=D/2` and `s_i=1[i>=m]`. The complete channel
space is

```text
X = u*1^T + 1*v^T + s*w^T,
```

where u and v are arbitrary and w is constant on each interior interval
`[0,m-2]` and `[m+1,D-1]`, with independent entries at `m-1` and `m`.
The constant component of w can be absorbed in u. There are exactly
three additional midpoint channels, so the full dimension is `2D+2`
and every scalar channel has rank at most three.

The proof uses adjacent differences, without numerical inference.

Let `Delta_i=e_(i+1)^T-e_i^T` and let `P_ij=1[i>j]`, so
`Delta*P=I`. For any X,

```text
A = Delta*X*Delta^T.
```

The condition `X in L_D` is exactly that A is tridiagonal. In one
direction, the mixed differences of `u_i+v_j` vanish away from the
diagonal. Conversely, zero mixed differences propagate the additive
triangle representation. Equivalently, every X decomposes as
`P*A*P^T` plus a row-constant and column-constant matrix; all tridiagonal
A and all those constant terms are admitted. The dimensions are
`(3D-5)+(2D-1)=5D-6`.

Define `H=Delta*F*P`. Since F fixes 1 and `P*Delta*x=x-x_0*1`,
`Delta*F=H*Delta`. Therefore the two channel conditions are exactly

```text
A is tridiagonal,
H*A is tridiagonal.
```

H is invertible: it is the induced invertible F on the quotient by the
constant vector. Split its rows and columns into sizes `(m-1,1,m-1)`.
Using `F=[[alpha G,beta G],[beta G,alpha G]]`, where
`G=C_(f-1)`, gives

```text
H = [[alpha H0, 0, beta H0],
     [    *   , i,    *   ],
     [beta H0 , 0, alpha H0]],
H0 = Delta_m*G*P_m.
```

The middle column is exactly `i*e_(m-1)`, because
`F*s=beta*1+i*s`. The middle row's other entries are irrelevant to
the following elimination. H0 is invertible by the same quotient
argument, and `alpha,beta` are nonzero.

Column j of a tridiagonal A has support in `{j-1,j,j+1}`. If that window
lies entirely in the left block, its image has a right component
`beta H0*a`; to remain in the same left window it must vanish. The
column is therefore zero. The analogous argument applies on the right.
At `j=m-2` or `j=m`, the window contains the middle coordinate and just
one side; the side component again vanishes. Only the middle coordinate
can remain.

For `j=m-1`, the possible side components are `a*e_(m-2)` on the left
and `b*e_0` on the right. Choose interior row two of H0; it is not an
endpoint when `m>=8`. Both output sides must be zero there, giving

```text
alpha*a*H0[2,m-2] + beta*b*H0[2,0] = 0,
beta*a*H0[2,m-2]  + alpha*b*H0[2,0] = 0.
```

The two-by-two coefficient determinant is `alpha^2-beta^2=i`.
Both H0 entries are nonzero: with `n=f-1`, the endpoint-column formula
is

```text
H0[2,0]   = G[2,0]-G[3,0]     = i*alpha^(n-2)*beta,
H0[2,m-2] = G[3,m-1]-G[2,m-1] = i*alpha*beta^(n-2).
```

Thus `a=b=0`. Every surviving column is a multiple of the middle
coordinate, and only the three adjacent columns survive. Consequently
A has only its middle row, supported in those three positions.
Reconstructing `P*A*P^T` gives precisely the stated `s*w^T` family.
Conversely that family stays in both scan classes because
`F*s=beta*1+i*s`. This proves completeness and the dimension, rather
than merely supplying a candidate family.

The `f>=4` condition matters. Exact small solves give additional channels
at f2 and f3; the central endpoint-column argument needs a nonzero
interior row available at m8. Those exceptions are retained.

## Complete coupled input capacity

Allow W scalar banks and take an arbitrary vertical stack of W channels
from this class. The row-constant term in each block depends on one
shared input functional `1^T*x`; the column-constant terms depend on W
arbitrary functionals `v_b^T*x`; all residual terms depend on three
shared midpoint functionals. Therefore

```text
rank([X_1; ...; X_W]) <= W+4.
```

This is a bound on the whole stacked source column, not a conclusion
from individual singular blocks alone. At W6 the bound is ten, and
the literal controls construct stacks of exact rank ten.

For the common missing-line quotient
`P0=diag(I,I,F,F,F,F)`, a true pre/post boundary satisfies
`R=diag(F,...,F)*B^-1*P0^-1`. For either I source block, if every inverse
input block `X_b=(B^-1)_bj` and corresponding output block `R_bj=F*X_b`
is in this scan class, its complete source column has rank at most ten.
An invertible B requires that column to have rank D. Thus the assumed
six-bank boundary is impossible for every `f>=4`.

Other source columns need not satisfy this restriction for the argument
to apply. However, admitting more banks changes the bound to W+4.
Zero scratch, noninvertible encodings with a changed data domain, or
extra materialized channels require their own complete stock and
endpoint analysis. The actual joint component has two distinct source
labels; identifying it with this common quotient remains a separate
unproved physical step.

## Exact finite evidence

The [linear solver](../../code/synthesis/weighted_scan_intertwiners.py)
uses an independent explicit basis and all original additive triangle
constraints over `Q(i)`. It clears each null vector to integer Gaussian
coefficients and rechecks every original equation.

| f | D | Full channel dimension | Residual common left/right ranks | Largest tested scalar rank | Six-bank stack lower/upper ranks |
| --- | ---: | ---: | --- | ---: | --- |
| 2 | 4 | 12 | 3 / 3 | 4 | 4 / 4 |
| 3 | 8 | 19 | 2 / 3 | 4 | 8 / 8 |
| 4 | 16 | 34 | 1 / 3 | 3 | 10 / 10 |
| 5 | 32 | 66 | 1 / 3 | 3 | 10 / 10 |

Four workers completed the solve in at most 27.067 seconds per case.
Tested scalar and stack ranks are exact finite witnesses; they are not
claims of exhaustive rank maximization. The all-size completeness and
upper bounds follow from the proof above.

The separate [structure controls](../../code/synthesis/weighted_scan_structure.py)
use literal Gaussian-integer Fourier coefficients. They check every
entry of `Delta F=H Delta`, every off-center recursive block, and every
column's entire local tridiagonal transport system at f4/f5/f6/f7.
All channel dimensions match the three-middle-column formula. They also
check the three explicit spanning channels and exact rank-ten stacks.
Four workers pass these controls in at most 0.504 seconds per case.
Address reversal is explicitly rejected from the class, and I is in
the class while F is not.

No external dependencies are used. Completed sources and raw protocol
bytes are pinned by the two durable runs:

- [Exact full-space solve](../../runs/20261009T042142Z-synthesis-weighted-scan-intertwiners/)
- [Literal structure controls](../../runs/20261009T042806Z-synthesis-weighted-scan-structure/)

The first raw namespace was selected 102.049124 seconds before its actual
protocol start; its durable name follows that actual start. The second
namespace was generated by UTC immediately at launch. Both original
protocols remain unchanged and both persistence receipts distinguish
ignored raw evidence from durable complete copies.

From the topic root, use fresh output directories:

```sh
python3 -B code/synthesis/weighted_scan_intertwiners.py --workers 4 \
  --output work/reproduce/<fresh>-weighted-scan-space/results
python3 -B code/synthesis/weighted_scan_structure.py --workers 2 --columns 4 5 \
  --output work/ci/<fresh>-weighted-scan-structure/results
```

## Restriction lifted next

The theorem concerns additive weighted scan sums in one fixed address
ordering. Products of scan operators, hierarchical scans, reversal,
global or nonlinear address permutations, and large-stride buffers can
have much larger relevant cut ranks and are not covered. The native
traffic of per-address weight generation, buffer/layout conversion,
precision and endpoints remains an independent obligation even inside
the class. A genuine positive must supply an executable cheap post
factorization and complete physical input capacity. This result rules
out replacing that work by these three low-rank channels.
