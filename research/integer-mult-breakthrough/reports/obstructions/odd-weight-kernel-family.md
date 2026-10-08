# Odd-weight complex central kernels beyond triples

Status: EXACT FINITE ALGEBRAIC EVIDENCE and elementary analytical component
lemmas. This family changes the frozen triple representation. It does not
yet supply a side circuit, physical network, child distribution or exponent.

The prior [degree-two bit-motif screen](../../../integer-multiplication-bounds/reports/five-subset-motif-screen.md)
already used the k5 fitting polynomial and excluded its stated large rational
label architecture. This report treats Gaussian-dyadic scalar features with
binary address labels of dimension h and records that different scope.

## Polynomial family and Gaussian-dyadic arithmetic

Let `k=2r+1>=3`, and index source and target labels by k-subsets of `[h]`.
Their binary indicator vectors have norm one. Define

`f_k(t)=product_(j=0..r-1) (t-(2j+1))/(k-(2j+1))`

`        = binom((t-1)/2,r)`.

Then `f_k(k)=1`, and every possible odd off-diagonal intersection
`1,3,...,k-2` is a zero. Subtracting `f_k(t)` on distinct even-intersection
pairs gives the scalar identity map. Those side pairs are orthogonal in the
binary label field. The binary address-space dimension stays h; using a
higher-degree scalar fitting polynomial does not itself tensor that space.

For integer t, the binomial argument is integral or half-integral. Integral
binomial values are integers. For half-integral arguments, Vandermonde's
identity and

`binom(-1/2,s)=(-1)^s binom(2s,s)/4^s`

show that all values are dyadic rationals. Newton differences
`c_j=Delta^j f_k(0)` are therefore also dyadic, giving

`f_k(t)=sum_(j=0..r) c_j binom(t,j)`.

For each j-subset J, use the feature `sum_(X containing J) x_X`.
Summing features contained in a target reproduces `binom(t,j)`. Thus the
central factorization uses at most `sum_(j=0..r) binom(h,j)` features, all
with Gaussian-dyadic coefficients, while its binary labels remain in
`F2^h`. For k=5, the coefficients are `(3/8,-3/8,1/4)`; for k=7 they are
`(-5/16,5/16,-1/4,1/8)`. More features are a cost, not a free rank gain.

## Uniform feature-span lemma

Fix J of size j with `0<k-j<h-j`. Indicator vectors of k-subsets containing
J span the vectors whose coordinates inside J all equal p and whose outside
parity is `(k-j)p`. Differences of the outside `(k-j)`-subsets generate the
even-parity outside space; one odd-norm source adds the remaining dimension.
The span consequently has dimension `h-j`.

For even h and odd k, it is nondegenerate in the ordinary binary dot form.
A vector in its orthogonal complement has constant outside coordinate c
and inside-coordinate sum `(k-j)c`. If it also lies in the span, then

`j*c=(k-j)*p`, and `j*p=(k-j)*c`, over F2.

The parities of j and k-j are opposite. The two equations force p=c=0,
and the vector is zero. The j=0 feature is the full space. This all-h
argument was independently supplied by the complex agent after reviewing
the coordinator's finite implementation. It is not an inference from rank
agreement at selected examples or primes.

With every feature retained separately, the sum of feature-span dimensions
is `L0=sum_(j=0..r) binom(h,j)(h-j)`. Using that sum as a whole-network
decreasing-rank loss still requires the actual frame schedule; scatter,
copy and restoration must not be inferred from source spans alone.

## Five-subset refinement and independent scope checks

For k=5, point totals recover from pair totals by division by four.
Replacing two pair totals by their complements permits total recovery by
division by eight. The coordinator independently checked every source
basis column for h=10, both reconstruction identities, and full binary
support spans of the complementary pair gathers at tested h>=8.
The [complex track's report](../complex/five-subset-mixed-pair.md) gives the
paid copied-center interpretation and optimistic complete-moment envelope.

An initial concern that a pair center could not reach a target containing
only one endpoint was narrowed by independent transfer review: the pinned
copied-center schedule reads a paid full-stream copy in the common background,
not the small source-feature frame. This resolves that particular objection.
Complete source/copy/erase/restoration, phase and guard obligations remain.

The necessary optimistic side-role allowance is around 31--32 roles per
source at h=20--24. This is not sufficient: the optimistic ledger assigns
every unknown internal residual its most favorable width. The naive separate
E0/E2/E4 decomposition exceeds its allowance, so a genuinely shared side
representation or changed phase architecture is needed.

## Actual checks and continuation

The four-worker run in
`work/obstructions/20261008T2128Z-odd-weight-kernels/results.json` checked:

- Exact intersection values and Newton coefficients for k=3,5,7,9,11.
- Complete star bases and their Gram ranks for nine (h,k) pairs up to h=20.
- All ordered scalar source/target pairs for (8,3), (8,5), and (10,7).
- Five-subset total/point reconstruction, including a corrupt coefficient
  that leaves a nonzero forbidden odd-intersection residual.

Run `python3 -B research/integer-mult-breakthrough/code/obstructions/odd_weight_kernels.py --workers 4 --output /NEW/ignored/results.json`.
Use `--bounded --workers 1` for the registered finite CI replay. No dependencies
outside the Python standard library are required. Source hashes and actual
execution times are retained in run evidence; originals are unchanged.

The immediate continuation is efficient weighted intersection summation for
the k=5 side map, with literal common-frame/dirty programs and a complete
characteristic before any exponent claim. The k=7 family remains a supporting
alternative: extracting lower features from top triples introduces divisions
by five and fifteen, so the k=5 elimination cannot be copied without a new
dyadic construction.

## Provenance and limits

The original triple motif is read-only
`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`, section 3. It cites
Noga Alon's [The Shannon Capacity of a Union (1998)](https://www.tau.ac.il/~nogaa/PDFS/shann3.pdf),
whose polynomial representations provide the broader combinatorial context.
The half-binomial specialization, exact probes and all-h star proof were
developed by Codex agents; worldwide novelty and external review are unassessed.
No formal verification, efficient scalar side program or full multiplication
result is claimed.
