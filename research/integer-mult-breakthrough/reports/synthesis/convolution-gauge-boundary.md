# Same-coordinate convolution boundary and padded escapes

## Result and scope

Let `D=2^N`, `W[x,y]=(-1)^(x dot y)`, and `C_N=C^{tensor N}` for
`C=[[alpha,beta],[beta,alpha]]`, `alpha=(1+i)/2`, `beta=(1-i)/2`.
For `N>=3`, independent permutations and arbitrary nonzero complex row and
column gauges cannot turn `W` or `C_N` into a `D`-by-`D` Toeplitz operator.
The claim includes circulant and negacyclic operators on the same coordinate
set. It concerns one operator of that form, not sums, larger Kronecker
embeddings, or arbitrary sparse input/output slots in a larger convolution.

This is an elementary mathematical obstruction accompanied by exact finite
checks. It is not a lower bound on integer multiplication. No novelty claim
is made. The Gaussian tensor identity

`C_N = alpha^N diag((-i)^popcount(x)) W diag((-i)^popcount(y))`

reduces its gauge-equivalence question to the Walsh matrix.

## Proof for arbitrary nonzero gauges

Suppose `T[i,j]=t[i-j]=r[i] W[p(i),q(j)] c[j]` with all gauges nonzero and
`p,q` permutations. Adjacent gauge-free minors give

`t[s]^2/(t[s-1]t[s+1]) = (-1)^(delta p(i) dot delta q(j))`, `s=i-j`.

Consequently these ratios are signs depending only on `s`. Choose signs
`sigma[0]=sigma[1]=1` and extend in both directions by
`sigma[s+1]=sigma[s-1] rho[s]`. The sign Toeplitz matrix
`H[i,j]=sigma[i-j]` has the same adjacent cross ratios as the permuted Walsh
matrix. Their entrywise quotient has every adjacent cross ratio equal to one,
so it is a product of a row gauge and a column gauge. Since both matrices
have sign entries, these gauges can be chosen as signs. Thus `H` is Hadamard:
`H H^T = D I`.

The inner product of successive rows `i,i+1` is zero. Subtracting this
identity for adjacent values of `i` gives

`sigma[t]sigma[t+1] = sigma[t-D]sigma[t-D+1]`, `1<=t<=D-2`.

Hence all ratios `sigma[t]/sigma[t-D]`, `1<=t<=D-1`, are the same
`epsilon in {+1,-1}`. This is exactly a circulant or negacyclic wrap. Its
one-coordinate shift supplies a monomial automorphism whose row permutation
and column permutation are full `D`-cycles. Conjugating the gauges and address
permutations gives such an automorphism of `W`.

Every monomial automorphism of `W` has binary affine address permutations.
Indeed, if `W[p(x),q(y)]=u[x]v[y]W[x,y]`, taking the cross ratio with row and
column zero eliminates the gauges and proves

`(p(x)+p(0)) dot (q(y)+q(0)) = x dot y` over `GF(2)`.

The two translated permutations fix zero and are bijections. Varying `y`
shows that the first is additive; varying `x` does the same for the second.
They therefore are `A x` and `A^{-T} y`. In particular `p` is affine.

An affine permutation on `GF(2)^N` cannot be a full `2^N`-cycle for `N>=3`.
Represent it by an invertible `(N+1)`-by-`(N+1)` homogeneous matrix `R`. A full
cycle would give `R` order `2^N`. In characteristic two, an element of power
of two order is unipotent: `(R-I)^{2^N}=0`. A nilpotent matrix of size `N+1`
has index at most `N+1`; hence `R` has order at most
`2^ceil(log2(N+1)) < 2^N`. This contradiction proves the claim.

The proof allows all nonzero complex gauges, including nonunitary
Gaussian-dyadic gauges. A general constant wrap unit in a twisted circulant
also supplies the forbidden full-cycle monomial automorphism directly.

## Exact finite evidence

The four-worker deterministic screen in
[the completed run](../../runs/20261008T232353Z-synthesis-convolution-gauges/report.md)
uses the adjacent-minor criterion above, modulo row/column translations and
simultaneous dual linear coordinate maps.

| Active bits | Representative permutation pairs | Toeplitz gauge hits |
| --- | ---: | ---: |
| 1 | 1 | 1 |
| 2 | 6 | 2 |
| 3 | 151,200 | 0 |

The positive small cases have exact reconstruction with 36 pairs of
Gaussian-dyadic unit seeds, including `alpha`, `beta`, `1+i` and `1-i`.
Their varying amplitudes and wrap units are retained. All 322,560 binary
affine maps on four bits were separately enumerated: none is a 16-cycle,
and the largest power of two order is eight.

## Padding is a distinct problem

For any `D`-by-`D` matrix `A`, place input `b` at position `D*b`, put
`A[a,b]` at kernel position `a+D*(D-1-b)`, and read output
`D*(D-1)+a`. One ordinary polynomial convolution then computes `A x`.
This uses `D^2` kernel coefficients and product extent `2D^2-D`. All 64
target entries were exactly replayed for `C_3`. It is a clean linear
embedding with quadratic space, not a dirty or native circuit.

A separate fourth-root phase SMT model synthesizes distinct positions
`A_x,B_y` in `[0,M-1]` and a kernel phase `K` modulo four satisfying

`K(A_x-B_y)-K(A_x)-K(-B_y) = 2*(x dot y) mod 4`.

Independent exact Gaussian ordinary-polynomial replay found `N=3,M=24`
with fixed `A_x=x`, 47 kernel coefficients and product extent 70. This
shows that some padded embeddings are smaller than the generic quadratic
construction at this size. It does not produce a uniform all-size family.
The `M=8,12,16` jobs timed out after 60 seconds and are **UNKNOWN**, not
exclusions. The same-size `M=8` model is excluded by the independent theorem
and exhaustive scan, not by the timeout. Bounded `N=1,M=2` and `N=2,M=4`
solver controls both returned SAT and were exactly replayed.

The completed
[main SMT run](../../runs/20261008T232752Z-synthesis-padded-convolution/report.md)
and [bounded solver controls](../../runs/20261008T232752Z-synthesis-padded-smoke/report.md)
retain seeds, pinned solver identity, statistics, all phase/position models,
timeouts and source hashes. Kernels, data movement, clean padding,
coefficient encoding and restoration remain uncharged.

## Reproduction

From the repository root, use fresh output directories:

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/convolution_gauge_screen.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-run>/results
python3 -m venv research/integer-mult-breakthrough/work/synthesis/<fresh-env>
research/integer-mult-breakthrough/work/synthesis/<fresh-env>/bin/python -m pip install -r research/integer-mult-breakthrough/configs/synthesis/solver-requirements.txt
research/integer-mult-breakthrough/work/synthesis/<fresh-env>/bin/python -B research/integer-mult-breakthrough/code/synthesis/padded_convolution_smt.py --workers 4 --timeout 60 --output research/integer-mult-breakthrough/work/synthesis/<fresh-smt>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_convolution_gauges.py --output research/integer-mult-breakthrough/work/synthesis/<fresh-check>/check.json
```

The solver-free bounded verifier reruns the complete three-bit sign-gauge
scan, the one/two-bit positive Gaussian gauge cases, affine cycles through
three bits, both padded polynomial controls and a corrupted kernel phase.
Its [completed receipt](../../runs/20261008T235643Z-synthesis-convolution-ci/results/check.json)
pins all four source files and the independently replayed small witness.

The finite-field construction in
[the separate report](finite-field-cyclic-core.md) uses a `D-1` nonzero
cyclic core with paid zero-border operations. It does not contradict the
same-`D` obstruction.
