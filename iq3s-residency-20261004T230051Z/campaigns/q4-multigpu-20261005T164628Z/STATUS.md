# Q4 controlled multi-GPU campaign

COMPLETE

```json
{
  "state": "COMPLETE",
  "completed": [
    "binary/source/model verified",
    "bounded layer check",
    "27valid measured4096requests",
    "9fixed64-output warmups",
    "sameID and helper-capacity fairness",
    "report/CSV/JSON",
    "frozen safe launchers checked",
    "artifact hashes",
    "owned processes stopped and bothGPUsidle"
  ],
  "running": null,
  "pending": [],
  "next_exact_action": "user review and real-prompt testing; no automatic residency experiment",
  "updated_utc": "2026-10-05T18:22:20.574731+00:00",
  "completed_cells": [
    "original-helper/256k",
    "original-helper/128k",
    "original-helper/32k",
    "layer-split/256k",
    "layer-split/128k",
    "layer-split/32k",
    "optimized-helper/256k",
    "optimized-helper/128k",
    "optimized-helper/32k"
  ],
  "valid_final_requests": 27,
  "current_winners": {
    "32k": {
      "decode": "layer-split",
      "prefill": "layer-split",
      "request_wall": "layer-split"
    },
    "128k": {
      "decode": "layer-split",
      "prefill": "layer-split",
      "request_wall": "layer-split"
    },
    "256k": {
      "decode": "layer-split",
      "prefill": "layer-split",
      "request_wall": "layer-split"
    }
  },
  "recommendation": "USE_LAYER_SPLIT",
  "audit": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z/analysis/audit.json"
}
```
