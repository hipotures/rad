# Reproduce the fresh PR165/PR168 complex evidence

Run from the sprint root with Python 3.11 or later and assertions enabled.
No third-party Python package or GPU is required. Source snapshots are
recoverable GitHub archives at the full commit hashes given in the report
and coordinator's `agents/frontier/pr165-archive-manifest.json` and
`pr168-archive-manifest.json`. Acquire them with GitHub CLI, preserve their
original bytes, and set the two source-path arguments below to the exported
roots. A fresh output path is mandatory for each command.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 agents/signed/code/export_pr165_inputs.py \
  --source work/frontier/pr165-7518fed/extracted/chafreaky-integer-mult-bounds-7518fed \
  --output work/signed/reproduce-pr165

PYTHONDONTWRITEBYTECODE=1 python3 agents/signed/code/rebuild_pr165_fusion.py \
  --source work/frontier/pr165-7518fed/extracted/chafreaky-integer-mult-bounds-7518fed \
  --export work/signed/reproduce-pr165 \
  --output work/signed/reproduce-pr165/fusion-reconstruction.json

PYTHONDONTWRITEBYTECODE=1 python3 agents/signed/code/check_pr165_signed_control.py \
  --export work/signed/reproduce-pr165 \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --output work/signed/reproduce-pr165/signed-audit.json

PYTHONDONTWRITEBYTECODE=1 python3 agents/signed/code/regenerate_pr168_control.py \
  --source work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b \
  --output-dir work/signed/reproduce-pr168

PYTHONDONTWRITEBYTECODE=1 python3 agents/signed/code/check_pr165_signed_control.py \
  --export work/signed/reproduce-pr168 \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --output work/signed/reproduce-pr168/signed-audit.json

PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 agents/signed/code/screen_pr168_modules.py \
  --source work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b \
  --plan work/frontier/pr165-7518fed/extracted/chafreaky-integer-mult-bounds-7518fed/research/paired-cube-plateau-162/references/pr162/make_plan.py \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --interval-code agents/signed/code/interval_moments.py \
  --output work/signed/reproduce-pr168-producer-batch --workers 4 \
  --trial-saving 617042388/1000000000000
```

The pin-checked PR165 export path is separate from the actual source
reconstruction command. Its proof does not rely on calling saved graph
loading a regenerated search. The PR168 command freshly constructs the
changed source modules and signed DAG, carrier closure, gauges and word;
it rechecks saved physical choices against that word and rebuilds the paid
profile. Reproduction of historical optimization searches is not required
or claimed. The complete four-variant path was exercised. Exact output
profiles, source/dirty coefficients, controls and shared trial results
are in the compact result files; displayed root estimates are discovery
calculations only. The separate geometry lane's independent checker is
identified by path and byte hash in the control result.

The joint continuation entry point accepts the immutable same-word fusion
export and a checked initial operation-frame list:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 agents/signed/code/continue_fused_pairs.py \
  --source work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b \
  --export work/signed/pr168-fusion-export-20261009T0848Z \
  --initial-frames work/placement/pr168-fusion-components-98c115b/frames.json \
  --plan work/frontier/pr165-7518fed/extracted/chafreaky-integer-mult-bounds-7518fed/research/paired-cube-plateau-162/references/pr162/make_plan.py \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --interval-code agents/signed/code/interval_moments.py \
  --output work/signed/reproduce-joint --workers 4 --rounds 6 --passes 30
```

Those initial frames and the coherent fusion export are frozen completed
text evidence, rather than downloadable upstream inputs. Their archive
manifests record full decompressed byte identities. Recover them by safe
gzip decompression to a new task-owned work directory, or regenerate the
four-variant producer batch and placement component run with the pinned
sources/checkers. The joint protocol pins its initial frame bytes and all
dependencies. Do not place these frames on another graph or word.

All important source modifications are authored under `../code/`; the
external snapshots remain unchanged. The only finite verifier adaptation
in the changed batch is recorded in every result. No output claims a final
accepted exponent. The coordinator owns archive review and Git publication.

## Global-lower joint successor and exact moment review

The stronger seed31 state was generated using the same joint entry point,
changing only these arguments in the command above:

```bash
  --initial-frames work/placement/pr168-fusion-global-lower-98c115b/frames.json \
  --output work/signed/reproduce-global-joint --workers 4 --rounds 4 --passes 30 \
  --trial-saving 617042388/1000000000000
```

Retain the historical trial to reproduce the discovery choices exactly.
The `seed31/physical-frames.json`, `physical-pairs.json` and `profile.json`
form one coherent physical state on the same base graph/closure/word. Its
new pairs must accompany its frames. The frozen expected-format base export
is a deterministic renaming of the completed producer `complete_fusion/`
outputs: `graph.json`, `baseline.json` and `frames.json` retain their names;
`selection.json` becomes `word.json`, `selected-profile.json` becomes
`profile-before.json`, and `physical-profile.json` becomes `profile.json`.
`fresh-physical-inputs.json` supplies the raw `physical-frames.json` and
`physical-pairs.json` lists. Export protocols hash all eight inputs. To
freeze a successor, preserve the five graph/closure/word inputs and replace
all three physical inputs together, then recompute their protocol hashes.

The exact moment entry point checks every export pin, reconstructs the
complete paid histogram from its constituent bills, and rigorously encloses
both requested trials and its root on a one-in-10^12 grid:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 agents/signed/code/enclose_finite_export.py \
  --export work/placement/fused168-joint-raise-frozen-20261009T0937Z \
  --interval-code agents/signed/code/interval_moments.py \
  --saving 617560360/1000000000000 \
  --saving 617660000/1000000000000 \
  --output work/signed/reproduce-raise-moment.json
```

That placement continuation is a separate pinned driver/run with unchanged
graph, word and seed31 pairs. Its full exact signed core is checked by the
same generic core command above with this final export argument. Literal
complemented reflection and final assembly remain distinct checkers.
