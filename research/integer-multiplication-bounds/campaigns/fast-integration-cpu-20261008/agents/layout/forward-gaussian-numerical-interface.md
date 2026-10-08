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
