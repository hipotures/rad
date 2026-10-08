# Independent review: reflected joined-block moments

The already accepted reflected h51 construction with R500703 admits the
stronger explicit primitive saving `a=16368437325414951/10^24`, approximately
`1.6368437325414951e-8`. This sharpens the lower bound on moments of its
existing canonical pivot runs. It changes no scalar circuit, frame,
fixed address table, runtime operation or recursive depth bound.

The independent [source](../code/review_joined_block.py),
[protocol](../runs/20261008T0603Z-review-joined-block-drain/protocol.json)
and [exact certificate](../runs/20261008T0603Z-review-joined-block-drain/results/certificate.json)
are frozen. The certificate SHA256 is
`157708ae64eaeada9e7855c048d7525441c17c97cc2731d5add05035fbe0e78d`.
The source SHA256 is
`ed0f6d743f8250e8964356c1d215d68de50a7bb5b329089af392aae95d42fb10`.

## A proof-only lower transformation

Use the accepted axis cycle and all-ones reflection from
[the reflected-basis review](review-reflected-basis.md). Let
`P_X=u_X v_X^T` be the resulting line projectors; every first source
coefficient and last dual coefficient is nonzero. A joined residual is

`A=I_h tensor B-P_B tensor T`,

where `B=I_(h^2)-P_B tensor P_C`, `T=I_h tensor P_A` and `P_A P_C=0`.
Write `s=h^2`. Choose unit lower matrices S and R by

`S_(i,0)=-u_B(i)/u_B(0)` for i>0,

`R_(h-1,j)=-v_B(j)/v_B(h-1)` for j<h-1.

They satisfy `S u_B=u_B(0)e_0` and
`v_B^T R=v_B(h-1)e_(h-1)^T`. Thus, with the unit lower matrix `D=SR`,

`(S tensor I) A (R tensor I)
 =D tensor B-c e_0 e_(h-1)^T tensor T`,

where `c=u_B(0)v_B(h-1)` is nonzero. Left and right invertible lower
multiplications preserve the canonical lower/lower profile. These
matrices are used only to prove that profile; they are not added to
the actual address table or physical schedule.

## The interior profiles survive elimination

The first outer block has entries only in block0 and the last block.
When its rightmost pivot lies in the last block, the corresponding
column is zero in every interior outer row. Its column elimination
also has zero coefficients for all interior-block columns, since
the pivot row has zero entries there. When a first-block pivot lies
in block0, its last-block tail is necessarily zero: otherwise its
rightmost pivot would be in the last block. Its operations then affect
only block0 or earlier columns. Therefore processing the first block
does not change any interior diagonal block B.

Induct over outer blocks1 through h-2. A preceding normal pivot row
has support only in its own or earlier blocks. A row whose local B
part becomes zero can pivot in an earlier block, but cannot change
any later diagonal block. Consequently every one of these h-2
interior blocks retains the complete local canonical profile of B.
The proof permits interleaving of first-block and last-block spike
pivots; it does not require all spike pivots to occur first.

The reflected tensor line has a nonzero first source coefficient and
last dual coefficient. Its rank-one-complement profile is
`(0,s-1),(1,1),...,(s-2,s-2)`. Each interior block therefore contains
one maximal diagonal run of length `s-2`. The first local pivot is
off the diagonal and its final local row is not a diagonal pivot, so
the run cannot merge across either block boundary.

## A disjoint Jensen remainder

The existing low-rank bound guarantees at least `m-4h` diagonal
pivots in at most `4h+1` maximal diagonal runs for each joined residual.
Remove the h-2 known maximal runs just proved. The remainder has at
least

`t_rem=m-4h-(h-2)(h^2-2)=2(h-2)(h+1)`

diagonal pivots and at most `g_rem=3(h+1)` runs. At h51 these are
5096 and 156; their ratio is greater than1. Convexity of `r ln(r)`
therefore gives the following conservative first moment per joined
residual:

`(h-2)(h^2-2) ln(h^2-2)+t_rem ln(t_rem/g_rem)`.

If the actual remainder has more diagonal pivots or fewer runs,
this expression only increases. The known runs and remainder are
disjoint; no off-diagonal pivot is credited to this lower bound.
Multiply by the exact joined multiplicity `(R+h)v^2`, and retain the
already reviewed reflected middle and data moments.

## Exact evidence and transfer limits

Three complete rational joined matrices at h5, h5 and h7 reproduce
the proof-only tensor transformation entry by entry and have exactly
the same canonical profile before and after it. Every interior
profile, known maximal run, remainder count, rank `m-2h` and spaced
kernel hole is checked. A negative control verifies that the first
outer block is not another untouched copy of B.

The characteristic check independently reconstructs N, W, L, D and s
from the accepted R500703 counts. It encloses logarithms using safe
64-term rational intervals, rounds lower bounds downward to a
`2^-256` grid, and verifies the strict normalized inequality

`D-a(s ln(m)-M)-a^2 s ln(m)^2/[2(1-a ln(m))]>0`.

Here M is the reviewed lower bound on all credited first moments,
and every occurrence of an upper logarithm is enclosed in the
conservative direction. The resulting exact rational a above is
strictly larger than the accepted reflected predecessor.

The maximum child remains `h^2(h-2)=127449<m=132651`. The retained
uncapped proof uses `W^D<p^2600` and the sufficient reservoir condition
`b^(1-epsilon)>10400(log2(b)+8)`. All fixed-tape main/tail placements,
volume V/W, row padding, activation restoration, common-frame
telescoping and prime/setup qualifications are inherited unchanged.
The separate complex numerical guard is unchanged. A fresh complete
parameter assembly must consume this characteristic before a new
multiplication kappa is promoted.

The executed Python3.14.7 run used one worker, one numerical thread,
a 16GiB address-space limit and a 120s timeout. It took 0.99s with
57644KiB peak RSS and zero swaps, then released its owned reservation.
Two earlier attempts failed only at CPU admission before a scientific
child was launched; their protocols and failure reports remain at
run0558 and run0600. The successful run records the finite agent's
explicit stopped-admission drain handoff and actual live-worker count.
