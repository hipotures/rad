# Componentwise positive-frame retention

This is an experimental structural extension of the interval-strip construction
of Avi Eisenberg (PR #62, `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`) and the
joint compiler of eumemic (PR #57, tested at
`cd350f76c9bc01489ec83568bded532cb69be938`). The inherited source-partition,
whole-chain, rational-frame, and earlier construction credits remain applicable.
The parameter-only public refinement is due to Alejandro Zarzuelo Urdiales
(PR #61, `afb7cb67d1858641315cfbf4ac768ee64a8eff3a`). This note and its code
were prepared with OpenAI Codex assistance.

The previous selective construction assigned an address either its original
core/cover space or its complete legal signed enlargement. Componentwise
retention chooses individual additional signed classes. It preserves every
literal XOR and every physical role while changing the actual rational address
projectors and their ordered recursive child widths.

For forced core F of cardinality f in {1,2}, put s = 3 - f. A signed class
has disjoint support C_l, cardinality n_l, signs epsilon_i, and signed sum
tau_l. Its source-coordinate basis column is

    B_l = tau_l 1_F + s epsilon_l.

With H0 = I - J/9, the Gram matrix is

    B^T H0 B = s^2 diag(n_l) + (f-1) tau tau^T.

It is positive definite for every nonempty selected class family. Removing
classes therefore produces a genuine positive subspace. Every class required
by the original E(C,M) is retained. Each such class is a singleton at an
originally covered coordinate; the implementation checks this fact and also
checks exact containment independently after constructing the selected frame.

The complete maximal frame contains all legal terminal annihilators propagated
backwards along every actual physical address transition. A selected subset
therefore remains within every required output kernel. Source triples and
copied-center endpoints are protected by the original-frame containment and
their separately checked literal descriptors.

For an actual transition from A to B, assume A is already contained in the
maximal B frame. The coefficients of a vector in that maximal B basis are
uniquely determined at its disjoint class coordinates outside the forced core.
Consequently the minimal recipient class set is exactly the set of B classes
intersecting the support of A outside B's forced core. The support of A is its
active class union, with the forced core included whenever an active class has
nonzero signed sum. The source-triple case is handled separately.

The implementation propagates these necessary classes to a fixed point over
all literal word transitions. It then independently checks

    original E <= selected frame <= maximal signed frame

at every address and selected A <= selected B at every actual transition.
The support shortcut is therefore not the sole containment certificate.
Every resulting word receives complete source/target support replay and full
arbitrary-dirty replay in both orientations.

Balanced added classes have tau_l = 0. Their columns contain no forced-core
component and L_beta = I - beta J leaves them unchanged. In particular an
ordinary terminal can add e_a - e_b with projector dd^T/2. Unbalanced classes
change the common-core coupling. Searching these classes separately exposes
which additions help the actual child-width profile, rather than assuming
that the maximal enlargement is always best.

The first completed h23 candidate, on the independently recovered 3,584-merge
joint word, selects balanced classes at original rank at least 12 and forced
core size one. It seeds 6,003 classes, propagates 2,760 recipient classes, and
retains 8,763 additional classes in total. Its physical role count remains
27,719 and its complete local rank mass remains 638,043. At the discovery
probe a = 4e-5, its measured local moment increment is 139.84303410752054,
compared with 139.86776997043881 for the previous full core-single enlargement
at threshold 18. Both numbers use beta23 = 1/15 and the same coherent
coordinate flag. They are discovery comparisons, not certified exponents.

Actual source, dirty-state, containment, and full bounded-minor native matrix
checks have passed for this candidate. Independent source-only regeneration,
complete scalar stock, full data-family binding, the exact recurrence moment,
all assembly constraints, and independent final acceptance are still separate
mandatory gates. No result in this note is an accepted conditional construction.

Reproduction uses `code/componentwise_signed_word_enlargement.py`, the portable
`enlarge_components` function, and the frozen configuration
`configs/joint-componentwise-20261008T201004.json`. Large full words, native
matrix audits, and execution logs are external regenerable artifacts. Their
paths and hashes are recorded per completed row. A scientific publication
must retain the selected compact result and archive its complete word and
matrix receipts under the repository's unsplit text-evidence rules.
