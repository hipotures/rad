# Exact support-span drops at the trimmed side cancellation frontier

Status: **EXACT FINITE SCALAR-DAG AUDIT AND SCOPED PHASE BOUND**.
This audit does not prove a lower bound for arbitrary globally shared
circuits or establish a multiplication exponent.

The coordinator's [trimmed side transform](../obstructions/trimmed-side-transform.md)
has a much smaller scalar DAG than the weighted-tree construction.
Its degree-k identity term cancels a low-degree central sum.
The present audit reconstructs every characteristic-zero coefficient
at every node, then computes the binary span of its actual nonzero
source labels. It uses the parent source read-only, pinned by SHA256
`c7093318d5892d7a2161f5614135f7f94be474a91dcd4a95ef5eb0b1ef498ced`.
The complete scalar coefficients and small gate frontier are generated
deterministically from that preserved source.

For an addition `a+b`, let U be the span of both predecessor supports
and F the span of the resulting support after exact cancellations.
The measured decrease is `dim(U)-dim(F)`. This is a scalar support
quantity; it is not automatically a physical phase-edge charge.

Four workers complete [the bounded audit](../../runs/20261008T224752Z-complex-trimmed-frontier/)
in under half a second:

| h | k | Sources | All output coefficient checks | Rank-decreasing additions | Final output decreases |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 3 | 35 | 1225 | 63 | 35 |
| 8 | 5 | 56 | 3136 | 218 | 56 |
| 10 | 5 | 252 | 63504 | 637 | 252 |
| 10 | 7 | 120 | 14400 | 967 | 120 |

Every measured decrease is exactly one. At EVERY final output the
predecessor support spans together have dimension h, while the final
support spans the target-orthogonal hyperplane of dimension h-1.
Both predecessors carry a nonzero self coefficient with opposite signs;
the final gate cancels it exactly. All 82,265 output coefficients pass
the independently evaluated intersection polynomial. Each receipt
retains the actual parent nodes, their dimensions, the canceled self
coefficients, scale denominators and source hashes.

The [degenerate-frame embedding](degenerate-subspace-clifford-frames.md)
allows ANY nested binary subspaces, so degeneracy itself causes no extra
helper loss. The canceled decrease remains: a full predecessor span does
not nest in the final kernel. This is why merely replacing rational
projectors by degenerate Clifford frames does not compile the present
SSA topology at its optimistic scalar count.

A precise local negative applies to the separate-output materialization
schedule. Suppose a central carrier is in the full frame, its own-source
carrier is in the target line, the two-role cancellation gate retains
the central carrier for a full-frame continuation, and the result must
enter the target kernel. For any common Lagrangian B, all four incidences
cost

```text
d(line,B)+2*d(full,B)+d(B,kernel) >= d(line,kernel) = h.
```

The full frame attains h. Adding the paid source-copy entry of rank one
and final kernel-to-full helper cleanup of rank one gives h+2, two ranks
above one helper's h-capacity. This argument includes full Lagrangian
frames, including non-graph choices. Its premise is the specified
central/full continuation and separately materialized output. A bounded
all-135-Lagrangian check at n=3 confirms the same minimum; the inequality
itself is dimension-independent.

Charging such a separate return per output is too large for the
inherited five-subset moment envelope. This does not establish a universal
per-output loss: shared pair centers, interleaved cancellation, a different
virtual data basis or different source/sink chronology change its premises.
The synthesis track independently audits a concrete retained-SSA dirty
chronology; this report does not import its role allocator or claim that
SSA slots equal the physical motif R.

The useful next test is a joint pair-feature frontier with complete
physical source/target anchors, rather than another exhaustive parameter
sweep over this terminal materialization. Scalar cancellation, dirty
restoration, frame rank and recursive bit guard must be proved together.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/trimmed_frame_frontier.py \
  --h 10 --k 5 --output /tmp/fresh-trimmed-frontier.json
python3 -B research/integer-mult-breakthrough/code/complex/test_degenerate_frames.py
```

The audit imports the persisted coordinator scalar source but never changes
it. All dependencies are task-owned source or Python's standard library.
Raw logs remain in the ignored task-owned workspace; small complete
frontier receipts, larger compact summaries and regeneration instructions are durable.

## Complete frontier evidence recovery

The larger [h10 k5 summary](../../runs/20261008T224752Z-complex-trimmed-frontier/results/h10-k5.summary.json)
and [h10 k7 summary](../../runs/20261008T224752Z-complex-trimmed-frontier/results/h10-k7.summary.json)
retain counts, histograms, hashes and the exact scope. They omit the listed
rank-decreasing addition and final-frontier rows. Complete unchanged originals
are in [h10 k5 gzip](../../evidence/20261008T230948Z-checkpoint-four-20261008T224752Z-complex-trimmed-frontier/results/h10-k5.json.gz)
and [h10 k7 gzip](../../evidence/20261008T230948Z-checkpoint-four-20261008T224752Z-complex-trimmed-frontier/results/h10-k7.json.gz).
Original local files are unchanged and ignored.
