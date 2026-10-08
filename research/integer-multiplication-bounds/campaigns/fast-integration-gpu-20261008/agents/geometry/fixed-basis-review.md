# Changed-DAG fixed-basis transfer and exact-profile review

Status: accepted algebraic/finite component for the original-envelope witnesses; literal compiled dirty-state restoration is independently checked by the graph worker. This is not formal verification or external human review.

The immediate fixed-basis mechanism is Dominik Scholz's PR38 at `cc794077f6c103e24ec0939be765cd1521239aab`, based on icekylinx PR32/36 and PR35. The campaign contribution is to replace its unchanged scalar DAGs with new association and point-order DAGs, then reconstruct the actual original-envelope matching and every local physical matrix profile. Positive-label matches are never reused for this specialization.

## Original-envelope identities and chronology

For a common core C and union M, the original label is `E(C,M)`, supported on M with equal coordinates t on C and `sum x=3t`. Put `O=M\C`, `c=|C|`, `s=3-c`. An integer basis is obtained by giving one outside coordinate the value s and every forced core coordinate the value one. Each label is positive and nondegenerate under the exact common-point identity `x^T(I-J/9)x=sum_(j!=i) x_j^2`. Sources are the original norm-two triple lines.

The independent axis checker reads native witness bytes directly and verifies every operand inclusion, selected donor inclusion, output exclusion, scalar support and terminal-use separation. It reconstructs local ranks and copied-center histograms without importing the original matcher. The fixed basis uses its own original envelope ranks, dependencies, selected use identities and exact matching cardinality. In particular equality of a role count with a positive-label construction would not justify identifying their geometries.

Forward nested growth differences `P_V-P_U` and inverse complementary differences are the same rational idempotents, because the verified positive spaces are nested. Original designated total outputs are h separate terminal-use vertices at rank h-1. The paid copy/transform/read/discard schedule applies to those actual terminal reads and preserves the original source/sink operators. It removes exactly h width-h original cleanups and adds h singleton complements, retaining every rank-(h-1) copy transform. All N rank-one data endpoint corrections remain.

## Fixed basis and complete physical profiles

The local bases are `L_h=I_h+J_h`. Their inverses are `I_h-J_h/(h+1)`. With the pinned controlled permutation completions, each factor-sized ambient corner is a nonzero diagonal scaling of the actual local conjugate. Thus the exact local rightmost pivot runs transfer to physical contiguous blocks; there is no runtime basis adapter.

The native profiler reconstructs the entire multiset of matrices before profiling. An addition z contributes `degree(z)-1` copies of `P_z`, one `I-P_z`, and the two operand growths. A source contributes degree-many line projectors. A designated total contributes `P_z` and `I`. A selected donor continuation removes the three actual matrices `I-P_donor`, `P_value`, `P_target-P_value` and inserts `P_target-P_donor`. These are multiset operations with separately verified use identities. Side growth and its line cleanup remain conservatively singleton calls. Zero rank is retained in accounting and omitted only from the recursive call list.

## Why modular profiles are exact here

The separate [rational checker](code/fixed_formula_review.py) constructs envelope projectors from an independently chosen Gram basis. For core size c and n outside points that Gram is `I+(c-1)J/(3-c)^2`, with explicit Sherman-Morrison inverse. Direct conjugation by `I+J` equals the supplier's fixed formula entry by entry. It also checks same-core growth correction ranks independently on retained rational controls.

Each local matrix is a zero-one diagonal mask plus a rational correction of rank at most two for a single envelope, complement or same-core growth; at most three for source growth; at most four for a core-two to core-one growth. The first two rank bounds follow from the common-point orthogonal basis, and the latter two from subtracting respectively a rank-one source or two rank-two corrections. Nested covers and decreasing cores make the diagonal mask difference zero-one.

For h23 and h25 define `Z=3h-7`, `B0=(4h-2)Z+27(h+1)`, `D=3(h+1)(h-1)^2` and `B=2(h-1)B0`. The independently checked numerator bound B0 holds in every admissible membership category and outside size. Each constituent denominator is `3(h+1)d` with `d<=h-1`; their common denominator is at most D and each multiplier is at most h-1. Therefore B bounds a two-projector correction numerator.

For a correction of rank at most r, expand an e-square determinant by choosing correction columns. Terms with more than r correction columns vanish. Multiplying by the actual common denominator to power r leaves an integer of absolute value at most

`sum_(j=0..r) binom(h,j) j! B^j D^(r-j)`.

This bound does not depend on e. The r2 bound is below the prime `2^61-1`; the r3/r4 bounds are below `(2^61-1)(2^31-1)(2^19-1)`. Independent Lucas-Lehmer checks confirm all three primes. Every constituent denominator is smaller than the least prime. Thus a rational northeast minor is zero exactly when all applicable modular reductions are zero. Its rational rank is the maximum of the modular ranks, even if their individual pivot patterns differ. Taking northeast-rank differences recovers the exact rational ordered pivots. The three-prime native checks are therefore exact finite certificates rather than unqualified numerical samples.

The rank-two follow-up explicitly profiled every formerly conservative rank-two matrix in six changed DAGs, and obtained exactly the same aggregate children. This informative exclusion changes neither source nor stock and does not exclude another basis.

## Complete common-basis choices

For both local bases fixed, use PR38's verified unreversed dimensions `(25,23)` and its conservative data profile 26 singletons plus `[21,481]`. Its two bipartite restriction trees prove full data-corner rank for every nonzero primal/dual coordinate choice, and its explicit first-block elimination supplies the 21 run. The h23 and h25 new original-envelope matrices are finite explicit specializations of the same fixed local construction, so their exact native profiles already share this ambient basis.

Alternatively PR39 fixes only the middle L25 and leaves L23 free in the reversed `(23,25)` geometry. Its full 2300-line prefix proof and irreducible finite-product argument preserve nine singletons plus `[21,17,481]`. New first-axis positive residuals add ordinary nonzero minor conditions on that same free GL23 family. This hybrid therefore requires the fixed original-envelope second-axis witness and the positive generic first-axis witness. Both-fixed profiles cannot reuse the hybrid's 17 block.

The coordinator separately reconstructs complete moments and all 47 assembly conditions with paid endpoint, scalar, stock and semantic interfaces. Fixed rational setup, eligible address primes, native tables, tape/layout constants and eventual thresholds remain explicit qualifications.
