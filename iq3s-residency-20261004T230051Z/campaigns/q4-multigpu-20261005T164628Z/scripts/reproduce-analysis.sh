#!/usr/bin/env bash
set -euo pipefail
campaign_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
campaign_python=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
"$campaign_python" "$campaign_dir/scripts/analyze_q4_multigpu.py" --campaign "$campaign_dir"
"$campaign_python" "$campaign_dir/scripts/render_q4_report.py" --campaign "$campaign_dir"
"$campaign_python" "$campaign_dir/scripts/audit_q4_multigpu.py" --campaign "$campaign_dir"
