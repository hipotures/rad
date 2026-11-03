# Reproduction guide

All commands run from this topic directory unless stated. Large/disposable material lives in this topic's ignored
`work/` directory (inside the working directory, excluded from Git tracking). **Do not use /tmp** (RAM-backed on the
reference host). Set:

```bash
TOPIC=$PWD; W=$TOPIC/work
export WSE_WORK_ROOT=$W TMPDIR=$W/tmp      # WSE_WORK_ROOT defaults to <topic>/work when unset
# keep every tool cache inside the topic (nothing is written to $HOME or /tmp)
export UV_CACHE_DIR=$W/cache/uv HF_HOME=$W/cache/hf XDG_CACHE_HOME=$W/cache VLLM_CACHE_ROOT=$W/cache/vllm \
       TRITON_CACHE_DIR=$W/cache/triton FLASHINFER_WORKSPACE_BASE=$W/cache TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor
mkdir -p $W/{repos,inputs,derived,envs,raw,logs,tmp,cache}
```

Prerequisites: Linux, `bwrap` (bubblewrap ≥ 0.11), `uv`, `git`, `curl`, NVIDIA driver for the GPU steps
(reference: 2× RTX 4090 24 GiB, driver 615.71.09; see `reports/environment.json`). Disk: ≈ 6 GB for weights,
exports and envs (+ ≈ 8 GB for the vLLM env).

## 1. Environments (pinned in `configs/requirements-*.lock.txt`)

```bash
cd $W/envs
uv venv -p 3.12 wse     && VIRTUAL_ENV=$W/envs/wse     uv pip install -r $TOPIC/configs/requirements-wse.lock.txt
uv venv -p 3.12 sandbox && VIRTUAL_ENV=$W/envs/sandbox uv pip install -r $TOPIC/configs/requirements-sandbox.lock.txt
uv venv -p 3.12 vllm    && VIRTUAL_ENV=$W/envs/vllm    uv pip install -r $TOPIC/configs/requirements-vllm.lock.txt
cd $TOPIC
```

`sandbox` must contain numpy only (the editor's sandbox has no torch, no autograd and no game simulator).

## 2. Inputs (identities in `input-manifest.json`)

```bash
git clone https://github.com/RikiyaT/lm_understand-logs.git $W/repos/lm_understand-logs
git -C $W/repos/lm_understand-logs checkout 4d09ba6d6a7e891dd8063974dfe81b3d78e3494f

D=$W/inputs/qwen3.5-0.8B-2fc0636; mkdir -p $D
R=https://huggingface.co/Qwen/Qwen3.5-0.8B/resolve/2fc06364715b967f1860aea9cf38778875588b17
for f in config.json model.safetensors-00001-of-00001.safetensors model.safetensors.index.json tokenizer.json \
         tokenizer_config.json chat_template.jinja merges.txt vocab.json LICENSE; do curl -sfL -o $D/$f $R/$f; done
sha256sum $D/model.safetensors-00001-of-00001.safetensors   # expect 04b1c301…4696
chmod a-w $D/*

mkdir -p $W/inputs/math500
curl -sfL -o $W/inputs/math500/test.jsonl \
  https://huggingface.co/datasets/HuggingFaceH4/MATH-500/resolve/6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be/test.jsonl
sha256sum $W/inputs/math500/test.jsonl                      # expect 35dc4108…6132
```

## 3. Phase A — rebuild the published exp8 edits (CPU, ~10 s each)

```bash
cd $TOPIC/code
G=$W/inputs/qwen3.5-0.8B-2fc0636/model.safetensors-00001-of-00001.safetensors
E=$W/repos/lm_understand-logs/exp8_math
$W/envs/wse/bin/python -m wse.p50c --gold-file $G --edit-dir $E/runs/p50c/edit \
   --out $TOPIC/runs/<new-run-id>/results/reconstruction.json
for r in p10c p25c; do $W/envs/wse/bin/python -m wse.p50c --run-name $r --gold-file $G \
   --edit-dir $E/runs/$r/edit --out $TOPIC/runs/<new-run-id>/results/reconstruction_$r.json; done
# cross-check with the upstream tool (run from a directory outside the checkout)
(cd $W/tmp && $W/envs/wse/bin/python -I $E/code/apply_edit.py $G $E/runs/p50c/edit $W/derived/p50c-upstream-npy)
```

Expected: every `checks` field true; p50c patch id `p-4b2661ed6f35`; changed entries 130,188.

Text-only exports (as evaluated upstream) and the bounded MATH-500 check (2 GPUs, ≈ 30–60 min):

```bash
U=$E/base_model/Qwen3.5-0.8B-text
$W/envs/wse/bin/python -m wse.text_export --gold-id 'qwen3.5-0.8B@2fc0636' --hf-dir $W/inputs/qwen3.5-0.8B-2fc0636 \
   --text-config-dir $U --out $W/derived/qwen3.5-0.8B-text-gold
$W/envs/wse/bin/python -m wse.text_export --gold-id 'qwen3.5-0.8B@2fc0636' --patch-id p-4b2661ed6f35 \
   --hf-dir $W/inputs/qwen3.5-0.8B-2fc0636 --text-config-dir $U --out $W/derived/qwen3.5-0.8B-text-p50c
# recorded run used the per-model split:  RUN=<id> GPU_GOLD=<uuid> GPU_P50C=<uuid> code/scripts/run_p50c_math500_bounded.sh
# preferred (balanced, problem-sharded across GPUs):
cd $TOPIC && RUN=<new-run-id> GPUS="<uuid0> <uuid1>" code/scripts/run_math500_sharded.sh
cd code && $W/envs/wse/bin/python -m wse.compare_math500 --ours $TOPIC/runs/<new-run-id>/results \
   --upstream-eval $E/eval --out $TOPIC/runs/<new-run-id>/results/comparison_vs_upstream.json
```

Expected (bounded subset, sampling noise ±~8 pp): Gold ≈ 6–8% with ≈ 93–95% cut; p50c ≈ 45–48% with ≈ 33% cut.

## 4. Harness tests

```bash
cd $TOPIC/code
WSE_SANDBOX_VENV=$W/envs/sandbox $W/envs/wse/bin/python -m pytest -q -p no:cacheprovider \
   --basetemp=$W/tmp/pytest-base tests          # expect 14 passed
```

## 5. MinAtar evaluator validation (CPU, ≈ 20 s)

```bash
cd $TOPIC/code
$W/envs/wse/bin/python -m wse.validate_minatar --exp5 $W/repos/lm_understand-logs/exp5_write_from_scratch \
   --games seaquest,asterix --episodes 1000 --seed-base 0 --workers 4 --out $TOPIC/runs/<new-run-id>/results/validation.json
```

Expected: Seaquest ≈ 53.1, Asterix ≈ 53 (|z| < 3 vs published); seeds 0..999 give exactly the recorded values.

## 6. Phase C — bounded editor session

```bash
cd $TOPIC/code
$W/envs/wse/bin/python -m wse.register_minatar --exp5 $W/repos/lm_understand-logs/exp5_write_from_scratch --game seaquest
# editor context (game rules + MinAtar source + input description from the upstream exp5 prompt)
U5=$W/repos/lm_understand-logs/exp5_write_from_scratch/runs/seaquest/message.txt
mkdir -p $W/derived/editor-context
{ sed -n 3,5p $U5; echo; awk '/^The game.s exact implementation/{p=1} p{print} /^How the 6 channels are built/{exit}' $U5; } \
   > $W/derived/editor-context/seaquest_game_source.txt      # sha256 f83f4156…fa48
$W/envs/wse/bin/python -m wse.lab --session <session-id> init ../configs/phaseC_seaquest_v1.json   # sandbox self-test must pass
```

Give the editor a wrapper that runs `python -m wse.lab --session <session-id> "$@"` (see
`runs/20261103T-phaseC-seaquest-v1-e1/protocol.json` for the exact editor prompt). After it submits:

```bash
$W/envs/wse/bin/python -m wse.heldout --session <session-id> --out-dir $TOPIC/runs/<new-run-id> \
   --raw-dir $W/raw/<new-run-id> --episodes 1000 --control-seeds 3
```

v3 (preregistered in `runs/20261103T-phaseC-seaquest-v3/protocol.json`) runs two conditions with configs
`configs/phaseC_seaquest_v3{S,N}.json`; condition N needs the prose-only context:

```bash
S=$W/derived/editor-context/seaquest_game_source.txt; N=$W/derived/editor-context/seaquest_rules_prose.txt
{ awk '/^The game.s exact implementation/{exit} {print}' $S; awk '/^THE INPUT/{p=1} /^How the 6 channels are built/{exit} p{print}' $S; } > $N
sha256sum $N    # cda7e33bdf1360ebeb23acf71910ec3767b2e19bb1440275c1386f55aad57b2f (checked by `lab brief --game-source`)
```

v2 used `configs/phaseC_seaquest_v2.json` (three sessions `phaseC-seaquest-v2-e{1,2,3}`), with
`--episodes 2000 --control-seeds 3 --active-controls --workers 6` for the per-session held-out. Joint comparison of all
submitted candidates on one shared fresh seed set, and the post-hoc ablation arms:

```bash
$W/envs/wse/bin/python -m wse.compare_candidates --sessions phaseC-seaquest-v1-e1 phaseC-seaquest-v2-e1 \
   phaseC-seaquest-v2-e2 phaseC-seaquest-v2-e3 --out-dir $TOPIC/runs/<new-run-id> --raw-dir $W/raw/<new-run-id> --episodes 4000 --workers 8
$W/envs/wse/bin/python -m wse.ablate_patch p-8255708841a2 --keep W1 --rationale "gate only"        # -> p-ed1458fd3f44
$W/envs/wse/bin/python -m wse.ablate_patch p-8255708841a2 --keep W2 b2 --rationale "hunting only"  # -> p-fa2f19291b16
$W/envs/wse/bin/python -m wse.compare_candidates --sessions phaseC-seaquest-v2-e3 \
   --extra-patches p-fa2f19291b16 p-ed1458fd3f44 p-ba49fc57d8c2 --out-dir $TOPIC/runs/<new-run-id> --raw-dir $W/raw/<new-run-id> --episodes 4000 --workers 8
$W/envs/wse/bin/python -m wse.export_patches --out $TOPIC/runs/<run>/results/patches <patch ids>   # compact Git copies
```

Without the original sessions, a patch can be recreated from its Git delta (`results/patches/<id>.delta.json`: flat
indices and new float32 values per tensor) with `wse.patch.create`; the content-addressed id must match.

The held-out seed base is drawn at that moment (recorded in `protocol.json`), so a re-run uses new seeds; compare
distributions, not exact values. To re-score an existing candidate on the recorded seeds, use
`wse.minatar_eval.evaluate` with `range(test_seed_base, test_seed_base + 1000)` and the patch from
`runs/<run>/results/` (the patch delta is stored in Git as a compact JSON).

## 7. Recovery notes

- Everything under `work/` is downloadable or deterministically regenerable from the commands above,
  except editor session transcripts and raw logs, which are archived as text evidence under `evidence/`.
- Gold directories are made read-only; to delete a work root, first `chmod -R u+w $W/gold $W/sessions`.
