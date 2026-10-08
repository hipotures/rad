# A small runnable changed-producer search

The coordinator requested an eligible existing producer that allows a change
of the computation DAG, rather than another matching replay on the unchanged
large graph. The pinned PR40 source already exposes the needed hooks:
`partial_swap/paired.py` has `base_threshold` and `grouping(points)`, and
`partial_swap/shared.py` accepts the local producer and global point order.
Its exact provenance is the eligible science commit
`43f59ff533598762cbc43a5e14af2bbbc76fabbd` in
`rohanarun/integer-mult-bounds`, downloaded at campaign intake. Newly
campaign-linked public producer branches are excluded and were not used.

[changed_dag_seed.py](code/changed_dag_seed.py) is an authored wrapper around
those pinned interfaces. It changes the top recursion partition into adjacent
pairs and singletons and the association of disjoint sums. Associations are
the upstream balanced tree, a left chain, a right chain, or deterministic
small-support-first merging. These preserve the coefficient map but can
change the equal sums shared across common-point circuits, the number of
roles and all child widths. Each circuit gets exact support and reversible
frame checks before any counts are interpreted. Retained common-point totals
and the original global aligned point order remain part of this starting
family.

Groups must have size at most two. The upstream formula for two omitted points
within one group is `out[a,b]=outside[group]`. It is correct for a pair and
does not account for remaining within-group terms in a ternary group. The
launcher enforces singleton/pair groups and strictly decreasing recursion;
naively replacing grouping by triples would invalidate the construction.

The scout's brief exact controls generated 12 distinct DAG hashes at
`h=6,7,8`, with two top partitions and two associations per dimension.
Every output support and forward/reverse frame inclusion passed. At `h=6`,
changing partition `221` to `212` reduced pre-matching scalar roles from
195 to 194. At `h=8`, `2221` to `2212` reduced 824 to 819 under balanced
association. These are useful small search seeds, not an exponent result.
The complete denominator and recursive width profile may reverse a favorable
scalar-role comparison. Full counts and input/source hashes are retained in
[changed-dag-seed.json](changed-dag-seed.json); binary DAGs live in ignored
execution storage and are deterministically regenerable.

Run from the repository root, replacing the fresh output path for each attempt:

```sh
SCOUT_CAMPAIGN=research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008
SCOUT_SOURCE=$SCOUT_CAMPAIGN/work/scout/snapshots/pr40-43f59ff53359
python3 -B "$SCOUT_CAMPAIGN/agents/scout/code/changed_dag_seed.py" \
  --source-root "$SCOUT_SOURCE" \
  --output "$SCOUT_CAMPAIGN/work/scout/fresh-changed-dag-control" \
  --dimensions 6 7 8 --max-patterns 2 --export-dags
```

The smaller control takes approximately 0.05 seconds of one Python worker.
For a root-owned search, dimensions `10 12 14 16`, up to 16 patterns, and all
four associations are a bounded initial expansion. Each dimension can be
assigned to one of the coordinator's allocated workers.

The launcher also supports `--matcher-directory <directory>` containing
precompiled pinned `match_exported_dag` and `match_positive_dag`. Compile them
once into the task's ignored build directory:

```sh
SCOUT_MATCHERS=$SCOUT_CAMPAIGN/work/scout/fresh-matcher-build
mkdir -p "$SCOUT_MATCHERS"
c++ -O3 -std=c++17 "$SCOUT_SOURCE/scripts/partial_swap/match_exported_dag.cpp" \
  -o "$SCOUT_MATCHERS/match_exported_dag"
c++ -O3 -std=c++17 "$SCOUT_SOURCE/scripts/partial_swap/match_positive_dag.cpp" \
  -o "$SCOUT_MATCHERS/match_positive_dag"
```

For each distinct candidate it then exports the `.bin` DAG, runs the first
matcher to create `.links`, propagates positive labels through the pinned
`positive.run`, and runs the second matcher with the `.positive` labels.
Both complete generic histograms, matching counts, loss, role denominator
and exact rank identity are saved in `results.json`. Matcher diagnostics
remain in separate ignored files. The original profile is included so an
unsupported positive-label case can be diagnosed rather than confused with
a valid moment improvement. The scout exercised the support/frame path;
the coordinator owns the compute allocation and matcher execution.

A finalist still needs the complete copied-center adjustment, exterior and
data profiles, changed denominator, and the eligible reference's fixed
`I+J` basis check. Generic small-producer statistics do not establish those
obligations or a new multiplication bound.
