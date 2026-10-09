# Independent review of the cap-row spectrum and materialization census

This is a source-based analytical review of the coordinator's
[`paired_cube_cap_channels.py`](../../code/obstructions/paired_cube_cap_channels.py)
and separate
[`paired_cube_cap_channel_census.py`](../../code/obstructions/paired_cube_cap_channel_census.py).
The producer manifest is `configs/obstructions/cap-channel-milestone.json`,
SHA-256 `bac37b863d9cf93cca6b2423d06f9c99b0b2886238556e8b5ce85bb2578f0350`.
The producer's exact finite rank runs are not rerun or described as independent
finite enumeration here. The independent dirty-bank and fanout experiments
linked below test additional physical-stock obligations.

For odd `k=2r+1` and a proper intersection `J` of size `j`, the scalar row is
`f_k(j-wt(u xor t))`, where `f_k(x)=binom((x-1)/2,r)`. Every even integer
argument from zero through `j` is nonzero, and every odd argument is a root.
For `j>0`, the exact support therefore requires
`parity(u)=j mod2 xor parity(t)`. Within one target parity the literal source
support is identical; the two target parities have disjoint source supports.
Flipping a shared selector bit exchanges the two blocks. Keeping actual
independent rows separately within each target parity preserves full scalar
rank and the physical cap flag. The source support spans the codimension-one
cap of the `(k+1)`-dimensional full-cube label span, hence has dimension `k`.
For `j=0` the literal support is the full cube and has dimension `k+1`.

The all-odd spectral formula follows without a numerical assumption. Extend
the `j`-bit difference by `k-j` ones in the normalized full-cube low-character
expansion of `f_k`. Fourier summation over those `j` bits leaves, for a
character of weight `a`,

```text
lambda(j,a) = 2^(j-k+1) sum_{ell=0}^{r-a} (-1)^ell binom(k-j,ell)
            = 2^(j-k+1) (-1)^(r-a) binom(k-j-1,r-a).
```

The last expression is zero when `r-a<0` or `r-a>=k-j`. The elementary partial
alternating-binomial identity supplies the second equality, including those
zero tails. Thus

```text
R_j = sum_{a=max(0,j-r)}^{min(j,r)} binom(j,a).
```

The separate parity blocks each have half this rank for `j>0`. This confirms
the reported `k5` ranks `1,2,4,6,6`. For all available proper `J`, the weighted
rank census counts three-color assignments with the first two color counts
both at most `r`. The two excluded events are disjoint because
`2r+2=k+1`. Consequently

```text
S_k = 3^k - 2 sum_{a=r+1}^k binom(k,a) 2^(k-a).
```

This confirms `S3=13`, `S5=141` and `S7=1429`. A binomial Chernoff bound for
success probability `1/3` bounds each excluded fraction by
`(sqrt(8)/3)^k`, so `S_k/3^k` tends to one. Its ratio to the `2^k` input count
therefore grows like `(3/2)^k` under distinct retained-cap materialization.
It is not a universal physical-role lower bound: joint source bases,
chronological role reuse, shared kernel parking, target mixing and changed
readout ports are outside that counting premise. The scalar all-`J` span can
still be only `2^(k-1)`.

The all-proper-`J` census requires at least `2k` paired coordinates. A literal
source cube in a `p`-pair host can meet a target cube in `j` pairs only if
`j>=max(0,2k-p)`. At `p9,k5`, `j0` is absent: the raw/live/parked counts are
`210/140/70`, rather than `211/141/70`. At `p7` only `j3/j4` are present,
with counts `160/90/70`. These restrictions change materialization counts;
they do not invalidate the abstract scalar rank formula.

The independent
[`dirty completion and fanout report`](cap-dirty-completion-and-fanout-boundary.md)
accepts the component-level dyadic realizability while retaining every parked
bank and every scalar multiplication temporary. It also shows why a live
channel rank does not supply a completed native side word. No result in this
review certifies a new exponent, formal proof package, or full arbitrary-dirty
Gaussian address compiler.
