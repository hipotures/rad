# Paired five-coordinate cubes: scalar correction and the first complete side baseline

This is a new structural hypothesis prompted by the paired-cube PR163 review.
It combines that paper's paired-label architecture with this campaign's earlier
odd-weight polynomial family. It is not an adopted external exponent.

**EXACT FINITE EVIDENCE:** a literal in-place dyadic source-bank correction,
its inverse and complete temporary bounds pass; every pair-star center at four
selected sizes has the claimed nondegenerate source frame. A completely
specified independent-edge side recipe has a counted child profile.
**REFUTED WITHIN STATED SCOPE:** that independent-edge recipe cannot reach
complex saving `b >= 1/10000`. The smaller hypothetical capacity bounds are
necessary sensitivity estimates, not attained profiles or kappa certificates.

## Cube identity and paid source-bank implementation

Select one coordinate from each of five distinct coordinate pairs. With p
pairs, `h=2p` and `v=32 binom(p,5)`. Set

    f(t)=(t-1)(t-3)/8,       B[T,S]=f(|T intersection S|),
    B_cube = B restricted to each same-five-pair cube,
    K=I-B_cube,              H=B_cube-B.

Then `K+H+B=I`. Outside a common cube, H is nonzero only at intersection
0, 2 or 4, with coefficients `-3/8, 1/8, -3/8`. Its sources are therefore
orthogonal to the relevant target. K exchanges selector parity classes inside
each cube and is an exact involution.

For a selector u on the first four pairs, the even source is
`(u,parity(u))`, while its assigned odd target row is
`(u,1+parity(u))`. The resulting sixteen-bank block is

    Q = H_4 diag(-1 for weight <=2; +1 otherwise) H_4 /16,

where H_4 is the unnormalized sixteen-by-sixteen Walsh matrix. It has amplitudes
of magnitudes 1/8 and 3/8, so it is not a single Clifford frame. The independent
source verifies every entry and `Q^t Q=I`, as well as its literal inverse word.

Each Walsh butterfly on existing banks a,b is implemented as

    a += b;       b *= -2;       b += a.

Both Walsh words, every sign and every final division by sixteen are paid.
There are 219 gates per parity block: 128 additions and 91 scales. Thus one
whole cube needs 438 gates for mutation and another 438 for unmutation,
or `219v/8` scalar gates per local invocation including the inverse. No clean
or extra source bank is introduced.

Every source bank of one selector parity is first raised from its line to the
same **actual** representative F_U, where U has rank five and radical four.
All operations of Q stay within that representative. Its output rows are
assigned to opposite-parity targets while their physical source slots and
current frame remain unchanged. Since U is contained in every such target cap,
the parked sources can later grow to those caps. After readout, all sources
reach the same full frame and Q is inverted in the original slots before
source cleanup. The source child widths are `[4,h-6,1]`.

The two parity classes have different U. There is no scalar gate between
those two actual frames and no unpaid parity-bank exchange. This is fixed
role-bank arithmetic pointwise across the complete address stream. It is not
`Q^tensor f` on an exponentially growing bank alphabet and is not a pair of
recursive rank-five address-transform calls.

The observed exact row-L1 prefix maxima, including all multiplication
temporaries, are 64 forward and 32 inverse. Both use at most three extra
fractional bits. The endpoint row-L1 norm is 7/2. Four Gaussian fields and both
real/imaginary components return exactly under the inverse. Omitting the final
normalization rejects. Actual record movement, current-frame compilation and
complete scalar bit implementation still need their native bills.

## Pair-star centers

There are `q=2p(p-1)` nonpartner coordinate pairs. For fixed i,j, put
`w=e_i+e_j`. The pair star comprises `w+u`, with u a three-coordinate paired
label on the remaining p-2 pairs. For the tested sizes and, by the same span
argument, p>=7, those u span the outside coordinate space. The star therefore
has the explicit basis

    e_c+w,       c outside both fixed coordinate pairs.

These vectors are orthonormal: w has norm zero and disjoint support from c.
The center frame is nondegenerate with rank `h-4`, and the conservative copied
center loss is `q(h-4)`. This differs from PR163's singleton-star radical-one
frames.

Let P_ij be the complete sum of source ports containing i,j. Each source lies
in ten such stars, and each containing coordinate occurs in four pair stars.
Consequently the following decoder equals f(intersection) exactly:

    alpha_ij(T) = 1/4 [i,j in T] -3/32([i in T]+[j in T]) +3/80.

Its three values are `1/10, -9/160, 3/80`. The common grid is 1/160 and the
fixed odd divisor is five. PR163's divisor-three precision construction cannot
be inherited unchanged. The positive copy/frame bill is a conditional use of
the retained center interface, not a newly verified native implementation.

The four-worker discriminator checked all center spans at p7/8/9/12 and
1,448,960 direct central entries. At p7 it checked the complete central matrix;
larger cases checked the declared first 32 target rows against every source.
All centers had radical zero. The full run took 1.261 seconds.

## First complete side recipe and its failure

The baseline uses one independent dirty side carrier for every nonzero
directed H edge, and one independent source-copy carrier for every pair-center
incidence. There are ten center incidences per source. All V copies occur
while the original source retains its own line. No source is assumed clean.

For each side edge S-to-T, the carrier follows

    zero -> line(S) -> T-perp -> full,

with widths `[1,h-2,1]`. Each center uses its first copied leaf as pivot. For
each next leaf, both pivot and incoming leaf grow to their actual span union;
the leaf is added into the pivot, and the incoming carrier then retires at
full. The pivot finishes at its actual rank-h-4 star, pays the copied-center
call, and reaches full. All prefix spans and both participating chains are
counted. The center phase finishes before all side reads. Each target's side
reads use only its own line as annihilator, so target chains remain nested;
their one positive width is `h-1` per target.

The literal scalar recipe is `V`, the independent center sum trees M, and the
edge/center decoder J. It verifies `JMV+K=I` on every source pair. Its arbitrary
dirty echo is `-JMz`, followed by source injection, M and `+Jz`, then reversed
M and source subtraction. Old JM formation and its inverse are charged; the
early correction is not a free precomputed sum. All mutated original sources
are unmixed before that cleanup. Tests use both shear signs and all four
Gaussian fields; dropping an old correction changes the output and rejects.

Under the inherited complete-core/role-cover interface, the ledger is

    R = directed_H_edges +10v,
    W = 2v+R,
    child_histogram =3(local+original_source+target)+2v calls of width2,
    rank =3hW-2v+3q(h-4).

There are no gauges or aliases. This is a complete finite rank recipe with
explicit scalar/frame chronology, rather than a freely chosen R/v. It is
still not an execution of the whole Gaussian address program or ambient
group. Its reuse of the generic completed-core lift, odd-five grid and global
native movement remains conditional. Additional costs cannot repair the
negative moment conclusion below.

At p9, all 16,257,024 source pairs and every center prefix were checked:

| Quantity | Result |
| --- | ---: |
| h / m / v | 18 / 54 / 4,032 |
| Nonzero side edges per target | 2,000 |
| Side carriers | 8,064,000 |
| Center source-copy carriers | 40,320 |
| Persistent W | 8,112,384 |
| Complete rank | 438,066,720 |
| Copied center loss / rank deficit | 2,016 / 2,016 |
| K mutation plus inverse scalar gates | 110,376 |

The complete scalar recipe conservatively counts four center M/M-inverse
passes, both source injection/subtraction, both old/new edge and center reads,
and both K words. This totals 33,768,936 scalar operations per completed local
invocation before additional phase, precision and native routing charges.
The native model must move every complete record and spectator field.

Every positive child has `r<=h-1`, so `log(m/r)>log(3)>1`. For b>0,

    Phi(1-b) > (rank/(mW)) (1+b).

At `b=1/10000` the exact lower bound is
`434633459/434592000 >1`. More generally, this profile necessarily requires
`b<21/4563195`, about `4.60e-6`. It therefore fails the campaign's first
complex threshold by a large margin. The full four-worker run took 1.071
seconds. This is a useful negative baseline for sharing work, not a claim
that paired-five constructions in general cannot improve the exponent.

## Capacity and continuation criterion

If a future shared side word actually achieves the same center loss, stock
`W=2v+R` and maximum child at most h-1, then its necessary capacity conditions
include the following floating sensitivity estimates:

| p | R/v ceiling for b=0.0001 | R/v ceiling for b=0.001 |
| --- | ---: | ---: |
| 9 | 78.118 | 6.016 |
| 10 | 132.594 | 11.466 |
| 11 | 156.311 | 13.839 |
| 12 | 165.357 | 14.744 |

These are necessary only, conditional on the stated full ledger and maximum
child. They give no sufficient moment bound. Small p7/p8 have negative deficit
under these copied centers, even before investing in a side sweep. A final
integer-product kappa also needs a stronger binary supplier and the complete
transfer; b=0.0001 by itself is not kappa=0.0001.

The next task is a genuinely shared side chronology, with actual common
frames and compatible target flags. A promising local observation is that
both H and B annihilate high selector-degree channels, but a dense source
basis change cannot be treated as free. No parameter sweep is justified by
the unattained capacity table alone.

## Reproduction and attribution

The independent sources are standard-library Python. The original paired
architecture and K source itinerary are attributed to icekylinx's PR144 and
the read-only PR163 package. The odd-weight family was explored independently
in this campaign's earlier polynomial reports. The scalar-bank word and this
baseline are authored here with OpenAI Codex assistance. No priority claim is
made for standard Walsh diagonalization or elementary dirty linear echoes.

Portable bounded checks are:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/paired_five_cube_discriminator.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_five_complete_baseline.py --workers 1 --bounded
```

Removing `--bounded` regenerates the retained full cases; `--workers 4`
requests the natural four-worker split. Optional `--output NEW_PATH` writes a
fresh certificate. The immutable full runs are
`20261009T082807Z-complex-paired-five-discriminator` and
`20261009T084849Z-complex-paired-five-complete-baseline`.
Source closure, exact commands, original hashes and outcome scope are recorded
in their protocols. The scalar word is not optimized for gate count. No failed
execution, source patch or discarded numerical result occurred.
