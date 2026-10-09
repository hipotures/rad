# Independent review of the full Walsh/cyclic embedding boundary

Status: **ACCEPTED ANALYTICAL SCOPE REVIEW**. This receipt is independent
internal mathematical review, not formal verification or a new execution of
the exhaustive controls. It accepts the coordinator's stated obstruction for
one complete cyclic or negacyclic transform with invertible monomial
boundaries. No multiplication exponent is inferred.

Reviewed on 2026-10-09 UTC: [the proof and source attribution](../obstructions/walsh-single-cyclic-convolution-boundary.md)
and [the standalone exact generator](../../code/obstructions/walsh_cyclic_embedding.py),
source SHA-256 `d9d35fe680a3dcb014f9a20f3aaee59493c8786c1f1f8a5d980c1fc81b5a5655`.
The existing [four-worker evidence](../../runs/20261009T043158Z-walsh-cyclic-embedding/report.md)
is reused with its unchanged dependencies; this reviewer did not duplicate
that enumeration or independently verify every recorded finite case.

The cross-ratio step is valid for arbitrary nonzero complex row and column
factors. Four entries cancel those factors and leave the centered binary
pairing identity. The centered opposite permutation is a bijection, hence
spans the full binary space. Additivity of the pairing then forces each
centered permutation to be linear; their linear parts are inverse
transposes. This argument requires neither unit modulus nor positivity.

Conjugating the simultaneous full shift through the proposed monomial
boundaries retains a full-cycle underlying row permutation. Signed
negacyclic shifts have the same permutation requirement. The homogeneous
binary matrix of an affine full cycle has the same order as that permutation:
the affine points `(x,1)` span the homogeneous space. Its nilpotent index is
at most `f+1`, giving order at most `2^ceil(log2(f+1))`, strictly below `2^f`
for `f>=3`. The order-four positive case remains a genuine exception; the
proof does not extrapolate its negative claim to it.

The Gaussian gauge identity is exact, since
`weight(x xor y)=weight(x)+weight(y)-2(x dot y)` modulo four. Thus
`C_f=alpha^f D H_f D`, with `D[x]=(-i)^weight(x)`, transfers the same
necessary permutation condition through nonzero diagonal factors.

The conclusion does **not** cover the length `2^f-1` nonzero field core with
its separately handled zero coordinate, multiple convolutions, Toeplitz
restrictions, sums or products of structured maps, larger extension
algebras, sparse operand subspaces, changed output contracts, nonmonomial
bilinear encodings, or complete native routing costs. The separate partial
Gaussian product algebra investigated by this track changes the bilinear
interface and is outside this theorem. These boundaries are necessary to
keep the accepted obstruction from becoming an unsupported general lower
bound.

Attribution and AI assistance: the affine automorphism context comes from
the primary author manuscript identified in the reviewed coordinator
report. This receipt checks that report's elementary derivation; it imports
no additional source theorem. The review was produced by the complex
research agent in the coordinated AI-assisted campaign.
