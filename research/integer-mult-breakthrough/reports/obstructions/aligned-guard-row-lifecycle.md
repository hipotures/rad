# Aligned old-row splits retain complete native guard cubes

Status: **EXACT FINITE ALLOCATION AND CONDITIONAL NATIVE REHYDRATION**.
A complete canonical scalar network, its paid moment and its growing-depth
precision contract remain required. No multiplication exponent is claimed.

## Corrected split

The [initial pool](retired-guard-row-lifecycle.md) retired t>=2h complete
K-bit guard chunks into an existing row index. Its combined-index split
does not preserve an independent fresh guard cube per role. The correction
uses G=2^(tK), pads the OLD row count R to R_pad=W ceil(R/W), and assigns
role w by old_row mod W. The new role row count is

```text
R_role = ceil(R/W) G,
child volume / old parent volume = ceil(R/W)/R,
padding fraction < W/R.
```

Every role has the exact Cartesian factors
(old_row quotient, fresh_guard_cube, complete_active_suffix, spectators).
The role is independent of every bit in the fresh cube. At the first
invocation R can be one: padding to W rows is a fixed, explicitly paid
volume expansion. It is done once, and added root rows finish zero.
After any split R_role>=G>=2^(2hK). Thus every nonroot padding fraction
is bounded by epsilon_K=W*2^(-2hK). The root's fixed factor affects only
the time constant. The conditional strict-moment proof applies thereafter
with inflated nonroot weights (1+epsilon_K)n_r/W.

Each complete invocation restores its own row representation before
returning. A descendant may partition older guard coordinates as part of
its old rows; it uses its own fresh cube for its local wrappers. The
ancestor's complete guard shape returns at the child endpoint. Temporary
loss of the old cube inside a descendant does not authorize borrowing it
as a complete native slot before that restoration.

## Whole-chunk rehydration with changed active order

Set aside the u remainder guards, which remain complete spectators.
The main region contains 2hg active K-bit chunks and 2h fresh terminal
guard chunks. In the intended native layout, guard j belongs at chunk
position (j+1)(g+1)-1. Track the location of every guard label and swap
it into its target. At most 2h whole-K exchanges suffice. Previously
placed guards cannot be disturbed because all labels and targets are
distinct. Every remaining position contains an active chunk, in a
possibly different order.

Let P be this exact complete-address permutation. It moves all K bits
of every exchanged chunk and all payload fields. If A_old and A_new are
the old and new active coordinate sets, the complete tensor identity is

```text
P^-1 (C_(A_new) tensor I_(new guards)) P
    = C_(A_old) tensor I_(old guards).
```

The same chosen rho bit in each K chunk remains selected. All K-1
unselected bits move with the chunk and return under P^-1. This identity
uses a full tensor of identical C kernels; it is not valid for an arbitrary
partial-output interface. A scalar network must be generated consistently
in the NEW slot grouping, including every source, sink, child frame,
quadratic phase and dirty role. Reusing unchanged old port descriptors
would invalidate the binding.

Under the pinned original complete equal-width address-chunk exchange
contract, a fixed number of these exchanges has the required conditional
O_h(V((eK)^tau+1)) bill, including its actual metadata and exceptional
repair terms. The complete fresh cube and suffix supply the stated shape.
This applies an inherited routing contract; Python reindexing does not
independently establish that native algorithm.

## Remaining integration and precision

The conditional moment theorem requires an actual arbitrary-dirty network
whose every physical role finishes as C on its active tensor. This makes
the retired guard preprocessing commute at the complete endpoint and
makes zero padding recoverable. A partial-output promise, a source-only
identity or a scalar matrix with freely cleared helpers is insufficient.
Guard-dependent completed routes require a different proof.

Metadata must be bounded locally by each retained complete long record.
The unweighted number of nodes can grow exponentially; no polynomial
node bound is inherited. The strict paid moment bounds the total weighted
volume bill. A nonstrict full-rank recurrence can instead take a linear
number of large local steps and lose the desired power.

Worst branch depth can be Theta(d). The actual scalar prefix norms,
denominator grids, endpoint regridding, numerical errors and temporary
coefficient widths must therefore be reviewed again. The old O(log d)
depth argument cannot certify this reserve. The allocation proof neither
increases coefficient magnitudes by reindexing nor supplies that missing
Gaussian precision analysis.

## Finite controls and reproduction

The [aligned four-worker run](../../runs/20261009T053816Z-aligned-guard-row-pool/)
uses complete K=1 cubes at e8/e9/e10/e12 with W3/W5 and one, two or three
original rows. All 33,792 record fields agree with the full C reference,
the true chronological inverse restores the exact Gaussian inputs, and
every deleted padded row is zero. Each role retains the complete fresh
guard cube. These are four Gaussian fields, not omitted coefficient samples.

The rehydration controls cover h2/g1, h2/g2 and h3/g1. They enumerate all
256,4096,4096 respective physical addresses and four Gaussian fields,
retaining every whole-chunk exchange and its inverse. The conjugated
tensor agrees exactly despite the changed active order. The all-K argument
above is mathematical; the complete physical operator enumerations use K1.
The native guard assumptions are not asserted for this small K1 toy.

The aligned producer imports only the original frozen row producer's
integer Gaussian kernel and bit-projection helpers. Both source hashes
are captured before and after the run. Original naive evidence is preserved
with its geometry qualification and is not relabeled as the repaired result.

From the worktree root, standard-library Python only:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/aligned_guard_row_pool.py \
  --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/aligned-guards
```

Use `--workers 1 --bounded` for the smaller independent cases. Choose a
new output directory for each attempt. Indexing and child C transforms
in this verifier are explicit reference oracles, rather than native tape
time measurements. Internal analytical review is distinct from formal
verification or an independently proved full multiplication exponent.
