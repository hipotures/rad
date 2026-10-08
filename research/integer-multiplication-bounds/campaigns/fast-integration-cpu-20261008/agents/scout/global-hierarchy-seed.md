# Independent global hierarchy producer seed

At approximately 15:29 UTC, [global_hierarchy_seed.py](code/global_hierarchy_seed.py) tested an independent support-interning construction with a different local pair hierarchy for each common point. It preserves global adjacent pairs under deletion of that point; a broken pair becomes a singleton at its original location, and deleting an odd final singleton leaves an empty coarse vertex. This changes the computation DAG rather than only relabeling the old circuit.

The code imports only the eligible PR40 pair recursion and generic reversible compiler at `43f59ff533598762cbc43a5e14af2bbbc76fabbd`. It independently constructs dense global supports, interns equal supports exactly, and verifies all sums, output supports and forward/reverse frame inclusions. Its independent baseline agrees with the pinned producer's addition, output and role counts.

The bounded run tested dimensions 6, 7, 8 and 10, eight producer cases in 0.064 seconds. Relative scalar role changes were respectively `-2`, `+6`, `+4`, `+16`. There is no favorable general trend from these controls. Matching, complete fixed I+J moments and physical geometry were not evaluated, so no multiplication improvement follows from the h6 scalar reduction.

[global-hierarchy-seed.json](global-hierarchy-seed.json) retains the protocol, source hashes, exact per-case controls and summary. The binary DAGs are ignored execution payloads and are deterministically regenerable. This dense seed is deliberately bounded to dimensions at most 20; it is not an efficient large-graph producer.

From the campaign directory:

```bash
python3 -B agents/scout/code/global_hierarchy_seed.py \
  --source-root work/scout/snapshots/pr40-43f59ff53359 \
  --output work/scout/<fresh-run> --dimensions 6 7 8 10 --export-dags
```

Any further investigation should first test a complete fixed-profile moment on a genuinely changed small graph, rather than infer a saving from scalar roles.
