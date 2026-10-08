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
