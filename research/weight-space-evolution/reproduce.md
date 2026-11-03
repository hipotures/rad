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

## 8. Phase D pilot (E0 / p50c as editors of F1-F3 targets)

```bash
cd $TOPIC/code
export OMP_NUM_THREADS=4 HF_HOME=$W/cache/hf VLLM_CACHE_ROOT=$W/cache/vllm XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor TMPDIR=$W/tmp
for M in gold:E0 p50c:p50c; do for K in 0 1; do      # one (model, mode) per GPU; GPU UUIDs from nvidia-smi
  CUDA_VISIBLE_DEVICES=<uuid> $W/envs/vllm/bin/python -m wse.editor_pilot --model $W/derived/qwen3.5-0.8B-text-${M%%:*} \
     --label ${M##*:} --thinking $K --out $TOPIC/runs/<new-run-id> --raw-dir $W/raw/<new-run-id>
done; done
$W/envs/wse/bin/python -m wse.pilot_rescore --gens $W/raw/<new-run-id> --out $TOPIC/runs/<new-run-id>/results/rescore.json \
   E0_think0 p50c_think0 E0_think1 p50c_think1
```

Targets are deterministic from (family, split, index) (`wse.targets.build`), so no target files need to be stored;
`python -m wse.targets generate --family F2 --split pilot --n 16 --out $W/derived/targets` writes them with a manifest.

## 9. vLLM 32K performance campaign (inference tuning only)

Prerequisites: the vLLM environment (`work/envs/vllm`, lock `configs/requirements-vllm.lock.txt`), the text export
`work/derived/qwen3.5-0.8B-text-gold` (§3), and for the swap test `work/derived/qwen3.5-0.8B-text-p50c`. Record the
GPU unlock state first (absolute numbers depend on it; see `runs/20261103T-vllm-perf-32k/results/env/environment.json`).

```bash
cd code
C=20261103T-vllm-perf-32k          # use a fresh campaign id for a new attempt; results are never overwritten
PY=../work/envs/vllm/bin/python
# MTP drafter checkpoint (backbone hard-linked, Gold's mtp.* head copied)
$PY -m bench.add_mtp_head --text-dir ../work/derived/qwen3.5-0.8B-text-gold \
    --gold-st "../work/gold/qwen3.5-0.8B@2fc0636/weights.safetensors" --out ../work/derived/qwen3.5-0.8B-text-gold-mtp
# stages (each job: one engine on one GPU; two GPUs in parallel)
for s in stage0_baseline stage1_screen stage1b_mtp_reduced stage2_finalists; do
  $PY -m bench.queue ../configs/vllm_perf/$s.json --campaign $C; done
CAMPAIGN=$C bench/run_stage_f.sh                      # solo / both GPUs / TP=2
$PY -m bench.queue ../configs/vllm_perf/stage3_holdout.json --campaign $C
CAMPAIGN=$C bench/run_swap.sh                         # in-place checkpoint swap vs fresh engine
# summaries, behaviour checks, figures
R=../runs/$C/results
$PY -m bench.summarize --campaign $C --out $R
$PY -m bench.check_outputs --campaign $C --pilot ../work/raw/20261103T-phaseD-pilot-e0/E0_think0_generations.jsonl \
    --case P_free_max4096 --cand pilot_exact_g0 --out $R/output_equivalence.json
$PY -m bench.check_outputs --campaign $C --ref baseline_g0 --cand baseline_g1 m_attn_flashinfer s_mns1024 m_kv_fp8 \
    sp_mtp1 sp_mtp2 sp_mtp3 --out $R/output_equivalence.json
../work/envs/wse/bin/python -m bench.plots --summary $R/summary.json --out $R/figures --ref fin_ref_baseline \
    --highlight fin_p1_flashinfer,fin_p3_fi_mns1024_mnbt16k,fin_p2_fi_mnbt32k_mns512_kvfp8
```

Expected checks: `pilot_exact_g0` reproduces the committed pilot texts (identical_share 1.0); `baseline_g0` and
`baseline_g1` agree within about 1%; swap hashes equal the fresh-engine hashes. Using a profile in the Phase D pilot:
`python -m wse.editor_pilot ... --engine-json '{"attention_backend": "FLASHINFER", "max_num_seqs": 1024,
"max_num_batched_tokens": 16384}'` (opt-in; the default engine is unchanged and remains the bit-exact reference).

## 10. Phase D v2 benchmark and persistent weight-swap evaluator

Prerequisites: environments `work/envs/wse` (numpy/torch CPU, MinAtar) and `work/envs/vllm` (vLLM 0.33), the text
export `work/derived/qwen3.5-0.8B-text-gold` (§3), the upstream clone (§2) and both MinAtar Gold networks:

```bash
cd $TOPIC/code
$W/envs/wse/bin/python -m wse.register_minatar --exp5 $W/repos/lm_understand-logs/exp5_write_from_scratch --game seaquest
$W/envs/wse/bin/python -m wse.register_minatar --exp5 $W/repos/lm_understand-logs/exp5_write_from_scratch --game asterix
```

Benchmark instances (CPU; F4 episodes dominate, about 10-20 min per split on 24 cores). The held-out salt
`work/benchmarks/phaseD-v2/secret_salt.txt` is created on first use; to regenerate the *same* test/transfer splits the
original salt file must be restored (its sha256 is `salt_sha256` in `configs/phaseD_v2/protocol_v2_frozen.json`).
Without it a new salt defines a new benchmark version.

```bash
for s in pilot dev select test transfer; do CUDA_VISIBLE_DEVICES= $W/envs/wse/bin/python -m wse.pd2_bench generate --split $s; done
for s in pilot dev select test transfer; do $W/envs/wse/bin/python -m wse.pd2_bench rebaseline --split $s; done
$W/envs/wse/bin/python -m wse.pd2_bench verify --split dev            # regenerates 6 instances, must be byte-identical
CUDA_VISIBLE_DEVICES= $W/envs/wse/bin/python -m pytest -q -p no:cacheprovider --basetemp=$W/tmp/pytest-base tests/test_phaseD_v2.py
$W/envs/wse/bin/python -m wse.editor_population --out ../configs/phaseD_v2/editor_population.json   # 12 patches (seed 20261103)
```

Persistent evaluator integrity tests (both GPUs, about 15 min) and the determinism probe:

```bash
CAMPAIGN=<new-id> P=r2_ EXT=32 EXTSEED=1 EXTFULL=--ext-full scripts/run_swap_tests.sh
$W/envs/wse/bin/python -m wse.swap_analyze --raw $W/raw/<new-id> --prefix r2_ --out <results>/swap_tests_r2.json
scripts/run_determinism_probe.sh
```

Expected: every visit `identical_to_some_fresh` for greedy, sampled and constrained; all Gold audits ok.

Editor evaluation (job queue; one persistent engine per GPU; held-out splits require `--allow-heldout`):

```bash
Q=$W/queues/<campaign>; EDS=$(python3 -c "import json;print(','.join(e['editor_id'] for e in json.load(open('../configs/phaseD_v2/editors.json'))['editors']))")
PYTHONPATH=. $W/envs/vllm/bin/python -m wse.pd2_eval submit --queue $Q --editors $EDS --split dev
date +%s > $W/tmp/<campaign>.start
CAMPAIGN=<campaign> QUEUE=$Q GPUS="0 1" SWAP_MODE=direct scripts/run_pd2_workers.sh
$W/envs/wse/bin/python -m wse.pd2_report --campaign <campaign> --split dev --out <results>
$W/envs/wse/bin/python -m wse.pd2_throughput --campaign <campaign> --label direct-2gpu --since $(cat $W/tmp/<campaign>.start) --out <results>/throughput_direct-2gpu.json
BASE=<campaign> scripts/run_pd2_throughput_modes.sh      # restart / reload on 2 GPUs, direct on 1 GPU
$W/envs/wse/bin/python -m wse.pd2_figures --e2e <results> --swap <swap results>/swap_tests_r2.json --out <run>/figures
```

Protocol freeze (already done; re-running on the same pilot results must reproduce the committed file except for the
`status` text): `python -m wse.pd2_freeze --pilot ../runs/20261103T-phaseD-v2-pilot/results/editor_results_pilot.json --out-dir ../configs/phaseD_v2`.


## 11. Phase D parent-bootstrap preparation (no paid calls)

From this topic directory, with existing environments and acquired benchmark inputs from section 10:

```bash
PYTHONPATH=code work/envs/wse/bin/python -m wse.bootstrap_prepare
PYTHONPATH=code work/envs/wse/bin/python -m pytest -q code/tests/test_bootstrap_prepare.py code/tests/test_phaseD_v2.py
```

Unset `WSE_WORK_ROOT` and `WSE_BENCH_DIR`; preparation refuses overrides. The preparation tool checks the committed
source/protocol lock, the original salt commitment, all five manifests and all 595 JSON/NPZ payload pairs, then
verifies immutable Gold, tightens private file permissions and writes four separate prompt views under
`work/phaseD-bootstrap/phaseD-parent-*/view/`. It never creates a salt, scores held-out targets or launches a model.
A missing or corrupt original is an error; recover it from its recorded source or private backup, never regenerate
a replacement salt. The exported dev views omit oracle fields, baselines and T0 answer keys. Prompts themselves
contain the intended task information, including all T0 options.

The existing sandbox must pass `Sandbox.selftest` with the topic, salt and select/test/transfer paths forbidden.
Only allowlisted Gold views and per-session scratch are mounted. Parents must not be launched as unrestricted
workspace agents. The sandbox test verifies numerical-code isolation, not a future provider/tool broker.
The broker must enforce dev-only admission, per-session ledgers and patch-lineage ownership before execution.
The prepared configuration does not implement a paid-provider transport or authorize any calls.

Before paid execution, record explicit approval in `configs/phaseD_bootstrap/budget.json`, verify current pricing and
provider terms for that exact model, identify a private persistent salt backup, and validate the broker. Use the
existing `wse.pd2_eval` queue and workers on discovered GPU UUIDs (one engine each, profile3, direct mode with
verified reload fallback). Keep the frozen protocol and source lock intact. Register sealed candidate patches only
after their numerical recipes and lineage have been retained; do not overwrite the frozen integration registry.
Use a campaign-specific registry binding or a reviewed evaluator adapter and preserve its source separately.
Do not treat `paid_launch_enabled` as access control; no executable paid launcher is supplied by preparation.

Seal one candidate per parent before select. Run select once operator-side, return no feedback, then run the final
fixed candidate set with E0 and controls on test/transfer once. Preserve every failure and duplicate hash. Use the
frozen primary cells, decoding and `pd2_report` inference; no candidate replacement after select or test.
