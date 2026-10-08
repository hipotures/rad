# Arbitrary quadratic-phase independent controls

Status: **EXACT AUXILIARY CERTIFICATE**. The independent full-payload
decomposition passes; no native fixed-tape implementation or exponent is
certified.

Four workers verified 128 cases, 3,680 complete records and three dyadic
complex fields per record. The literal one-child decomposition, canonical
frame-difference correction and inverse dirty restoration agree exactly with
the Fourier reference. All symmetric three-by-three matrices are included.
Seventeen quotients are alternating and 21 have nonzero radical translation.
Bulk two-column cases are checked. Runtime was 0.293 seconds.

Negative controls detect omitted radical translation, deleted-diagonal
correction, alternating global unit and complete payload fields. The triangle
radical witness shows why affine routing cannot be called a scalar phase.
The unit wrappers introduce no extra denominator or magnitude growth outside
the child. Paid fixed-tape address routing, actual guards, scalar-network
semantics, complete child moments and all-size integration remain open.

See the [independent proof and review](../../reports/transfers/general-quadratic-phase-review.md)
and [protocol](protocol.json). The source is self-contained, deterministic,
standard-library Python with recorded seeds. The full source-generated JSON
is retained in the ignored work location given in the protocol; the compact
summary omits per-case timing and matrix listings, which can be regenerated.
