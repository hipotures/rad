# Aligned global pairings: a finite-circuit improvement

## Result and status

At ground size `h=50`, aligning each common-point circuit with one fixed
global pairing reduces side roles per invocation from **509,194 to 494,250**.
The local paired recursion still uses 9,813 additions. The change increases
cross-common-point sharing from 40,256 to 55,200 merged additions. The retained
global graph has 435,450 additions and 58,800 designated partial outputs.

Under the pinned construction's source-span/complement-frame transfer,
stopped guard, tight Gaussian setup, and unchanged multiplication interfaces,
an exact strict witness is

```text
kappa = 738998782479 / 400000000000000000000000000000
      = 1.8474969561975e-18
```

This is approximately 1.0650 times `2^-59`. This is a genuine change to the
finite circuit: the downstream recipe is unchanged. The certified limiting
margin increases by the exact factor `93025/87616` relative to the pinned
limiting margin, approximately 1.06175. The witness retains explicit strict
slack of one part in one thousand below its own limiting margin. The complete
upstream multiplication theorem remains an assumption, and novelty beyond the
pinned repository has not been established by a literature review.

Reference: [CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds),
immutable commit `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, inspected
2026-10-07. The starting published claim is conditional `kappa=2^-59`, with
exact limiting margin `272158569/156250000000000000000000000`.

## Construction

Pair the global vertices as `{0,1},{2,3},...,{48,49}`. For common point `i`,
order its other points by listing all pairs other than `i`'s pair in the
original global order, then append its mate `i xor 1`. Thus the local paired
recursion groups intact global pairs and ends with a singleton. Apply the
unchanged weighted paired recursion, with direct base cases of at most four
vertices, to this ordering.

Identify the same physical triple inputs across groups. Identify equal
addition supports using the pinned exact pair-star rule: a sum shared across
two common points has a fixed pair and a set of remaining vertices. Preserve
the first encountered decomposition and compile the physical reversible roles
from the resulting graph. No occupied roles are identified directly.

Every local graph still computes the complete leave-two-vertices-out pair map.
Reordering its points permutes the inputs and outputs consistently. Each
neighboring source/target triple pair contributes to exactly the group of
their unique common point, so the global map remains the intersection-one
correction.

## Frames, restoration, endpoints, and rank

Every retained addition support still consists of triples sharing a point
`i`. If `U` is their rational indicator span in the original form `I-J/9`,
then every `u in U` satisfies `sum_j u_j=3u_i`, and

```text
<u,u> = sum_(j != i) u_j^2 > 0 for nonzero u.
```

Consequently all source spans are nondegenerate. Directed graph edges give
increasing source spans; the reverse graph gives increasing orthogonal
complements. The complete graph checker follows every compiled role and
checks both inclusion directions. Output support orthogonality supplies the
original target boundaries. Early and late mixers use the same original low
and high frames. The physical data frames and central operations are unchanged.

The reversible compiler uses `c+q=494250` roles. The original schedule

```text
L, J, inverse L, R0, V, G, R0, L, J, inverse L, G, V
```

gives `JLz+JL(z+Vx)=JLVx` for arbitrary initial scratch `z`; cleanup restores
all scratch and center values. The exact complete linear map is checked on
every data and dirty-scratch input basis vector at `h=6,8`, in both stage
orientations. Independently expanded global support sets check all small
coefficients. Complete three-stage shared-bank exchange checks at `h=6,8`
use payload seeds 1 and 109. An additional `h=10` run checks both dirty-input
bases and a complete shared-bank exchange with seed 109.

The unchanged `h=50` triple matching is checked on all 19,600 triples for
bijection and intersection-one orthogonality. It supplies the same nested
first/third-stage auxiliary joins. Every surviving auxiliary role retains
endpoints `0,I_m` and its scalar value is restored; data endpoints are
unchanged. The only decreasing dimensions remain the central returns.

With `v=19600`, `N=v^3`, `m=125000`, and `R=494250`, the exact counts are

```text
W = 2N + 2v^2(R+h) = 394839648000000
L = 3v^2h^2 = 2881200000000
D = N - 2L = 1767136000000
s = Wm - D = 49354954232864000000
eta = D/(Wm) = 23/642375000.
```

Telescoping gives absolute label change `Wm-2N+2L`; the unchanged source
correction contributes rank `N`, giving total edge rank `s`. Thus no role
saving is credited without the corresponding endpoint and rank argument.

## Downstream certificate

Exact rational log bounds give `log(m)<11737/1000`. The bit deficit supports
`a_b=305/10^11`, with exact slack
`eta-a_b*(11737/1000)=696977/102780000000000000 > 0`. The unchanged `h=50`
complex motif supports `a_c=1/10^11`.

Use the pinned recipe with `epsilon=199/1000`, `beta=999/1000`,
`delta=1/10000`, `C1=2`,

```text
c = beta*a_b
lambda = 1 - (1+beta)*a_b^2/2
lambda' = 1 - beta*a_b^2.
```

All strict constraints pass. The limiting margins are exactly
`g2=g3=739738521/400000000000000000000000000`; the displayed `kappa` is
`999/1000` times this value. These arithmetic checks are conditional on the
same written downstream proof extensions as the starting paired construction.

## Bounded negative results and continued search

Simple uniform blocks of size 3, 4, and 5 at local `n=49` use respectively
12,590, 15,319, and 13,813 additions, versus 9,813 for pairs. A complete
486-case scan of three-level block schedules in `{2,3,4}`, direct base
thresholds 2 through 7, and three output parenthesizations found no substantial
local improvement: the best circuit has 9,812 additions (pair blocks and base
2 or 3), a one-addition saving. This is a bounded family screen, not a lower
bound for arbitrary circuits.

Alternative orderings at `h=50` gave 533,425 roles for cyclic point order and
548,169 for independently randomized point order (seed 109), versus 509,194
for natural order and 494,250 for the globally paired order. This directly
discriminates alignment from arbitrary relabeling.

The next local direction is joint factoring of all pair-star sums used by
different common-point groups, plus heterogeneous or tree-aligned local
orders. These preserve the proven common-point nondegeneracy condition.

## Artifacts and reproduction

- [Exact witness](../runs/20261007T223510Z-finite-aligned-pairing/results/certificate.json).
- [Local schedule scan](../runs/20261007T223650Z-finite-block-schedules/results/summary.json).
- [Circuit generator and complete-map/frame checker](../code/finite_block_search.py).
- [Strict witness and small dirty-scratch/stage checker](../code/finite_pairing_certificate.py).
- [Bounded parallel schedule search](../code/finite_scan.py).

Python 3.11+ and the explicitly pinned reference checkout suffice; no external
packages, compiled binaries, or model weights are needed.

```bash
python3 research/integer-multiplication-bounds/code/finite_pairing_certificate.py \
  --reference /path/to/integer-mult-bounds \
  --output /tmp/aligned-pairing-certificate.json
```

The witness run completed in 31.17 wall seconds during concurrent bounded
searches. The local schedule scan used two workers, took 32.95 wall seconds,
and recorded 65.16 summed per-case wall seconds. No GPUs were used. The extra
`h=10` full scalar test took 76.28 wall seconds and exercised 62,208,000
physical roles in the small three-stage model.

All graph and evidence files are deterministically regenerable from the
pinned source and the authored scripts. Raw probe and scan evidence is in the
campaign's external `derived/finite/` directory; it will be published through
the repository's completed-text evidence path by the coordinating agent.
