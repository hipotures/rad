# Independent numerical check of fractional packed forward Gaussian cells

Completed 2026-10-08 at approximately13:51:44 UTC. The actual launch was13:51:00;
the ignored output directory's `135331` label is an arbitrary run identifier,
not the launch timestamp. Four one-thread processes evaluated four distinct
changed interfaces in44.12 seconds. This is representative numerical evidence,
not an all-size proof or a replacement for CRT movement.

## Reference and producer

The reference evaluates the normalized periodic forward map

`S'_(k,j)=(2 alpha)^-1 sum_v exp[-pi (rho j-k+v t)^2/(rho^2 alpha^2)]`,

in each coordinate, with `rho=t/s`. It uses images v=-1,0,1, source sides
249,251,253, target side256, and independent signed inputs that are sums of
two separable tensors. Every input is bounded in magnitude by1/8. Remote
periodic images are much smaller than the128-bit target tolerance in these
specific cells. This contraction-normalized definition and the chirped
Toeplitz identity come from the pinned public Gaussian interface, as documented
in [the inverse agent's analytic report](../inverse/reports/packed-forward-precision.md).
The public source is CrocSwap PR38 science commit
`cc794077f6c103e24ec0939be765cd1521239aab`,
`notes/fast-gaussian-resampling.tex`.

The independent producer does all of the following:

1. Derives the true source core `[floor(s k0/t),floor(s(k0+L)/t))` for each
   actual target origin k0, including the half-cell-shifted grid.
2. Computes `j0=floor(s k0/t)` and `y=rho j0-k0` separately for every axis.
3. Forms the exact contracting input diagonal and Toeplitz kernel and rounds
   every tensor prefix product to the chosen dyadic work grid.
4. Appends zeros in unoccupied source-core slots and packs the source/kernel
   with mixed-radix base `B=L+2R`, using two actual nonnegative integer products
   for signed input. The polynomial kernel displacement is b-a, whereas the
   analytic Toeplitz argument is a-b; its orientation is explicit.
5. Extracts the packed coefficients, applies the full output diagonal and
   normalization, and compares with the separately evaluated global reference.
6. Evaluates exact global compression selectors `q_j=floor(tj/s+1/2)` and
   compares their selected packed outputs with the same reference.

The source imports neither an upstream producer/checker nor another campaign
agent's code. Decimal reference precision is160 decimal digits. Work precision
is chosen before any output comparisons:

`P=128+G+ceil(log2(L^D))+ceil(log2 D)+48`,

where G rounds up the FULL tensor chirp reserve. Actual P values268--294 bits
are larger than the128-bit output target because this finite near-one geometry
has G=83--104 bits. Treating128 bits as the setup precision would be unsupported.
Packed slot widths contain2P, the input-volume accumulation guard, and five
extra bits; no carry is allowed to spill between coefficient slots.

## Evidence

| Cell | Input records | Kernel records | Checked outputs | Selector samples | Largest absolute error |
|---|---:|---:|---:|---:|---:|
| 2D, L16, unshifted |256|225|4|2|1.507e-75|
| 2D, L32, half-shifted |961|625|4|4|2.299e-79|
| 3D, L16, unshifted |4096|3375|8|4|8.908e-82|
| 3D, L16, half-shifted |3600|3375|8|4|1.908e-81|

All24 outputs beat2^-128;14 are also selected through the exact global
compression map. Direct unwrapped Gaussian cell sums and exact chirped
factorizations agree to at most5.62e-160 absolute error. The finite padded
volumes900,3136,27000,27000 are recorded explicitly; these small examples do
not by themselves establish the campaign's growing-d halo-volume bound.

Retained negatives constrain easy mistakes:

- Replacing the true cell-dependent y with a constant zero produces errors
  between0.00121 and0.00769. Shifted-grid covariance cannot be assumed.
- For s13,t16,L2,k0=4,b=1, `floor(s(k0+b)/t)` is the first source index of the
  NEXT packet. The selector requires a face exclusion or repair.
- At a source-period cut, the unwrapped Gaussian loses a material wrapped
  contribution. Original-period strips must be excluded and repaired.

## Reproduction and scope

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout/code/check_forward_gaussian_fractional_cells.py \
 --workers 4 --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/layout/fresh-forward-numerical
```

Python3.14.4 standard library. Configurations, seeds, exact origins, y values,
guard widths, all outputs, source digest and per-case timings are retained in
[the compact certificate](results/forward-fractional-gaussian.json). Inputs are
deterministically regenerable. This checks true Gaussian factors, normalization,
fractional padding and selector alignment. It grants neither an all-size error
bound nor a fast modular CRT router. The latter remains a distinct full-algorithm
obligation after these local interfaces pass.

## Changed larger families and setup-precision correction

Two additional parameter families passed with the same independent operator
comparison. Six cases vary L32/64/128, source sides509/503/499, alpha and radius;
they check32 outputs and14 exact selectors. Two new 3D L32 cases use source
periods1009/1013/1019 and target1024, checking16 outputs and8 exact selectors.
They contain31,744/30,752 occupied source records,9,261 kernel records each,
and140,608 actual padded slots each. Their largest absolute error is9.41e-95;
both use324-bit work grids with a131-bit full-tensor reserve. This second pair
took358.27 seconds with two one-thread workers.

The larger-family review found a meaningful bounded-check issue: its two L128
cases choose P614 but initially used160 Decimal digits, only about531 bits.
Their sampled interior outputs pass128-bit tolerance, but this cannot validate
614-bit setup factors. The original receipts are preserved unchanged and this
precision limitation is explicit. The producer now chooses

`Decimal digits=max(160,ceil((P+64)/log2(10)))`

and evaluates pi by Machin's formula with a matching convergent-tail cutoff.
It rebuilds rational geometry after increasing precision. A changed rerun of
ONLY those two affected cases uses205 decimal digits and the same predefined
614-bit grid; the corrected receipt is added when complete. The other finite
cases need no unchanged rerun because P<=374 fits their original160 digits.

Reproduce the changed families by adding `--config` with respectively
`configs/forward-large-family.json`, `configs/forward-three-dimensional-L32.json`,
or `configs/forward-L128-precision-repair.json` to the command above. Use at most
the currently allocated workers. Configurations include all seeds and shapes.
Original source versions are reconstructible from the final published producer
using the small reverse patches in `fixtures/`; their digests match the receipts.
The CLI extension and subsequent precision correction are separate retained
source histories, not silently replaced successful attempts.
