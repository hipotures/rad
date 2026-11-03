"""Full candidate-evaluation cycle throughput from wse.pd2_eval worker logs (any environment with numpy).

    python -m wse.pd2_throughput --campaign <id> --label direct-2gpu --since <unix time> --out <json>

Per job (one candidate editor on one split): transition (patch preparation + application/reload/restart + cache reset +
hash verification), generation (round 1 + probe-pass feedback + round 2), scoring and persistence (in the scoring thread,
overlapping the next job's generation). Throughput is completed jobs per wall-clock minute from the first claim to the
last completion, per worker and for all workers together; the worker's one-time engine start is reported separately.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from . import work_root


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--since", type=float, default=0)
    ap.add_argument("--until", type=float, default=1e18)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    raw = work_root() / "raw" / a.campaign
    logs = [json.loads(f.read_text()) for f in sorted(raw.glob("worker-*.json"))]
    logs = [w for w in logs if a.since <= min([j.get("claimed_at", 1e18) for j in w["jobs"]] or [1e18]) <= a.until]
    jobs = [j for w in logs for j in w["jobs"] if "error" not in j]
    if not jobs:
        raise SystemExit("no jobs")
    tr = lambda j, k: (j.get("transition") or {}).get(k) or 0.0   # noqa: E731
    per = [{"job": j["job_id"], "worker": j["worker"], "mode": (j.get("transition") or {}).get("mode_used"),
            "transition_s": tr(j, "total_s"), "prepare_s": tr(j, "prepare_s"), "export_s": tr(j, "export_s"),
            "apply_s": tr(j, "apply_s"), "reset_s": tr(j, "reset_s"), "verify_s": tr(j, "verify_s"),
            "generate_s": j["gen"]["generate_s"], "feedback_s": j["gen"]["feedback_s"], "round2_s": j["gen"]["round2_s"],
            "score_s": j.get("score_s"), "persist_s": j.get("persist_s"), "gen_tokens": j["gen"]["gen_tokens"],
            "requests": j["gen"]["requests"], "probe_passes": j["gen"]["probe_passes"],
            "gpu_path_s": j["generated_at"] - j["claimed_at"], "end_to_end_s": j["completed_at"] - j["claimed_at"]}
           for j in jobs]
    t0 = min(j["claimed_at"] for j in jobs)
    t1 = max(j["completed_at"] for j in jobs)
    med = lambda k: float(np.median([p[k] or 0 for p in per]))   # noqa: E731
    out = {"label": a.label, "campaign": a.campaign, "workers": len(logs), "jobs": len(jobs),
           "swap_modes": sorted({w["swap_mode"] for w in logs}), "engine_startup_s": [w["startup_s"] for w in logs],
           "worker_init_s": [w["init_s"] for w in logs],
           "wall_s": t1 - t0, "candidates_per_minute": len(jobs) / (t1 - t0) * 60,
           "candidates_per_gpu_hour": len(jobs) / (t1 - t0) * 3600 / len(logs),
           "median_s": {k: med(k) for k in ("transition_s", "prepare_s", "export_s", "apply_s", "reset_s", "verify_s",
                                            "generate_s", "feedback_s", "round2_s", "score_s", "persist_s",
                                            "gpu_path_s", "end_to_end_s")},
           "sum_s": {k: float(sum(p[k] or 0 for p in per)) for k in ("transition_s", "generate_s", "feedback_s",
                                                                       "round2_s", "score_s", "persist_s")},
           "final_audits_ok": all(w["final_audit"]["ok"] for w in logs),
           "memory_allocated_mib": [w["final_memory"]["allocated"] >> 20 for w in logs],
           "failed_jobs": sum(1 for w in logs for j in w["jobs"] if "error" in j), "per_job": per}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "per_job"}, indent=1))


if __name__ == "__main__":
    main()
