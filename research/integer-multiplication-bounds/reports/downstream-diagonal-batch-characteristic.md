# Exact prospective characteristics for diagonal Bruhat batches

Two disjoint families of physical residuals give strict characteristic
improvements if the independently investigated diagonal-batching transfer
is used. The capped row supports

`a=1043048637144781/(2*10^23)`

for the independently accepted h51 R502265 finite network. This is greater
than 2^-28. It is a primitive characteristic screen, not a completed
multiplication theorem or an assembly promotion. The capped version is the
preferred transfer candidate because each child is at most 1/51 of its
parent.

## Disjoint families and rank conservation

Use the finite h51 counts and identity from the
[accepted-input composition report](downstream-odd51-semantic-bulk.md).
Let v=C(h,3), m=h³ and R=502265. Only the following families change:

1. The final middle auxiliary endpoints have residual
   I tensor I tensor (I-P_t). A triple with minimum a has C(h-a-1,2)
   occurrences. Each of its h² blocks has diagonal runs a and h-a-2 plus
   one offdiagonal pivot. The multiplicity factor is (R+h)v h². The exact
   positive batch histogram is preserved in the earlier
   [subset run](../runs/20261008T043058Z-downstream-diagonal-tail-subset/results/subset-certificate.json).
2. The joined first/third auxiliary endpoints have residual I-P with
   rank(P)=d=2h. There are (R+h)v² such endpoints. The proposed universal
   lower/lower rank-profile lemma gives at least m-2d diagonal pivots in
   at most 2d+1 runs.

The modified old rank totals are respectively
28,330,705,423,416,375,000 and 28,875,099,370,768,297,500. They are disjoint
and their sum is below s. Every other old pivot stays individual. The
whole rank sum remains s=60,190,685,022,033,566,875 and its deficit from Wm
remains D=2,263,379,181,875.

The universal profile argument concentrates the rank-d perturbation into
at most d rows by a lower row change used only for its proof. Under
top-down rightmost-pivot elimination, all other rows remain lower. Such a
row loses its diagonal only if an earlier exceptional row stole that
column. Thus at most d original exceptional rows and d stolen rows cover
all zero and offdiagonal rows: at least m-2d pivots stay diagonal, in at
most 2d+1 runs. The actual implementation still uses the original
canonical lower/lower factors and finite odd-prime table; this proof does
not supply new rational numerical factors to the complex computation.
The full profile and transfer require independent review.

## Uncapped and capped log sums

For diagonal runs of total length at least t in at most g pieces,
convexity gives sum(r log r)>=t log(t/g), provided t/g>1. Here t=m-4h.
The uncapped row uses g=4h+1 and the exact final-middle histogram. Its
strict characteristic saving is
`1058685652786963/(2*10^23)`.

For the preferred row, split each joined diagonal run into pieces of
length at most h². The total number of pieces is at most

`(4h+1)+(m-2h)/h² < 5h+1`.

Using the conservative integer upper bound g=5h+1 yields the capped
saving stated above. Middle runs already have length at most h-2 and
every unchanged pivot has length one, so the largest child rank is h².
Writing e=m b+t_tail gives r b<=floor(e/h) and r b<e. The exact tail
schedule is in the [stream report](downstream-arbitrary-width-tail-batching.md).
The depth is bounded by ceil(log_h e), which is at most
3 ceil(log_(h³) e). The capped source checks these implications at exact
power boundaries for h6,h8,h50,h51, including nondivisible widths.

The actual physical call histogram is not fabricated from Jensen's
bound: the joined contribution is explicitly a lower bound on its rank
log sum. Rank conservation and a loose whole-network remainder suffice
for the characteristic certificate. If J_lower is the lower bound on
sum(n_r r log r), the checked inequality is

`D - a*(W*m*log(m)_upper - J_lower)
   - (a*a/2)*s*(log(m)_upper)^2 > 0`.

Because every child rank is below m, the last term bounds the entire
quadratic exponential remainder. The strict inequality implies
W m^(1-a)>sum(n_r r^(1-a)). All comparisons use rational logarithm
enclosures and exact fractions; no floating-point threshold is used.

## Evidence, reproduction and remaining transfer

The uncapped [source](../code/downstream_diagonal_batch_join_bound.py)
has executed SHA256
`b0724b5e85992559050393c89a835daf31948a90fb99180f1a6afeb9ecb9543e`.
Its [run](../runs/20261008T043510Z-downstream-diagonal-join-bound/protocol.json)
preserves command/input/admission/log provenance; its
[certificate](../runs/20261008T043510Z-downstream-diagonal-join-bound/results/certificate.json)
has SHA256
`6dffd26119b35d828468f7f31b88687f12bd252e2e7cf1db0fa8ac24c644aa61`.

The capped [source](../code/downstream_diagonal_batch_capped_bound.py)
has executed SHA256
`770a6f3b761d614469e80a6d900fb6aff309033c683974d4281847e253c68af3`.
Its [run](../runs/20261008T043654Z-downstream-diagonal-capped-bound/protocol.json)
and [certificate](../runs/20261008T043654Z-downstream-diagonal-capped-bound/results/certificate.json)
(SHA256 `d3bd801fb1001d85bfdac22ce2bd9d8635fe960e9169404e91d517a4585f820f`)
are separate and leave the uncapped evidence unchanged. Both commands
consume the existing independent odd51 finite certificate; neither
replays a finite graph or builds a dense joined h51 matrix. Reproduce the
protocol commands with fresh output paths.

The remaining complete transfer obligations are physical endpoint
multiplicity and rank-profile review; grouped componentwise affine updates
with carry reset; preservation of the original rational factors and prime;
arbitrary-width tails on complete streams; the recursive cost induction;
row reservation, base cases and setup dominance; and fresh full assembly
arithmetic using the new primitive saving. The existing semantic/complex
numerical guard is unchanged by a proof-only rational row concentration.

The original campaign start/deadline and the user's authorized extension
are preserved in both protocols. Sources, compact results and completed
runs are stable for parent publication.
