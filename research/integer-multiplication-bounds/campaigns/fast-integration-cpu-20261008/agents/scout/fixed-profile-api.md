# Fixed I+J profile and complete controller API

## Eligible source and bounded preparation

All public algorithm inputs below are pinned to [eligible PR40 science commit](https://github.com/rohanarun/integer-mult-bounds/tree/43f59ff533598762cbc43a5e14af2bbbc76fabbd), `43f59ff533598762cbc43a5e14af2bbbc76fabbd`. The source profiler is `research/copied-both-reversed/full_profiles23.cpp`, copyright icekylinx, Apache-2.0. Its retained source notices also credit the archived partial-swap and PR7 producers. No new aggregate-main or quarantined campaign result is a scientific input.

[fixed_profiler_prepare.py](code/fixed_profiler_prepare.py) deterministically adapts this source to dimensions 6 through 28, excluding the degenerate `h=9`. It replaces only two dimension guards, the output suffix and descriptive h23 comments. It does not change matching, rational Gram formulas, modular elimination or block reconstruction. Generated third-party source and binaries remain in ignored work; [fixed-profiler-receipt.json](fixed-profiler-receipt.json) records input/generated/binary hashes, the compiler command and the exact enclosure for every supported dimension.

From the campaign directory, prepare and run:

```bash
python3 -B agents/scout/code/fixed_profiler_prepare.py \
  --source-root work/scout/snapshots/pr40-43f59ff53359 \
  --output work/scout/<fresh-build> --max-dimension 28
work/scout/<fresh-build>/fixed_ij_profiles \
  work/<changed-dag>.bin work/<changed-dag>.bin.fixed.links
```

Compilation requires C++17 and `unsigned __int128`. Run one profiler per assigned CPU slot. The output is exactly `<input.bin>.fixed_ij_profiles.json`, with `h`, `v`, `R`, `loss`, `rank_sum`, `field_prime`, `frames`, `distinct_matrices`, `crt_matrices`, `crt_disagreements`, and the length-`h+1` nonnegative integer array `blocks`. The binary link stream is auxiliary execution evidence; the source DAG, configuration and generator must be retained for recovery.

The profiler recomputes the **original-envelope matching** before collecting the actual `I+J` transitions. Never pair its blocks with an enlarged-positive histogram or a different matching's `R`. A scalar-role count or generic rank histogram is not a full fixed-basis moment.

## Exact rational corner enclosure

Each nontrivial frame matrix is a diagonal 0/1 mask plus a correction of rank at most two. Conservative frame denominator/numerator bounds are

| Frame | denominator upper bound | numerator upper bound |
| --- | --- | --- |
| core size 1 | `12(h+1)` | `12h²-10h+38` |
| core size 2 | `3(h²-1)` | `12h²-34h+64` |
| source triple line | `6(h+1)` | `12h-28` |

Let `D0` and `B0` be the column maxima. For a nested difference, the diagonal masks subtract to a 0/1 mask and the correction rank is at most four. Its **actual** clearing denominator is the product of the two actual frame denominators, at most `D=D0²`; its integer correction entries have magnitude at most `B=2D0B0`.

Expanding any selected square minor along the diagonal mask leaves at most `binom(h,j)` correction determinants of size `j`, each bounded by `j! B^j`, and all terms with `j>4` vanish. Multiplying by the actual clearing denominator to the fourth power gives an integer numerator with absolute value at most

`sum(j=0..4) binom(h,j) j! B^j D^(4-j)`.

`D` is a magnitude bound, not a universal clearing denominator. The proof does not multiply by `D^4` as if it cleared every rational coefficient.

The primes are `2^61-1`, `2^31-1`, `2^19-1`, `2^17-1`, `2^13-1`. Lucas–Lehmer checks establish their primality; each exceeds `D0`, hence every actual frame denominator is invertible. Their product strictly exceeds the all-minor bound for every supported dimension. At h23 the numerator bound is 115 bits and the prime product is 141 bits.

Every nonzero rational corner minor has a nonzero residue in at least one field: otherwise its nonzero bounded integer numerator would be divisible by the larger prime product. Each field corner rank is at most its rational rank. Therefore the **maximum of the five northeast corner ranks** equals the rational northeast rank. Rank second differences reconstruct the rational ordered pivot permutation. A union of modular pivot sets would not be valid.

The first field's full transition rank is also exact. A nested projector difference is idempotent, with rational trace equal to its rank `r<h<p`. Idempotence and trace descend to every admissible field, where rank lies in `[0,h]` and is therefore determined by that trace. This does not establish individual corner ranks, which still need the five-prime numerator argument.

The upstream source pays every rank-one and rank-two transition as singleton children. This is a safe conservative fallback, not a claim that every such transition has only singleton runs. Any later rank-two refinement needs a distinct build/output suffix and finite receipt.

## Complete two-axis controller arithmetic

[fixed_controller_score.py](code/fixed_controller_score.py) accepts two complete ORIGINAL fixed profiles. It checks `v=binom(h,3)`, `loss=h(h-1)`, and block mass `hR+2loss`. For each axis it removes the `h` known identity cleanup blocks and adds `h` rank-one complement calls, giving copied mass `hR+loss`. It retains every copied transform's actual fixed profile.

For dimensions `a,b`, set `m=ab`, `N=binom(a,3)binom(b,3)`, bank `Bi=(N/vi)Ri`, `W=2N+B1+B2`, and `L=sum_i (N/vi)loss_i`. Charge all these parallel families:

- copied internal blocks, each repeated `N/vi` times;
- `Bi` exterior pairs of widths `hi` and `m-2hi`;
- `2N` source-growth pairs of widths `1` and `hi-2` for each axis;
- all data children;
- `N` paid endpoint children of width one.

For ordered `(23,25)`, the inherited fixed-both data geometry has `2N` copies of `9*[1]+[21,17,481]`. The total block mass must equal `Wm-N+L`, and every child must be strictly narrower than `m`. The normalized characteristic moment at saving `a_bit` is

`sum_t count[t] * (t/m)^(1-a_bit) / W`.

The scorer's 24-term rational logarithm bounds and conservative exponential bound prove strict pass/fail inequalities. [fixed-controller-reference.json](fixed-controller-reference.json) reproduces the eligible pinned reference from its compact h23/h25 profile files: `W=188181929`, rank mass `108202762275`, deficit `1846900`. This is small arithmetic, not an unchanged large graph replay.

Known reference input paths are

`work/scout/snapshots/pr40-43f59ff53359/research/copied-both-reversed/profile-23.json`

and

`work/scout/snapshots/pr40-43f59ff53359/research/copied-fixed-reversed/profile-25.json`.

These are ignored downloaded inputs, so normal `rg --files` omits them; use exact paths or `--no-ignore` when locating them. Reacquire the pinned archive through `gh api repos/rohanarun/integer-mult-bounds/tarball/43f59ff533598762cbc43a5e14af2bbbc76fabbd`, extract it in a fresh ignored directory, and verify the retained input hashes.

For other dimensions, `--optimistic-data` charges one ideal block with the minimum concave moment for the required residual rank. An optimistic FAIL excludes this paid topology. An optimistic PASS supplies no physical data geometry and cannot support a new multiplication bound.

## Changed-controller review

[changed-fixed-review.md](changed-fixed-review.md) independently reviews the changed h23 tree paired with the unchanged fixed h25 producer. It explains why the existing complete data-corner proof applies to the unchanged source families, checks the native `C1=1` and product-row constants, and preserves an independently implemented exact complete-moment check. The all-size tape/compiler assumptions remain explicitly conditional.
