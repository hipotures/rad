# A subset-zeta primitive and its first center-release boundary

Status: **EXACT TRANSFER ALGEBRA AND RESTRICTED ALL-SIZE OBSTRUCTION**.
There is no faster native zeta supplier, new coupled recurrence, or
multiplication exponent in this result.

## Alternative primitive

Let `Z_e=[[1,0],[1,1]]^tensor e`. It adds a source only toward the
upper endpoint of each selected Boolean edge. It is directional,
nonunit and determinant one, making it a different synthesis target
from the Gaussian complex transform.

Writing `alpha=(1+i)/2` and `D_i[x,x]=i^wt(x)` gives the exact identity

```text
C_e = D_i^-1 * alpha^e * Z_e * diag((-2)^wt) * Z_e^T * D_i^-1.
```

Indeed, `Z_e[i,j]=1[j subset i]` and the middle product has entry
`sum_(a subset i&j) (-2)^wt(a)=(-1)^wt(i&j)`, the Hadamard matrix.
The chirps and global normalization then give the actual dyadic C_e.
All coefficients, including that normalization, are part of the identity.

The transpose is `X_all*Z_e*X_all`; the inverse is
`diag((-1)^wt)*Z_e*diag((-1)^wt)`. These are operator identities,
not a free tape route. An independently faster **complete native Z_e
supplier** could consequently transfer its exponent to C through two
Z calls and the paid wrappers. Those calls must not be analyzed as two
same-size improved C oracles. A complete new Z/native recurrence is
still missing.

The naive factorization requires only O(e) extra guard bits, rather
than an unbounded coefficient oracle: Z passes have row L1 at most
`2^e`, and the middle diagonal has magnitude at most `2^e`. A coarse
whole-word prefix bound is `2^(3e)`. The common fractional grid can
reserve e bits for the final alpha power. Multiplying its unreduced
Gaussian numerator needs a further O(e) temporary allowance before
division. This is an algebraic guard bound, not verification of an
unsupplied faster Z algorithm's prefixes or actual full-record layout.

## Involutive signed-zeta anchors

Set `T_e=Z_e*diag((-1)^wt)`. Each one-axis factor is
`[[1,0],[1,-1]]` and squares to I. The tensor factors commute.
For a coordinate subset S, write T_S for its signed-zeta factors.
Then

```text
T_S^2=I,
T_full*T_S=T_(complement S).
```

A virtual signed swap with source anchors `(T_S,I)` and sink anchors
`(T_full,T_(complement S))` has complete raw outputs
`(T_full*y,-T_full*x)`. It needs no residual line repair in this
algebraic interface. An arbitrary dirty helper held at the appropriate
frame must still finish as its actual T_full-transformed raw input;
no whole helper word is supplied here.

The obvious hope is to use many width-k source anchors, saving k
endpoint ranks per role rather than one. The next screen rejects the
first shared-center geometry before costly synthesis.

## Point-star rank obstruction

Restrict common frames to coordinate subsets with nested geodesic
transport. A side transfer from source S to target T can remain on
that chronology only if
`S subset E subset complement T`, hence `S intersect T` is empty.
For `I=K+Q`, with K carried through shared central channels, this
requires

```text
K_SS=1,
K_TS=0 whenever S!=T and S intersect T is nonempty.
```

Allow any distinct nonempty coordinate-subset portfolio, unequal
weights, arbitrary complex K entries and cancellations. All labels
containing a fixed coordinate i form an exact identity principal minor
of K. Therefore `rank K >= n_i`, where n_i counts such labels. By
double counting,

```text
h*rank K >= h*max_i n_i >= sum_S |S|.
```

Under the proposed closed full-width center release, central loss is
at least `2h*rank K`, while the available source/sink saving is
`2 sum_S |S|`. It can never leave a positive first-moment deficit.
This argument does not require an unproved minimum-rank formula or
assuming the candidate K is optimal.

For all weight-k subsets, v=`binomial(h,k)` and every point-star has
size `binomial(h-1,k-1)=k v/h`. A concrete K is
`I+(-1)^(k+1)*A`, where A is the disjointness adjacency matrix.
The exact finite screen retains these candidates and their ranks:

| h | k | v | Identity-minor rank lower bound | Candidate rank | Candidate endpoint saving minus closed loss |
| --- | --- | ---: | ---: | ---: | ---: |
| 4 | 2 | 6 | 3 | 3 | 0 |
| 5 | 2 | 10 | 4 | 5 | -10 |
| 6 | 3 | 20 | 10 | 10 | 0 |
| 7 | 3 | 35 | 15 | 21 | -84 |

The zero cases identify a capacity boundary, not a positive exponent.
If a declared complete profile has first moment at least one, every
paid child width is at most the parent, and at least one proper child
is present, then its `1-b` moment is strictly larger than its first
moment for any b>0. No actual bulk profile or native circuit is
constructed from this table.

## Evidence, reproduction and next escape

The standalone producer plus read-only exact arithmetic dependency are
pinned in
[the four-worker run](../../runs/20261009T050015Z-synthesis-subset-zeta-primitive/).
It checks every C-factorization matrix coefficient at e4/e5/e6/e7,
all selected source/complement anchor columns and a dense integer field
for every label, all exact point-star minors and full candidate K
ranks. The signed-zeta operations retain both integer fields.
Omitting the weighted diagonal or incorrectly treating ordinary Z as
an involution fails. These are finite operator checks, not a replay
of an unsupplied complete many-role bulk word.

Maximum per-case runtime is 2.223 seconds with four workers. The raw
protocol, complete compact results and source hashes are preserved
unchanged; all matrix inputs are deterministically generated.

From the topic root:

```sh
python3 -B code/synthesis/subset_zeta_primitive_screen.py --workers 4 \
  --output work/reproduce/<fresh>-subset-zeta-primitive/results
```

The clique obstruction applies only to coordinate-subset geodesic
side transport and full-width closed center release. General
noncommuting zeta frames, different side chronology, dynamic releases,
or a native supplier using another mechanism remain open. A positive
Z architecture must lift at least one of those restrictions, supply
its complete dirty word, and pay its own routing, scalar coefficients,
prefix guards and recursive stock before the transfer can claim an
exponent.
