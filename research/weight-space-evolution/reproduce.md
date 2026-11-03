# Reproduction guide

All commands run from this topic directory unless stated. Large/disposable material lives in a disk-backed work root
outside Git; **do not use /tmp** (RAM-backed on the reference host). Set:

```bash
export WSE_WORK_ROOT=$HOME/work/rad/weight-space-evolution   # any writable disk path
export TMPDIR=$WSE_WORK_ROOT/tmp
W=$WSE_WORK_ROOT; TOPIC=$PWD
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
cd $TOPIC && RUN=<new-run-id> GPU_GOLD=<uuid|0> GPU_P50C=<uuid|1> code/scripts/run_p50c_math500_bounded.sh
```

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

The held-out seed base is drawn at that moment (recorded in `protocol.json`), so a re-run uses new seeds; compare
distributions, not exact values. To re-score an existing candidate on the recorded seeds, use
`wse.minatar_eval.evaluate` with `range(test_seed_base, test_seed_base + 1000)` and the patch from
`runs/<run>/results/` (the patch delta is stored in Git as a compact JSON).

## 7. Recovery notes

- Everything under `$WSE_WORK_ROOT` is downloadable or deterministically regenerable from the commands above,
  except editor session transcripts and raw logs, which are archived as text evidence under `evidence/`.
- Gold directories are made read-only; to delete a work root, first `chmod -R u+w $W/gold $W/sessions`.
