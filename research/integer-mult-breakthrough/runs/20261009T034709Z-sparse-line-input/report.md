# Sparse-transversal input preparation and volume boundary

Four exact workers completed all four retained cases successfully in about
0.27 seconds of parent command wall time. All 164 restricted input columns,
51,232 exact coefficients and complete Gaussian fields match the copy/phase
formula, its inverse and its physical partial/full endpoint. Omitted phase
and out-of-domain dense-input controls discriminate.

The independently derived original coefficient-layout density exceeds 1/8.
A one-record-per-orbit f-direction transversal has density at most 2^-f,
so f>=3 requires repacking. Its required volume exceeds 2^(f-3) times
the original box; growing f=Theta(p^epsilon) exceeds every polynomial in p.
These claims concern unchanged coefficient-record semantics. Orbit-major
layout conversion, fanout buffers and precision remain separate paid
obligations, and different payload encodings or fused suppliers remain open.

[Mathematical report](../../reports/obstructions/sparse-line-input-volume-boundary.md),
[exact source](../../code/obstructions/sparse_line_input_encoding.py),
[protocol](results/protocol.json), [complete results](results/summary.json),
[original-byte provenance](persistence.json). Original outputs remain unchanged.
