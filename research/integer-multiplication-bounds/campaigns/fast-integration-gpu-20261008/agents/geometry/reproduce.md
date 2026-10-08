Campaign closed at the user's request. Final accepted conditional κ=5.143624568e-5; see the [final handoff](../../reports/final-campaign-handoff.md). The checkpoint narrative below is historical.

# Geometry branch recovery

Run from the repository root on a little-endian host with Python3.14, a GCC or Clang C++17 compiler supporting unsigned128-bit integers, and Boost multiprecision headers. Promoted fixed/negative witnesses need no NumPy environment. The flag and boundary discovery scripts additionally use the recorded NumPy2.5.3 environment. Keep execution outside Git and set all BLAS/OpenMP thread variables to one. The worker count is a TOTAL native CPU allocation, not a per-task multiplier.

Recover the selected scalar DAG using [the graph branch](../graph/reproduce.md) and its retained parent/clone configurations. Choose the actual DAG whose SHA256 matches the selected axis wrapper; do not substitute a positive carrier matching or its R. Complete selected maps are retained in the wrapper or its complete gzip evidence copy. The geometry recovery driver accepts either form.

```bash
GEOMETRY=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/geometry
WORK=/path/to/fresh/external/recovery
python3 "$GEOMETRY/code/reproduce_selected_axis.py" \
  --dag /path/to/recovered/dag.bin \
  --expected "$GEOMETRY/results/best-negative-original-axis-23.json" \
  --work "$WORK"
```

Use the size25 wrapper for the other axis. For fixed I+J select `best-fixed-original-axis-23.json` or25. The driver compiles the retained native source from scratch, freshly derives ORIGINAL E(C,M) ranks and maximum matching, applies the recorded actual matrix-moment ordering/exchanges, recomputes every physical local profile with the appropriate fresh CRT bounds, compares every selected use and every histogram entry, creates independent integer envelope labels, and runs both independent scalar/frame and literal original compiler checks. No machine-local executable or foreign modified checkout is used. Four complete recovery runs were exercised: the first selected fixed axes and the best negative axes at both sizes, including fresh compilation and literal compiler review; receipts are in `results/recovery-*.json`.

To recover the negative data certificate, compile `code/negative_basis_classify_pairs.cpp` and run it into a fresh external JSON file. This enumerates the entire4073300-pair Cartesian family and replays whole pairs at alternate primes. Compile and run `code/fixed23_negative25_data_pairs.cpp` for the complete mixed certificate. Never combine prefixes from different primes into one nonvanishing replay.

The both-negative classification's `failures` records contain the exact192596 exceptions. Run `python3 code/build_negative_fixture.py --classification /path/to/classification.json --output /path/to/exceptions.bin` from this worker directory. It checks unique lexical indices and creates the complete fixture. Compile `code/negative_exception_rank_union.cpp` using `c++ -O3 -std=c++17`. Run four disjoint parts, or choose a lower total worker count:

```bash
negative_exception_rank_union /path/to/exceptions.bin 0 4 > /path/to/part0.json
negative_exception_rank_union /path/to/exceptions.bin 1 4 > /path/to/part1.json
negative_exception_rank_union /path/to/exceptions.bin 2 4 > /path/to/part2.json
negative_exception_rank_union /path/to/exceptions.bin 3 4 > /path/to/part3.json
```

Each part must report48149 exact pairs and1011129 field replays. Sum profile counts to192596. Add3880704 regular null profiles (nine singletons plus21,17) and add4073300 central481 blocks. The one-front rank mass must be4073300*528. The two-front distribution doubles the one-front counts. Compare with `results/both-negative-data-histogram.json`. The proof for this procedure is [negative-basis-proof.md](negative-basis-proof.md). The failed uniform19-profile checker is retained as a negative; it is not the certificate used for promotion.

The portable commands above reconstruct changed finite components. The coordinator's exact recurrence, bulk stock, correction calls, scalar bounds and all47 assembly inequalities are separate scripts and certificates. This branch does not claim that local profile recovery alone proves an infinite multiplication theorem.

## Actual signed positive frames

Later DAGs use their literal enlarged signed frames. Recover the exact DAG, `.positive` labels, and selected map using the sibling graph driver, then use this gate; an equal role count is insufficient to identify the fixture.

```bash
python3 "$GEOMETRY/code/reproduce_positive_profile.py" \
  --dag /path/to/fresh/dag.bin \
  --selected /path/to/fresh/selected-uses.json \
  --expected "$GEOMETRY/results/best-public54-mapped-weighted-negative-axis-25.json" \
  --source-receipt /path/to/fresh/graph-source-receipt.json \
  --work "$WORK/positive-profile" --output "$WORK/positive-profile-receipt.json"
```

This freshly compiles the exact profiled source, compares all actual frame and map digests, profiles every physical transition, and invokes the independent literal compiler. For source receipts with a separate `weighted_selected` field, that field's producer and selected map must be used for its explicitly named fixture. A different field with the same scalar DAG or role count is not a substitute. Tested full source-only matrix/chronology recoveries include the selected enlarged skip axes, both public54-enlarged axes, fixed mapped h23, and negative mapped h25. Failed equal-role and wrong map-field attempts remain recorded.

## PR62/PR57 executed joint words

The authorized PR62 head contains the unmodified joint words and the PR57 compiler helpers. Obtain it through GitHub CLI into a fresh external directory. The PR57 reference head is `cd350f76c9bc01489ec83568bded532cb69be938`; the used helpers are present in the pinned PR62 archive. The campaign acquisition manifest and this branch's input manifest retain source hashes.

```bash
TASK_WORK=/path/to/fresh/external/joint-word-recovery
mkdir -p "$TASK_WORK/source"
gh api repos/ikeboy/integer-mult-bounds/tarball/ad0f25ff7b23cff7f08ad237c2254e6ecf74257e \
  > "$TASK_WORK/pr62.tar.gz"
tar -xf "$TASK_WORK/pr62.tar.gz" --strip-components=1 -C "$TASK_WORK/source"
c++ -O3 -std=c++17 "$GEOMETRY/code/joint_word_conjugate_profiles.cpp" \
  -o "$TASK_WORK/joint-word-profiler"
python3 "$GEOMETRY/code/profile_joint_word.py" \
  --source "$TASK_WORK/source" --h 23 --binary "$TASK_WORK/joint-word-profiler" \
  --work "$TASK_WORK/h23" --output "$TASK_WORK/h23-receipt.json"
python3 "$GEOMETRY/code/profile_joint_word.py" \
  --source "$TASK_WORK/source" --h 25 --binary "$TASK_WORK/joint-word-profiler" \
  --work "$TASK_WORK/h25" --output "$TASK_WORK/h25-receipt.json"
```

This extraction reconstructs the positive transition multiset from the actual XOR word, compares it to the compiler event chronology and pinned public receipt, then freshly profiles fixed I+J, its conjugate, and all rank-two transitions in both bases. All four histograms were identical for each unmodified axis. The words' copied-center births, terminal charges and cleanup are already represented; do not apply an older per-DAG copied-center adjustment to these profiles.

The generic rational-basis profiler uses exact integer denominators and full bounded-minor CRT. For example, the unchanged size25 word in the negative basis is recovered by:

```bash
c++ -O3 -std=c++17 "$GEOMETRY/code/parameter_joint_word_profiles.cpp" \
  -o "$TASK_WORK/parameter-word-profiler"
"$TASK_WORK/parameter-word-profiler" "$TASK_WORK/h25/transitions.bin" \
  beta:1:21 "$TASK_WORK/negative25-profile.json" "$TASK_WORK/negative25-transition-audit.json"
```

The complete fourteen parameter configurations are retained inside `results/joint-word-parameters-20261008T1820-part{0,1,2}.json`. Extract each `rows[].config`, replace its binary path with the freshly regenerated axis binary, and run `code/run_joint_word_parameters.py --input CONFIG.json --binary FRESH_BINARY --work FRESH_WORK --output RECEIPT.json`. The actual per-transition rank bound follows the nested nondegenerate frame proof in [joint-word-basis-review.md](joint-word-basis-review.md), rather than a numerical rank guess.

Independent direct rational controls use `code/review_joint_word_profiles.py`. Its input is a list of `{case_id,binary,basis,audit}` objects, with `binary` the word-derived transition file and `audit` the fresh native transition audit. Sixteen distinct controls per basis were exercised, for 224 controls across the fourteen profiles; every Gram, nesting, idempotence, exact denominator, integer minor bound and rational ordered-pivot comparison passed. This does not replace the independent full literal word/dirty replay performed by the graph branch.

The coherent-flag discovery driver `code/search_joint_word_flags.py` accepts `{case_id,transitions,order}` rows. `order[i]` is the new position of old coordinate `i`. Every frame is transformed by the same coordinate permutation, and the inverse mask transform is checked. It does not synthesize a new scalar DAG. Acceptance additionally requires coherent source-triple keys and output/common labels in a fresh literal word, the complete source-family bijection, and exact full recurrence. A local width improvement alone does not close these gates.

The commands for the two unmodified words, all fourteen parameter profiles, and the 224 direct rational controls were exercised from the immutable source snapshot and freshly built native code. The archive acquisition itself was performed by the coordinator through the pinned GitHub source; the mathematical replay does not depend on an old executable or modified dependency checkout.
