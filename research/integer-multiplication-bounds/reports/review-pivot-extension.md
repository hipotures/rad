# Independent fine-grid and stage3 batching review

The finer two-family primitive witness

`a=1058685652786963/(2*10^23)`

is accepted. A disjoint stage3 data-edge family additionally supports

`a=5385522401708297/10^24`.

Both use the completed [contiguous-pivot transfer](review-contiguous-pivot-transfer.md)
on the independently accepted h51 R502265 bit network. This report audits
the exact characteristic arithmetic and the additional physical family.
It does not assert a composed integer-multiplication kappa. The finite
network and the separate complex transform remain unchanged.

## Independent fine-grid calculation

The producer's direct characteristic difference is

```text
F(a)=W*m*exp(-a*log(m))-sum_r n_r*r*exp(-a*log(r)).
```

For a>=0, `exp(-x)>=1-x` and `exp(-x)<=1-x+x^2/2`. Thus a sufficient
strict lower bound is

```text
D-a*(W*m*log(m)_upper-M_lower)
 -a^2*s*log(m)_upper^2/2 > 0,
```

where `D=W*m-s` and `M_lower` bounds the actual rank-log moment below.
This negative-exponential proof is valid as written. It does not require
the denominator that appears in the separate positive-exponential
normalization used by the independent review. The latter independently
checks the stronger explicit remainder bound

```text
D-a*(s*L_upper-M_lower)
 -a^2*s*L_upper^2/(2*(1-a*L_upper)) > 0.
```

The fresh checker imports no producer characteristic function. It
reconstructs the finite counts, the complete middle histogram, the joined
Jensen lower bound and independent 64-term rational logarithm enclosures.
It then checks the producer's exact fine-grid a with the latter inequality.
The strict normalized gap is greater than 141,322. The producer's larger
linear coefficient supplies more than enough allowance for the different
positive-exponential remainder. This is an exact rational comparison;
the displayed integer is only a floor of the retained positive gap.

The two-family input has

```text
h=51, v=20825, m=132651, R=502265
W=453752231686250, s=60190685022033566875
D=2263379181875.
```

The accepted joined kernel holes preserve `rmax=h^2-1=2600`, even for the
uncapped fine-grid moment using only `4h+1=205` joined diagonal runs.
Arbitrary integer widths, original prime/factors, complete rows and the
fixed-tape recursive schedule are exactly those of the preceding transfer
report. No reinterpretation of this a as `1-log_m(s/W)` is allowed.

## Disjoint stage3 data residuals

In the original section 03 coordinate order, let
`A12=F tensor F`, let `P12` project onto
`line(t_1 tensor t_2)`, and put `B12=I12-P12`. Let P3 project onto the
third indicator line. Stage3 has no remaining future tensor factor.

The physical X data wire has incoming projector `I12 tensor P3`; its
time-2 gate has projector `B12 tensor I + P12 tensor P3`. Their difference
is `B12 tensor (I-P3)`.

The physical Y data wire's time-0 gate has projector `B12 tensor P3`, and
its time-1 gate has projector `B12 tensor I`. Their difference is the same
matrix. The second family is Y **0->1**, not Y incoming->0, whose difference
is zero. Original stage2 reversal and bank exchange supply these stage3
incoming labels; the accepted finite scalar compilation preserves the
external data chronology while changing only side-register allocation.
The negative source projection exception occurs in stage1, so it does not
affect these two stage3 edges.

There is one edge of each kind for every data index, hence exactly 2N
copies. These are data-wire edges; the earlier two families are final
middle auxiliary sinks and shared first/third auxiliary joins. The three
families are disjoint physical edges.

Let `R3=B12 tensor (I-P3)`. Both tensor factors are nondegenerate
orthogonal complementary projections, so

```text
rank(R3)=(h^2-1)*(h-1)=130000
d3=m-rank(R3)=h^2+h-1=2651.
```

The complement `I-R3` is a projection of rank d3. Applying the proved
low-rank diagonal-profile theorem gives at least
`t3=m-2d3=127349` diagonal pivots in at most
`g3=2d3+1=5303` runs per edge.

The residual annihilates `e_i tensor e_j tensor t_3` for every i,j. Its
earliest nonzero kernel coordinate is `k=(i*h+j)*h+min(t_3)`; all other
support columns are later. The exact suffix-rank argument therefore
forbids this pivot column. There is one hole in every h-column block, so
every increasing contiguous pivot run has length at most h-1. No larger
child is needed for the new data family. The global largest run is still
the joined bound h^2-1, and the same `ceil(log_h e)` row depth applies.

These facts do not depend on a particular triple support or on a positive
definite ambient rational metric. They depend on the original nondegenerate
indicator lines and the fixed tensor coordinate order. Dropping the
third-factor perpendicular condition changes the rank to
`(h^2-1)*h`; it is not a valid replacement for the physical residual.

## Three-family exact bound

There are `2N=18062798031250` new data edges. Their old total rank is
`2348163744062500000`. This fits strictly within the previously unchanged
rank after removing the middle and joined families. The complete rank
sum remains s: no rank saving is introduced by simply repartitioning
pivots into groups.

The new contribution to the actual rank-log moment is at least

`2N*t3*log(t3/g3)`.

Adding this lower bound to the already proved middle and joined moments
gives the accepted kernel-hole a displayed above. The fresh independent
positive-exponential bound has strict normalized gap greater than 143,780.
The conservative capped variant also passes independently at
`a=1326086397164473/(2.5*10^23)`, with gap greater than 141,613.
That variant adds at most `ceil(130000/2601)=50` pieces, giving g3=5353;
it is retained separately and not substituted into the sharper kernel-hole
row. All logarithms and strict inequalities are exact rational enclosures.

## Executed evidence and recovery

Fresh [source](../code/review_pivot_extension.py), SHA256
`7928f9bb07744dfe10b475b536eb77d9d9d7b6ae565f981b0310d881c2d507d0`,
and [protocol](../runs/20261008T0454Z-review-pivot-extension/protocol.json)
reconstruct all three count/moment witnesses and three full exact rational
stage3 matrices at h6, h7 and h8. Across them, 852,898 gate-edge matrix
entries, 149 kernel column relations and all rightmost pivot profiles are
checked independently. Their ranks are respectively 175, 288 and 441.
Their actual increasing-run maxima are 4, 5 and 4, below the proven h-1
bound. Both X and Y physical gate differences are compared entry by entry.

The [certificate](../runs/20261008T0454Z-review-pivot-extension/results/certificate.json)
has SHA256
`b4962136b2b0e1a3f6ce9b05f9e28097a9b767fee1b4e96fef0978c828c95865`.
Execution was terminal PASS in 1.96 seconds, with one CPU worker,
Python 3.14.7, 36,708 KiB peak RSS and no swap. The owned reservation was
released in the recorded finally block. The timeout was 120 seconds and
the address-space cap was 16 GiB.

The producer witnesses are immutable inputs from
`20261008T043510Z-downstream-diagonal-join-bound` and
`20261008T044503Z-downstream-diagonal-data-bound`. The checker verifies
their source digests and their accepted h51 finite input hash before
evaluating the witnesses. Reproduce the recorded command with a fresh
output path and the pinned dependencies. System Python has an integer
string conversion limit below the largest retained exact fractions; the
authored checker explicitly removes that limit before decoding them.

No giant h51 matrix or full multiplication implementation was executed.
The all-size projection, profile, hole and physical multiplicity arguments
above establish the new family. A composed numeric cutoff must still
include complete-row reservations and the retained eventual setup
thresholds; its mathematical interfaces are unchanged from the positive
two-family transfer. Parent publication owns commit/push and remote
verification. The original campaign clock and the active user extension
are retained in the protocol.
