# Recycle retired guards into a recursive row pool

Status: **EXACT FINITE ROW LIFECYCLE AND CONDITIONAL ALLOCATION/RECURRENCE**.
No complete canonical Gaussian scalar network, new precision theorem or
larger multiplication exponent is established.

## The row-capacity gap

The [two-guard layout](frozen-control-selected-bit-reversal.md) makes a
nominal full-width child strictly smaller: e'=e-2h-u. Strict integer
decrease permits induction, but its worst depth can be Theta(d), rather
than O(log d). The pinned original layers section supplies its role rows
using an O(log d) preprocessing block and proves a polynomial node count
for its own geometric recursion. Neither argument automatically covers
these full-rank chains. Preprocessing Theta(d) selected bits individually
would instead consume the intended sublinear local allowance.

The proposed change recycles complete guard chunks which the current
invocation has already transformed. This is an allocation mechanism on
the existing complete address volume. It does not add independent address
bits or assume extra clean scalar roles.

## Allocation contract and row recurrence

Fix h, W and a whole-stream scalar network with W physical roles. At a
node, assume e=2h(g+1)+u, g>=1 and 0<=u<2h. Apply elementary C kernels
to the two terminal selected bits in each old slot and to the u remainder
bits, using fewer than 4h complete-stream kernel scans. There are
t=2h+u complete K-bit chunks to retire. The completed active network
must act only on the remaining selected bits and be independent of the
retired guard values. Every address companion is restored before its
gate endpoint. These are required operator hypotheses.

If the previous row range is R_old>=1, concatenate those complete retired
chunks into that row index, leaving every active and spectator range
complete. The new row range is R_old*2^(tK); the suffix is smaller by the
same factor, so the record volume is unchanged. Pad this range to the
next W multiple, then split row u=Wg+w into physical role w. Each role
has the same complete suffix and

```text
R_child = ceil(R_old*2^(tK)/W),
padding fraction < W/(R_old*2^(tK)) <= epsilon_K := W*2^(-2hK).
```

This produces complete role rows at every depth. Whole-chunk compaction
must carry the row/active/spectator descriptors and be undone after the
child; reindexing is not a free payload operation. Mixed-radix row splits,
padding, copies and recombination are paid full-stream passes with local
descriptor work. The completed active-only operator commutes with the
retired guard C kernels. Added zero rows finish zero and are removed only
after the invocation's complete endpoint. An intermediate dirty value is
not evidence that a padded row may be deleted early.

There are at most d strictly decreasing nodes on a root-to-leaf path.
Consequently pathwise padding inflation is at most
(1+epsilon_K)^d <= exp(d epsilon_K), tending to one when
K/log(d) tends to infinity. This statement does not bound the unweighted
number of nodes: that number can be exponential in d.

## Conditional stopped moment transfer

Assume each complete network has n_r rank-r child calls, each on at most
(1+epsilon_K)/W of the current volume, for 1<=r<=h. Their selected sizes
e_r are strictly smaller than e and satisfy e_r<=r e/h. Rank-zero work
is charged to local overhead. Suppose a fixed p in (0,1) satisfies the
strict paid moment

```text
m_p := sum_(r=1..h) (n_r/W) (r/h)^p < 1.
```

Fix beta in (0,1), K<=d^c, and local exponent tau>0 with
tau(1+c/beta)<p. Assume all complete payload movement, scalar work,
local metadata and required precision fit O(V((eK)^tau+1)) uniformly
above e>=d^beta. Below that threshold, elementary kernels cost O(Ve).
For sufficiently large d, (1+epsilon_K)m_p<1.

Strong induction on e then bounds time divided by stream volume by

```text
F_d(e) <= A d^(beta(1-p)) e^p,
F_d(d) = O(d^(p+beta(1-p))).
```

The base bound follows from e^(1-p)<=d^(beta(1-p)). At an internal node,
the inductive child bill is at most (1+epsilon_K)m_p times that potential.
The local bill is O(e^lambda) for a fixed lambda strictly between
tau(1+c/beta) and p, and is absorbed by the remaining uniform moment
margin. Choose A large enough for both constants. Strict size decrease
justifies this induction even at r=h; no logarithmic-depth or polynomial
node-count assumption is used.

A nonstrict moment does not suffice. The recurrence
F(e)=F(e-1)+e^lambda has one strictly smaller full-rank child but costs
Theta(e^(lambda+1)). Thus geometric allocation alone cannot certify a
power saving. The n_r, actual complete network, native local bill and
precision contract above remain unsupplied inputs of this conditional
theorem. Its exponent is for selected transform width, not a multiplier
kappa certificate.
