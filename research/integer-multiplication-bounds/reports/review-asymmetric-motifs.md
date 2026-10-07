# Independent review of unequal outer and middle bit motifs

The `p,q,p` construction is a valid extension of the retained paired bit
motif, provided that its two local circuits satisfy the existing scalar
and rational-envelope certificates. The middle-axis matching, rather than
an outer-axis matching, supplies the required stage-joining inclusion.
No new precision or Turing-machine assumption is required by this finite
extension. The resulting asymptotic statement still depends on the
retained upstream interfaces and the separately reviewed reusable
Gaussian inverse.

Campaign interval: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned reference: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.
Reviewed source: `asymmetric_motif.py`, SHA-256
`8a7c9373deb99f7725e2dffde47321979acb285b5795ed9f84877afec032580d`.
The original v1 certificate is pinned by SHA-256 in the independent run.

## Scalar operation and indexing

Let `vp=C(p,3)`, `vq=C(q,3)`, with even `p,q>=6`. Data coordinates are
triples `(a,b,c)` drawn from `vp,vq,vp`, respectively. The stage-one and
stage-three invocations use the same outer circuit; the middle stage uses
the `q` circuit. Each local forward invocation sends `(x,y)` to `(x,y+x)`
over characteristic two and restores arbitrary side and central scratch.
The inverse middle invocation, with the logical banks exchanged, sends
`(x,y+x)` to `(y,y+x)`. The last invocation gives `(y,x)`. This argument
holds independently in every tensor coordinate.

The shared stage-one bank indexed by spectators `(A,B)` is assigned to
stage three with spectators `(B,pi_q(A))`. The permutation `pi_q` of middle
triples has intersection one with its input. Its inverse in the physical
bank indexing is essential. The independent checker enumerates all
invocation partitions and this bank bijection at unequal small pairs
`p=6,q=8` and `p=8,q=6`. Every data coordinate occurs exactly once per
stage, and every shared invocation bank occurs exactly once in stages
one and three.

The parent certificate expands the complete local identity invocation in
both directions, including arbitrary central registers: 196 basis vectors
at `h=6`, and 816 at `h=8`. It also executes all elementary operations of
the complete unequal three-stage exchange for both small pairs at seeds
1 and 109, with deterministic 32-bit data and dirty scratch. Those four
tests pass. The independent earlier envelope review expands the complete
side invocation on every local basis vector, separately from central
registers. The global unequal tests are payload tests; they are not dense
global basis expansions. The coordinatewise shear identity and exact bank
bijection give the general scalar argument.

## Rational labels and complete bank joining

Use the original rational form `I-J/9` on each of `F_p,F_q,F_p`, with tensor
product ambient dimension `m=p^2 q`. These spaces are nondegenerate:
their dimensions are even and hence not nine. Every triple line has norm
two. Products of the spectator lines are therefore nondegenerate.

The original data-label argument in `03-motifs.tex`, lines 253 onward,
uses only a nondegenerate prefix tensor product, a nondegenerate prefix
line, and a nondegenerate future line. Replace identical factors by
`F_p,F_q,F_p`. The decompositions `A=B perpendicular-sum P`, and every
successive incoming/outgoing data-label identity, continue to hold.
Within each exposed factor use its separately certified positive rational
envelopes and reverse complements. Their common component `B tensor F`
is orthogonal to the local `P tensor F` component. Consequently local
envelope positivity, nondegeneracy of reverse complements, and nesting
survive the tensor lift. Central returns are still the only decreases.

The shared-computation schedule places every auxiliary role's early gates
in the common `B tensor F` component and ends its late computation in
`A tensor F`. This is the complete-bank schedule from the pinned
`docs/research/incidence-network.md`, lines 134 onward, and
`docs/research/shared-computation.md`, lines 114 onward; it includes the
central roles. Thus the joining endpoints for the matched invocations are

```text
E = F_p tensor line(t_A) tensor line(t_B),
H = line(t_B tensor t_pi_q(A))^perp_(F_p tensor F_q) tensor F_p.
```

Here `dim E=p` and `dim H=m-p`. For every `u` in `F_p`, the inner product
of `u tensor t_A` with `t_B tensor t_pi_q(A)` is
`B_p(u,t_B) B_q(t_A,t_pi_q(A))=0`, because the middle triples meet once.
Therefore `E subset H`. Both spaces are nondegenerate: `E` is a scaled
copy of `F_p`; `H` is a tensor product of nondegenerate spaces obtained by
removing a nondegenerate line. The joining residual is nondegenerate
with dimension `m-2p`.

For each shared physical role, remove its old two endpoint edges
`E -> full ambient` and `0 -> H`, of total rank `2(m-p)`, and insert
`E -> H`, of rank `m-2p`. The saving is exactly `m` per joined physical
role. This holds for every compiled side role and every central role.
All other endpoint labels and the rational source correction stay as in
the original interface. The source correction is still exactly `N`:
the leaf input label remains its triple line on all three axes.

## Counts and selected witness

Write `Rp,Rq` for the respective physical side-role counts. There are
`vp*vq` outer invocations at each of stages one and three, sharing their
`Rp+p` complete auxiliary bank, and `vp^2` middle invocations with
`Rq+q` registers. Therefore

```text
N = vp^2 vq,
W = 2N + vp vq (Rp+p) + vp^2 (Rq+q),
L = 2 vp vq p^2 + vp^2 q^2,
s = Wm - N + 2L.
```

Each outer central role loses rank `p` and each middle central role loses
rank `q`; this gives the displayed `L`. The label-dimension telescope is
`Wm-2N+2L`; the extra rational source correction gives `s`. In the uniform
case these formulas become exactly the reviewed `W=2N+2v^2(R+h)` and
`L=3v^2h^2`. The independent checker verifies this regression at all 11
screened even grounds.

The selected circuits have `p=52,q=48,Rp=549120,Rq=426624`.

| Quantity | Exact value |
|---|---:|
| `N` | 8,447,539,360,000 |
| `m` | 129,792 |
| `W` | 435,202,334,195,200 |
| `L` | 3,192,459,212,800 |
| `N-2L` | 2,062,620,934,400 |
| `s` | 56,485,779,297,242,464,000 |
| Relative rank deficit | `8629/236308959744` |
| Joined physical auxiliary roles | 209,916,383,955,200 |

The complex primitive remains the original `h=50` network.
`05-layers.tex`, lines 473-478, explicitly allows its constants to differ
from the chunk-swap constants. The finite bit dimensions and saving
therefore change only the corresponding bit recurrence parameters.

The checker reads the saved witness without importing its producer. It
independently recomputes counts, longer rational logarithm enclosures,
the balance-root signs, 30 strict recurrence/guard/Gaussian constraints,
every exponent margin, the gamma cutoff, and strict final absorption.
It verifies

```text
kappa = 6412736146231 / 10^30 > 3.696690703179 * 2^-59.
```

All 121 primitive savings have independent disjoint rational enclosures
showing that `p=52,q=48` is uniquely best within this screened grid. This
is a finite-grid comparison, not a global optimum over constructions.
The slight improvement over uniform `h=50,R=486200` is about 0.136% in
the resulting saving. The all-size analytic scope and very large eventual
cutoff `b>=2^7340032` are those of the retained LU review.

## Evidence, limitations, and reproduction

The pinned v1 source's `joining_certificates.joined_roles` field counts
paired invocation banks `vp*vq`, not physical registers. Main counts are
correct. The independent result names both quantities explicitly. A
parent v2 metadata repair can rename this field without changing arithmetic;
the original v1 evidence should remain available.

The large individual graphs at `h=48,52` have parent full coefficient and
frame certificates. This review reads their role counts as finite inputs
and audits their tensor transfer; it does not repeat those complete large
graph expansions. The earlier independent `h=50` envelope audit and the
complete unequal small scalar calibration exercise the same compiler
rules. A headline still requires the large finite certificates and the
separately reviewed all-size analytic proofs.

Fresh independent evidence and environment details are in
`runs/20261007T234400Z-review-asymmetric-motifs`. Reproduce from the
repository root, with the pinned v1 source certificate:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/integer-multiplication-bounds/code/review_asymmetric_motif.py \
  --certificate "$ASYMMETRIC_V1_CERTIFICATE" --output "$OUT"
```

The independent checker uses only Python's standard library and the
retained review logarithm helper. Actual executed interpreter:
CPython 3.14.4. No invalid tensor joining or parameter inequality was found.
