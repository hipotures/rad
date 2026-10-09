# Independent analytical review of general scan cut rank

The coordinator source `code/obstructions/scan_order_cut_rank.py` at SHA-256
`ddec3f540c5fbfe0f398f666674bcd81634febb6f2a59f6154666f317e563132`
was read as source only. The producer was not imported or executed and its
891-order measurements were not rerun by this review. This receipt therefore
separates analytical/source acceptance from the producer's finite evidence.

For a fixed bit cut, let r be the number of adjacent 0-to-1 transitions in the
address order. The initial 1-run has no preceding zero columns and contributes
only zero rows. The final 0-run has no following one rows and contributes only
zero columns. Every other one row belongs to its most recent positive
transition, and every other zero column belongs to its next positive
transition. Prefix entries are one exactly when the column's transition index
is at most the row's index. This proves the complete factorization E L_r F,
including r=0. Choosing the first one-row and preceding zero-column at each
transition gives the unit lower-triangular minor L_r. Difference entries are
minus one only at the disjoint transition pairs, giving the minor -I_r. Thus
both ranks are r over every field, even for initial-one/final-zero edge cases.

The implementation's row_groups/col_groups, complete entry checks, unit
minors, and empty-transition handling bind that proof. Its finite-field
elimination is a separate independent control, not the proof of all fields.
Nonzero left/right diagonal gauges preserve the cross rank; the zero-gauge
negative correctly identifies a domain restriction.

For two arbitrary matrices partitioned by the same fixed Boolean coordinate,
(AB)10=A10 B00+A11 B10, so cross rank is subadditive. Each fixed-label zeta
cross block identifies with Z_(f-1) and is unit lower triangular of rank 2^(f-1).
Summing the factor inequalities over f coordinates yields total word flux at
least f*2^(f-1). The Hamming path identity counts positive versus negative
coordinate changes and is unaffected by coefficient cancellation.

An independent endpoint permutation must be charged as a factor or must
change the target cut analysis; it cannot be discarded as a free renaming.
Arbitrary nonlex orders are covered by the flux lemma, while the stronger
lexicographic closed bound requires that stated order restriction. Extra
dirty banks, projections and nonlinear amplitude words are outside this
one-bank factor model. The proof supplies neither native head motion nor a
multiplication exponent. Whole prefix amplification, dyadic coefficient
heights, complete record geometry and routing remain paid obligations.
