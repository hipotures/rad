# Three selected ordered scans and an exact dyadic lift

## Question and model

Can a constant number of contiguous prefix/difference primitives implement
the Boolean subset-zeta map, while admitting a genuinely different native
supplier? This report first tests an exact, one-bank algebraic model. It does
not assume a native scan endpoint, paid address ordering, recursive child,
or multiplication exponent.

Let `N=2^f` and `Z_f[x,y]=1[y is a subset of x]`, with the original Boolean
address labels fixed. For an address permutation `pi`, `L_pi` is inclusive
prefix summation in that order and `D_pi=L_pi^-1` is adjacent difference.
The target family is

```
Z_f = diag(a) S_pi diag(b) T_sigma diag(c) U_rho diag(d),
```

where every diagonal entry is nonzero, and each scan is `L` or `D`.
The selected orders are natural order and reversal of the `f` address bits.
Independent input/output permutations, arbitrary other orders, extra dirty
banks, projections, and non-diagonal amplitude wrappers are outside this
family. All scales in a retained literal word remain paid operations.

The reason to test scans is their dense support with streaming scalar cost.
Neither dense support nor a formal `O(N)` addition count supplies a fast
fixed-tape selected-orbit primitive. Actual record geometry, buffers,
guards, address metadata, whole intermediate coefficients, and precision
must still be supplied.

## Exact finite reduction and preserved failed lift

The original discriminator exhausts nonzero middle diagonals over `F_3`,
normalizing the first entry of each to one. A global scalar is absorbed by
the outside diagonals, so this loses no finite-field solution. For each
left diagonal, exact homogeneous elimination describes the right
diagonal's zero constraints; every nonzero normalized right candidate is
then checked against the entire target, including the required nonzero
entries and both outer diagonal gauges.

Every real dyadic unit `+/-2^k` reduces to a nonzero element of `F_3`.
Therefore an exhaustive finite negative excludes those real units for
the chosen orders. It alone excludes neither Gaussian phases nor other
orders or scalar domains.

Four workers checked 136 cases in the original attempt:

| Width | Cases | Exhaustive `F_3` exclusions | Finite positives |
| --- | ---: | ---: | ---: |
| `f=1` | 8 | 0 | 8 |
| `f=2` | 64 | 48 | 16 |
| `f=3` | 64 | 64 | 0 |

The run exhausted 8,666 normalized left-diagonal assignments in total.
Every simple `+/-1` characteristic-zero lift of the `f=2` finite
positives failed. That failed lift is retained in the unchanged original
certificate; it is a failure of that lift, not a proof that three scans
are impossible at `f=2`.

Original evidence:
[real-dyadic run](../../runs/20261009T095321Z-synthesis-three-scan-real-dyadic/report.md).
Source:
[three_scan_real_dyadic_probe.py](../../code/synthesis/three_scan_real_dyadic_probe.py).

## Exact three-prefix dyadic word at two bits

A later, separate exact lift succeeds:

```
Z_2 = diag(1,1,-1,-1) L_4 diag(1,-1,-1,1)
      L_4 diag(1,-1,2,-2) L_4 diag(1,1,1/2,1/2).
```

The literal chronology contains three complete prefixes, nine unit
additions, and nine explicit scales. Four scales have magnitude `2` or
`1/2`; five are signs. Complete replay checks all four forward columns,
all four inverse columns, and 48 complete Gaussian fields on grids with
0, 1, 4, and 9 fractional bits. Omitting the final output signs and
substituting the failed finite-field sign lift both reject.

The maximum complete prefix row `L1` norm is 6 forward and 4 inverse,
and both words need one additional fractional grid bit. Arithmetic
temporaries and a native record-buffer layout are separately unpaid.
Both completed endpoints are integral. Together with the previously
retained [two-scan exclusion](two-ordered-scan-products.md), this attains
the local minimum of three scans at `f=2` in the fixed-label model with
nonzero diagonal gauges. It uses more elementary additions than the
ordinary four-addition zeta word and is not a gate-count improvement.

Evidence:
[dyadic-lift run](../../runs/20261009T101213Z-synthesis-three-scan-dyadic-lift/report.md).
Source:
[three_scan_dyadic_lift.py](../../code/synthesis/three_scan_dyadic_lift.py).

## All-size exclusion for natural/bit-reversal orders

The following is an analytical characteristic-zero result for arbitrary
nonzero complex diagonal entries. Gaussian units and nonunit Gaussian
coefficients are covered. Finite integer checks bind the displayed block
identities, but do not constitute formal verification of the all-size
proof.

**Result.** For every `f>=3`, no product of three natural/bit-reversal
prefix or difference scans with nonzero address-diagonal gauges equals
the fixed-labeled `Z_f`.

Write `m=2^(f-1)` and split rows and columns by the most significant bit.
Every natural scan has blocks

```
N = [[A,0],[K,A]],
```

where `A` is the corresponding smaller natural scan. For a prefix,
`K=J_m`; for a difference, `K=-e_0 e_(m-1)^T`. In either case
`K[0,m-1]` is nonzero. Let `R` be the smaller bit-reversal prefix,
`D=R^-1`, and `H=D-I`. The full bit-reversal scans are exactly

```
B_L = [[R,R-I],[R,R]],     B_D = [[I,H],[-I,I]].
```

Classify the three factors by the number of bit-reversal scans.

**Zero or three.** In their common order, each scan has cross-midpoint
rank one. A nonzero diagonal has cross rank zero. The product has cross
rank at most three. The corresponding zeta cross block is a complete
smaller zeta map of rank `m>=4`. Bit reversal is an axis permutation and
preserves the Boolean zeta target. Thus both cases fail.

**One.** Both natural factors are block lower triangular and invertible.
The unique bit-reversal upper-right block has rank `m-1`, which is
preserved by the invertible block-diagonal factors on either side.
The target upper-right block is zero. Thus this case fails regardless
of where the unique bit-reversal scan occurs.

**Two consecutive.** Put `Q=B_left diag(B0,B1) B_right`, with `B0,B1`
invertible diagonal matrices. The remaining natural factor cannot
annihilate a nonzero `Q01`, so `Q01=0` is necessary. It implies
`B0 H + H B1=0` for two scans of the same kind, and
`B0 H - H B1=0` for mixed kinds. Direct block algebra then gives:

| Consecutive kinds | Forced diagonal block identities |
| --- | --- |
| prefix/prefix | `Q00=R B0`, `Q11=B1 R` |
| difference/difference | `Q00=B0 D`, `Q11=D B1` |
| prefix/difference | `Q11=B1` |
| difference/prefix | `Q00=B0` |

At least one required target diagonal block is therefore a product of
at most two smaller ordered scans with nonzero diagonal gauges. The
retained two-scan result excludes it for `f-1>=2`. A single scan also
cannot have the zeta support: for `k>=2`, prefix support has
`2^k(2^k+1)/2 > 3^k` entries, while difference support has
`2^(k+1)-1 < 3^k`. Diagonal gauges preserve these support counts.

**Two separated.** The middle gauged natural factor is
`M=[[U,0],[W,V]]`, with `U,V` lower triangular and
`W=B1 K C0`. For the upper-right block of `B_left M B_right`,
multiply on the left by `D` when the left scan is a prefix, and on the
right by `D` when the right scan is a prefix. These invertible operations
preserve whether the block is zero. The four expressions become:

```
prefix/prefix:       -U H - H V + H W H
prefix/difference:   U H - H V - H W H
difference/prefix:  -U H + H V - H W H
difference/difference: U H + H V + H W H.
```

Choose `r=m/2` and `c=m/2-1`. In the smaller bit-reversal chain,
`r` is the first successor of zero and `c` is the last predecessor of
`m-1`. Hence

```
(UH)[r,c] = -U[r,m-1] = 0,
(HV)[r,c] = -V[0,c]   = 0,
(HWH)[r,c] = W[0,m-1] != 0.
```

Here `m>=4`, and the zero equalities follow from natural lower
triangularity. The final nonzero value is the product of two nonzero
diagonal entries and `K[0,m-1]`. It cannot cancel, so the upper-right
block cannot be zero. This exhausts the selected family.

Four workers bound these identities at `f=3,4,5,6`: 208 complete exact
integer block cases, a missing-middle-bridge corruption control, and
the inherited 2,304 complete two-scan cases.
Evidence:
[block-control run](../../runs/20261009T103619Z-synthesis-three-lex-block-obstruction/report.md).
Source:
[three_lex_order_block_obstruction.py](../../code/synthesis/three_lex_order_block_obstruction.py).

## Reproduction and interpretation

From the research worktree, use fresh output paths:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/three_scan_real_dyadic_probe.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/FRESH-real/results
python3 -B research/integer-mult-breakthrough/code/synthesis/three_scan_dyadic_lift.py --output research/integer-mult-breakthrough/work/synthesis/FRESH-lift/certificate.json
python3 -B research/integer-mult-breakthrough/code/synthesis/three_lex_order_block_obstruction.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/FRESH-block/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_three_scan_components.py --component selected
```

The bounded standard-library wrapper reruns the finite reduction,
normalization/corruption controls, 52 `f=3` block bindings, the complete
two-scan lower-dimensional controls, and the literal dyadic lift with its
full prefix/grid bill. Its optional `--output` must name a fresh file.
All effective local imports are recorded in the receipt and publication
inventory. Original completed attempts remain unchanged.

These exclusions redirect the supplier search toward genuinely nonlex
orders or borrowed-bank/interference architectures. The separate
[high-flux report](nonlex-scan-flux-and-native-boundaries.md) exhibits an
order escaping the lexicographic cut-rank budget. Neither package
provides a native transform or asserts a larger kappa.
