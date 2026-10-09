# Actual canonical Clifford side-word replay

The complete framed identity shear passes finite physical replay through
chosen noncoordinate and degenerate Clifford frames. This closes the
actual-operator gap in the small geodesic edge-helper component. It does
not remove the separately paid raw-input canonical `C_h` wrappers.

[canonical_geodesic_side_review.py](../../code/synthesis/canonical_geodesic_side_review.py)
consumes A's standalone
[canonical_subspace_frames.py](../../code/complex/canonical_subspace_frames.py)
read-only. For every subspace used in the word, it independently executes
the literal `D/P/Htilde` frame specification on every address basis
column and binds the result to the API's integer coefficient matrix.
Line, full and odd-kernel overrides are actual operators. Every scalar
gate checks equality of the chosen current actual frame. Every nested
relative transition is compiled with one child of the dimension difference,
paid affine input/output maps and explicit quadratic fourth-root phases.
The q center full-to-zero resets and outgoing returns are retained.

The scalar center is A's unimodular triple-total basis. Its source order
and decoder are explicit, and the side edge coefficients are independently
derived from `I-(intersection-1)/2`. All sources, sinks, dirty center
helpers and dirty side helpers have fixed labeled endpoints. The exact
integer Gaussian engine tracks a common dyadic denominator per bank;
there is no floating operator calculation.

Four independent cases completed:

| h | Selected columns | Source order | Explicit input columns | Complete Gaussian fields |
| ---: | ---: | --- | ---: | ---: |
| 4 | 1 | Forward | All384 | 3 |
| 4 | 2 | Forward | 17 selected origins | 3 |
| 5 | 1 | Forward | 35 selected origins | 3 |
| 5 | 1 | Reverse | 35 selected origins | 3 |

The h4 cases use24 physical banks. The h5 cases use90 physical banks.
The h4/f1 case checks every physical address/bank column. Other cases
check only the stated origins plus every bank/address value in three
complete Gaussian dyadic fields. They do **not** claim full basis coverage
from origins. Their complete-field checks cover36,864 payload values
across the four cases. The actual dirty endpoint in every case is
`C_full` times the original virtual dirty value.

The h4 words exercise three generic frame representatives; h5 forward
and reverse exercise16 and13 respectively. Removing an indispensable
helper cleanup fails. Skipping an actual generic-frame transition while
advancing its nominal label also fails. A separate even-line generic
representative proves that the per-gate XOR covariance shortcut is false.
Internal generic representatives need not be convolutions. Only the
complete end operator has the desired convolution structure, which follows
from the exact shared-frame scalar/telescoping equations.

The finite word's width ledger agrees exactly with
`Wh-2v+2qh`. At these small triple cases the deficit is negative, as
expected: h4 has deficit-24 and h5 has deficit-30. The larger abstract
capacity profiles are separately scoped in
[geodesic-edge-side-component.md](geodesic-edge-side-component.md).
No positive multiplier saving is inferred from the small operator replay.

The completed
[actual-time run](../../runs/20261009T015416Z-synthesis-canonical-side-word/report.md)
records four workers, the complete loaded source closure, exact output
hashes and coverage. All raw originals remain immutable.

Reproduce from the worktree root with a fresh output directory:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/canonical_geodesic_side_review.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-canonical-side-word/results
```

The next structural task is a joint signed exchange or other complete
canonical architecture. Independent raw-input source encoding and sink
repair consume two width-one calls per label and erase the framed saving.
Native tape layout, precision, larger all-column replay, full primitive
assembly and asymptotic transfer remain open.
