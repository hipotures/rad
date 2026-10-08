# Exact cancellation frontier of the trimmed side DAG

Four workers reconstruct all 82,265 output coefficients at (h,k)=
(7,3),(8,5),(10,5),(10,7). Every final output is an actual addition whose
two predecessor supports span h, whose self coefficients cancel, and
whose resulting support spans the target-orthogonal hyperplane h-1.
The complete rank-decreasing-node receipts are retained.

This is an exact scalar-DAG audit and does not assign arbitrary dirty
physical roles. A separate-output materialization bound applies under
explicit source/full-center/kernel continuation assumptions; global shared
pair-frontier schedules remain open. See
[the scope and proof](../../reports/complex/trimmed-cancellation-frontier.md).
