Campaign closed at the user's request. Final accepted conditional κ=5.143624568e-5; see the [final handoff](../../reports/final-campaign-handoff.md). The checkpoint narrative below is historical.

# Executable graph and controller recovery

Requirements: Python 3.10 or later with the standard library, a C++17
compiler, GitHub CLI access to the pinned public input, and fresh external
storage. Run from the RaD repository root. No Python environment, external
binary DAG, native executable or old execution log is needed for the
selected recoveries below. Do not reuse an existing output directory.

Acquire the unchanged public producer and retain its notices:

```bash
GRAPH_OWN="$PWD/research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/graph"
GRAPH_RUN="/srv/ai/work/rad/integer-multiplication-bounds/reproduce-fast-gpu-graph"
PR36_ROOT="$GRAPH_RUN/repos/pr36"
PR36_REV="11817ccacb564bb7f98789c20dc11d3fece207e3"
mkdir -p "$GRAPH_RUN/inputs" "$PR36_ROOT"
gh api "repos/icekylinx/integer-mult-bounds/tarball/$PR36_REV" > "$GRAPH_RUN/inputs/pr36.tar.gz"
tar -xzf "$GRAPH_RUN/inputs/pr36.tar.gz" --strip-components=1 -C "$PR36_ROOT"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
```

The authored subclasses and C++ matchers contain all changes; the source
snapshot is not edited. The drivers build their own native executables,
recompute all scalar gates and backward-positive labels, replay the exact
retained chain edits, rerun the actual matching, and assert the recorded
DAG, label and selected-link digests and exact rank histograms.

Rebuild the six genuine h10 whole-chain clones and exercise all 2,049
source, target and dirty-role basis vectors in both orientations:

```bash
python3 "$GRAPH_OWN/code/rebuild_selected.py" \
  --source "$PR36_ROOT" --work "$GRAPH_RUN/whole-h10" \
  --parent "$GRAPH_OWN/fixtures/small-cloned-parent-10.json" \
  --selected "$GRAPH_OWN/fixtures/small-cloned-axis-10.json" --dirty
```

Rebuild the selected larger whole-chain refinements, with the full scalar,
rational-frame, physical-role, rank and reverse-complement audits:

```bash
for h in 23 25; do
  python3 "$GRAPH_OWN/code/rebuild_selected.py" \
    --source "$PR36_ROOT" --work "$GRAPH_RUN/refined-whole-$h" \
    --parent "$GRAPH_OWN/fixtures/refined-cloned-parent-$h.json" \
    --selected "$GRAPH_OWN/results/refined-cloned-axis-$h.json"
done
```

Rebuild the genuine five additional alternative-partition h10 producers:

```bash
python3 "$GRAPH_OWN/code/rebuild_alternative_selected.py" \
  --source "$PR36_ROOT" --work "$GRAPH_RUN/alternative-h10" \
  --base-parent "$GRAPH_OWN/fixtures/small-cloned-parent-10.json" \
  --whole-selected "$GRAPH_OWN/fixtures/small-cloned-axis-10.json" \
  --selected "$GRAPH_OWN/results/alternative-small-producer-clones.json" --dirty
```

Rebuild the complete selected h23/h25 lineage, including the new global
hierarchy, whole-chain clones and then alternative source partitions:

```bash
for h in 23 25; do
  python3 "$GRAPH_OWN/code/rebuild_alternative_selected.py" \
    --source "$PR36_ROOT" --work "$GRAPH_RUN/alternative-$h" \
    --base-parent "$GRAPH_OWN/fixtures/alternative-base-parent-$h.json" \
    --whole-selected "$GRAPH_OWN/fixtures/alternative-parent-clones-$h.json" \
    --selected "$GRAPH_OWN/results/alternative-axis-$h.json"
done
```

Expected positive-frame final roles are h10 R1804, h23 R36015 and h25
R47429. Every driver writes `rebuild-result.json` and preserves the derived
binary DAGs, literal frame arrays, coefficient partition/controller edits,
native selected links and independent audit. Recovery evidence lives in
`results/selected-recovery-h*.json` and
`results/alternative-selected-recovery-h*.json`; the report states exactly
which commands passed. The first alternative h10 attempt failed on a
one-row JSON wrapper and was preserved before the corrected fresh attempt.

Full exploratory searches are executable entry points in `code/`, using
`--source`, fresh `--work`, fresh `--output` and bounded `--workers`. Their
retained complete JSON evidence records the exact command, seeds,
configuration and native source hashes. The initial allocation was eight
slots, then ten, then seven (six allocation workers plus one audit slot)
after the coordinator reserved GPU host resources. Native children are
sequential within each worker slot; all numerical libraries use one thread.

The fixed ORIGINAL-envelope profiles and exact 47-inequality compositions
are separate [geometry](../geometry/) and coordinator artifacts. A new
positive-frame histogram cannot be inserted into that fixed-basis
interface. The eventual common bases, finite alphabets, setup, tape
interfaces and strict absorption remain conditional mathematical transfer
dependencies.

The best actual-positive negative-basis parents are a different selection
from the earlier minimum-role parents. Their complete source-only recovery
was exercised independently for both dimensions:

```bash
for h in 23 25; do
  python3 "$GRAPH_OWN/code/rebuild_alternative_selected.py" \
    --source "$PR36_ROOT" --work "$GRAPH_RUN/best-positive-negative-$h" \
    --base-parent "$GRAPH_OWN/fixtures/best-positive-negative-base-parent-$h.json" \
    --whole-selected "$GRAPH_OWN/fixtures/best-positive-negative-whole-clones-$h.json" \
    --selected "$GRAPH_OWN/fixtures/best-positive-negative-mapped-partitions-$h.json"
done
```

Expected roles are h23 R36,219 and h25 R47,461. The fixtures preserve each
coefficient partition, actual rewritten donor, consumed controller capacity,
chain edit, seed and terminal stage. Both runs assert exact DAG, positive
label, selected-link and histogram digests and run the independent literal
compiler. Receipts are `results/best-positive-negative-recovery-{23,25}.json`.
Geometry's later weighted/global controller maps are separately preserved
in its complete profile wrappers and source-only replay receipts. Replacing
the retained map requires a fresh literal audit of that actual map.

The versioned `check_permuted_compiled_witness.py` additionally binds every
primitive source and designated target to the recorded `old_to_new`
coordinate permutation. It retains the independently implemented physical
compiler, terminal checks and both dirty orientations. Its small complete
controls are reproducible after the earlier h10 alternative rebuild:

```bash
python3 "$GRAPH_OWN/code/audit_flag_controls.py" \
  --parent "$GRAPH_OWN/results/alternative-small-producer-clones.json" \
  --work "$GRAPH_RUN/flag-small-controls" \
  --output "$GRAPH_RUN/flag-small-controls.json"
```

If the historical paths inside that parent wrapper are unavailable, replace
its `producer` with the source-only h10 `rebuild-result.json` producer first;
the scalar DAG, frame and selected-use digests must agree. The two controls
exercise all 2,044 source, target and arbitrary dirty-role basis vectors over
F2 in both invocation orientations. They do not establish a corresponding
integer or odd-characteristic dirty word.

For a completed flagged candidate, `code/flag_permutation_search.py`
provides `transform(parent_wrapper, fresh_directory, order)`. Use the
recovered DAG/positive labels, the retained complete chosen controller map,
and the explicitly retained `global_coordinate_order` and `old_to_new`
arrays. Inverse byte normalization must reproduce the unpermuted DAG and
frame digests exactly. Then run:

```bash
python3 "$GRAPH_OWN/code/check_permuted_compiled_witness.py" \
  --witness "$GRAPH_RUN/flagged/input-witness.json" \
  --output "$GRAPH_RUN/flagged/literal-audit.json"
```

The actual negative-basis CRT profiler is authored under `../geometry/code/`.
Compile `positive_frame_profiles.cpp` with `c++ -O3 -std=c++17`, and run
`run_positive_profiles.py --help` for the retained wrapper interface. Both
flag search drivers perform that build and preserve the exact invocation,
source hashes, literal profile input, minor bounds and primes. A coordinate
flag changes internal ordered matrix profiles; its complete source-pair
family transfers by the reviewed coherent permutation lemma. Every scalar
mask, signed frame and both source/target endpoint labels must receive the
same permutation. The initial broad 606 orders are excluded from the 2,286
nearby transposition/window orders; these counts are coordinate flags on
two unchanged scalar graphs, not thousands of new scalar producer graphs.


## Independently implemented skip producer and selected clone recovery

The public skip-prefix identity is credited to Avi Eisenberg / ikeboy, with
Anthropic assistance, in CrocSwap PR53. The first implementation here used
that public mathematical description and pinned PR36; later user authorization
allowed inspection of public PR54, PR53 and PR51 implementation snapshots.
The selected R=32,669 / 42,974 graphs below are regenerated from PR36 and the
retained independently authored identity, rather than imported PR54 outputs.

Run from the RaD repository root. `C` is this campaign and `G` its graph branch;
`PR36` is an immutable unpacked source snapshot at the indicated public commit.
All writable paths below must be fresh external directories.

```bash
C=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008
G=$C/agents/graph
PR36=/path/to/immutable/pr36-11817ccacb564bb7f98789c20dc11d3fece207e3
REPLAY=/path/to/fresh/external/skip-recovery
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
python3 "$G/code/rebuild_skip_selected.py" --source "$PR36" \
  --work "$REPLAY/h23" --parent "$G/fixtures/skip-selected-parent-23.json" \
  --selected "$G/results/skip-cloned-axis-23.json" \
  --skip-driver "$C/code/independent_skip_search.py" --dirty
python3 "$G/code/rebuild_skip_selected.py" --source "$PR36" \
  --work "$REPLAY/h25" --parent "$G/fixtures/skip-selected-parent-25.json" \
  --selected "$G/results/skip-fixed-selected-axis-25.json" \
  --skip-driver "$C/code/independent_skip_search.py" --dirty
```

If the input snapshot is unavailable, acquire the exact public source with
`gh api repos/icekylinx/integer-mult-bounds/tarball/11817ccacb564bb7f98789c20dc11d3fece207e3`
and unpack it outside Git. Retain its Apache-2.0 license and existing author
notices. The driver compiles three retained/pinned native matchers in its own
external build directory, rebuilds the frozen parent, checks its DAG/frame/map
hashes, reproduces every selected whole-carrier-chain edit, rematches, and
checks all final hashes and the exact histogram. It then independently verifies
scalar coefficients, rational frame containment, the physical chronology,
copied-center terminal uses, and the complete F2 payload basis in both dirty
orientations. No old derived DAG or executable is consumed.

This complete path was exercised on both actual selected dimensions on
2026-10-08: h23 had 264+36 paid copies and 36,211 total basis vectors; h25 had
368+67 paid copies and 47,574 basis vectors. See
`results/skip-source-only-recovery-23.json` and
`results/skip-fixed-source-only-recovery-25.json`. The earlier wide-l8 h25
role tie has a separate successful recovery; its DAG is not substituted for
the fixed-profile scarce-l4 winner. Matrix profiles and
conditional composition are separate geometry/coordinator checks; a dirty
PASS does not itself prove the asymptotic conditional theorem.

## Public PR54 reference replay

Acquire the authorized public source with
`gh api repos/CrocSwap/integer-mult-bounds/tarball/84eb0b067741dc2690da837743fda06d133da865`
and unpack into another immutable external directory. Never compile or write
Python bytecode there. Then run:

```bash
python3 "$G/code/rebuild_public_pr54.py" --source /path/to/immutable/pr54 \
  --work /path/to/fresh/external/public54-replay \
  --output /path/to/fresh/external/public54-replay.json
```

This pinned reference path was fully exercised: all 606 paid clone edits, both
literal selected-use maps, exact scalar ledgers, R=32,693 / 43,056 and
W=159,592,676, with complete dirty basis checks in both orientations.
`results/public-pr54-rebuild-1710.json` retains the receipt. The public fixed
matrix and exact composition checks are owned separately by geometry/root.


## Public PR54 followed by task-owned whole-chain copies

The following source-only path preserves every pinned original frame and
replays each retained new paid whole-carrier-chain copy. All matchers compile
into the fresh external output directory. No old DAG, frame labels, matching
file or executable is consumed.

```bash
PR54=/path/to/immutable/pr54-84eb0b067741dc2690da837743fda06d133da865
NEW_REPLAY=/path/to/fresh/external/public54-enlarged-replay
python3 "$G/code/rebuild_public_enlarged.py" --source "$PR54" \
  --work "$NEW_REPLAY/h23" --parent "$G/results/public-pr54-original-axis-23.json" \
  --selected "$G/results/public54-enlarged-axis-23.json"
python3 "$G/code/rebuild_public_enlarged.py" --source "$PR54" \
  --work "$NEW_REPLAY/h25" --parent "$G/results/public-pr54-original-axis-25.json" \
  --selected "$G/results/public54-enlarged-axis-25.json"
```

Both complete actual-dimension paths were exercised on2026-10-08. They add333
and395 task-owned paid copies after the pinned253/353 upstream copies and
produce R32,360/42,661, with35,902/47,261 complete payload basis vectors
checked in both dirty orientations. The fresh DAG/frame/map byte hashes
match these precise retained wrappers. H25 uses the wide-l8 clone policy;
a different scarce-l4 graph has the same role count and a different matrix
profile and must be separately recovered if selected. Receipts:
`results/public54-enlarged-source-only-recovery-23.json` and `-25.json`.
The graph source remains public upstream work; the later first-consumer-frame
copy mechanism and its independent checks are task-owned contributions.
