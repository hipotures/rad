# Scan order cut ranks and a necessary flux budget

Status: **ANALYTICAL RESULT WITH EXACT FINITE CONTROLS**, 2026-10-09.
This is an exclusion for a specified one-bank scan model, not a lower bound
for arbitrary reversible circuits or a new integer-multiplication exponent.

## Question and model

Can a fixed number of whole ordered inclusive-prefix or adjacent-difference
scans implement growing Boolean subset zeta? Allow arbitrary nonzero diagonal
gauges, mixed scan types and cancellation. Each scan acts on the same complete
set of N = 2^f Boolean addresses. The input and output retain their fixed
Boolean labels; additional banks, projections and arbitrary free endpoint
permutations are outside this model.

For an address order o_0, ..., o_(N-1), let L_o have entry 1 exactly when its
column precedes or equals its row. Let D_o be its true inverse: identity minus
the immediately preceding address shift. For coordinate b, write A_10 for the
submatrix with row bit b = 1 and column bit b = 0.

## Exact rank of either scan cut

Let r_b(o) count consecutive **0-to-1** changes of bit b along the address
order. Then over every field,

    rank((L_o)_10) = rank((D_o)_10) = r_b(o).

To prove the prefix statement, divide the order into runs of the coordinate
bit. An initial 1-run has no preceding 0-addresses and gives zero cut rows.
A final 0-run has no following 1-addresses and gives zero cut columns.
Every remaining 1-run corresponds to one positive transition. Each row in
that run selects its transition index; each column in a 0-run selects the
first following positive transition. The complete cut therefore factors as
E L_r F, where E and F are rectangular zero/one selectors and L_r is the
r-dimensional inclusive-prefix matrix. This proves rank at most r.

For transition indices j_1 < ... < j_r, choose rows o_(j_a) and columns
o_(j_c-1). Their prefix minor is L_r, with determinant 1. The corresponding
difference minor is -I_r. Every nonzero difference cut entry is precisely one
of these disjoint transition edges. Both ranks are thus exactly r, including
characteristic two. No positivity or characteristic-zero argument is used.

Nonzero diagonal gauges on either side of a scan preserve its cut rank. The
unit minors and integral factorization also identify good-reduction controls;
they are not an unrestricted finite-ring radical theorem.

## All-size word budget

For any two square matrices on these fixed labels,

    (AB)_10 = A_10 B_00 + A_11 B_10,
    rank((AB)_10) <= rank(A_10) + rank(B_10).

The Boolean-zeta matrix Z_f has entry 1 when the column is a subset of the
row. Its b-cut is Z_(f-1), hence has rank N/2: in natural remaining-address
order it is unit lower triangular. Repeated cut subadditivity shows that a
word of s scans, in orders o^(1), ..., o^(s), with arbitrary invertible
diagonal factors, necessarily satisfies for **every coordinate b**,

    sum_i r_b(o^(i)) >= N/2.

Consequently its total positive transition flux must satisfy

    sum_i sum_b r_b(o^(i)) >= f N/2.

This necessary condition is not sufficient. It applies to mixed scans and
cancellation and does not count scalar additions as native time. Extra
non-diagonal boundary operators would contribute their own cut ranks to the
same inequality; treating arbitrary boundary permutations as free would
change the model.

## Lexicographic and local-jump consequences

In an axis-permutation lexicographic order, if b has position t counted from
the most significant selected bit, r_b = 2^(t-1). Thus each scan contributes
exactly N-1 total positive transitions, regardless of its axis order. Any
such mixed scan word implementing Z_f obeys

    s >= ceil(f N / (2(N-1))) = floor(f/2) + 1, for f >= 1.

A fixed number of these scans cannot supply growing zeta. The earlier
all-prefix inverse-support argument is stronger for its narrower family:
it requires s >= f. The present argument handles arbitrary mixtures of
prefix and difference scans and arbitrary axis permutations.

For a completely general order, let d(o) be its consecutive Hamming path
length and let delta(o) be endpoint Hamming-weight change. Counting positive
and negative bit transitions gives the exact identity

    2 sum_b r_b(o) = d(o) + delta(o).

Therefore an s-scan word needs

    sum_i d(o^(i)) >= f(N-s).

With jumps bounded by a fixed h, a necessary bound is
s >= f N / (h(N-1)+f). A fixed-count escape must have mean Hamming jump
of order f. This is an algebraic discriminator, not a physical head-motion
or routing lower bound.

## A concrete escape from the lexicographic obstruction

The involutive binary shear

    P(j) = j XOR ((j AND 1) * (N-2))

orders addresses as even values ascending, interleaved with odd values
descending. Its total positive flux is N(f-1)/2 + 1. Its Hamming path length
is N(f-1)+1 and endpoint weight change is 1. It can pass the aggregate
necessary budget with a constant number of scans, so extending the
lexicographic exclusion to all address orders is false.

This does not construct zeta. A separate synthesis-agent reduction tests
selected natural/shear three-factor words. Native conditional routing,
selected-orbit synchronization, complete records, scan magnitude growth,
fixed coefficient grids and dirty restoration still require their actual
cost contracts. A cheap scalar prefix implementation cannot make those
obligations disappear.

## Independent finite evidence and reproduction

Source: [scan_order_cut_rank.py](../../code/obstructions/scan_order_cut_rank.py),
SHA256 `ddec3f540c5fbfe0f398f666674bcd81634febb6f2a59f6154666f317e563132`.
Full run: `20261009T103847Z-scan-order-cut-rank`, four worker processes,
0.467 seconds on this host. Standard-library Python; no producer imports.

The run checks all axis-permutation lexicographic orders through f = 6,
plus Gray, complement-shear and seeded arbitrary orders at each size:
891 orders and 10,204 complete coordinate/scan-type certificates. Every
complete cut entry matches its integral rank factorization or transition
support, and every lower-rank witness is an exact unit minor. Independent
elimination over F2, F3 and F5 checks the small cases and nonzero gauges.
There are 120 further product cut-subadditivity controls. Zero gauges and
the unjustified extension of the lexicographic budget to the shear order
are rejected as adverse controls.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/scan_order_cut_rank.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/scan_order_cut_rank.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/scan-order-cut-rank
```

Choose a fresh output directory. The complete 1,053,367-byte certificate
is retained whole in gzip evidence; readable compact results omit individual
address-order rows and name that omission. The all-size proof above, rather
than testing through six coordinates, establishes the stated infinite
family result. No proof-assistant formalization is claimed.

## Next discriminator

Preserve this barrier while seeking high-flux scan orders whose complete
conditional layout and normalization can actually be paid. The selected
natural-fiber accumulator proposal is a separate native-layout hypothesis.
Its amortized record movement, counter movement and f extra magnitude bits
must be established before it can be used in a coupled recurrence. A
positive complete scan factorization would then need every diagonal and
input/output permutation, not only an optimistic transition count.
