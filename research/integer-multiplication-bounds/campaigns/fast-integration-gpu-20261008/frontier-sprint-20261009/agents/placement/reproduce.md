# Reproduce the moment-aware placement construction

Run from this sprint directory. Prerequisites are Python 3, Bash, tar, and an
authenticated GitHub CLI for source acquisition. Python uses only the standard
library. Use a fresh output directory for every attempt; the scripts reject
existing output files/directories. All paths below are relative to the sprint.

## Pinned source and producer

The coordinator's existing immutable source is `work/repos/pr161-d14e291` and
the regenerated producer export is `work/baseline/pr161-complex-export`. To
recover without either local directory:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
placement_run=work/placement/reproduction-fresh
mkdir -p "$placement_run/source"
gh api repos/eumemic/integer-mult-bounds/tarball/d14e29157bc905be1ced0776dd893d0714013f3a > "$placement_run/source.tar.gz"
tar -xzf "$placement_run/source.tar.gz" --strip-components=1 -C "$placement_run/source"
python3 -B "$placement_run/source/scripts/paired_cube_producer.py" \
  --work-dir "$placement_run/export" --output "$placement_run/producer-receipt.json"
```

Check the retained source and export SHA-256 values against
`input-manifest.json`. These are identities of the decompressed source/export,
not a promise of byte-identical GitHub tarball packaging. The source is a pinned
downloaded snapshot; running `git rev-parse` in it can report the enclosing RaD
checkout rather than the dependency revision.

## Replay the frozen explicit frames

```bash
python3 -B agents/placement/code/replay_frames.py \
  --source "$placement_run/source" --export "$placement_run/export" \
  --frames agents/placement/fixtures/pr161-components-converged-frames.json \
  --output "$placement_run/frozen-replay.json"
```

Expected: 12,827 frame entries relative to the producer's original backward
intersections; 6,030 operation frames differ from the PR161 public physical
frames. The complete profile has `m=66`, `W_per_vertex=15681`,
`rank_per_vertex=1033626`, deficit `1320`, and maximum child `20`. The inherited
physical checker tests exact binary subspace nesting and pair/read chronology,
then arbitrary dirty scalar replay at two seeds modulo `2^61-1` and three
negative controls. This command is not the independent signed/reflected audit
or a rigorous moment/assembly certificate. It explicitly rejects Python `-O`.

## Regenerate the placement choice

```bash
python3 -B agents/placement/code/physical_search.py \
  --source "$placement_run/source" --export "$placement_run/export" \
  --variant components --passes 6 --seed 20261009 \
  --output "$placement_run/component-search"
```

The last pass accepts no move. Expected raw `frames.json` SHA-256:
`f02a59311c667316b1f2e21916cebf71c58f79fbfbd3a126a24743d1d7ff016a`.
The source fixture wraps this list as `{"frames": [...]}` and has SHA-256
`3dc05748386e9dd5a9eadb227e40c9de2a21aa1e95e90d4bae479951713d1652`.
The fixture is directly usable as upstream
`references/paired-cube/physical/frames.json` in an isolated writable candidate
tree. Do not copy it onto the immutable downloaded reference.

For upstream integration in a separate candidate tree, replace only that frame
reference with the fixture, run `python3 -B scripts/paired_cube_physical.py
--write` to regenerate the complete physical input, and rebuild the complete
network certificate with the assembly lane's accepted parameters. A changed
histogram alone is insufficient; include independent geometry/sign/dirty audits
and all 47 constraints and seven margins.

## Continue distinct discovery runs

```bash
python3 -B agents/placement/code/physical_exchanges.py \
  --source "$placement_run/source" --export "$placement_run/export" \
  --start-frames "$placement_run/component-search/frames.json" \
  --policy op-pairs --passes 6 --output "$placement_run/op-pairs"
python3 -B agents/placement/code/physical_exchanges.py \
  --source "$placement_run/source" --export "$placement_run/export" \
  --start-frames "$placement_run/op-pairs/frames.json" \
  --policy components --passes 6 --output "$placement_run/op-pairs-polished"
```

These are different candidate identities and are not substitutions for the
frozen certification run. Every completed variant's retained configuration,
reproduction arguments and output frame hashes are recorded in
`configs/batch-protocol.json`; that file marks missing original maximum-pass
caps rather than reconstructing them as historical facts. No search in this lane
claims global placement optimality or a new all-size transfer theorem.
