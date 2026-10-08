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
