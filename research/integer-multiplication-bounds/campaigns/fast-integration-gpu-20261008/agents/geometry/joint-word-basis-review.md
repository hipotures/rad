# Actual executed-word geometry

The initial PR62/PR57 geometry checks completed on 2026-10-08 at 18:17–18:25 UTC. They use the unchanged compressed XOR words, rather than a scalar-DAG gate histogram. The pinned source is CrocSwap PR62 head `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`; its compiler/profile helpers are inherited from the authorized PR57 head `cd350f76c9bc01489ec83568bded532cb69be938`. The upstream contributor credits and Apache notices are retained in the adapted native source. Scalar compilation, whole dirty-basis replay, source-only recovery, and the full recurrence are separate graph/coordinator gates.

## Frames, nesting, and the rank upper bound

Let `H = I - J/9`. An ordinary frame with forced set `C`, support `U`, `c = |C|` in `{1,2}`, and `O = U \ C` has basis

`b_j = (3-c)e_j + 1_C`, for `j` in `O`.

Writing `s = 3-c`, its exact Gram matrix is `s^2 I + (c-1)J`. This is positive definite: it is `4I` for `c=1`, and `I+J` for `c=2`. Its rank is therefore `|O|`. A source frame has `C=U` equal to a triple, basis `1_C`, and `H`-norm squared `2`. The zero frame and whole ambient frame have ranks zero and `h` respectively. All these frames are nondegenerate.

An ordinary frame consists exactly of vectors supported in `U`, constant with value `a` on `C`, and satisfying `sum_{j in U\C} x_j = (3-c)a`. The source triple satisfies the same coordinate conditions with `c=3`. If `C_b` is a subset of `C_a` and `U_a` is a subset of `U_b`, then moving the `c_a-c_b` dropped forced coordinates into the outside sum changes it from `(3-c_a)a` to `(3-c_b)a`. Thus the smaller frame is contained in the larger frame. This also covers source-to-ordinary growth. The transition extractor checks these two mask inclusions on every chronological nontrivial incidence; zero births and cleanup into the ambient frame are immediate.

For the corresponding `H`-orthogonal projectors, nesting gives `P_a P_b = P_b P_a = P_a`. Hence `P_b-P_a` is an idempotent of rank `rank(P_b)-rank(P_a)`. An invertible common basis preserves this identity and rank. This is the independent rank upper bound used by the general integer-minor profiler. It is not inferred from the largest modular rank or from a numerical trace.

## Actual word extraction and charges

The pinned `binary_frame_profile_prepare.py` reconstructs physical incidences directly from the source entrance assignments, every XOR operation, and the terminal outputs. It verifies the resulting positive transition multiset against the compiler's separate event chronology. It adds the prescribed copied retained-center birth and original cleanup, terminal side singleton charges, and final cleanup of every nonterminal physical role. Its resulting rank mass is `h R + h(h-1)`.

The new geometry driver requires that this extraction equals the pinned transition receipt. The unmodified fixed-basis native mode must reproduce the public profile object exactly. Both requirements passed for `h=23` and `h=25`. The retained-center charge is already present in these word profiles; a composition must not apply the older per-DAG copied-center histogram adjustment again.

The rank-one side/source corrections remain separately charged as in the executed-word extractor. Their source-specific endpoint and inverse chronology are inherited dependencies, rather than a claim that every terminal can be replaced by a generic center complement.

## Common basis and conjugation

For `L(beta)=I-beta J`, with `beta != 1/h`, put `gamma=(9 beta-1)/(3(1-h beta))`. The conjugated ordinary frame projector is

`P = D + [s u z^T + s w u^T + v w z^T - (c-1)u u^T]/d`,

where `D` is the diagonal mask on `O`, `u=1_O`, `v=|O|`, `d=s^2+(c-1)v`, `w=1_C-3 beta 1`, and `z=1_C+gamma 1`. This is the singleton-class specialization of the independently reviewed signed-frame formula. The source projector is `(1_C-3 beta 1)(1_C+gamma 1)^T/2`.

The conjugate parameter `beta*=(1-9 beta)/(9(1-h beta))` satisfies `L(beta*) L(beta)=H`. Every original frame projector is `H` self-adjoint, so its conjugated projector and every actual nested transition are transposed under `beta*`. This justifies profiling the transpose of the actual matrices. Northeast rank profiles are still recomputed: transposition by itself is not a preservation theorem for the fixed physical corner flags.

Source and copied-center coordinate nonvanishing, equality of source products under conjugation, and compatibility with the complete data family are separate scoped scout receipts. In particular, arbitrary rational pairs must not reuse the old both-negative histogram or the fixed-I+J data proof.

## Exact corners

`parameter_joint_word_profiles.cpp` clears the exact denominators of each pair of projectors. If the resulting integer transition has entry bound `Z` and the independently proved rank is `r`, every relevant minor of order at most `r` is bounded by `r^ceil(r/2) Z^r`. All larger minors vanish by the nested-projector rank theorem above. The profiler proves every selected 31-bit prime by trial division, checks every frame denominator, and requires a strict prime product above this integer bound.

For every northeast corner, the maximum of its ranks over these primes equals its rank over the rationals. Taking second mixed differences of this exact rank table gives the rook pivots; contiguous increasing runs give the recursive child widths. Taking a union of individual modular pivot lists would not be valid. No low-rank correction shortcut is used in the general parameter profiler.

The separately adapted public fixed-I+J native kernel uses its inherited diagonal-mask/rank-at-most-four minor bounds. Its conjugate and coherent coordinate-isometry modes preserve those entry/minor bounds. The general full-integer profiler and independent direct rational controls provide additional checks of the changed actual-word interface.

## Completed evidence and scoped findings

- [Unmodified h23 word profiles](results/joint-word-20261008T1818-h23.json) and [h25 word profiles](results/joint-word-20261008T1818-h25.json): fixed basis, conjugate basis, and full rank-two replay all have identical child-width histograms. This excludes these two changes on the unchanged word, rather than on all future frame compilers.
- The fourteen exact rational-basis profiles are in `results/joint-word-parameters-20261008T1820-part{0,1,2}.json`. Their full transition bounds and pivots remain in external owned execution storage with hashes in the compact receipts.
- The 224 independently computed Fraction Gram, nesting, idempotence, denominator, minor-bound and rational-pivot controls passed in `results/joint-word-rational-controls-20261008T1826-part{0,1,2}.json`. These selected controls supplement the full native CRT; they are not external human review or a formal proof assistant result.
- The unchanged h25 word at `beta=1/21` replaces two singleton children by one width-two child in one rank-twelve transition. Its two frame IDs are `6040` and `6066`, with ranks `8` and `20`. This is a changed profile of an actual physical transition, not a rank-two residual. Complete assembly and the fixed23/negative25 data gate remain separate prerequisites.

Coherent coordinate-flag experiments are still discovery evidence. They conjugate all frame masks by one permutation while preserving the actual transition IDs and counts. A selected permutation additionally needs source and output relabeling in the literal word, a full source-family bijection, paid endpoint and chronology checks, and exact full recurrence accounting before promotion.
