#!/usr/bin/env bash
# Reconstruct the bounded four-case finite experiment in a fresh output root.
# RaD, OpenAI GPT-6.1 Sol assistance. Apache-2.0.
set -euo pipefail

if (( $# < 3 || $# > 4 )); then
    printf '%s\n' 'Usage: reproduce.sh SOURCE_ROOT PLAN_SOURCE_ROOT FRESH_OUTPUT_ROOT [WORKERS]' >&2
    exit 2
fi
module_source_root=$(realpath -- "$1")
module_plan_source_root=$(realpath -- "$2")
module_output_root=$(realpath -m -- "$3")
module_workers=${4:-4}
module_script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
module_sprint_root=$(cd -- "$module_script_dir/../../.." && pwd)

if [[ -e "$module_output_root" ]]; then
    printf 'Refusing an existing output root: %s\n' "$module_output_root" >&2
    exit 2
fi
if [[ ! "$module_workers" =~ ^[1-4]$ ]]; then
    printf '%s\n' 'Use one through four workers.' >&2
    exit 2
fi
mkdir -p -- "$module_output_root"
cd -- "$module_sprint_root"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

python3 agents/signed/code/regenerate_frontier_complex.py \
    --source "$module_source_root" \
    --source-head fd25adb7fbaa12ee761d02c733c54d1d2a7687ee \
    --output-dir "$module_output_root/control-export" > "$module_output_root/regeneration.log" 2>&1
python3 agents/module/code/generate_variants.py \
    --source "$module_source_root" --output "$module_output_root/inputs" > "$module_output_root/generation.log" 2>&1
python3 agents/module/code/screen_structural_modules.py \
    --source "$module_source_root" --export "$module_output_root/control-export" \
    --plan "$module_plan_source_root/research/paired-cube-plateau-162/references/pr162/make_plan.py" \
    --exact-core agents/baseline/code/exact_aliased_core.py \
    --interval-code agents/signed/code/interval_moments.py \
    --placement-code agents/placement/code --candidates "$module_output_root/inputs" \
    --output "$module_output_root/batch" --workers "$module_workers" \
    --trial-saving 655861417/1000000000000 > "$module_output_root/batch.log" 2>&1
python3 agents/module/code/collect_results.py \
    --source "$module_source_root" --candidates "$module_output_root/inputs" \
    --first-attempt "$module_output_root/batch" --repair "$module_output_root/batch" \
    --repaired-full-batch --output "$module_output_root/summary"
