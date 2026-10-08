# CRT movement negatives and an alternative carry interface

Completed exact controls on 2026-10-08. The known coordinate-bit router cannot
perform the inherited modular CRT map unchanged. A separate guarded-reflection
replacement is reviewed in [the layout review](crt-reflection-layout-review.md).
This note preserves scoped negatives and a different, unpromoted backup.

## Exact existing schedule and failed shortcuts

For `P_i=product_(j<i)s_j`, `mu_i=P_i^-1 mod s_i`, and scalar digit index
`k=sum_i a_i P_i`, the required tensor coordinate is

`b_i=a_i+mu_i sum_(j<i)a_j P_j mod s_i`.

Descending valid-interval rotations keep each prefix original. The independent
checker simulates actual two-piece target rotations with complete spectator
suffixes, then the ascending inverse. Five prime shapes in2--4 dimensions pass
24,573 valid records; their forward/inverse programs charge525,376 full-record
reads and the same number of writes. These are counted copies of the existing
schedule, not an inference from metadata work.

The following exact controls exclude specific substitutions:

- With primes3,5, input digits(1,0) map to CRT digits(1,2). Padded binary
  Hamming weight changes from1 to2, impossible for a known slot permutation.
- CRT output lexicographic order contains decreasing scalar source indices,
  so it cannot be produced by the product-monotone source embedding used for
  Gaussian packets. Uncached single-head traversal counts are retained.
- Scalar inputs at indices2 and1 multiply to index3 in cyclic order15.
  An unrouted3x5 tensor instead places their product at scalar index0 because
  it drops the mixed-radix carry. Matching both operands in that wrong layout
  does not repair ordinary convolution alignment.

These are scoped exclusions. They prove neither optimality of O(dV) CRT nor a
lower bound against arbitrary new fixed-tape algorithms.

## Alternative global mixed-radix addition and sparse carry corrections

At a balanced CRT tree depth one could gather all LEFT controls and all RIGHT
targets, compact the right product to one true mixed-radix scalar X, and add
the encoded vector C of desired component offsets in ONE controlled rotation.
Let its output digits be y. The incoming carry for digit i is exactly

`carry_i=1[lower_scalar(y,i)<lower_scalar(C,i)]`.

Then `(y_i-carry_i) mod radix_i` is the desired independently rotated digit.
Comparing only the preceding digit gives the same carry unless it equals
the corresponding offset digit. Comparing their upper bits similarly works
away from an explicitly excluded low-bit block.

On the remaining set, unit decrements can be formed by descending low-bit
flips, whose controls depend only on unchanged lower bits and a previous
digit's upper bits. A high borrow out of the truncated field is another
explicit exclusion. This suggests a compact predicate gadget and sparse
exact repair, but that gadget and its complete physical field placement have
NOT been implemented or proved here. The exact reflection route avoids these
approximation obligations and is the preferred candidate.

The fresh three-worker family checked1,012,000 random/adversarial states and
16,748,000 exact carry identities with radices of10--256 bits and2--128
dimensions. It passed957,121 good-state corrections and16,011,665 selected-bit
flips. Adversarial trials deliberately hit equality thresholds and high borrows;
the measured exclusion frequency is therefore not an unbiased density estimate.
Both negatives are retained with exact digits and required outputs. Family
wall time75.51 seconds; per-profile times6.60,15.93,75.47 seconds.

## Reproduction

```sh
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout/code/check_crt_movement_obligations.py \
 --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/layout/fresh-crt-negatives
OMP_NUM_THREADS=1 python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout/code/check_joint_crt_carries.py \
 --workers 3 --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/layout/fresh-crt-carries
```

Python3.14.4 standard library. Source digests, exact configurations, seeds,
counts, and negatives are in
[the existing-schedule certificate](results/crt-movement-obligations.json) and
[the carry certificate](results/joint-crt-carries.json). These inputs are
deterministically regenerable. Neither control claims to implement a fast
computed-key sort or to certify a complete multiplication exponent.
