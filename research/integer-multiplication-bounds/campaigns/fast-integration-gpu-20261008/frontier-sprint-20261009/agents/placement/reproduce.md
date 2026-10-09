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

## Recover the current complete fused168 winner

The current producer and coherent alias state are new inputs, not PR161 frame
substitutions. Use Python 3.11 or later for the signed producer; this lane tested
Python 3.14.4. There are no third-party Python dependencies or GPU requirements.
The source acquisition pins are PR168
`98c115b53742b6613ad630de4d493f37b0119da7` in the eumemic fork and PR165
`7518fed2688baf25c7c32bae32674f3334b517da` in the chafreaky fork. Acquire each
immutable source with `gh api repos/<fork>/integer-mult-bounds/tarball/<commit>`
into a fresh work location. The PR165 `make_plan.py` dependency is pinned to
`29a4548855513bb51b08c4cfe10a3ce717fdb837d24769c16f5b71a7b7a681dc`.

The complete producer and signed alias reconstruction commands are in
[the signed lane's reproduction note](../signed/reports/reproduce-pr165-pr168.md).
Its four-variant `screen_pr168_modules.py` constructs the actual full-fusion word.
The `complete_fusion/` outputs become the expected-format fusion input using the
exact map in that note. The following downstream steps were executed; replace
every output with a fresh directory when reproducing.

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
placement_source=work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b
placement_input=work/signed/pr168-fusion-export-20261009T0848Z
placement_run=work/placement/reproduction-fused168-fresh

python3 -B agents/placement/code/prepare_context.py \
  --source "$placement_source" --input "$placement_input" \
  --source-commit 98c115b53742b6613ad630de4d493f37b0119da7 \
  --source-repository https://github.com/eumemic/integer-mult-bounds \
  --output "$placement_run/fusion-context"
python3 -B agents/placement/code/physical_exchanges.py \
  --source "$placement_run/fusion-context/source" \
  --export "$placement_run/fusion-context/export" \
  --policy components --order alternating --passes 6 \
  --trial 0.000617042388 --output "$placement_run/components"
python3 -B agents/placement/code/physical_closure.py \
  --source "$placement_run/fusion-context/source" \
  --export "$placement_run/fusion-context/export" \
  --context "$placement_run/fusion-context/context.json" \
  --start-frames "$placement_run/components/frames.json" \
  --direction lower --seed 20261009 --seed-limit 8000 --max-nodes 256 \
  --passes 2 --trial 617042388/1000000000000 \
  --output "$placement_run/global-lower"
```

Expected component frames SHA-256 is `defa54c2911e21d511c3144e0a798d732f638431f8a8c8a1ef594eb8ced67a81`;
expected global-lower frames SHA-256 is
`908faafb23a65a892f90a9b08a2b5814eb90a8b4998059a53199298e534771a3`.
Run the signed lane's `continue_fused_pairs.py` with this global-lower initial
frame list, the same fusion input, `--workers 4 --rounds 4 --passes 30` and the
historical `--trial-saving 617042388/1000000000000`. Preserve the complete
`seed31/` frames, pairs and profile together; its expected frame SHA-256 is
`9552ac025438c5f90ce95423a52dee84d039a3dfc0ebceee31633f8a64113dfc`.

```bash
placement_joint=work/signed/fusion-joint-global-20261009T0904Z/seed31
python3 -B agents/placement/code/prepare_alias_context.py \
  --base-input "$placement_input" --continuation "$placement_joint" \
  --output "$placement_run/joint-input"
python3 -B agents/placement/code/prepare_context.py \
  --source "$placement_source" --input "$placement_run/joint-input" \
  --source-commit 98c115b53742b6613ad630de4d493f37b0119da7 \
  --source-repository https://github.com/eumemic/integer-mult-bounds \
  --output "$placement_run/joint-context"
python3 -B agents/placement/code/physical_closure.py \
  --source "$placement_run/joint-context/source" \
  --export "$placement_run/joint-context/export" \
  --context "$placement_run/joint-context/context.json" \
  --start-frames "$placement_run/joint-input/physical-frames.json" \
  --direction raise --seed 20261009 --seed-limit 33568 --max-nodes 256 \
  --passes 3 --trial 617560360/1000000000000 \
  --output "$placement_run/global-raise"
python3 -B agents/placement/code/freeze_frame_candidate.py \
  --base-input "$placement_run/joint-input" \
  --candidate "$placement_run/global-raise" --output "$placement_run/frozen"
```

Expected final frames SHA-256 is
`594f2c56d91d7353254f4087de4d4cf409ad6e8815f2ab6f8c274eeccd07681d`;
physical pairs SHA-256 is
`d082e9dff59a93dbdf9d56195bc542f9d4177efeb934bce7a059cd82c839e515`.
The compact outcomes and exact configurations of all 16 downstream attempts are
in `results/pr168-placement.json` and `configs/pr168-placement-protocol.json`.
The latter identifies one earlier maximum-pass cap absent from the original
result, and uses a sufficient deterministic reproduction cap without claiming
it is the original historical value.

## Exact byte recovery without repeating discovery

The entire frozen eight-input bundle is preserved in the current evidence
archive, not only its histogram. From this sprint directory:

```bash
python3 -B - <<'PY'
import gzip, hashlib, json
from pathlib import Path
archive = Path('agents/placement/evidence/pr168-placement-20261009T092200Z/fused168-joint-raise-frozen-20261009T0937Z')
recovered = Path('work/placement/recovered-fused168-fresh')
recovered.mkdir(parents=True, exist_ok=False)
names = ['graph.json', 'baseline.json', 'frames.json', 'word.json',
         'profile-before.json', 'physical-frames.json', 'physical-pairs.json',
         'profile.json', 'protocol.json']
for name in names:
    data = gzip.decompress((archive / (name + '.gz')).read_bytes())
    (recovered / name).write_bytes(data)
protocol = json.loads((recovered / 'protocol.json').read_text())
for name, pin in protocol['input_pins'].items():
    data = (recovered / name).read_bytes()
    if len(data) != pin['bytes'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
        raise ValueError('Recovered input differs: ' + name)
print('All eight coherent inputs recovered and pin checked.')
PY
```

This recovery path was exercised on the full frozen bundle. The archive checker
also verifies every current original SHA-256, gzip CRC/framing, UTF-8 and namespace
membership. For independent finite/moment checks, use the recovered expected
schema with the separate signed and geometry entry points. The accepted native
root bracket is `(617664283/10^12,617664284/10^12)`; final assembly must use its
own accepted ordinary supplier, parameters and all constraints. Never install
only these frames over the unchanged public PR168 word: its scalar producer,
closure, gauges and aliases differ from this candidate.
# Fresh 91f6a05 and fd25adb literal-sink batches

These are separate source-specific continuations. Their 13 exact final plans,
complete histograms and raw-result hashes are recorded in
`configs/pr168-91fd-sink-protocol.json` and
`results/pr168-91fd-sink-placement.json`. Use a fresh output ID throughout each
chain; all scientific attempt scripts reject an existing output. No GPU or pip
dependency is required. Python 3.14.4 was exercised; the signed producer minimum
is Python 3.11. Set `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
`NUMEXPR_NUM_THREADS` and `PYTHONDONTWRITEBYTECODE` to `1`; run without `-O`.

Run these commands from the sprint directory. Source checkouts are disposable
dependencies outside the durable repository:

```bash
PLACEMENT_DEP_ROOT=/srv/ai/work/rad/integer-multiplication-bounds/placement-91fd-reproduce
mkdir -p "$PLACEMENT_DEP_ROOT"
gh repo clone eumemic/integer-mult-bounds "$PLACEMENT_DEP_ROOT/pr168-91" -- --filter=blob:none
git -C "$PLACEMENT_DEP_ROOT/pr168-91" checkout --detach 91f6a059f44fb0513639d5185bde2a38973e99ca
gh repo clone eumemic/integer-mult-bounds "$PLACEMENT_DEP_ROOT/pr168-fd" -- --filter=blob:none
git -C "$PLACEMENT_DEP_ROOT/pr168-fd" checkout --detach fd25adb7fbaa12ee761d02c733c54d1d2a7687ee
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 -B agents/signed/code/regenerate_pr168_91f6a05_control.py \
  --source "$PLACEMENT_DEP_ROOT/pr168-91" \
  --source-head 91f6a059f44fb0513639d5185bde2a38973e99ca \
  --output-dir work/placement/reproduce-91-input
python3 -B agents/signed/code/regenerate_frontier_complex.py \
  --source "$PLACEMENT_DEP_ROOT/pr168-fd" \
  --source-head fd25adb7fbaa12ee761d02c733c54d1d2a7687ee \
  --output-dir work/placement/reproduce-fd-body-input
python3 -B agents/signed/code/export_terminal_sinks.py \
  --source "$PLACEMENT_DEP_ROOT/pr168-fd" \
  --body-export work/placement/reproduce-fd-body-input \
  --output work/placement/reproduce-fd-sink-input
python3 -B agents/placement/code/prepare_context.py \
  --source "$PLACEMENT_DEP_ROOT/pr168-91" \
  --input work/placement/reproduce-91-input \
  --output work/placement/reproduce-91-context \
  --source-commit 91f6a059f44fb0513639d5185bde2a38973e99ca \
  --source-repository https://github.com/eumemic/integer-mult-bounds
python3 -B agents/placement/code/prepare_context.py \
  --source "$PLACEMENT_DEP_ROOT/pr168-fd" \
  --input work/placement/reproduce-fd-body-input \
  --output work/placement/reproduce-fd-context \
  --source-commit fd25adb7fbaa12ee761d02c733c54d1d2a7687ee \
  --source-repository https://github.com/eumemic/integer-mult-bounds
```

Verify each source checkout's full `git rev-parse HEAD` before regeneration.
The source and generated-file hashes are in `input-manifest.json`; the context
helper verifies every decoded producer pin. Retain each dependency's original
Apache-2.0 license and notices. New placement/sink method attribution is in
`NOTICE`. The large literal event export is regenerable with the pinned source
gate and signed driver and is separately archived by the signed lane.

The protocol lists each placement argv in execution order. Substitute the new
context and input paths consistently, along with the corresponding fresh
source gate path. The fd endpoint batch uses `physical_sinks.py`. Its strongest
global raise is the starting frame file for the control/raise/lower/mixed
`physical_sink_elementary.py` batch. The lower row is the chosen final plan.
Freeze it with `freeze_sink_candidate.py`, using the newly reconstructed body
and sink input directories together; its `profile.json` remains the body
profile and `sink-profile.json` is the actual final complete profile.

For exact recovery of the retained winner, a source search rerun is unnecessary.
The following whole-gzip path was exercised for all ten chosen inputs and the
protocol; every original hash and size matched:

```python
import gzip, hashlib, json
from pathlib import Path

archive = Path("agents/placement/evidence/pr168-91fd-sinks-20261009T1024Z")
name = "pr168-fd25adb-sink-winner-frozen-20261009T1014Z"
out = Path("work/placement/recovered-fd-winner-new-id")
out.mkdir(exist_ok=False)
protocol_bytes = gzip.decompress((archive / name / "protocol.json.gz").read_bytes())
protocol = json.loads(protocol_bytes)
for filename, pin in protocol["input_pins"].items():
    data = gzip.decompress((archive / name / (filename + ".gz")).read_bytes())
    if len(data) != pin["bytes"] or hashlib.sha256(data).hexdigest() != pin["sha256"]:
        raise ValueError("chosen input recovery mismatch: " + filename)
    (out / filename).write_bytes(data)
(out / "protocol.json").write_bytes(protocol_bytes)
```

Archive framing, CRC, UTF-8, credentials, complete membership and current
originals were verified with
`python3 tools/archive_workspace.py verify-text --destination <this-namespace> --check-originals`
from the RaD root. The byte-recovery receipt is
`results/pr168-91fd-sink-byte-recovery.json`. Two scoped negative checks rejected
`-O` and a changed source head before candidate creation. All 13 positive
source-specific commands and full native recounters were exercised. This batch
did not repeat GitHub dependency reacquisition or independent exact operator,
rational moment and all-size assembly gates for the clearly losing new plan.
