# Common outside diagonal gauges do not repair the fixed response family

Status: **ALL-SIZE SCOPED ALGEBRAIC OBSTRUCTION WITH EXACT FINITE CONTROLS**.
For f>=5, Boolean subset-zeta cannot be a common invertible left/right
diagonal gauge of an arbitrary sum of the previously tested two-scan
responses. This closes a particular amplitude escape from the four-entry
separator. It excludes neither different address orders nor separately
gauged response terms, non-diagonal boundary words or longer scan paths.
There is no native cost or multiplier-exponent claim.

Let N=2^f and P(x)=x XOR [(x AND 1)(N-2)]. Allowed scans S,T are natural
or P-ordered inclusive prefix/difference. Middle coefficients are
completely arbitrary, including zero. The candidate is

    Z = D_left [sum_j S_j diag(w_j) T_j] D_right,

where the two outside diagonals are shared across the entire sum and
have nonzero entries. The claim holds over every field, and in particular
over the complex numbers, without positivity or cancellation restrictions.
The fixed boundary address labels are essential.

## A rank-three target and rank-two responses

Take rows R=(9,11,13) and columns C=(0,2,4). For each allowed S, every
difference between a row in R and row 9 is supported within

    A = {8,9,10,11,12,13,N-10,N-12,N-14}.

For each allowed T, every difference between a column in C and column 0
is supported within

    B = {0,1,2,3,4,5,N-1,N-3,N-5}.

These sets are disjoint for N>=32. In the natural prefix, a row difference
occupies the short interval between its two thresholds. In the P-prefix,
odd row r has threshold N-r, so inverse P maps that short interval into
odd low addresses and even high addresses. Difference rows contain only
the row and its predecessor in the selected order. This gives A. For
columns, the thresholds 0,2,4 are even and fixed by P; prefix differences
occupy natural initial addresses or their P-images. Difference columns
contain the column and its successor, giving B. The displayed whole sets
therefore cover every allowed scan, not merely a sampled coefficient.

For H=S diag(w) T and rows r,9 and columns c,0, the mixed difference is

    H[r,c]-H[r,0]-H[9,c]+H[9,0]
      = sum_k (S[r,k]-S[9,k]) w[k] (T[k,c]-T[k,0]) = 0.

This survives arbitrary sums of response terms. The restriction to R,C
thus has entries a_i+b_j, a sum of two rank-one matrices, so its rank is
at most two. The subset-zeta restriction is exactly

    [[1,0,0], [1,1,0], [1,0,1]],

with determinant one. Left and right nonzero diagonals rescale rows and
columns and preserve that minor's rank. Consequently the proposed common
outside gauge cannot turn the response restriction into the target.

## Evidence and reproduction

The standalone standard-library source is
[the exact rank control](../../code/synthesis/two_response_outer_gauge_rank.py),
SHA256 727d5cbe05bbd05547f6ca71ba26553d1634606ad5d018acbc1680465a847040.
Its complete integer generator checks cover every middle index for every
one of the sixteen S,T choices and all four mixed differences. The first
four-worker run, actual start 2026-10-09T11:27:46.572659+00:00, passed
79,872 equations at f=5,6,7,10. The bounded reproduction, actual start
2026-10-09T11:36:15.364464+00:00, passed 6,144 equations at f=5,6.
No wall-clock performance metric was collected.

Both attempts retain the common nonzero diagonal rank control, the zero
outside-gauge scope negative and an explicit failed extension at f=4.
The run certificates are complete compact copies of the original results;
original logs and results are unchanged under ignored work/synthesis.
The publication inventory records their hashes and complete archive needs.
The bounded output path must be a new file.

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/two_response_outer_gauge_rank.py --workers 4 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/two_response_outer_gauge_rank.py --workers 4
```

The written all-size argument is an ordinary mathematical proof with exact
finite controls, not a formal proof-assistant artifact. It was developed
with AI assistance. A useful next mechanism must alter an assumption of
the displayed response family rather than add a common diagonal amplitude.
