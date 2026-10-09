# Independent analytical review of three selected scans

Status: **ACCEPTED ANALYTICAL RESULT WITH EXPLICIT SCOPE**, 2026-10-09.
This coordinator review concerns the synthesis agent's frozen
[three-scan report](../synthesis/three-ordered-scans-and-dyadic-lift.md).
It does not rerun that agent's finite measurements or constitute external
peer review or proof-assistant verification.

The reviewed model retains the fixed Boolean address labels, one amplitude
bank, natural/bit-reversal prefix or difference scans, and arbitrary nonzero
complex address-diagonal gauges. Independent endpoint permutations, other
orders, additional dirty banks and non-diagonal wrappers remain outside.

The coordinator independently reconstructed all four consecutive reversal
pair reductions. Factoring a prefix by its smaller inverse D gives the
two-by-two upper-block H = D-I. Requiring a zero upper-right block forces
B0 H + H B1 = 0 for equal scan types and B0 H - H B1 = 0 for mixed types.
The forced diagonal blocks are respectively R B0/B1 R, B0 D/D B1, B1,
and B0. The remaining natural factor gives at most two smaller scans in
one target diagonal block. The earlier complete fixed-label two-axis
exclusion covers f=3; the growing two-scan restrictions cover larger f.

For two separated reversal scans, left/right inverse multiplication on
prefix wrappers yields the report's four signed combinations of UH, HV
and HWH. With r=m/2 and c=m/2-1, the smaller reversal successor/predecessor
relations give H[r,:]=-e0^T and H[:,c]=-e_(m-1). Natural lower triangularity
therefore kills (UH)[r,c] and (HV)[r,c]. The third contribution is exactly
W[0,m-1], a nonzero product of two diagonal units and the natural bridge
entry. It cannot cancel. Zero/three reversal factors separately have common
order midpoint cut rank at most three, while the zeta cut has rank m>=4.
The one-reversal case retains its nonzero upper block under invertible
natural neighbors. This covers all selected three-factor cases.

The resulting all-size exclusion for f>=3 is accepted over nonzero complex
gauges. This is stronger than the earlier selected real-dyadic F3 screen;
it does not broaden that screen itself. The exact f=2 dyadic lift remains
a local three-scan realization with all scales and grid reserve paid.
Its scan-count improvement is not an addition-count or native improvement.

Frozen inventories:
[selected package](../../configs/synthesis/three-scan-selected-publication.json),
[high-flux package](../../configs/synthesis/three-scan-flux-publication.json).
The high-flux shear lies outside the all-size selected-order theorem. Its
chosen finite negatives and unpaid native boundaries retain their stated
scope. No multiplication exponent follows from this review.
