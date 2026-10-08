# Whole-residual complex children: numerical screen and guard hypothesis

The accepted h28 complex counts support a promising exact characteristic
**if** a nonalternating residual of rank r can be compiled as one complete
child `C^(r*f)` instead of r separate `C^f` calls. For the accepted R92309
controller circuit, the screen gives
`b=1845487113109502349/10^24`, about `1.845487113109e-6`.
This is a changed recursive construction, not a rounding of its old
uniform saving near `4.0034e-8`. It would make the current generic bit
saving near `1.43492e-7` the limiting primitive. The full fixed-tape/frame/
volume/tail transfer is pending; **this report promotes no new primitive
or multiplication kappa**.

## Exact characteristic screen

Let `J=(R+h+1)v^2`. Group only three disjoint boundary families:

| Family | Rank r | Multiplicity |
| --- | ---: | --- |
| Final middle-bank complement | m-h^2 | J |
| Joined auxiliary/central complement | m-2h | J |
| Stage3 data complements | (h^2-1)(h-1) | 2N |

Every other physical residual remains individual. The screen checks all
counts against accepted finite complex inputs, checks positive remaining
individual rank, and changes no role count or scalar gate plan.
With `M_L=sum n_r*r*log(r)_L` and rigorous upper `log(m)_U`, it proves

`D-b*(s*log(m)_U-M_L)-b^2*s*log(m)_U^2/[2*(1-b*log(m)_U)]>0`.

This bounds the positive normalized characteristic
`sum n_r*r*exp(b*log(m/r))<Wm`, using
`exp(x)<=1+x+x^2/[2*(1-x)]` for `0<=x<1`.
All acceptance uses rational arithmetic and outward 24-term logarithm
intervals on a common `2^256` grid. No floating thresholds are used.

| Accepted roles | Strict screen saving | Maximum child | Binary depth constant |
| ---: | --- | ---: | ---: |
| 97586 | `1751827165437614461/1000000000000000000000000` | 21896 | 272 |
| 92309 | `1845487113109502349/1000000000000000000000000` | 21896 | 272 |

The exact inequality `m^272>2*21896^272` yields a depth bound
`272 ceil(log2 e)`. Since `W<2^41` and
`41*272*(2+1/25)<23000`, a complete `p^23000` complex row reservoir
would suffice after the usual `e<=Cp,p>=C,log2p>=25` assumptions.
The accepted generic bit reservoir is larger, `p^66000`, so it can cover
both after a newly scoped common setup constant. The screen alone does
not prove this layout implication.

## Mixed directions and arbitrary widths

After the existing orthonormal binary address adapter, the r active banks
can be put first. Their adjacent complete `f*K` fields share the same
selected offset rho and concatenate into one `(r*f)*K` field with the
selected positions `rho+j*K`, `0<=j<r*f`. This equality of full fields
requires a fixed-tape proof with the inactive banks and parked arbitrary
scratch still intact. It must not be replaced by an uncharged gather.

An orthonormal basis vector can have weight 1 or 3 modulo4, so the r
kernels are not automatically all forward. The retained corrected inverse
identity gives a uniform forward child and aligned diagonal wrappers:

`mixed = (-i)^(f*n_minus) Z_minus C^(r*f) Z_minus`.

Here Z_minus is parity on precisely the negative active slots. The
already accepted aligned mask/phase scans are the relevant paid operation;
all-forward substitution without these wrappers is invalid. The alternative
identity `C^-1=X C` also works algebraically, but needs a paid address
translation and is not assumed free.

The new C(e) contract must accept arbitrary widths, since `r*f` need not
be a power of m. Write `e=m*f+t`, `0<=t<m`. The main field recursively
uses grouped children. The tail is exposed, transformed by t exact C1
butterflies and restored with the fixed-width crossing schedule. Merely
calling the old BASE-m powers routine r times would lose the claimed
saving. The actual tape schedule and all arbitrary scratch restoration
remain independent proof obligations.

## New semantic guard, same possible explicit constant

The uniform-child active recurrence cannot be copied verbatim. Under a
complete grouped child contract the correct bound is

`A(e)<=A(r_max*floor(e/m))+s*floor(e/m)+E`.

A completed grouped forward/inverse tensor has coefficients in
`2^(-r*f) Z[i]` and row norm at most `2^(r*f)`, exactly the semantic charge
of the complete separate children it replaces. Thus temporary child excess
does not persist after return. For B=s+E>=8, a direct induction gives
`A(e)<=2Be`: at an internal node `e=m*f+t`, `f>=1`,
`2B*(m-r_max)>=s+E` because r_max<m. The base has `A(e)<=8e`.
Alternatively active widths strictly decrease as integers, so depth<=e,
`sum floor(e_j/m)<=e/(m-r_max)<=e`, and the same linear bound follows.
Completed outer BASE-m pieces have total semantic size<=d, giving
`A_layer<=(2B+18)d<32mB^2*d` independently of fixed rational beta.
The same fine-grid integer format is kept throughout; no actual child
rounding, bit compaction or coarser storage is introduced.

The retained E must additionally cover the concrete arbitrary-width tail
butterflies. A direct scalar realization uses only saved-input sums,
differences, unit i phases and exact halves, with a conservative bound
of 32 elementary depth units per tail bit. At t<m this adds at most32m.
This is much smaller than the independently accepted literal-G/E slack,
but its inclusion in the actual schedule must be checked, not inferred
from a false `G<6W` shortcut.

## Variable-shrink stopped-tree estimate

The homogeneous characteristic exponent sigma is a branching bound, not
a claim that a complete C(e) call costs e^sigma while ignoring binary
address adapters. Node overhead still has the accepted bit exponent tau.
For child width `r*floor(e/m)` and volume factor `n_r/W`, the sigma
potential decreases because `sum(n_r/W)*(r/m)^sigma<1`.

Stop at e<d^beta. Under the explicit d^beta>2m condition, a terminal
child has size at least d^beta/(2m), while an internal node has size at
least d^beta. At each actual depth the sigma potential is at most d^sigma.
The depth is O(log d), with a new fixed constant. If tau>=sigma, internal
cost is root dominated by d^tau; if tau<sigma, use
`e^(tau-sigma)<=d^(beta*(tau-sigma))` at internal nodes. This gives

`chi=tau+(1-beta)*max(sigma-tau,0)`

and leaf cost `d^(sigma+beta*(1-sigma))`, with fixed geometric/logarithmic
constants absorbed only across strict gaps. Retain
`max(tau,sigma,chi)<lambda<lambda_prime` and the original reservation,
precision, Gaussian, routing and resampling constraints. This derivation
is the numerical route for a future complete composition; the current
accepted general-beta uniform witness remains unchanged.

## Executed exact controls and scope

The [screen source](../code/downstream_nonuniform_complex_screen.py) and
[screen run](../runs/20261008T065948Z-downstream-nonuniform-complex-screen/)
are frozen. Screen certificate SHA256 `5153ccefa9ac3dac74e6e5b0677ff31b80de4ce017f9c2ece8906c43ebdca37e`.
It used one worker, 0.367s and 23,140KiB peak RSS.
The separate [fixed-grid source](../code/downstream_nonuniform_semantic_guard.py)
and [guard run](../runs/20261008T070532Z-downstream-nonuniform-semantic-guard/)
passed 623544 exact Gaussian-integer
halvings, 126 complete basis columns,
146 forward/closed-form/inverse probes,
and 396 exact stopped nonuniform
recurrence cases. Its certificate SHA256 is `4447e27b40a2a1dd3e776f5dace24b64b4bf44354b293d5ed7960cfaec3b92ab`.
The child completed in 1.520s with 24,516KiB peak RSS and released its
owned worker.

The toy recursion has real near-parent-width cancellation children and a
three-bit fine-grid excursion. Every halving asserts two even integer
numerators on a fixed preallocated linear grid. Returned tensors agree
with an independently computed closed Gaussian coefficient formula;
no Fraction simplification is used. Grouped active bits agree with
complete separate child blocks. The negative eager-rounding control
changes a true nonzero child image. These tests discriminate numerical
boundary errors; they are not a replay of the full enormous finite phase
network or proof of the pending actual tape schedule.

Reproduce from the topic directory with one numerical thread and fresh
output paths:

```bash
PYTHONINTMAXSTRDIGITS=0 python3 code/downstream_nonuniform_complex_screen.py \
  --accepted-assembly runs/20261008T065403Z-downstream-generic-general-beta-repair/results/certificate.json \
  --output /path/to/fresh-screen.json
python3 code/downstream_nonuniform_semantic_guard.py \
  --output /path/to/fresh-grid-controls.json
```

The first input contains accepted finite complex counts; its complete
uniform multiplication assembly was independently accepted later at
[the root review](../runs/20261008T070246Z-review-general-beta-assembly/results/certificate.json).
The newer uniform R88377 complex circuit is independently promoted and
may enter a separate thin composition. Its new whole-rank transfer is
still separate. No original input or historical certificate was edited.
The original start and user-extended 2026-10-08 10:00 UTC deadline persist.
